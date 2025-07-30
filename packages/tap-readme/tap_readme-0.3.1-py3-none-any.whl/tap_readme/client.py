"""REST client handling, including ReadMeStream base class."""

from __future__ import annotations

import typing as t
from urllib.parse import parse_qsl

from requests.auth import HTTPBasicAuth
from singer_sdk import RESTStream
from singer_sdk.pagination import BaseHATEOASPaginator

if t.TYPE_CHECKING:
    from urllib.parse import ParseResult

    from requests import Response
    from singer_sdk.helpers.types import Context


class ReadMePaginator(BaseHATEOASPaginator):
    """ReadMe.com paginator."""

    def get_next_url(self, response: Response) -> str | None:
        """Return the next page URL from a response. If no next page, return None."""
        return response.links.get("next", {}).get("url")  # type: ignore[no-any-return]


class ReadMeStream(RESTStream[t.Any]):
    """ReadMe.com stream class."""

    url_base = "https://dash.readme.com/api"
    records_jsonpath = "$[*]"

    _page_size = 100

    @property
    def authenticator(self) -> HTTPBasicAuth:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        return HTTPBasicAuth(self.config["api_key"], "")

    @property
    def http_headers(self) -> dict[str, str]:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {"User-Agent": f"{self.tap_name}/{self._tap.plugin_version}"}

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: ParseResult | None,
    ) -> dict[str, t.Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        params: dict[str, t.Any] = {"perPage": self._page_size}

        if next_page_token:
            params.update(parse_qsl(next_page_token.query))

        return params

    def get_new_paginator(self) -> ReadMePaginator:
        """Get a new paginator object."""
        return ReadMePaginator()
