"""
Initiate constants
"""
from typing import cast

import os
from pathlib import Path

from asta_s_eu.scraping.core.log import get_loggers

_, ALARM_LOG = get_loggers(Path(__file__), Path(__file__).parent / 'logging.yaml')

EMAIL_NOTIFICATION_FROM = os.getenv("EMAIL_NOTIFICATION_FROM")
assert EMAIL_NOTIFICATION_FROM

EMAIL_NOTIFICATION_PASSWORD = os.getenv("EMAIL_NOTIFICATION_PASSWORD")
assert EMAIL_NOTIFICATION_PASSWORD

EMAIL_NOTIFICATION_TO = os.getenv("EMAIL_NOTIFICATION_TO") or ''
WEB_SITE = "kleinanzeigen.de"

def get_environments() -> tuple[str, str]:
    """
    Get a mandatory environment, fail in case not finds.
    """
    assert os.getenv("EMAIL_NOTIFICATION_FROM")
    assert os.getenv("EMAIL_NOTIFICATION_PASSWORD")
    return (
        cast(str, os.getenv("EMAIL_NOTIFICATION_FROM")),
        cast(str, os.getenv("EMAIL_NOTIFICATION_PASSWORD"))
    )
