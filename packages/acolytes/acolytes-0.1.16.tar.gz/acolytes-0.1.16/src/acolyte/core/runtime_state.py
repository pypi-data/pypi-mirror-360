"""Runtime state management for persistent key-value storage.

Provides a simple interface to the runtime_state table for storing
minimal runtime state that should persist across restarts.

USE FOR:
    - Device fallbacks (GPU -> CPU)
    - Feature flags that change at runtime
    - Small runtime configuration values
    - Simple key-value pairs that need persistence

DO NOT USE FOR:
    - Job checkpoints → use job_states table instead
    - Large JSONs → use dedicated tables with proper schema
    - Temporary data → use memory cache or temp files
    - Process state → use job_states with structured fields

Examples:
    # Good usage
    await state.set("embeddings.device", "cpu")
    await state.set("feature.new_ui", "enabled")

    # Bad usage (use job_states instead)
    # await state.set("indexing_progress_task123", huge_json)
"""

from typing import Optional, Dict, Any
import json

from acolyte.core.database import get_db_manager, FetchType
from acolyte.core.logging import logger


class RuntimeStateManager:
    """
    Simplified interface for runtime_state table.

    Used for storing minimal runtime state that should persist
    across restarts (device fallbacks, indexing progress, etc).

    The runtime_state table is a simple key-value store:
    - key: TEXT PRIMARY KEY
    - value: TEXT NOT NULL
    - updated_at: DATETIME (auto-updated)

    Example usage:
        >>> state = RuntimeStateManager()
        >>> await state.set("embeddings.device", "cpu")
        >>> device = await state.get("embeddings.device")
        >>> print(device)  # "cpu"
    """

    def __init__(self):
        self._db = None

    @property
    def db(self):
        """Lazy load database manager."""
        if self._db is None:
            self._db = get_db_manager()
        return self._db

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from runtime_state.

        Args:
            key: The key to retrieve

        Returns:
            The value if found, None otherwise
        """
        try:
            result = await self.db.execute_async(
                "SELECT value FROM runtime_state WHERE key = ?", (key,), FetchType.ONE
            )
            if result.data and isinstance(result.data, dict):
                return result.data.get("value")
            return None
        except Exception as e:
            logger.warning("Failed to get runtime state", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str) -> bool:
        """
        Set value in runtime_state.

        Args:
            key: The key to set
            value: The value to store (will be converted to string)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure value is string
            str_value = str(value)

            await self.db.execute_async(
                "INSERT OR REPLACE INTO runtime_state (key, value) VALUES (?, ?)",
                (key, str_value),
                FetchType.NONE,
            )
            logger.debug("Runtime state saved", key=key, value=str_value)
            return True
        except Exception as e:
            logger.error("Failed to save runtime state", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from runtime_state.

        Args:
            key: The key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute_async(
                "DELETE FROM runtime_state WHERE key = ?", (key,), FetchType.NONE
            )
            return result.rows_affected > 0
        except Exception as e:
            logger.error("Failed to delete runtime state", key=key, error=str(e))
            return False

    async def list_keys(self, prefix: Optional[str] = None) -> list[str]:
        """
        List all keys, optionally filtered by prefix.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of keys matching the prefix (or all keys if no prefix)
        """
        try:
            if prefix:
                query = "SELECT key FROM runtime_state WHERE key LIKE ? ORDER BY key"
                params = (f"{prefix}%",)
            else:
                query = "SELECT key FROM runtime_state ORDER BY key"
                params = ()

            result = await self.db.execute_async(query, params, FetchType.ALL)
            if result.data and isinstance(result.data, list):
                # Type guard to ensure result.data is List[Dict[str, Any]]
                keys = []
                for row in result.data:
                    if isinstance(row, dict) and "key" in row:
                        keys.append(row["key"])
                return keys
            return []
        except Exception as e:
            logger.error("Failed to list runtime state keys", error=str(e))
            return []

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from runtime_state and parse as JSON.

        Args:
            key: The key to retrieve

        Returns:
            The parsed JSON value if found and valid, None otherwise
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in runtime state", key=key, value=value)
                return None
        return None

    async def set_json(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Set JSON value in runtime_state.

        Args:
            key: The key to set
            value: The dictionary to store (will be JSON-encoded)

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value)
        except (TypeError, ValueError) as e:
            logger.error("Failed to encode JSON for runtime state", key=key, error=str(e))
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """
        Delete all keys with a given prefix.

        Useful for cleaning up related state (e.g., all indexing_progress_*)

        Args:
            prefix: The prefix to match

        Returns:
            Number of keys deleted
        """
        try:
            result = await self.db.execute_async(
                "DELETE FROM runtime_state WHERE key LIKE ?", (f"{prefix}%",), FetchType.NONE
            )
            if result.rows_affected > 0:
                logger.info("Cleared runtime state keys", prefix=prefix, count=result.rows_affected)
            return result.rows_affected
        except Exception as e:
            logger.error("Failed to clear runtime state prefix", prefix=prefix, error=str(e))
            return 0


# Singleton instance for convenience
_runtime_state_manager = None


def get_runtime_state() -> RuntimeStateManager:
    """Get the singleton RuntimeStateManager instance."""
    global _runtime_state_manager
    if _runtime_state_manager is None:
        _runtime_state_manager = RuntimeStateManager()
    return _runtime_state_manager
