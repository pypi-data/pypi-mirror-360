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

from typing import Optional

import rich_click as click

from silkaj import tools, tui
from silkaj.auth import auth_method
from silkaj.blockchain.tools import get_head_block
from silkaj.money import tools as m_tools
from silkaj.public_key import gen_pubkey_checksum, is_pubkey_and_check
from silkaj.wot import tools as wt


@click.command(
    "balance",
    help="Wallet·s balance·s. Multiple public keys can be passed, then a sum is computed. Also works with the authentication.",
)
@click.argument("pubkeys", nargs=-1)
@click.pass_context
def balance_cmd(ctx: click.Context, pubkeys: str) -> None:
    if not tools.has_account_defined(exit_error=False):
        # check input pubkeys
        if not pubkeys:
            ctx.fail("You should specify one or many pubkeys")
        pubkeys_list = []
        wrong_pubkeys = False
        for input_pubkey in pubkeys:
            checked_pubkey = is_pubkey_and_check(input_pubkey)
            if checked_pubkey:
                pubkey = str(checked_pubkey)
            else:
                pubkey = input_pubkey
                wrong_pubkeys = True
                click.echo(f"ERROR: pubkey {pubkey} has a wrong format")
            if pubkey in pubkeys_list:
                ctx.fail(
                    f"Pubkey {gen_pubkey_checksum(pubkey)} was specified many times",
                )
            pubkeys_list.append(pubkey)
        if wrong_pubkeys:
            ctx.fail("Please check the pubkeys format reported above.")

        total = [0, 0]
        for pubkey in pubkeys_list:
            inputs_balance = m_tools.get_amount_from_pubkey(pubkey)
            show_amount_from_pubkey(pubkey, inputs_balance)
            total[0] += inputs_balance[0]
            total[1] += inputs_balance[1]
        if len(pubkeys_list) > 1:
            show_amount_from_pubkey("Total", total)
    else:
        key = auth_method()
        pubkey = key.pubkey
        show_amount_from_pubkey(pubkey, m_tools.get_amount_from_pubkey(pubkey))


def show_amount_from_pubkey(label: str, inputs_balance: list[int]) -> None:
    """
    Shows the balance of a pubkey.
    `label` can be either a pubkey or "Total".
    """
    totalAmountInput = inputs_balance[0]
    balance = inputs_balance[1]
    currency_symbol = tools.get_currency_symbol()
    ud_value = m_tools.get_ud_value()
    average = get_average()
    member = None

    # if `pubkey` is a pubkey, get pubkey:checksum and uid
    if label != "Total":
        member = wt.is_member(label)
        label = gen_pubkey_checksum(label)
    # display balance table
    display = []
    display.append(["Balance of pubkey", label])

    if member:
        display.append(["User identifier", member["uid"]])

    if totalAmountInput - balance != 0:
        m_tools.display_amount(
            display,
            "Blockchain",
            balance,
            ud_value,
            currency_symbol,
        )
        m_tools.display_amount(
            display,
            "Pending transaction",
            (totalAmountInput - balance),
            ud_value,
            currency_symbol,
        )
    m_tools.display_amount(
        display,
        "Total balance",
        totalAmountInput,
        ud_value,
        currency_symbol,
    )
    if average:
        display.append(
            [
                "Total relative to M/N",
                f"{round(totalAmountInput / average, 2)} x M/N",
            ],
        )

    table = tui.Table()
    table.fill_rows(display)
    click.echo(table.draw())


def get_average() -> Optional[int]:
    head = get_head_block()
    try:
        return head["monetaryMass"] / head["membersCount"]
    except ZeroDivisionError:
        print("The currency reached zero members")
        return None
