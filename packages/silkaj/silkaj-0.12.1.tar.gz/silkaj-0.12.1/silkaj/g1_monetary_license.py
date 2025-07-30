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

import rich_click as click

import g1_monetary_license as gml


def license_approval(currency: str) -> None:
    if currency != "g1":
        return
    if click.confirm(
        "You will be asked to approve Ğ1 license. Would you like to display it?",
    ):
        g1ml = G1MonetaryLicense()
        g1ml.display_license()
    click.confirm("Do you approve Ğ1 license?", abort=True)


@click.command("license", help="Display Ğ1 monetary license")
def license_command() -> None:
    g1ml = G1MonetaryLicense()
    g1ml.display_license()


class G1MonetaryLicense:
    def __init__(self):
        self.licenses_dir_path = gml.__path__.__dict__["_path"][0]
        self._available_languages()

    def display_license(self) -> None:
        """
        Determine available languages
        Ask to select a language code
        Display license in the terminal
        """
        selected_language_code = self.language_prompt()
        license_path = self.get_license_path(selected_language_code)
        click.echo_via_pager(license_path.read_text(encoding="utf-8"))

    def language_prompt(self) -> str:
        return click.prompt(
            "In which language would you like to display Ğ1 monetary license?",
            type=click.Choice(self.languages_codes),
            show_choices=True,
            show_default=True,
            default="en",
        )

    def _available_languages(self) -> None:
        """
        Handle long language codes ie: 'fr-FR'
        """
        self.languages_codes = []
        licenses_path = sorted(Path(self.licenses_dir_path).glob(file_name("*")))
        for license_path in licenses_path:
            language_code = license_path.stem[-2:]
            if language_code.isupper():
                language_code = license_path.stem[-5:]
            self.languages_codes.append(language_code)

    def get_license_path(self, language_code: str) -> Path:
        return Path(self.licenses_dir_path, file_name(language_code))


def file_name(language_code: str) -> str:
    return f"g1_monetary_license_{language_code}.rst"
