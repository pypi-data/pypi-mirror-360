"""Custom typing"""
from typing import TypedDict

from asta_s_eu.scraping.core import typing


class ProspectsResults(TypedDict):
    """
    Data Type for Prospects Results
    """
    has_more: bool
    prospects: typing.Prospects
