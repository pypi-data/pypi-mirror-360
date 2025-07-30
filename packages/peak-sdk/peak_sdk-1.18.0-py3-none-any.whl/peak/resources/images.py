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
"""image client module."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, Tuple, overload

from peak.base_client import BaseClient
from peak.constants import ArtifactInfo, ContentType, HttpMethods
from peak.helpers import download_logs_helper, parse_body_for_multipart_request
from peak.session import Session


class Image(BaseClient):
    """Image Client Class."""

    BASE_ENDPOINT_V2 = "image-management/api/v2"

    def __get_artifact_details(self, artifact: Optional[ArtifactInfo] = None) -> Tuple[str | None, list[str] | None]:
        path, ignore_files = None, None

        if artifact:
            path = artifact.get("path")
            ignore_files = artifact.get("ignore_files")

        return path, ignore_files

    @overload
    def list_images(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        status: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_images(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        status: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_images(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        status: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the list of images.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/images/get_api_v2_images>`__

        Args:
            page_size (int | None): The number of images per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            name: (str | None): Image Name or version to search for.
            status (List[str] | None): Filter images on the basis of the status of the latest version.
                Valid values are `not-ready`, `ready`, `in-use`, `deleting`, `delete-failed`.
            scope (List[str] | None): Filter out on the basis of the type of the image - `global` or `custom`.
            last_build_status (List[str] | None): Filter out on the basis of last build status of the latest version.
                Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.
            tags (List[str] | None): Filter out on the basis of the tags attached to the latest version.
            return_iterator (bool): Whether to return an iterator object or list of images for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT_V2}/images/"
        params = {
            "pageSize": page_size,
            "searchTerm": name,
            "status": status,
            "scope": scope,
            "lastBuildStatus": last_build_status,
            "tags": tags,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="images",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    @overload
    def list_image_versions(
        self,
        image_id: int,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        version: Optional[str] = None,
        status: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_image_versions(
        self,
        image_id: int,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        version: Optional[str] = None,
        status: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_image_versions(
        self,
        image_id: int,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        version: Optional[str] = None,
        status: Optional[List[str]] = None,
        last_build_status: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve a list of image versions.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/get_api_v2_images__imageId__versions>`__

        Args:
            image_id (int): The Image id for which we want to get versions.
            page_size (int | None): The number of images per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            version: (str | None): Search by version.
            status (List[str] | None): Filter versions on the basis of their status.
                Valid values are `not-ready`, `ready`, `in-use`, `deleting`, `delete-failed`.
            last_build_status (List[str] | None): Filter out on the basis of last build status of version.
                Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.
            tags (List[str] | None): Filter out on the basis of the tags attached to the version.
            return_iterator (bool): Whether to return an iterator object or list of images for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any] | Dict[str, Any]: An iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform this operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions"
        params = {
            "pageSize": page_size,
            "searchTerm": version,
            "status": status,
            "lastBuildStatus": last_build_status,
            "tags": tags,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="versions",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def create_image(
        self,
        body: Dict[str, Any],
        artifact: Optional[ArtifactInfo] = None,
    ) -> Dict[str, Any]:
        """Create a new image.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/images/post_api_v2_images>`__

        Args:
            body (Dict[str, Any]):  Represents the body to be used to create image. Schema can be found below.
            artifact (Optional[ArtifactInfo]): Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.
                                        Required for image of source `upload`.

        Returns:
            Dict[str, Any]: `buildId`, `imageId`, and `versionId` of the newly created image and the corresponding version.

        SCHEMA:
            Images can be created by three ways:

            .. tabs::

                .. tab:: Upload

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Github

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "branch": "string",
                                    "repository": "string",
                                    "token": "string",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Dockerfile

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfile": "string"
                                },
                        }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            PayloadTooLargeException: The artifact exceeds maximum size.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT_V2}/images/"

        path, ignore_files = self.__get_artifact_details(artifact)
        body = parse_body_for_multipart_request(body)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=body,
            path=path,
            ignore_files=ignore_files,
        )

    def create_version(
        self,
        image_id: int,
        body: Dict[str, Any],
        artifact: Optional[ArtifactInfo] = None,
    ) -> Dict[str, Any]:
        """Create a new version.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/post_api_v2_images__imageId__versions>`__

        Args:
            image_id (int): The ID of the image for which we have to create a new version.
            body (Dict[str, Any]):  Represents the body to be used to create image version. Schema can be found below.
            artifact (Optional[ArtifactInfo]): Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.

        Returns:
            Dict[str, Any]: `imageId`, `buildId`, `versionId` and `autodeploymentId` of the newly created version.

        SCHEMA:
            Image versions can be created by three ways:

            .. tabs::

                .. tab:: Upload

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Github

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "branch": "string",
                                    "repository": "string",
                                    "token": "string",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Dockerfile

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfile": "string"
                                },
                        }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            PayloadTooLargeException: The artifact exceeds maximum size.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions"

        path, ignore_files = self.__get_artifact_details(artifact)
        body = parse_body_for_multipart_request(body)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=body,
            path=path,
            ignore_files=ignore_files,
        )

    def describe_image(
        self,
        image_id: int,
    ) -> Dict[str, Any]:
        """Retrieve details of a specific image and its latest version.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/images/get_api_v2_images__imageId_>`__

        Args:
            image_id (int): The ID of the image to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the details of the image and its latest version.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT_V2}/images/{image_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def describe_version(
        self,
        image_id: int,
        version_id: int,
    ) -> Dict[str, Any]:
        """Retrieve details of a specific version.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/get_api_v2_images__imageId__versions__versionId_>`__

        Args:
            image_id (int): The ID of the image to retrieve.
            version_id (int): The ID of the image to retrieve.

        Returns:
            Dict[str, Any]: a dictionary containing the details of the version.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions/{version_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def update_version(
        self,
        image_id: int,
        version_id: int,
        body: Dict[str, Any],
        artifact: Optional[ArtifactInfo] = None,
    ) -> dict[str, str]:
        """Update an existing image version.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/patch_api_v2_images__imageId__versions__versionId_>`__

        Args:
            image_id (int): The ID of the image to update.
            version_id (int): The ID of the version to update.
            body (Dict[str, Any]):  Represents the body to be used to update image version. Schema can be found below.
            artifact (Optional[ArtifactInfo]):    Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.

        Returns:
            Dict[str, Any]: `imageId`, `buildId`, `versionId` and `autodeploymentId` of the updated version.

        SCHEMA:
            .. tabs::

                .. tab:: Upload

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Github

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "branch": "string",
                                    "repository": "string",
                                    "token": "string",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Dockerfile

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfile": "string"
                                },
                        }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image or version does not exist.
            PayloadTooLargeException: The artifact exceeds maximum size.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.PATCH, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions/{version_id}"

        path, ignore_files = self.__get_artifact_details(artifact)
        body = parse_body_for_multipart_request(body)

        response: Dict[str, Any] = self.session.create_request(
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=body,
            path=path,
            ignore_files=ignore_files,
        )
        return response

    def create_or_update_image_version(
        self,
        body: Dict[str, Any],
        artifact: Optional[ArtifactInfo] = None,
    ) -> Dict[str, Any]:
        """Create a new image or version if none exists, update version if exists based on image name and version combination.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/images/post_api_v2_images>`__

        Args:
            body (Dict[str, Any]):  Represents the body to be used to create image. Schema can be found below.
            artifact (Optional[ArtifactInfo]): Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.

        Returns:
            Dict[str, Any]: `buildId`, `imageId`, and `versionId` of the newly created image and the corresponding version when no image/version exists.
                            In case when image exists but version doesn't it will return `buildId` and `versionId` of the newly created version along with `imageId` of the existing image.
                            In case when image and version exists, it will return `buildId` for the updated version along with `imageId` and `versionId` of the existing image / version.

        SCHEMA:
            .. tabs::

                .. tab:: Upload

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Github

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "branch": "string",
                                    "repository": "string",
                                    "token": "string",
                                    "dockerfilePath": "string",
                                    "context": "string"
                                },
                        }

                .. tab:: Dockerfile

                    .. code-block:: json

                        {
                            "name": "string (required)",
                            "type": "string (required)",
                            "description": "string",
                            "version": "string",
                            "buildDetails":
                                {
                                    "source": "string",
                                    "buildArguments": [
                                        {
                                            "name": "string",
                                            "value": "string"
                                        }
                                    ],
                                    "secrets": [],
                                    "useCache": "boolean",
                                    "dockerfile": "string"
                                },
                        }

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            PayloadTooLargeException: The artifact exceeds maximum size.
            InternalServerErrorException: The server failed to process the request.
        """
        image_name = body.get("name", "")
        version = body.get("version", "")
        response = (
            {} if not len(image_name) else self.list_images(page_size=100, return_iterator=False, name=image_name)
        )
        filtered_images = list(filter(lambda image: image.get("name", "") == image_name, response.get("images", [])))

        if len(filtered_images) > 0:
            image_id = filtered_images[0]["id"]
            versions_response = (
                {}
                if not len(version)
                else self.list_image_versions(
                    image_id=image_id,
                    version=version,
                    page_size=1,
                    return_iterator=False,
                )
            )
            filtered_versions = list(
                filter(lambda ver: ver.get("version", "") == version, versions_response.get("versions", [])),
            )
            if len(filtered_versions) > 0:
                version_id = filtered_versions[0]["id"]
                return self.update_version(image_id=image_id, version_id=version_id, body=body, artifact=artifact)

            return self.create_version(image_id=image_id, body=body, artifact=artifact)

        return self.create_image(body=body, artifact=artifact)

    def delete_image(
        self,
        image_id: int,
    ) -> Dict[None, None]:
        """Delete an Image. All the versions in the image will first go into `deleting` state before actually being deleted.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/images/delete_api_v2_images__imageId_>`__

        Args:
            image_id (int): The ID of the image to delete.

        Returns:
            dict: Empty dictionary object.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT_V2}/images/{image_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def delete_version(
        self,
        image_id: int,
        version_id: int,
    ) -> Dict[None, None]:
        """Delete an Image Version.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/delete_api_v2_images__imageId__versions__versionId_>`__

        Args:
            image_id (int): The ID of the image to delete.
            version_id (int): The ID of the version to delete.

        Returns:
            dict: Empty dictionary object.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform this operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions/{version_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def delete_versions(
        self,
        image_id: int,
        version_ids: List[int],
    ) -> Dict[None, None]:
        """Delete given versions for an image. All the versions will first go into `deleting` state before they and all their associated resources are deleted.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/versions/delete_api_v2_images__imageId__versions>`__

        Args:
            image_id (int): The ID of the image to delete.
            version_ids (List[int]): The IDs of the versions to delete.

        Returns:
            dict: Empty dictionary object.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform this operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/versions"

        params = {
            "versionIds": version_ids,
        }

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params=params,
        )

    @overload
    def list_image_builds(
        self,
        image_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        version_ids: Optional[List[str]] = None,
        build_status: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_image_builds(
        self,
        image_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        version_ids: Optional[List[str]] = None,
        build_status: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_image_builds(
        self,
        image_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        version_ids: Optional[List[str]] = None,
        build_status: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists image builds.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/builds/get_api_v2_images__imageId__builds>`__

        Args:
            image_id (int): ID of the image to fetch image build history.
            date_from (str | None): The date after which the image builds should be included (in ISO format).
                It is 90 days from current date by default.
            date_to (str | None): The date till which the image builds should be included (in ISO format).
                It is current date by default.
            page_size (int | None): Number of builds per page.
            page_number (int | None): Page number to retrieve. Only used when return_iterator is False.
            count (int | None): Number of builds required (Ordered by latest to earliest).
                For example, if 5 is provided, it will return last 5 builds.
                It is -1 by default which means it will return all the available builds within the given dates.
            version_ids (List[str] | None): List of version ids to filter builds.
            build_status (List[str] | None): List of build statuses to filter builds.
                Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.


            return_iterator (bool): Whether to return an iterator object or a dictionary of list of image builds. Defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT_V2}/images/{image_id}/builds"

        params: Dict[str, Any] = {
            "dateTo": date_to,
            "dateFrom": date_from,
            "pageSize": page_size,
            "count": -1 if count is None else count,
            "versions": version_ids,
            "buildStatus": build_status,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                params=params,
                response_key="builds",
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def get_build_logs(
        self,
        image_id: int,
        build_id: int,
        next_token: Optional[str] = None,
        save: Optional[bool] = False,  # noqa: FBT002
        file_name: Optional[str | None] = None,
    ) -> Dict[str, Any] | None:
        """Retrieve or save the logs of an image build.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/image-management/api-docs/index.htm#/builds/get_api_v2_images__imageId__builds__buildId__logs>`__

        Args:
            image_id (int): The ID of the image.
            build_id (int): The ID of the image build.
            next_token (str | None): The token to retrieve the next set of logs.
            save (bool): Whether to save the logs to a file. Defaults to False.
            file_name (str | None): File name or path where the contents should be saved. Default file name is `image_build_logs_{image_id}_{build_id}.log`.

        Returns:
            Dict[str, Any]: A dictionary containing the logs of the build. If `save` is set to True, the signed URL to download the logs is returned and the logs are saved to a file.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform this operation.
            NotFoundException: The given image or build does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method = HttpMethods.GET
        get_logs_endpoint = f"{self.BASE_ENDPOINT_V2}/images/{image_id}/builds/{build_id}/logs"
        download_logs_endpoint = f"{get_logs_endpoint}/download"

        if save:
            response = self.session.create_request(
                download_logs_endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
            )
            updated_file_name = (
                f"image_build_logs_{image_id}_{build_id}.log" if not file_name or not len(file_name) else file_name
            )
            download_logs_helper(response=response, file_name=updated_file_name)
            return None

        params: Dict[str, Any] = {
            "nextToken": next_token,
        }

        return self.session.create_request(  # type: ignore[no-any-return]
            get_logs_endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params=params,
        )


def get_client(session: Optional[Session] = None) -> Image:
    """Returns an Image Management client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Image: the image client object
    """
    return Image(session)


__all__: List[str] = ["get_client"]
