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

"""Peak Metric commands."""

import json
from typing import Any, Dict, List, Optional

import typer
from peak import config
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.helpers import combine_dictionaries, parse_list_of_strings, variables_to_dict
from peak.metrics.metrics import Metric
from peak.output import Writer
from typing_extensions import Annotated

app = typer.Typer(
    help="Metrics commands.",
    short_help="Manage Metrics.",
)

_ARTIFACT_PATH = typer.Option(None, help="Path to the artifact.")

_PUBLISH_NAMESPACE = _NAMESPACE = typer.Option(
    None,
    help="The namespace where you intend to publish the metrics. If not provided, the default namespace is used.",
)

_NAMESPACE = typer.Option(
    None,
    help="The namespace associated with the metrics. If not provided, the default namespace is used.",
)

_NAMESPACE_DESCRIPTION = typer.Option(
    None,
    help="A description of the namespace.",
)

_NAMESPACE_METADATA = typer.Option(
    None,
    help="Key-value metadata associated with the namespace. Provide them in stringified JSON format.",
)
_GENERATE_SQL = typer.Option(
    None,
    help="Indicates whether to return the SQL query instead of data. If `true`, the response will include the SQL query used to retrieve the metrics. Default is `false`.",
)
_MEASURES = typer.Option(
    None,
    help="An array of measures to include in the query. Measures represent quantitative metrics such as sums or counts. Provide them in stringified JSON format.",
)
_DIMENSIONS = typer.Option(
    None,
    help="An array of dimensions to include in the query. Dimensions represent qualitative categories such as time, location, or product names. Provide them in stringified JSON format.",
)
_FILTERS = typer.Option(
    None,
    help="An array of filter objects to apply to the query. Filters limit the data returned based on specific conditions. Provide them in stringified JSON format.",
)
_TIME_DIMENSIONS = typer.Option(
    None,
    help="An array of time dimensions to include in the query. Time dimensions allow querying over specific time ranges with optional granularity (e.g., day, month, year). Provide them in stringified JSON format.",
)
_SEARCH_TERM = typer.Option(
    None,
    help="A search term to filter the metrics. This can be used to search for specific metrics by name.",
)
_SEGMENTS = typer.Option(
    None,
    help="An array of segments to include in the query. Segments represent pre-defined filters that can be applied to metrics. Provide them in stringified JSON format.",
)
_ORDER = typer.Option(
    None,
    help="Defines the sort order of the results. This is an object where keys are the dimensions/measures and values are either 'asc' or 'desc' to specify ascending or descending order. Provide them in stringified JSON format.",
)
_LIMIT = typer.Option(
    None,
    help="Limits the number of rows returned by the query. If not provided, the default limit is applied.",
)
_OFFSET = typer.Option(
    None,
    help="Specifies the number of rows to skip before starting to return data. Useful for pagination.",
)

_METRIC_TYPES = typer.Option(
    None,
    help="The type of metric to create. If not provided, all metrics are retrieved. Available types are `cube`, `view`, `dimension`, `measure`, `segment` and `all`.",
)

_COLLECTION_NAME = typer.Option(
    None,
    help="Name of the metric collection.",
)
_PUBLICATION_ID = typer.Option(
    None,
    help="The publication ID associated with the metrics.",
)

_MEASURES_DELETE = typer.Option(
    None,
    help="An array of measures to delete.",
)

_COLLECTION_ID = typer.Option(
    None,
    help="The ID of the collection to publish the metrics.",
)

_COLLECTION_SCOPE = typer.Option(
    None,
    help="Scope of the metrics collection. Must be one of the following: PUBLIC, PRIVATE.",
)

_COLLECTION_DESCRIPTION = typer.Option(
    None,
    help="Description of the metric collection.",
)

_COLLECTION_IDS = typer.Option(
    None,
    help="An array of collection IDs to include in the query. If not provided, all collections are retrieved.",
)

_COLLECTION_SCOPES = typer.Option(
    None,
    help="An array of scopes to filter the collections by. Available scopes are `PUBLIC` and `PRIVATE`. If not provided, all collections of the tenant along with all public collections are retrieved.",
)


