# Copyright  2016-2025 Maël Azimi <m.a@moul.re>
#
# Silkaj is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Silkaj is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Silkaj. If not, see <https://www.gnu.org/licenses/>.

import functools
import re
import sys
from typing import Any
from urllib.error import HTTPError

from duniterpy import constants as du_const
from duniterpy.api import endpoint as ep
from duniterpy.api.client import Client
from duniterpy.documents import Document

from silkaj import constants, tools


def determine_endpoint() -> ep.Endpoint:
    """
    Pass custom endpoint, parse through a regex
    {host|ipv4|[ipv6]}:{port}{/path}
    ^(?:(HOST)|(IPV4|[(IPV6)]))(?::(PORT))?(?:/(PATH))?$
    If gtest flag passed, return default gtest endpoint
    Else, return g1 default endpoint
    """

    regex = f"^(?:(?P<host>{du_const.HOST_REGEX})|(?P<ipv4>{du_const.IPV4_REGEX})|\
(?:\\[(?P<ipv6>{du_const.IPV6_REGEX})\\]))(?::(?P<port>{du_const.PORT_REGEX}))?\
(?:/(?P<path>{du_const.PATH_REGEX}))?$"

    try:
        from click.globals import get_current_context

        ctx = get_current_context()
        endpoint = ctx.obj.get("ENDPOINT", None)
        gtest = ctx.obj.get("GTEST", None)
    except (ModuleNotFoundError, RuntimeError):
        endpoint, gtest = None, None

    if endpoint:
        m = re.search(re.compile(regex), endpoint)
        if not m:
            tools.click_fail(
                "Passed endpoint is of wrong format. Expected format: {host|ipv4|[ipv6]}:{port}{/path}",
            )
            return None
        port = int(m["port"]) if m["port"] else 443
        host, ipv4 = ep.fix_host_ipv4_mix_up(m["host"], m["ipv4"])

        if port == 443:
            return ep.SecuredBMAEndpoint(host, ipv4, m["ipv6"], port, m["path"])
        return ep.BMAEndpoint(host, ipv4, m["ipv6"], port)

    if gtest:
        return ep.endpoint(constants.G1_TEST_DEFAULT_ENDPOINT)
    return ep.endpoint(constants.G1_DEFAULT_ENDPOINT)


@functools.lru_cache(maxsize=1)
def client_instance():
    return Client(determine_endpoint())


def send_document(bma_path: Any, document: Document) -> None:
    client = client_instance()
    doc_name = document.__class__.__name__
    try:
        client(bma_path, document.signed_raw())
        print(f"{doc_name} successfully sent")
    except HTTPError as error:
        print(error)
        tools.click_fail(f"Error while publishing {doc_name.lower()}")


def exit_on_http_error(error: HTTPError, err_code: int, message: str) -> None:
    """
    Nicely displays a message on an expected error code.
    Else, displays the HTTP error message.
    """
    if error.code == err_code:
        tools.click_fail(message)
    print(error)
    sys.exit(constants.FAILURE_EXIT_STATUS)
