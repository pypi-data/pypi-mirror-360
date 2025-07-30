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

import hashlib
import re
from typing import Any, Optional, Union

import base58

from silkaj.constants import PUBKEY_PATTERN, SHORT_PUBKEY_SIZE
from silkaj.tools import message_exit

PUBKEY_DELIMITED_PATTERN = f"^{PUBKEY_PATTERN}$"
CHECKSUM_SIZE = 3
CHECKSUM_PATTERN = f"[1-9A-HJ-NP-Za-km-z]{{{CHECKSUM_SIZE}}}"
PUBKEY_CHECKSUM_PATTERN = f"^{PUBKEY_PATTERN}:{CHECKSUM_PATTERN}$"


def is_pubkey_and_check(pubkey: str) -> Union[str, bool]:
    """
    Checks if the given argument contains a pubkey.
    If so, verifies the checksum if needed and returns the pubkey.
    Exits if the checksum is wrong.
    Else, return False
    """
    if re.search(re.compile(PUBKEY_PATTERN), pubkey):
        if check_pubkey_format(pubkey, True):
            return validate_checksum(pubkey)
        return pubkey
    return False


def check_pubkey_format(pubkey: str, display_error: bool = True) -> Optional[bool]:
    """
    Checks if a pubkey has a checksum.
    Exits if the pubkey is invalid.
    """
    if re.search(re.compile(PUBKEY_DELIMITED_PATTERN), pubkey):
        return False
    if re.search(re.compile(PUBKEY_CHECKSUM_PATTERN), pubkey):
        return True
    if display_error:
        message_exit(f"Error: bad format for following public key: {pubkey}")
    return None


def validate_checksum(pubkey_checksum: str) -> Any:
    """
    Check pubkey checksum after the pubkey, delimited by ":".
    If check pass: return pubkey
    Else: exit.
    """
    pubkey, checksum = pubkey_checksum.split(":")
    if checksum == gen_checksum(pubkey):
        return pubkey
    message_exit(
        f"Error: public key '{pubkey}' does not match checksum '{checksum}'.\n\
Please verify the public key.",
    )
    return None


def gen_checksum(pubkey: str) -> str:
    """
    Returns the checksum of the input pubkey (encoded in b58)
    """
    pubkey_byte = base58.b58decode(pubkey)
    _hash = hashlib.sha256(hashlib.sha256(pubkey_byte).digest()).digest()
    return str(base58.b58encode(_hash)[:3].decode("utf-8"))


def gen_pubkey_checksum(
    pubkey: str,
    short: Optional[bool] = False,
    length: Optional[int] = SHORT_PUBKEY_SIZE,
) -> str:
    """
    Returns "<pubkey>:<checksum>" in full form.
    returns `length` first chars of pubkey and checksum in short form.
    `length` defaults to SHORT_PUBKEY_SIZE.
    """
    short_pubkey = f"{pubkey[:length]}…" if short else pubkey
    return f"{short_pubkey}:{gen_checksum(pubkey)}"