@app.command(short_help="Publish metrics.")
def publish(
    ctx: typer.Context,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    namespace: Optional[str] = _PUBLISH_NAMESPACE,
    namespace_description: Optional[str] = _NAMESPACE_DESCRIPTION,
    artifact_path: Optional[str] = _ARTIFACT_PATH,
    collection_id: Optional[str] = _COLLECTION_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Publish*** metrics.

    The metrics can be published either by passing artifact and namespace,
    or by passing collection_id and namespace. If both artifact and collection_id
    are provided, artifact takes priority. If the namespace is not provided, the 'default' namespace is used.
    Namespace metadata and Namespace description are optional.

    \b
    🧩 ***Input file schema(yaml):***<br/>

     **_Publish metrics using artifact and namespace_**
    ```yaml
      body (map):
        namespace (str): The namespace associated with the metrics.
        namespaceMetadata (map | required: false): Key-value metadata associated with the namespace.
        namespaceDescription (str | required: false): A description of the namespace.

      artifact (map):
        path (str): Path to the artifact.
    ```
     **_Publish metrics using collection id and namespace_**
    ```yaml
      body (map):
        namespace (str): The namespace associated with the metrics.
        namespaceMetadata (map | required: false): Key-value metadata associated with the namespace.
        namespaceDescription (str | required: false): A description of the namespace.

      collectionId (str): The ID of the collection to publish the metrics.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak metrics publish '/path/to/metrics.yaml' --params-file '/path/to/values.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    # Publish metrics using artifact and namespace
    peak metrics publish --artifact-path <path> --namespace <namespace> --namespace-description "Metrics for pricing"

    # Publish metrics using collection id and namespace
    peak metrics publish --collection-id <collection-id> --namespace <namespace> --namespace-description "Metrics for pricing"
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "artifactId": "7dc0feaa-be90-467b-9c3a-009a234e4b2b",
        "collectionId": "bc8b6ef5-d2f6-4b7f-9365-0261b43997c9",
        "publicationId": "79af8462-2820-483c-a8b6-d697555a8fc2",
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/post_api_v1_metrics)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        namespace,
        namespace_description,
    )

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, metrics_client.publish)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)
    artifact = helpers.get_updated_artifacts(body, artifact_path, None)

    with writer.pager():
        response: Dict[str, Any] = metrics_client.publish(
            body=updated_body,
            artifact=artifact,  # type: ignore  # noqa: PGH003
            collection_id=collection_id,
        )
        writer.write(response)


@app.command(short_help="Query metrics.")
def query(
    ctx: typer.Context,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    namespace: Optional[str] = _NAMESPACE,
    generate_sql: Optional[bool] = _GENERATE_SQL,
    measures: Optional[List[str]] = _MEASURES,
    dimensions: Optional[List[str]] = _DIMENSIONS,
    filters: Optional[List[str]] = _FILTERS,
    time_dimensions: Optional[List[str]] = _TIME_DIMENSIONS,
    segments: Optional[List[str]] = _SEGMENTS,
    order: Optional[str] = _ORDER,
    limit: Optional[int] = _LIMIT,
    offset: Optional[int] = _OFFSET,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Query*** a published metric in the semantic layer using the provided parameters.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
        namespace (str | required: false): The namespace associated with the metrics. If not provided, the default namespace is used.
        generateSql (bool | required: false): Indicates whether to return the SQL query instead of data. If `true`, the response will include the SQL query used to retrieve the metrics. Default is `false`.
        measures (list(str) | required: false): An array of measures to include in the query. Measures represent quantitative metrics such as sums or counts.
        dimensions (list(str) | required: false): An array of dimensions to include in the query. Dimensions represent qualitative categories such as time, location, or product names.
        filters (list(map) | required: false):
            dimension (str): The dimension to filter on. Supported values are `equals`, `notEquals`, `contains`, `notContains`, `startsWith`, `notStartsWith`, `endsWith`, `notEndsWith`, `gt`, `gte`, `lt`, `lte`, `inDateRange`, `notInDateRange`, `beforeDate`, `beforeOrOnDate`, `afterDate`, `afterOrOnDate` etc.
            operator (str): The operator to use for the filter.
            values (list(str)): An array of values to filter on.
        timeDimensions (list(map) | required: false):
            dimension (str): The time dimension to include in the query.
            granularity (str | required: false): The granularity of the time dimension. Supported values are `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, and `year`.
            dateRange (list(str) | str | required: false): An array of two dates that define the time range for the query. Alternatively, you can provide a single string out of the following predefined date ranges `today`, `yesterday`, `this week`, `last week`, `this month`, `last month`, `this quarter`, `last quarter`, `this year`, `last year`, `last 7 days` and `last 30 days`.
        segments (list(str) | required: false): An array of segments to include in the query. Segments represent pre-defined filters that can be applied to metrics.
        order (map | required: false): Defines the sort order of the results. This is a stringified object where keys are the dimensions/measures and values are either 'asc' or 'desc' to specify ascending or descending order.
        limit (int | required: false): Limits the number of rows returned by the query. If not provided, the default limit is applied.
        offset (int | required: false): Specifies the number of rows to skip before starting to return data. Useful for pagination.
    ```

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak metrics query '/path/to/query.yaml' --params-file '/path/to/values.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***<br/>
    ```bash
    peak metrics query --measures "<cube_name>.<resource_name_1>" --measures "<cube_name>.<resource_name_2>" --dimensions "<cube_name>.<resource_name>" --time-dimensions "{\"dimension\":\"<cube_name>.<resource_name>\",\"dateRange\":[\"2024-01-26T00:00:00Z\",\"2024-06-06T00:00:00Z\"],\"granularity\":\"day\"}"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "data": [
            {
                "region": "North America",
                "total_sales": 1000000
            },
            {
                "region": "Europe",
                "total_sales": 500000
            }
        ],
        "sql": "SELECT region, SUM(total_sales) AS total_sales FROM orders GROUP BY region"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Query/get_api_v1_metrics_query)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    request_params: Dict[str, Any] = {}

    if file:
        request_params = helpers.template_handler(file, params_file, params)
        request_params = helpers.remove_unknown_args(request_params, metrics_client.query)

    cli_params = {
        "namespace": namespace,
        "generate_sql": generate_sql,
        "measures": parse_list_of_strings(measures) if measures else [],
        "dimensions": parse_list_of_strings(dimensions) if dimensions else [],
        "filters": [json.loads(query_filter) for query_filter in filters] if filters else [],
        "time_dimensions": (
            [json.loads(time_dimension) for time_dimension in time_dimensions] if time_dimensions else []
        ),
        "segments": parse_list_of_strings(segments) if segments else [],
        "order": json.loads(order) if order else {},
        "limit": limit,
        "offset": offset,
    }

    merged_params = {**request_params}
    for key, value in cli_params.items():
        if (value not in [None, [], {}] and key in merged_params) or key not in merged_params:
            merged_params[key] = value

    with writer.pager():
        response = metrics_client.query(**merged_params)
        cli_output_type = config.OUTPUT_TYPE

        if "data" in response:
            total_count = len(response["data"])
            response["totalCount"] = total_count

        if "generate_sql" in merged_params and merged_params["generate_sql"] is True and cli_output_type == "table":
            response["data"] = []

        writer.write(response)


