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

import shutil
import sys
from typing import Optional

import rich_click as click
from texttable import Texttable

from silkaj import constants

VERT_TABLE_CHARS = ["─", "│", "│", "═"]


def send_doc_confirmation(document_name: str) -> None:
    if not click.confirm(f"Do you confirm sending this {document_name}?"):
        sys.exit(constants.SUCCESS_EXIT_STATUS)


class Table(Texttable):
    def __init__(
        self,
        style="default",
    ):
        super().__init__(max_width=shutil.get_terminal_size().columns)

        if style == "columns":
            self.set_deco(self.HEADER | self.VLINES | self.BORDER)
        self.set_chars(VERT_TABLE_CHARS)

    def fill_rows(self, rows: list[list], header: Optional[list] = None) -> None:
        """
        Fills a table from header and rows list.
        `rows` is a list of lists representing each row content.
        each element of `rows` and header must be of same length.
        """
        if header:
            if len(rows) == 0:
                rows.append([""] * len(header))
            assert len(header) == len(rows[0])
            self.header(header)
        for line in rows:
            assert len(line) == len(rows[0])
            self.add_row(line)

    def fill_from_dict(self, _dict: dict) -> None:
        """
        Given a dict where each value represents a column,
        fill a table where labels are dict keys and columns are dict values
        This function stops on the first line with only empty cells
        """
        keys = list(_dict.keys())
        rows = []

        n = 0
        while True:
            row = []
            empty_cells_number = 0

            for key in keys:
                try:
                    row.append(_dict[key][n])
                except IndexError:
                    row.append("")
                    empty_cells_number += 1
                # break on first empty row
            if empty_cells_number == len(keys):
                break
            rows.append(row)
            n += 1

        return self.fill_rows(rows, keys)

    def fill_from_dict_list(self, dict_list: list[dict]) -> None:
        """
        Given a list of dict with same keys,
        fills the table with keys as header
        """
        header = list(dict_list[0].keys())
        content = []
        for _dict in dict_list:
            assert list(_dict.keys()) == header
            line = []
            for head in header:
                line.append(_dict[head])
            content.append(line)
        return self.fill_rows(content, header)
