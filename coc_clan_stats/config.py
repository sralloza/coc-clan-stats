import os

import click


def get_env_var(var):
    try:
        var = "COC_CLAN_STATS_" + var.upper().replace("-", "_")
        return os.environ[var]
    except KeyError as exc:
        raise click.ClickException(f"Must define variable {var!r}") from exc


class config:
    csv_path = ""
    clan_tag = ""

    @classmethod
    def init_config(cls):
        for attr in dir(cls):
            if attr.startswith("_") or "init" in attr:
                continue

            value = get_env_var(attr)
            setattr(cls, attr, value)
