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
"""Peak specs commands."""
from typing import List, Optional

import typer
from peak.cli import args
from peak.cli.args import OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes
from peak.output import Writer
from peak.press.specs import Spec
from rich.console import Console

app = typer.Typer(
    help="Manage both Block and App specs.",
    short_help="Manage both Block and App specs.",
)
console = Console()

RELEASE_VERSION = typer.Option(None, help="The release version of the spec in valid semantic versioning format.")


@app.command("list", short_help="List App and Block specs.")
def list_specs(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = args.STATUS_FILTER_SPECS,
    kind: Optional[str] = args.KIND_FILTER,
    term: Optional[str] = args.TERM_FILTER,
    sort: Optional[List[str]] = args.SORT_KEYS,
    scope: Optional[List[str]] = args.SCOPES,
    featured: Optional[bool] = args.FEATURED,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all the App and Block specs that exists for the tenant.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak specs list --featured --page-size 10 --page-number 1
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

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Specs/get_v1_specs)
    """
    spec_client: Spec = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = spec_client.list_specs(
            status=status,
            featured=featured,
            kind=kind,
            term=term,
            sort=sort,
            scope=scope,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="List deployments for a spec release.")
def list_release_deployments(
    ctx: typer.Context,
    spec_id: str = args.SPEC_ID,
    version: Optional[str] = RELEASE_VERSION,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = args.STATUS_FILTER_SPEC_RELEASES,
    name: Optional[str] = args.NAME_FILTER,
    title: Optional[str] = args.TITLE_FILTER,
    sort: Optional[List[str]] = args.SORT_KEYS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all the deployments for a given spec. Version is optional and if not provided, all deployments for the spec will be returned.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak specs list-release-deployments --spec-id "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --status deployed,failed --version 1.0.0
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "deploymentCount": 1,
        "deployments": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10,
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Specs/get_v1_specs__specId__releases__version__deployments)
    """
    spec_client: Spec = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = spec_client.list_spec_release_deployments(
            spec_id=spec_id,
            version=version,
            status=status,
            name=name,
            title=title,
            sort=sort,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)
