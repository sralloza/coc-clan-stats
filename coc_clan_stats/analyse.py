from io import StringIO

import click

from coc_clan_stats.fetch_data import get_current_players

from .csv_manager import get_tag_map
from .csv_manager import get_csv

try:
    import numpy as np
except ImportError:
    click.secho("Install numpy to use analyse command", fg="bright_red", err=True)
    raise click.Abort()

try:
    import pandas as pd
except ImportError:
    click.secho("Install pandas to use analyse command", fg="bright_red", err=True)
    raise click.Abort()

SENSITIVITY = pd.Timedelta("1H")


def get_df(local=False) -> pd.DataFrame:
    csv_str = get_csv(local)
    data = StringIO(csv_str)
    df = pd.read_csv(data, parse_dates=["timestamp"])
    return df


def analyse(freq="1D", local=False, filter_to_print=True, aggressive=True):
    df = get_df(local=local)
    df = filter_players_in_clan(df)

    # Remove useless columns, the rank and the previous rank
    df.drop(columns=["clan_rank", "previous_clan_rank"], inplace=True)

    # Include other data
    df["donations_diff"] = df.donations - df.donations_received

    # In 'all' mode, do not filter data by time
    if freq == "all":
        td = None
        end = None
        start = None
    else:
        freq += " 1h"
        td = pd.Timedelta(freq)
        end = pd.Timestamp.now()
        start = end - td

    starts = []
    ends = []

    def parser(group: pd.DataFrame):
        group = group.set_index("timestamp")

        if td:
            data = group[start:end]
        else:
            data = group

        if data.empty:
            return None

        player_name = group.player_name.unique()[0]
        if td and aggressive and data.iloc[0].name - start >= SENSITIVITY:
            msg = f"Excluding {player_name} (start-time) [{data.iloc[0].name}]"
            click.secho(msg, fg="bright_yellow")
            return None

        if td and aggressive and end - data.iloc[-1].name >= SENSITIVITY:
            msg = f"Excluding {player_name} (end-time) [{data.iloc[-1].name}]"
            click.secho(msg, fg="bright_yellow")
            return None

        starts.append(data.iloc[0].name)
        ends.append(data.iloc[-1].name)

        result = data.select_dtypes(exclude="object").diff(data.shape[0] - 1).dropna()
        return result

    difs = df.groupby("tag").apply(parser)

    if difs.empty:
        raise ValueError("Emtpy data")

    # Show the date limits via index and columns' names
    if td and aggressive and len(set(starts)) != 1:
        raise ValueError(f"Multiple start times: {set(starts)}")

    if td and aggressive and len(set(ends)) != 1:
        raise ValueError(f"Multiple ends times: {set(ends)}")

    real_start = pd.to_datetime(pd.to_datetime(starts).values.astype(np.int64).mean())
    real_end = pd.to_datetime(pd.to_datetime(ends).values.astype(np.int64).mean())

    difs.index = [get_tag_map(local=local)[x[0]] for x in difs.index]
    difs.index.name = real_start.round("1T")
    difs.columns.name = real_end.round("1T")

    if filter_to_print:
        # Remove lines with zeros
        difs = difs.replace(0, np.nan).dropna(how="all").fillna("-")

    return difs


def filter_players_in_clan(data):
    current_players = get_current_players()
    mask = data.apply(lambda x: x.player_name in current_players, 1)
    return data[mask]
