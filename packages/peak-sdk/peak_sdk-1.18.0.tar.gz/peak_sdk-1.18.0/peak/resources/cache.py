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
"""Peak Cache Client.

Provides caching functionality with tenant-based key prefixing.
Supports cache operations with JSON serialization and connection management.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, cast
from urllib.parse import quote_plus, unquote_plus, urlparse

import valkey
from valkey.exceptions import ConnectionError, TimeoutError, ValkeyError

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session

logger = logging.getLogger(__name__)

DEFAULT_VALKEY_PORT = 6379
SECURE_VALKEY_PORT = 6380


class CacheError(Exception):
    """Base exception for cache operations."""


class CacheConnectionError(CacheError):
    """Exception for cache connection issues."""


def _raise_connection_error(message: str) -> None:
    """Raise a CacheConnectionError with the given message."""
    raise CacheConnectionError(message)


def _raise_cache_error(message: str) -> None:
    """Raise a CacheError with the given message."""
    raise CacheError(message)


class CacheClient(BaseClient):
    """Peak Cache Client for caching operations.

    Provides auto key prefixing based on tenant names to ensure
    proper isolation and access control patterns.

    Inherits from BaseClient to use the default session pattern.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        *,
        debug_logs: bool = True,
        additional_prefix: Optional[str] = None,
        connection_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize cache client.

        Args:
            session: Peak session for authentication (optional)
            debug_logs: Enable or disable debug logging (default: True)
            additional_prefix: Additional prefix to add after tenant name (optional)
            connection_config: Custom connection configuration overrides (optional)
                Available options:
                - decode_responses: bool (default: True)
                - socket_timeout: float (default: 5.0)
                - socket_connect_timeout: float (default: 5.0)
                - retry_on_timeout: bool (default: True)
                - health_check_interval: int (default: 60)
                - max_connections: int (default: None)
                - retry_on_error: list (default: None)
                - socket_keepalive: bool (default: None)
                - socket_keepalive_options: dict (default: None)
        """
        super().__init__(session)
        self._client: Optional[valkey.Valkey] = None
        self._connection_config: Optional[Dict[str, Any]] = None
        self._tenant_name: Optional[str] = None
        self._debug_logs = debug_logs
        self._additional_prefix = additional_prefix
        self._custom_connection_config = connection_config or {}

    def _debug_log(self, message: str) -> None:
        """Log debug message if debug logging is enabled."""
        if self._debug_logs:
            logger.debug(message)

    def _get_connection_config(self) -> Dict[str, Any]:
        """Get cache connection configuration from credentials endpoint."""
        if self._connection_config is None:
            try:
                self._debug_log("Getting cache credentials...")
                response = self.session.create_request(
                    endpoint="connections/api/v1/connections/valkey-credentials",
                    method=HttpMethods.GET,
                    content_type=ContentType.APPLICATION_JSON,
                    subdomain="service",
                )

                self._tenant_name = response.get("tenant")
                if not self._tenant_name:
                    _raise_connection_error("Tenant information not found in cache credentials response")

                engine = response.get("engine", "valkey")

                url = response.get("url")
                if not url:
                    host = response.get("host")
                    port = response.get("port", DEFAULT_VALKEY_PORT)
                    username = response.get("userId")
                    password = response.get("password")

                    if not all([host, username, password]):
                        _raise_connection_error("Missing required cache connection credentials")

                    encoded_username = quote_plus(username)
                    encoded_password = quote_plus(password)
                    use_ssl = port == SECURE_VALKEY_PORT or engine == "valkey"
                    scheme = "rediss" if use_ssl else "redis"
                    url = f"{scheme}://{encoded_username}:{encoded_password}@{host}:{port}"

                parsed = urlparse(url)

                decoded_username = unquote_plus(parsed.username) if parsed.username else None
                decoded_password = unquote_plus(parsed.password) if parsed.password else None

                if engine == "valkey":
                    decoded_username = self._tenant_name

                self._validate_connection_config(
                    {
                        "host": parsed.hostname,
                        "port": parsed.port,
                        "username": decoded_username,
                        "password": decoded_password,
                    },
                )

                use_ssl = parsed.scheme == "rediss"

                config = {
                    "host": parsed.hostname,
                    "port": parsed.port or DEFAULT_VALKEY_PORT,
                    "password": decoded_password,
                    "username": decoded_username,
                    "ssl": use_ssl,
                    "decode_responses": True,
                    "socket_timeout": 5.0,
                    "socket_connect_timeout": 5.0,
                    "retry_on_timeout": True,
                    "health_check_interval": 60,
                }

                # Merge custom configuration (only allow safe overrides)
                safe_overrides = {
                    "decode_responses",
                    "socket_timeout",
                    "socket_connect_timeout",
                    "retry_on_timeout",
                    "health_check_interval",
                    "max_connections",
                    "retry_on_error",
                    "socket_keepalive",
                    "socket_keepalive_options",
                }

                for key, value in self._custom_connection_config.items():
                    if key in safe_overrides:
                        config[key] = value
                        self._debug_log(f"Cache config override: {key} = {value}")
                    else:
                        logger.warning("Ignoring unsafe connection config override: %s", key)

                self._connection_config = config

                logger.info("Cache configured for tenant: %s", self._tenant_name)

            except Exception as e:
                logger.exception("Failed to get cache credentials")
                msg = f"Failed to get cache credentials: {e}"
                raise CacheConnectionError(msg) from e

        return self._connection_config

    def _validate_connection_config(self, config: Dict[str, Any]) -> None:
        """Validate connection configuration."""
        required_fields = ["host", "port", "password", "username"]
        missing = [field for field in required_fields if not config.get(field)]
        if missing:
            _raise_connection_error(f"Missing required connection fields: {missing}")

    def _get_client(self) -> valkey.Valkey:
        """Get or create cache client."""
        if self._client is None:
            try:
                config = self._get_connection_config()
                self._client = valkey.Valkey(**config)
                self._debug_log("Cache client created successfully")
            except Exception as e:
                logger.exception("Failed to create cache client")
                msg = f"Failed to create cache client: {e}"
                raise CacheConnectionError(msg) from e
        return self._client

    def _prefix_key(self, key: str) -> str:
        """Add tenant prefix to key."""
        if not self._tenant_name:
            self._get_connection_config()
        prefix = f"{self._tenant_name}:"
        if self._additional_prefix:
            prefix += f"{self._additional_prefix}:"
        return f"{prefix}{key}"

    def _prefix_keys(self, keys: List[str]) -> List[str]:
        """Add tenant prefix to multiple keys."""
        return [self._prefix_key(key) for key in keys]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in the cache.

        Args:
            key: The key to set
            value: The value to set (will be JSON serialized if not string)
            ttl: Time to live in seconds (optional)

        Returns:
            bool: True if successful, False otherwise

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            prefixed_key = self._prefix_key(key)

            serialized_value = value if isinstance(value, str) else json.dumps(value)

            result = client.set(prefixed_key, serialized_value, ex=ttl)
            self._debug_log(f"Set key: {key} (prefixed: {prefixed_key})")
            return bool(result)

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache set operation failed for key: %s", key)
            msg = f"Failed to set cache key: {e}"
            raise CacheError(msg) from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the cache.

        Args:
            key: The key to get
            default: Default value if key doesn't exist

        Returns:
            Any: The value (JSON deserialized if applicable) or default

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            prefixed_key = self._prefix_key(key)

            value = client.get(prefixed_key)
            if value is None:
                self._debug_log(f"Key not found: {key}")
                return default

            if isinstance(value, str):
                value_str = value
            else:
                value_str = value.decode("utf-8") if isinstance(value, bytes) else str(value)

            if value_str.startswith(("{", "[")):
                try:
                    result = json.loads(value_str)
                except json.JSONDecodeError:
                    pass
                else:
                    self._debug_log(f"Got key: {key} (JSON deserialized)")
                    return result

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache get operation failed for key: %s", key)
            msg = f"Failed to get cache key: {e}"
            raise CacheError(msg) from e
        else:
            self._debug_log(f"Got key: {key} (as string)")
            return value_str

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from the cache.

        Args:
            keys: Keys to delete

        Returns:
            int: Number of keys deleted

        Raises:
            CacheError: If the operation fails
        """
        if not keys:
            return 0

        try:
            client = self._get_client()
            prefixed_keys = self._prefix_keys(list(keys))

            result = client.delete(*prefixed_keys)
            self._debug_log(f"Deleted {result} keys: {list(keys)}")
            return int(cast(int, result))

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache delete operation failed for keys: %s", keys)
            msg = f"Failed to delete cache keys: {e}"
            raise CacheError(msg) from e

    def exists(self, *keys: str) -> int:
        """Check if one or more keys exist in the cache.

        Args:
            keys: Keys to check

        Returns:
            int: Number of keys that exist

        Raises:
            CacheError: If the operation fails
        """
        if not keys:
            return 0

        try:
            client = self._get_client()
            prefixed_keys = self._prefix_keys(list(keys))

            result = client.exists(*prefixed_keys)
            self._debug_log(f"Checked existence of {len(keys)} keys, {result} exist")
            return int(cast(int, result))

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache exists operation failed for keys: %s", keys)
            msg = f"Failed to check cache key existence: {e}"
            raise CacheError(msg) from e

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: The key to set expiration for
            ttl: Time to live in seconds

        Returns:
            bool: True if successful, False if key doesn't exist

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            prefixed_key = self._prefix_key(key)

            result = client.expire(prefixed_key, ttl)
            self._debug_log(f"Set expiration for key: {key} (TTL: {ttl}s)")
            return bool(result)

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache expire operation failed for key: %s", key)
            msg = f"Failed to set cache key expiration: {e}"
            raise CacheError(msg) from e

    def ttl(self, key: str) -> int:
        """Get the time to live for a key.

        Args:
            key: The key to check

        Returns:
            int: TTL in seconds (-1 if no expiration, -2 if key doesn't exist)

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            prefixed_key = self._prefix_key(key)

            result = client.ttl(prefixed_key)
            self._debug_log(f"Got TTL for key: {key} (TTL: {result}s)")
            return int(cast(int, result))

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache TTL operation failed for key: %s", key)
            msg = f"Failed to get cache key TTL: {e}"
            raise CacheError(msg) from e

    def mget(self, *keys: str) -> List[Any]:
        """Get multiple values from the cache.

        Args:
            keys: Keys to get

        Returns:
            List[Any]: List of values (None for missing keys)

        Raises:
            CacheError: If the operation fails
        """
        if not keys:
            return []

        try:
            client = self._get_client()
            prefixed_keys = self._prefix_keys(list(keys))

            values = client.mget(prefixed_keys)
            results: List[Any] = []

            for value in cast(List[Any], values):
                if value is None:
                    results.append(None)
                    continue

                if isinstance(value, str):
                    value_str = value
                else:
                    value_str = value.decode("utf-8") if isinstance(value, bytes) else str(value)

                if value_str.startswith(("{", "[")):
                    try:
                        results.append(json.loads(value_str))
                    except json.JSONDecodeError:
                        pass
                    else:
                        continue

                results.append(value_str)

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache mget operation failed for keys: %s", keys)
            msg = f"Failed to get multiple cache keys: {e}"
            raise CacheError(msg) from e
        else:
            self._debug_log(f"Got {len(keys)} keys via mget")
            return results

    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple key-value pairs in the cache.

        Args:
            mapping: Dictionary of key-value pairs to set
            ttl: Time to live in seconds (optional, applies to all keys)

        Returns:
            bool: True if successful

        Raises:
            CacheError: If the operation fails
        """
        if not mapping:
            return True

        try:
            client = self._get_client()
            prefixed_mapping = {}

            for key, value in mapping.items():
                prefixed_key = self._prefix_key(key)
                serialized_value = json.dumps(value) if not isinstance(value, str) else value
                prefixed_mapping[prefixed_key] = serialized_value

            result = client.mset(prefixed_mapping)

            if ttl is not None:
                for prefixed_key in prefixed_mapping:
                    client.expire(prefixed_key, ttl)

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache mset operation failed")
            msg = f"Failed to set multiple cache keys: {e}"
            raise CacheError(msg) from e
        else:
            self._debug_log(f"Set {len(mapping)} keys via mset")
            return bool(result)

    def flush_tenant(self) -> int:
        """Flush all keys for the current tenant.

        Returns:
            int: Number of keys deleted

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            if not self._tenant_name:
                self._get_connection_config()

            pattern = f"{self._tenant_name}:*"
            keys = list(client.scan_iter(match=pattern))

            if not keys:
                self._debug_log("No keys found for tenant flush")
                return 0

            result = client.delete(*keys)
            self._debug_log(f"Flushed {result} keys for tenant: {self._tenant_name}")
            return int(cast(int, result))

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache flush_tenant operation failed")
            msg = f"Failed to flush tenant cache: {e}"
            raise CacheError(msg) from e

    def flush_by_pattern(self, pattern: str) -> int:
        """Flush keys matching a pattern within the tenant namespace.

        Args:
            pattern: Pattern to match (will be prefixed with tenant name)

        Returns:
            int: Number of keys deleted

        Raises:
            CacheError: If the operation fails
        """
        try:
            client = self._get_client()
            if not self._tenant_name:
                self._get_connection_config()

            prefixed_pattern = self._prefix_key(pattern)
            keys = list(client.scan_iter(match=prefixed_pattern))

            if not keys:
                self._debug_log(f"No keys found for pattern: {pattern}")
                return 0

            result = client.delete(*keys)
            self._debug_log(f"Flushed {result} keys for pattern: {pattern}")
            return int(cast(int, result))

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache flush_by_pattern operation failed for pattern: %s", pattern)
            msg = f"Failed to flush cache by pattern: {e}"
            raise CacheError(msg) from e

    def set_additional_prefix(self, additional_prefix: Optional[str]) -> None:
        """Set additional prefix for cache keys.

        Args:
            additional_prefix: Additional prefix to add after tenant name
        """
        self._additional_prefix = additional_prefix
        self._debug_log(f"Set additional prefix: {additional_prefix}")

    def get_additional_prefix(self) -> Optional[str]:
        """Get current additional prefix.

        Returns:
            Optional[str]: Current additional prefix
        """
        return self._additional_prefix

    def ping(self) -> bool:
        """Test the connection to the cache.

        Returns:
            bool: True if connection is successful

        Raises:
            CacheError: If the connection fails
        """
        try:
            client = self._get_client()
            result = client.ping()
            self._debug_log("Cache ping successful")
            return bool(result)

        except (ConnectionError, TimeoutError, ValkeyError) as e:
            logger.exception("Cache ping failed")
            msg = f"Cache connection test failed: {e}"
            raise CacheError(msg) from e

    def close(self) -> None:
        """Close the cache connection."""
        if self._client is not None:
            try:
                self._client.close()  # type: ignore[no-untyped-call]
                self._debug_log("Cache connection closed")
            except (ConnectionError, TimeoutError, ValkeyError) as e:
                logger.debug("Error closing cache connection: %s", e)
            finally:
                self._client = None


def get_client(
    session: Optional[Session] = None,
    *,
    debug_logs: bool = True,
    additional_prefix: Optional[str] = None,
    connection_config: Optional[Dict[str, Any]] = None,
) -> CacheClient:
    """Get a cache client instance.

    Args:
        session: Peak session for authentication (optional)
        debug_logs: Enable or disable debug logging (default: True)
        additional_prefix: Additional prefix to add after tenant name (optional)
        connection_config: Custom connection configuration overrides (optional)

    Returns:
        CacheClient: Cache client instance
    """
    return CacheClient(
        session=session,
        debug_logs=debug_logs,
        additional_prefix=additional_prefix,
        connection_config=connection_config,
    )


__all__: List[str] = ["CacheClient", "CacheError", "CacheConnectionError", "get_client"]
