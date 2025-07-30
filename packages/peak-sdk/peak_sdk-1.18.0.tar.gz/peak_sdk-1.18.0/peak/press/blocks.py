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
"""Blocks client module."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional, overload

import yaml

from peak.base_client import BaseClient
from peak.constants import ArtifactInfo, ContentType, HttpMethods
from peak.session import Session


class Block(BaseClient):
    """Client class for interacting with Blocks."""

    SPECS_BASE_ENDPOINT = "v1/blocks/specs"
    DEPLOYMENTS_BASE_ENDPOINT = "v1/blocks/deployments"

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
        """Lists all published Block specs ordered by creation date. Returns info for the latest release for each spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs>`__

        Args:
            status (List[str] | None): List of statuses to filter specs.
                Valid values are `available`, `unavailable` and `archived`.
            featured (bool | None): Whether to only return featured specs.
            name (str | None): Only return specs whose names begins with the query string.
            title (str | None): Only return specs whose title begins with the query string.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response,
                defaults to `[]`. Valid fields are `createdAt`, `createdBy`, `name` and `title`.
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
            StopIteration: There are no more pages to list.
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
        artifact: Optional[ArtifactInfo] = None,
        featured: Optional[bool] = None,
        scope: Optional[str] = None,
        tenants: Optional[List[str]] = None,
        parameters: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        auto_run_on_deploy: Optional[bool] = None,
    ) -> Dict[str, str]:
        """Create a new Block spec.

        For each Block kind, all Specs must have unique names within a tenant.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/post_v1_blocks_specs>`__

        Args:
            body (Dict[str, Any]): Dictionary containing Block spec metadata and configuration.
            artifact (ArtifactInfo | None):    Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.
                                        It is not required if an existing image and version is used for creating the spec.
            featured (bool | None): Whether to feature this spec. By default it is False.
            scope (str | None): Specify weather tenants can discover and deploy this spec.
                `private` restricts the spec to this tenant alone, `public` makes it available on all tenants
                and `shared` allows specifying what set of tenants can access and use this spec.
                By default it is `private`.
            tenants (List[str] | None): Given a shared scope, specify what other tenants can discover and deploy this spec.
            parameters (Optional[Dict[str, List[Dict[str, Any]]]]): A dictionary containing optional keys `build` and `run`. The structure of the dictionary is as follows:

                - `build` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given and used at deployment time.
                - `run` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given at deployment time and will be used at run time.
            auto_run_on_deploy (bool | None): Whether to execute the resource after the block is deployed. By default it is False.

        Returns:
            Dict[str, str]: Id of the created block spec.

        SCHEMA (body):
            Information about providing image details in blocks can be found `here <https://docs.peak.ai/sdk/latest/snippets/press-examples.html#providing-image-details-for-block-specs>`__.

            .. tabs::

                .. tab:: Workflow Block Spec

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
                                "notes": "string",
                                "version": "string (required)",
                            },
                            "config": {
                                "images": {
                                    "image-name": {
                                        "version": "string",
                                        "dockerfile": "string",
                                        "context": "string",
                                        "useCache": "boolean",
                                        "buildArguments": {
                                            "key (string)": "value (string)"
                                        },
                                    }
                                },
                                "steps": {
                                    "stepName": {
                                        "type": "standard",
                                        "image": {
                                            "version": "string",
                                            "dockerfile": "string",
                                            "context": "string",
                                            "useCache": "boolean",
                                            "buildArguments": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": []
                                        }
                                        "imageRef": "string",
                                        "imageDetails": {
                                            "id": "number (required)",
                                            "versionId": "number"
                                        },
                                        "command": "string (required)",
                                        "resources": {
                                            "instanceTypeId": "number",
                                            "storage": "string"
                                        },
                                        "parents": [],
                                        "stepTimeout": "number",
                                        "clearImageCache": "boolean",
                                        "repository": {
                                            "branch": "string",
                                            "token": "string",
                                            "url": "string"
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        },
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": [],
                                        },
                                        "outputParameters": {
                                            "key (string)": "value (string)"
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        }
                                    },
                                    "stepName2": {
                                        "type": "http",
                                        "method": "enum(get, post, put, patch, delete)",
                                        "url": "string",
                                        "payload": "string",
                                        "headers": {
                                            "absolute": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": {
                                                "key (string)": "value (string)"
                                            }
                                        },
                                        "auth": {
                                            "type": "enum(no-auth, oauth, basic, api-key, bearer-token)(required)",
                                            "clientId": "string | required for oauth",
                                            "clientSecret": "",
                                            "authUrl": "string | required for oauth",
                                            "username": "string | required for basic",
                                            "password": "",
                                            "apiKey": "",
                                            "bearerToken": "string | required for bearer-token"
                                        },
                                        "parents": [],
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "inherit": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": [],
                                        },
                                        "outputParameters": {
                                            "key (string)": "value (string)"
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    },
                                    "stepName3": {
                                        "type": "export",
                                        "schema": "string (required)",
                                        "table": "string (required)",
                                        "sortBy": "string (required)",
                                        "sortOrder": "enum(asc, desc) | Default is asc",
                                        "compression": "boolean | Default is false",
                                        "parents": [],
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    },
                                    "stepName4": {
                                        "type": "sql",
                                        "sqlQueryPath": "string",
                                        "repository": {
                                            "branch": "string | Required if repository is provided",
                                            "token": "string",
                                            "url": "string | Required if repository is provided",
                                            "filePath": "string | Required if repository is provided"
                                        }
                                        "parents": [],
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "inherit": {
                                                "key (string)": "value (string)"
                                            }
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    }
                                },
                                "triggers": [
                                    {
                                        "cron": "string"
                                    },
                                    {
                                        "webhook": "boolean"
                                    },
                                ],
                                "watchers": [
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "user": "string",
                                    },
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "webhook": {
                                            "name": "string(required)",
                                            "url": "string(required)",
                                            "payload": "string(required)"
                                        }
                                    },
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "email": {
                                            "name": "string",
                                            "recipients": {
                                                "to": ["string"]
                                            }
                                        }
                                    }
                                ],
                            }
                        }

                .. tab:: Service Block Spec

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
                                "notes": "string",
                                "version": "string (required)",
                            },
                            "config": {
                                "serviceType": "string",
                                "image": {
                                    "version": "string",
                                    "dockerfile": "string",
                                    "context": "string",
                                    "useCache": "boolean",
                                    "buildArguments": {
                                        "key (string)": "value (string)"
                                    },
                                    "secrets": []
                                },
                                "imageDetails": {
                                    "id": "number (required)",
                                    "versionId": "number"
                                },
                                "resources": {
                                    "instanceTypeId": "number (required)",
                                },
                                "parameters": {
                                    "env": {
                                        "key (string)": "value (string)"
                                    },
                                    "secrets": []
                                },
                                "sessionStickiness": "boolean (only for web-app service)",
                                "scaleToZero": "boolean (only for web-app service)",
                                "entrypoint": "string",
                                "healthCheckURL": "string",
                                "minInstances": "number. Default is 1 and maximum is 2",
                            }
                        }

        SCHEMA(Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {   "build": [
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
                                    "operator": "equals|not-equals",
                                    "value": "string|number|boolean"
                                },
                                // Composite condition
                                {
                                    "conditionType": "AND|OR",
                                    "conditions": [
                                        {
                                            "dependsOn": "string",
                                            "operator": "equals|not-equals",
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
            PayloadTooLargeException: The given artifact size exceeds maximum limit.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.SPECS_BASE_ENDPOINT}/"

        request_body = {
            "spec": json.dumps(body),
            "featured": json.dumps(featured),
            "scope": scope,
            "autoRunOnDeploy": json.dumps(auto_run_on_deploy),
        }

        if tenants:
            request_body["tenants"] = json.dumps(tenants)

        if parameters:
            request_body["parameters"] = json.dumps(parameters)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=request_body,
            path=artifact["path"] if artifact is not None else None,
            ignore_files=artifact.get("ignore_files") if artifact is not None else None,
            subdomain="press",
        )

    def describe_spec(
        self,
        spec_id: str,
    ) -> Dict[str, Any]:
        """Describes an existing Block spec and also provides details of the latest release.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId_>`__

        Args:
            spec_id (str): The ID of the block spec to retrieve.

        Returns:
            Dict[str, Any]: Dictionary containing the details of the spec.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given block spec does not exist.
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
        """Update the metadata and discoverability of a Block Spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/patch_v1_blocks_specs__specId_>`__

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
            NotFoundException: The given block spec does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
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

    def delete_spec(
        self,
        spec_id: str,
    ) -> Dict[None, None]:
        """Delete a Block Spec and all it's associated releases.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/delete_v1_blocks_specs__specId_>`__

        Args:
            spec_id (str): The ID of the Block spec to delete.

        Returns:
            dict: Empty dict object.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given Block spec does not exist.
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

    def create_spec_release(
        self,
        spec_id: str,
        body: Dict[str, Any],
        artifact: Optional[ArtifactInfo] = None,
        parameters: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        auto_run_on_deploy: Optional[bool] = None,
    ) -> Dict[str, str]:
        """Publish a new release to an existing Block spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/post_v1_blocks_specs__specId__releases>`__

        Args:
            spec_id (str): Id of the spec in which new release will be created.
            body (Dict[str, Any]): Dictionary containing updated release and config in the expected format.
            artifact (ArtifactInfo | None):    Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.
                                        It is not required if an existing image and version is used for creating the spec.
            parameters (Optional[Dict[str, List[Dict[str, Any]]]]): A dictionary containing optional keys `build` and `run`. The structure of the dictionary is as follows:

                - `build` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given and used at deployment time.
                - `run` (List[Dict[str, Any]], optional): A list of parameter objects, the values of which will be given at deployment time and will be used at run time.
            auto_run_on_deploy (bool | None): Whether to execute the resource after the block is deployed. By default it is False.

        Returns:
            Dict[str, str]: Dictionary containing spec id and release version.

        SCHEMA (body):
            Information about providing image details in blocks can be found `here <https://docs.peak.ai/sdk/latest/snippets/press-examples.html#providing-image-details-for-block-specs>`__.

            .. tabs::

                .. tab:: Workflow Block Spec

                    .. code-block:: json

                        {
                            "release": {
                                "notes": "string",
                                "version": "string (required)",
                            },
                            "config": {
                                "images": {
                                    "image-name": {
                                        "version": "string",
                                        "dockerfile": "string",
                                        "context": "string",
                                        "useCache": "boolean",
                                        "buildArguments": {
                                            "key (string)": "value (string)"
                                        },
                                    }
                                },
                                "steps": {
                                    "stepName": {
                                        "type": "string",
                                        "image": {
                                            "version": "string",
                                            "dockerfile": "string",
                                            "context": "string",
                                            "useCache": "boolean",
                                            "buildArguments": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": []
                                        }
                                        "imageRef": "string",
                                        "imageDetails": {
                                            "id": "number (required)",
                                            "versionId": "number"
                                        },
                                        "command": "string (required)",
                                        "resources": {
                                            "instanceTypeId": "number",
                                            "storage": "string"
                                        },
                                        "parents": [],
                                        "stepTimeout": "number",
                                        "clearImageCache": "boolean",
                                        "repository": {
                                            "branch": "string",
                                            "token": "string",
                                            "url": "string"
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        },
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": [],
                                        },
                                        "outputParameters": {
                                            "key (string)": "value (string)"
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        }
                                    },
                                    "stepName2": {
                                        "type": "http",
                                        "method": "enum(get, post, put, patch, delete)",
                                        "url": "string",
                                        "payload": "string",
                                        "headers": {
                                            "absolute": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": {
                                                "key (string)": "value (string)"
                                            }
                                        },
                                        "auth": {
                                            "type": "enum(no-auth, oauth, basic, api-key, bearer-token)(required)",
                                            "clientId": "string | required for oauth",
                                            "clientSecret": "",
                                            "authUrl": "string | required for oauth",
                                            "username": "string | required for basic",
                                            "password": "",
                                            "apiKey": "",
                                            "bearerToken": "string | required for bearer-token"
                                        },
                                        "parents": [],
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "inherit": {
                                                "key (string)": "value (string)"
                                            },
                                            "secrets": [],
                                        },
                                        "outputParameters": {
                                            "key (string)": "value (string)"
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    },
                                    "stepName3": {
                                        "type": "export",
                                        "schema": "string (required)",
                                        "table": "string (required)",
                                        "sortBy": "string (required)",
                                        "sortOrder": "enum(asc, desc) | Default is asc",
                                        "compression": "boolean | Default is false",
                                        "parents": [],
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    },
                                    "stepName4": {
                                        "type": "sql",
                                        "sqlQueryPath": "string",
                                        "repository": {
                                            "branch": "string | Required if repository is provided",
                                            "token": "string",
                                            "url": "string | Required if repository is provided",
                                            "filePath": "string | Required if repository is provided"
                                        }
                                        "parents": [],
                                        "parameters": {
                                            "env": {
                                                "key (string)": "value (string)"
                                            },
                                            "inherit": {
                                                "key (string)": "value (string)"
                                            }
                                        },
                                        "executionParameters": {
                                            "conditional": [
                                                {
                                                    "condition": "string",
                                                    "paramName": "string",
                                                    "stepName": "string",
                                                    "value": "string"
                                                }
                                            ],
                                            "parentStatus": [
                                                {
                                                    "condition": "string",
                                                    "parents": [],
                                                    "status": []
                                                }
                                            ]
                                        },
                                        "runConfiguration": {
                                            "retryOptions": {
                                                "duration": "number",
                                                "exitCodes": [],
                                                "exponentialBackoff": "boolean",
                                                "numberOfRetries": "number"
                                            },
                                            "skipConfiguration": {
                                                "skip": "boolean",
                                                "skipDAG": "boolean",
                                            }
                                        }
                                    }
                                },
                                "triggers": [
                                    {
                                        "cron": "string"
                                    },
                                    {
                                        "webhook": "boolean"
                                    }
                                ],
                                "watchers": [
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "user": "string",
                                    },
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "webhook": {
                                            "name": "string(required)",
                                            "url": "string(required)",
                                            "payload": "string(required)"
                                        }
                                    },
                                    {
                                        "events": {
                                            "success": "boolean",
                                            "fail": "boolean",
                                            "runtimeExceeded": "number"
                                        },
                                        "email": {
                                            "name": "string",
                                            "recipients": {
                                                "to": ["string"]
                                            }
                                        }
                                    }
                                ],
                            }
                        }

                .. tab:: Service Block Spec

                    .. code-block:: json

                        {
                            "release": {
                                "notes": "string",
                                "version": "string (required)",
                            },
                            "config": {
                                "serviceType": "string",
                                "image": {
                                    "version": "string",
                                    "dockerfile": "string",
                                    "context": "string",
                                    "useCache": "boolean",
                                    "buildArguments": {
                                        "key (string)": "value (string)"
                                    },
                                    "secrets": []
                                },
                                "imageDetails": {
                                    "id": "number (required)",
                                    "versionId": "number"
                                },
                                "resources": {
                                    "instanceTypeId": "number (required)",
                                },
                                "parameters": {
                                    "env": {
                                        "key (string)": "value (string)"
                                    },
                                    "secrets": []
                                },
                                "sessionStickiness": "boolean (only for web-app service)",
                                "scaleToZero": "boolean (only for web-app service)",
                                "entrypoint": "string",
                                "healthCheckURL": "string",
                                "minInstances": "number. Default is 1 and maximum is 2",
                            }
                        }

        SCHEMA(Parameters):
            The valid types for parameters are `boolean`, `string`, `string_array`, `number`, `number_array`, `object` and `object_array`.

            .. code-block:: json

                {   "build": [
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
                                    "operator": "equals|not-equals",
                                    "value": "string|number|boolean"
                                },
                                // Composite condition
                                {
                                    "conditionType": "AND|OR",
                                    "conditions": [
                                        {
                                            "dependsOn": "string",
                                            "operator": "equals|not-equals",
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
            PayloadTooLargeException: The given artifact size exceeds maximum limit.
            NotFoundException: The given app spec does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases"

        request_body = {
            "spec": json.dumps(body),
            "autoRunOnDeploy": json.dumps(auto_run_on_deploy),
        }

        if parameters:
            request_body["parameters"] = json.dumps(parameters)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=request_body,
            path=artifact["path"] if artifact is not None else None,
            ignore_files=artifact.get("ignore_files") if artifact is not None else None,
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
        """Get all releases of a Block spec (ordered by most recently created to oldest).

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId__releases>`__

        Args:
            spec_id (str): The ID of the Block spec to retrieve.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response.
                Valid fields are `createdAt` and `createdBy`.
            page_size (int | None): Number of specs to include per page.
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
            NotFoundException: The given Block spec does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list.
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases"
        params: Dict[str, Any] = {
            "pageSize": page_size,
            "sort": sort,
        }

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

    def describe_spec_release(
        self,
        spec_id: str,
        version: str,
    ) -> Dict[str, Any]:
        """Describe an existing spec release.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId__releases__release_>`__

        Args:
            spec_id (str): The ID of the block spec to retrieve.
            version (str): The release version of spec to retrieve in valid semantic versioning format.

        Returns:
            Dict[str, Any]: Dictionary containing the details of the spec.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given block spec does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.SPECS_BASE_ENDPOINT}/{spec_id}/releases/{version}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def create_deployment(self, body: Dict[str, str]) -> Dict[str, str]:
        """Creates a new deployment from Block spec.

        Uses the latest spec release if release version is not provided.
        For each Block kind, all Deployments must have unique names within a tenant.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/post_v1_blocks_deployments>`__

        Args:
            body (Dict[str, str]): Dictionary containing deployment metadata, spec ID, release version (optional, defaults to latest spec release), revision info and parameters that would be used at run-time.

        Returns:
            Dict[str, str]: ID of the created Block deployment

        SCHEMA:
            .. code-block:: json

                {
                    "metadata": {
                        "description": "string",
                        "descriptionContentType": "string",
                        "imageUrl": "string",
                        "name": "string(required)",
                        "summary": "string(required)",
                        "tags": [
                            {
                                "name": "string",
                            }
                        ],
                        "title": "string",
                    },
                    "parameters": {
                        "build": {
                            "param_name": "param_value (string | number | boolean | array)"
                        },
                        "run": {
                            "param_name": "param_value (string | number | boolean | array)"
                        }
                    },
                    "revision": {
                        "notes": "string(required)",
                    },
                    "spec": {
                        "id": "string(required)",
                        "release": {
                            "version": "string",
                        }
                    }
                }

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given block spec release does not exist.
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
        title: Optional[str] = None,
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
        title: Optional[str] = None,
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
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists Block deployments ordered by creation date.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments>`__

        Args:
            status (List[str] | None): List of statuses to filter deployments.
                Valid values are `deploying`, `deployed`, `deleting`, `delete_failed`, `failed`, `platform_resource_error`, `redeploying`, `rollback`, `rollback_complete`, `rollback_failed`, and `warning`.
            name (str | None): Only return deployments whose names begins with the query string.
            title (str | None): Only return deployments whose title begins with the query string.
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
            "title": title,
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

    def describe_deployment(self, deployment_id: str) -> dict[str, Any]:
        """Describes an existing Block deployment, also provides details of the latest revision. Parameters listed in the response are masked if "hideValue" was set to true when creating th block spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId_>`__

        Args:
            deployment_id (str): The ID of the Block deployment to retrieve.

        Returns:
            Dict[str, Any]: Dictionary containing the details of the deployment.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given Block deployment does not exist.
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

    def update_deployment_metadata(
        self,
        deployment_id: str,
        body: Dict[str, Any],
    ) -> Dict[None, None]:
        """Update the metadata of the Block deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/patch_v1_blocks_deployments__deploymentId_>`__

        Args:
            deployment_id (str): ID of the Block deployment to update.
            body (Dict[str, Any]): Dictionary of the new deployment metadata.

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
            NotFoundException: The given block spec does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server encountered an unexpected condition that
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

    def redeploy(self, deployment_id: str) -> Dict[str, Any]:
        """Redeploy latest revision of an existing Block deployment.

        This function allows you to redeploy a Block deployment that is in `failed` or `warning` state.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/post_v1_blocks_deployments__deploymentId__redeploy>`__

        Args:
            deployment_id (str): The ID of the Block deployment to redeploy.

        Returns:
            Dict[str, Any]: A dictionary containing details of the deployment.

        Raises:
            BadRequestException: The given parameters are invalid.
            ConflictException: There is a conflict with the current state of the target resource.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            NotFoundException: The given block deployment or its revisions do not exist.
            UnauthorizedException: The credentials are invalid.
        """
        method, endpoint = HttpMethods.POST, f"{self.DEPLOYMENTS_BASE_ENDPOINT}/{deployment_id}/redeploy"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

    def delete_deployment(self, deployment_id: str) -> Dict[None, None]:
        """Deletes the Block deployment.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/delete_v1_blocks_deployments__deploymentId_>`__

        Args:
            deployment_id (str): The ID of the Block deployment to delete.

        Returns:
            dict: Empty dict object.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given Block deployment does not exist.
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

    def create_deployment_revision(self, deployment_id: str, body: Dict[str, str]) -> Dict[str, str]:
        """Creates a new Revision of a Deployment, from a selected Block Spec Release.

        Publish a new revision of a Block Deployment. The payload may specify the release version of the parent spec that you wish to use (if one is not provided, the latest available will be used),
        optional revision notes in the expected format, and optional parameters if required by the spec release.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/post_v1_blocks_deployments__deploymentId__revisions>`__

        Args:
            deployment_id (str): Id of the deployment in which new revision will be created.
            body (Dict[str, str]): release version, revision notes, and any parameters required

        Returns:
            Dict[str, str]: ID of the created Block deployment, and the new Revision number

        SCHEMA:
            .. code-block:: json

                {
                    "release": {
                        "version": "string"
                    },
                    "revision": {
                        "notes": "string",
                    },
                    "parameters": {
                        "build": {
                            "param_name": "param_value (string | number | boolean | array)"
                        },
                        "run": {
                            "param_name": "param_value (string | number | boolean | array)"
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
        """Describes an existing Block deployment revision, Parameters listed in the response are masked if "hideValue" was set to true when creating the block spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId__revisions__revision_>`__

        Args:
            deployment_id (str): The ID of the Block deployment to retrieve the revision from.
            revision (str): The revision number to retrieve

        Returns:
            Dict[str, Any]: Dictionary containing the details of the deployment revision.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given Block deployment or revision does not exist.
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
        """Lists revisions for a Block deployment ordered by creation date or provided sort key.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId__revisions>`__

        Args:
            deployment_id (str): The ID of the Block deployment to retrieve the revision from.
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
            NotFoundException: The given Block deployment or revision does not exist.
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

    def get_parameters(
        self,
        deployment_id: Optional[str] = None,
        fallback_params_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get the parameters for a deployment at run time.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/get_v1_deployments__deploymentId__parameters_run>`__

        Args:
            deployment_id (str | None): The ID of the deployment.
            fallback_params_file (str | None): Path of the YAML file to be used when deployment_id is not present.

        Returns:
            Dict[str, Any]: Dictionary containing deployment run parameters.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given deployment does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            TypeError: Required parameters were not passed or the YAML file is invalid.
            FileNotFoundError: File specified in fallback_params_file is not present.
        """
        final_deployment_id = os.getenv("PRESS_DEPLOYMENT_ID", deployment_id)

        if not final_deployment_id:
            if not fallback_params_file:
                msg = "Please pass in a fallback params file when deployment id is not present"
                raise TypeError(msg) from None

            file_path = Path(fallback_params_file)
            if not file_path.is_file():
                msg = f"File - {fallback_params_file} does not exist. Please check the path again."
                raise FileNotFoundError(msg) from None

            with file_path.open() as file:
                try:
                    return dict(yaml.safe_load(file.read()))
                except (yaml.YAMLError, ValueError):
                    msg = f"{fallback_params_file} is not a valid YAML. Please validate the file content."
                    raise TypeError(msg) from None

        method, endpoint = HttpMethods.GET, f"v1/deployments/{final_deployment_id}/parameters/run"

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

    def get_related_block_details(
        self,
        deployment_id: Optional[str] = None,
        fallback_details_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get the info for related blocks within an app.

        Args:
            deployment_id (str | None): The ID of the deployment.
            fallback_details_file (str | None): Path of the YAML file to be used when deployment_id is not present. should be a List of Dicts

        Returns:
            A list of dictionaries, where each dictionary represents a block with the following keys:
            - "id" (str): The unique identifier of the block
            - "resource_id" (str | None): The unique identifier of the block's main platform resource.
                May be None if resource has been manually deleted or is awaiting creation
            - "kind" (str): The type or category of the resource.
            - "name" (str): The name of the resource.
            - "status" (str): The current status of the block. The platform resource status can be inferred from this.

        Example return value:
            .. code-block:: json

                [
                    {   "id": "12345",
                        "resource_id": "6789",
                        "kind": "workflow",
                        "name": "my-workflow",
                        "status": "deployed",
                    },
                ]

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given deployment does not exist.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            TypeError: The YAML file is invalid.
            ValueError: The YAML file is empty.
            FileNotFoundError: File specified in fallback_details_file is not present.
        """
        final_deployment_id = os.getenv("PRESS_DEPLOYMENT_ID", deployment_id)

        if not final_deployment_id:
            if not fallback_details_file:
                msg = "Please pass in a fallback details file when deployment id is not present"
                raise TypeError(msg) from None

            file_path = Path(fallback_details_file)
            if not file_path.is_file():
                msg = f"File - {fallback_details_file} does not exist. Please check the path again."
                raise FileNotFoundError(msg) from None

            with file_path.open() as file:
                file_content = file.read().strip()
                if not file_content:
                    msg = f"{fallback_details_file} is an empty YAML file."
                    raise ValueError(msg)

                try:
                    return list(yaml.safe_load(file_content))

                except yaml.YAMLError:
                    msg = f"{fallback_details_file} is not a valid YAML. Please validate the file content."
                    raise TypeError(msg) from None

        this_block = self.session.create_request(
            f"v1/blocks/deployments/{final_deployment_id}",
            HttpMethods.GET,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

        if not isinstance(this_block, dict) or this_block.get("parent") is None:
            return []

        parent_id = this_block["parent"].get("id")

        this_app = self.session.create_request(
            f"v1/apps/deployments/{parent_id}",
            HttpMethods.GET,
            content_type=ContentType.APPLICATION_JSON,
            subdomain="press",
        )

        return [
            {
                "id": block["deploymentId"],
                "resource_id": block["platformId"],
                "kind": block["kind"],
                "name": block["name"],
                "status": block["status"],
            }
            for block in this_app["latestRevision"]["blocks"]
        ]


def get_client(session: Optional[Session] = None) -> Block:
    """Returns a Block client.

    Args:
        session (Optional[Session]): A Session Object. If no session is provided, a default session is used.

    Returns:
        Block: the Block client object
    """
    return Block(session)


__all__: List[str] = ["get_client"]
