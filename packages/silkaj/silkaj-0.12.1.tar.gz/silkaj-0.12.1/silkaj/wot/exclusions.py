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
import socket
import sys
import time
import urllib

import pendulum
import rich_click as click
from duniterpy import constants as dp_const
from duniterpy.api.bma import blockchain
from duniterpy.api.client import Client
from duniterpy.documents.block import Block
from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError

from silkaj import constants
from silkaj.blockchain.tools import get_blockchain_parameters
from silkaj.network import client_instance
from silkaj.tools import get_currency_symbol
from silkaj.wot.tools import wot_lookup

G1_CESIUM_URL = "https://demo.cesium.app/"
GTEST_CESIUM_URL = "https://g1-test.cesium.app/"
CESIUM_BLOCK_PATH = "#/app/block/"

DUNITER_FORUM_URL = "https://forum.duniter.org/"
MONNAIE_LIBRE_FORUM_URL = "https://forum.monnaie-libre.fr/"

DUNITER_FORUM_G1_TOPIC_ID = 4393
DUNITER_FORUM_GTEST_TOPIC_ID = 6554
MONNAIE_LIBRE_FORUM_G1_TOPIC_ID = 30219  # 26117, 17627, 8233


@click.command(
    "exclusions",
    help="DeathReaper: Generate membership exclusions messages, \
markdown formatted and publish them on Discourse Forums",
)
@click.option(
    "-a",
    "--api-id",
    help="Username used on Discourse forum API",
)
@click.option(
    "-du",
    "--duniter-forum-api-key",
    help="API key used on Duniter Forum",
)
@click.option(
    "-ml",
    "--ml-forum-api-key",
    help="API key used on Monnaie Libre Forum",
)
@click.argument("days", default=1, type=click.FloatRange(0, 50))
@click.option(
    "--publish",
    is_flag=True,
    help="Publish the messages on the forums, otherwise it will be printed here.",
)
def exclusions_command(api_id, duniter_forum_api_key, ml_forum_api_key, days, publish):
    params = get_blockchain_parameters()
    currency = params["currency"]
    check_options(api_id, duniter_forum_api_key, ml_forum_api_key, publish, currency)
    bma_client = client_instance()
    blocks_to_process = get_blocks_to_process(bma_client, days, params)
    if not blocks_to_process:
        no_exclusion(days, currency)
    message = gen_message_over_blocks(bma_client, blocks_to_process, params)
    if not message:
        no_exclusion(days, currency)
    header = gen_header(blocks_to_process)
    # Add ability to publish just one of the two forum, via a flags?

    publish_display(
        api_id,
        duniter_forum_api_key,
        header + message,
        publish,
        currency,
        "duniter",
    )
    if currency == dp_const.G1_CURRENCY_CODENAME:
        publish_display(
            api_id,
            ml_forum_api_key,
            header + message,
            publish,
            currency,
            "monnaielibre",
        )


def check_options(api_id, duniter_forum_api_key, ml_forum_api_key, publish, currency):
    if publish and (
        not api_id
        or not duniter_forum_api_key
        or (not ml_forum_api_key and currency != dp_const.G1_TEST_CURRENCY_CODENAME)
    ):
        sys.exit(
            f"Error: To be able to publish, api_id, duniter_forum_api, and \
ml_forum_api_key (not required for {constants.GTEST_SYMBOL}) options should be specified",
        )


def no_exclusion(days, currency):
    # Use Humanize
    print(f"No exclusion to report within the last {days} day(s) on {currency}")
    # Success exit status for not failing GitLab job in case there is no exclusions
    sys.exit()


def get_blocks_to_process(bma_client, days, params):
    head_number = bma_client(blockchain.current)["number"]
    block_number_days_ago = (
        head_number - days * 24 * constants.ONE_HOUR / params["avgGenTime"]
    )
    # print(block_number_days_ago) # DEBUG

    i = 0
    blocks_with_excluded = bma_client(blockchain.excluded)["result"]["blocks"]
    for i, block_number in reversed(list(enumerate(blocks_with_excluded))):
        if block_number < block_number_days_ago:
            index = i
            break
    return blocks_with_excluded[index + 1 :]


def gen_message_over_blocks(bma_client, blocks_to_process, params):
    """
    Loop over the list of blocks to retrieve and parse the blocks
    Ignore revocation kind of exclusion
    """
    if params["currency"] == dp_const.G1_CURRENCY_CODENAME:
        es_client = Client(constants.G1_CSP_USER_ENDPOINT)
    else:
        es_client = Client(constants.GTEST_CSP_USER_ENDPOINT)
    message = ""
    for block_number in blocks_to_process:
        logging.info("Processing block number %s", block_number)
        print(f"Processing block number {block_number}")
        # DEBUG / to be removed once the #115 logging system is set

        try:
            block = bma_client(blockchain.block, block_number)
        except urllib.error.HTTPError:
            time.sleep(2)
            block = bma_client(blockchain.block, block_number)
        block_hash = block["hash"]
        block = Block.from_signed_raw(block["raw"] + block["signature"] + "\n")

        if block.revoked and block.excluded[0] == block.revoked[0].pubkey:
            continue
        message += generate_message(es_client, block, block_hash, params)
    return message


