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
"""Peak Users commands."""
from typing import Optional

import typer
from peak import Session
from peak.cli.args import OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.resources import users

app = typer.Typer(
    help="User management and permission checking.",
    short_help="Manage User Permissions.",
)

_FEATURE = typer.Option(..., help="The feature path to check permissions for, e.g., 'PRICING.GUARDRAILS'.")
_ACTION = typer.Option(..., help="The action to check for the feature path, e.g., 'read' or 'write'.")
_AUTH_TOKEN = typer.Option(
    None,
    help="Authentication token for the user. If not provided, the token from the environment will be used.",
)


@app.command(short_help="Check user permission for a specific feature.")
def check_permission(
    ctx: typer.Context,
    feature: str = _FEATURE,
    action: str = _ACTION,
    auth_token: Optional[str] = _AUTH_TOKEN,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """Check if the user has the specified permission for the given feature path.

    \b
    📝 ***Example usage:***
    ```bash
    peak user check-permission --feature "PRICING.GUARDRAILS" --action "read" --auth-token <your-auth-token>
    ```

    \b
    🆗 ***Response:***
    True if the user has the permission, False otherwise.
    """
    user_session = Session(auth_token=auth_token)
    user_client = users.get_client(session=user_session)
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = user_client.check_permissions({feature: action})
        writer.write(response.get(feature, False), output_type=OutputTypes.json)
