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

#
"""Peak Services service commands."""

import json
from typing import Any, Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.helpers import combine_dictionaries, map_user_options, parse_list_of_strings, variables_to_dict
from peak.output import Writer
from peak.resources.services import Service
from typing_extensions import Annotated

app = typer.Typer(
    help="Develop web services to deliver insights, suggestions and recommendations.",
    short_help="Create and Manage Services.",
)

_SERVICE_ID = typer.Argument(..., help="ID of the service to be used in this operation.")

_SERVICE_NAME = typer.Argument(..., help="Name of the service to be used in this operation.")

_LIST_STATUS = typer.Option(
    None,
    help="A list of service status to filter the list by. Valid values are `CREATING`, `DEPLOYING`, `AVAILABLE`, `DELETING`, `CREATE_FAILED`, `DELETE_FAILED`.",
)

_SERVICE_TYPE = typer.Option(
    None,
    help="A list of service types to filter the list by. Valid values are `api`, `web-app` and `shiny`.",
)

_LIST_NAME = typer.Option(None, help="Service name to search for.")

FILE_HELP_STRING = (
    "Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template."
)

NAME = typer.Option(None, help="Name of the service")

DESCRIPTION = typer.Option(None, help="Description of the service")

TITLE = typer.Option(None, help="Title of the service")

IMAGE_ID = typer.Option(None, help="ID of the image to be used in this operation.")

VERSION_ID = typer.Option(
    None,
    help="ID of the version to be used in this operation. If version-id is not passed, service will be created using latest ready version of the image.",
)

INSTANCE_TYPE_ID = typer.Option(None, help="The ID of the instance type to be used in this operation.")

SESSION_STICKINESS = typer.Option(
    None,
    help="Enable session stickiness for the service. Not required for API type services.",
)

SCALE_TO_ZERO = typer.Option(
    None,
    help="Enable scale to zero for the service. Only applicable for web-app type services.",
)

_ENVS = typer.Option(None, help="List of plain text environment variables in the format arg1=value1.")

_SECRETS = typer.Option(None, help="List of secret names to be passed as environment variables.")

_ENTRYPOINT = typer.Option(None, help="Entrypoint for the service.")

_HEALTH_CHECK_URL = typer.Option(None, help="Endpoint to monitor service's operational status.")

_MIN_INSTANCES = typer.Option(
    None,
    help="Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.",
)

_HTTP_METHOD = typer.Option(None, help="HTTP method to be used to test the service.")

_PATH = typer.Option(None, help="Path to be used to test the service.")

_PAYLOAD = typer.Option(None, help="Payload to be used to test the service. To be passed in stringified json format.")

MAPPING = {
    "imageId": "imageDetails",
    "versionId": "imageDetails",
    "instanceTypeId": "resources",
    "env": "parameters",
    "secrets": "parameters",  # pragma: allowlist secret
}


