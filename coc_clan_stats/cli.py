from pathlib import Path

import click
from pendulum import now

from .analyse import analyse
from .config import config
from .csv_manager import get_tag_map, save_player_records
from .fetch_data import fetch_player_records
from .parasites import find_parasites

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--config-path", help="show config path", is_flag=True)
def main(config_path):
    if config_path:
        return print_config_path()

    config.init_config()


def print_config_path():
    path = Path(click.get_app_dir("coc-clan-stats")).joinpath("config.txt")
    click.echo(path)


@main.command()
def fetch():
    t0 = now()
    player_records = fetch_player_records()
    save_player_records(player_records)
    t1 = now()
    delta = t1 - t0
    click.secho(f"Fetched data in {delta.in_words()}", fg="bright_green")


@main.command("analyse")
@click.argument("freq", nargs=1, required=False, default="1H")
def analyse_command(freq):
    try:
        df = analyse(freq)
        print(df)
    except Exception as exc:
        msg = type(exc).__name__ + ": " + str(exc)
        click.secho(msg, fg="bright_red")
        raise click.Abort()


@main.command("get-map")
def get_command():
    click.echo(get_tag_map())


@main.command("find-parasites")
def find_parasites_command():
    find_parasites()


@main.command("reset")
def reset_csv():
    try:
        Path(config.csv_path).unlink()
        click.secho("File removed", fg="bright_green")
    except FileNotFoundError:
        click.secho("File didn't exist", fg="bright_yellow")


def cli():
    return main(prog_name="coc-clan-stats")


if __name__ == "__main__":
    cli()
