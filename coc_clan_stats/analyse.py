import click
import requests

from .config import config
from .csv_manager import get_tag_map

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

from io import StringIO


def get_df(local=False) -> pd.DataFrame:
    if local:
        data = config.csv_path
    else:
        click.echo("Fetching data from remote...")
        data = StringIO(
            requests.get(
                "https://sralloza.es/coc-clan-stats",
                headers={"user-agent": "coc-clan-stats"},
            ).text
        )
    df = pd.read_csv(data, parse_dates=["timestamp"])
    return df


def analyse(freq="1D", local=False, filter_to_print=True):
    df = get_df(local=local)

    # Remove useless columns, the rank and the previous rank
    df.drop(columns=["clan_rank", "previous_clan_rank"], inplace=True)

    # Include other data
    df["donations_diff"] = df.donations - df.donations_received

    def parser(group: pd.DataFrame):
        group = group.set_index("timestamp")

        # Set index with o'clock times
        start = group.index.min()
        end = group.index.max()

        if end - start > pd.Timedelta(hours=2):
            start = start.ceil("1H")
            end = end.ceil("1H")

        if freq == "all":
            new_index = pd.date_range(start=start, end=end, periods=2)
        else:
            new_index = pd.date_range(start=start, end=end, freq=freq)

        group = group.reindex(new_index, method="ffill").select_dtypes(exclude="object")

        # At least 2 values must exist to calculate the difference
        if len(group) < 2:
            msg = f"Not enough data (freq={freq!r}): [{start}] - [{end}]\n\n{group}"
            raise ValueError(msg)

        # Calculate the difference
        result = group.diff(1).dropna().iloc[-1:].reset_index(drop=True)
        result.index.name = f"{group.index[-2]} - {group.index[-1]}"
        return result

    difs = df.groupby("tag").apply(parser)

    # Show the date limits via index and columns' names
    start, end = difs.index.names[-1].split(" - ")
    difs.index = [get_tag_map()[x[0]] for x in difs.index]
    difs.index.name = start
    difs.columns.name = end

    if filter_to_print:
        # Remove lines with zeros
        difs = difs.replace(0, np.nan).dropna(how="all").fillna("-")
    return difs
