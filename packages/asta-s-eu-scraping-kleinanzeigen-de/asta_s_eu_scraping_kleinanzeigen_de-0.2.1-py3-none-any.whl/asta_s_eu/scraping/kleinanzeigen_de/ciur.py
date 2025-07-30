"""
Ciur extension layer
"""
from typing import Any, Callable, Iterable, Optional, Sequence, cast

import datetime
import logging
import re
from pathlib import Path

import ciur.parse
import retry
from ciur.exceptions import CiurBaseException
from ciur.models import Document
from ciur.rule import ListOfT

from asta_s_eu.scraping.core import CONFIG_DIR, catch_alarms
from asta_s_eu.scraping.core.log import MakeRetryAsInfo
from asta_s_eu.scraping.core.prospect_database.dynamo_db import \
    DynamoDB as ProspectDatabase
from asta_s_eu.scraping.core.send_email import gmailing_prospects

from . import irequests as requests
from .defaults import (ALARM_LOG, EMAIL_NOTIFICATION_TO, WEB_SITE,
                       get_environments)
from .the_config import (CIUR_SEARCH_RULE, FOLLOW_PERSONS,
                         IGNORE_PERSONS_BY_PRO_HREF, PARSED_PAGES_LIMIT,
                         SEARCH)
from .typing import ProspectsResults

assert ALARM_LOG, "ALARM_LOG path is required in logging.yaml"


LOG = logging.getLogger(__name__)


EMAIL_NOTIFICATION_FROM, EMAIL_NOTIFICATION_PASSWORD = get_environments()


def _ciur_parse_html_type(response: requests.Response, ciur_rule: ListOfT) -> dict[str, Any]:
    assert response.status_code == 200, response.status_code

    document = Document(response)

    if cast(str, InvalidHtml.__doc__) in response.text:
        raise InvalidHtml(f"Invalid html for url {response.url}")

    try:
        result = ciur.parse.html_type(document, ciur_rule[0])
        if isinstance(result, dict):
            return result

        raise ValueError(f'Expecting dictionary output, but got {type(result)}, see {result}')

    except CiurBaseException:
        log_time = f"{datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%S}"
        CONFIG_DIR.joinpath(
            f"ciur_fail_to_parse.{Path(__file__).name}.{log_time}.html"
        ).write_bytes(response.content)

        raise


class InvalidHtml(Exception):
    """<html><head><meta charset="utf-8"><script>f1xx.v1xx=v1xx;"""


@retry.retry(
   exceptions=(CiurBaseException, InvalidHtml, AssertionError),  # type: ignore[arg-type]  # can not explain yet
   tries=3,
   delay=120,
   logger=MakeRetryAsInfo(LOG.name, LOG.level)
)
def parse_page(url: str, web: requests.Session = requests.session()) -> dict[str, Any]:
    """
    Parse a search page, retry if fail to parse.
    """
    LOG.info("parse page %r", url)

    # pylint: disable=line-too-long
    #cookies = {
    #    'rbzid': 'bRiznBnNc+C9JiK+u+AIrMFBSwW9BXPK5Fxp9jycXmy4WxgrjNvmNOtTY+JLswY0eqY0QmJp04cOMkco/'
    #             'kgk9NWfm3WjuU3jonfcPTKpHAg4jdfJPYyrtrcqlqbmtdZ3OMahCM1GvKum0u0urJtIbXk7QGRp2H2WbZx8QK0XZPQ1vk7rG9KyFP'
    #            '+sUxpNZ8kxezD+90vRcEa+31K59hGPmzXtK9XLm5NF4CJCz/D9aP0=',
    #}
    # pylint: enable=line-too-long
    # if not web.cookies:
    #     _base_url = '/'.join(url.split('/', maxsplit=3)[:3])
    #     LOG.info("get cookies from home page %r", _base_url)
    #     LOG.info("headers %s", web.headers)
    #     _response = web.get(_base_url)
    #     assert _response.status_code == 200, _response.status_code
    #     del _base_url, _response

    response = web.get(url)

    assert response.status_code == 200, response.status_code

    # no person has no adds published
    if ' id="page-searchresults-noresultMessage" ' in response.text:
        return {
            "prospect_list": [],
            "has_next_page": False
        }

    # TODO: add this feature in ciur # pylint: disable=fixme
    if "Es wurden leider keine Ergebnisse für " in response.text:
        return {
            "prospect_list": [],
            "has_next_page": False
        }

    web_data = _ciur_parse_html_type(response, CIUR_SEARCH_RULE)
    for prospect in web_data['body']['prospect_list']:
        p_date = prospect['date']
        if p_date.startswith('Heute, '):
            prospect['date'] = datetime.datetime.now(datetime.UTC).strftime('%d.%m.%Y')
        elif p_date.startswith('Gestern, '):
            prospect['date'] = (
                    datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
            ).strftime('%d.%m.%Y')

    return cast(dict[str, Any], web_data['body'])


