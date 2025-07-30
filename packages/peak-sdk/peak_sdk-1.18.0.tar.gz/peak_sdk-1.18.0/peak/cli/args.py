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
"""CLI arguments."""

import typer
from peak.callbacks import dry_run, generate_yaml, handle_output, paging
from peak.cli.version import display_version
from peak.constants import OutputTypes

VERSION_OPTION = typer.Option(False, "--version", callback=display_version, is_eager=True)

TEMPLATE_PATH = typer.Argument(
    ...,
    help="""
        Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.
    """,
)

TEMPLATE_DESCRIPTION_FILE = typer.Option(
    None,
    "--desc-file",
    "-d",
    help="""
        Path to the file that defines the description for this operation, supports `md`, and `txt` files only.
    """,
)

TEMPLATE_PARAMS_FILE = typer.Option(
    None,
    "--params-file",
    "-v",
    help="Path to the `yaml` file containing the parameter values map for the template file.",
)

TEMPLATE_PARAMS = typer.Option(
    None,
    "--params",
    "-p",
    help="Parameters to be used with the template file. Overrides the parameters in the params file. Parameters should be in the format `key=value`.",
)

PAGE_NUMBER = typer.Option(None, help="The page number to retrieve.")

PAGE_SIZE = typer.Option(None, help="Number of entities to include per page.")

DATE_FROM = typer.Option(None, help="The date after which the entities should be included (in ISO format).")

DATE_TO = typer.Option(None, help="The date till which the entities should be included (in ISO format).")

IMAGE_ID = typer.Option(..., help="ID of the image to be used in this operation.")

VERSION_ID = typer.Option(..., help="ID of the version to be used in this operation.")

SPEC_ID = typer.Option(..., help="ID of the spec to be used in this operation.")

DEPLOYMENT_ID = typer.Option(..., help="ID of the deployment to be used in this operation.")

RELEASE_VERSION = typer.Option(..., help="Release version to be used in this operation.")

REVISION = typer.Option(..., help="Revision number of the Block deployment revision to be used in this operation")

SORT_KEYS = typer.Option(
    None,
    help="A comma-separated list of fields to order results by, in the format \\<field\\>:\\<order\\>.",
)

STATUS_FILTER_SPECS = typer.Option(
    None,
    help="A comma-separated list of statuses to filter specs. Valid values are `available`, `unavailable` and `archived`.",
)

STATUS_FILTER_SPEC_RELEASES = typer.Option(
    None,
    help="A comma-separated list of statuses to filter spec releases. Valid values are `deleting`, `delete_failed`, `deployed`, `deploying`, `failed`, `platform_resource_error`, `redeploying`, `rollback`, `rollback_complete`, `rollback_failed` and `warning`.",
)

STATUS_FILTER_DEPLOYMENTS = typer.Option(
    None,
    help="A comma-separated list of statuses to filter deployments. Valid values are `deploying`, `deployed`, `deleting`, `delete_failed`, `failed`, `platform_resource_error`, `redeploying`, `rollback`, `rollback_complete`, `rollback_failed`, and `warning`.",
)

STATUS_FILTER_DEPLOYMENT_REVISIONS = typer.Option(
    None,
    help="A comma-separated list of statuses to filter deployments. Valid values are `deleting`, `delete_failed`, `deployed`, `deploying`, `failed`, `platform_resource_error`, `rollback`, `rollback_complete`, `rollback_failed` and `superseded`",
)


NAME_FILTER = typer.Option(None, help="Only return entities whose names begins with the query string.")

TITLE_FILTER = typer.Option(None, help="Only return entities whose title begins with the query string.")

SCOPES = typer.Option(None, help="A comma-separated list of scopes to only return entities of those scopes.")

FEATURED = typer.Option(None, "--featured", help="Whether to only return featured entities.")

KIND_FILTER = typer.Option(None, help="Only return entities with the kind specified.")

TERM_FILTER = typer.Option(
    None,
    help="Only return entities which contain the term in name, title, description or summary.",
)

DRY_RUN = typer.Option(
    False,
    "--dry-run",
    help="If set, prints the debug information instead of sending the actual request.",
    callback=dry_run,
)

PAGING = typer.Option(
    False,
    "--paging",
    help="If set, prints the output using the default pager.",
    callback=paging,
)

OUTPUT_TYPES = typer.Option(
    OutputTypes.json,
    "--output",
    "-o",
    help="The output format to display data in.",
    callback=handle_output,
)

GENERATE_YAML = typer.Option(
    False,
    "--generate",
    help="Generate Sample YAML that can be used in this operation.",
    callback=generate_yaml,
)

NEXT_TOKEN = typer.Option(None, help="The token to retrieve the next set of logs.")

FOLLOW = typer.Option(False, help="Whether to follow the logs.")

SAVE = typer.Option(
    False,
    help="If set, saves the logs locally to log file.",
)

FILE_NAME = typer.Option(
    None,
    help="Name or path of the file to save the logs.",
)

RELEASE_NOTES_FILE = typer.Option(
    None,
    "--release-notes-file",
    "-n",
    help="""
        Path to the file that defines the release notes for this operation, supports `md`, and `txt` files only.
    """,
)

REVISION_NOTES_FILE = typer.Option(
    None,
    "--revision-notes-file",
    "-n",
    help="""
        Path to the file that defines the revision notes for this operation, supports `md`, and `txt` files only.
    """,
)
