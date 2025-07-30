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

SILKAJ_VERSION = "0.12.1"
G1_SYMBOL = "Ğ1"
GTEST_SYMBOL = "ĞTest"

G1_DEFAULT_ENDPOINT = "BMAS g1.duniter.org 443"
G1_TEST_DEFAULT_ENDPOINT = "BMAS g1-test.duniter.org 443"

G1_CSP_USER_ENDPOINT = "ES_USER_API g1.data.e-is.pro 443"
GTEST_CSP_USER_ENDPOINT = "ES_USER_API g1-test.data.e-is.pro 443"

ONE_HOUR = 3600

SUCCESS_EXIT_STATUS = 0
FAILURE_EXIT_STATUS = 1

BMA_MAX_BLOCKS_CHUNK_SIZE = 5000
BMA_SLEEP = 0.1
PUBKEY_MIN_LENGTH = 43
PUBKEY_MAX_LENGTH = 44
PUBKEY_PATTERN = f"[1-9A-HJ-NP-Za-km-z]{{{PUBKEY_MIN_LENGTH},{PUBKEY_MAX_LENGTH}}}"

MINIMAL_ABSOLUTE_TX_AMOUNT = 0.01
MINIMAL_RELATIVE_TX_AMOUNT = 1e-6
CENT_MULT_TO_UNIT = 100
SHORT_PUBKEY_SIZE = 8

# pendulum constants
# see https://pendulum.eustace.io/docs/#localized-formats
DATE = "LL"
HOUR = "LTS"
ALL = "LLL"
# Not ISO 8601 compliant but common
ALL_DIGITAL = "YYYY-MM-DD HH:mm:ss"
