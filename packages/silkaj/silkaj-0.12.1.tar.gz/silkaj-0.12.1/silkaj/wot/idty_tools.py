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

import shutil
import sys
import urllib
from typing import Union

import pendulum
import rich_click as click
from duniterpy.api import bma
from duniterpy.documents import BlockID, Identity, Revocation
from texttable import Texttable

from silkaj.constants import ALL
from silkaj.network import client_instance
from silkaj.public_key import gen_pubkey_checksum
from silkaj.wot.tools import wot_lookup


def display_identity(idty: Identity) -> Texttable:
    """
    Creates a table containing the identity infos
    """
    client = client_instance()
    id_table = []
    id_table.append(["Public key", gen_pubkey_checksum(idty.pubkey)])
    id_table.append(["User ID", idty.uid])
    id_table.append(["Blockstamp", str(idty.block_id)])
    creation_block = client(bma.blockchain.block, idty.block_id.number)
    creation_date = pendulum.from_timestamp(creation_block["time"], tz="local").format(
        ALL,
    )
    id_table.append(["Created on", creation_date])
    # display infos
    table = Texttable(max_width=shutil.get_terminal_size().columns)
    table.add_rows(id_table, header=False)
    return table


def check_many_identities(document: Union[Identity, Revocation]) -> bool:
    """
    Checks if many identities match the one looked after.
    Returns True if the same identity is found, False if not.
    """
    doc_type = document.__class__.__name__
    error_no_identical_id = f"{doc_type} document does not match any valid identity."
    idty = document if doc_type == "Identity" else document.identity

    try:
        results_pubkey = wot_lookup(idty.pubkey)
        results_uid = wot_lookup(idty.uid)
    except urllib.error.HTTPError:
        sys.exit(
            f"{error_no_identical_id}\nuid: {idty.uid}\npubkey: \
{gen_pubkey_checksum(idty.pubkey)}",
        )

    # get all matching identities
    lookup_ids = merge_ids_lists(results_pubkey, results_uid, idty.currency)
    match = False
    for n, lookup in enumerate(lookup_ids):
        if idty == lookup:
            lookup_ids.pop(n)
            match = True
            break
    alternate_ids = display_alternate_ids(lookup_ids).draw()
    if match:
        if len(lookup_ids) >= 1:
            click.echo(f"One matching identity!\nSimilar identities:\n{alternate_ids}")
        return True
    click.echo(f"{error_no_identical_id}\nSimilar identities:\n{alternate_ids}")
    return False


def display_alternate_ids(ids_list: list) -> Texttable:
    labels = ["uid", "public key", "timestamp"]
    table = Texttable(max_width=shutil.get_terminal_size().columns)
    table.header(labels)
    for _id in ids_list:
        table.add_row(
            [_id.uid, gen_pubkey_checksum(_id.pubkey), str(_id.block_id)[:12]],
        )
    return table


def merge_ids_lists(lookups_pubkey: list, lookups_uid: list, currency: str) -> list:
    """
    merge two lists of identities and remove duplicate identities.
    """
    ids = ids_list_from_lookups(lookups_pubkey, currency)
    ids_uid = ids_list_from_lookups(lookups_uid, currency)
    for _id in ids_uid:
        # __equal__ does not work. This is condition "id in ids".
        for listed_id in ids:
            if _id.signed_raw() == listed_id.signed_raw():
                id_in_ids = True
                break
            id_in_ids = False
        if not id_in_ids:
            ids.append(_id)
    return ids


def ids_list_from_lookups(lookups: list, currency: str) -> list:
    ids = []
    for lookup in lookups:
        pubkey = lookup["pubkey"]
        lookup_ids = lookup["uids"]
        for _id in lookup_ids:
            appended_id = Identity(
                currency=currency,
                pubkey=pubkey,
                uid=_id["uid"],
                block_id=BlockID.from_str(_id["meta"]["timestamp"]),
            )
            appended_id.signature = _id["self"]
            ids.append(appended_id)
    return ids
