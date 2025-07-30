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
"""Logging module, a wrapper around `structlog <https://www.structlog.org/en/stable/>`_ library."""

from __future__ import annotations

import functools
import inspect
import logging
import os
import sys
from types import MappingProxyType
from typing import Any, Callable, Final, Hashable, List, MutableMapping, Optional, Tuple, Union

import orjson
import structlog

from .log_handler import LogHandler
from .log_level import LOG_LEVEL_NAMES_TO_LOG_LEVEL, LogLevel, LogLevelNames
from .utils import mask_nested_pii_data

__title__ = "logging"
__author__ = "PEAK AI"
__license__ = "Apache License, Version 2.0"
__copyright__ = "2024, Peak AI"
__status__ = "production"
__date__ = "14 March 2024"

__all__: List[str] = [
    "DEFAULT_SHARED_PROCESSORS",
    "LOG_LEVEL_NAMES_TO_LOG_LEVEL",
    "LogHandler",
    "LogLevelNames",
    "LogLevel",
    "PeakLogger",
    "default_processors_factory",
    "get_logger",
    "pii_masking_processor",
    "peak_contexts_processor",
]


# ---------------------------------------------------------------------------
# Utility private functions
# ---------------------------------------------------------------------------


def pii_masking_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Masks sensitive PII data present in event_dict."""
    return mask_nested_pii_data(event_dict)


def peak_contexts_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add the standard attribute to the event_dict."""
    attributes_to_add: dict[str, Any] = {
        "source": "peak-sdk",
        "runtime": os.getenv("PEAK_RUNTIME"),
        "press_deployment_id": os.getenv("PRESS_DEPLOYMENT_ID"),
        "run_id": os.getenv("PEAK_RUN_ID"),
        "exec_id": os.getenv("PEAK_EXEC_ID"),
        "stage": os.getenv("PEAK__STAGE", os.getenv("STAGE")),
        "tenant_name": os.getenv("TENANT_NAME", os.getenv("TENANT")),
        "tenant_id": os.getenv("TENANT_ID"),
        "api_name": os.getenv("PEAK_API_NAME"),
        "api_id": os.getenv("PEAK_API_ID"),
        "step_name": os.getenv("PEAK_STEP_NAME"),
        "step_id": os.getenv("PEAK_STEP_ID"),
        "webapp_name": os.getenv("PEAK_WEBAPP_NAME"),
        "webapp_id": os.getenv("PEAK_WEBAPP_ID"),
        "workflow_name": os.getenv("PEAK_WORKFLOW_NAME"),
        "workflow_id": os.getenv("PEAK_WORKFLOW_ID"),
        "workspace_name": os.getenv("PEAK_WORKSPACE_NAME"),
        "workspace_id": os.getenv("PEAK_WORKSPACE_ID"),
        "image_name": os.getenv("PEAK_IMAGE_NAME"),
        "image_id": os.getenv("PEAK_IMAGE_ID"),
    }

    for attr, value in attributes_to_add.items():
        if value:
            event_dict[attr] = value

    return event_dict


# ---------------------------------------------------------------------------
# Utility functions at module level for main logger factory
# ---------------------------------------------------------------------------


DEFAULT_SHARED_PROCESSORS: Tuple[structlog.types.Processor | Any, ...] = (
    structlog.contextvars.merge_contextvars,
    peak_contexts_processor,
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    pii_masking_processor,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.EventRenamer("message"),
)

_ORJSON_OPTS: Final[int] = (
    orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_SERIALIZE_DATACLASS
    | orjson.OPT_SERIALIZE_UUID
    | orjson.OPT_NON_STR_KEYS
    | orjson.OPT_SORT_KEYS
)


def _orjson_serializer(
    obj: Any,
    sort_keys: Optional[bool] = None,
    default: Callable[[Any], Any] = str,
) -> str:
    """Custom serializer using orjson.dumps for structlog."""
    apply_opts: int = (_ORJSON_OPTS | orjson.OPT_SORT_KEYS) if sort_keys else _ORJSON_OPTS

    return orjson.dumps(obj, option=apply_opts, default=default).decode("utf-8")


