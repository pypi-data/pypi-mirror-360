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
"""Peak Images service commands."""
from typing import Any, Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable, OutputTypesOnlyJson
from peak.helpers import combine_dictionaries, map_user_options, parse_list_of_strings, variables_to_dict
from peak.output import Writer
from peak.resources.images import Image
from typing_extensions import Annotated

app = typer.Typer(
    help="Create Docker images that Workflows, Workspaces, and other services use.",
    short_help="Create and manage Images.",
)

_IMAGE_ID = typer.Argument(..., help="ID of the image to be used in this operation.")

_BUILD_ID = typer.Option(..., help="ID of the image build to be used in this operation.")

_COUNT = typer.Option(None, help="Number of builds required.")

_BUILD_STATUS = typer.Option(
    None,
    help="List of build status to filter image builds. Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.",
)

_VERSIONS = typer.Option(None, help="List of version ids to filter image builds.")

_IMAGE_LIST_NAME = typer.Option(None, help="Image Name or version to search for.")

_IMAGE_LIST_STATUS = typer.Option(
    None,
    help="List of status of the latest version to filter the images by. Valid values are `not-ready`, `ready`, `in-use`, `deleting`, `delete-failed`.",
)

_IMAGE_LIST_SCOPE = typer.Option(
    None,
    help="List of type of image to filter the images by. Valid values are `custom` and `global`.",
)

_IMAGE_LIST_BUILD_STATUS = typer.Option(
    None,
    help="List of build status of the latest version to filter the images by. Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.",
)

_IMAGE_LIST_TAGS = typer.Option(None, help="List of tags on the latest version to filter the images by.")

_VERSION_LIST_VERSION = typer.Option(None, help="Version to search for.")

_VERSION_LIST_STATUS = typer.Option(
    None,
    help="List of statuses to filter the versions by. Valid values are `not-ready`, `ready`, `in-use`, `deleting`, `delete-failed`.",
)

_VERSION_LIST_BUILD_STATUS = typer.Option(
    None,
    help="List of build statuses to filter the versions by. Valid values are `building`, `failed`, `success`, `stopped`, `stopping`.",
)

_VERSION_LIST_TAGS = typer.Option(None, help="List of tags to filter the versions by.")

_NAME = typer.Option(None, help="Name of the image.")

_VERSION = typer.Option(None, help="A valid semantic image version.")

_TYPE = typer.Option(
    None,
    help="Type of the image. Allowed values are 'workflow', 'workspace-r', 'workspace-python, 'api', 'webapp'.",
)

_DESCRIPTION = typer.Option(None, help="Description of the image.")

_ARTIFACT_PATH = typer.Option(None, help="Path to the artifact.")

_ARTIFACT_IGNORE_FILES = typer.Option(None, help="Ignore files to use when creating artifact.")

_BUILD_DETAILS = typer.Option(None, help="Build details of the image. To be passed in stringified json format.")

_SOURCE = typer.Option(
    None,
    help="The source via which the image is to be created. Allowed values are 'github', 'dockerfile' and 'upload'.",
)

_DOCKERFILE = typer.Option(None, help="The dockerfile to be used to create the image.")

_DOCKERFILE_PATH = typer.Option(None, help="Path to the dockerfile.")

_CONTEXT = typer.Option(None, help="The path within the artifact to the code to be executed by the Dockerfile.")

_REPOSITORY = typer.Option(None, help="When source is github, the repository where the Dockerfile content is stored.")

_BRANCH = typer.Option(None, help="When source is github, the Branch that contains the Dockerfile.")

_TOKEN = typer.Option(None, help="When source is github, the token to be used to clone the required repository.")

_USE_CACHE = typer.Option(None, help="Whether to enable image caching to reduce build time.")

_BUILD_ARGUMENTS = typer.Option(None, help="List of build arguments in the format arg1=value1.")

_SECRETS = typer.Option(None, help="List of secret names to be passed as build arguments.")

_VERSIONS_TO_DELETE = typer.Option(..., help="List of version ids to delete.")

