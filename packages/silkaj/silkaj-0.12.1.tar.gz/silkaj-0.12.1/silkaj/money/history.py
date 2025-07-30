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

import csv
from operator import eq, itemgetter, ne, neg
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError

import pendulum
import rich_click as click
from duniterpy.api.bma.tx import history
from duniterpy.api.client import Client
from duniterpy.documents.transaction import OutputSource, Transaction
from duniterpy.grammars.output import Condition

from silkaj.constants import ALL, ALL_DIGITAL, CENT_MULT_TO_UNIT
from silkaj.money import tools as mt
from silkaj.network import client_instance
from silkaj.public_key import (
    check_pubkey_format,
    gen_pubkey_checksum,
    validate_checksum,
)
from silkaj.tools import get_currency_symbol
from silkaj.tui import Table
from silkaj.wot import tools as wt


@click.command("history", help="History of wallet money movements")
@click.argument("pubkey")
@click.option("--uids", "-u", is_flag=True, help="Display identities username")
@click.option(
    "--full-pubkey", "-f", is_flag=True, help="Display full-length public keys"
)
@click.option(
    "--csv-file",
    "--csv",
    type=click.Path(exists=False, writable=True, dir_okay=False, path_type=Path),
    help="Write in specified file name in CSV (Comma-separated values) format the history of money movements",
)
def transaction_history(
    pubkey: str,
    uids: bool,
    full_pubkey: bool,
    csv_file: Optional[Path],
) -> None:
    if csv_file:
        full_pubkey = True

    if check_pubkey_format(pubkey):
        pubkey = validate_checksum(pubkey)

    client = client_instance()
    ud_value = mt.get_ud_value()
    currency_symbol = get_currency_symbol()

    received_txs, sent_txs = [], []  # type: list[Transaction], list[Transaction]
    get_transactions_history(client, pubkey, received_txs, sent_txs)
    remove_duplicate_txs(received_txs, sent_txs)

    txs_list = generate_txs_list(
        received_txs,
        sent_txs,
        pubkey,
        ud_value,
        currency_symbol,
        uids,
        full_pubkey,
    )
    table_headers = [
        "Date",
        "Issuers/Recipients",
        f"Amounts {currency_symbol}",
        f"Amounts UD{currency_symbol}",
        "Reference",
    ]
    if csv_file:
        if csv_file.is_file():
            click.confirm(f"{csv_file} exists, would you like to erase it?", abort=True)
        txs_list.insert(0, table_headers)
        with csv_file.open("w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(txs_list)
        click.echo(f"{csv_file} file successfully saved!")
    else:
        table = Table()
        table.fill_rows(txs_list, table_headers)
        header = generate_header(pubkey, currency_symbol, ud_value)
        click.echo_via_pager(header + table.draw())


def generate_header(pubkey: str, currency_symbol: str, ud_value: int) -> str:
    try:
        idty = wt.identity_of(pubkey)
    except HTTPError:
        idty = {"uid": ""}
    balance = mt.get_amount_from_pubkey(pubkey)
    balance_ud = round(balance[1] / ud_value, 2)
    date = pendulum.now().format(ALL)
    return f"Transactions history from: {idty['uid']} {gen_pubkey_checksum(pubkey)}\n\
Current balance: {balance[1] / CENT_MULT_TO_UNIT} {currency_symbol}, {balance_ud} UD {currency_symbol} on {date}\n"


def get_transactions_history(
    client: Client,
    pubkey: str,
    received_txs: list,
    sent_txs: list,
) -> None:
    """
    Get transaction history
    Store txs in Transaction object
    """
    tx_history = client(history, pubkey)
    currency = tx_history["currency"]

    for received in tx_history["history"]["received"]:
        received_txs.append(Transaction.from_bma_history(received, currency))
    for sent in tx_history["history"]["sent"]:
        sent_txs.append(Transaction.from_bma_history(sent, currency))


def remove_duplicate_txs(received_txs: list, sent_txs: list) -> None:
    """
    Remove duplicate transactions from history
    Remove received tx which contains output back return
    that we don't want to displayed
    A copy of received_txs is necessary to remove elements
    """
    for received_tx in list(received_txs):
        if received_tx in sent_txs:
            received_txs.remove(received_tx)


def generate_txs_list(
    received_txs: list[Transaction],
    sent_txs: list[Transaction],
    pubkey: str,
    ud_value: int,
    currency_symbol: str,
    uids: bool,
    full_pubkey: bool,
) -> list:
    """
    Generate information in a list of lists for texttable
    Merge received and sent txs
    Sort txs temporarily
    """

    received_txs_list, sent_txs_list = (
        [],
        [],
    )  # type: list[Transaction], list[Transaction]
    parse_received_tx(
        received_txs_list,
        received_txs,
        pubkey,
        ud_value,
        uids,
        full_pubkey,
    )
    parse_sent_tx(sent_txs_list, sent_txs, pubkey, ud_value, uids, full_pubkey)
    txs_list = received_txs_list + sent_txs_list

    txs_list.sort(key=itemgetter(0), reverse=True)
    return txs_list


def parse_received_tx(
    received_txs_table: list[Transaction],
    received_txs: list[Transaction],
    pubkey: str,
    ud_value: int,
    uids: bool,
    full_pubkey: bool,
) -> None:
    """
    Extract issuers` pubkeys
    Get identities from pubkeys
    Convert time into human format
    Assign identities
    Get amounts and assign amounts and amounts_ud
    Append reference/comment
    """
    issuers = []
    for received_tx in received_txs:
        for issuer in received_tx.issuers:
            issuers.append(issuer)
    identities = wt.identities_from_pubkeys(issuers, uids)
    for received_tx in received_txs:
        for issuer in received_tx.issuers:
            tx_list = []
            tx_list.append(
                pendulum.from_timestamp(received_tx.time, tz="local").format(
                    ALL_DIGITAL
                )
            )
            tx_list.append(assign_idty_from_pubkey(issuer, identities, full_pubkey))
            amounts = tx_amount(received_tx, pubkey, received_func)[0]
            tx_list.append(amounts / CENT_MULT_TO_UNIT)
            tx_list.append(round(amounts / ud_value, 2))
            tx_list.append(received_tx.comment)
            received_txs_table.append(tx_list)


def parse_sent_tx(
    sent_txs_table: list[Transaction],
    sent_txs: list[Transaction],
    pubkey: str,
    ud_value: int,
    uids: bool,
    full_pubkey: bool,
) -> None:
    """
    Extract recipients` pubkeys from outputs
    Get identities from pubkeys
    Convert time into human format
    If not output back return:
    Assign amounts, amounts_ud, identities, and comment
    """
    pubkeys = []
    for sent_tx in sent_txs:
        outputs = tx_amount(sent_tx, pubkey, sent_func)[1]
        for output in outputs:
            if output_available(output.condition, ne, pubkey):
                pubkeys.append(output.condition.left.pubkey)

    identities = wt.identities_from_pubkeys(pubkeys, uids)
    for sent_tx in sent_txs:
        total_amount, outputs = tx_amount(sent_tx, pubkey, sent_func)
        for output in outputs:
            if output_available(output.condition, ne, pubkey):
                tx_list = []
                tx_list.append(
                    pendulum.from_timestamp(sent_tx.time, tz="local").format(
                        ALL_DIGITAL
                    )
                )
                wallet = assign_idty_from_pubkey(
                    output.condition.left.pubkey, identities, full_pubkey
                )
                tx_list.append(wallet)
                tx_list.append(
                    neg(mt.amount_in_current_base(output)) / CENT_MULT_TO_UNIT,
                )
                tx_list.append(
                    round(neg(mt.amount_in_current_base(output)) / ud_value, 2),
                )
                tx_list.append(sent_tx.comment)
                sent_txs_table.append(tx_list)


def tx_amount(
    tx: list[Transaction],
    pubkey: str,
    function: Any,
) -> tuple[int, list[OutputSource]]:
    """
    Determine transaction amount from output sources
    """
    amount = 0
    outputs = []
    for output in tx.outputs:  # type: ignore[attr-defined]
        if output_available(output.condition, ne, pubkey):
            outputs.append(output)
        amount += function(output, pubkey)
    return amount, outputs


def received_func(output: OutputSource, pubkey: str) -> int:
    if output_available(output.condition, eq, pubkey):
        return mt.amount_in_current_base(output)
    return 0


def sent_func(output: OutputSource, pubkey: str) -> int:
    if output_available(output.condition, ne, pubkey):
        return neg(mt.amount_in_current_base(output))
    return 0


def output_available(condition: Condition, comparison: Any, value: str) -> bool:
    """
    Check if output source is available
    Currently only handle simple SIG condition
    XHX, CLTV, CSV should be handled when present in the blockchain
    """
    if hasattr(condition.left, "pubkey"):
        return comparison(condition.left.pubkey, value)
    return False


def assign_idty_from_pubkey(pubkey: str, identities: list, full_pubkey: bool) -> str:
    idty = gen_pubkey_checksum(pubkey, short=not full_pubkey)
    for identity in identities:
        if pubkey == identity["pubkey"]:
            pubkey_mod = gen_pubkey_checksum(pubkey, short=not full_pubkey)
            idty = f"{identity['uid']} - {pubkey_mod}"
    return idty
