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

import pendulum
import rich_click as click

from silkaj.blockchain.tools import get_head_block
from silkaj.constants import ALL
from silkaj.network import determine_endpoint
from silkaj.tools import get_currency_symbol


@click.command("info", help="Currency information")
def currency_info() -> None:
    head_block = get_head_block()
    ep = determine_endpoint()
    current_time = pendulum.from_timestamp(head_block["time"], tz="local")
    mediantime = pendulum.from_timestamp(head_block["medianTime"], tz="local")
    print(
        "Connected to node:",
        ep.host,
        ep.port,
        "\nCurrent block number:",
        head_block["number"],
        "\nCurrency name:",
        get_currency_symbol(),
        "\nNumber of members:",
        head_block["membersCount"],
        "\nMinimal Proof-of-Work:",
        head_block["powMin"],
        "\nCurrent time:",
        current_time.format(ALL),
        "\nMedian time:",
        mediantime.format(ALL),
        "\nDifference time:",
        current_time.diff_for_humans(mediantime, True),
    )