@functools.lru_cache(maxsize=2, typed=True)  # Only 2 different combinations of disable_masking are possible
def default_processors_factory(
    disable_masking: Optional[bool],
) -> list[structlog.types.Processor | Any]:
    """Return the default processors for PeakLogger.

    Args:
        disable_masking (Optional[bool], optional): Whether to disable masking of sensitive data. Defaults to False.

    Returns:
        list[structlog.types.Processor | Any]: List of processors to be used by the logger.
    """
    _processors = list(DEFAULT_SHARED_PROCESSORS)

    if disable_masking:
        _processors.remove(pii_masking_processor)

    # add renderer based on the environment
    if sys.stdout.isatty():
        # Pretty printing when we run in a terminal session.
        _processors.remove(structlog.processors.format_exc_info)
        _processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                event_key="message",
                timestamp_key="timestamp",
                exception_formatter=structlog.dev.RichTracebackFormatter(color_system="truecolor"),
            ),
        )
    else:
        # Print JSON when we run in production
        _processors.append(structlog.processors.JSONRenderer(serializer=_orjson_serializer, sort_keys=True))

    return _processors


@functools.lru_cache(maxsize=128, typed=True)
def _handle_and_patch_processor_factory_kwargs(
    func: Callable[..., List[structlog.types.Processor | Any]],
    **kwargs: Hashable,
) -> List[structlog.types.Processor | Any]:
    """Handle keyword arguments for custom_processors_factory using inspect.signature, additionally patch the processors list to include EventRenamer in the right position if not already present.

    Unknown keyword arguments are ignored.

    Args:
        func (Callable[..., List[structlog.types.Processor | Any]]): Custom processor factory function.
        **kwargs: Additional keyword arguments to be passed to the custom_processors_factory, if provided.
            kwargs received by the factory function must be hashable else TypeError will be raised by this wrapper.

    Returns:
        List[structlog.types.Processor | Any]: List of processors to be used by the logger.

    Raises:
        ValueError: If multiple renderers are found in the processor factory's returned processors list.
    """
    func_params: MappingProxyType[str, inspect.Parameter] = inspect.signature(func).parameters
    _processors = func(**{k: v for k, v in kwargs.items() if k in func_params})

    if "structlog.processors.EventRenamer" not in str(_processors):

        # find index of KeyValueRenderer/JSONRenderer/ConsoleRenderer and push EventRenamer to before either of them
        indices_for_insertion: list[int] = [
            _processors.index(processor)
            for processor in _processors
            if getattr(processor, "__name__", processor.__class__.__name__)
            in ("KeyValueRenderer", "JSONRenderer", "ConsoleRenderer")
        ]

        if len(indices_for_insertion) > 1:
            multiple_renderer_error_msg: str = f"""
            Multiple renderers found in the processors list returned by the `custom_processors_factory` function: {func.__name__}.
            Please ensure only one of KeyValueRenderer, JSONRenderer, or ConsoleRenderer is present in the processors list.
            """
            raise ValueError(multiple_renderer_error_msg)

        _processors.insert(
            min([*indices_for_insertion, len(_processors)]),
            structlog.processors.EventRenamer("message"),
        )

    return _processors


# ---------------------------------------------------------------------------
# Logger factory function
# ---------------------------------------------------------------------------


