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
"""Handler for sending requests to the API."""

from __future__ import annotations

import contextlib
import json
import mimetypes
from abc import ABC, ABCMeta, abstractmethod
from io import BufferedReader
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import Any, Callable, ClassVar, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

import requests
from requests.adapters import HTTPAdapter
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor, user_agent
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from urllib3.util import Retry

import peak.config
from peak.compression import compress, get_files_to_include, print_file_tree
from peak.constants import ContentType, HttpMethods
from peak.exceptions import BaseHttpException, PayloadTooLargeException
from peak.output import Writer
from peak.telemetry import telemetry
from peak.validators import check_file_size

from ._version import __version__

T = TypeVar("T")
Serializable = Dict[str, Union[str, int, float, bool]]
OptionalSerializable = Optional[Serializable]
writer = Writer(ignore_debug_mode=True)


class HandlerRegistryMeta(type):
    """Metaclass for registering all types of Handler classes."""

    REGISTRY: ClassVar[Dict[ContentType, BaseHandler]] = {}

    def __new__(
        cls: "Type[HandlerRegistryMeta]",
        name: str,
        bases: Tuple[Any, ...],
        attrs: Dict[str, Any],
    ) -> HandlerRegistryMeta:
        """This method runs whenever a new class (that uses this class as its metaclass) is defined.

        This method automatically adds the handler classes to its Registry.
        It uses the `CONTENT_TYPE` attribute of the class as key and the class itself as value in registry.
        Ref: https://charlesreid1.github.io/python-patterns-the-registry.html

        Args:
            name (str): Name of the child class
            bases (tuple): Tuple of the child class's inheritance tree
            attrs (dict): Name and value pairs of all the attributes defined in the child class

        Returns:
            HandlerRegistryMeta: the class itself, forward annotated for type checking

        Raises:
            TypeError: if the child class does not have a `CONTENT_TYPE` attribute
        """
        error_invalid_content_type: str = f"Invalid content type for {name} handler"
        new_cls: "HandlerRegistryMeta" = type.__new__(cls, name, bases, attrs)

        content_type: Optional[ContentType] = attrs.get("CONTENT_TYPE")
        try:
            if content_type and ContentType(content_type):
                cls.REGISTRY[content_type] = new_cls()
        except ValueError as err:
            raise TypeError(error_invalid_content_type) from err
        else:
            return new_cls


class _CombinedMeta(HandlerRegistryMeta, ABCMeta):
    """Utility class for combining multiple meta-classes."""


class AuthRetrySession(requests.Session):
    """Session with retries."""

    _DEFAULT_RETRY_CONFIG: ClassVar[Dict[str, Any]] = {
        "backoff_factor": 2,
        "total": 3,
        "status_forcelist": [429, 500, 502, 503, 504],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
    }

    def _add_retries(self, retry_config: Optional[Dict[str, Any]] = None) -> None:
        if retry_config is None:
            retry_config = self._DEFAULT_RETRY_CONFIG
        adapter = HTTPAdapter(max_retries=Retry(**retry_config))
        self.mount("http://", adapter=adapter)
        self.mount("https://", adapter=adapter)


