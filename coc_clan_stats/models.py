from datetime import datetime
import re

valid_names = [
    "timestamp",
    "tag",
    "player_name",
    "role",
    "exp_level",
    "war_stars",
    "trophies",
    "versus_trophies",
    "clan_rank",
    "previous_clan_rank",
    "donations",
    "donations_received",
]

roles = ["member", "admin", "coLeader", "leader"]


class PlayerRecord:
    def __init__(self, **kwargs):
        keys = list(kwargs.keys())
        for key in keys:
            value = kwargs.pop(key)
            key = self.snake_case(key)

            if key not in valid_names:
                raise ValueError(key)
            setattr(self, key, value)

        if kwargs:
            raise RuntimeError(kwargs)

        self.fix()

    def fix(self):
        try:
            self.role = int(self.role)
        except ValueError:
            self.role = roles.index(self.role)

        for attr in valid_names:
            try:
                value = int(getattr(self, attr))
                setattr(self, attr, value)
            except (ValueError, TypeError):
                pass

    @staticmethod
    def snake_case(name) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @staticmethod
    def gen_first_csv_line():
        return ",".join(valid_names) + "\n"

    def to_csv(self) -> str:
        strings = []
        for key in valid_names:
            if key.startswith("_"):
                continue
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            strings.append(str(value))

        return ",".join(strings) + "\n"

    def __repr__(self) -> str:
        output = "PlayerRecord(%s)"
        strings = []
        keys = list(sorted(vars(self)))
        for key in keys:
            if key.startswith("_"):
                continue
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            strings.append(f"{key}={value!r}")

        return output % ", ".join(strings)
