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
"""Peak blocks specs commands."""

from typing import Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.press.blocks import Block
from rich.console import Console

app = typer.Typer()
console = Console()

_SPEC_ID = typer.Argument(..., help="ID of the Block spec to be used in this operation.")


@app.command("list", short_help="List Block specs.")
def list_block_specs(
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
    """***List*** all Block specs that exists in the tenant along with the public-scoped ones.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks specs list --featured --scope shared,private --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "specsCount": 1,
        "specs": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.list_specs(
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


@app.command(short_help="Create a Block spec.")
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
    """***Create*** a Block spec. A Block spec is just a blueprint for a specific resource. This creates a version of the spec also know as a ***Release***.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
    featured (bool | required: false): Boolean specifying whether to feature this spec.
    scope (str | required: false): Specify what tenants can discover and deploy this spec.
    tenants (list(str) | required: false): Given a shared scope, specify what other tenants can discover and deploy this spec.
    autoRunOnDeploy (bool | required: false): Whether to execute the resource after the block is deployed. By default it is False.
    body (map):
        version (int): Version of the spec.
        kind (string): Specifies the type of spec.
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
        # Workflow Block
        config (map):
            images(map | required: false):
                image-name (map): Dictionary containing the image configuration. Here the key is name of the image.
                    version (string | required: false): A valid semantic image version.
                    dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                    context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                    useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                    buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                    secrets (list(str)) | required: false): List of secret names to be passed.
            steps (map | required: false):
                <stepName> (map): Dictionary containing the step configuration. Here the key is name of the step.
                    # Standard Step
                    image: (map | required: false):
                        version (string | required: false): A valid semantic image version.
                        dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                        context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                        useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                        buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                        secrets (list(str)) | required: false): List of secret names to be passed.
                    imageDetails (map | required: false):
                        id (int): ID of the existing image.
                        versionId: (int): ID of the existing image version.
                    imageRef (string | required: false): Name of the image defined above.
                    type (string | required: false): Type of workflow step. This should be 'standard' for a Standard Step which is the default value.
                    command (string): Command to run when step is executed.
                    clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                    stepTimeout (int | required: false): Time after which the step timeouts.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        secrets (list(str) | required: false): List of secret names to be passed.
                    parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                    repository (map | required: false):
                        branch (string): Branch of the repository containing the required files.
                        token (string | required: false): The token to be used to clone the repository.
                        url (string): URL of the repository.
                    resources (map | required: false):
                        instanceTypeId (int): ID of the instance type to be used in the step.
                        storage (string): Storage in GB. For example, "10GB".
                    outputParameters (map | required: false):
                        <keyName> (string | required: false): Represents a key-value pair where the key is the parameter name, and the value is the file name where the output is stored.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # HTTP Step
                    type (string | required: false): Type of workflow step. This should be 'http' for a HTTP Step.
                    method (string | required: true): The HTTP method to be used for the API call. Should be one of - get, post, put, patch, and delete
                    url (string | required: true): The URL to make the HTTP API call to.
                    payload (string | required: false): Stringified JSON payload to be sent in case of non-get requests.
                    headers (map | required: false):
                        absolute (map | required: false): Key-Value pair where key is the name of the header and value is the value of the header.
                        secrets (map | required: false): Key-Value pair where key is the name of the header and value is the name of the secret to get the value from.
                    auth (map | required: false):
                        type (string | required: true): The type of authentication to use. Should be one of - no-auth, oauth, basic, api-key, and bearer-token.
                        clientId (string | required: false): The Client ID used to get the access token in case of OAuth. Value should be the name of a secret. Required when type is oauth.
                        clientSecret (string | required: false): The Client Secret used to get the access token in case of OAuth. Value should be the name of a secret. Required when type is oauth.
                        authUrl (string | required: false): The URL that is hit to get the access token in case of OAuth. Required when type is oauth.
                        username (string | required: false): The username used for basic authentication. Required when type is basic.
                        password (string | required: false): The password used for basic authentication. Value should be the name of a secret. Required when type is basic.
                        apiKey (string | required: false): The API Key used for authentication. Value should be the name of a secret. Required when type is api-key.
                        bearerToken (string | required: false): The bearer token used for authentication. Value should be the name of a secret. Required when type is bearer-token.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                        secrets (list(str) | required: false): List of secret names to be passed.
                    outputParameters (map | required: false):
                        <keyName> (string | required: false): Represents a key-value pair where the key is the parameter name. Note that in case of HTTP step, value should always be "response.txt", otherwise this parameter would be rejected.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # Export Step
                    type (string | required: true): Type of workflow step. This should be 'export' for a export Step.
                    schema (string | required: true): Schema from which the data is to be exported.
                    table (string | required: true): Table from which the data is to be exported.
                    sortBy (string | required: true): Column name by which the data is to be sorted.
                    sortOrder (string | required: false): Order in which the data is to be sorted. Should be one of - asc, desc. Default is asc.
                    compression (boolean | required: false): Whether to compress the files to '.gz' format while exporting. Default is false.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # SQL Step
                    type (string | required: true): Type of workflow step. This should be 'sql' for a sql Step.
                    sqlQueryPath (string | required: false): Path to the SQL query file. One of the 'sqlQueryPath' or 'repository' is required.
                    repository (map | required: false):
                        branch (string | required: true): Branch of the repository containing the required files.
                        token (string | required: false): The token to be used to clone the repository.
                        url (string | required: true): URL of the repository.
                        filePath (string | required: true): Path to the file containing the SQL query.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
            triggers (list(map)):
                - cron (string | required: false): A valid cron expression.
                  webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
                  webhookId (string | required: false): ID of the webhook.
            watchers (list(map) | required: false):
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  user (string): User to be notified.
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  webhook (map):
                    name (string): Name of the webhook.
                    url (string): URL of the webhook.
                    payload (string): Webhook payload.
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  email (map):
                    name (string): Name of the email watcher.
                    recipients (map):
                        to (list(str)): List of email addresses to send the email to. Email can be sent only to the users who are added in the tenant.
        # Service Block
        config (map): # One of "image" or "imageDetails" is required.
            serviceType (string): Type of the service. Should be one of "web-app" or "api". It is "web-app" by default.
            image (map | required: false):
                version (string | required: false): A valid semantic image version.
                dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                secrets (list(str)) | required: false): List of secret names to be passed.
            imageDetails (map | required: false):
                id (int): ID of the existing image.
                versionId: (int | required: false): ID of the existing image version. If not provided, the latest version will be used.
            resources (map | required: false): To be used only in case of service block.
                instanceTypeId (int): ID of the instance type to be used in the service block.
            parameters (map | required: false):
                env (map | required: false): Key-Value pair where key is the name of the env.
                secrets (list(str) | required: false): List of secret names to be passed.
            sessionStickiness (boolean | required: false): Whether to enable session stickiness for the service. It is false by default. To be used only in case of service block of type web-app.
            scaleToZero (boolean | required: false): Enable scale to zero for the service. Only applicable for web-app type services. Default value is false. Enabling Scale to zero ensures that the resources hosting your app are scaled down when ideal over a period of time. The resources will scale back up automatically on next launch.
            entrypoint (string | required: false): Entry point for the service.
            healthCheckURL (string | required: false): URL to check the health of the service.
            minInstances (number | required: false): Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.
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
    artifact (map | required: false):
      path (str): Path to the artifact.
      ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks specs create /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/post_v1_blocks_specs)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if description_file:
        markdown_files["body:metadata:description"] = description_file
    if release_notes_file:
        markdown_files["body:release:notes"] = release_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, block_client.create_spec)

    with writer.pager():
        response: Dict[str, str] = block_client.create_spec(**body)
        writer.write(response)


