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

import functools

from duniterpy.api.bma import blockchain

from silkaj.network import client_instance


@functools.lru_cache(maxsize=1)
def get_blockchain_parameters() -> dict:
    client = client_instance()
    return client(blockchain.parameters)


@functools.lru_cache(maxsize=1)
def get_head_block() -> dict:
    client = client_instance()
    return client(blockchain.current)


@functools.lru_cache(maxsize=1)
def get_currency() -> str:
    return get_head_block()["currency"]
