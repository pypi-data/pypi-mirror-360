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

import time
from operator import itemgetter
from urllib.error import HTTPError

import pendulum
import rich_click as click
from duniterpy.api import bma

from silkaj import tui
from silkaj.blockchain.tools import get_head_block
from silkaj.constants import ALL, BMA_SLEEP
from silkaj.network import client_instance
from silkaj.wot.tools import identity_of


@click.command("blocks", help="Display blocks: default: 0 for current window size")
@click.argument("number", default=0, type=click.IntRange(0, 5000))
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Force detailed view. Compact view happen over 30 blocks",
)
def list_blocks(number: int, detailed: bool) -> None:
    head_block = get_head_block()
    current_nbr = head_block["number"]
    if number == 0:
        number = head_block["issuersFrame"]
    client = client_instance()
    blocks = client(bma.blockchain.blocks, number, current_nbr - number + 1)
    issuers = []
    issuers_dict = {}
    for block in blocks:
        issuer = {}
        issuer["pubkey"] = block["issuer"]
        if detailed or number <= 30:
            issuer["block"] = block["number"]
            issuer["gentime"] = pendulum.from_timestamp(
                block["time"], tz="local"
            ).format(ALL)
            issuer["mediantime"] = pendulum.from_timestamp(
                block["medianTime"], tz="local"
            ).format(ALL)
            issuer["hash"] = block["hash"][:10]
            issuer["powMin"] = block["powMin"]
        issuers_dict[issuer["pubkey"]] = issuer
        issuers.append(issuer)
    for pubkey in issuers_dict.items():
        issuer = issuers_dict[pubkey[0]]
        time.sleep(BMA_SLEEP)
        try:
            idty = identity_of(issuer["pubkey"])
        except HTTPError:
            idty = None
        for issuer2 in issuers:
            if (
                issuer2.get("pubkey") is not None
                and issuer.get("pubkey") is not None
                and issuer2["pubkey"] == issuer["pubkey"]
            ):
                issuer2["uid"] = idty["uid"] if idty else None
                issuer2.pop("pubkey")
    print_blocks_views(issuers, current_nbr, number, detailed)


def print_blocks_views(issuers, current_nbr, number, detailed):
    header = (
        f"Last {number} blocks from n°{current_nbr - number + 1} to n°{current_nbr}"
    )
    print(header, end=" ")
    if detailed or number <= 30:
        sorted_list = sorted(issuers, key=itemgetter("block"), reverse=True)

        table = tui.Table(style="columns")
        table.set_cols_align(["r", "r", "r", "r", "r", "l"])
        table.set_cols_dtype(["i", "t", "t", "t", "i", "t"])
        table.fill_from_dict_list(sorted_list)
        table.set_cols_align(["r", "r", "r", "r", "r", "l"])
        table.set_cols_dtype(["i", "t", "t", "t", "i", "t"])
        print(f"\n{table.draw()}")

    else:
        list_issued = []
        for issuer in issuers:
            found = False
            for issued in list_issued:
                if issued.get("uid") is not None and issued["uid"] == issuer["uid"]:
                    issued["blocks"] += 1
                    found = True
                    break
            if not found:
                issued = {}
                issued["uid"] = issuer["uid"]
                issued["blocks"] = 1
                list_issued.append(issued)
        for issued in list_issued:
            issued["percent"] = round(issued["blocks"] / number * 100)
        sorted_list = sorted(list_issued, key=itemgetter("blocks"), reverse=True)
        table = tui.Table(style="columns")
        table.fill_from_dict_list(sorted_list)
        table.set_cols_align(["l", "r", "r"])
        table.set_cols_dtype(["t", "i", "i"])
        print(f"from {len(list_issued)} issuers\n{table.draw()}")
