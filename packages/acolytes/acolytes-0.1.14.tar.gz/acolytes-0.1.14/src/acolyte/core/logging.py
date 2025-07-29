"""
Lightweight asynchronous logging system for ACOLYTE.
"""

import re
import time
import os
from pathlib import Path
from queue import Queue
from logging.handlers import QueueHandler
from typing import List, Pattern, Optional
from contextlib import contextmanager


class AsyncLogger:
    """
    Lightweight asynchronous logger with a plain-text format.

    Format: timestamp | level | component | message
    No emojis, no JSON, near-zero latency.
    """

    def __init__(self, component: str, debug_mode: bool = False):
        self.component = component
        self.debug_mode = debug_mode
        self.queue = Queue()
        self.handler = QueueHandler(self.queue)
        self._handler_id = None
        self._current_log_path = None
        # Delay handler setup until first log

    def _get_log_path(self) -> Path:
        """
        Determine log path based on context (Docker, local project, or temp).
        """
        # 1. Docker environment - use DATA_DIR
        if data_dir := os.getenv("DATA_DIR"):
            # In Docker, the project_id is in the directory structure
            # The data dir is mounted from ~/.acolyte/projects/{project_id}/data
            # So we extract project_id from the parent directory name
            try:
                # Try to get project_id from the mounted path structure
                data_path = Path(data_dir)
                if data_path.parent.name and len(data_path.parent.name) == 12:
                    # Looks like a project_id (12 char hash)
                    project_id = data_path.parent.name
                    log_dir = data_path / "logs"
                    log_dir.mkdir(parents=True, exist_ok=True)
                    return log_dir / f"{project_id}.log"
            except Exception:
                pass

            # Fallback - try to get project name from config
            config_path = Path("/.acolyte")
            if config_path.exists():
                try:
                    # Only import yaml when needed
                    import yaml

                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        project_name = config.get("project", {}).get("name", "acolyte")
                        # Sanitize project name for filesystem
                        safe_name = "".join(
                            c for c in project_name if c.isalnum() or c in "-_"
                        ).lower()
                        log_dir = Path(data_dir) / "logs"
                        log_dir.mkdir(parents=True, exist_ok=True)
                        return log_dir / f"{safe_name}.log"
                except Exception:
                    pass

            # Final fallback for Docker
            log_dir = Path(data_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir / "acolyte.log"

        # 2. Local project - check for .acolyte.project
        cwd = Path.cwd()
        project_file = cwd / ".acolyte.project"

        if project_file.exists():
            try:
                # Only import yaml when needed
                import yaml

                with open(project_file) as f:
                    data = yaml.safe_load(f)
                    project_id = data.get("project_id")

                    if project_id:
                        log_dir = Path.home() / ".acolyte" / "projects" / project_id / "logs"
                        log_dir.mkdir(parents=True, exist_ok=True)
                        return log_dir / f"{project_id}.log"
            except Exception:
                pass

        # 3. Fallback - temp directory with PID
        temp_logs = Path.home() / ".acolyte" / "logs" / "temp"
        temp_logs.mkdir(parents=True, exist_ok=True)
        return temp_logs / f"acolyte-{os.getpid()}.log"

    def _ensure_handler(self):
        """
        Set up or update handler if log path changes.
        """
        # Lazy import loguru
        from loguru import logger as loguru_logger

        log_path = self._get_log_path()

        # Only reconfigure if path changed
        if log_path != self._current_log_path:
            # Remove old handler if exists
            if self._handler_id is not None:
                loguru_logger.remove(self._handler_id)

            # Add new handler with correct path
            self._handler_id = loguru_logger.add(
                str(log_path),  # Convert to string for cross-platform compatibility
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[component]} | {message}",
                rotation="10 MB",
                compression="zip",
                enqueue=True,  # Key for async
            )
            self._current_log_path = log_path

    def log(self, level: str, message: str, **context):
        """
        Register a log message asynchronously.

        Steps:
        1. Ensure handler is configured for current context
        2. Put the record in the queue (instant)
        3. Background worker writes it
        4. No blocking for the caller
        """
        self._ensure_handler()
        # Lazy import loguru
        from loguru import logger as loguru_logger

        loguru_logger.bind(component=self.component).log(level, message, **context)

    def debug(self, message: str, **context):
        """DEBUG level log."""
        self.log("DEBUG", message, **context)

    def info(self, message: str, **context):
        """INFO level log."""
        self.log("INFO", message, **context)

    def warning(self, message: str, **context):
        """WARNING level log."""
        self.log("WARNING", message, **context)

    def error(self, message: str, include_trace: Optional[bool] = None, **context):
        """
        ERROR level log with optional stack trace.

        Args:
            message: Error message
            include_trace: Force stack trace (None = auto based on debug_mode)
            **context: Additional context
        """
        # Decidir si incluir stack trace
        should_include_trace = include_trace if include_trace is not None else self.debug_mode

        if should_include_trace:
            import traceback

            context["stack_trace"] = traceback.format_exc()

        self.log("ERROR", message, **context)


