#
# # Copyright © 2025 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Log Writer Module."""

from __future__ import annotations

import contextlib
import json
import sys
from typing import Any, List

import yaml
from rich.console import Console, PagerContext
from rich.highlighter import JSONHighlighter
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from peak import config
from peak.constants import OutputTypes

console = Console()
json_highlighter = JSONHighlighter()


class Writer:
    """The Writer class used to print out data in the CLI."""

    def __init__(self, *, ignore_debug_mode: bool = False) -> None:
        """Initialise the write class.

        Args:
            ignore_debug_mode (bool): don't consider debug mode and print the output anyways.
        """
        self.ignore_debug_mode = ignore_debug_mode

    def write(
        self,
        data: Any,
        deprecation_message: str | None = None,
        output_type: OutputTypes | None = None,
    ) -> None:
        """Write logs to the terminal.

        Args:
            data (Any): Data to be printed on the terminal.
                This handles dry-run, debug mode and exit code for the CLI.
            deprecation_message (str, optional): Deprecation message to be printed on the terminal.
            output_type (OutputTypes, optional): Override for the output type set in the config.
        """
        output_type_parsed = output_type or config.OUTPUT_TYPE
        table_params = config.TABLE_PARAMS

        if not config.DEBUG_MODE or self.ignore_debug_mode:
            if deprecation_message:
                self._print_deprecation_warning(deprecation_message)
            if output_type_parsed == OutputTypes.yaml.value:
                self.__yaml(data)
            elif output_type_parsed == OutputTypes.table.value:
                self.__table(data, table_params)
            else:
                self.__json(data, output_type)

    def __json(self, data: Any, output_type: OutputTypes | None = None) -> None:
        """Write logs to the terminal in JSON format.

        Args:
            data (Any): Data to be printed on the terminal.
            output_type (OutputTypes): If passed, JSON parser would be used to print output
                even if the data is not a dictionary.
        """
        if isinstance(data, (dict, list)) or output_type == OutputTypes.json:
            console.print_json(data=data)
        else:
            console.print(data)

    def __table(self, data: dict[Any, Any], params: dict[str, Any]) -> None:
        """Write logs to the terminal in a tabular format.

        Args:
            data (dict[Any, Any]): Data to be printed on the terminal.
            params (dict[str, Any]): Parameters for table-related formatting.
        """
        caption = (
            f"Page {data['pageNumber']} of {data['pageCount']}"
            if ("pageCount" in data and "pageNumber" in data)
            else None
        )

        if not len(data[params["data_key"]]):
            console.print(Panel(Text("No data to display.", justify="center")))
            return

        title = params["title"]

        if "subheader_key" in params and params["subheader_key"] in data:
            subheader_title = params.get("subheader_title", "Total")
            title = f'{title} ({subheader_title} = {data[params["subheader_key"]]})'

        table = Table(
            expand=True,
            highlight=True,
            row_styles=["grey62", ""],
            header_style="bold cyan",
            leading=1,
            title=title,
            title_style="bold",
            caption=caption,
        )

        output_keys = params["output_keys"].items()

        if len(output_keys) == 0:
            keys = data[params["data_key"]][0].keys()
            params["output_keys"] = {key: {"label": key} for key in keys}
            output_keys = params["output_keys"].items()

        for key_details in output_keys:
            table.add_column(key_details[1]["label"])

        for val in data[params["data_key"]]:
            parsed_values = []

            for key_details in output_keys:
                v = self.__get_data(val, key_details[0])

                if not v:
                    v = "-"
                elif "parser" in key_details[1]:
                    v = key_details[1]["parser"](v)

                if isinstance(v, (dict, list)):
                    parsed_value = json_highlighter(Text(json.dumps(v, indent=2), overflow="fold"))
                else:
                    parsed_value = Text(str(v), overflow="fold")

                parsed_values.append(parsed_value)

            table.add_row(*parsed_values)

        console.print("\n")
        console.print(table)
        console.print("\n")

    def __yaml(self, data: dict[Any, Any]) -> None:
        """Write logs to the terminal in YAML format.

        Args:
            data (dict[Any, Any]): Data to be printed on the terminal.
        """
        console.print(yaml.dump(data, indent=4))

    def __get_data(self, data: dict[Any, Any], key: str) -> Any:
        """Get value of a nested key from a dict.

        Args:
            data (dict[Any, Any]): The dictionary to get data from.
            key (str): The key to get the value for.

        Returns:
            Any: The value for the required key.
        """
        if not key:
            return data

        if key in data:
            return data[key]

        key_first_part = key.split(".")[0]
        key_rest = ".".join(key.split(".")[1:])

        if key_first_part not in data:
            return None

        return self.__get_data(data[key_first_part], key_rest)

    def pager(self) -> PagerContext | contextlib.nullcontext[None]:
        """Returns a Pager context manager."""
        if config.ENABLE_PAGING:
            return console.pager(styles=True)
        return contextlib.nullcontext()

    def _print_deprecation_warning(self, deprecation_message: str) -> None:
        """Prints a deprecation warning message."""
        print(f"\nNote: {deprecation_message}", file=sys.stderr)  # noqa: T201


__all__: List[str] = ["Writer"]
