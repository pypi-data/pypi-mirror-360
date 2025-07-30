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

import urllib

import rich_click as click

from silkaj.network import exit_on_http_error
from silkaj.public_key import gen_pubkey_checksum, is_pubkey_and_check
from silkaj.wot import tools as wt


@click.command("lookup", help="Username identifier and public key lookup")
@click.argument("uid_pubkey")
def lookup_cmd(uid_pubkey: str) -> None:
    checked_pubkey = is_pubkey_and_check(uid_pubkey)
    if checked_pubkey:
        uid_pubkey = str(checked_pubkey)

    try:
        lookups = wt.wot_lookup(uid_pubkey)
    except urllib.error.HTTPError as e:
        exit_on_http_error(e, 404, f"No identity found for {uid_pubkey}")

    content = f"Public keys or user id found matching '{uid_pubkey}':\n"
    for lookup in lookups:
        for identity in lookup["uids"]:
            pubkey_checksum = gen_pubkey_checksum(lookup["pubkey"])
            content += f"\n→ {pubkey_checksum} ↔ {identity['uid']}"
    click.echo(content)
