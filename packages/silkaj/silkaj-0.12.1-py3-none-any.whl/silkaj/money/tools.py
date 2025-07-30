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
from typing import Union

from duniterpy.api import bma
from duniterpy.documents.transaction import InputSource, OutputSource

from silkaj.constants import CENT_MULT_TO_UNIT
from silkaj.network import client_instance
from silkaj.public_key import gen_pubkey_checksum
from silkaj.wot import tools as wt


def display_amount(
    tx: list,
    message: str,
    amount: float,
    ud_value: float,
    currency_symbol: str,
) -> None:
    """
    Displays an amount in unit and relative reference.
    """
    UD_amount = str(round((amount / ud_value), 2))
    unit_amount = str(amount / CENT_MULT_TO_UNIT)
    tx.append(
        [
            f"{message} (unit|relative)",
            f"{unit_amount} {currency_symbol} | {UD_amount} UD {currency_symbol}",
        ],
    )


def display_pubkey(tx: list, message: str, pubkey: str) -> None:
    """
    Displays a pubkey and the eventually associated identity
    """
    tx.append([f"{message} (pubkey:checksum)", gen_pubkey_checksum(pubkey)])
    idty = wt.is_member(pubkey)
    if idty:
        tx.append([f"{message} (id)", idty["uid"]])


def get_amount_from_pubkey(pubkey: str) -> list[int]:
    listinput, amount = get_sources(pubkey)

    totalAmountInput = 0
    for _input in listinput:
        totalAmountInput += amount_in_current_base(_input)
    return [totalAmountInput, amount]


def get_sources(pubkey: str) -> tuple[list[InputSource], int]:
    client = client_instance()
    # Sources written into the blockchain
    sources = client(bma.tx.sources, pubkey)

    listinput = []
    amount = 0
    for source in sources["sources"]:
        if source["conditions"] == f"SIG({pubkey})":
            listinput.append(
                InputSource(
                    amount=source["amount"],
                    base=source["base"],
                    source=source["type"],
                    origin_id=source["identifier"],
                    index=source["noffset"],
                ),
            )
            amount += amount_in_current_base(listinput[-1])

    # pending source
    history = (client(bma.tx.pending, pubkey))["history"]
    pendings = history["sending"] + history["pending"]

    # add pending output
    pending_sources = []
    for pending in pendings:
        for i, output in enumerate(pending["outputs"]):
            # duniterpy#80
            outputsplited = output.split(":")
            if outputsplited[2] == f"SIG({pubkey})":
                inputgenerated = InputSource(
                    amount=int(outputsplited[0]),
                    base=int(outputsplited[1]),
                    source="T",
                    origin_id=pending["hash"],
                    index=i,
                )
                if inputgenerated not in listinput:
                    # add pendings before blockchain sources for change txs
                    listinput.insert(0, inputgenerated)

        for _input in pending["inputs"]:
            pending_sources.append(InputSource.from_inline(_input))

    # remove input already used
    for _input in pending_sources:
        if _input in listinput:
            listinput.remove(_input)

    return listinput, amount


@functools.lru_cache(maxsize=1)
def get_ud_value() -> int:
    client = client_instance()
    blockswithud = client(bma.blockchain.ud)
    NBlastUDblock = blockswithud["result"]["blocks"][-1]
    lastUDblock = client(bma.blockchain.block, NBlastUDblock)
    return lastUDblock["dividend"] * 10 ** lastUDblock["unitbase"]


def amount_in_current_base(source: Union[InputSource, OutputSource]) -> int:
    """
    Get amount in current base from input or output source
    """
    return source.amount * 10**source.base
