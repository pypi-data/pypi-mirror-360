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
"""Supported Log levels."""
from __future__ import annotations

import logging
from enum import IntEnum
from typing import Final, Literal


class LogLevel(IntEnum):
    """Enumeration of log levels to be used in logging.

    Each enum member corresponds to a specific log level defined in the logging module.
    The enum provides a convenient way to specify log levels when configuring loggers.

    Attributes:
        DEBUG: Debug log level. Intended for detailed debugging information.
        INFO: Info log level. Used for general information about program execution.
        WARN: Warning log level. Indicates potential issues or unexpected behavior.
        WARNING: Warning log level. Indicates potential issues or unexpected behavior.
        ERROR: Error log level. Indicates errors that do not prevent program execution.
        EXCEPTION: Error log level. Indicates errors that do not prevent program execution.
        CRITICAL: Critical log level. Indicates severe errors that might lead to program failure.
        FATAL: Critical log level. Indicates severe errors that might lead to program failure.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    EXCEPTION = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL


LogLevelNames = Literal[
    "DEBUG",
    "INFO",
    "WARN",
    "WARNING",
    "ERROR",
    "EXCEPTION",
    "CRITICAL",
    "FATAL",
]


LOG_LEVEL_NAMES_TO_LOG_LEVEL: Final[dict[LogLevelNames, LogLevel]] = {
    "DEBUG": LogLevel.DEBUG,
    "INFO": LogLevel.INFO,
    "WARNING": LogLevel.WARN,
    "WARN": LogLevel.WARN,
    "ERROR": LogLevel.ERROR,
    "EXCEPTION": LogLevel.ERROR,
    "FATAL": LogLevel.CRITICAL,
    "CRITICAL": LogLevel.CRITICAL,
}
