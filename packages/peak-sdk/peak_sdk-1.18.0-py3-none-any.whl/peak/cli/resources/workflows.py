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
"""Peak Workflow management service commands."""

from typing import Any, Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable, OutputTypesOnlyJson
from peak.helpers import parse_list_of_strings
from peak.output import Writer
from peak.resources.workflows import Workflow
from typing_extensions import Annotated

app = typer.Typer(
    help="Create Machine Learning Pipelines using Workflows.",
    short_help="Create and manage Workflows.",
)

_WORKFLOW_STATUS = typer.Option(
    None,
    help="List of status to filter workflows. Valid values are `Draft`, `Running`, `Available`, `Paused`.",
)

_LAST_EXECUTION_STATUS = typer.Option(
    None,
    help="List of execution status of the latest run of the workflows to filter them by. Valid values are `Success`, `Running`, `Stopped`, `Stopping`, `Failed`.",
)

_LAST_MODIFIED_BY = typer.Option(None, help="List of users who last modified the workflow, used to filter workflows.")

_WORKFLOW_ID = typer.Argument(..., help="ID of the workflow to be used in this operation.")

_WORKFLOW_ID_OPTION = typer.Option(..., help="ID of the workflow to be used in this operation.")

_EXECUTION_ID = typer.Option(..., help="ID of the workflow execution to be used in this operation.")

_LIST_NAME = typer.Option(None, help="Workflow name to search for.")

_NAME = typer.Option(None, help="Name of the workflow")

_STEP_NAME = typer.Option(..., help="Name of the workflow step to be used in this operation.")

_REPOSITORY = typer.Option(None, help="URL of the repository containing the required files.")

_BRANCH = typer.Option(None, help="The branch of the repository to use.")

_TOKEN = typer.Option(None, help="The token to use to access the repository.")

_COMMAND = typer.Option(None, help="The command to run when workflow step is executed.")

_IMAGE_ID = typer.Option(None, help="The ID of the image to use for the workflow step.")

_IMAGE_VERSION_ID = typer.Option(None, help="The ID of the image version to use for the workflow step.")

_INSTANCE_TYPE_ID = typer.Option(None, help="The ID of the instance type to use for the workflow step.")

_STORAGE = typer.Option(None, help="The storage to use for the workflow step.")

_STEP_TIMEOUT = typer.Option(None, help="The time after which the step timeouts.")

_CLEAR_IMAGE_CACHE = typer.Option(None, help="Whether to clear image cache on workflow execution.")

_STEP_NAMES = typer.Option(None, help="List of step names to be updated.")

_EXECUTION_STATUS = typer.Option(
    None,
    help="List of workflow execution statuses. Valid values are `Success`, `Running`, `Stopped`, `Stopping` and `Failed`.",
)

_COUNT = typer.Option(
    None,
    help="Number of workflow executions required in the provided time range or 90 days. If not provided, all executions are returned.",
)


