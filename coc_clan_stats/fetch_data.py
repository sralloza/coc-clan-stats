from datetime import datetime
from datetime import timedelta
import os
from typing import List
from urllib.parse import quote

from cachier import cachier
import click
import requests

from .config import config
from .models import PlayerRecord

CLAN_ENDPOINT = "https://api.clashofclans.com/v1/clans/{}/members"
PLAYER_ENDPOINT = "https://api.clashofclans.com/v1/players/{}"
INVALID_KEYS = ["league"]


@cachier(pickle_reload=False, stale_after=timedelta(minutes=5))
def request_coc_api(url):
    token = os.getenv("COC_API_TOKEN")
    headers = {"authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if not response.ok:
        msg = "Invalid response: " + str(response.json())
        raise RuntimeError(msg)

    return response


def request_clan_data():
    return request_coc_api(CLAN_ENDPOINT.format(quote(config.clan_tag)))


def request_player_data(player_tag):
    return request_coc_api(PLAYER_ENDPOINT.format(quote(player_tag)))


def get_current_players() -> List[str]:
    clan_response = request_clan_data()
    return [x["name"] for x in clan_response.json()["items"]]


def fetch_player_records() -> List[PlayerRecord]:
    clan_response = request_clan_data()
    json_response = clan_response.json()["items"]

    players = []
    ts = datetime.now()
    for player in json_response:
        player_response = request_player_data(player["tag"])

        kwargs = {"warStars": player_response.json()["warStars"]}
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
