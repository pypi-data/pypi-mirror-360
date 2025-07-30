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

"""Metrics client module."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ArtifactInfo, ContentType, HttpMethods
from peak.exceptions import InvalidParameterException
from peak.session import Session


class Metric(BaseClient):
    """Client class for interacting with metrics resource."""

    BASE_ENDPOINT = "semantic-layer/api/v1"

    def __get_artifact_details(self, artifact: ArtifactInfo) -> str | None:
        path = None

        if artifact:
            path = artifact.get("path")

        return path

    def publish(
        self,
        artifact: Optional[ArtifactInfo] = None,
        collection_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Publish Metrics.

        The metrics can be published either by passing artifact and namespace,
        or by passing collection_id and namespace. If both artifact and collection_id
        are provided, artifact takes priority. If the namespace is not provided, the 'default' namespace is used.
        You can optionally include `namespaceMetadata` and `namespaceDescription` in the body
        to provide additional context about the namespace.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/post_api_v1_metrics>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the details to publish the metrics.
            artifact (ArtifactInfo | None): Mapping of artifact attributes that specifies how the artifact will be generated,
                                     it accepts one key `path`,
            collection_id (str | None): The ID of the collection to publish the metrics.

        Returns:
            Dict[str, Any]: A dictionary containing details about the published metrics.

        SCHEMA:
            .. code-block:: json

                {
                  "namespace": "string",
                  "namespaceMetadata": { "key": "value" },
                  "namespaceDescription": "Optional description"
                }

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        if body and "namespaceMetadata" in body:
            body["namespaceMetadata"] = json.dumps(body["namespaceMetadata"])

        if artifact:
            method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/metrics"
            path = self.__get_artifact_details(artifact)
            return self.session.create_request(  # type: ignore[no-any-return]
                endpoint,
                method,
                content_type=ContentType.MULTIPART_FORM_DATA,
                body=body,
                path=path,
            )

        if collection_id:
            method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/metrics/collections/{collection_id}/publish"
            return self.session.create_request(  # type: ignore[no-any-return]
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                body=body,
            )

        raise InvalidParameterException(
            message="Either Artifact or Collection ID must be passed to publish the metrics.",
        )

    def query(
        self,
        measures: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        generate_sql: Optional[bool] = False,  # noqa: FBT002
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        time_dimensions: Optional[List[Dict[str, Any]]] = None,
        segments: Optional[List[str]] = None,
        order: Optional[Dict[str, Literal["asc", "desc"]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Query a published metric in the semantic layer using the provided parameters.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Query/get_api_v1_metrics_query>`__

        Args:
            measures (List[str] | None): An array of measures to include in the query. Measures represent quantitative metrics such as sums or counts.
            namespace (str | None): The namespace associated with the metrics. If not provided, the default namespace is used.
            generate_sql (bool | None): Indicates whether to return the SQL query instead of data. If `true`, the response will include the SQL query used to retrieve the metrics. Default is `false`.
            dimensions (List[str] | None): An array of dimensions to include in the query. Dimensions represent qualitative categories such as time, location, or product names.
            filters (List[Dict[str, Any]] | None): An array of filter objects to apply to the query. Filters limit the data returned based on specific conditions.
                dimension (str): The dimension to filter on.
                operator (str): The operator to use for the filter. Supported values are `equals`, `notEquals`, `contains`, `notContains`, `startsWith`, `notStartsWith`, `endsWith`, `notEndsWith`, `gt`, `gte`, `lt`, `lte`, `inDateRange`, `notInDateRange`, `beforeDate`, `beforeOrOnDate`, `afterDate`, `afterOrOnDate` etc.
                values (List[str]): An array of values to filter on.
            time_dimensions (List[Dict[str, Any]] | None): Time dimensions allow querying over specific time ranges with optional granularity (e.g., day, month, year).
                dimension (str): The time dimension to include in the query.
                granularity (str | None): The granularity of the time dimension. Supported values are `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, and `year`.
                dateRange (list(str) | str | None): An array of two dates that define the time range for the query. Alternatively, you can provide a single string out of the following predefined date ranges `today`, `yesterday`, `this week`, `last week`, `this month`, `last month`, `this quarter`, `last quarter`, `this year`, `last year`, `last 7 days` and `last 30 days`.
            segments (List[str] | None): An array of segments to include in the query. Segments represent pre-defined filters that can be applied to metrics.
            order (Dict[str, Any] | None): Defines the sort order of the results. This is an object where keys are the dimensions/measures and values are either 'asc' or 'desc' to specify ascending or descending order.
            limit (int | None): Limits the number of rows returned by the query. If not provided, the default limit is applied.
            offset (int | None): Specifies the number of rows to skip before starting to return data. Useful for pagination.

        Returns:
            Dict[str, Any]: A dictionary containing the query metrics response.

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/metrics/query"

        request_params = {
            "namespace": namespace,
            "generateSql": str(generate_sql).lower(),
            "measures": measures,
            "dimensions": dimensions,
            "filters": json.dumps(filters) if filters else None,
            "timeDimensions": json.dumps(time_dimensions) if time_dimensions else None,
            "segments": segments,
            "order": json.dumps(order) if order else None,
            "limit": limit,
            "offset": offset,
        }

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            params=request_params,
            content_type=ContentType.APPLICATION_JSON,
        )

    @overload
    def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        publication_id: Optional[str] = None,
        namespace: Optional[str] = None,
        search_term: Optional[str] = None,
        type: Optional[str] = None,  # noqa: A002
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        publication_id: Optional[str] = None,
        namespace: Optional[str] = None,
        search_term: Optional[str] = None,
        type: Optional[str] = None,  # noqa: A002
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        publication_id: Optional[str] = None,
        namespace: Optional[str] = None,
        search_term: Optional[str] = None,
        type: Optional[str] = None,  # noqa: A002
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the list of metrics.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/get_api_v1_metrics>`__

        Args:
            page_size (int | None): The number of images per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            publication_id (str | None): The publication ID to retrieve metrics from. If not provided, all metrics are retrieved.
            namespace (str | None): The namespace associated with the metrics. If not provided, the default namespace is used.
            search_term (str | None): The search term to filter the metrics by. If not provided, all metrics are retrieved.
            type (str | None): The type of metrics to retrieve. If not provided, all metrics are retrieved. Available types are `cube`, `view`, `dimension`, `measure`, `segment` and `all`.
            return_iterator (bool): Whether to return an iterator object or list of metrics for a specified page number, defaults to True.

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
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/metrics"
        params = {
            "pageSize": page_size,
            "publicationId": publication_id,
            "namespace": namespace,
            "searchTerm": search_term,
            "type": type,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="data",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def delete(
        self,
        *,
        namespace: Optional[str] = None,
        measures: Optional[List[str]] = None,
        publication_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete one or more measures.

        The measures can be deleted either by passing publication_id in which case all metrics related to the publication will be deleted.
        Or by passing namespace and measures in which case only the specified measures will be deleted.
        If both are passed, publication_id takes priority.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/delete_api_v1_metrics_publications__publicationId_>`__

        Args:
            namespace (str): The namespace to delete the measures from. Required if measures is passed.
            measures (List[str]): An array of measures to delete.
            publication_id (str): The publication ID to delete. Passing this will delete all the metrics in the
                publication.

        Returns:
            Dict[str, Any]: An empty dictionary.

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        if publication_id:
            method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/metrics/publications/{publication_id}"
            return self.session.create_request(  # type: ignore[no-any-return]
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
            )

        if measures:
            method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/metrics"
            body = {"namespace": namespace, "measures": measures}
            return self.session.create_request(  # type: ignore[no-any-return]
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                params=body,
            )

        raise InvalidParameterException(
            message="Either Publication Id or Measures must be passed.",
        )

    def create_collection(
        self,
        artifact: ArtifactInfo,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create Metric Collection.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/post_api_v1_metrics_collections>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the details to publish the metrics.
            artifact (ArtifactInfo): Mapping of artifact attributes that specifies how the artifact will be generated,
                                     it accepts one key `path`,

        Returns:
            Dict[str, Any]: A dictionary containing details about the published metrics.

        SCHEMA:
            .. code-block:: json

                {
                  "name": "string",
                  "scope": "string",
                  "description": "string"
                }

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/metrics/collections"

        if not artifact:
            raise InvalidParameterException(
                message="Artifact must be provided to create the metrics collection.",
            )

        path = self.__get_artifact_details(artifact)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=body,
            path=path,
        )

    def delete_collection(self, collection_id: str) -> Dict[str, Any]:
        """Delete a metric collection.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/delete_api_v1_metrics_collections__collectionId_>`__

        Args:
            collection_id (str): The ID of the collection to delete.

        Returns:
            Dict[str, Any]: A dictionary containing details about the deleted collection.

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/metrics/collections/{collection_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    @overload
    def list_collections(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        id: Optional[List[str]] = None,  # noqa: A002
        scope: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_collections(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        id: Optional[List[str]] = None,  # noqa: A002
        scope: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_collections(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        id: Optional[List[str]] = None,  # noqa: A002
        scope: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the list of metric collections.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/get_api_v1_metrics_collections>`__

        Args:
            page_size (int | None): The number of images per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            id (List[str] | None): An array of collection IDs to retrieve. If not provided, all collections are retrieved.
            scope (List[str] | None): An array of scopes to filter the collections by. Available scopes are `PUBLIC` and `PRIVATE`. If not provided, all collections of the tenant along with all public collections are retrieved.
            return_iterator (bool): Whether to return an iterator object or list of metrics for a specified page number, defaults to True.

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
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/metrics/collections"
        params = {
            "pageSize": page_size,
            "id": id,
            "scope": scope,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="collections",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    @overload
    def list_namespaces(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_namespaces(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_namespaces(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the list of namespaces.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Namespaces/get_api_v1_namespaces>`__

        Args:
            page_size (int | None): The number of images per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of metrics for a specified page number, defaults to True.

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
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/namespaces"
        params = {
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="namespaces",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def update_namespace(
        self,
        namespace: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a namespace with a new description and metadata.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/semantic-layer/api-docs/index.htm#/Namespaces/patch_api_v1_namespaces__namespace_>`__

        Args:
            namespace (str): The name of the namespace to update.
            description (str | None): The new description for the namespace.
            metadata (Dict[str, Any] | None): The new metadata for the namespace.

        Returns:
            Dict[str, Any]: A dictionary containing details about the updated namespace.

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given namespace does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        if not namespace:
            raise InvalidParameterException(message="Namespace must be provided.")

        method, endpoint = HttpMethods.PATCH, f"{self.BASE_ENDPOINT}/namespaces/{namespace}"
        body = {}
        if description is not None:
            body["description"] = description
        if metadata is not None:
            body["metadata"] = json.dumps(metadata)

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )


def get_client(session: Optional[Session] = None) -> Metric:
    """Returns a Metrics client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Metric: The metric client object.
    """
    return Metric(session)


__all__: List[str] = ["get_client"]
