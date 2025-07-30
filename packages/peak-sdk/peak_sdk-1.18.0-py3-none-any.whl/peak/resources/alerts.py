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

"""Alerts client module."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class Alert(BaseClient):
    """Client class for interacting with alerts resource."""

    BASE_ENDPOINT = "notifications/api/v1"

    @overload
    def list_emails(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_emails(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_emails(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        count: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the history of emails sent.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/notifications/api-docs/index.htm#/emails/get_api_v1_emails>`__

        Args:
            date_from (str | None): The date after which the emails should be included (in ISO format).
                It is 90 days from current date by default.
            date_to (str | None): The date till which the emails should be included (in ISO format).
                It is current date by default.
            page_size (int | None): Number of emails to retrieve per page. It is 25 by default.
            page_number (int | None): Page number to retrieve. Only used when return_iterator is False.
            count (int | None): Number of emails required (Ordered by latest to earliest).
                For example, if 5 is provided, it will return last 5 emails.
                It is -1 by default which means it will return all the available emails within the given dates.
            return_iterator (bool): Whether to return an iterator object or list of emails for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/emails"

        params: Dict[str, Any] = {
            "dateTo": date_to,
            "dateFrom": date_from,
            "pageSize": page_size,
            "count": -1 if count is None else count,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="emails",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def send_email(
        self,
        body: Dict[str, Any],
        attachments: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Send an email to the specified recipients using the specified template.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/notifications/api-docs/index.htm#/Emails/post_api_v1_emails>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the details of the email to send.
            attachments (Optional[list[str]]): A list of file paths to attach to the email.
                When a directory is provided, a zip is automatically created for the same.

        Returns:
            Dict[str, Any]: A dictionary containing the ID of the email sent.

        SCHEMA:
            .. code-block:: json

                {
                    "recipients": ["string"],
                    "cc": ["string"],
                    "bcc": ["string"],
                    "subject": "string",
                    "templateName": "string",
                    "templateParameters": {
                        "string": "string"
                    }
                }

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given feature does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/emails"

        parsed_body = {k: json.dumps(v) if not isinstance(v, str) else v for (k, v) in body.items()}

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            body=parsed_body,
            content_type=ContentType.MULTIPART_FORM_DATA,
            path=attachments,
            file_key="attachments",
        )

    def describe_email(self, email_id: int) -> Dict[str, Any]:
        """Retrieve the details of a specific email.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/notifications/api-docs/index.htm#/Emails/get_api_v1_emails__id_>`__

        Args:
            email_id (int): The ID of the email to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the details of the email.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: Email with the given ID does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/emails/{email_id}"

        return self.session.create_request(endpoint, method, content_type=ContentType.APPLICATION_JSON)  # type: ignore[no-any-return]

    @overload
    def list_templates(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        scope: Optional[List[str]] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]: ...

    @overload
    def list_templates(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        scope: Optional[List[str]] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]: ...

    def list_templates(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        scope: Optional[List[str]] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the history of emails sent.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/notifications/api-docs/index.htm#/Templates/get_api_v1_emails_templates>`__

        Args:
            name (str | None): The name of the email template
            scope (List[str] | None): Filter out on the basis of the type of the template - global or custom.
            page_size (int | None): Number of emails to retrieve per page. It is 25 by default.
            page_number (int | None): Page number to retrieve. Only used when return_iterator is False.
            return_iterator (bool): Whether to return an iterator object or list of emails for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/emails/templates"

        params: Dict[str, Any] = {
            "searchTerm": name,
            "scope": scope,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="templates",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def describe_template(self, template_name: str) -> Dict[str, Any]:
        """Retrieve the details of a specific template.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/notifications/api-docs/index.htm#/Templates/get_api_v1_emails_templates__name_>`__

        Args:
            template_name (str): The name of the template to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the details of the template.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: Email with the given ID does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/emails/templates/{template_name}"

        return self.session.create_request(endpoint, method, content_type=ContentType.APPLICATION_JSON)  # type: ignore[no-any-return]


def get_client(session: Optional[Session] = None) -> Alert:
    """Returns a Alert client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Alert: The alert client object.
    """
    return Alert(session)


__all__ = ["get_client"]
