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

"""Collection of basic helper functions."""

from __future__ import annotations

import inspect
import json
import re
from datetime import datetime, timezone
from types import FrameType
from typing import Any, Dict, List, Optional

import requests

from peak import config
from peak.constants import Sources
from peak.output import Writer


def parse_body_for_multipart_request(body: Dict[str, Any]) -> Dict[str, str]:
    """Parses an object to make it suitable for passing in a multipart request.

    Args:
        body (Dict[str, Any]): the object to be parsed

    Returns:
        Dict[str, str]: the parsed object
    """
    return {key: (value if isinstance(value, str) else json.dumps(value)) for (key, value) in body.items()}


def remove_keys(body: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Removes given keys from a dictionary.

    Args:
        body (Dict[str, Any]): the object to be parsed
        keys (List[str]): the keys to remove

    Returns:
        Dict[str, str]: the final object with required keys removed
    """
    return {key: value for (key, value) in body.items() if key not in keys}


def get_base_domain(stage: str, subdomain: Optional[str] = "service") -> str:
    """Gets the base domain for a stage with the given subdomain.

    Args:
        stage (str): the stage
        subdomain (Optional[str]): the subdomain

    Returns:
        str: the final base domain
    """
    if stage == "prod":
        stage = ""
    elif stage == "latest":
        stage = "dev"

    domain: str = f"https://{subdomain}.{stage}.peak.ai"
    return domain.replace("..", ".")  # for prod domain


def parse_list_of_strings(param: List[str] | None) -> List[str] | None:
    """Split comma separated strings in the list and flatten that list.

    Args:
       param (List[str] | None): List of strings

    Returns:
        List[Any] | None: The final flattened list
    """
    if param is None or len(param) == 0:
        return param

    result: List[str] = []
    for e in param:
        result = result + e.split(",")

    return result


def snake_case_to_lower_camel_case(snake_case_string: str) -> str:
    """Converts underscore string to lower camel case.

    Args:
        snake_case_string (str): string in underscore

    Returns:
        str: lower camel case string
    """
    parts = snake_case_string.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def variables_to_dict(*args: Any, frame: FrameType | None = None) -> Dict[str, str]:
    """Converts arbitrary variables to a dictionary.

    Args:
        args (str|int): tuple of string|int variables
        frame (FrameType|None): Current Frame of caller

    Returns:
        Dict[str, str]: Dictionary containing key value pair of variables
    """
    if frame is None:
        frame = inspect.currentframe()
        if frame:
            # set frame to previous
            frame = frame.f_back

    var_dict = {}
    if frame and frame.f_locals:
        for var_name, var_value in frame.f_locals.items():
            if var_value in args and var_value:
                var_dict[snake_case_to_lower_camel_case(var_name)] = var_value

    del frame  # Explicitly release the frame to avoid reference cycles
    return var_dict


def combine_dictionaries(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    nested_keys_to_skip: Optional[List[str]] = [],  # noqa: B006
) -> Dict[str, Any]:
    """Combines two dictionaries. Values for second dictionary have higher precedence.

    Args:
        dict1 (Dict[str, Any]): dictionary 1
        dict2 (Dict[str, Any]): dictionary 2
        nested_keys_to_skip (List[str] | None): Keys for which nested combining is not required.

    Returns:
        Dict[str, Any]: Combined dictionary
    """
    if not dict1:
        return dict2

    combined_dict = dict(dict1)
    for key in dict2:
        if key in combined_dict and isinstance(combined_dict[key], dict) and key not in (nested_keys_to_skip or []):
            combined_dict[key] = combine_dictionaries(combined_dict[key], dict2[key])
        else:
            combined_dict[key] = dict2[key]
    return combined_dict


def map_user_options(
    user_options: Dict[str, Any],
    mapping: Dict[str, str],
    dict_type_keys: List[str] = [],  # noqa: B006
) -> Dict[str, Any]:
    """Maps user provided inputs to a specific format.

    Args:
        user_options (Dict[str, Any]): Dictionary containing user inputs
        mapping (Dict[str, Any]): Mapping to be used for conversion
        dict_type_keys (List[str]): List of keys which have json type values

    Returns:
        Dict[str, str]: Mapped dictionary
    """
    result: Dict[str, Any] = {}
    for key in user_options:
        if key in mapping:
            nested_dict = result.get(mapping[key], {})
            nested_dict[key] = json.loads(user_options[key]) if key in dict_type_keys else user_options[key]
            result[mapping[key]] = nested_dict
        else:
            result[key] = json.loads(user_options[key]) if key in dict_type_keys else user_options[key]
    return result


def remove_none_values(data: Any) -> Dict[str, Any]:
    """Recursively remove all keys with `None` values from a dictionary.

    Args:
        data (Any): Dictionary to be cleaned.

    Returns:
        Dict[str, Any]: Dictionary with all keys with `None` values removed.
    """
    if isinstance(data, dict):
        return {k: remove_none_values(v) for k, v in data.items() if v is not None}

    return data  # type: ignore[no-any-return]


def convert_to_snake_case(s: str) -> str:
    """Converts a given string from camelCase or TitleCase to snake case.

    Args:
        s (str): The string to be converted.

    Returns:
        str: The converted string in snake case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def convert_keys_to_snake_case(data: Dict[str, Any], *, convert_nested: bool = False) -> Dict[str, Any]:
    """Converts keys of a dictionary to snake case.

    Args:
        data (Dict[str, Any]): Dictionary to be converted.
        convert_nested (bool): Whether to convert nested keys as well. Default is False.

    Returns:
        Dict[str, Any]: Dictionary with keys converted to snake case.
    """

    def convert_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        new_dict = {}
        for k, v in d.items():
            new_key = convert_to_snake_case(k)
            if convert_nested and isinstance(v, dict):
                new_dict[new_key] = convert_dict(v)
            else:
                new_dict[new_key] = v
        return new_dict

    return convert_dict(data)


def format_date(timestamp: str, time_format: str = "%Y/%m/%d %H:%M:%S") -> str:
    """Format a timestamp to a given format.

    Args:
        timestamp (str): Timestamp to be formatted in milliseconds.
        time_format (str): Format to be used for formatting the given timestamp.

    Returns:
        str: Formatted timestamp.
    """
    return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc).strftime(time_format)