MAPPING = {
    "source": "buildDetails",
    "dockerfile": "buildDetails",
    "dockerfilePath": "buildDetails",
    "context": "buildDetails",
    "repository": "buildDetails",
    "branch": "buildDetails",
    "token": "buildDetails",
    "useCache": "buildDetails",
    "buildArguments": "buildDetails",
    "secrets": "buildDetails",  # pragma: allowlist secret
}


@app.command(short_help="Create a new image.")
def create(
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
    name: Optional[str] = _NAME,
    version: Optional[str] = _VERSION,
    type: Optional[str] = _TYPE,  # noqa: A002
    description: Optional[str] = _DESCRIPTION,
    artifact_path: Optional[str] = _ARTIFACT_PATH,
    artifact_ignore_files: Optional[List[str]] = _ARTIFACT_IGNORE_FILES,
    build_details: Optional[str] = _BUILD_DETAILS,
    source: Optional[str] = _SOURCE,
    dockerfile: Optional[str] = _DOCKERFILE,
    dockerfile_path: Optional[str] = _DOCKERFILE_PATH,
    context: Optional[str] = _CONTEXT,
    repository: Optional[str] = _REPOSITORY,
    branch: Optional[str] = _BRANCH,
    token: Optional[str] = _TOKEN,
    use_cache: Optional[bool] = _USE_CACHE,
    build_arguments: Optional[List[str]] = _BUILD_ARGUMENTS,
    secrets: Optional[List[str]] = _SECRETS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new image. This also adds the first version in the image.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (str): Name of the image.
        version (str | required: false): A valid semantic image version. If not provided, the version will be set to 0.0.1.
        type (str): Type of the image. Allowed values are 'workflow', 'workspace-r', 'workspace-python, 'api' and 'webapp'.
        description (str | required: false): Description of the image.
        buildDetails (map | required: false):
          source (str | required: false): The source via which the image is to be created. Allowed values are 'github', 'dockerfile' and 'upload'. It is 'upload' by default.
          useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
          buildArguments (list(map) | required: false):
            name (str): Name of the build argument.
            value (str): Value of the build argument.
          secrets (list(str)) | required: false): List of secret names to be passed as build arguments.
          context (str | required: false): The path within the artifact to the code to be executed by the Dockerfile.
          dockerfilePath (str | required: false): Path to the Dockerfile inside artifact or the repository.
          repository (str | required: false): When source is github, the repository where the Dockerfile content is stored.
          branch (str | required: false): When source is github, the Branch that contains the Dockerfile.
          token (str | required: false): When source is github, the token to be used to clone the required repository.
          dockerfile (str | required: false): When source is dockerfile, this represents the content of Dockerfile to build the image from.
      artifact (map | required: false):
        path (str): Path to the artifact.
        ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak images create '/path/to/image.yaml' --params-file '/path/to/values.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak images create --name <name> --type <type> --description <description> --version <version> --source <source> --dockerfile <dockerfile> --secrets <secret_1> --secrets <secret_2>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "buildId": "build-image-mock:2198c71e-22c5-aca3eac3a55e",
        "imageId": 9999,
        "versionId": 1,
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/images/post_api_v2_images)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        name,
        description,
        type,
        version,
        build_details,
        source,
        dockerfile,
        repository,
        branch,
        token,
        dockerfile_path,
        context,
        use_cache,
        build_arguments,
        secrets,
    )

    user_options = map_user_options(user_options, MAPPING, dict_type_keys=["buildDetails"])

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, image_client.create_image)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)
    artifact = helpers.get_updated_artifacts(body, artifact_path, artifact_ignore_files)

    if build_arguments:
        updated_body["buildDetails"]["buildArguments"] = helpers.parse_build_arguments(build_arguments)

    if secrets:
        updated_body["buildDetails"]["secrets"] = parse_list_of_strings(secrets)

    with writer.pager():
        response: Dict[str, Any] = image_client.create_image(body=updated_body, artifact=artifact)  # type: ignore  # noqa: PGH003
        writer.write(response)