def find_next_url(url: str, page: int) -> str:
    # pylint: disable=pointless-string-statement
    """
    examples how url is paginated
    https://www.ebay-kleinanzeigen.de/s-13507/l3453r1
    https://www.ebay-kleinanzeigen.de/s-13507/seite:1/l3453r1

    https://www.ebay-kleinanzeigen.de/s-13507/        raspberry-pi/k0l3453r5
    https://www.ebay-kleinanzeigen.de/s-13507/seite:2/raspberry-pi/k0l3453r20

    https://www.ebay-kleinanzeigen.de/s-bestandsliste.html?userId=5037556
    https://www.ebay-kleinanzeigen.de/s-bestandsliste.html?userId=5037556&pageNum=2&sortingField=SORTING_DATE
    """
    # pylint: enable=pointless-string-statement

    if "/s-bestandsliste.html" in url:
        return f"{url}&pageNum={page + 1}&sortingField=SORTING_DATE"

    match = cast(re.Match[str], re.search(r"(.+)/(s-)?(\d{5})/(.+)", url))
    head = match.group(1)
    zip_search = (match.group(2) or '') + match.group(3)
    tail = match.group(4)
    return f"{head}/{zip_search}/seite:{page + 1}/{tail}"


def parse_a_search_page_until_n_captured(
        parse: Callable[[str], dict[str, Any]],
        start_url_page: str,
        db: ProspectDatabase,
        page_limit: int,
        captured_amount: int) -> ProspectsResults:
    """
    parse pages until hit ``page_limit`` or ``captured_amount``
    already captured items in our database
    """
    next_url = start_url_page
    prospects = []
    prospect_in_db = []
    page = 0
    for page in range(1, page_limit):
        parsed = parse(next_url)

        for prospect in parsed["prospect_list"]:
            if prospect in db:
                prospects += parsed["prospect_list"]
                prospect_in_db.append(prospects)
                if len(prospect_in_db) == captured_amount:
                    LOG.info("skip after %r match", captured_amount)
                    return ProspectsResults(has_more=False, prospects=prospects)
            else:
                # reset count
                prospect_in_db.clear()

        prospects += parsed["prospect_list"]

        if not parsed["has_next_page"]:
            LOG.info("No next page for ")
            break

        next_url = find_next_url(start_url_page, page)

    if prospects and page == page_limit - 1:
        return ProspectsResults(has_more=True, prospects=prospects)

    return ProspectsResults(has_more=False, prospects=prospects)


def config_parser(the_config: dict[str, Any]) -> Iterable[tuple[str, str]]:
    """
    Parse custom big config into smaller `query url` tuples
    """
    # Chausseestraße 117, 10115 Berlin
    for zip_label, zip_value in the_config["zip_label_value"].items():
        for _, value in the_config["value"].items():
            for query_, url_ in value.items():
                kwargs: dict[str, str] = {
                    "zip": zip_value,
                    "zip_label": zip_label,
                    "zip_value": zip_value
                }
                query = query_.format(**kwargs)
                url = url_.format(**kwargs)
                yield query, url


@catch_alarms(f"{WEB_SITE} - alarms",
              LOG, ALARM_LOG,
              EMAIL_NOTIFICATION_FROM, EMAIL_NOTIFICATION_TO, EMAIL_NOTIFICATION_PASSWORD)