def download_logs_helper(
    response: Dict[str, Any],
    file_name: str,
) -> None:
    """Save logs to a file or return the download url.

    Args:
        response (Dict[str, Any]): Response object from the API.
        file_name (str): Name of the file where the contents should be saved.

    Returns: None
    """
    download_response = requests.get(response["downloadUrl"], timeout=20, stream=True)
    download_response.raise_for_status()

    with open(file_name, "wb") as file:  # noqa: PTH123
        file.write(download_response.content)
        if config.SOURCE == Sources.CLI:
            writer = Writer()
            writer.write(f"\nLog contents have been saved to: {file_name}")


def search_action(current_path: str, current_dict: Dict[str, Any], action: str) -> Dict[str, bool]:
    """Search for a specified action within a nested dictionary structure and check if deeper levels exist.

    Args:
        current_path (str): The dot-separated path representing the feature hierarchy.
        current_dict (Dict[str, Any]): The nested dictionary representing the permissions structure.
        action (str): The action to search for (e.g., "read" or "write").

    Returns:
        bool: A dictionary with keys 'has_permission' indicating if the action is found and
              'deeper_levels' indicating if there are deeper levels that need specification.
    """
    keys = current_path.split(".")
    for key in keys:
        if key in current_dict:
            current_dict = current_dict[key]
        else:
            return {"has_permission": False, "deeper_levels": False}

    if "actions" in current_dict:
        actions = current_dict["actions"]
        has_permission = "*" in actions or action in actions or ("write" in actions and action == "read")
        return {"has_permission": has_permission, "deeper_levels": False}

    return {"has_permission": False, "deeper_levels": True}


def safe_json(response: requests.Response) -> Optional[Any]:
    """Safely attempts to decode JSON from the given response.

    Returns the decoded JSON if available; otherwise, returns None.
    """
    headers = getattr(response, "headers", {})
    if headers.get("Content-Type", "").startswith("application/json"):
        try:
            return response.json()
        except (ValueError, json.JSONDecodeError):
            return None
    return None