@app.command("list", short_help="List metrics.")
def list_metrics(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    publication_id: Optional[str] = _PUBLICATION_ID,
    namespace: Optional[str] = _NAMESPACE,
    search_term: Optional[str] = _SEARCH_TERM,
    type: Optional[str] = _METRIC_TYPES,  # noqa: A002
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** metrics in the semantic layer.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak metrics list --page-size 25 --page-number 1 --namespace <namespace> --type <type> --search-term <search_term> --publication-id <publication_id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "data": [
            {
                "name": "product",
                "type": "cube",
                "public": true,
                "measures": [
                    {
                        "name": "product.max_price",
                        "type": "number",
                        "aggType": "max",
                        "public": true
                    },
                    {
                        "name": "product.max_discount",
                        "type": "number",
                        "aggType": "max",
                        "public": true
                    },
                ],
                "dimensions": [
                    {
                        "name": "product.sale",
                        "type": "string",
                        "public": true,
                        "primaryKey": true
                    },
                    {
                        "name": "order.created_at",
                        "type": "time",
                        "public": true,
                        "primaryKey": false
                    },
                ],
                "segments": [],
                "collectionId": "b8d8308e-4f45-42e5-9c08-d4c4ba6db7f6",
                "publicationId": "299e7d07-db2f-4050-88c3-40afd7603807"
            }
        ],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25,
        "totalCount": 2
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/get_api_v1_metrics)
    """
    metric_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = metric_client.list(
            page_size=page_size,
            page_number=page_number,
            publication_id=publication_id,
            namespace=namespace,
            search_term=search_term,
            type=type,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Create metrics collection.")
def create_collection(
    ctx: typer.Context,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    name: str = _COLLECTION_NAME,
    scope: str = _COLLECTION_SCOPE,
    description: Optional[str] = _COLLECTION_DESCRIPTION,
    artifact_path: str = _ARTIFACT_PATH,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** metrics collection.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (str): Name of the metric collection.
        scope (str): Scope of the metrics artifact.
        description (str | required: false): Description of the metric collection.
      artifact (map):
        path (str): Path to the artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak metrics create-collection '/path/to/metrics.yaml' --params-file '/path/to/values.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak metrics create-collection --artifact-path <path> --name <name> --scope <scope> --description <description>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "artifactId": "7dc0feaa-be90-467b-9c3a-009a234e4b2b",
        "collectionId": "bc8b6ef5-d2f6-4b7f-9365-0261b43997c9",
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/post_api_v1_metrics_collections)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        name,
        scope,
        description,
    )

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, metrics_client.create_collection)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)
    artifact = helpers.get_updated_artifacts(body, artifact_path, None)

    with writer.pager():
        response: Dict[str, Any] = metrics_client.create_collection(body=updated_body, artifact=artifact)  # type: ignore  # noqa: PGH003
        writer.write(response)


@app.command(short_help="Delete the metrics.")
def delete(
    ctx: typer.Context,
    namespace: Optional[str] = _NAMESPACE,
    measures: Optional[List[str]] = _MEASURES_DELETE,
    publication_id: Optional[str] = _PUBLICATION_ID,
    *,
    dry_run: bool = DRY_RUN,  # noqa: ARG001
    output_type: OutputTypesNoTable = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** one or more measures.

    Measures can either be deleted by passing a namespace and a list of measures or
    by giving a publication id which would delete all the measures associated with that publication. If both are passed,
    publication id takes priority.

    \b
    📝 ***Example usage:***
    ```bash
    # Delete using namespace and measure names
    peak metrics delete --namespace <namespace> --measures <measure> --measures <measure>
    # Delete using publication id
    peak metrics delete --publication-id
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Metrics/delete_api_v1_metrics_publications__publicationId_)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = {
        "namespace": namespace,
        "measures": parse_list_of_strings(measures) if measures else [],
        "publication_id": publication_id,
    }

    with writer.pager():
        response: Dict[str, Any] = metrics_client.delete(**body)
        writer.write(response)


@app.command(short_help="Delete metrics collection.")
def delete_collection(
    ctx: typer.Context,
    collection_id: str = typer.Argument(..., help="ID of the metric collection."),
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** metrics collection.

    \b
    📝 ***Example usage:***
    ```bash
    peak metrics delete-collection <collection_id>
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/delete_api_v1_metrics_collections__collectionId_)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response: Dict[str, Any] = metrics_client.delete_collection(collection_id=collection_id)
        writer.write(response)


@app.command(short_help="List metrics collections.")
def list_collections(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    id: Optional[List[str]] = _COLLECTION_IDS,  # noqa: A002
    scope: Optional[List[str]] = _COLLECTION_SCOPES,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** metrics collections.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak metrics list-collections --page-size 25 --page-number 1 --id <collection_id_1> --id <collection_id_2> --scope <scope>
    ```

    \b
    🆗 ***Response:***<br/>
    ```json
    {
        "collections": [
            {
                "id": "b8d8308e-4f45-42e5-9c08-d4c4ba6db7f6",
                "name": "product",
                "tenant": "tenant-name",
                "scope": "PUBLIC",
                "description": "Product metrics",
                "artifactId": "7dc0feaa-be90-467b-9c3a-009a234e4b2b",
                "createdAt": "2024-01-26T00:00:00Z",
                "createdBy": "someone@peak.ai",
                "updatedAt": "2024-01-26T00:00:00Z",
                "updatedBy": "someone@peak.ai"
            }
        ],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25,
        "totalCount": 1
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Collections/get_api_v1_metrics_collections)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = metrics_client.list_collections(
            page_size=page_size,
            page_number=page_number,
            id=parse_list_of_strings(id) if id else [],
            scope=parse_list_of_strings(scope) if scope else [],
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="List namespaces.")
def list_namespaces(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** namespaces.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak metrics list-namespaces --page-size 25 --page-number 1
    ```

    \b
    🆗 ***Response:***<br/>
    ```json
    {
        "namespaces": [
            {
                "description": "Default namespace",
                "metadata": {
                    "owner": "abc",
                    "environment": "development"
                },
                "name": "default",
                "models": [
                    {
                        "name": "stocks",
                        "publicationId": "5503a4df-fa33-4932-9f60-9e3930f37f65",
                        "type": "cube"
                    }
                ]
            }
        ],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25,
        "totalCount": 1
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/semantic-layer/api-docs/index.htm#/Namespaces/get_api_v1_namespaces)
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = metrics_client.list_namespaces(
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Update a namespace.")
def update_namespace(
    ctx: typer.Context,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    namespace: Optional[str] = typer.Option(None, help="The name of the namespace to update."),
    description: Optional[str] = _NAMESPACE_DESCRIPTION,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Update*** a namespace with a new description and metadata.

    \b
    📝 ***Example usage:***
    ```bash
    peak metrics update-namespace update-namespace.yaml --namespace new_namespace --description "Updated description"
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "namespace": "new_namespace",
        "description": "Updated description",
        "message": "Updated namespace new_namespace",
        "metadata": {
            "key": "value"
        }
    }
    ```
    """
    metrics_client: Metric = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)

    cli_options: Dict[str, Any] = variables_to_dict(
        namespace,
        description,
    )

    updated_body = combine_dictionaries(body or {}, cli_options)

    if not updated_body.get("namespace") and not namespace:
        error_message = "Namespace must be provided either through file or CLI option."
        raise typer.BadParameter(error_message)

    final_namespace = updated_body.pop("namespace", namespace)
    metadata = updated_body.get("metadata")

    with writer.pager():
        response = metrics_client.update_namespace(
            namespace=final_namespace,
            description=updated_body.get("description"),
            metadata=metadata,
        )
        writer.write(response)
