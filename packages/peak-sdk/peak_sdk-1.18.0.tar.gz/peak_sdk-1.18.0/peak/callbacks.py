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
"""All the Typer callbacks."""
from __future__ import annotations

from pathlib import Path

import click
import typer

import peak.config
from peak._metadata import command_metadata, command_parameter
from peak.constants import OutputTypes
from peak.output import Writer

writer = Writer(ignore_debug_mode=True)


def dry_run(*, debug_mode: bool) -> None:
    """Callback to enable dry run."""
    peak.config.DEBUG_MODE = debug_mode


def paging(*, enable_paging: bool) -> None:
    """Callback to enable paging."""
    peak.config.ENABLE_PAGING = enable_paging


def update_command(ctx: typer.Context, command: str) -> str:
    """Callback to update the command based on the command parameter."""
    if not ctx or not hasattr(ctx, "params") or command not in command_parameter:
        return command

    param = command_parameter[command]
    param_value = ctx.params.get(param)
    if param_value:
        command_with_params = f"{command}>{param_value}"
        if command_with_params in command_metadata and "table_params" in command_metadata[command_with_params]:
            return command_with_params
    return command


def get_full_command_name(ctx: typer.Context | click.core.Context | None) -> str:
    """Callback to get the full command name."""
    if ctx:
        parent = get_full_command_name(ctx.parent)
        if parent:
            return f"{parent}>{ctx.info_name}"
        return str(ctx.info_name)

    return ""


def get_command_name(ctx: typer.Context) -> str:
    """Callback to get the parsed command name with first part removed."""
    command = get_full_command_name(ctx)
    return ">".join(command.split(">")[1:])


def handle_output(output_type: OutputTypes, ctx: typer.Context) -> None:
    """Callback to handle CLI output type and set all the required parameters for Table output."""
    peak.config.OUTPUT_TYPE = output_type

    command = get_command_name(ctx)
    command = update_command(ctx, command)

    if (command not in command_metadata) or ("table_params" not in command_metadata[command]):
        return

    peak.config.TABLE_PARAMS = command_metadata[command]["table_params"]


def generate_yaml(ctx: typer.Context, generate_yaml: bool) -> None:  # noqa: FBT001 # pragma: no cover
    """Callback to generate yaml file."""
    command = get_command_name(ctx)
    output_type = peak.config.OUTPUT_TYPE

    if (
        (command not in command_metadata)
        or ("request_body_yaml_path" not in command_metadata[command])
        or output_type == "table"
    ):
        return

    if generate_yaml:
        current_file_path = Path(__file__).resolve().parent
        file_path = Path(f"{current_file_path}/{command_metadata[command]['request_body_yaml_path']}").resolve()
        with file_path.open() as file:
            yaml_text = file.read()
            with writer.pager():
                writer.write(yaml_text)
                raise typer.Exit
