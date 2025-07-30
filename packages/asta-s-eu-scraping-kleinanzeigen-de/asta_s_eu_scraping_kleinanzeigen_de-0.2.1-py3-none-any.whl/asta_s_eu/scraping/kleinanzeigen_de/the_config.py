"""
Initiate constants by reading content from files
"""
import json
import os
from pathlib import Path

from ciur import bnf_parser
from ciur.rule import Rule

PARSED_PAGES_LIMIT: int = 200

def find_config_dir() -> Path:
    """
    Search for "config" in the following order of priority:
    1. From the OS.
    2. From the sample config directory.
    3. From the Configuration directory.
    """
    directory = os.getenv('KLEINANZEIGEN_DE_CONFIG_FOLDER')
    if directory:
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory '{directory}' provided by "
                                    f"env 'KLEINANZEIGEN_DE_CONFIG_FOLDER' not found")
        return path

    tests_directory = Path(__file__).parent / "../../../../tests"
    path = tests_directory / "KLEINANZEIGEN_DE_CONFIG_FOLDER"
    if path.exists():
        return path

    path = tests_directory / "KLEINANZEIGEN_DE_CONFIG_FOLDER_SAMPLE"
    if path.exists():
        return path

    raise ValueError('No configuration directory found')

_CONFIG_DIR = find_config_dir()

FOLLOW_PERSONS: dict[str, str] = json.loads(
    _CONFIG_DIR.joinpath("follow_persons.json").read_bytes()
)
IGNORE_PERSONS_BY_PRO_HREF: dict[str, str] = json.loads(
    _CONFIG_DIR.joinpath("IGNORE_PERSONS_BY_PRO_HREF.json").read_bytes()
)

SEARCH: dict[str, str] = json.loads(
    _CONFIG_DIR.joinpath("search.json").read_bytes()
)

_SEARCH_RULE = _CONFIG_DIR.joinpath("search_rule.ciur").read_text('utf-8')

_RES_SEARCH = bnf_parser.external2dict(_SEARCH_RULE)
CIUR_SEARCH_RULE = Rule.from_list(_RES_SEARCH)


__all__ = (
    'CIUR_SEARCH_RULE',
    'FOLLOW_PERSONS',
    'IGNORE_PERSONS_BY_PRO_HREF',
    'PARSED_PAGES_LIMIT',
    'SEARCH',
)
