from pathlib import Path

import click
from dotenv import load_dotenv

from ._version import get_versions

dotenv_path = Path(click.get_app_dir("coc-clan-stats")).joinpath("config.txt")
load_dotenv(dotenv_path)


__version__ = get_versions()["version"]
del get_versions
del load_dotenv
del Path
