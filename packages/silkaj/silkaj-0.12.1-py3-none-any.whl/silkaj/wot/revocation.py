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

import os
import sys
from pathlib import Path

import rich_click as click
from duniterpy.api import bma
from duniterpy.documents.block_id import BlockID
from duniterpy.documents.document import MalformedDocumentError
from duniterpy.documents.identity import Identity
from duniterpy.documents.revocation import Revocation
from duniterpy.key.verifying_key import VerifyingKey

from silkaj import auth, network, tui
from silkaj.account_storage import AccountStorage
from silkaj.blockchain import tools as bc_tools
from silkaj.constants import FAILURE_EXIT_STATUS, SUCCESS_EXIT_STATUS
from silkaj.public_key import gen_pubkey_checksum
from silkaj.wot import idty_tools
from silkaj.wot import tools as w_tools


@click.command("create", help="Create and save revocation document")
def create() -> None:
    currency = bc_tools.get_currency()

    key = auth.auth_method()
    gen_pubkey_checksum(key.pubkey)
    _id = (w_tools.choose_identity(key.pubkey))[0]
    rev_doc = create_revocation_doc(_id, key.pubkey, currency)
    rev_doc.sign(key)

    idty_table = idty_tools.display_identity(rev_doc.identity)
    click.echo(idty_table.draw())

    revocation_file_path = AccountStorage().revocation_path(check_exist=False)

    confirm_message = "Do you want to save the revocation document for this identity?"
    if click.confirm(confirm_message):
        save_doc(revocation_file_path, rev_doc.signed_raw(), key.pubkey)
    else:
        click.echo("Ok, goodbye!")


@click.command(
    "revoke",
    help="Create and publish revocation document. Will immediately revoke the identity.",
)
@click.pass_context
def revoke_now(ctx: click.Context) -> None:
    currency = bc_tools.get_currency()

    warn_before_dry_run_or_display(ctx)

    key = auth.auth_method()
    gen_pubkey_checksum(key.pubkey)
    _id = (w_tools.choose_identity(key.pubkey))[0]
    rev_doc = create_revocation_doc(_id, key.pubkey, currency)
    rev_doc.sign(key)

    if ctx.obj["DRY_RUN"]:
        click.echo(rev_doc.signed_raw())
        return

    idty_table = idty_tools.display_identity(rev_doc.identity)
    click.echo(idty_table.draw())
    if ctx.obj["DISPLAY_DOCUMENT"]:
        click.echo(rev_doc.signed_raw())

    warn_before_sending_document()
    network.send_document(bma.wot.revoke, rev_doc)


@click.command(
    "verify",
    help="Verifies that the revocation document is correctly formatted and matches an existing identity",
)
def verify() -> None:
    revocation_file_path = AccountStorage().revocation_path()
    rev_doc = verify_document(revocation_file_path)
    idty_table = idty_tools.display_identity(rev_doc.identity)
    click.echo(idty_table.draw())
    click.echo("Revocation document is valid.")


@click.command(
    "publish",
    help="Publish previously created revocation document. Identity will be immediately revoked.",
)
@click.pass_context
def publish(ctx: click.Context) -> None:
    revocation_file_path = AccountStorage().revocation_path()
    warn_before_dry_run_or_display(ctx)

    rev_doc = verify_document(revocation_file_path)
    if ctx.obj["DRY_RUN"]:
        click.echo(rev_doc.signed_raw())
        return

    idty_table = idty_tools.display_identity(rev_doc.identity)
    click.echo(idty_table.draw())
    if ctx.obj["DISPLAY_DOCUMENT"]:
        click.echo(rev_doc.signed_raw())

    warn_before_sending_document()
    network.send_document(bma.wot.revoke, rev_doc)


def warn_before_dry_run_or_display(ctx: click.Context) -> None:
    if ctx.obj["DRY_RUN"]:
        click.echo("WARNING: the document will only be displayed and will not be sent.")


def warn_before_sending_document() -> None:
    click.secho("/!\\WARNING/!\\", blink=True, fg="red")
    click.echo(
        "This identity will be revoked.\n\
It will cease to be member and to create the Universal Dividend.\n\
All currently sent certifications will remain valid until they expire.",
    )
    tui.send_doc_confirmation("revocation document immediately")


def create_revocation_doc(_id: dict, pubkey: str, currency: str) -> Revocation:
    """
    Creates an unsigned revocation document.
    _id is the dict object containing id infos from request wot.requirements
    """
    idty = Identity(
        currency=currency,
        pubkey=pubkey,
        uid=_id["uid"],
        block_id=BlockID.from_str(_id["meta"]["timestamp"]),
    )
    idty.signature = _id["self"]
    return Revocation(
        currency=currency,
        identity=idty,
    )


def opener_user_rw(path, flags):
    return os.open(path, flags, 0o600)


def save_doc(rev_path: Path, content: str, pubkey: str) -> None:
    pubkey_cksum = gen_pubkey_checksum(pubkey)
    # Ask confirmation if the file exists
    if rev_path.is_file():
        if click.confirm(
            f"Would you like to erase existing file `{rev_path}` with the \
generated revocation document corresponding to {pubkey_cksum} public key?",
        ):
            rev_path.unlink()
        else:
            click.echo("Ok, goodbye!")
            sys.exit(SUCCESS_EXIT_STATUS)
    with open(rev_path, "w", encoding="utf-8", opener=opener_user_rw) as fh:
        fh.write(content)
    click.echo(
        f"Revocation document file stored into `{rev_path}` for following public key: {pubkey_cksum}",
    )


def verify_document(doc: Path) -> Revocation:
    """
    This checks that:
      - that the revocation signature is valid.
      - if the identity is unique (warns the user)
    It returns the revocation document or exits.
    """
    error_invalid_sign = "Error: the signature of the revocation document is invalid."
    error_invalid_doc = (
        f"Error: {doc} is not a revocation document, or is not correctly formatted."
    )

    original_doc = doc.read_text(encoding="utf-8")

    try:
        rev_doc = Revocation.from_signed_raw(original_doc)
    except (MalformedDocumentError, IndexError):
        sys.exit(error_invalid_doc)

    verif_key = VerifyingKey(rev_doc.pubkey)
    if not verif_key.check_signature(rev_doc.raw(), rev_doc.signature):
        sys.exit(error_invalid_sign)

    many_idtys = idty_tools.check_many_identities(rev_doc)
    if many_idtys:
        return rev_doc
    sys.exit(FAILURE_EXIT_STATUS)
