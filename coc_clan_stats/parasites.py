import click

try:
    import pandas as pd
except ImportError:
    click.secho(
        "Install pandas to use find-parasites command", fg="bright_red", err=True
    )
    raise click.Abort()

from .analyse import analyse


class PlayerAnalisys:
    def __init__(self, data):
        self.role = data.role
        self.exp_level = data.exp_level
        self.trophies = data.trophies
        self.versus_trophies = data.versus_trophies
        self.donations = data.donations
        self.donations_received = data.donations_received
        self.donations_diff = data.donations_diff
        self.war_stars = data.war_stars


def find_parasites():
    df = analyse(freq="all", filter_to_print=False)
    df2 = pd.DataFrame(columns=["karma"])

    for player_name, player_data in df.iterrows():
        karma = calculate_karma(player_data)
        df2.loc[player_name] = karma

    df2.sort_values(by="karma", ascending=False, inplace=True)
    return df2


def calculate_karma(player):
    karma = 0
    player = PlayerAnalisys(player)

    if player.donations_diff > 0:
        karma += 2

    if player.donations_diff < 0:
        karma += 1

    if player.trophies > 0:
        karma += 2

    if player.trophies < 0:
        karma += 1

    karma += player.war_stars

    return karma