class HandlerUtils(AuthRetrySession):
    """Utility class for handling requests."""

    @contextlib.contextmanager
    def make_artifact(
        self,
        path: Optional[str | list[str]],
        body: Dict[str, Any],
        ignore_files: Optional[list[str]],
        file_key: Optional[str] = "artifact",
    ) -> Iterator[MultipartEncoderMonitor]:
        """Create a multipart/form-data encoded file with given body and path as file.

        Args:
            path (Optional[str]): path to the file or folder that will be compressed and used as artifact
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact
            body (Dict[str, Any]): body content to be sent with artifact
            file_key (Optional[str]): the field in which the files must be uploaded

        Yields:
            MultipartEncoderMonitor: MultipartEncoderMonitor generator object
        """
        if path:
            with contextlib.ExitStack() as stack:
                files: list[tuple[str, SpooledTemporaryFile[bytes] | BufferedReader, str | None]] = []
                if isinstance(path, list):
                    for p in path:
                        file_path = Path(p)
                        if file_path.is_dir():
                            context = compress(p)
                            compressed_file = stack.enter_context(context)
                            file_name = f"{file_path.name}.zip"
                            files.append((file_name, compressed_file, "application/zip"))
                        else:
                            fh = open(p, "rb")  # noqa: SIM115, PTH123
                            stack.push(fh)
                            file_name = file_path.name
                            files.append((file_name, fh, mimetypes.guess_type(file_name)[0]))
                else:
                    context = compress(path, ignore_files)
                    file = stack.enter_context(context)
                    check_file_size(file)
                    files.append(
                        (
                            "artifact.zip",
                            file,
                            "application/zip",
                        ),
                    )

                files_object = [(file_key, file) for file in files]
                body_array = list(body.items())

                encoder = MultipartEncoder(
                    files_object + body_array,
                )

                callback = self._default_callback(encoder)
                monitor = MultipartEncoderMonitor(encoder, callback)
                yield monitor
        else:
            encoder = MultipartEncoder({**body})
            monitor = MultipartEncoderMonitor(encoder)
            yield monitor

    make_artifact.__annotations__["return"] = contextlib.AbstractContextManager

    def _default_callback(self, encoder: MultipartEncoder) -> Callable[[MultipartEncoderMonitor], None]:
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )
        progress.start()
        bar = progress.add_task("[green]Uploading", total=encoder.len)

        def callback(monitor: MultipartEncoderMonitor) -> None:
            progress.update(bar, completed=monitor.bytes_read, refresh=True)
            progress.refresh()
            if monitor.bytes_read >= monitor.len:
                progress.stop()
                progress.console.clear_live()

        return callback

    @staticmethod
    def parse_args(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Parse arguments dict and remove the parameters whose values are not provided.

        Args:
            arguments (Dict[str, Any]): dictionary of arguments

        Returns:
            Dict[str, Any]: filtered dictionary where value is not None
        """
        return {k: v for k, v in arguments.items() if v is not None}

    @staticmethod
    def handle_response(response: requests.Response) -> requests.Response:
        """Handles the response from the API.

        Args:
            response (requests.Response): response object from the API

        Returns:
            requests.Response: response of the request.

        # noqa: DAR401
        Raises:
            BaseHttpException: The HTTP exception based on status code
        """
        if 200 <= response.status_code < 300:  # noqa: PLR2004
            return response

        if response.status_code == 413:  # noqa: PLR2004
            raise PayloadTooLargeException(response.json().get("detail", ""))

        error_response = response.text
        with contextlib.suppress(Exception):
            error_response = response.json()

        raise BaseHttpException.REGISTRY[response.status_code](error_response)


class BaseHandler(ABC, HandlerUtils, metaclass=_CombinedMeta):
    """Abstract base class for all handler type classes."""

    CONTENT_TYPE: ClassVar[ContentType]

    @abstractmethod
    def handle(
        self,
        url: str,
        method: HttpMethods,
        *,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        body: Optional[Dict[str, Any]],
        path: Optional[str | list[str]],
        ignore_files: Optional[list[str]],
        request_kwargs: OptionalSerializable,
        file_key: Optional[str],
    ) -> requests.Response:
        """Placeholder handle method."""
        ...


class MultipartFormDataHandler(BaseHandler):
    """Handles requests with multipart/form-data content type."""

    CONTENT_TYPE = ContentType.MULTIPART_FORM_DATA

    def handle(
        self,
        url: str,
        method: HttpMethods,
        *,
        path: Optional[str | list[str]],
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
        ignore_files: Optional[list[str]] = None,
        file_key: Optional[str] = "artifact",
        request_kwargs: OptionalSerializable = None,
    ) -> requests.Response:
        """Handle multipart/form-data requests.

        Args:
            url (str): url to send the request to
            method (HttpMethods): method to use for the request, e.g. get, post, put, delete
            headers (Dict[str, str]): headers to send with the request
            params (Dict[str, Any]): params to send to the request, not used for multipart/form-data
            body (Dict[str, Any]): body to send to the request
            path (Optional[str]): path to the file or folder that will be compressed and used as artifact
            request_kwargs (OptionalSerializable): extra arguments to be passed when making the request, defaults to None
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact
            file_key (Optional[str]): the field in which the files must be uploaded

        Returns:
            requests.Response: response of the request
        """
        self._add_retries()

        with self.make_artifact(path, self.parse_args(body or {}), ignore_files, file_key) as monitor:
            headers = {**headers, "Content-Type": monitor.content_type}
            response: Any = getattr(self, method.value)(url, data=monitor, headers=headers, **request_kwargs)
        return self.handle_response(response)


class ApplicationJsonHandler(BaseHandler):
    """Handles requests with application/json content type."""

    CONTENT_TYPE = ContentType.APPLICATION_JSON

    def handle(
        self,
        url: str,
        method: HttpMethods,
        *,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        body: Optional[Dict[str, Any]],
        path: Optional[str | list[str]] = None,  # noqa: ARG002
        ignore_files: Optional[list[str]] = None,  # noqa: ARG002
        file_key: Optional[str] = "artifact",  # noqa: ARG002
        request_kwargs: OptionalSerializable = None,
    ) -> requests.Response:
        """Handle application/json requests.

        Args:
            url (str): url to send the request to
            method (HttpMethods): method to use for the request, e.g. get, post, put, delete
            headers (Dict[str, str]): headers to send with the request
            params (Dict[str, Any]): params to send to the request
            body (Dict[str, Any]): body to send to the request
            path (Optional[str]): path to the file or folder that will be compressed and used as artifact, not used in application/json handler
            request_kwargs (OptionalSerializable): extra arguments to be passed when making the request, defaults to None
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact
            file_key (Optional[str]): the field in which the files must be uploaded

        Returns:
            requests.Response: response of the request.
        """
        self._add_retries()

        headers = {**headers, "Content-Type": self.CONTENT_TYPE.value}
        response: Any = getattr(self, method.value)(
            url,
            params=self.parse_args(params or {}),
            json=body,
            headers=headers,
            **request_kwargs,
        )
        return self.handle_response(response)


class Handler:
    """Handler class to handle requests to the API."""

    USER_AGENT: str = user_agent(__package__ or __name__, __version__)

    @staticmethod
    def _pretty_print_request(
        *_: Any,
        content_type: str,
        path: Optional[str | list[str]] = None,
        ignore_files: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        writer.write(f"\nSample request: {json.dumps(kwargs, indent=2)}\n")
        if content_type == ContentType.MULTIPART_FORM_DATA.value and path is not None:
            writer.write("\nArtifact file tree:")
            if isinstance(path, list):
                for p in path:
                    print_file_tree(get_files_to_include(p, ignore_files))
            else:
                print_file_tree(get_files_to_include(path, ignore_files))

    @telemetry
    def make_request(
        self,
        url: str,
        method: HttpMethods,
        content_type: ContentType,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        path: Optional[str | list[str]] = None,
        request_kwargs: Optional[Dict[str, int | bool | str | float]] = None,
        ignore_files: Optional[list[str]] = None,
        file_key: Optional[str] = "artifact",
    ) -> requests.Response:
        """Redirects the request to the appropriate strategy based on the content type.

        Args:
            url (str): url to send the request to
            method (HttpMethods): The HTTP method to use, e.g. get, post, put, delete
            content_type (ContentType): content type of the request
            headers (Dict[str, str]): headers to send with the request
            params (Dict[str, Any]): params to send to the request
            body (Dict[str, Any]): body to send to the request
            path (Optional[str]): path to the file or folder that will be compressed and used as artifact, defaults to None
            request_kwargs(Dict[str, int | bool | str | float] | None): extra arguments to be passed when making the request.
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact
            file_key (Optional[str]): the field in which the files must be uploaded

        Returns:
            requests.Response: response json
        """
        headers = {"User-Agent": self.USER_AGENT} if headers is None else {**headers, "User-Agent": self.USER_AGENT}
        params = params or {}
        body = body or {}
        request_kwargs = request_kwargs or {}

        if peak.config.DEBUG_MODE:
            self._pretty_print_request(
                url=url,
                method=method.value.upper(),
                content_type=content_type.value,
                headers=headers,
                params=params,
                body=body,
                path=path,
                ignore_files=ignore_files,
            )
            response = requests.models.Response()
            response._content = b"{}"  # noqa: SLF001
            return response

        return BaseHandler.REGISTRY[content_type].handle(
            url=url,
            method=method,
            headers=headers,
            params=params,
            body=body,
            path=path,
            request_kwargs=request_kwargs,
            ignore_files=ignore_files,
            file_key=file_key,
        )


__all__: List[str] = ["Handler", "ApplicationJsonHandler", "MultipartFormDataHandler"]
