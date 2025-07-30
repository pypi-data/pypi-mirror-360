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
"""Deployments client module."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class Deployment(BaseClient):
    """Client class for interacting with Deployments."""

    BASE_ENDPOINT = "v1/deployments"

    @overload
    def list_deployments(
        self,
        status: Optional[List[str]] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_deployments(
        self,
        status: Optional[List[str]] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_deployments(
        self,
        status: Optional[List[str]] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """List all App & Block Deployments ordered by creation date. Returns info on the latest revision of each deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Deployments/get_v1_deployments>`__

        Args:
            status (List[str] | None): List of statuses to filter deployments.
                Valid values are `deploying`, `deployed`, `deleting`, `delete_failed`, `failed`, `platform_resource_error`, `redeploying`, `rollback`, `rollback_complete`, `rollback_failed`, and `warning`.
            kind (str | None): Return deployments of the kind specified.
            term (str | None): Return deployments containing the specified term in name, title, description and summary.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response,
                defaults to `[]`. Valid fields are `createdAt`, `createdBy`, `name` and `title`.
            page_size (int | None): Number of deployments to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of deployments for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: An iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/"
        params: Dict[str, Any] = {
            "status": status,
            "kind": kind,
            "term": term,
            "sort": sort,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="deployments",
                params=params,
                subdomain="press",
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
            subdomain="press",
        )

    def execute_resources(self, deployment_id: str) -> Dict[str, Any]:
        """Trigger the resources of an app or block deployment. This will execute the resources of the latest revision of the deployment.

        Args:
            deployment_id (str): ID of the app or block deployment to trigger resources for.

        Returns:
            Dict[str, Any]: A dictionary containing the details of the triggered deployment.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/{deployment_id}/execute"
        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def patch_parameters(
        self,
        deployment_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get the parameters for a deployment at run time.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/patch_v1_deployments__deploymentId__parameters_run>`__

        Args:
            deployment_id (str): The ID of the deployment.
            body (Dict[str, Any]): Dictionary containing the updated parameters.

        Returns:
            Dict[str, Any]: Dictionary containing the updated parameters.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given deployment does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.PATCH, f"v1/deployments/{deployment_id}/parameters/run"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            body=body,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def patch_parameters_v2(
        self,
        deployment_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get the runtime parameters for a deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/patch_v2_deployments__deploymentId__parameters_run>`__

        Args:
            deployment_id (str): The ID of the deployment.
            body (Dict[str, Any]): body (Dict[str, str]): Dictionary of app and block parameters.

        Returns:
            Dict[str, Any]: Dictionary containing app and block parameters.

        SCHEMA(Block Deployment Run Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {
                    "parameters": {
                        "param_name": "param_value (string | number | boolean | dict | array)"
                    }
                }

        SCHEMA(App Deployment Run Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {
                    "appParameters": {
                        "param_name": "param_value (string | number | boolean | dict | array)"
                    },
                    "parameters": {
                        "block_name": {
                            "param_name": "param_value (string | number | boolean | dict | array)"
                        }
                    }
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given deployment does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.PATCH, f"v2/deployments/{deployment_id}/parameters/run"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            body=body,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )


def get_client(session: Optional[Session] = None) -> Deployment:
    """Returns a Deployment client.

    Args:
        session (Optional[Session]): A Session Object. If no session is provided, a default session is used.

    Returns:
        Deployment: the Deployment client object
    """
    return Deployment(session)


__all__: List[str] = ["get_client"]
