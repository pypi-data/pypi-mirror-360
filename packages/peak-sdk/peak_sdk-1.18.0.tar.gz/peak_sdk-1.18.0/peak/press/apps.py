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
"""Apps client module."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class App(BaseClient):
    """Client class for interacting with Apps."""

    SPECS_BASE_ENDPOINT = "v1/apps/specs"
    DEPLOYMENTS_BASE_ENDPOINT = "v1/apps/deployments"

    @overload
    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists all published App specs ordered by creation date. Returns info for the latest release for each spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs_>`__

        Args:
            status (List[str] | None): List of statuses to filter specs.
                Valid values are `available`, `unavailable` and `archived`.
            featured (bool | None): Whether to only return featured specs.
            name (str | None): Only return specs whose names begins with the query string.
            title (str | None): Only return specs whose title begins with the query string.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response,
                defaults to `[]`. Valid fields are `createdAt`, `createdBy`, `name`, `title`.
            scope (List[str] | None): List of scopes to only return specs of those scopes. Valid values are `private`, `public` and `shared`.
            page_size (int | None): Number of specs to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of specs for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/"
        params: Dict[str, Any] = {
            "status": status,
            "featured": featured,
            "name": name,
            "title": title,
            "sort": sort,
            "scope": scope,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="specs",
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

    def create_spec(
        self,
        body: Dict[str, Any],
        featured: Optional[bool] = None,
        scope: Optional[str] = None,
        tenants: Optional[List[str]] = None,
        parameters: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, str]:
        """Creates a new App spec.

        All App Specs must have unique names within a tenant.
        An App Spec must now be made up of already existing block specs.
        Spec details (Block spec ID and Release version) needs to be added to the `config` key.
        `config` also contains a `autoRunOnDeploy` key which is a boolean value to specify if the resource should be executed on successful deployment of the app. By default, it is False.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/post_v1_apps_specs_>`__

        Args:
            body (Dict[str, Any]):  A payload specifying an App's metadata, release and corresponding config in the expected format.
            featured (bool | None): Whether to feature this spec. By default it is False.
            scope (str | None): Specify weather tenants can discover and deploy this spec.
                `private` restricts the spec to this tenant alone, `public` makes it available on all tenants
                and `shared` allows specifying what set of tenants can access and use this spec.
                By default it is `private`.
            tenants (List[str] | None): Given a shared scope, specify what other tenants can discover and deploy this spec.
            parameters (Optional[Dict[str, List[Dict[str, Any]]]]): A dictionary containing optional keys `build` and `run`. The structure of the dictionary is as follows:

                - `build` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given and used at deployment time.
                - `run` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given at deployment time and will be used at run time.

        Returns:
            Dict[str, str]: Id of the created app spec.

        SCHEMA:
            .. code-block:: json

                {
                    "version": "number(required)",
                    "kind": "string(required)",
                    "metadata": {
                        "name": "string(required)",
                        "title": "string",
                        "summary": "string(required)",
                        "description": "string",
                        "descriptionContentType": "string",
                        "imageUrl": "string",
                        "tags": [
                            {
                                "name": "string",
                            }
                        ]
                    },
                    "release": {
                        "notes": "string(required)",
                        "version": "string(required)",
                    },
                    "config": [
                        {
                            "id": "string(required)",
                            "release": {
                                "version": "string(required)",
                            },
                            "autoRunOnDeploy": "boolean (By default it is False)",
                        }
                    ]
                }
        SCHEMA(Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {
                    "build": [
                        {
                            "name": "string(required)",
                            "type": "string(required)",
                            "required": "boolean(required)",
                            "description": "string",
                            "defaultValue": "string(required)",
                            "title": "string",
                            "options": "list(str)",
                            "hideValue": "boolean",
                        }
                    ],
                    "run": [
                        {
                            "name": "string(required)",
                            "type": "string(required)",
                            "required": "boolean(required)",
                            "description": "string",
                            "defaultValue": "string(required)",
                            "title": "string",
                            "options": "list(str)",
                            "hideValue": "boolean",
                            "conditions": [
                                // Basic condition
                                {
                                    "dependsOn": "string",
                                    "operator": "string",
                                    "value": "string|number|boolean"
                                },
                                // Composite condition
                                {
                                    "conditionType": "AND|OR",
                                    "conditions": [
                                        {
                                            "dependsOn": "string",
                                            "operator": "string",
                                            "value": "string|number|boolean"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.SPECS_BASE_ENDPOINT}/"

        body = {
            "spec": json.dumps(body),
            "featured": json.dumps(featured),
            "scope": scope,
            "parameters": json.dumps(parameters),
        }

        if tenants:
            body["tenants"] = json.dumps(tenants)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
            subdomain="press",
        )

    def describe_spec(
        self,
        spec_id: str,
    ) -> Dict[str, Any]:
        """Describes an existing App spec and also provides details of the latest release.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId_>`__

        Args:
            spec_id (str): The ID of the app spec to retrieve.

        Returns:
            Dict[str, Any]: Dictionary containing the details of the spec.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given app spec does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def update_spec_metadata(self, spec_id: str, body: Dict[str, Any]) -> Dict[None, None]:
        """Updates the metadata of an App spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/patch_v1_apps_specs__specId_>`__

        Args:
            spec_id (str): ID of the spec to update
            body (Dict[str, Any]): Dictionary containing the new spec metadata

        Returns:
            dict: Dictionary containing the details of the updated spec.

        SCHEMA:
            .. code-block:: json

                {
                    "metadata": {
                        "name": "string",
                        "title": "string",
                        "summary": "string",
                        "description": "string",
                        "descriptionContentType": "string",
                        "imageUrl": "string",
                        "tags": [
                            {
                                "name": "string",
                            }
                        ],
                        "status": "string",
                    },
                    "featured": "boolean",
                    "scope": "string",
                    "tenants": [
                        "string",
                    ]
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App spec does not exist.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.PATCH, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
            subdomain="press",
        )

    def create_spec_release(
        self,
        spec_id: str,
        body: Dict[str, Any],
        parameters: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, str]:
        """Publish a new release to an existing App spec.

        Spec details (Block spec ID and Release version) needs to be added to the `config` key.
        `config` also contains a `autoRunOnDeploy` key which is a boolean value to specify if the resource should be executed on successful deployment of the app. By default, it is False.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/post_v1_apps_specs__specId__releases>`__

        Args:
            spec_id (str): Id of the spec in which new release will be created
            body (Dict[str, Any]): Dictionary containing updated release and config in the expected format.
            parameters (Optional[Dict[str, List[Dict[str, Any]]]]): A dictionary containing optional keys `build` and `run`. The structure of the dictionary is as follows:

                - `build` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given and used at deployment time.
                - `run` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given at deployment time and will be used at run time.

        Returns:
            Dict[str, str]: Dictionary containing spec id and release version

        SCHEMA:
            .. code-block:: json

                {
                    "config": [
                        {
                            "id": "string(required)",
                            "release": {
                                "version": "string(required)",
                            },
                            "autoRunOnDeploy": "boolean (By default it is False)",
                        }
                    ],
                    "release": {
                        "notes": "string(required)",
                        "version": "string(required)",
                    }
                }

        SCHEMA(Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {
                    "build": [
                        {
                            "defaultValue": "string(required)",
                            "description": "string",
                            "hideValue": "boolean",
                            "name": "string(required)",
                            "required": "boolean(required)",
                            "title": "string",
                            "type": "string(required)",
                        }
                    ],
                    "run": [
                        {
                            "defaultValue": "string(required)",
                            "description": "string",
                            "hideValue": "boolean",
                            "name": "string(required)",
                            "required": "boolean(required)",
                            "title": "string",
                            "type": "string(required)",
                            "conditions": [
                                // Basic condition
                                {
                                    "dependsOn": "string",
                                    "operator": "string",
                                    "value": "string|number|boolean"
                                },
                                // Composite condition
                                {
                                    "conditionType": "AND|OR",
                                    "conditions": [
                                        {
                                            "dependsOn": "string",
                                            "operator": "string",
                                            "value": "string|number|boolean"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given app spec does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body={
                **body,
                "parameters": parameters,
            },
            subdomain="press",
        )

    def delete_spec(
        self,
        spec_id: str,
    ) -> Dict[None, None]:
        """Delete an App Spec and all it's associated releases.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/delete_v1_apps_specs__specId_>`__

        Args:
            spec_id (str): The ID of the App spec to delete.

        Returns:
            dict: Empty dict object.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App spec does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def describe_spec_release(self, spec_id: str, version: str) -> Dict[str, Any]:
        """Describes an existing App spec release.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId__releases__release_>`__

        Args:
            spec_id (str): The ID of the app spec to retrieve.
            version (str): The release version of spec to retrieve in valid semantic versioning format.

        Returns:
            Dict[str, Any]: Dictionary containing details of the spec release

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given app spec does not exist.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases/{version}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    @overload
    def list_spec_releases(
        self,
        spec_id: str,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_spec_releases(
        self,
        spec_id: str,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_spec_releases(
        self,
        spec_id: str,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Get all releases of an App spec (ordered by most recently created to oldest).

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId__releases>`__

        Args:
            spec_id (str): The ID of the app spec to retrieve.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response.
                Valid fields are `createdAt` and `createdBy`.
            page_size (int | None, optional): Number of releases to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of releases for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App spec does not exist.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases"
        params: Dict[str, Any] = {"pageSize": page_size, "sort": sort}

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="releases",
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

    def create_deployment(self, body: Dict[str, Any]) -> Dict[str, str]:
        """Creates a new deployment from App spec.

        Uses the latest spec release if release version is not provided.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/post_v1_apps_deployments>`__

        Args:
            body (Dict[str, str]): Dictionary containing deployment metadata, spec ID, release version, revision info and parameters that would used at run-time.

        Returns:
            Dict[str, str]: ID of the created App deployment

        SCHEMA:
            .. code-block:: json

                {
                    "metadata": {
                        "description": "string"
                        "descriptionContentType": "string"
                        "imageUrl": "string"
                        "name": "string(required)",
                        "summary": "string(required)",
                        "tags": [
                            {
                                "name": "string"
                            }
                        ],
                        "title": "string"
                    },
                    "appParameters": {
                        "build": {
                            "param_name": "param_value (string | number | boolean | array)"
                        },
                        "run": {
                            "param_name": "param_value (string | number | boolean | array)"
                        }
                    },
                    "parameters": {
                        "spec_name": {
                            "build": {
                                "param_name": "param_value (string | number | boolean | array)"
                            },
                            "run": {
                                "param_name": "param_value (string | number | boolean | array)"
                            }
                        },
                    },
                    "revision": {
                        "notes": "string(required)",
                    },
                    "spec": {
                        "id": "string(required)",
                        "release": {
                            "version": "string(required)",
                        },
                        "includes": [
                            {
                                "id": "string",
                                "releaseVersion": "string"
                            }
                        ],
                        "excludes": [
                            {
                                "id": "string",
                                "releaseVersion": "string"
                            }
                        ]
                    }
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given app spec release does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
            subdomain="press",
        )

    @overload
    def list_deployments(
        self,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
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
        name: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_deployments(
        self,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists App deployments ordered by creation date.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/get_v1_apps_deployments>`__

        Args:
            status (List[str] | None): List of statuses to filter deployments.
                Valid values are `deploying`, `deployed`, `deleting`, `delete_failed`, `failed`, `platform_resource_error`, `redeploying`, `rollback`, `rollback_complete`, `rollback_failed`, and `warning`.
            name (str | None): Only return deployments whose names begins with the query string.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response.
                Valid fields are `createdAt`, `createdBy`, `name` and `title`.
            page_size (int | None): Number of deployments to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of deployments for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list.
        """
        method, endpoint = HttpMethods.GET, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/"

        params: Dict[str, Any] = {
            "status": status,
            "name": name,
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

    def describe_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Describes an existing App deployment, also provides details of the latest revision.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/get_v1_apps_deployments__deploymentId_>`__

        Args:
            deployment_id (str): The ID of the App deployment to retrieve.

        Returns:
            Dict[str, Any]: Dictionary containing the details of the deployment.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def redeploy(self, deployment_id: str) -> Dict[str, Any]:
        """Redeploy latest revision of an existing App deployment.

        This function allows you to redeploy an App deployment that is in a `failed` or `warning` state, provided at least one of its block deployments is also in a `failed` or `warning` state.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/post_v1_apps_deployments__deploymentId__redeploy>`__

        Args:
            deployment_id (str): The ID of the App deployment to redeploy.

        Returns:
            Dict[str, Any]: A dictionary containing details of the deployment.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment or its revisions do not exist.
            ConflictException: There is a conflict with the current state of the target resource.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}/redeploy"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def delete_deployment(self, deployment_id: str) -> Dict[None, None]:
        """Deletes an App deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/delete_v1_apps_deployments__deploymentId_>`__

        Args:
            deployment_id (str): The ID of the App deployment to delete.

        Returns:
            dict: Empty dict object.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def create_deployment_revision(self, deployment_id: str, body: Dict[str, Any]) -> Dict[str, str]:
        """Creates a new Revision of a Deployment, from a selected App Spec Release.

        Publish a new revision of an App Deployment. The payload must specify the release version of the parent spec that you wish to use (if one is not provided, the latest available will be used),
        optional revision notes in the expected format,, and optional parameters if required by the associated block spec releases.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/post_v1_apps_deployments__deploymentId__revisions>`__

        Args:
            deployment_id (str): Id of the deployment in which new revision will be created.
            body (Dict[str, str]): release version, revision notes, and any parameters required

        Returns:
            Dict[str, str]: ID of the created App deployment, and the new Revision number

        SCHEMA:
            .. code-block:: json

                {
                    "release": {
                        "version": "string"
                    },
                    "revision": {
                        "notes": "string",
                    },
                    "blocksConfig": {
                        "includes": [
                            {
                                "id": "string",
                                "releaseVersion": "string"
                            }
                        ],
                        "excludes": [
                            {
                                "id": "string",
                                "releaseVersion": "string"
                            }
                        ]
                    },
                    "appParameters": {
                        "build": {
                            "param_name": "param_value (string | number | boolean | array)"
                        },
                        "run": {
                            "param_name": "param_value (string | number | boolean | array)"
                        }
                    },
                    "parameters": {
                        "block-name-1":{
                            "build": {
                                "param_name": "param_value (string | number | boolean | array)"
                            },
                            "run": {
                                "param_name": "param_value (string | number | boolean | array)"
                            }
                        },
                        "block-name-2":{
                            "build": {
                                "param_name": "param_value (string | number | boolean | array)"
                            },
                            "run": {
                                "param_name": "param_value (string | number | boolean | array)"
                            }
                        }
                    }
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given deployment or spec release does not exist.
            ConflictException: There is a conflict with the current state of the target resource.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}/revisions"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
            subdomain="press",
        )

    def describe_deployment_revision(self, deployment_id: str, revision: str) -> dict[str, Any]:
        """Describes an existing App deployment revision, Parameters listed in the response are masked if "hideValue" was set to true when creating the associated block specs.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/get_v1_apps_deployments__deploymentId__revisions__revision_>`__

        Args:
            deployment_id (str): The ID of the App deployment to retrieve the revision from.
            revision (str): The revision number to retrieve

        Returns:
            Dict[str, Any]: Dictionary containing the details of the deployment revision.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment or revision does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}/revisions/{revision}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    @overload
    def list_deployment_revisions(
        self,
        deployment_id: str,
        sort: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_deployment_revisions(
        self,
        deployment_id: str,
        sort: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_deployment_revisions(
        self,
        deployment_id: str,
        sort: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists revisions for an App deployment ordered by creation date or provided sort key.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId__revisions>`__

        Args:
            deployment_id (str): The ID of the App deployment to retrieve the revision from.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response.
                Valid fields are `createdAt`, `createdBy`, `name` and `title`.
            status (List[str] | None): List of statuses to filter revisions.
                Valid values are `deleting`, `delete_failed`, `deployed`, `deploying`, `failed`, `platform_resource_error`, `rollback`, `rollback_complete`, `rollback_failed` and `superseded`.
            page_size (int | None): Number of revisions to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of revisions for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list.
        """
        method, endpoint = HttpMethods.GET, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}/revisions"

        params: Dict[str, Any] = {
            "sort": sort,
            "status": status,
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

    def update_deployment_metadata(self, deployment_id: str, body: Dict[str, Dict[str, str]]) -> Dict[None, None]:
        """Update the metadata of an App deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/App%20Deployments/patch_v1_apps_deployments__deploymentId_>`__

        Args:
            deployment_id (str): ID of the App deployment to update.
            body (Dict[str, Dict[str, str]]): Dictionary of the new deployment metadata.

        Returns:
            dict: Details of the updated deployment.

         SCHEMA:
            .. code-block:: json

                {
                    "description": "string",
                    "descriptionContentType": "string",
                    "imageUrl": "string",
                    "name": "string",
                    "summary": "string",
                    "tags": [
                        {
                            "name": "string",
                        }
                    ],
                    "title": "string",
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given App deployment does not exist.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.PATCH, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
            subdomain="press",
        )


def get_client(session: Optional[Session] = None) -> App:
    """Returns an App client.

    Args:
        session (Optional[Session]): A Session Object. If no session is provided, a default session is used.

    Returns:
        App: the App client object
    """
    return App(session)


__all__: List[str] = ["get_client"]