@app.command(short_help="Create a new image version.")
def create_version(
    ctx: typer.Context,
    image_id: int = _IMAGE_ID,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    version: Optional[str] = _VERSION,
    description: Optional[str] = _DESCRIPTION,
    artifact_path: Optional[str] = _ARTIFACT_PATH,
    artifact_ignore_files: Optional[List[str]] = _ARTIFACT_IGNORE_FILES,
    build_details: Optional[str] = _BUILD_DETAILS,
    source: Optional[str] = _SOURCE,
    dockerfile: Optional[str] = _DOCKERFILE,
    dockerfile_path: Optional[str] = _DOCKERFILE_PATH,
    context: Optional[str] = _CONTEXT,
    repository: Optional[str] = _REPOSITORY,
    branch: Optional[str] = _BRANCH,
    token: Optional[str] = _TOKEN,
    use_cache: Optional[bool] = _USE_CACHE,
    build_arguments: Optional[List[str]] = _BUILD_ARGUMENTS,
    secrets: Optional[List[str]] = _SECRETS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new version in an existing image.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        version (str | required: false): A valid semantic image version. If not provided, the next patch version of the latest version will be used.
        description (str | required: false): Description of the image version.
        buildDetails (map | required: false):
          source (str | required: false): The source via which the image version is to be created. Allowed values are 'github', 'dockerfile' and 'upload'. It is 'upload' by default.
          useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
          buildArguments (list(map) | required: false):
            name (str): Name of the build argument.
            value (str): Value of the build argument.
          secrets (list(str) | required: false): List of secret names to be passed as build arguments.
          context (str | required: false): The path within the artifact to code to be executed by the Dockerfile.
          dockerfilePath (str | required: false): Path to the Dockerfile inside artifact or repository.
          repository (str | required: false): When source is github, the repository where the Dockerfile content is stored.
          branch (str | required: false): When source is github, the Branch that contains the Dockerfile.
          token (str | required: false): When source is github, the token to be used to clone the required repository.
          dockerfile (str | required: false): When source is dockerfile, this represents the content of Dockerfile to build the image from.
        autodeployResources (list(map) | required: false): A list of resources that should be redeployed when the build completes.
            entityId (str): The id of the resource to be redeployed.
            entityType (str): The type of the resource to be redeployed. Allowed values are 'workflow', 'workspace', 'api' and 'webapp'.
      artifact (map | required: false):
        path (str): Path to the artifact.
        ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak images create-version <imageId> '/path/to/file.yaml' -v '/path/to/parmas.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak images create-version <image_id> --description <description> --version <version> --source <source> --dockerfile <dockerfile> --secrets <secret_1>,<secret_2>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "buildId": "build-image-mock:2198c71e-22c5-aca3eac3a55e",
        "versionId": 101,
        "autodeploymentId": "0a12abcd-11ab-22d2-123a-a1234b333abc"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/post_api_v2_images__imageId__versions)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        description,
        version,
        build_details,
        source,
        dockerfile,
        repository,
        branch,
        token,
        dockerfile_path,
        context,
        use_cache,
        build_arguments,
        secrets,
    )

    user_options = map_user_options(user_options, MAPPING, dict_type_keys=["buildDetails"])

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, image_client.create_version)

    updated_body = combine_dictionaries(
        body.get("body") or {},
        user_options,
    )
    artifact = helpers.get_updated_artifacts(body, artifact_path, artifact_ignore_files)

    if build_arguments:
        updated_body["buildDetails"]["buildArguments"] = helpers.parse_build_arguments(build_arguments)

    if secrets:
        updated_body["buildDetails"]["secrets"] = parse_list_of_strings(secrets)

    with writer.pager():
        response: Dict[str, Any] = image_client.create_version(image_id=image_id, body=updated_body, artifact=artifact)  # type: ignore  # noqa: PGH003
        writer.write(response)


