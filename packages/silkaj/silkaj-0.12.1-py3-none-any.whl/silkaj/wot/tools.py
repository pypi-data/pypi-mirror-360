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

import contextlib
import time
import urllib
from typing import Optional
from urllib.error import HTTPError

import rich_click as click
from duniterpy.api.bma import wot

from silkaj.constants import BMA_SLEEP
from silkaj.network import client_instance, exit_on_http_error
from silkaj.public_key import gen_pubkey_checksum
from silkaj.tui import Table


def identity_of(pubkey_uid: str) -> dict:
    """
    Only works for members
    Not able to get corresponding uid from a non-member identity
    Able to know if an identity is member or not
    """
    client = client_instance()
    return client(wot.identity_of, pubkey_uid)


def is_member(pubkey_uid: str) -> Optional[dict]:
    """
    Check identity is member
    If member, return corresponding identity, else: False
    """
    try:
        return identity_of(pubkey_uid)
    except HTTPError:
        return None


def wot_lookup(identifier: str) -> list:
    """
    :identifier: identity or pubkey in part or whole
    Return received and sent certifications lists of matching identities
    if one identity found
    """
    client = client_instance()
    return (client(wot.lookup, identifier))["results"]


def identities_from_pubkeys(pubkeys: list[str], uids: bool) -> list:
    """
    Make list of pubkeys unique, and remove empty strings
    Request identities
    """
    if not uids:
        return []

    uniq_pubkeys = list(filter(None, set(pubkeys)))
    identities = []
    for pubkey in uniq_pubkeys:
        time.sleep(BMA_SLEEP)
        with contextlib.suppress(HTTPError):
            identities.append(identity_of(pubkey))
    return identities


def choose_identity(pubkey_uid: str) -> tuple[dict, str, list]:
    """
    Get lookup from a pubkey or an uid
    Loop over the double lists: pubkeys, then uids
    If there is one uid, returns it
    If there is multiple uids, prompt a selector
    """

    try:
        lookups = wot_lookup(pubkey_uid)
    except urllib.error.HTTPError as e:
        exit_on_http_error(e, 404, f"No identity found for {pubkey_uid}")

    # Generate table containing the choices
    identities_choices = {
        "id": [],
        "uid": [],
        "pubkey": [],
        "timestamp": [],
    }  # type: dict
    for pubkey_index, lookup in enumerate(lookups):
        for uid_index, identity in enumerate(lookup["uids"]):
            identities_choices["id"].append(str(pubkey_index) + str(uid_index))
            identities_choices["pubkey"].append(gen_pubkey_checksum(lookup["pubkey"]))
            identities_choices["uid"].append(identity["uid"])
            identities_choices["timestamp"].append(
                identity["meta"]["timestamp"][:20] + "…",
            )

    identities = len(identities_choices["uid"])
    if identities == 1:
        pubkey_index = 0
        uid_index = 0
    elif identities > 1:
        table = Table().set_cols_dtype(["t", "t", "t", "t"])
        table.fill_from_dict(identities_choices)
        click.echo(table.draw())
        # Loop till the passed value is in identities_choices
        message = "Which identity would you like to select (id)?"
        selected_id = None
        while selected_id not in identities_choices["id"]:
            selected_id = click.prompt(message)

        pubkey_index = int(str(selected_id)[:-1])
        uid_index = int(str(selected_id)[-1:])

    return (
        lookups[pubkey_index]["uids"][uid_index],
        lookups[pubkey_index]["pubkey"],
        lookups[pubkey_index]["signed"],
    )
