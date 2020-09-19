from collections import namedtuple
import json
import os
from pathlib import Path
import re
from typing import List

import click
from requests import Session

Key = namedtuple("key", "id name description ips token")


def set_token(token):
    path = Path(click.get_app_dir("coc-clan-stats")).joinpath("config.txt")
    data = re.sub(
        r"COC_API_TOKEN=([\w\._-]+)", "COC_API_TOKEN=" + token, path.read_text()
    )
    path.write_text(data)
    click.secho("Token set sucessfully", fg="bright_green")


class TokenManager:
    def __init__(self):
        self.session = Session()
        headers = {"content-type": "application/json", "user-agent": "coc-stats"}
        self.session.headers.update(headers)

    def login(self):
        email = os.environ.get("COC_CLAN_STATS_API_EMAIL")
        password = os.environ.get("COC_CLAN_STATS_API_PASSWORD")
        data = {"email": email, "password": password}
        url = "https://developer.clashofclans.com/api/login"

        r = self.session.post(url, data=json.dumps(data))
        r.raise_for_status()

    @staticmethod
    def json_to_key(json_key: dict) -> Key:
        return Key(
            json_key["id"],
            json_key["name"],
            json_key["description"],
            json_key["cidrRanges"],
            json_key["key"],
        )

    def list_keys(self) -> List[Key]:
        response = self.session.post(
            "https://developer.clashofclans.com/api/apikey/list", data="{}"
        )
        keys = response.json()["keys"]

        parsed_keys = []
        for key in keys:
            parsed_keys.append(self.json_to_key(key))

        return parsed_keys

    def generate_key(self, ip_address: str) -> Key:
        url = "https://developer.clashofclans.com/api/apikey/create"
        data = {
            "cidrRanges": [ip_address],
            "description": "temporal-key",
            "name": "temporal-key",
            "scopes": None,
        }

        response = self.session.post(url, data=json.dumps(data))
        response.raise_for_status()
        return self.json_to_key(response.json()["key"])

    def remove_key(self, key: Key):
        url = "https://developer.clashofclans.com/api/apikey/revoke"
        data = {"id": key.id}
        response = self.session.post(url, data=json.dumps(data))
        response.raise_for_status()

    def remove_temp_keys(self):
        valid_keywords = ["raspberry"]
        for key in self.list_keys():
            for keyword in valid_keywords:
                if keyword in key.name:
                    break
            else:
                self.remove_key(key)

    def get_public_ip(self) -> str:
        response = self.session.get("http://httpbin.org/ip")
        return response.json()["origin"]

    @classmethod
    def update_token(cls):
        self = cls()
        self.login()
        self.remove_temp_keys()
        new_key = self.generate_key(self.get_public_ip())
        set_token(new_key.token)
