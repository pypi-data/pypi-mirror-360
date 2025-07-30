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

"""Service client module."""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class Service(BaseClient):
    """Client class for interacting with services resource."""

    BASE_ENDPOINT = "webapps/api/v1"

    @overload
    def list_services(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        service_type: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_services(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        service_type: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_services(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        service_type: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve a list of services.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/list-service>`__

        Args:
            page_size (int | None): The number of services per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            status (List[str] | None): A list of service status to filter the list by.
                Valid values are `CREATING`, `DEPLOYING`, `AVAILABLE`, `DELETING`, `CREATE_FAILED`, `DELETE_FAILED`.
            name (str | None): Name of the service to search for.
            service_type (List[str] | None): A list of service types to filter the list by. Valid values are `api`, `web-app` and `shiny`.
            return_iterator (bool): Whether to return an iterator object or list of services for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.
            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/webapps/"
        params = {
            "pageSize": page_size,
            "status": status,
            "searchTerm": name,
            "serviceType": service_type,
            "featureType": "services",
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="services",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def create_service(self, body: Dict[str, Any]) -> Dict[str, str]:
        """Create a new service.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/create-service>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the service config. Schema can be found below.

        Returns:
            Dict[str, str]: Id of the new service

        SCHEMA:
            .. code-block:: json

                {
                    "name": "string(required)",
                    "title": "string",
                    "serviceType": "string. Valid values are 'api', 'web-app' and 'shiny'",
                    "imageDetails": {
                        "imageId": "number(required)",
                        "versionId": "number"
                    },
                    "resources": {
                        "instanceTypeId": "number"
                    },
                    "parameters": {
                        "env": {
                            "key: string": "value: string"
                        },
                        "secrets": []
                    },
                    "description": "string",
                    "sessionStickiness": "boolean. Not required for 'api' service type.",
                    "scaleToZero": "boolean. Only for 'web-app' service type.",
                    "entrypoint": "string",
                    "healthCheckURL": "string",
                    "minInstances": "number. Default is 1 and maximum is 2",
                }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/webapps/"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def update_service(
        self,
        service_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, str]:
        """Updates the existing service.

        When updating the service, it will trigger a redeployment only under specific conditions.
        Redeployment is triggered if you make changes to any of the following parameters: imageId, versionId, instanceTypeId, parameters, healthCheckURL, entrypoint, scaleToZero or sessionStickiness.
        However, only modifying the title or description will not trigger a redeployment.

        With the help of this operation, we can just update the required fields (except name and serviceType) and keep the rest of the fields as it is.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/update-service>`__

        Args:
            service_id (str): The ID of the service to update.
            body (Dict[str, Any]): A dictionary containing the service config. Schema can be found below.

        Returns:
            Dict[str, str]: Id of the service.

        SCHEMA:
            .. code-block:: json

                {
                    "title": "string",
                    "imageDetails": {
                        "imageId": "number(required)",
                        "versionId": "number",
                    },
                    "resources": {
                        "instanceTypeId": "number"
                    },
                    "parameters": {
                        "env": {
                            "key: string": "value: string",
                        },
                        "secrets": []
                    },
                    "description": "string",
                    "sessionStickiness": "boolean. Not required for 'api' service type.",
                    "scaleToZero": "boolean. Only for 'web-app' service type.",
                    "entrypoint": "string",
                    "healthCheckURL": "string",
                    "minInstances": "number. Default is 1 and maximum is 2",
                }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given service does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.PATCH, f"{self.BASE_ENDPOINT}/webapps/{service_id}"
        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def create_or_update_service(self, body: Dict[str, Any]) -> Dict[str, str]:
        """Create a new service or updates an existing service based on service name.

        When updating the service, it will trigger a redeployment only under specific conditions.
        Redeployment is triggered if you make changes to any of the following parameters: imageId, versionId, instanceTypeId, parameters, healthCheckURL, entrypoint, scaleToZero or sessionStickiness.
        However, only modifying the title or description will not trigger a redeployment.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/create-service>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the service config. Schema can be found below.

        Returns:
            Dict[str, str]: Id of the new or updated service.

        SCHEMA:
            .. code-block:: json

                {
                    "name": "string(required)",
                    "title": "string",
                    "serviceType": "string. Valid values are 'api', 'web-app' and 'shiny'",
                    "imageDetails": {
                        "imageId": "number(required)",
                        "versionId": "number"
                    },
                    "resources": {
                        "instanceTypeId": "number"
                    },
                    "parameters": {
                        "env": {
                            "key: string": "value: string",
                        },
                        "secrets": []
                    },
                    "description": "string",
                    "sessionStickiness": "boolean. Not required for 'api' service type.",
                    "scaleToZero": "boolean. Only for 'web-app' service type.",
                    "entrypoint": "string",
                    "healthCheckURL": "string",
                    "minInstances": "number. Default is 1 and maximum is 2",
                }


        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        service_name = body.get("name", "")
        response = (
            {} if not len(service_name) else self.list_services(page_size=100, return_iterator=False, name=service_name)
        )
        filtered_services = list(
            filter(lambda service: service.get("name", "") == service_name, response.get("services", [])),
        )

        if len(filtered_services) > 0:
            service_id = filtered_services[0]["id"]
            return self.update_service(service_id=service_id, body=body)

        return self.create_service(body=body)

    def delete_service(
        self,
        service_id: str,
    ) -> Dict[str, str]:
        """Delete a service.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/delete-service>`__

        Args:
            service_id (str): The ID of the service to delete.

        Returns:
            Dict[str, str]: Dictonary containing ID of the deleted service.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given service does not exist.
            ConflictException: If the service is in a conflicting state while deleting.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/webapps/{service_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def describe_service(
        self,
        service_id: str,
    ) -> Dict[str, Any]:
        """Retrieve details of a specific service.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/get-service>`__

        Args:
            service_id (str): The ID of the service to fetch.

        Returns:
            Dict[str, Any]: Dictonary containing details of the service.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given service does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/webapps/{service_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def test_service(
        self,
        service_name: str,
        http_method: str,
        path: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Test an API service to verify it's health and if it is working. Make sure the service is of type "api".

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/webapps/api-docs/index.htm#/Services/test-api-service>`__

        Args:
            service_name (str): The name of the API type service to test.
            http_method (str): The HTTP method to use for the test. Valid values are 'get', 'post', 'put', 'patch' and 'delete'.
            path (str, None): The path to test the service with. Default is '/'.
            payload (Dict[str, Any], None): The payload to test the service with.

        Returns:
            Dict[str, Any]: Dictonary containing response of the test.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given service does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/webapps/{service_name}/test"
        body = {"httpMethod": http_method, "path": path, "payload": payload}

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )


def get_client(session: Optional[Session] = None) -> Service:
    """Returns a Service client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Service: The service client object.
    """
    return Service(session)


__all__ = ["get_client"]