@app.command(
    short_help="Create a new image/version or Update and existing version.",
)
def create_or_update(
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
    name: Optional[str] = _NAME,
    version: Optional[str] = _VERSION,
    type: Optional[str] = _TYPE,  # noqa: A002
    description: Optional[str] = _DESCRIPTION,
    artifact_path: Optional[str] = _ARTIFACT_PATH,
    artifact_ignore_files: Optional[List[str]] = _ARTIFACT_IGNORE_FILES,
    build_details: Optional[str] = _BUILD_DETAILS,
    source: Optional[str] = _SOURCE,
    dockerfile: Optional[str] = _DOCKERFILE,
    dockerfile_path: Optional[str] = _DOCKERFILE_PATH,
    context: Optional[str] = _CONTEXT,
    repository: Optional[str] = _REPOSITORY,
    branch: Optional[str] = _BRANCH,
    token: Optional[str] = _TOKEN,
    use_cache: Optional[bool] = _USE_CACHE,
    build_arguments: Optional[List[str]] = _BUILD_ARGUMENTS,
    secrets: Optional[List[str]] = _SECRETS,
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new image if it doesn't exist. This also adds the first version in the image. In case image exists, it will add a new version to the image. ***Update*** a version if exists.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (str): Name of the image.
        version (str | required: false): A valid semantic image version. If not provided, the next patch version of the latest version will be used.
        type (str): Type of the image. Allowed values are 'workflow', 'workspace-r', 'workspace-python, 'api' and 'webapp'.
        description (str | required: false): Description of the image.
        buildDetails (map | required: false): If not provided and if the image version already exists, the build details of the existing version will be used.
          source (str | required: false): The source via which the image is to be created. Allowed values are 'github', 'dockerfile' and 'upload'. It is 'upload' by default if new version is being created otherwise the existing version's source will be used.
          useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
          buildArguments (list(map) | required: false):
            name (str): Name of the build argument.
            value (str): Value of the build argument.
          secrets (list(str)) | required: false): List of secret names to be passed as build arguments.
          context (str | required: false): The path within the artifact to the code to be executed by the Dockerfile.
          dockerfilePath (str | required: false): Path to the Dockerfile inside artifact or the repository.
          repository (str | required: false): When source is github, the repository where the Dockerfile content is stored.
          branch (str | required: false): When source is github, the Branch that contains the Dockerfile.
          token (str | required: false): When source is github, the token to be used to clone the required repository.
          dockerfile (str | required: false): When source is dockerfile, this represents the content of Dockerfile to build the image from.
      artifact (map | required: false):
        path (str): Path to the artifact.
        ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak images create-or-update '/path/to/image.yaml' --params-file '/path/to/values.yaml'
    ```

    \b
    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak images create-or-update --name <name> --type <type> --description <description> --version <version> --source <source> --dockerfile <dockerfile> --secrets <secret_1> --secrets <secret_2>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "buildId": "build-image-mock:2198c71e-22c5-aca3eac3a55e",
        "imageId": 9999,
        "versionId": 1,
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/images/post_api_v2_images)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        name,
        description,
        type,
        version,
        build_details,
        source,
        dockerfile,
        repository,
        branch,
        token,
        dockerfile_path,
        context,
        use_cache,
        build_arguments,
        secrets,
    )

    user_options = map_user_options(user_options, MAPPING, dict_type_keys=["buildDetails"])

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, image_client.create_or_update_image_version)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)
    artifact = helpers.get_updated_artifacts(body, artifact_path, artifact_ignore_files)

    if build_arguments:
        updated_body["buildDetails"]["buildArguments"] = helpers.parse_build_arguments(build_arguments)

    if secrets:
        updated_body["buildDetails"]["secrets"] = parse_list_of_strings(secrets)

    with writer.pager():
        response: Dict[str, Any] = image_client.create_or_update_image_version(body=updated_body, artifact=artifact)  # type: ignore  # noqa: PGH003
        writer.write(response)


@app.command("list", short_help="List images.")
def list_images(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    name: Optional[str] = _IMAGE_LIST_NAME,
    status: Optional[List[str]] = _IMAGE_LIST_STATUS,
    scope: Optional[List[str]] = _IMAGE_LIST_SCOPE,
    last_build_status: Optional[List[str]] = _IMAGE_LIST_BUILD_STATUS,
    tags: Optional[List[str]] = _IMAGE_LIST_TAGS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all images that exists in the tenant along with details about their latest version.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images list --page-size 10 --page-number 1 --name "test" --status "ready,in-use" --scope "custom" --last-build-status "building" --tags "tag1"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "imageCount": 1,
        "images": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/images/get_api_v2_images)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = image_client.list_images(
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
            name=name,
            status=parse_list_of_strings(status),
            scope=parse_list_of_strings(scope),
            last_build_status=parse_list_of_strings(last_build_status),
            tags=parse_list_of_strings(tags),
        )

        writer.write(response)


@app.command("list-versions", short_help="List image versions.")
def list_image_versions(
    ctx: typer.Context,
    image_id: int = _IMAGE_ID,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    version: Optional[str] = _VERSION_LIST_VERSION,
    status: Optional[List[str]] = _VERSION_LIST_STATUS,
    last_build_status: Optional[List[str]] = _VERSION_LIST_BUILD_STATUS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    tags: Optional[List[str]] = _VERSION_LIST_TAGS,
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all versions for an image.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images list-versions 9999 --page-size 10 --page-number 1 --version "0.0.1" --status "ready,in-use" --last-build-status "failed"  --tags "tag1,tag2"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "versionCount": 1,
        "versions": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/get_api_v2_images__imageId__versions)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response: Dict[str, Any] = image_client.list_image_versions(
            image_id=image_id,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
            version=version,
            status=parse_list_of_strings(status),
            last_build_status=parse_list_of_strings(last_build_status),
            tags=parse_list_of_strings(tags),
        )

        writer.write(response)


@app.command(short_help="Describe details of a specific image.")
def describe(
    ctx: typer.Context,
    image_id: int = _IMAGE_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details of a specific image and its latest version.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images describe 9999
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": 1,
        "name": "awesome-image",
        "type": "workflow",
        "scope": "custom",
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "someone@peak.ai",
        "latestVersion": {...}
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/images/get_api_v2_images__imageId_)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = image_client.describe_image(image_id=image_id)
        writer.write(response)


@app.command(short_help="Describe details of a specific version.")
def describe_version(
    ctx: typer.Context,
    image_id: int = args.IMAGE_ID,
    version_id: int = args.VERSION_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details of a specific version.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images describe-version --image-id 9999 --version-id 101
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "imageName": "awesome-image",
        "imageType": "Workflow",
        "id": 101,
        "version": "0.0.1-python3.9",
        "description": "This is an awesome image",
        "status": "not-ready",
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "someone@peak.ai",
        "updatedAt": "2020-01-01T18:00:00.000Z",
        "updatedBy": "someone@peak.ai",
        "pullUrl": "<image-url>",
        "lastBuildStatus": "building",
        "lastBuildAt": "2020-01-01T18:00:00.000Z",
        "buildDetails": {...},
        "tags": [...]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/get_api_v2_images__imageId__versions__versionId_)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response: Dict[str, Any] = image_client.describe_version(image_id=image_id, version_id=version_id)
        writer.write(response)


@app.command(short_help="Update an image version.")
def update_version(
    ctx: typer.Context,
    image_id: int = args.IMAGE_ID,
    version_id: int = args.VERSION_ID,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    description: Optional[str] = _DESCRIPTION,
    artifact_path: Optional[str] = _ARTIFACT_PATH,
    artifact_ignore_files: Optional[List[str]] = _ARTIFACT_IGNORE_FILES,
    build_details: Optional[str] = _BUILD_DETAILS,
    source: Optional[str] = _SOURCE,
    dockerfile: Optional[str] = _DOCKERFILE,
    dockerfile_path: Optional[str] = _DOCKERFILE_PATH,
    context: Optional[str] = _CONTEXT,
    repository: Optional[str] = _REPOSITORY,
    branch: Optional[str] = _BRANCH,
    token: Optional[str] = _TOKEN,
    use_cache: Optional[bool] = _USE_CACHE,
    build_arguments: Optional[List[str]] = _BUILD_ARGUMENTS,
    secrets: Optional[List[str]] = _SECRETS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** an image version. Only the versions that are in `not-ready` state can be updated and you can not update their version while updating them.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
    body (map):
      description (str | required: false): Description of the image version.
      buildDetails (map | required: false): If not provided, the existing build details will be used.
        source (str | required: false): The source via which the image version is to be created. Allowed values are 'github', 'dockerfile' and 'upload'. Source of existing version will be used if not provided.
        useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
        buildArguments (list(map) | required: false):
          name (str): Name of the build argument.
          value (str): Value of the build argument.
        secrets (list(str) | required: false): List of secret names to be passed as build arguments.
        context (str | required: false): The path within the artifact to code to be executed by the Dockerfile.
        dockerfilePath (str | required: false): Path to the Dockerfile inside artifact or repository.
        repository (str | required: false): When source is github, the repository where the Dockerfile content is stored.
        branch (str | required: false): When source is github, the Branch that contains the Dockerfile.
        token (str | required: false): When source is github, the token to be used to clone the required repository.
        dockerfile (str | required: false): When source is dockerfile, this represents the content of Dockerfile to build the image from.
      autodeployResources (list(map) | required: false): A list of resources that should be redeployed when the build completes.
            entityId (str): The id of the resource to be redeployed.
            entityType (str): The type of the resource to be redeployed. Allowed values are 'workflow', 'workspace', 'api' and 'webapp'.
    artifact (map | required: false):
      path (str): Path to the artifact.
      ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak images update-version --image-id 9999 --version-id 101 '/path/to/file.yaml' -v '/path/to/parmas.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak images update-version --image-id <image_id> --version-id <version_id> --description <description> --source <source> --dockerfile <dockerfile> --secrets <secret_1>,<secret_2>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "buildId": "build-image-mock:2198c71e-22c5-aca3eac3a55e",
        "versionId": 101,
        "autodeploymentId": "0a12abcd-11ab-22d2-123a-a1234b333abc"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/patch_api_v2_images__imageId__versions__versionId_)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        description,
        build_details,
        source,
        dockerfile,
        repository,
        branch,
        token,
        dockerfile_path,
        context,
        use_cache,
        build_arguments,
        secrets,
    )

    user_options = map_user_options(user_options, MAPPING, dict_type_keys=["buildDetails"])

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, image_client.update_version)

    updated_body = combine_dictionaries(
        body.get("body") or {},
        user_options,
    )
    artifact = helpers.get_updated_artifacts(body, artifact_path, artifact_ignore_files)

    if build_arguments:
        updated_body["buildDetails"]["buildArguments"] = helpers.parse_build_arguments(build_arguments)

    if secrets:
        updated_body["buildDetails"]["secrets"] = parse_list_of_strings(secrets)

    with writer.pager():
        response: Dict[str, str] = image_client.update_version(
            image_id=image_id,
            version_id=version_id,
            body=updated_body,
            artifact=artifact,  # type: ignore  # noqa: PGH003
        )
        writer.write(response)


@app.command(short_help="Delete an image.")
def delete(
    ctx: typer.Context,
    image_id: int = _IMAGE_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** an image. All the versions in the image will first go into `deleting` state before actually being deleted.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images delete 9999
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/images/delete_api_v2_images__imageId_)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = image_client.delete_image(image_id=image_id)
        writer.write(response)


@app.command(short_help="Delete an image version.")
def delete_version(
    ctx: typer.Context,
    image_id: int = args.IMAGE_ID,
    version_id: int = args.VERSION_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** an image version. An image cannot be deleted if it is being used by any other resource.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images delete-version --image-id 9999 --version-id 1
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/delete_api_v2_images__imageId__versions__versionId_)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response: Dict[None, None] = image_client.delete_version(image_id=image_id, version_id=version_id)
        writer.write(response)


@app.command(short_help="Delete all the specified versions.")
def delete_versions(
    ctx: typer.Context,
    image_id: int = args.IMAGE_ID,
    version_ids: List[str] = _VERSIONS_TO_DELETE,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** all the specified versions for an image.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images delete-versions --image-id 9999 --version-ids 1 --version-ids 2
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/versions/delete_api_v2_images__imageId__versions)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]
    parsed_version_ids = [int(version_id) for version_id in parse_list_of_strings(version_ids) or []]

    with writer.pager():
        response: Dict[None, None] = image_client.delete_versions(
            image_id=image_id,
            version_ids=parsed_version_ids,
        )
        writer.write(response)


@app.command(short_help="List image builds.")
def list_builds(
    ctx: typer.Context,
    image_id: int = _IMAGE_ID,
    count: Optional[int] = _COUNT,
    version_ids: Optional[List[str]] = _VERSIONS,
    build_status: Optional[List[str]] = _BUILD_STATUS,
    date_from: Optional[str] = args.DATE_FROM,
    date_to: Optional[str] = args.DATE_TO,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** image builds for a specific image. If you want to view builds for a specific version you can pass in Version's ID to the command.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images list-builds 9999 --version-ids 1,2,3 --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "buildCount": 1,
        "builds": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/builds/get_api_v2_images__imageId__builds)
    """
    image_client: Image = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = image_client.list_image_builds(
            image_id=image_id,
            count=count,
            build_status=parse_list_of_strings(build_status),
            version_ids=parse_list_of_strings(version_ids),
            date_from=date_from,
            date_to=date_to,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )

        writer.write(response)


@app.command(short_help="Get image build logs.")
def get_build_logs(
    ctx: typer.Context,
    image_id: int = args.IMAGE_ID,
    build_id: int = _BUILD_ID,
    next_token: Optional[str] = args.NEXT_TOKEN,
    follow: Optional[bool] = args.FOLLOW,
    save: Optional[bool] = args.SAVE,
    file_name: Optional[str] = args.FILE_NAME,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesOnlyJson] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** logs for an image build.

    \b
    If you want to save the logs to a file, you can use the `--save` flag.
    If you don't provide a file name, the logs will be saved to a file with the name `image_build_logs_{image_id}_{build_id}.log`.

    \b
    If you want to view next set of logs you can pass in the `nextToken` to the command.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak images get-build-logs --image-id <image_id> --build-id <build_id> --next-token <next_token>
    ```

    \b
    To follow the logs, you can use the `--follow` flag.

    \b
    📝 ***Example usage to follow the logs:***<br/>
    ```bash
    peak images get-build-logs --image-id <image_id> --build-id <build_id> --follow
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "buildStatus": "building",
        "finishTime": "2023-06-01T19:00:00.000Z",
        "logs": [
            {
                "ingestionTime": "2023-06-01T18:00:00.000Z",
                "message": "Building the Docker image...",
                "timestamp": "2023-06-01T18:00:00.000Z"
            }
        ],
        "nextToken": "f/37241814580157116960215105647056337845181039459911335941/s",
        "startTime": "2023-06-01T18:00:00.000Z"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/image-management/api-docs/index.htm#/builds/get_api_v2_images__imageId__builds__buildId__logs)
    """
    image_client: Image = ctx.obj["client"]
    writer = Writer()

    pager = writer.pager()  # Create pager context

    with pager:
        while True:
            response = image_client.get_build_logs(
                image_id=image_id,
                build_id=build_id,
                next_token=next_token,
                save=save,
                file_name=file_name,
            )

            if save or not response or "buildStatus" not in response or "logs" not in response:
                break

            if follow:
                if (response["buildStatus"] != "building") and (response["logs"] is None or len(response["logs"]) == 0):
                    break
                formatted_logs = helpers.format_logs(response["logs"])
                if len(formatted_logs):
                    writer.write(formatted_logs)
            else:
                writer.write(response)
                break

            next_token = response.get("nextToken", None)
