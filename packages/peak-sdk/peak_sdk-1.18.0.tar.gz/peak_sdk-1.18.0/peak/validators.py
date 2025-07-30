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
"""Validators for peak sdk."""
from __future__ import annotations

import os
import tempfile
from typing import Dict, List

from peak.constants import MAX_ARTIFACT_SIZE_MB, MB
from peak.exceptions import FileLimitExceededException, InvalidParameterException


def check_file_size(fh: tempfile.SpooledTemporaryFile[bytes], max_size: float = MAX_ARTIFACT_SIZE_MB) -> None:
    """Check file is smaller than 10MB."""
    file_size: int = _get_file_size(fh)
    if file_size > max_size * MB:
        raise FileLimitExceededException(max_size=max_size)


def validate_action(action: str) -> None:
    """Validate the action provided.

    Args:
        action (str): The action to be validated.

    Raises:
        InvalidParameterException: If the action is not 'read' or 'write'.

    Returns: None
    """
    if action not in ["read", "write"]:
        raise InvalidParameterException(message="The action must be 'read' or 'write'.")


def validate_feature_path(search_result: Dict[str, bool], feature_path: str) -> None:
    """Validate the feature path provided.

    Args:
        search_result (Dict[str, bool]): The search result for the feature path.
        feature_path (str): The feature path to be validated.

    Raises:
        InvalidParameterException: If the feature path is incomplete and more subfeatures need to be specified.

    Returns: None
    """
    if search_result["deeper_levels"]:
        message = f"'{feature_path}' contains more subfeatures. Please specify the complete path."
        raise InvalidParameterException(message=message)


def _get_file_size(fh: tempfile.SpooledTemporaryFile[bytes]) -> int:
    """Get file size in bytes."""
    old_pos: int = fh.tell()
    fh.seek(0, os.SEEK_END)
    file_size_bytes: int = fh.tell()
    fh.seek(old_pos)
    return file_size_bytes


__all__: List[str] = ["check_file_size"]
