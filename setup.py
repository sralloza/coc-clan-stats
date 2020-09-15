from setuptools import setup

from pathlib import Path

from setuptools import find_packages, setup

import versioneer

requirements = Path(__file__).with_name("requirements.txt").read_text().splitlines()

setup(
    name="coc-clan-stats",
    version=versioneer.get_version(),
    author="Diego Alloza",
    entry_points={
        "console_scripts": [
            "coc-clan-stats=coc_clan_stats.cli:cli",
            "ccs=coc_clan_stats.cli:cli",
        ]
    },
    include_package_data=True,
    author_email="coc-clan-stats-support@sralloza.es",
    url="git+http://github.com/sralloza/coc-clan-stats.git",
    install_requires=requirements,
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
)