class SensitiveDataMasker:
    """
    Masks sensitive data in logs.

    Patterns masked:
    - Tokens/API keys
    - Full paths (only basename is kept)
    - Long hashes (keep first 8 chars only)
    """

    def __init__(self, patterns: Optional[List[Pattern]] = None):
        self.patterns = patterns or []

    def mask(self, text: str) -> str:
        """
        Mask sensitive data.

        Example:
        - "token=abc123def456" → "token=***"
        - "/home/user/project" → ".../project"
        - "a1b2c3d4e5f6..." → "a1b2c3d4..."
        """
        # Copia del texto para modificar
        masked = text

        # 1. Enmascarar tokens largos (>20 chars alfanuméricos continuos)
        # Busca secuencias largas que parecen tokens/keys
        masked = re.sub(r'\b[a-zA-Z0-9]{20,}\b', '***TOKEN***', masked)

        # 2. Acortar paths absolutos
        # Linux/Mac paths: /home/user/project → .../project
        masked = re.sub(r'/[a-zA-Z0-9_/.-]{10,}/([a-zA-Z0-9_.-]+)', r'.../\1', masked)

        # Windows paths: C:\Users\Name\project → ...\project
        masked = re.sub(
            r'[A-Z]:\\\\[a-zA-Z0-9_\\\\.-]{10,}\\\\([a-zA-Z0-9_.-]+)', r'...\\\1', masked
        )

        # 3. Acortar hashes largos (>16 chars hex)
        # Muestra solo primeros 8 caracteres
        masked = re.sub(r'\b([a-f0-9]{8})[a-f0-9]{8,}\b', r'\1...', masked)

        # 4. Enmascarar patterns tipo key=value con valores largos
        masked = re.sub(
            r'(api_key|token|secret|password|key)=[a-zA-Z0-9]{8,}',
            r'\1=***',
            masked,
            flags=re.IGNORECASE,
        )

        return masked


class PerformanceLogger:
    """
    Logger specialised for performance metrics.

    Automatically records:
    - Duration
    - Memory usage
    """

    def __init__(self):
        self.logger = AsyncLogger("performance")

    @contextmanager
    def measure(self, operation: str, **context):
        """
        Context manager to measure an operation.

        Example:
        ```python
        with perf_logger.measure("database_query", query=sql):
            result = await db.execute(sql)
        ```
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.logger.info(
                "Operation completed", operation=operation, duration_ms=duration * 1000, **context
            )


# Logger global configurado
# debug_mode se configurará desde .acolyte cuando SecureConfig esté disponible
def _get_debug_mode() -> bool:
    """Retrieve debug_mode from config file or environment variable."""
    # Fallback a variable de entorno para evitar cargar yaml al importar
    return os.getenv("ACOLYTE_DEBUG", "false").lower() == "true"


# Lazy-loaded logger to avoid initialization during import
_logger: Optional[AsyncLogger] = None


def _get_logger() -> AsyncLogger:
    """Get the global logger instance (lazy-loaded)."""
    global _logger
    if _logger is None:
        # Check config file when actually creating the logger
        debug_mode = _get_debug_mode()
        try:
            # Only import yaml when needed
            import yaml

            config_path = Path(".acolyte")
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    debug_mode = config.get("logging", {}).get("debug_mode", debug_mode)
        except Exception:
            pass

        _logger = AsyncLogger("acolyte", debug_mode=debug_mode)
    return _logger


# Create a proxy object that behaves like AsyncLogger
class LoggerProxy:
    """Proxy that forwards all calls to the real logger when accessed."""

    def __getattr__(self, name):
        return getattr(_get_logger(), name)


logger = LoggerProxy()

# Explicit exports
__all__ = [
    "AsyncLogger",
    "SensitiveDataMasker",
    "PerformanceLogger",
    "LoggerProxy",
    "logger",
]
