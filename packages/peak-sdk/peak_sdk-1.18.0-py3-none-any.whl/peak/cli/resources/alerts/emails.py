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

"""Peak Alerts commands."""

from typing import Any, Dict, List, Optional

import typer
from peak.cli import helpers
from peak.cli.args import OUTPUT_TYPES, PAGING, TEMPLATE_PARAMS, TEMPLATE_PARAMS_FILE
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.helpers import combine_dictionaries, map_user_options, parse_list_of_strings, variables_to_dict
from peak.output import Writer
from peak.resources.alerts import Alert
from typing_extensions import Annotated

app = typer.Typer(
    help="Alerts management commands.",
    short_help="Manage alerts.",
)

_EMAIL_ID = typer.Argument(..., help="The ID of the email.")
_RECIPIENTS = typer.Option(None, help="The email addresses of the recipients.")
_SUBJECT = typer.Option(None, help="The subject of the email.")
_TEMPLATE_NAME = typer.Option(None, help="The name of the email template.")
_TEMPLATE_PARAMETERS = typer.Option(
    None,
    help="The parameters for the email template. To be passed in stringified JSON format.",
)
_COUNT = typer.Option(None, help="The number of emails to retrieve.")
_DATE_FROM = typer.Option(None, help="The date from which to retrieve emails (in ISO format).")
_DATE_TO = typer.Option(None, help="The date till which to retrieve emails (in ISO format).")
_PAGE_SIZE = typer.Option(None, help="The number of emails per page.")
_PAGE_NUMBER = typer.Option(None, help="The page number to retrieve.")
_CC = typer.Option(None, help="The email addresses of the recipients to be CC'd.")
_BCC = typer.Option(None, help="The email addresses of the recipients to be BCC'd.")
_LIST_TEMPLATE_NAME = typer.Option(None, help="Email Template Name to search for.")
_LIST_TEMPLATE_SCOPE = typer.Option(None, help="List of type of template to filter the templates by.")
_DESCRIBE_TEMPLATE_NAME = typer.Argument(None, help="The name of the email template.")
_ATTACHMENTS = typer.Option(None, help="The path of files to be sent as the mail attachments.")


