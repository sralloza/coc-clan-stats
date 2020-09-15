from datetime import datetime
import os
from typing import List
from urllib.parse import quote

import click
import requests

from .config import config
from .models import PlayerRecord

CLAN_ENDPOINT = "https://api.clashofclans.com/v1/clans/{}/members"
PLAYER_ENDPOINT = "https://api.clashofclans.com/v1/players/{}"
INVALID_KEYS = ["league"]


def fetch_player_records() -> List[PlayerRecord]:
    token = os.getenv("COC_API_TOKEN")
    headers = {"authorization": f"Bearer {token}"}
    clan_tag = quote(config.clan_tag)
    response = requests.get(CLAN_ENDPOINT.format(clan_tag), headers=headers)

    if not response.ok:
        msg = "Invalid response: " + str(response.json())
        raise click.ClickException(msg)

    json_response = response.json()["items"]

    players = []
    ts = datetime.now()
    for player in json_response:
        player_tag = quote(player["tag"])
        response = requests.get(PLAYER_ENDPOINT.format(player_tag), headers=headers)

        if not response.ok:
            msg = "Invalid response: " + str(response.json())
            raise click.ClickException(msg)

        kwargs = {"warStars": response.json()["warStars"]}
        kwargs["timestamp"] = ts
        for key, value in player.items():
            if key in INVALID_KEYS:
                continue
            if isinstance(value, dict):
                value = value["name"]
            kwargs[key] = value
        kwargs["player_name"] = kwargs["name"]
        del kwargs["name"]

        player = PlayerRecord(**kwargs)
        players.append(player)

    return players