def search_all() -> None:
    """
    Search by some predefined keywords and locations
    """
    LOG.info("========= SEARCH all =========")

    # Chausseestraße 117, 10115 Berlin
    for query, url in config_parser(SEARCH):
        LOG.info("query %r", query)
        db = ProspectDatabase()
        prospects_result = parse_a_search_page_until_n_captured(
            parse=parse_page,
            start_url_page=url,
            db=db,
            page_limit=PARSED_PAGES_LIMIT,
            captured_amount=5
        )

        prospects = prospects_result['prospects']

        LOG.info("Found %r prospects for query %r", len(prospects), query)

        new_prospects = list(filter_prospects(db.capture(prospects), IGNORE_PERSONS_BY_PRO_HREF))
        LOG.info("Found %r new products, send email to %r with new records",
                 len(new_prospects), EMAIL_NOTIFICATION_TO)

        LOG.info("Found %r new prospects from %r",
                 len(new_prospects), len(prospects_result))

        if new_prospects:
            gmailing_prospects(
                EMAIL_NOTIFICATION_FROM,
                EMAIL_NOTIFICATION_TO,
                f"{WEB_SITE} - {query}",
                EMAIL_NOTIFICATION_PASSWORD,
                new_prospects
            )
        else:
            LOG.info("No new item was added")


def filter_prospects(
        prospects: Sequence[dict[str, Any]],
        ignore_persons_by_pro_href: dict[str, str]) -> Iterable[dict[str, Any]]:
    """Custom filter for prospects"""
    switch_apartment = re.compile(r'(?i)(wohnungs| )tausch')
    for prospect in prospects:
        if prospect.get('pro_href') in ignore_persons_by_pro_href.values():
            LOG.info('Skip prospect by IGNORE_PERSONS_BY_PRO_HREF config')
            continue

        if prospect.get("price") in ("VB", None):
            LOG.info('Skip prospect by not set price')
            continue

        tag_list: Optional[list[str]] = prospect.get('tag_list')
        if tag_list:
            dhl_action = 'DHL Aktion'
            if dhl_action in tag_list:
                tag_list.remove(dhl_action)  # TODO:ciur: remove 'DHL Aktion' via ciur script

            ignore_girls_cloths_and_shoes = False
            for size in ['27', '28', '29', '30', '104', '110', '116']:
                if size in tag_list and 'Mädchen' in tag_list:
                    ignore_girls_cloths_and_shoes = True
                    break
            if ignore_girls_cloths_and_shoes:
                LOG.info("ignore girls cloths and shoes for %r", prospect['link'])
                continue

            ignore_apartment_change = False
            for size in ['4 Zimmer', '3 Zimmer']:
                if size in tag_list and switch_apartment.search(prospect['text'].lower()):
                    ignore_apartment_change = True
                    break
            if ignore_apartment_change:
                LOG.info("ignore apartment change for %r", prospect['link'])
                continue

        if tag_list == []: # noqa
            prospect.pop('tag_list')

        yield prospect


@catch_alarms(f"{WEB_SITE} - follow person",
              LOG, ALARM_LOG,
              EMAIL_NOTIFICATION_FROM, EMAIL_NOTIFICATION_TO, EMAIL_NOTIFICATION_PASSWORD)
def follow_person() -> None:
    """
    Follow concrete persons on ebay-kleinanzeigen.de since they may have some valuable prospects
    """
    LOG.info("========= FALLOW person =========")
    for query, person_id in FOLLOW_PERSONS.items():
        LOG.info("query %r", query)
        db = ProspectDatabase()
        url = f"https://www.kleinanzeigen.de/s-bestandsliste.html?userId={person_id}"
        prospects_result = parse_a_search_page_until_n_captured(
            parse=parse_page,
            start_url_page=url,
            db=db,
            page_limit=PARSED_PAGES_LIMIT,
            captured_amount=5,
        )

        prospects = prospects_result['prospects']
        LOG.info("Found %r prospects for query %r", len(prospects), query)

        new_prospects = list(filter_prospects(db.capture(prospects), IGNORE_PERSONS_BY_PRO_HREF))

        LOG.info("Found %r new products, send email to %r with new records",
                 len(new_prospects), EMAIL_NOTIFICATION_TO)
        LOG.info("Found %r new prospects from %r", len(new_prospects), len(prospects))

        if new_prospects:
            gmailing_prospects(
                EMAIL_NOTIFICATION_FROM,
                EMAIL_NOTIFICATION_TO,
                f"{WEB_SITE} - {query}",
                EMAIL_NOTIFICATION_PASSWORD,
                new_prospects
            )
        else:
            LOG.info("No new item was added")

    LOG.info("DONE")


__all__ = [
    'ProspectDatabase',
    'follow_person',
    'search_all',
]