@app.command(short_help="Create a new workflow.")
def create(
    ctx: typer.Context,
    file: str = args.TEMPLATE_PATH,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new workflow.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (string): Name of the worklfow.
        tags (list(map) | required: false):
            - name (string): Name of the tag.
        triggers (list(map) | required: false):
            - cron (string | required: false): A valid cron expression.
              webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
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
        retryOptions (map | required: false): # Workflow level retry options which will be applied to all steps.
            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
        steps(map):
            <stepName> (map): # Dictionary containing the step configuration. Here the key is name of the step.
                # Standard Step
                imageId (int): ID of the existing image.
                imageVersionId: (int | required: false): ID of the existing image version.
                type (string | required: false): Type of workflow step. This should be 'standard' for a Standard Step.
                command (string): Command to run when step is executed.
                clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                stepTimeout (int | required: false): Time after which the step timeouts.
                parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                repository (map | required: false):
                    branch (string): Branch of the repository containing the required files.
                    token (string | required: false): The token to be used to clone the repository.
                    url (string): URL of the repository.
                resources (map | required: false):
                    instanceTypeId (int): ID of the instance type to be used in the step.
                    storage (string): Storage in GB. For example, "10GB".
                parameters (map | required: false):
                    env (map | required: false): Key-Value pair where key is the name of the env.
                    inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                    secrets (list(str) | required: false): List of secret names to be passed.
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
                type (string | required: true): Type of workflow step. This should be 'http' for a HTTP Step.
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
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak workflows create /path/to/file.yml -v /path/to/params.yml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": 123,
        "triggers": [
            {
                "webhook": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
            }
        ]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/create-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = helpers.template_handler(file=file, params_file=params_file, params=params)
    body = helpers.remove_unknown_args(body, workflow_client.create_workflow)
    with writer.pager():
        response: Dict[str, int] = workflow_client.create_workflow(**body)
        writer.write(response)


@app.command(short_help="Update an existing workflow.")
def update(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    file: str = args.TEMPLATE_PATH,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** an existing workflow.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (string): Name of the worklfow.
        tags (list(map) | required: false):
            - name (string): Name of the tag.
        triggers (list(map) | required: false):
            - cron (string | required: false): A valid cron expression.
              webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
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
        retryOptions (map | required: false): # Workflow level retry options which will be applied to all steps.
            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
        steps(map):
            <stepName> (map): # Dictionary containing the step configuration. Here the key is name of the step.
                # Standard Step
                imageId (int): ID of the existing image.
                imageVersionId: (int | required: false): ID of the existing image version.
                type (string | required: false): Type of workflow step. This should be 'standard' for Standard Step.
                command (string): Command to run when step is executed.
                clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                stepTimeout (int | required: false): Time after which the step timeouts.
                parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                repository (map | required: false):
                    branch (string): Branch of the repository containing the required files.
                    token (string | required: false): The token to be used to clone the repository.
                    url (string): URL of the repository.
                resources (map | required: false):
                    instanceTypeId (int): ID of the instance type to be used in the step.
                    storage (string): Storage in GB. For example, "10GB".
                parameters (map | required: false):
                    env (map | required: false): Key-Value pair where key is the name of the env.
                    inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                    secrets (list(str) | required: false): List of secret names to be passed.
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
      ```

    \b
    📝 ***Example usage:***
    ```bash
    peak workflows update 9999 /path/to/file.yml -v /path/to/params.yml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": 123,
        "triggers": [
            {
                "webhook": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
            }
        ]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/update-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = helpers.template_handler(file=file, params_file=params_file, params=params)
    body = helpers.remove_unknown_args(body, workflow_client.update_workflow)
    with writer.pager():
        response: Dict[str, Any] = workflow_client.update_workflow(workflow_id=workflow_id, **body)
        writer.write(response)


@app.command(
    short_help="Create a new workflow or Update an existing workflow.",
)
def create_or_update(
    ctx: typer.Context,
    file: str = args.TEMPLATE_PATH,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a new workflow or ***Update*** an existing workflow based on workflow name.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        name (string): Name of the worklfow.
        tags (list(map) | required: false):
            - name (string): Name of the tag.
        triggers (list(map) | required: false):
            - cron (string | required: false): A valid cron expression.
              webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
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
        retryOptions (map | required: false): # Workflow level retry options which will be applied to all steps.
            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
        steps(map):
            <stepName> (map): # Dictionary containing the step configuration. Here the key is name of the step.
                # Standard Step
                imageId (int): ID of the existing image.
                imageVersionId: (int | required: false): ID of the existing image version.
                type (string | required: false): Type of workflow step. This should be 'standard' for Standard Step.
                command (string): Command to run when step is executed.
                clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                stepTimeout (int | required: false): Time after which the step timeouts.
                parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                repository (map | required: false):
                    branch (string): Branch of the repository containing the required files.
                    token (string | required: false): The token to be used to clone the repository.
                    url (string): URL of the repository.
                resources (map | required: false):
                    instanceTypeId (int): ID of the instance type to be used in the step.
                    storage (string): Storage in GB. For example, "10GB".
                parameters (map | required: false):
                    env (map | required: false): Key-Value pair where key is the name of the env.
                    inherit (map | required: false): Key-Value pair where key is the name of the env and value is the name of the output parameter.
                    secrets (list(str) | required: false): List of secret names to be passed.
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
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak workflows create-or-update /path/to/file.yml -v /path/to/params.yml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": 123,
        "triggers": [
            {
                "webhook": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
            }
        ]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/create-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    body: Dict[str, Any] = helpers.template_handler(file=file, params_file=params_file, params=params)
    body = helpers.remove_unknown_args(body, workflow_client.create_or_update_workflow)
    with writer.pager():
        response: Dict[str, int] = workflow_client.create_or_update_workflow(**body)
        writer.write(response)


@app.command(short_help="Update required fields of an existing workflow.")
def patch(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    name: str = _NAME,
    repository: str = _REPOSITORY,
    branch: str = _BRANCH,
    token: str = _TOKEN,
    image_id: int = _IMAGE_ID,
    image_version_id: int = _IMAGE_VERSION_ID,
    command: str = _COMMAND,
    clear_image_cache: bool = _CLEAR_IMAGE_CACHE,
    step_timeout: int = _STEP_TIMEOUT,
    instance_type_id: int = _INSTANCE_TYPE_ID,
    storage: str = _STORAGE,
    step_names: List[str] = _STEP_NAMES,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** an existing workflow.

    \b
    This command allows to efficiently modify trigger details, watchers, workflow name, and specific step attributes such as repository URL, branch, token, image ID, version ID etc.

    \b
    By specifying step_names, we can globally update specified steps with provided parameters, streamlining the update process. If step_names is not provided, all the steps for that workflow would be updated.

    \b
    Alternatively, we can selectively modify individual step attributes across different steps by providing the details in the yaml file. With this, we can also add new steps to the workflow by providing the parameters required by the step.

    \b
    If both body and specific parameters are used, the latter takes precedence.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
    body (map | required: false):
        name (string | required: false): Name of the worklfow.
        tags (list(map) | required: false):
            - name (string): Name of the tag.
        triggers (list(map) | required: false):
            - cron (string | required: false): A valid cron expression.
              webhook (boolean | required: false): Should be true if webhook type trigger is to be used.
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
        retryOptions (map | required: false): # Workflow level retry options which will be applied to all steps.
            duration (int | required: false): Duration in seconds after which the step is retried if it fails. Default is 5 seconds and maximum is 120 seconds.
            exitCodes (list(int) | required: false): List of exit codes for which the step is retried. If not provided, the step is retried for all exit codes.
            exponentialBackoff (boolean | required: false): Whether to use exponential backoff for retrying the step. If provided as true, the factor used will be 2.
            numberOfRetries (int | required: false): Number of times the step should be retried. Default is 3 and maximum is 5.
        steps(map):
            <stepName> (map): # Dictionary containing the step configuration. Here the key is name of the step.

            # Standard Step
                imageId (int): ID of the existing image.
                imageVersionId: (int | required: false): ID of the existing image version.
                type (string | required: false): Type of workflow step. This should be standard for Standard Step.
                command (string): Command to run when step is executed.
                clearImageCache (boolean | required: false): Whether to clear image cache on workflow execution.
                stepTimeout (int | required: false): Time after which the step timeouts.
                parents (list(str) | required: false): List containing names of steps on which this step is dependent on.
                repository (map | required: false):
                    branch (string): Branch of the repository containing the required files.
                    token (string | required: false): The token to be used to clone the repository.
                    url (string): URL of the repository.
                resources (map | required: false):
                    instanceTypeId (int): ID of the instance type to be used in the step.
                    storage (string): Storage in GB. For example, "10GB".
                parameters (map | required: false):
                    env (map | required: false): Key-Value pair where key is the name of the env.
                    secrets (list(str) | required: false): List of secret names to be passed.
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
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak workflows patch 9999 /path/to/file.yml -v /path/to/params.yml
    ```

    \b
    📝 ***Example usage for updating workflow by passing only required parameters:***
    ```bash
    peak workflows patch 9999 --name <workflow_name> --image-id <image-id> --version-id <image-version-id> --step-names <step-name-1>,<step-name-2>
    ```

    \b
    🆗 ***Response:***
    ```js
    {
        "triggers": [
            {
                "webhook": "db88c21d-1add-45dd-a72e-8c6b83b68dee"
            }
        ]
        "id": 9999,
    }
    ```
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]
    body: Dict[str, Any] = {}

    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, workflow_client.patch_workflow)

    with writer.pager():
        response: Dict[str, Any] = workflow_client.patch_workflow(
            workflow_id=workflow_id,
            body=body["body"] if body else {},
            step_names=step_names,
            name=name,
            repository=repository,
            branch=branch,
            token=token,
            image_id=image_id,
            image_version_id=image_version_id,
            command=command,
            clear_image_cache=clear_image_cache,
            step_timeout=step_timeout,
            instance_type_id=instance_type_id,
            storage=storage,
        )
        writer.write(response)


@app.command("list", short_help="List workflows.")
def list_workflows(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    workflow_status: Optional[List[str]] = _WORKFLOW_STATUS,
    last_execution_status: Optional[List[str]] = _LAST_EXECUTION_STATUS,
    last_modified_by: Optional[List[str]] = _LAST_MODIFIED_BY,
    name: Optional[str] = _LIST_NAME,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all workflows that exist for the tenant.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows list --page-size 10 --page-number 1 --workflow-status "Draft" --last-execution-status "Success" --last-modified-by "abc@peak.ai" --name "test"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25,
        "workflows": [...],
        "workflowsCount": 1
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/get-workflows)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.list_workflows(
            page_size=page_size,
            page_number=page_number,
            workflow_status=parse_list_of_strings(workflow_status),
            last_execution_status=parse_list_of_strings(last_execution_status),
            last_modified_by=parse_list_of_strings(last_modified_by),
            name=name,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Describe details of a workflow.")
def describe(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details of a specific workflow.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows describe 9999
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": 9999,
        "name": "workflow-name",
        "createdAt": "2020-01-01T18:00:00.000Z",
        "updatedAt": "2020-01-01T18:00:00.000Z",
        "status": "Available",
        "steps": {
            "step-name": {...}
        },
        "lastExecution": {...},
        "triggers": [...],
        "watchers": [...],
        "tags": [...]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/describe-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.describe_workflow(workflow_id=workflow_id)
        writer.write(response)


@app.command(short_help="Pause a scheduled workflow.")
def pause(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Pause*** a scheduled workflow.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows pause 9999
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.dev.peak.ai/workflows/api-docs/index.htm#/Workflows/post_api_v1_workflows__workflowId__pause)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.pause_workflow(workflow_id=workflow_id)

        writer.write(response)


@app.command(short_help="Resume a paused workflow.")
def resume(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Resume*** a paused workflow.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows resume 9999
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.dev.peak.ai/workflows/api-docs/index.htm#/Workflows/post_api_v1_workflows__workflowId__resume)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.resume_workflow(workflow_id=workflow_id)
        writer.write(response)


@app.command(short_help="Delete a workflow.")
def delete(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** a workflow.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows delete 9999
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/delete-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.delete_workflow(workflow_id=workflow_id)
        writer.write(response)


@app.command(short_help="Start a workflow run.")
def execute(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    file: Annotated[Optional[str], args.TEMPLATE_PATH] = None,
    params_file: str = args.TEMPLATE_PARAMS_FILE,
    params: List[str] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Start*** a workflow run. This allows you to pass dynamic parameters to the workflow while running it.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        params (map | required: false):
            global (map | required: false):
                <keyName> (string | required: false): Key-Value pair. Key is the name of the param which and value is the value of the param.
            stepWise (map | required: false):
                <stepName> (map | required: false): # Parameters to be passed to the step with name `stepName`.
                    <keyName> (string | required: false): Key-Value pair. Key is the name of the param which and value is the value of the param.
        stepsToRun (list(map) | required: false):
            - stepName (string): Name of the step to be executed.
              runDAG (boolean | required: false): Whether to run the dependent steps.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak workflows execute 9999 /path/to/file.yml -v /path/to/params.yml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "executionId": "d6116a56-6b1d-41b4-a599-fb949f08863f"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/execute-workflow)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response: Dict[str, str] = {}

        if file:
            body: Dict[str, Any] = helpers.template_handler(file=file, params_file=params_file, params=params)
            body = helpers.remove_unknown_args(body, workflow_client.execute_workflow)

            response = workflow_client.execute_workflow(workflow_id=workflow_id, **body)
        else:
            response = workflow_client.execute_workflow(workflow_id=workflow_id)

        writer.write(response)


@app.command(short_help="List all available resources.")
def list_resources(
    ctx: typer.Context,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all available resources that can be used in workflow steps.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows list-resources
    ```

    \b
    🆗 ***Response:***
    ```json
    [
        {
            "cpu": 0.25,
            "gpu": null,
            "gpuMemory": null,
            "id": 21,
            "memory": 0.5
        }
    ]
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Resources/get-resources)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.list_resources()
        writer.write(response)


@app.command(short_help="List default resources.")
def list_default_resources(
    ctx: typer.Context,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** default resources for the workflows.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows list-default-resources
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "instanceTypeId": 21,
        "storage": "10GB"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Resources/get-default-resources)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.get_default_resource()
        writer.write(response)


@app.command(short_help="List executions for the given workflow.")
def list_executions(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID,
    date_from: Optional[str] = args.DATE_FROM,
    date_to: Optional[str] = args.DATE_TO,
    status: Optional[List[str]] = _EXECUTION_STATUS,
    count: Optional[int] = _COUNT,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** executions for the given workflow.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows list-executions 9999 --page-size 10 --page-number 1 --status "Running" --status "Failed"
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "executions": [...],
        "pageSize": 25,
        "pageNumber": 1,
        "pageCount": 1,
        "workflowId": 11876
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Executions/get-workflow-executions)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.list_executions(
            workflow_id=workflow_id,
            date_from=date_from,
            date_to=date_to,
            status=parse_list_of_strings(status),
            count=count,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Get workflow execution logs.")
def get_execution_logs(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID_OPTION,
    execution_id: str = _EXECUTION_ID,
    step_name: str = _STEP_NAME,
    next_token: Optional[str] = args.NEXT_TOKEN,
    follow: Optional[bool] = args.FOLLOW,
    save: Optional[bool] = args.SAVE,
    file_name: Optional[str] = args.FILE_NAME,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesOnlyJson] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** execution logs for a specific workflow step.

    \b
    If you want to save the logs to a file, you can use the `--save` flag.
    If you don't provide a file name, the logs will be saved to a file with the name `workflow_execution_logs_<workflow_id>_<execution_id>_<step_name>.log`.

    \b
    If you want to view next set of logs you can pass in the `nextToken` to the command.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows get-execution-logs --workflow-id <workflow_id> --execution-id <execution_id> --step-name <step_name> --next-token <next_token>
    ```

    \b
    To follow the logs, you can use the `--follow` flag.

    \b
    📝 ***Example usage to follow the logs:***<br/>
    ```bash
    peak workflows get-execution-logs --workflow-id <workflow_id> --execution-id <execution_id> --step-name <step_name> --follow
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "stepRunStatus": "Running",
        "logs": [
            {
                "message": "Cloning into service-workflows-api...",
                "timestamp": 1697089188119
            }
        ],
        "nextToken": "f/37846375578651780454915234936364900527730394239380553728/s"
    }
    ```
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer = Writer()

    is_spoke_tenant = workflow_client.session.is_spoke_tenant

    pager = writer.pager()  # Create pager context

    with pager:
        while True:
            response = workflow_client.get_execution_logs(
                workflow_id=workflow_id,
                execution_id=execution_id,
                step_name=step_name,
                next_token=next_token,
                save=save,
                file_name=file_name,
            )

            if save or not response or "logs" not in response:
                break

            if follow:
                if (is_spoke_tenant or response["stepRunStatus"] != "Running") and (
                    response["logs"] is None or len(response["logs"]) == 0
                ):
                    break
                formatted_logs = helpers.format_logs(response["logs"])
                if len(formatted_logs):
                    writer.write(formatted_logs)
            else:
                writer.write(response)
                break

            next_token = response.get("nextToken", None)


@app.command(short_help="Get workflow execution details.")
def get_execution_details(
    ctx: typer.Context,
    workflow_id: int = _WORKFLOW_ID_OPTION,
    execution_id: str = _EXECUTION_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** execution details for a specific workflow run.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak workflows get-execution-details --workflow-id <workflow_id> --execution-id <execution_id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "steps": [...],
        "executedAt": "2020-01-01T18:00:00.000Z",
        "finishedAt": "2020-01-01T18:00:00.000Z",
        "runId": "db88c21d-1add-45dd-a72e-8c6b83b68dee",
        "status": "Success"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/workflows/api-docs/index.htm#/Executions/get-workflow-execution-details)
    """
    workflow_client: Workflow = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = workflow_client.get_execution_details(
            workflow_id=workflow_id,
            execution_id=execution_id,
        )

        writer.write(response)
