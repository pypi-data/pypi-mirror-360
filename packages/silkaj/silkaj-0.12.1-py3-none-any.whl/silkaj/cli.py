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

import rich_click as click
from duniterpy.api.endpoint import endpoint as du_endpoint

from silkaj import tools
from silkaj.about import about
from silkaj.auth import generate_auth_file
from silkaj.blockchain.blocks import list_blocks
from silkaj.blockchain.difficulty import difficulties
from silkaj.blockchain.information import currency_info
from silkaj.checksum import checksum_command
from silkaj.constants import (
    G1_DEFAULT_ENDPOINT,
    G1_TEST_DEFAULT_ENDPOINT,
    SILKAJ_VERSION,
)
from silkaj.g1_monetary_license import license_command
from silkaj.money.balance import balance_cmd
from silkaj.money.history import transaction_history
from silkaj.money.transfer import transfer_money
from silkaj.wot import certify, revocation
from silkaj.wot.lookup import lookup_cmd
from silkaj.wot.membership import send_membership
from silkaj.wot.status import status

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.OPTION_GROUPS = {
    "silkaj": [
        {
            "name": "Basic options",
            "options": ["--help", "--version"],
        },
        {
            "name": "Endpoint and currency specification",
            "options": ["--endpoint", "--gtest"],
        },
        {
            "name": "Account and authentication specification",
            "options": ["--account", "--password"],
        },
    ],
}


@click.group()
@click.help_option("-h", "--help")
@click.version_option(SILKAJ_VERSION, "-v", "--version")
@click.option(
    "--endpoint",
    "-ep",
    help=f"Without specifying this option, the default endpoint reaches Ğ1 currency on its official endpoint: https://{du_endpoint(G1_DEFAULT_ENDPOINT).host}. \
--endpoint allows to specify a custom endpoint following `<host>:<port>/<path>` format. \
`port` and `path` are optional. In case no port is specified, it defaults to 443.",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["gtest"],
)
@click.option(
    "--gtest",
    "-gt",
    is_flag=True,
    help=f"Uses official ĞTest currency endpoint: https://{du_endpoint(G1_TEST_DEFAULT_ENDPOINT).host}",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["endpoint"],
)
@click.option(
    "account_name",
    "--account",
    "-a",
    help="Account name used in storage `$HOME/.local/share/silkaj/$currency/$account_name` for authentication and revocation.",
)
@click.option(
    "--password",
    "-p",
    help="EWIF authentication password. If you use this option, prefix the command \
with a space so the password is not saved in your shell history. \
In case of an encrypted file, password input will be prompted.",
)
@click.option(
    "--display",
    "-d",
    is_flag=True,
    help="Display the generated document before sending it",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="By-pass the licence and confirmation. Do not send the document, but display it instead",
)
@click.pass_context
def cli(
    ctx: click.Context,
    endpoint: str,
    gtest: bool,
    account_name: str,
    password: str,
    display: bool,
    dry_run: bool,
) -> None:
    if display and dry_run:
        ctx.fail("Display and dry-run options can not be used together")

    ctx.obj = {}
    ctx.ensure_object(dict)
    ctx.obj["ENDPOINT"] = endpoint
    ctx.obj["GTEST"] = gtest
    ctx.obj["ACCOUNT_NAME"] = account_name
    ctx.obj["PASSWORD"] = password
    ctx.obj["DISPLAY_DOCUMENT"] = display
    ctx.obj["DRY_RUN"] = dry_run
    ctx.help_option_names = ["-h", "--help"]


cli.add_command(about)
cli.add_command(generate_auth_file)
cli.add_command(checksum_command)
cli.add_command(license_command)


@cli.group("blockchain", help="Blockchain related commands")
def blockchain_group() -> None:
    pass


blockchain_group.add_command(list_blocks)
blockchain_group.add_command(difficulties)
blockchain_group.add_command(currency_info)


@cli.group("money", help="Money management related commands")
def money_group() -> None:
    pass


money_group.add_command(balance_cmd)
money_group.add_command(transaction_history)
money_group.add_command(transfer_money)


@cli.group("wot", help="Web-of-Trust related commands")
def wot_group() -> None:
    pass


wot_group.add_command(certify.certify)
with contextlib.suppress(ModuleNotFoundError):
    from silkaj.wot.exclusions import exclusions_command

    wot_group.add_command(exclusions_command)

wot_group.add_command(lookup_cmd)
wot_group.add_command(send_membership)
wot_group.add_command(status)


@wot_group.group("revocation", help="Manage revocation document commands.")
def revocation_group() -> None:
    pass


revocation_group.add_command(revocation.create)
revocation_group.add_command(revocation.verify)
revocation_group.add_command(revocation.publish)
revocation_group.add_command(revocation.revoke_now)
