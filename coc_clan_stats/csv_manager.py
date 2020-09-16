import csv
from pathlib import Path
from typing import List

from .config import config
from .models import PlayerRecord


def save_player_records(players: List[PlayerRecord]):
    csv_path = Path(config.csv_path)

    if not csv_path.is_file():
        csv_path.write_text(PlayerRecord.gen_first_csv_line(), encoding="utf8")

    with csv_path.open("at", encoding="utf8") as file:
        for player in players:
            file.write(player.to_csv())


def get_tag_map():
    file_data = Path(config.csv_path).read_text("utf8").splitlines()
    file_reader = csv.reader(file_data)
    headers = next(file_reader)
    real_map = {}

    for fields in file_reader:
        data = {k: v for k, v in zip(headers, fields)}
        if data["tag"] not in real_map:
            real_map[data["tag"]] = data["player_name"]

    return real_map