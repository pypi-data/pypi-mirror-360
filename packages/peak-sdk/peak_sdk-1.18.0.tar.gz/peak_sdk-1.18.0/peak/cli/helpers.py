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
"""Helper functions for Peak `cli`."""

from __future__ import annotations

import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

import yaml
from peak import base_client, press, resources
from peak.exceptions import BadParameterException
from peak.helpers import format_date, remove_none_values
from peak.metrics import metrics
from peak.template import load_template
from rich.console import Console

console = Console()


def parse_params(params: Optional[List[str]]) -> Dict[str, str]:
    """Parse parameters into key-value pairs.

    Args:
        params (Optional[List[str]]): List of key-value pairs

    Returns:
        Dict[str, str]: Dictionary of key-value pairs

    Raises:
        BadParameterException: If a value is invalid

    >>> params = ["foo=1", "bar=2"]
    >>> vals = parse_params(params)
    >>> vals
    {'foo': '1', 'bar': '2'}

    Raises an error if a value is invalid
    >>> parse_params(["bar==foo"]) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    BadParameterException: Unable to parse: bar==foo
    """
    if params is None:
        return {}

    _to_pass: Dict[str, Any] = {}
    for keyval in params:
        if keyval.count("=") != 1:
            raise BadParameterException(keyval)
        s: List[str] = keyval.split("=", 1)  # split on first '='
        _to_pass[s[0]] = s[-1]
    return _to_pass


def check_file_extension(file_path: str) -> None:
    """Checks if the file has a .txt or .md extension.

    Args:
        file_path (str): Path to the file to check.

    Raises:
        ValueError: If the file extension is not .txt or .md.
    """
    file_type = Path(file_path).suffix
    if file_type not in [".txt", ".md"]:
        msg = f"Unsupported file type: `{file_type}` Only .txt and .md files are supported."
        raise ValueError(msg)


def template_handler(
    file: str,
    params_file: Optional[str] = None,
    params: Optional[List[str]] = None,
    markdown_files: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Loads and returns the rendered template.

    Args:
        file (str): Path to the template file.
        params_file (Optional[str]): Path to the params map file.
        params (Optional[List[str]]): List of params to override.
        markdown_files (Optional[Dict[str, str]]): Dictionary of markdown files to load.
            The key is a colon-separated string representing the nested key path (e.g., "body:metadata:description"), and the value is the path to the markdown file.

    Returns:
        Dict[str, Any]: Rendered template with values substituted.
    """
    params_dict: Dict[str, Any] = {}
    markdown_data: Dict[str, str] = {}

    if params_file:
        with Path(params_file).open("r") as f:
            params_dict = yaml.safe_load(f.read())

    if markdown_files:
        for key, value in markdown_files.items():
            check_file_extension(value)
            with Path(value).open("r") as f:
                markdown_data[key] = f.read()

    params_dict = remove_none_values({**params_dict, **parse_params(params)})

    return load_template(file, params_dict, markdown_data=markdown_data, convert_to_snake_case=True)


def remove_unknown_args(args: Dict[str, Any], func: Callable[..., Any]) -> Dict[str, Any]:
    """Filters keys from dictionary which are not accepted by the function.

    Args:
        args (Dict[str, Any]): dictionary to filter
        func (Callable): function to filter for

    Returns:
        Dict[str, Any]: filtered dictionary
    """
    func_params = inspect.signature(func).parameters
    return {k: v for k, v in args.items() if k in func_params}


def get_updated_artifacts(
    body: Dict[str, Any],
    artifact_path: str | None,
    artifact_ignore_files: List[str] | None,
) -> Dict[str, Any]:
    """Returns updated artifacts by replacing artifact path and ignore files by the ones provided via cli args.

    Args:
        body (Dict[str, Any]): Dictionary containing request body generated from user provided yaml file
        artifact_path (str | None): Path to the artifact.
        artifact_ignore_files (List[str] | None): Ignore files to use when creating artifact.

    Returns:
        Dict[str, Any]: Dictionary containing updated artifacts
    """
    artifact: Dict[str, Any] = {}

    if artifact_path:
        artifact["path"] = artifact_path
    elif "artifact" in body and "path" in body["artifact"]:
        artifact["path"] = body["artifact"]["path"]

    if artifact_ignore_files:
        artifact["ignore_files"] = artifact_ignore_files
    elif "artifact" in body and "ignore_files" in body["artifact"]:
        artifact["ignore_files"] = body["artifact"]["ignore_files"]

    return artifact


def parse_build_arguments(build_arguments: List[str]) -> List[Dict[str, str]]:
    """Parses build arguments provided via cli args to the format {name: arg1, value: value1}.

    Args:
        build_arguments (List[str]): List of build arguments provided via cli args

    Returns:
        List[Dict[str, str]]: List of build arguments in the required format

    Raises:
        BadParameterException: If a value is invalid
    """
    parsed_build_arguments: List[Dict[str, str]] = []
    for build_argument in build_arguments:
        try:
            key, value = build_argument.split("=", 1)
        except ValueError as err:
            raise BadParameterException(
                build_argument,
                message="Invalid build argument format. It should in the --build-arguments arg1=value1 format",
            ) from err
        key, value = build_argument.split("=", 1)
        parsed_build_arguments.append({"name": key, "value": value})
    return parsed_build_arguments


def parse_envs(env: List[str]) -> Dict[str, str]:
    """Parses envs provided via cli args to the format {arg1: value1}.

    Args:
        env (List[str]): List of envs provided via cli args.

    Returns:
        Dict[str, str]: Envs in the required format.

    Raises:
        BadParameterException: If a value is invalid.
    """
    parsed_envs: Dict[str, str] = {}
    for env_arg in env:
        try:
            key, value = env_arg.split("=", 1)
        except ValueError as err:
            raise BadParameterException(
                env_arg,
                message="Invalid env format. It should in the --env arg1=value1 format",
            ) from err
        parsed_envs[key] = value
    return parsed_envs


def format_logs(logs: List[Dict[str, Any]]) -> str:
    """Formats logs into a readable format.

    Args:
        logs (List[Dict[str, Any]]): List of logs

    Returns:
        str: Formatted logs
    """
    formatted_logs = ""
    for log in logs:
        updated_log = f"{format_date(timestamp=log['timestamp'])}: {log['message']}\n\n"
        formatted_logs += updated_log

    return formatted_logs


def get_client(command: str) -> base_client.BaseClient:
    """Create a client for the invoked command.

    Args:
        command (str): Invoked CLI command

    Returns:
        BaseClient: client class for the invoked command
    """
    command_client_map: Dict[str, ModuleType] = {
        "apps": press.apps,
        "blocks": press.blocks,
        "specs": press.specs,
        "deployments": press.deployments,
        "artifacts": resources.artifacts,
        "cache": resources.cache,
        "images": resources.images,
        "workflows": resources.workflows,
        "services": resources.services,
        "webapps": resources.webapps,
        "tenants": resources.tenants,
        "users": resources.users,
        "alerts": resources.alerts,
        "metrics": metrics,
    }
    return command_client_map[command].get_client()  # type: ignore[no-any-return]
