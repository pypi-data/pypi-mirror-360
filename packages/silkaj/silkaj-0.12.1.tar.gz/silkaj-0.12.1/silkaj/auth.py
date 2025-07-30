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
from pathlib import Path
from typing import Optional

import rich_click as click
from duniterpy.key.scrypt_params import ScryptParams
from duniterpy.key.signing_key import SigningKey, SigningKeyException

from silkaj import tools
from silkaj.account_storage import AccountStorage
from silkaj.constants import PUBKEY_PATTERN
from silkaj.public_key import gen_pubkey_checksum

SEED_HEX_PATTERN = "^[0-9a-fA-F]{64}$"
PUBSEC_PUBKEY_PATTERN = f"pub: ({PUBKEY_PATTERN})"
PUBSEC_SIGNKEY_PATTERN = "sec: ([1-9A-HJ-NP-Za-km-z]{87,90})"


@click.pass_context
def auth_method(ctx: click.Context) -> SigningKey:
    """Account storage authentication"""
    password = ctx.obj["PASSWORD"]
    authfile = AccountStorage().authentication_file_path()
    wif_content = authfile.read_text()
    regex = re.compile("Type: ([a-zA-Z]+)", re.MULTILINE)
    match = re.search(regex, wif_content)
    if match and match.groups()[0] == "EWIF" and not password:
        password = click.prompt("Encrypted WIF, enter your password", hide_input=True)
    return auth_by_wif_file(authfile, password)


def auth_options(
    auth_file: Path,
    auth_seed: bool,
    auth_wif: bool,
    nrp: Optional[str] = None,
) -> SigningKey:
    """Authentication from CLI options"""
    if auth_file:
        return auth_by_auth_file(auth_file)
    if auth_seed:
        return auth_by_seed()
    if auth_wif:
        return auth_by_wif()
    return auth_by_scrypt(nrp)


@click.command("authentication", help="Generate and store authentication file")
@click.option(
    "--auth-scrypt",
    "--scrypt",
    is_flag=True,
    help="Scrypt authentication. Default method",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["auth_file", "auth_seed", "auth_wif"],
)
@click.option("--nrp", help='Scrypt parameters: defaults N,r,p: "4096,16,1"')
@click.option(
    "--auth-file",
    "-af",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Seed hexadecimal authentication from file path",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["auth_scrypt", "auth_seed", "auth_wif"],
)
@click.option(
    "--auth-seed",
    "--seed",
    is_flag=True,
    help="Seed hexadecimal authentication",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["auth_scrypt", "auth_file", "auth_wif"],
)
@click.option(
    "--auth-wif",
    "--wif",
    is_flag=True,
    help="WIF and EWIF authentication methods",
    cls=tools.MutuallyExclusiveOption,
    mutually_exclusive=["auth_scrypt", "auth_file", "auth_seed"],
)
@click.option(
    "--password",
    "-p",
    help="EWIF encryption password for the destination file. \
If no password argument is passed, WIF format will be used. \
If you use this option prefix the command \
with a space so the password does not get saved in your shell history. \
Password input will be suggested via a prompt.",
)
@click.pass_context
def generate_auth_file(
    ctx: click.Context,
    auth_scrypt: bool,
    nrp: Optional[str],
    auth_file: Path,
    auth_seed: bool,
    auth_wif: bool,
    password: Optional[str],
) -> None:
    auth_file_path = AccountStorage().authentication_file_path(check_exist=False)

    if not password and click.confirm(
        "Would you like to encrypt the generated authentication file?",
    ):
        password = click.prompt("Enter encryption password", hide_input=True)

    if password:
        password_confirmation = click.prompt(
            "Enter encryption password confirmation",
            hide_input=True,
        )
        if password != password_confirmation:
            tools.click_fail("Entered passwords differ")

    key = auth_options(auth_file, auth_seed, auth_wif, nrp)
    pubkey_cksum = gen_pubkey_checksum(key.pubkey)
    if auth_file_path.is_file():
        message = (
            f"Would you like to erase {auth_file_path} with an authentication file corresponding \
to following pubkey `{pubkey_cksum}`?"
        )
        click.confirm(message, abort=True)
    if password:
        key.save_ewif_file(auth_file_path, password)
    else:
        key.save_wif_file(auth_file_path)
    print(
        f"Authentication file '{auth_file_path}' generated and stored for public key: {pubkey_cksum}",
    )


@click.pass_context
def auth_by_auth_file(ctx: click.Context, authfile: Path) -> SigningKey:
    """
    Uses an authentication file to generate the key
    Authfile can either be:
    * A seed in hexadecimal encoding
    * PubSec format with public and private key in base58 encoding
    """
    filetxt = authfile.read_text(encoding="utf-8")

    # two regural expressions for the PubSec format
    regex_pubkey = re.compile(PUBSEC_PUBKEY_PATTERN, re.MULTILINE)
    regex_signkey = re.compile(PUBSEC_SIGNKEY_PATTERN, re.MULTILINE)

    # Seed hexadecimal format
    if re.search(re.compile(SEED_HEX_PATTERN), filetxt):
        return SigningKey.from_seedhex_file(authfile)
    # PubSec format
    if re.search(regex_pubkey, filetxt) and re.search(regex_signkey, filetxt):
        return SigningKey.from_pubsec_file(authfile)
    tools.click_fail("The format of the file is invalid")
    return None


def auth_by_seed() -> SigningKey:
    seedhex = click.prompt("Please enter your seed on hex format", hide_input=True)
    try:
        return SigningKey.from_seedhex(seedhex)
    except SigningKeyException as error:
        tools.click_fail(error)


@click.pass_context
def auth_by_scrypt(ctx: click.Context, nrp: Optional[str]) -> SigningKey:
    salt = click.prompt(
        "Please enter your Scrypt Salt (Secret identifier)",
        hide_input=True,
        default="",
    )
    password = click.prompt(
        "Please enter your Scrypt password (masked)",
        hide_input=True,
        default="",
    )

    if nrp:
        a, b, c = nrp.split(",")

        if a.isnumeric() and b.isnumeric() and c.isnumeric():
            n, r, p = int(a), int(b), int(c)
            if n <= 0 or n > 65536 or r <= 0 or r > 512 or p <= 0 or p > 32:
                tools.click_fail("The values of Scrypt parameters are not good")
            scrypt_params = ScryptParams(n, r, p)
        else:
            tools.click_fail("one of n, r or p is not a number")
    else:
        scrypt_params = None

    try:
        return SigningKey.from_credentials(salt, password, scrypt_params)
    except SigningKeyException as error:
        tools.click_fail(error)


def auth_by_wif() -> SigningKey:
    wif_hex = click.prompt(
        "Enter your WIF or Encrypted WIF address (masked)",
        hide_input=True,
    )
    password = click.prompt(
        "(Leave empty in case WIF format) Enter the Encrypted WIF password (masked)",
        hide_input=True,
    )
    try:
        return SigningKey.from_wif_or_ewif_hex(wif_hex, password)
    except SigningKeyException as error:
        tools.click_fail(error)


def auth_by_wif_file(wif_file: Path, password: Optional[str] = None) -> SigningKey:
    try:
        return SigningKey.from_wif_or_ewif_file(wif_file, password)
    except SigningKeyException as error:
        tools.click_fail(error)