@app.command("list", short_help="List all emails.")
def list_emails(
    ctx: typer.Context,
    page_size: Optional[int] = _PAGE_SIZE,
    page_number: Optional[int] = _PAGE_NUMBER,
    count: Optional[int] = _COUNT,
    date_from: Optional[str] = _DATE_FROM,
    date_to: Optional[str] = _DATE_TO,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """Retrieve the history of emails sent.

    \b
    📝 ***Example usage:***
    ```bash
    peak alerts emails list --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "emailCount": 1,
        "emails": [
            {
                "createdAt": "2024-01-01T00:00:00.200Z",
                "createdBy": "platform@peak.ai",
                "id": 1,
                "status": "Delivered",
                "subject": "email_subject",
                "templateName": "template_name",
            }
        ],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/notifications/api-docs/index.htm#/Emails/get_api_v1_emails)
    """
    alert_client: Alert = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = alert_client.list_emails(
            page_size=page_size,
            page_number=page_number,
            count=count,
            date_from=date_from,
            date_to=date_to,
            return_iterator=False,
        )
        writer.write(response)


@app.command("send", short_help="Send an email.")
def send_email(
    ctx: typer.Context,
    file: Annotated[
        Optional[str],
        typer.Argument(
            ...,
            help="Path to the file that defines the body for this operation, supports both `yaml` file or a `jinja` template.",
        ),
    ] = None,
    params_file: str = TEMPLATE_PARAMS_FILE,
    params: List[str] = TEMPLATE_PARAMS,
    recipients: Optional[List[str]] = _RECIPIENTS,
    cc: Optional[List[str]] = _CC,
    bcc: Optional[List[str]] = _BCC,
    subject: Optional[str] = _SUBJECT,
    template_name: Optional[str] = _TEMPLATE_NAME,
    template_parameters: Optional[str] = _TEMPLATE_PARAMETERS,
    attachments: Optional[List[str]] = _ATTACHMENTS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """Send an email to the specified recipients using the specified template.

    \b
    🧩 ***Input file schema(yaml):***<br/>
    ```yaml
      body (map):
        recipients (list(str) | required: true): List of email addresses of the recipients.
        cc (list(str) | required: false): List of email addresses of the recipients to be CC'd.
        bcc (list(str) | required: false): List of email addresses of the recipients to be BCC'd.
        subject (str | required: true): The subject of the email.
        templateName (str | required: true): The name of the email template.
        templateParameters (map | required: false): The parameters for the email template.
        attachments (list(str) | required: false): The path of files to be sent as email attachments. A maximum of 3 files can be included, with each file not exceeding 10 MB. Supported file formats are: .pdf, .docx, .doc, .csv, .txt, .xlsx, .xls, and .zip.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak alerts emails send '/path/to/email.yaml' --params-file '/path/to/values.yaml'
    ```

    We can also provide the required parameters from the command line or combine the YAML template and command line arguments in which case the command line arguments will take precedence.

    \b
    📝 ***Example usage without yaml:***
    ```bash
    peak alerts emails send --recipients <recipient_email_1> --recipients <recipient_email_2> --subject <email_subject> --template-name <template_name> --template-parameters '{"key": "value"}' --attachments model.txt --attachments outputs
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": 1
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/notifications/api-docs/index.htm#/Emails/post_api_v1_emails)
    """
    alert_client: Alert = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    user_options: Dict[str, Any] = variables_to_dict(
        recipients,
        cc,
        bcc,
        subject,
        template_name,
        template_parameters,
    )

    body: Dict[str, Any] = {}
    if file:
        body = helpers.template_handler(file=file, params_file=params_file, params=params)
        body = helpers.remove_unknown_args(body, alert_client.send_email)

    updated_body = combine_dictionaries(body.get("body") or {}, user_options)
    final_attachments = body.get("attachments", attachments)

    if recipients:
        updated_body["recipients"] = parse_list_of_strings(recipients)

    if cc:
        updated_body["cc"] = parse_list_of_strings(cc)

    if bcc:
        updated_body["bcc"] = parse_list_of_strings(bcc)

    if template_parameters:
        updated_body["templateParameters"] = map_user_options(
            user_options=user_options,
            mapping={},
            dict_type_keys=["templateParameters"],
        )

    with writer.pager():
        response: Dict[str, Any] = alert_client.send_email(body=updated_body, attachments=final_attachments)
        writer.write(response)


@app.command(short_help="Describe details of a specific email.")
def describe(
    ctx: typer.Context,
    email_id: int = _EMAIL_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details of a specific email.

    \b
    📝 ***Example usage:***
    ```bash
    peak alerts emails describe <email-id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "createdAt": "2024-01-01T00:00:00.000Z",
        "createdBy": "platform@peak.ai",
        "deliveredAt": "2024-01-01T00:00:00.000Z",
        "id": 1,
        "recipients": {
            "cc": [],
            "to": ["someone@peak.ai"],
            "bcc": []
        },
        "status": "Delivered",
        "statusDetails": [
            {
                "email": "someone@peak.ai",
                "status": "Delivered",
                "description": "The email was successfully delivered."
            }
        ],
        "subject": "Hello, world!",
        "templateName": "template_name"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/notifications/api-docs/index.htm#/Emails/get_api_v1_emails__id_)
    """
    alert_client: Alert = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = alert_client.describe_email(email_id=email_id)
        writer.write(response)


@app.command(short_help="List all the templates.")
def list_templates(
    ctx: typer.Context,
    page_size: Optional[int] = _PAGE_SIZE,
    page_number: Optional[int] = _PAGE_NUMBER,
    scope: Optional[List[str]] = _LIST_TEMPLATE_SCOPE,
    name: Optional[str] = _LIST_TEMPLATE_NAME,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """Retrieve the email templates list.

    \b
    📝 ***Example usage:***
    ```bash
    peak alerts emails list-templates --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "templateCount": 1,
        "templates": [
            {
                "id": 1,
                "createdAt": "2021-09-01T12:00:00Z",
                "createdBy": "platform@peak.ai",
                "name": "test_template",
                "scope": "custom"
            }
        ],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/notifications/api-docs/index.htm#/Templates/get_api_v1_emails_templates)
    """
    alert_client: Alert = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = alert_client.list_templates(
            page_size=page_size,
            page_number=page_number,
            scope=scope,
            name=name,
            return_iterator=False,
        )
        writer.write(response)


@app.command(
    short_help="Describe details of a specific template.",
)
def describe_template(
    ctx: typer.Context,
    template_name: str = _DESCRIBE_TEMPLATE_NAME,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** details of a specific template.

    \b
    📝 ***Example usage:***
    ```bash
    peak alerts emails describe-template <template-name>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": 1,
        "createdAt": "2021-09-01T12:00:00Z",
        "createdBy": "platform@peak.ai",
        "name": "test_template",
        "subject": "Important Account Update Information",
        "body": "<h1>Hello</h1><p>Your account has been updated.</p>",
        "scope": "custom"
    }
    ```

    🔗 [**API Documentation**](https://service.peak.ai/notifications/api-docs/index.htm#/Templates/get_api_v1_emails_templates__name_)
    """
    alert_client: Alert = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = alert_client.describe_template(template_name=template_name)
        writer.write(response)
