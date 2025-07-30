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
"""Peak Tenants service commands."""
from typing import Optional

import typer
from peak.cli.args import OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.resources.tenants import Tenant

app = typer.Typer(
    help="Manage tenant settings and quota.",
    short_help="Create and manage Tenant Settings.",
)

_ENTITY_TYPE = typer.Option(
    ...,
    help="Entity type to be used in this operation (e.g. - `workflow`, `webapp`, `api-deployment`).",
)

_DATA_STORE_TYPE = typer.Option(
    None,
    help="Data store type. The only allowed values is data-warehouse.",
)


@app.command(
    "list-instance-options",
    short_help="List tenant instance options.",
)
def list_instance_options(
    ctx: typer.Context,
    entity_type: str = _ENTITY_TYPE,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all available instance options for a tenant.

    \b
    📝 ***Example Usage:***<br/>
    ```bash
    peak tenants list-instance-options --entity-type workflow
    ```

    \b
    🆗 ***Response:***
    ```json
    {
      "data": [
        {
          "cpu": 125,
          "gpu": null,
          "gpuMemory": null,
          "id": 20,
          "instanceClass": "General Purpose",
          "memory": 125,
          "name": "Pico (0.125CPU, 0.125GB RAM)",
          "provider": "k8s",
          "providerInstanceId": null
        }
      ]
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/quota/api-docs/index.htm#/settings/get_api_v1_settings_tenant_instance_options)
    """
    tenants_client: Tenant = ctx.obj["client"]
    writer = Writer()

    with writer.pager():
        response = tenants_client.list_instance_options(entity_type=entity_type)
        writer.write(response)


@app.command(
    short_help="Get credentails for a data store.",
)
def get_credentials(
    ctx: typer.Context,
    data_store_type: Optional[str] = _DATA_STORE_TYPE,
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** credentials for the given data store type.

    \b
    📝 ***Example Usage:***<br/>
    ```bash
    peak tenants get-credentials --data-store-type data-warehouse
    ```

    \b
    🆗 ***Response:***
    ```json
    {
      "application": "application",
      "connectionString": "snowflake://host/database?authenticator=OAUTH&token=generated-access-token",
      "integration": "integration_name",
      "port": 443,
      "role": "role_name",
      "schema": "schema",
      "warehouse": "warehouse",
      "accessToken": "generated-access-token",
      "authType": "oauth",
      "database": "database",
      "host": "host",
      "dataWarehouseType": "snowflake"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/connections/api-docs/index.htm#/connections/get_api_v1_connections_credentials)
    """
    tenants_client: Tenant = ctx.obj["client"]
    writer = Writer()

    with writer.pager():
        response = tenants_client.get_credentials(data_store_type=data_store_type)
        writer.write(response)