@app.command(short_help="Describe a Block spec.")
def describe(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** a Block spec with details of its latest release.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks specs describe "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
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
        "parameters": {...},
        "scope": "private"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId_)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.describe_spec(spec_id)
        writer.write(response)


@app.command(short_help="Update the Block spec metadata.")
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
    """***Update*** the Block spec metadata.

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
            imageUrl (string | required: false): URL of the image to be associated with the block spec.
            status (string | required: false): Status of the block spec.
            tags (list(map) | required: false):
                - name (string): Name of the tag.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks specs update-metadata "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "featured": false,
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
        "kind": "workflow",
        "latestRelease": {...},
        "metadata": {...},
        "scope": "private"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/patch_v1_blocks_specs__specId_)
    """
    markdown_files = {}
    if description_file:
        markdown_files["body:metadata:description"] = description_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    writer: Writer = ctx.obj["writer"]

    block_client: Block = ctx.obj["client"]
    body = helpers.remove_unknown_args(body, block_client.update_spec_metadata)

    with writer.pager():
        response: Dict[None, None] = block_client.update_spec_metadata(spec_id, **body)
        writer.write(response)


@app.command(short_help="Delete a Block spec.")
def delete(
    ctx: typer.Context,
    spec_id: str = _SPEC_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** a Block spec.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks specs delete "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/delete_v1_blocks_specs__specId_)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.delete_spec(spec_id)
        writer.write(response)


@app.command(short_help="Create a new release for a Block spec.")
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
    """***Create*** a new release for a Block spec.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
    body (map):
        release (map):
            version (string): A valid semantic release version of the spec. Must be greater than previous release version.
            notes (string | required: false): Notes for the release version.
        # Workflow Block
        config (map):
            images(map | required: false):
                image-name(map): Dictionary containing the image configuration. Here the key is name of the image.
                    version (string | required: false): A valid semantic image version.
                    dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                    context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                    useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                    buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                    secrets (list(str)) | required: false): List of secret names to be passed.
            steps(map | required: false):
                <stepName> (map): # Dictionary containing the step configuration. Here the key is name of the step.
                    # Standard Step
                    image: (map | required: false):
                        version (string | required: false): A valid semantic image version.
                        dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                        context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                        useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                        buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                        secrets (list(str)) | required: false): List of secret names to be passed.
                    imageDetails (map | required: false):
                        id (int): ID of the existing image.
                        versionId: (int): ID of the existing image version.
                    imageRef (string | required: false): Name of the image defined above.
                    type (string | required: false): Type of workflow step. This should be 'standard' for a Standard Step which is the default value.
                    command (string): Command to run when step is executed.
                    clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                    stepTimeout (int | required: false): Time after which the step timeouts.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                        secrets (list(str) | required: false): List of secret names to be passed.
                    outputParameters (map | required: false):
                        <keyName> (string | required: false): Represents a key-value pair where the key is the parameter name, and the value is the file name where the output is stored.
                    parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                    repository (map | required: false):
                        branch (string): Branch of the repository containing the required files.
                        token (string | required: false): The token to be used to clone the repository.
                        url (string): URL of the repository.
                    resources (map | required: false):
                        instanceTypeId (int): ID of the instance type to be used in the step.
                        storage (string): Storage in GB. For example, "10GB".
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # HTTP Step
                    type (string | required: false): Type of workflow step. This should be 'http' for a HTTP Step.
                    method (string | required: true): The HTTP method to be used for the API call. Should be one of - get, post, put, patch, and delete
                    url (string | required: true): The URL to make the HTTP API call to.
                    payload (string | required: false): Stringified JSON payload to be sent in case of non-get requests.
                    headers (map | required: false):
                        absolute (map | required: false): Key-Value pair where key is the name of the header and value is the value of the header.
                        secrets (map | required: false): Key-Value pair where key is the name of the header and value is the name of the secret to get the value from.
                    auth (map | required: false):
                        type (string | required: true): The type of authentication to use. Should be one of - no-auth, oauth, basic, api-key, and bearer-token.
                        clientId (string | required: false): The Client ID used to get the access token in case of OAuth. Value should be the name of a secret. Required when type is oauth.
                        clientSecret (string | required: false): The Client Secret used to get the access token in case of OAuth. Value should be the name of a secret. Required when type is oauth.
                        authUrl (string | required: false): The URL that is hit to get the access token in case of OAuth. Required when type is oauth.
                        username (string | required: false): The username used for basic authentication. Required when type is basic.
                        password (string | required: false): The password used for basic authentication. Value should be the name of a secret. Required when type is basic.
                        apiKey (string | required: false): The API Key used for authentication. Value should be the name of a secret. Required when type is api-key.
                        bearerToken (string | required: false): The bearer token used for authentication. Value should be the name of a secret. Required when type is bearer-token.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                        secrets (list(str) | required: false): List of secret names to be passed.
                    outputParameters (map | required: false):
                        <keyName> (string | required: false): Represents a key-value pair where the key is the parameter name. Note that in case of HTTP step, value should always be "response.txt", otherwise this parameter would be rejected.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # Export Step
                    type (string | required: true): Type of workflow step. This should be 'export' for a export Step.
                    schema (string | required: true): Schema from which the data is to be exported.
                    table (string | required: true): Table from which the data is to be exported.
                    sortBy (string | required: true): Column name by which the data is to be sorted.
                    sortOrder (string | required: false): Order in which the data is to be sorted. Should be one of - asc, desc. Default is asc.
                    compression (boolean | required: false): Whether to compress the files to '.gz' format while exporting. Default is false.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
                    # SQL Step
                    type (string | required: true): Type of workflow step. This should be 'sql' for a sql Step.
                    sqlQueryPath (string | required: false): Path to the SQL query file. One of the 'sqlQueryPath' or 'repository' is required.
                    repository (map | required: false):
                        branch (string | required: true): Branch of the repository containing the required files.
                        token (string | required: false): The token to be used to clone the repository.
                        url (string | required: true): URL of the repository.
                        filePath (string | required: true): Path to the file containing the SQL query.
                    parameters (map | required: false):
                        env (map | required: false): Key-Value pair where key is the name of the env.
                        inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                    executionParameters (map | required: false):
                        conditional (list(map) | required: false): # List of conditions to be evaluated based on the output params of the parent steps.
                            - condition (string): The evaluation condition, either 'equals' or 'not-equals'.
                            paramName (string): Name of the output parameter to be evaluated.
                            stepName (string): Name of the step containing the output parameter.
                            value (string): Value to be compared with the output parameter.
                        parentStatus (list(map) | required: false): # List of conditions to be evaluated based on the status of the parent steps.
                            - condition (string): The evaluation condition, either 'all-of' or 'one-of'.
                            parents (list(str)): List of parent step names.
                            status (list(str)): List of parent step statuses, with valid values being 'success' and 'failure'.
                    runConfiguration (map | required: false):
                        retryOptions (map | required: false): # Step level retry options which will override the workflow level retry options.
                            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
                            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
                            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
                            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
                        skipConfiguration (map | required: false):
                            skip (boolean | required: false): Indicates whether to skip the step. Default is false.
                            skipDAG (boolean | required: false): Indicates whether to skip dependent steps, including the current step. Default is false.
            triggers (list(map)):
                cron (string | required: false): A valid cron expression.
                webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
                webhookId (string | required: false): ID of the webhook.
            watchers (list(map) | required: false):
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  user (string): User to be notified.
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  webhook (map):
                    name (string): Name of the webhook.
                    url (string): URL of the webhook.
                    payload (string): Webhook payload.
                - events (map):
                    success (boolean | required: false): Whether to call event on success.
                    fail (boolean | required: false): Whether to call event on failure.
                    runtimeExceeded (int | required: false): The runtime in minutes after which event is called.
                  email (map):
                    name (string): Name of the email watcher.
                    recipients (map):
                        to (list(str)): List of email addresses to send the email to. Email can be sent only to the users who are added in the tenant.
        # Service Block
        config (map): # One of "image" or "imageDetails" is required.
            serviceType (string): Type of the service. Should be one of "web-app" or "api". It is "web-app" by default.
            image (map | required: false):
                version (string | required: false): A valid semantic image version.
                dockerfile (string | required: false): Path to the Dockerfile inside artifact.
                context (string | required: false): The path within the artifact where the code to be executed by the Dockerfile is located.
                useCache (boolean | required: false): Whether to enable image caching to reduce build time, is enabled by default.
                buildArguments (map | required: false): Dictionary containing build args. Here the key is the name of the arg and value is the value of the arg.
                secrets (list(str)) | required: false): List of secret names to be passed.
            imageDetails (map | required: false):
                id (int): ID of the existing image.
                versionId: (int | required: false): ID of the existing image version. If not provided, the latest version will be used.
            resources (map | required: false):
                instanceTypeId (int): ID of the instance type to be used in the service block.
            parameters (map | required: false):
                env (map | required: false): Key-Value pair where key is the name of the env.
                secrets (list(str) | required: false): List of secret names to be passed.
            sessionStickiness (boolean | required: false): Whether to enable session stickiness for the service. It is false by default. To be used only in case of service block of type web-app.
            scaleToZero (boolean | required: false): Enable scale to zero for the service. Only applicable for web-app type services. Default value is false. Enabling Scale to zero ensures that the resources hosting your app are scaled down when ideal over a period of time. The resources will scale back up automatically on next launch.
            entrypoint (string | required: false): Entry point for the service.
            healthCheckURL (string | required: false): URL to check the health of the service.
            minInstances (number | required: false): Minimum number of instances that would run for a service. Default value is 1 and maximum value allowed is 2.
    parameters (map | required: false):
        <parameterType> (list(map)): List containing the parameter objects. Here the key is the type of the parameter. Accepted values are "build" or "run".
            name (string): Name of the parameter.
            type (string): Type of the parameter. Should be one of "boolean", "string", "string_array", "number", "number_array", "object" and "object_array".
            required (boolean): Whether the parameter is required.
            description (string | required: false): Description of the parameter.
            defaultValue (string | required: false): Default value of the parameter.
            title (string | required: false): Title of the parameter.
            options (list(str) | required: false): List of options for the parameter. If provided, it must have at least one object with "title" and "value" field.
            conditions(list(map) | required: false): Conditions that determine when the parameter should be enabled. Conditions on two or more parameters should be used with conditionType "AND" or "OR".
                - dependsOn (string): Name of the parameter that this parameter depends on.
                  operator (string): Operator to be used for the condition. Should be one of "equals" or "not-equals".
                  value (string): Value to be compared with the parameter.
                - conditionType (string): Type of the condition. Should be one of "AND" or "OR".
                  conditions (list(map)): Nested conditions that determine when the parameter should be enabled.
    artifact (map | required: false):
        path (str): Path to the artifact.
        ignore_files (list(str) | required: false) : Ignore files to use when creating artifact.
    autoRunOnDeploy (bool | required: false): Whether to execute the resource after the block is deployed. By default it is False.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks specs create-release "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" '/path/to/body.yaml' -v '/path/to/params.yaml'
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

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/post_v1_blocks_specs__specId__releases)
    """
    markdown_files = {}
    if release_notes_file:
        markdown_files["body:release:notes"] = release_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    writer: Writer = ctx.obj["writer"]

    block_client: Block = ctx.obj["client"]
    body = helpers.remove_unknown_args(body, block_client.create_spec_release)

    with writer.pager():
        response: Dict[str, str] = block_client.create_spec_release(spec_id, **body)
        writer.write(response)


@app.command(short_help="Describe a Block spec release.")
def describe_release(
    ctx: typer.Context,
    spec_id: str = args.SPEC_ID,
    version: str = args.RELEASE_VERSION,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** a Block spec release.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks specs describe-release --spec-id "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --version 1.0.0
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "artifact": {
            "id": "721d738a-29f3-43b2-af52-c9055abe60b6",
            "version": 1
        },
        "config": {
            "images": {...},
            "steps": {...},
            "triggers": [
                {...}
            ],
            "watchers": [
                {...}
            ]
        },
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "someoneh@peak.ai",
        "id": "df113d64-ff44-4aa0-9278-edb03dae7a3f",
        "notes": "This is the original release",
        "autoRunOnDeploy": false,
        "parameters": {...},
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId__releases__release_)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.describe_spec_release(spec_id, version)
        writer.write(response)


@app.command(short_help="List releases of a Block spec.")
def list_releases(
    ctx: typer.Context,
    spec_id: str = args.SPEC_ID,
    sort: Optional[List[str]] = args.SORT_KEYS,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all releases for a given Block spec.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks specs list-releases --spec-id "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --sort createdBy:asc,createdAt --page-size 10 --page-number 1
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

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Specs/get_v1_blocks_specs__specId__releases)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.list_spec_releases(
            spec_id,
            sort=sort,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)
