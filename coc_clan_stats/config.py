import os

import click


def get_env_var(var):
    try:
        var = "COC_CLAN_STATS_" + var.upper().replace("-", "_")
        return os.environ[var]
    except KeyError:
        raise click.ClickException(f"Must define variable {var!r}")


class config:
    csv_path = None
    clan_tag = None

    @classmethod
    def init_config(cls):
        for attr in dir(cls):
            if attr.startswith("_") or "init" in attr:
                continue

            value = get_env_var(attr)
            setattr(cls, attr, value)