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
"""Peak Cache commands."""
import json
from typing import Any, Dict, Optional

import typer
from peak.cli.args import OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.resources.cache import CacheClient

app = typer.Typer(
    help="Cache operations for storing and retrieving data.",
    short_help="Manage Cache Operations.",
)

_KEY = typer.Option(..., help="The cache key to operate on.")
_VALUE = typer.Option(..., help="The value to store in the cache.")
_TTL = typer.Option(None, help="Time to live in seconds for the cache entry.")
_DEFAULT = typer.Option(None, help="Default value to return if key doesn't exist.")
_KEYS = typer.Option(..., help="Comma-separated list of keys to operate on.")
_MAPPING = typer.Option(..., help="JSON mapping of key-value pairs to store.")
_PATTERN = typer.Option(..., help="Pattern to match keys for deletion.")
_DEBUG = typer.Option(False, help="Enable debug logging.")
_PREFIX = typer.Option(None, help="Additional prefix for cache keys.")


def _parse_json_mapping(mapping: str) -> Dict[str, Any]:
    """Parse and validate JSON mapping for mset command.

    Args:
        mapping: JSON string to parse

    Returns:
        Parsed dictionary

    Raises:
        typer.BadParameter: If mapping is invalid
        TypeError: If mapping is not a JSON object
    """
    parsed_mapping = json.loads(mapping)
    if not isinstance(parsed_mapping, dict):
        msg = "Mapping must be a JSON object"
        raise TypeError(msg)
    return parsed_mapping


@app.command("set", short_help="Store a value in the cache.")
def set_value(
    ctx: typer.Context,
    key: str = _KEY,
    value: str = _VALUE,
    ttl: Optional[int] = _TTL,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Store a value in the cache with an optional TTL.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache set --key "user:123" --value "John Doe"
    peak cache set --key "config" --value '{"timeout": 30}' --ttl 3600
    ```

    \b
    🆗 ***Response:***
    True if the value was stored successfully, False otherwise.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value

    with writer.pager():
        result = client.set(key, parsed_value, ttl=ttl)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Retrieve a value from the cache.")
def get(
    ctx: typer.Context,
    key: str = _KEY,
    default: Optional[str] = _DEFAULT,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Retrieve a value from the cache.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache get --key "user:123"
    peak cache get --key "missing" --default "not found"
    ```

    \b
    🆗 ***Response:***
    The cached value or the default value if the key doesn't exist.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    parsed_default = None
    if default is not None:
        try:
            parsed_default = json.loads(default)
        except json.JSONDecodeError:
            parsed_default = default

    with writer.pager():
        result = client.get(key, default=parsed_default)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Retrieve multiple values from the cache.")
def mget(
    ctx: typer.Context,
    keys: str = _KEYS,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Retrieve multiple values from the cache.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache mget --keys "user:123,user:456,config"
    peak cache mget --keys "session:abc,session:def"
    ```

    \b
    🆗 ***Response:***
    List of values corresponding to the keys (null for non-existent keys).
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    key_list = [key.strip() for key in keys.split(",")]

    with writer.pager():
        result = client.mget(*key_list)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Store multiple key-value pairs in the cache.")
def mset(
    ctx: typer.Context,
    mapping: str = _MAPPING,
    ttl: Optional[int] = _TTL,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Store multiple key-value pairs in the cache.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache mset --mapping '{"user:123": "John", "user:456": "Jane"}'
    peak cache mset --mapping '{"config:timeout": 30, "config:retries": 3}' --ttl 3600
    ```

    \b
    🆗 ***Response:***
    True if all values were stored successfully, False otherwise.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    try:
        parsed_mapping = _parse_json_mapping(mapping)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        msg = f"Invalid JSON mapping: {e}"
        raise typer.BadParameter(msg) from e

    with writer.pager():
        result = client.mset(parsed_mapping, ttl=ttl)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Delete one or more keys from the cache.")
def delete(
    ctx: typer.Context,
    keys: str = _KEYS,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Delete one or more keys from the cache.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache delete --keys "user:123"
    peak cache delete --keys "user:123,user:456,config"
    ```

    \b
    🆗 ***Response:***
    Number of keys that were deleted.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    key_list = [key.strip() for key in keys.split(",")]

    with writer.pager():
        result = client.delete(*key_list)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Check if one or more keys exist in the cache.")
def exists(
    ctx: typer.Context,
    keys: str = _KEYS,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Check if one or more keys exist in the cache.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache exists --keys "user:123"
    peak cache exists --keys "user:123,user:456"
    ```

    \b
    🆗 ***Response:***
    Number of keys that exist in the cache.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    key_list = [key.strip() for key in keys.split(",")]

    with writer.pager():
        result = client.exists(*key_list)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Set expiration time for a key.")
def expire(
    ctx: typer.Context,
    key: str = _KEY,
    ttl: int = typer.Option(..., help="Time to live in seconds."),
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Set expiration time for a key.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache expire --key "user:123" --ttl 3600
    peak cache expire --key "session:abc" --ttl 1800
    ```

    \b
    🆗 ***Response:***
    True if the expiration was set, False if the key doesn't exist.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    with writer.pager():
        result = client.expire(key, ttl)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Get the remaining time to live for a key.")
def ttl(
    ctx: typer.Context,
    key: str = _KEY,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Get the remaining time to live for a key.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache ttl --key "user:123"
    peak cache ttl --key "session:abc"
    ```

    \b
    🆗 ***Response:***
    Remaining TTL in seconds (-1 if no expiration, -2 if key doesn't exist).
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    with writer.pager():
        result = client.ttl(key)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Test cache connection.")
def ping(
    ctx: typer.Context,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Test cache connection.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache ping
    ```

    \b
    🆗 ***Response:***
    True if the connection is successful, False otherwise.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    with writer.pager():
        result = client.ping()
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Delete all keys matching a pattern.")
def flush_pattern(
    ctx: typer.Context,
    pattern: str = _PATTERN,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Delete all keys matching a pattern within the tenant namespace.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache flush-pattern --pattern "user:*"
    peak cache flush-pattern --pattern "session:*"
    ```

    \b
    🆗 ***Response:***
    Number of keys that were deleted.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    with writer.pager():
        result = client.flush_by_pattern(pattern)
        writer.write(result, output_type=OutputTypes.json)


@app.command(short_help="Delete all keys for the current tenant.")
def flush_tenant(
    ctx: typer.Context,
    _debug: bool = _DEBUG,
    prefix: Optional[str] = _PREFIX,
    _paging: Optional[bool] = PAGING,
    _output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,
) -> None:
    """Delete all keys for the current tenant.

    \b
    📝 ***Example usage:***
    ```bash
    peak cache flush-tenant
    ```

    \b
    🆗 ***Response:***
    Number of keys that were deleted.
    """
    client: CacheClient = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    if prefix:
        client.set_additional_prefix(prefix)

    with writer.pager():
        result = client.flush_tenant()
        writer.write(result, output_type=OutputTypes.json)
