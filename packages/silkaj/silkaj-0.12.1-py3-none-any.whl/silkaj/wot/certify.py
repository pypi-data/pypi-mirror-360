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

import sys

import pendulum
import rich_click as click
from duniterpy.api import bma
from duniterpy.api.client import Client
from duniterpy.documents import Block, BlockID, Certification, Identity, get_block_id
from duniterpy.key import SigningKey

from silkaj import tui
from silkaj.auth import auth_method
from silkaj.blockchain import tools as bc_tools
from silkaj.constants import ALL, DATE
from silkaj.g1_monetary_license import license_approval
from silkaj.network import client_instance, send_document
from silkaj.public_key import gen_pubkey_checksum, is_pubkey_and_check
from silkaj.wot import tools as wot_tools


@click.command("certify", help="Certify identity")
@click.argument("uid_pubkey_to_certify")
@click.pass_context
def certify(ctx: click.Context, uid_pubkey_to_certify: str) -> None:
    client = client_instance()

    checked_pubkey = is_pubkey_and_check(uid_pubkey_to_certify)
    if checked_pubkey:
        uid_pubkey_to_certify = str(checked_pubkey)

    idty_to_certify, pubkey_to_certify, send_certs = wot_tools.choose_identity(
        uid_pubkey_to_certify,
    )

    # Authentication
    key = auth_method()

    issuer_pubkey = key.pubkey
    issuer = pre_checks(client, issuer_pubkey, pubkey_to_certify)

    # Display license and ask for confirmation
    head = bc_tools.get_head_block()
    currency = head["currency"]
    license_approval(currency)

    # Certification confirmation
    certification_confirmation(
        ctx,
        issuer,
        issuer_pubkey,
        pubkey_to_certify,
        idty_to_certify,
    )

    # Create and sign certification document
    certification = docs_generation(
        currency,
        pubkey_to_certify,
        idty_to_certify,
        issuer_pubkey,
        head,
        key,
    )

    if ctx.obj["DISPLAY_DOCUMENT"]:
        click.echo(certification.signed_raw(), nl=False)
        tui.send_doc_confirmation("certification")

    # Send certification document
    send_document(bma.wot.certify, certification)


def pre_checks(client: Client, issuer_pubkey: str, pubkey_to_certify: str) -> dict:
    # Check whether current user is member
    issuer = wot_tools.is_member(issuer_pubkey)
    if not issuer:
        sys.exit("Current identity is not member.")

    if issuer_pubkey == pubkey_to_certify:
        sys.exit("You can't certify yourself!")

    # Check if the certification can be renewed
    params = bc_tools.get_blockchain_parameters()
    requirements = client(bma.wot.requirements, pubkey_to_certify, pubkey=True)
    req = requirements["identities"][0]  # type: dict
    for cert in req["certifications"]:
        if cert["from"] == issuer_pubkey:
            # Ğ1: 0<->2y - 2y + 2m
            # ĞT: 0<->4.8m - 4.8m + 12.5d
            renewable = cert["expiresIn"] - params["sigValidity"] + params["sigReplay"]
            if renewable > 0:
                renewable_date = pendulum.now().add(seconds=renewable).format(DATE)
                sys.exit(f"Certification renewable from {renewable_date}")

    # Check if the certification is already in the pending certifications
    for pending_cert in req["pendingCerts"]:
        if pending_cert["from"] == issuer_pubkey:
            sys.exit("Certification is currently being processed")
    return issuer


def certification_confirmation(
    ctx: click.Context,
    issuer: dict,
    issuer_pubkey: str,
    pubkey_to_certify: str,
    idty_to_certify: dict,
) -> None:
    cert = []
    client = client_instance()
    idty_timestamp = idty_to_certify["meta"]["timestamp"]
    block_id_idty = get_block_id(idty_timestamp)
    block = client(bma.blockchain.block, block_id_idty.number)
    timestamp_date = pendulum.from_timestamp(block["time"], tz="local").format(ALL)
    block_id_date = f": #{idty_timestamp[:15]}… {timestamp_date}"
    cert.append(["ID", issuer["uid"], "->", idty_to_certify["uid"] + block_id_date])
    cert.append(
        [
            "Pubkey",
            gen_pubkey_checksum(issuer_pubkey),
            "->",
            gen_pubkey_checksum(pubkey_to_certify),
        ],
    )
    params = bc_tools.get_blockchain_parameters()
    cert_ends = pendulum.now().add(seconds=params["sigValidity"]).format(DATE)
    cert.append(["Valid", pendulum.now().format(DATE), "—>", cert_ends])

    table = tui.Table()
    table.fill_rows(
        cert,
        ["Cert", "Issuer", "->", "Recipient: Published: #block-hash date"],
    )
    click.echo(table.draw())

    if not ctx.obj["DISPLAY_DOCUMENT"]:
        tui.send_doc_confirmation("certification")


def docs_generation(
    currency: str,
    pubkey_to_certify: str,
    idty_to_certify: dict,
    issuer_pubkey: str,
    head: Block,
    key: SigningKey,
) -> Certification:
    identity = Identity(
        pubkey=pubkey_to_certify,
        uid=idty_to_certify["uid"],
        block_id=get_block_id(idty_to_certify["meta"]["timestamp"]),
        currency=currency,
    )
    identity.signature = idty_to_certify["self"]

    return Certification(
        pubkey_from=issuer_pubkey,
        identity=identity,
        block_id=BlockID(head["number"], head["hash"]),
        signing_key=key,
        currency=currency,
    )