def gen_header(blocks_to_process):
    nbr_exclusions = len(blocks_to_process)
    # Handle when there is one block with multiple exclusion within
    # And when there is a revocation
    s = "s" if nbr_exclusions > 1 else ""
    des_du = "des" if nbr_exclusions > 1 else "du"
    currency_symbol = get_currency_symbol()
    header = f"## Exclusion{s} de la toile de confiance {currency_symbol}, perte{s} {des_du} statut{s} de membre"
    message_g1 = "\n> Message automatique. Merci de notifier vos proches de leur exclusion de la toile de confiance."
    return header + message_g1


def generate_message(es_client, block, block_hash, params):
    """
    Loop over exclusions within a block
    Generate identity header + info
    """
    message = ""
    for excluded in block.excluded:
        lookup = wot_lookup(excluded)[0]
        uid = lookup["uids"][0]["uid"]

        pubkey = lookup["pubkey"]
        try:
            response = es_client.get(f"user/profile/{pubkey}/_source")
            es_uid = response["title"]
        except (urllib.error.HTTPError, socket.timeout):
            es_uid = uid
            logging.info("Cesium+ API: Not found pubkey or connection error")

        if params["currency"] == dp_const.G1_CURRENCY_CODENAME:
            cesium_url = G1_CESIUM_URL
        else:
            cesium_url = GTEST_CESIUM_URL
        cesium_url += CESIUM_BLOCK_PATH
        message += f"\n\n### @{uid} [{es_uid}]({cesium_url}{block.number}/{block_hash}?ssl=true)\n"
        message += generate_identity_info(lookup, block, params)
    return message


def generate_identity_info(lookup, block, params):
    info = "- **Certifié·e par**"
    nbr_different_certifiers = 0
    for i, certifier in enumerate(lookup["uids"][0]["others"]):
        if certifier["uids"][0] not in info:
            nbr_different_certifiers += 1
        info += elements_inbetween_list(i, lookup["uids"][0]["others"])
        info += "@" + certifier["uids"][0]
    if lookup["signed"]:
        info += ".\n- **A certifié**"
    for i, certified in enumerate(lookup["signed"]):
        info += elements_inbetween_list(i, lookup["signed"])
        info += "@" + certified["uid"]
    dt = pendulum.from_timestamp(block.mediantime + constants.ONE_HOUR, tz="local")
    info += ".\n- **Exclu·e le** " + dt.format("LLLL zz", locale="fr")
    info += "\n- **Raison de l'exclusion** : "
    if nbr_different_certifiers < params["sigQty"]:
        info += "manque de certifications"
    else:
        info += "expiration du document d'adhésion"
    # a renouveller tous les ans (variable) humanize(params[""])
    return info


def elements_inbetween_list(i, cert_list):
    return " " if i == 0 else (" et " if i + 1 == len(cert_list) else ", ")


def publish_display(api_id, forum_api_key, message, publish, currency, forum):
    if publish:
        topic_id = get_topic_id(currency, forum)
        publish_message_on_the_forum(api_id, forum_api_key, message, topic_id, forum)
    elif forum == "duniter":
        click.echo(message)


def get_topic_id(currency, forum):
    if currency == dp_const.G1_CURRENCY_CODENAME:
        if forum == "duniter":
            return DUNITER_FORUM_G1_TOPIC_ID
        return MONNAIE_LIBRE_FORUM_G1_TOPIC_ID
    return DUNITER_FORUM_GTEST_TOPIC_ID


def publish_message_on_the_forum(api_id, forum_api_key, message, topic_id, forum):
    if forum == "duniter":
        discourse_client = DiscourseClient(
            DUNITER_FORUM_URL,
            api_username=api_id,
            api_key=forum_api_key,
        )
    else:
        discourse_client = DiscourseClient(
            MONNAIE_LIBRE_FORUM_URL,
            api_username=api_id,
            api_key=forum_api_key,
        )
    try:
        response = discourse_client.create_post(message, topic_id=topic_id)
        publication_link(forum, response, topic_id)
    except DiscourseClientError:
        logging.exception("Issue publishing on %s", forum)
        # Handle DiscourseClient exceptions, pass them to the logger

    # discourse_client.close()
    # How to close this client? It looks like it is not implemented
    # May be by closing requests' client


def publication_link(forum, response, topic_id):
    forum_url = DUNITER_FORUM_URL if forum == "duniter" else MONNAIE_LIBRE_FORUM_URL
    print(f"Published on {forum_url}t/{response['topic_slug']}/{topic_id!s}/last")
