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
"""Peak apps specs commands."""

from typing import Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.press.apps import App
from rich.console import Console

app = typer.Typer()
console = Console()

_SPEC_ID = typer.Argument(..., help="ID of the App spec to be used in this operation.")


@app.command(short_help="Create an App spec.")
def create(
    ctx: typer.Context,
    file: str = args.TEMPLATE_PATH,
    description_file: Optional[str] = args.TEMPLATE_DESCRIPTION_FILE,
    release_notes_file: Optional[str] = args.RELEASE_NOTES_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** an App spec. A Spec is just a blueprint for an App and defines all the resources that need to be created for the App. This creates a version of the spec also known as ***Release***.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      featured (bool | required: false): Boolean specifying whether to feature this spec.
      scope (str | required: false): Specify what tenants can discover and deploy this spec.
      tenants (list(str) | required: false): Given a shared scope, specify what other tenants can discover and deploy this spec.
      body (map):
        version (int): Version of the spec.
        kind (string): Specifies the type of spec. Should be "app" in case of app spec.
        metadata (map):
            name (string): Name of the spec. Must be unique within the tenant.
            title (string | required: false): Title of the spec.
            summary (string): Summary of the spec.
            description (string | required: false): Description of the spec.
            descriptionContentType (string | required: false): Content type of the description. Should be one of "text/plain" or "text/markdown".
            imageUrl (string | required: false): URL of the image to be associated with the app spec.
            tags (list(map) | required: false):
                - name (string): Name of the tag.
        release (map):
            version (string): A valid semantic release version of the spec.
            notes (string | required: false): Notes for the release version.
        config (list(map)):
            - id (string): ID of the block spec.
              release (map):
                version (string): A valid semantic release version of the block spec.
              autoRunOnDeploy (bool | required: false): Whether to execute the resource after the app is deployed. By default it is False.
      parameters (map | required: false):
        <parameterType> (list(map)): List containing the parameter objects. Here the key is the type of the parameter. Accepted values are "build" or "run".
            name (string): Name of the parameter.
            type (string): Type of the parameter. Should be one of "boolean", "string", "string_array", "number", "number_array", "object" and "object_array".
            required (boolean): Whether the parameter is required.
            description (string | required: false): Description of the parameter.
            defaultValue (string | required: false): Default value of the parameter.
            title (string | required: false): Title of the parameter.
            options (list(str) | required: false): List of options for the parameter. If provided, it must have at least one object with "title" and "value" field.
            hideValue(boolean | required: false): Can be optionally provided to parameters of type "string", to mask the parameter's value when it has been set at deployment time.
            conditions(list(map) | required: false): Conditions that determine when the parameter should be enabled. Conditions on two or more parameters should be used with conditionType "AND" or "OR".
                - dependsOn (string): Name of the parameter that this parameter depends on.
                  operator (string): Operator to be used for the condition. Should be one of "equals" or "not-equals".
                  value (string): Value to be compared with the parameter.
                - conditionType (string): Type of the condition. Should be one of "AND" or "OR".
                  conditions (list(map)): Nested conditions that determine when the parameter should be enabled.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak apps specs create /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/post_v1_apps_specs_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if description_file:
        markdown_files["body:metadata:description"] = description_file
    if release_notes_file:
        markdown_files["body:release:notes"] = release_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, app_client.create_spec)

    with writer.pager():
        response: Dict[str, str] = app_client.create_spec(**body)
        writer.write(response)


