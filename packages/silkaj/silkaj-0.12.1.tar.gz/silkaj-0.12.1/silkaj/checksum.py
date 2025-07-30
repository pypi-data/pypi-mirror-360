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

import re

import rich_click as click

from silkaj import auth, tools
from silkaj.public_key import (
    PUBKEY_CHECKSUM_PATTERN,
    PUBKEY_DELIMITED_PATTERN,
    gen_checksum,
    gen_pubkey_checksum,
)

MESSAGE = "You should specify a pubkey or an authentication method"


@click.command(
    "checksum",
    help="Generate checksum out of a passed pubkey or an authentication method. \
Checks if the passed checksum is valid.",
)
@click.argument("pubkey_checksum", nargs=-1)
def checksum_command(pubkey_checksum: str) -> None:
    if tools.has_account_defined(exit_error=False):
        key = auth.auth_method()
        click.echo(gen_pubkey_checksum(key.pubkey))
    elif not pubkey_checksum:
        tools.click_fail(MESSAGE)
    elif re.search(re.compile(PUBKEY_DELIMITED_PATTERN), pubkey_checksum[0]):
        click.echo(gen_pubkey_checksum(pubkey_checksum[0]))
    elif re.search(re.compile(PUBKEY_CHECKSUM_PATTERN), pubkey_checksum[0]):
        pubkey, checksum = pubkey_checksum[0].split(":")
        if checksum == gen_checksum(pubkey):
            click.echo("The checksum is valid")
        else:
            click.echo("The checksum is invalid")
    else:
        tools.click_fail("Wrong public key format")
