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

from pathlib import Path

from silkaj import tools
from silkaj.blockchain import tools as bc_tools


class AccountStorage:
    xdg_data_home = ".local/share"
    program_name = "silkaj"
    revocation_file_name = "revocation.txt"
    authentication_v1_file_name = "authentication_file_ed25519.dewif"
    authentication_v2_file_name = "authentication_file_sr25519.json"

    def __init__(self) -> None:
        self.account_name = tools.has_account_defined()

        self.path = Path.home().joinpath(
            self.xdg_data_home,
            self.program_name,
            bc_tools.get_currency(),
            self.account_name,
        )
        self.path.mkdir(parents=True, exist_ok=True)

    def authentication_file_path(self, check_exist: bool = True) -> Path:
        auth_file_path = self.path.joinpath(self.authentication_v1_file_name)
        if check_exist and not auth_file_path.is_file():
            tools.click_fail(
                f"{auth_file_path} not found for account name: {self.account_name}",
            )
        return auth_file_path

    def revocation_path(self, check_exist: bool = True) -> Path:
        revocation_path = self.path.joinpath(self.revocation_file_name)
        if check_exist and not revocation_path.is_file():
            tools.click_fail(
                f"{revocation_path} not found for account name: {self.account_name}",
            )
        return revocation_path
