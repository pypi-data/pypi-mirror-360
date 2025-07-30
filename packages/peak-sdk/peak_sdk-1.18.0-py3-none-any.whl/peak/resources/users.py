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

"""User client module."""
from __future__ import annotations

from typing import Dict, Optional

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.helpers import search_action
from peak.session import Session
from peak.validators import validate_action, validate_feature_path


class User(BaseClient):
    """Client class for interacting with users resource."""

    BASE_ENDPOINT = "access-control/api/v2"

    def check_permissions(self, feature_actions: Dict[str, str]) -> Dict[str, bool]:
        """Check if the user has the specified permissions for the given features or subfeatures.

        Args:
            feature_actions (Dict[str, str]): A dictionary where keys are feature paths (e.g., "PRICING.GUARDRAILS")
                and values are actions (e.g., "read" or "write").

        Returns:
            Dict[str, bool]: A dictionary where keys are the same feature paths and values are booleans
                indicating whether the user has the specified action permission for that feature.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/access/permissions"

        permissions_response = self.session.create_request(
            endpoint,
            method,
            params={
                "type": "app",
            },
            content_type=ContentType.APPLICATION_JSON,
        )

        result_permissions = {}

        for feature_path, action in feature_actions.items():
            validate_action(action)

            search_result = search_action(feature_path, permissions_response, action)
            validate_feature_path(search_result=search_result, feature_path=feature_path)

            result_permissions[feature_path] = search_result["has_permission"]

        return result_permissions


def get_client(session: Optional[Session] = None) -> User:
    """Returns a User client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        User: The user client object.
    """
    return User(session)


__all__ = ["get_client"]
