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

import logging

import pendulum
import rich_click as click
from duniterpy.api import bma
from duniterpy.documents import BlockID, Membership, get_block_id
from duniterpy.key import SigningKey

from silkaj import auth, tui
from silkaj.blockchain import tools as bc_tools
from silkaj.constants import DATE
from silkaj.g1_monetary_license import license_approval
from silkaj.network import client_instance, send_document
from silkaj.public_key import gen_pubkey_checksum
from silkaj.wot import tools as w_tools


@click.command("membership", help="Send or renew membership.")
@click.pass_context
def send_membership(ctx: click.Context) -> None:
    dry_run = ctx.obj["DRY_RUN"]

    # Authentication
    key = auth.auth_method()

    # Get the identity information
    head_block = bc_tools.get_head_block()
    membership_block_id = BlockID(head_block["number"], head_block["hash"])
    identity = (w_tools.choose_identity(key.pubkey))[0]
    identity_uid = identity["uid"]
    identity_block_id = get_block_id(identity["meta"]["timestamp"])

    # Display license and ask for confirmation
    currency = head_block["currency"]
    if not dry_run:
        license_approval(currency)

    # Confirmation
    display_confirmation_table(identity_uid, key.pubkey, identity_block_id)
    if not dry_run and not ctx.obj["DISPLAY_DOCUMENT"]:
        tui.send_doc_confirmation("membership document for this identity")

    # Create and sign membership document
    membership = generate_membership_document(
        key.pubkey,
        membership_block_id,
        identity_uid,
        identity_block_id,
        currency,
        key,
    )

    logging.debug(membership.signed_raw())

    if dry_run:
        click.echo(membership.signed_raw())
        ctx.exit()

    if ctx.obj["DISPLAY_DOCUMENT"]:
        click.echo(membership.signed_raw())
        tui.send_doc_confirmation("membership document for this identity")

    # Send the membership signed raw document to the node
    send_document(bma.blockchain.membership, membership)


def display_confirmation_table(
    identity_uid: str,
    pubkey: str,
    identity_block_id: BlockID,
) -> None:
    """
    Check whether there is pending memberships already in the mempool
    Display their expiration date

    Actually, sending a membership document works even if the time
    between two renewals is not awaited as for the certification
    """

    client = client_instance()

    identities_requirements = client(bma.wot.requirements, pubkey, pubkey=True)
    for identity_requirements in identities_requirements["identities"]:
        if identity_requirements["uid"] == identity_uid:
            membership_expires = identity_requirements["membershipExpiresIn"]
            pending_expires = identity_requirements["membershipPendingExpiresIn"]
            pending_memberships = identity_requirements["pendingMemberships"]
            break

    table = []
    if membership_expires:
        expires = pendulum.now().add(seconds=membership_expires).diff_for_humans()
        table.append(["Expiration date of current membership", expires])

    if pending_memberships:
        table.append(
            [
                "Number of pending membership(s) in the mempool",
                len(pending_memberships),
            ],
        )

        table.append(
            [
                "Pending membership documents will expire",
                pendulum.now().add(seconds=pending_expires).diff_for_humans(),
            ],
        )

    table.append(["User Identifier (UID)", identity_uid])
    table.append(["Public Key", gen_pubkey_checksum(pubkey)])

    table.append(["Block Identity", str(identity_block_id)[:45] + "…"])

    block = client(bma.blockchain.block, identity_block_id.number)
    table.append(
        [
            "Identity published",
            pendulum.from_timestamp(block["time"], tz="local").format(DATE),
        ],
    )

    params = bc_tools.get_blockchain_parameters()
    table.append(
        [
            "Expiration date of new membership",
            pendulum.now().add(seconds=params["msValidity"]).diff_for_humans(),
        ],
    )

    table.append(
        [
            "Expiration date of new membership from the mempool",
            pendulum.now().add(seconds=params["msPeriod"]).diff_for_humans(),
        ],
    )

    display_table = tui.Table()
    display_table.fill_rows(table)
    click.echo(display_table.draw())


def generate_membership_document(
    pubkey: str,
    membership_block_id: BlockID,
    identity_uid: str,
    identity_block_id: BlockID,
    currency: str,
    key: SigningKey = None,
) -> Membership:
    return Membership(
        issuer=pubkey,
        membership_block_id=membership_block_id,
        uid=identity_uid,
        identity_block_id=identity_block_id,
        currency=currency,
        signing_key=key,
    )