def get_logger(
    name: Optional[str] = None,
    level: Optional[LogLevel] = None,
    custom_processors_factory: Optional[Callable[..., List[structlog.types.Processor | Any]]] = None,
    disable_masking: Optional[bool] = False,  # noqa: FBT002
    handlers: Optional[List[LogHandler]] = None,
    file_name: Optional[str] = None,
    **kwargs: Any,
) -> PeakLogger:
    """Return a logger with the specified settings.

    When using the default implementation, pretty-printing is automatically enabled when logger is run in a terminal session (sys.stdout.isatty() == True)
    and JSON printing is enabled when logger is run in production via the `structlog.processors.JSONRenderer` processor.

    Args:
        name (Optional[str], optional): Name of the logger. Defaults to None.
        level (LogLevel): Log level. Defaults to LogLevel.INFO.
        custom_processors_factory (Optional[Callable[..., List[structlog.types.Processor | Any]]], optional): A factory function that returns a list of custom processors.
            Defaults to None. This disables the default processors provided with the default implementation.
        disable_masking (Optional[bool], optional): Whether to disable masking of sensitive data. Defaults to False.
            Only applicable when using the default processors, as custom processors can be used to handle masking on their own.
        handlers (Optional[List[Handlers]], optional): List of log handlers (CONSOLE, FILE). Defaults to CONSOLE.
        file_name (Optional[str], optional): Filename for FILE handler. Required if FILE handler is used. Defaults to None.
        **kwargs: Additional keyword arguments to be passed to the custom_processors_factory, if provided.
            `disable_masking` is automatically passed to the custom_processors_factory and should not be provided here.
            if `custom_processors_factory` does not accept any keyword arguments, they will all be ignored.
            Additionally, all kwargs receivable by the factory function must be hashable else TypeError will be raised by the `_handle_and_patch_processor_factory_kwargs` wrapper.

    Returns:
        PeakLogger: A logger instance configured with the specified settings.

    Raises:
        ValueError: If the `file_name` is not provided for FILE handler or if `multiple renderers` are found in the `processor`(s) list returned by the `custom_processors_factory`.
    """
    if level is not None:
        _log_level = level.value
    elif os.getenv("LOG_LEVEL") is not None and os.getenv("LOG_LEVEL", "INFO").upper() in LOG_LEVEL_NAMES_TO_LOG_LEVEL:
        _log_level = LOG_LEVEL_NAMES_TO_LOG_LEVEL.get(
            os.getenv("LOG_LEVEL", "INFO").upper(),  # type: ignore # noqa: PGH003
            "INFO",
        ).value
    elif os.getenv("DEBUG", "false").lower() == "true":
        _log_level = logging.DEBUG
    else:
        _log_level = LogLevel.INFO.value

    _processors: list[structlog.types.Processor | Any] = (
        _handle_and_patch_processor_factory_kwargs(custom_processors_factory, disable_masking=disable_masking, **kwargs)
        if custom_processors_factory is not None
        else default_processors_factory(
            disable_masking=disable_masking,
        )
    )
    handlers_list: list[Any] = []
    if not handlers or LogHandler.CONSOLE in handlers:
        handlers_list.append(logging.StreamHandler())  # Console handler
    if handlers and LogHandler.FILE in handlers:
        if file_name:
            handlers_list.append(logging.FileHandler(file_name))  # File handler
        else:
            msg = "filename must be provided for FILE handler."
            raise ValueError(msg)

    # Set the log level and add the handlers to the root logger
    # This is required to ensure that the log level and handlers are applied to the root logger
    logging.basicConfig(level=_log_level, handlers=handlers_list, format="", force=True)

    # configure structlog with the specified settings
    structlog.configure(
        processors=[*_processors],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return PeakLogger(structlog.get_logger(name))


# ---------------------------------------------------------------------------
# Wrapper Logger class
# Basically delegate everything to `structlog`.
# ---------------------------------------------------------------------------


class PeakLogger:
    """Wrapper class for logging with various log levels."""

    # use __slots__ to avoid dynamic attribute creation
    __slots__: list[str] = ["_logger"]

    def __init__(self, logger: Any) -> None:
        """Initialize with a logger object.

        Args:
            logger (Any): Logger object to wrap.
        """
        self._logger: structlog.stdlib.BoundLogger = logger

    def __getattribute__(self, __name: str) -> Any:
        """Return the attribute from the wrapped logger object."""
        if __name in [*PeakLogger.__slots__, *PeakLogger.__dict__.keys()]:
            return object.__getattribute__(self, __name)
        return getattr(self._logger, __name)

    def bind(self, context: Union[dict[str, Any], None] = None, **kwargs: Any) -> None:
        """Bind contextual information to the logger, enriching log messages.

        This method allows attaching context data to the logger, such as additional information
        or system details, to provide more context in log messages.

        Args:
            context (Union[dict[str, Any], None]): A dictionary or None for contextual information.
            **kwargs: Additional key-value pairs to enhance context.
        """
        if context is None:
            context = {}

        if kwargs:
            # file deepcode ignore AttributeLoadOnNone: false positive
            context.update(kwargs)

        self._logger = self._logger.bind(**context)

    def unbind(self, keys: list[str]) -> None:
        """Unbind specified keys from the logger's context.

        Args:
            keys (list[str]): List of keys to unbind.
        """
        context: dict[str, Any] | dict[Any, Any] = structlog.get_context(self._logger)

        for key in keys:
            if key in context:
                del context[key]

        # Rebind the modified context to the logger
        self._logger = self._logger.bind(**context)

    def clone_with_context(self, context: Union[dict[str, Any], None] = None, **kwargs: Any) -> PeakLogger:
        """Return a frozen copy of this logger with the specified context added."""
        new_logger = PeakLogger(self._logger.new())
        new_logger.bind(context, **kwargs)
        return new_logger

    def set_log_level(self, level: LogLevel) -> None:
        """Set the log level of the root logger.

        Args:
            level (LogLevel): Log level to set.
        """
        if self._is_valid_log_level(level):
            logging.getLogger().setLevel(level.value)

    def _is_valid_log_level(self, level: LogLevel) -> bool:
        """Check if a given log level is valid."""
        return level in LogLevel