@app.command("list", short_help="List services.")
def list_services(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = _LIST_STATUS,
    name: Optional[str] = _LIST_NAME,
    service_type: Optional[List[str]] = _SERVICE_TYPE,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all services that exist for the tenant.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak services list --page-size 10 --page-number 1 --status CREATING --name test --service-type web-app
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "servicesCount": 1,
        "services": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/list-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = service_client.list_services(
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
            status=parse_list_of_strings(status),
            name=name,
            service_type=service_type,
        )
        writer.write(response)


@app.command(short_help="Create a new service.")
def create(
    ctx: typer.Context,
    file: Annotated[Optional[str], typer.Argument(..., help=FILE_HELP_STRING)] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    name: str = NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    image_id: int = IMAGE_ID,
    version_id: int = VERSION_ID,
    instance_type_id: int = INSTANCE_TYPE_ID,
    session_stickiness: bool = SESSION_STICKINESS,
    scale_to_zero: bool = SCALE_TO_ZERO,
    service_type: Optional[str] = _SERVICE_TYPE,
    env: Optional[List[str]] = _ENVS,
    secrets: Optional[List[str]] = _SECRETS,
    entrypoint: Optional[str] = _ENTRYPOINT,
    health_check_url: Optional[str] = _HEALTH_CHECK_URL,
    min_instances: Optional[int] = _MIN_INSTANCES,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new service and start its deployment.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (string): Name of the service.
        title (string | required: false): Title of the service.
        description (string | required: false): Description of the service.
        serviceType (string | required: false): Type of the service. Valid values are `api`, `web-app` and `shiny`. Default value is `web-app`.
        imageDetails (map):
            imageId (number): ID of the image.
            versionId (number | required: false): ID of the image version. If versionId is not passed, service will be created using latest ready version of the image.
        resources (map | required: false):
            instanceTypeId (number): ID of the instance type.
        parameters (map | required: false):
            env (map | required: false): Key-Value pair where key is the name of the env.
            secrets (list(str) | required: false): List of secret names to be passed.
        sessionStickiness (boolean | required: false): Enable session stickiness for the service. Default value is false. Enabling session stickiness will tie each user to a specific server for all their requests. Not required for API type services.
        scaleToZero (boolean | required: false): Enable scale to zero for the service. Only applicable for web-app type services. Default value is false. Enabling Scale to zero ensures that the resources hosting your app are scaled down when ideal over a period of time. The resources will scale back up automatically on next launch.
        entrypoint (string | required: false): Entrypoint for the service.
        healthCheckURL (string | required: false): Endpoint to monitor service's operational status.
        minInstances (number | required: false): Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak services create '/path/to/file.yml' -v '/path/to/params.yml'
    ```

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak services create --name <name> --title <title> --description <description> --service-type web-app --image-id <image-id> --version-id <version-id> --instance-type-id <instance-type-id> --scale-to-zero
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/create-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        name,
        description,
        title,
        image_id,
        version_id,
        instance_type_id,
        session_stickiness,
        scale_to_zero,
        service_type,
        env,
        secrets,
        entrypoint,
    )
    user_options = map_user_options(user_options, MAPPING)

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, service_client.create_service)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)

    if env:
        updated_body["parameters"]["env"] = helpers.parse_envs(env)

    if secrets:
        updated_body["parameters"]["secrets"] = parse_list_of_strings(secrets)

    if health_check_url:
        updated_body["healthCheckURL"] = health_check_url

    if min_instances:
        updated_body["minInstances"] = min_instances

    with writer.pager():
        response = service_client.create_service(body=updated_body)
        writer.write(response)


@app.command(short_help="Update an existing service.")
def update(
    ctx: typer.Context,
    service_id: str = _SERVICE_ID,
    file: Annotated[Optional[str], typer.Argument(..., help=FILE_HELP_STRING)] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    title: str = TITLE,
    description: str = DESCRIPTION,
    image_id: int = IMAGE_ID,
    version_id: int = VERSION_ID,
    instance_type_id: int = INSTANCE_TYPE_ID,
    session_stickiness: bool = SESSION_STICKINESS,
    scale_to_zero: bool = SCALE_TO_ZERO,
    env: Optional[List[str]] = _ENVS,
    secrets: Optional[List[str]] = _SECRETS,
    entrypoint: Optional[str] = _ENTRYPOINT,
    health_check_url: Optional[str] = _HEALTH_CHECK_URL,
    min_instances: Optional[int] = _MIN_INSTANCES,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** an existing service.

    \b
    When updating the service, it will trigger a redeployment only under specific conditions.
    Redeployment is triggered if you make changes to any of the following parameters: imageId, versionId, instanceTypeId, env, secrets, scaleToZero or sessionStickiness.
    However, only modifying the title or description will not trigger a redeployment.

    With the help of this operation, we can just update the required fields (except name and serviceType) and keep the rest of the fields as it is.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        title (string | required: false): Title of the service.
        description (string | required: false): Description of the service.
        imageDetails (map | required: false):
            imageId (number): ID of the image.
            versionId (number | required: false): ID of the image version. If versionId is not passed, service will be created using latest ready version of the image.
        resources (map | required: false):
            instanceTypeId (number): ID of the instance type.
        parameters (map | required: false):
            env (map | required: false): Key-Value pair where key is the name of the env.
            secrets (list(str) | required: false): List of secret names to be passed.
        sessionStickiness (boolean | required: false): Enable session stickiness for the service. Default value is false. Enabling session stickiness will tie each user to a specific server for all their requests. Not required for API type services.
        scaleToZero (boolean | required: false): Enable scale to zero for the service. Only applicable for web-app type services. Default value is false. Enabling Scale to zero ensures that the resources hosting your app are scaled down when ideal over a period of time. The resources will scale back up automatically on next launch.
        entrypoint (string | required: false): Entrypoint for the service.
        healthCheckURL (string | required: false): Endpoint to monitor service's operational status.
        minInstances (number | required: false): Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak services update <service-id> '/path/to/file.yml' -v '/path/to/params.yml'
    ```

     \b
    📝 ***Example usage without yaml:***
    ```bash
    peak services update <service-id> --title <title> --description <description> --image-id <image-id> --version-id <version-id> --instance-type-id <instance-type-id> --scale-to-zero
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "ab11c21d-1add-45dd-a72e-8c6b83b68dee"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/update-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        description,
        title,
        image_id,
        version_id,
        instance_type_id,
        session_stickiness,
        scale_to_zero,
        env,
        secrets,
        entrypoint,
    )
    user_options = map_user_options(user_options, MAPPING)

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, service_client.update_service)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)

    if env:
        updated_body["parameters"]["env"] = helpers.parse_envs(env)

    if secrets:
        updated_body["parameters"]["secrets"] = parse_list_of_strings(secrets)

    if health_check_url:
        updated_body["healthCheckURL"] = health_check_url

    if min_instances:
        updated_body["minInstances"] = min_instances

    with writer.pager():
        response = service_client.update_service(service_id=service_id, body=updated_body)
        writer.write(response)


@app.command(
    short_help="Create a new service or Update an existing service.",
)
def create_or_update(
    ctx: typer.Context,
    file: Annotated[Optional[str], typer.Argument(..., help=FILE_HELP_STRING)] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    name: str = NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    image_id: int = IMAGE_ID,
    version_id: int = VERSION_ID,
    instance_type_id: int = INSTANCE_TYPE_ID,
    session_stickiness: bool = SESSION_STICKINESS,
    scale_to_zero: bool = SCALE_TO_ZERO,
    service_type: Optional[str] = _SERVICE_TYPE,
    env: Optional[List[str]] = _ENVS,
    secrets: Optional[List[str]] = _SECRETS,
    entrypoint: Optional[str] = _ENTRYPOINT,
    health_check_url: Optional[str] = _HEALTH_CHECK_URL,
    min_instances: Optional[int] = _MIN_INSTANCES,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new service or ***Update*** an existing service based on service name and start its deployment.

    \b
    When updating the service, it will trigger a redeployment only under specific conditions.
    Redeployment is triggered if you make changes to any of the following parameters: imageId, versionId, instanceTypeId, env, secrets, scaleToZero or sessionStickiness.
    However, only modifying the title or description will not trigger a redeployment.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (string): Name of the service.
        title (string | required: false): Title of the service.
        description (string | required: false): Description of the service.
        serviceType (string | required: false): Type of the service. Valid values are `api`, `web-app` and `shiny`. Default value is `web-app`.
        imageDetails (map):
            imageId (number): ID of the image.
            versionId (number | required: false): ID of the image version. If versionId is not passed, service will be created using latest ready version of the image.
        resources (map | required: false):
            instanceTypeId (number): ID of the instance type.
        parameters (map | required: false):
            env (map | required: false): Key-Value pair where key is the name of the env.
            secrets (list(str) | required: false): List of secret names to be passed.
        sessionStickiness (boolean | required: false): Enable session stickiness for the service. Default value is false. Enabling session stickiness will tie each user to a specific server for all their requests. Not required for API type services.
        scaleToZero (boolean | required: false): Enable scale to zero for the service. Only applicable for web-app type services. Default value is false. Enabling Scale to zero ensures that the resources hosting your app are scaled down when ideal over a period of time. The resources will scale back up automatically on next launch.
        entrypoint (string | required: false): Entrypoint for the service.
        healthCheckURL (string | required: false): Endpoint to monitor service's operational status.
        minInstances (number | required: false): Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak services create-or-update '/path/to/file.yml' -v '/path/to/params.yml'
    ```

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak services create-or-update --name <name> --title <title> --description <description> --image-id <image-id> --version-id <version-id> --instance-type-id <instance-type-id> --scale-to-zero
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
    }
    ```

    🔗 [**API Documentation for creating a new service**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/create-service)

    🔗 [**API Documentation for updating an existing service**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/update-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        name,
        description,
        title,
        image_id,
        version_id,
        instance_type_id,
        session_stickiness,
        scale_to_zero,
        service_type,
        env,
        secrets,
        entrypoint,
    )
    user_options = map_user_options(user_options, MAPPING)

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, service_client.create_or_update_service)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)

    if env:
        updated_body["parameters"]["env"] = helpers.parse_envs(env)

    if secrets:
        updated_body["parameters"]["secrets"] = parse_list_of_strings(secrets)

    if health_check_url:
        updated_body["healthCheckURL"] = health_check_url

    if min_instances:
        updated_body["minInstances"] = min_instances

    response = service_client.create_or_update_service(body=updated_body)
    writer.write(response)


@app.command(short_help="Delete an existing service.")
def delete(
    ctx: typer.Context,
    service_id: str = _SERVICE_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** an existing service.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak services delete <service-id>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "ab11c21d-1add-45dd-a72e-8c6b83b68dee"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/delete-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = service_client.delete_service(service_id=service_id)
        writer.write(response)


@app.command(short_help="Describe details of a service.")
def describe(
    ctx: typer.Context,
    service_id: str = _SERVICE_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details for the specific service.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak services describe <service-id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": "ab11c21d-1add-45dd-a72e-8c6b83b68dee",
        "name": "awesome-service",
        "status": "AVAILABLE",
        "serviceType": "web-app",
        "imageDetails": {
            "imageId": 1,
            "versionId": 1
        },
        "resources": {
            "instanceTypeId": 1
        },
        "sessionStickiness": false,
        "scaleToZero": false,
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "someone@peak.ai",
        "updatedAt": "2020-01-01T18:00:00.000Z",
        "updatedBy": "someone@peak.ai",
        "entrypoint": "/",
        "healthCheckURL": "/health",
        "minInstances": 1,
        "tags": [...]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/get-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = service_client.describe_service(service_id=service_id)
        writer.write(response)


@app.command(short_help="Test API type service")
def test(
    ctx: typer.Context,
    service_name: str = _SERVICE_NAME,
    file: Annotated[Optional[str], typer.Argument(..., help=FILE_HELP_STRING)] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    http_method: str = _HTTP_METHOD,
    path: Optional[str] = _PATH,
    payload: Optional[str] = _PAYLOAD,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Test*** an API type service.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      payload (map): payload to be used to test the service.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak services test <service-name> '/path/to/file.yml' -v '/path/to/params.yml'
    ```

    \b
    📝 ***Example usage without yaml:***<br/>
    ```bash
    peak services test <service-name> --http-method 'get' --path '/'
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "responseBody": "{"status": "OK"}",
        "responseStatus": 200,
        "reqStartTime": "2024-01-01T10:00:01.064Z",
        "reqEndTime": "2024-01-01T10:00:05.064Z",
        "responseSize": "1KB"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/webapps/api-docs/index.htm#/Services/test-api-service)
    """
    service_client: Service = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, service_client.test_service)

    with writer.pager():
        response = service_client.test_service(
            service_name=service_name,
            http_method=http_method,
            path=path,
            payload=json.loads(payload) if payload else body.get("payload"),
        )
        writer.write(response)