@app.command("list", short_help="List App specs.")
def list_app_specs(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = args.STATUS_FILTER_SPECS,
    name: Optional[str] = args.NAME_FILTER,
    title: Optional[str] = args.TITLE_FILTER,
    sort: Optional[List[str]] = args.SORT_KEYS,
    scope: Optional[List[str]] = args.SCOPES,
    featured: Optional[bool] = args.FEATURED,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all App specs that have been created for the tenant along with the public-scoped ones.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak apps specs list --sort name:asc,title --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "specCount": 1,
        "specs": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = app_client.list_specs(
            status=status,
            featured=featured,
            name=name,
            title=title,
            sort=sort,
            scope=scope,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Describe an App spec.")
def describe(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** an App spec with details of its latest release.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak apps specs describe "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "featured": true,
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
        "kind": "app",
        "latestRelease": {...},
        "metadata": {...},
        "scope": "private"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = app_client.describe_spec(spec_id)
        writer.write(response)


@app.command(short_help="Update the App spec metadata.")
def update_metadata(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    file: str = args.TEMPLATE_PATH,
    description_file: Optional[str] = args.TEMPLATE_DESCRIPTION_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** the App spec metadata.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      body (map):
        featured (bool | required: false): Boolean specifying whether to feature this spec.
        scope (str | required: false): Specify what tenants can discover and deploy this spec.
        tenants (list(str) | required: false): Given a shared scope, specify what other tenants can discover and deploy this spec.
        metadata (map):
            name (string | required: false): Name of the spec. Must be unique within the tenant.
            title (string | required: false): Title of the spec.
            summary (string | required: false): Summary of the spec.
            description (string | required: false): Description of the spec.
            descriptionContentType (string | required: false): Content type of the description. Should be one of "text/plain" or "text/markdown".
            imageUrl (string | required: false): URL of the image to be associated with the app spec.
            status (string | required: false): Status of the app spec.
            tags (list(map) | required: false):
                - name (string): Name of the tag.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak apps specs update-metadata "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "featured": false,
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
        "kind": "app",
        "latestRelease": {...},
        "metadata": {...},
        "scope": "private"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/patch_v1_apps_specs__specId_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if description_file:
        markdown_files["body:metadata:description"] = description_file

    data = helpers.template_handler(file, params_file, params, markdown_files)
    data = helpers.remove_unknown_args(data, app_client.update_spec_metadata)

    with writer.pager():
        response: Dict[None, None] = app_client.update_spec_metadata(spec_id, **data)
        writer.write(response)


@app.command(short_help="Delete an App spec.")
def delete(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** an App spec.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak apps specs delete "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/delete_v1_apps_specs__specId_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = app_client.delete_spec(spec_id)
        writer.write(response)


@app.command(short_help="Create a new release of the App spec.")
def create_release(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    file: str = args.TEMPLATE_PATH,
    release_notes_file: Optional[str] = args.RELEASE_NOTES_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new release of the App spec.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      body (map):
        release (map):
            version (string): A valid semantic release version of the spec. Must be greater than previous release version.
            notes (string | required: false): Notes for the release version.
        config (list(map)):
            - id (string): ID of the block spec.
              release (map):
                version (string): A valid semantic release version of the block spec.
              autoRunOnDeploy (bool | required: false): Whether to execute the resource after the app is deployed. By default it is False.
      parameters (map | required: false):
        <parameterType> (list(map)): List containing the parameter objects. Here the key is the type of the parameter. Accepted values are "build" or "run".
            name (string): Name of the parameter.
            type (string): Type of the parameter. Should be one of "boolean", "string", "string_array", "number", "number_array", "object" and "object_array".
            required (boolean): Whether the parameter is required.
            description (string | required: false): Description of the parameter.
            defaultValue (string | required: false): Default value of the parameter.
            title (string | required: false): Title of the parameter.
            options (list(str) | required: false): List of options for the parameter. If provided, it must have at least one object with "title" and "value" field.
            hideValue(boolean | required: false): Can be optionally provided to parameters of type "string", to mask the parameter's value when it has been set at deployment time.
            conditions(list(map) | required: false): Conditions that determine when the parameter should be enabled. Conditions on two or more parameters should be used with conditionType "AND" or "OR".
                - dependsOn (string): Name of the parameter that this parameter depends on.
                  operator (string): Operator to be used for the condition. Should be one of "equals" or "not-equals".
                  value (string): Value to be compared with the parameter.
                - conditionType (string): Type of the condition. Should be one of "AND" or "OR".
                  conditions (list(map)): Nested conditions that determine when the parameter should be enabled.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak apps specs create-release "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb",
        "release": {
            "version": "2.0.0"
        }
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/post_v1_apps_specs__specId__releases)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if release_notes_file:
        markdown_files["body:release:notes"] = release_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, app_client.create_spec_release)

    with writer.pager():
        response: Dict[str, str] = app_client.create_spec_release(spec_id, **body)
        writer.write(response)


@app.command(short_help="Describe an App spec release.")
def describe_release(
    ctx: typer.Context,
    spec_id: str = args.SPEC_ID,
    version: str = args.RELEASE_VERSION,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** an App spec release.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak apps specs describe-release --spec-id "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --version 1.0.0
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "config": [
            {
                "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb",
                "release": {
                    "version": "1.0.0"
                }
            }
        ],
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "jane.smith@peak.ai",
        "id": "6a6b9e08-638e-4116-a29d-077086135062",
        "notes": "Updated workflows with new algorithms."
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId__releases__release_)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = app_client.describe_spec_release(spec_id, version)
        writer.write(response)


@app.command(short_help="List App specs releases.")
def list_releases(
    ctx: typer.Context,
    spec_id: str = args.SPEC_ID,
    sort: Optional[List[str]] = args.SORT_KEYS,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all the releases for a specific App Spec.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak apps specs list-releases --spec-id "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --sort createdAt:asc --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10,
        "releaseCount": 1,
        "releases": [...]
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/App%20Specs/get_v1_apps_specs__specId__releases)
    """
    app_client: App = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = app_client.list_spec_releases(
            spec_id=spec_id,
            sort=sort,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)
