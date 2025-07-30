import urllib.parse
from typing import TYPE_CHECKING, Optional

import httpx

from .version import _user_agent

if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    pass


def _get_base_headers(auth_token: Optional[str]):
    return {
        "authorization": auth_token,
        "user-agent": _user_agent,
    }


def _make_get_request(api_endpoint, path: str, headers: dict):
    url = urllib.parse.urljoin(api_endpoint, path)

    return httpx.get(url, headers=headers)


def _make_post_request(api_endpoint, path: str, headers: dict, json: dict):
    url = urllib.parse.urljoin(api_endpoint, path)
    return httpx.post(url, headers=headers, json=json)


def _make_put_request(api_endpoint, path: str, headers: dict, json: dict):
    url = urllib.parse.urljoin(api_endpoint, path)
    return httpx.put(url, headers=headers, json=json)
