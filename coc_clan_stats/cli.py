from pathlib import Path
import re

import click
from pendulum import now

from .config import config
from .csv_manager import get_csv, get_tag_map, save_player_records
from .fetch_data import fetch_player_records, get_current_players

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
@click.option("--token", prompt=True)
def set_token(token):
    path = Path(click.get_app_dir("coc-clan-stats")).joinpath("config.txt")
    data = re.sub(
        r"COC_API_TOKEN=([\w\._-]+)", "COC_API_TOKEN=" + token, path.read_text()
    )
    path.write_text(data)
    click.secho("Token set sucessfully", fg="bright_green")


@main.command()
def fetch():
    t0 = now()
    player_records = fetch_player_records()
    save_player_records(player_records)
    t1 = now()
    delta = t1 - t0
    click.secho(f"Fetched data in {delta.in_words()}", fg="bright_green")


@main.command("analyse")
@click.option("--local", is_flag=True)
@click.option("--all", "all_", is_flag=True, flag_value="all")
@click.argument("freq", nargs=1, required=False, default="1D")
def analyse_command(freq, local, all_):
    from .analyse import analyse

    if all_:
        freq = all_

    try:
        df = analyse(freq, local)
        click.echo(df)
    except Exception as exc:
        msg = type(exc).__name__ + ": " + str(exc)
        click.secho(msg, fg="bright_red")
        raise click.Abort()


@main.command("clear-cache")
def clear_cache_command():
    get_csv.clear_cache()
    click.echo("Cache cleared")


@main.command("tag-map")
@click.option("--local", is_flag=True)
@click.option("--clear-cache", "-c", is_flag=True)
def get_command(local, clear_cache):
    if clear_cache:
        get_csv.clear_cache()

    click.echo(get_tag_map(local))


@main.command("find-parasites")
@click.option("--local", is_flag=True)
@click.option("--all", "all_", is_flag=True, flag_value="all")
@click.argument("freq", nargs=1, required=False, default="1D")
def find_parasites_command(freq, local, all_):
    from .parasites import find_parasites

    if all_:
        freq = all_

    try:
        df = find_parasites(local=local, freq=freq)
        click.echo(df)
    except Exception as exc:
        msg = type(exc).__name__ + ": " + str(exc)
        click.secho(msg, fg="bright_red")
        raise click.Abort()


@main.command("reset")
def reset_csv():
    try:
        Path(config.csv_path).unlink()
        click.secho("File removed", fg="bright_green")
    except FileNotFoundError:
        click.secho("File didn't exist", fg="bright_yellow")


@main.command("current-players")
def show_current_players():
    players = get_current_players()
    click.echo(players)


def cli():
    return main(prog_name="coc-clan-stats")


if __name__ == "__main__":
    cli()
