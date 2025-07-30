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
"""Peak deployments commands."""

from typing import List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.press.deployments import Deployment
from rich.console import Console

app = typer.Typer(
    help="Manage both Block and App deployments.",
    short_help="Manage both Block and App deployments.",
)
console = Console()

_DEPLOYMENT_ID = typer.Argument(..., help="ID of the Block deployment to be used in this operation")


@app.command("list", short_help="List App and Block deployments.")
def list_deployments(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = args.STATUS_FILTER_DEPLOYMENTS,
    kind: Optional[str] = args.KIND_FILTER,
    term: Optional[str] = args.TERM_FILTER,
    sort: Optional[List[str]] = args.SORT_KEYS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all the App and Block deployments that have been created for the tenant.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak deployments list --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "deploymentCount": 1,
        "deployments": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Deployments/get_v1_deployments)
    """
    deployment_client: Deployment = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = deployment_client.list_deployments(
            status=status,
            kind=kind,
            term=term,
            sort=sort,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Execute the resources of an app or block deployment")
def execute_resources(
    ctx: typer.Context,
    deployment_id: str = typer.Argument(..., help="ID of the app or block deployment to execute resources for."),
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Execute*** the resources of an app or block deployment. This will execute the resources of the latest revision of the deployment for which `autoRunOnDeploy` property is enabled.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak deployments execute-resources <deployment_id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "executeResponse": [
            {
                "blockSpecId": "0bddb4c6-40c5-45c3-b477-fceb2c051609",
                "version": "1.0.0",
                "executionId": "a3e77006-86f3-4829-8c43-f21ad462dbbd",
                "status": "executed"
            }
        ]
    }
    ```
    """
    deployment_client: Deployment = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = deployment_client.execute_resources(deployment_id)
        writer.write(response)


@app.command(short_help="Update the runtime parameters for a deployment.")
def patch_parameters(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    file: str = args.TEMPLATE_PATH,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** the parameters for a deployment at run time.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
    body (map): Dictionary of parameters specific to the 'run' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak deployments patch-parameters <deployment-id> /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    {...}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/patch_v1_deployments__deploymentId__parameters_run)
    """
    body = helpers.template_handler(file, params_file, params)
    deployments_client: Deployment = ctx.obj["client"]
    body = helpers.remove_unknown_args(body, deployments_client.patch_parameters)
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = deployments_client.patch_parameters(deployment_id, **body)
        writer.write(response)


@app.command(short_help="Update the App runtime parameters and Block runtime parameters for a deployment.")
def patch_parameters_v2(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    file: str = args.TEMPLATE_PATH,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** the parameters for a deployment at runtime.

    \b
    🧩 ***Input file schema to update run parameters of an app deployment (yaml):***<br/>
    ```yaml
    body (map):
        appParameters (map | required: false):
            Dictionary of runtime app parameters. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
        parameters (map | required: false):
            <blockName> (map): Dictionary of parameters specific to each block, where each key represents the block name.
                Dictionary of runtime block parameters. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
    ```

    🧩 ***Input file schema to update run parameters of a block deployment (yaml):***<br/>
    ```yaml
    body (map):
        parameters (map | required: false):
            Dictionary of runtime block parameters. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak deployments patch-parameters-v2 <deployment-id> /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    { appParameters: {...}, parameters: {...} }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/patch_v2_deployments__deploymentId__parameters_run)
    """
    body = helpers.template_handler(file, params_file, params)
    deployments_client: Deployment = ctx.obj["client"]
    body = helpers.remove_unknown_args(body, deployments_client.patch_parameters_v2)
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = deployments_client.patch_parameters_v2(deployment_id, **body)
        writer.write(response)
