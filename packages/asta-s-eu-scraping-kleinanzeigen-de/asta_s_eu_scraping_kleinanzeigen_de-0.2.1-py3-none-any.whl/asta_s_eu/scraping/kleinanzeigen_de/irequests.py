"""
Requests Compatible Interface

For unknown reason request.session().get('https://kleinanzeigen_de') return 403
only inside Docker container

A simple replacement of this API with urllib.request solve the issue
"""
import urllib.parse
import urllib.request

from requests import Response
from requests.structures import CaseInsensitiveDict


class Session: # pylint: disable=too-few-public-methods
    """
    requests.Session replicator
    """
    @staticmethod
    def get(url: str) -> Response:
        """HTTP get"""
        with urllib.request.urlopen(url) as f:
            response = Response()
            response.status_code = f.getcode()
            response.url = url
            response.headers = CaseInsensitiveDict(f.getheaders())
            response._content = f.read() # pylint: disable=protected-access
            return response


def session() -> Session:
    """Object like requests.Session"""
    return Session()


__all__ = ['Response']
