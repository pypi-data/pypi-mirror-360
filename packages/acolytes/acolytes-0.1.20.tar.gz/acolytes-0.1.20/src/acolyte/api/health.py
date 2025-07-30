"""
Health check system ACOLYTE.
Monitors the status of all critical components.
"""

from fastapi import APIRouter, Response
from typing import Dict, Any, Optional
import psutil
import time
import asyncio
import os
from acolyte.core.utils.datetime_utils import utc_now_iso
import sqlite3

# Core imports
from acolyte.core.database import get_db_manager, FetchType
from acolyte.core.logging import logger
from acolyte.core.ollama import OllamaClient
from acolyte.core.secure_config import Settings
from acolyte.core.exceptions import (
    internal_error,
)

# Services imports
# Note: We don't need ConversationService - we use SQL directly for stats

# Embeddings import
# (get_embeddings solo se importa dentro de las funciones que lo usan)

router = APIRouter()

# Track service start time
SERVICE_START_TIME = time.time()

# Singleton instance of IndexingService (lazy loading)
_indexing_service = None


def get_indexing_service() -> Optional[Any]:
    """Get singleton instance of IndexingService with robust error handling."""
    global _indexing_service

    if _indexing_service is None:
        try:
            from acolyte.services import IndexingService

            _indexing_service = IndexingService()
            logger.info("IndexingService initialized", status="success")
        except ImportError as e:
            logger.warning("IndexingService not available", error=str(e))
            logger.info("[UNTESTED PATH] IndexingService import failed")
            _indexing_service = "not_available"  # Mark as not available
        except Exception as e:
            # Capture any other error during creation
            logger.error("IndexingService initialization failed", error=str(e), exc_info=True)
            logger.info("[UNTESTED PATH] IndexingService initialization error")
            _indexing_service = "error"  # Mark as error

    # Return None if not available or there was an error
    if _indexing_service in ["not_available", "error"]:
        return None

    return _indexing_service


@router.get("/health")
async def health_check(response: Response) -> Dict[str, Any]:
    """
    Full health check of the system with intelligent timeouts.

    Checks:
    - Ollama (acolyte:latest) - 5s timeout, non-critical
    - Weaviate (vector database) - 30s timeout, critical
    - SQLite (metadata) - 10s timeout, critical
    - UniXcoder (embeddings) - 5s timeout, non-critical
    - System (CPU, memory, disk)

    Returns:
        Dict with full state and metrics
    """
    # Check disk space before heavy checks (e.g., embeddings, ollama)
    disk = psutil.disk_usage(".")
    if disk.percent > 95:
        logger.warning("Low disk space detected before health checks", disk_percent=disk.percent)
        response.status_code = 507  # Insufficient Storage
        return {
            "status": "unhealthy",
            "error": "Espacio en disco insuficiente para operar con modelos grandes. Libera espacio y vuelve a intentarlo.",
            "disk_percent": disk.percent,
        }

    health_status: Dict[str, Any] = {
        "status": "healthy",  # healthy | degraded | unhealthy
        "timestamp": utc_now_iso(),
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - SERVICE_START_TIME),
        "services": {},
        "system": {},
    }

    # Helper function to run with timeout
    async def _run_with_timeout(coro, timeout_seconds: int, service_name: str):
        """Execute coroutine with timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning(
                f"Health check timeout for {service_name}",
                service=service_name,
                timeout=timeout_seconds,
            )
            return {
                "status": "timeout",
                "error": f"Check timed out after {timeout_seconds}s. Verifica la conectividad de red y el estado del servicio {service_name}.",
                "timeout_seconds": timeout_seconds,
            }
        except Exception as e:
            logger.error(
                f"Exception in health check for {service_name}", error=str(e), exc_info=True
            )
            return {
                "status": "unhealthy",
                "error": str(e),
                "user_message": f"Error inesperado comprobando {service_name}. Revisa los logs para más detalles.",
            }

    # List of checks to perform with criticality and timeouts
    # Format: (name, check_function, is_critical, timeout_seconds)
    checks = [
        ("database", _check_database, True, 10),  # Critical, 10s timeout
        ("weaviate", _check_weaviate, True, 30),  # Critical, 30s timeout
        ("ollama", _check_ollama, False, 300),  # Not critical, 5 min timeout para modelo grande
        (
            "embeddings",
            _check_embeddings,
            False,
            30,
        ),  # Not critical, 30s timeout (model loading can be slow)
    ]

    # Execute checks in parallel with timeouts
    tasks = []
    for service_name, check_func, is_critical, timeout in checks:
        task = _run_with_timeout(check_func(), timeout, service_name)
        tasks.append((service_name, is_critical, task))

    # Gather results
    results = []
    for service_name, is_critical, task in tasks:
        result = await task
        results.append((service_name, is_critical, result))

    # Process results
    for service_name, is_critical, result in results:
        if isinstance(result, Exception):
            health_status["services"][service_name] = {
                "status": "unhealthy",
                "error": str(result),
                "error_type": type(result).__name__,
            }
            if is_critical:
                health_status["status"] = "unhealthy"
            elif health_status["status"] == "healthy":
                health_status["status"] = "degraded"
        elif isinstance(result, dict):
            health_status["services"][service_name] = result

            # Adjust general status based on service status and criticality
            service_status = result.get("status", "unknown")

            if service_status in ["unhealthy", "timeout"]:
                if is_critical:
                    # Critical service failed - system is unhealthy
                    health_status["status"] = "unhealthy"
                else:
                    # Non-critical service failed - system is degraded
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
            elif service_status == "degraded" and health_status["status"] == "healthy":
                health_status["status"] = "degraded"

    # Check system (always last)
    try:
        health_status["system"] = await _check_system()
    except Exception as e:
        logger.error("System check failed", error=str(e))
        health_status["system"] = {"error": str(e)}
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"

    # Set HTTP status code based on health
    if health_status["status"] == "unhealthy":
        response.status_code = 503  # Service Unavailable
    elif health_status["status"] == "degraded":
        response.status_code = 200  # OK with warnings

    logger.info(
        f"Health Check | Status: {health_status['status']} | "
        f"Services: {len([s for s in health_status['services'].values() if s.get('status') == 'healthy'])}/"
        f"{len(health_status['services'])}"
    )

    return health_status


@router.get("/stats")
async def system_stats() -> Dict[str, Any]:
    """
    General system statistics for ACOLYTE.
    Useful for dashboard and monitoring.
    """
    config = Settings()
    try:
        # Get services
        db_manager = get_db_manager()

        # Conversation statistics
        try:
            conversation_stats: Dict[str, Any] = {
                "total": 0,
                "today": 0,
                "this_week": 0,
                "average_messages_per_session": 0.0,
            }

            # Direct SQL query to get basic stats
            query = """
            SELECT 
                COUNT(*) as total_conversations,
                COUNT(CASE WHEN DATE(created_at) = DATE('now') THEN 1 END) as today,
                COUNT(CASE WHEN DATE(created_at) >= DATE('now', '-7 days') THEN 1 END) as this_week
            FROM sessions
            """

            result = await db_manager.execute_async(query, fetch=FetchType.ONE)
            if result.data and isinstance(result.data, dict):
                conversation_stats["total"] = result.data.get("total_conversations", 0)
                conversation_stats["today"] = result.data.get("today", 0)
                conversation_stats["this_week"] = result.data.get("this_week", 0)

        except Exception as e:
            logger.warning("Failed to get conversation stats", error=str(e))
            conversation_stats = {"error": "Unable to fetch stats"}

        # Indexing statistics
        indexing_service = get_indexing_service()

        if indexing_service is None:
            # Service not available or error during initialization
            indexing_stats = {
                "total_files": 0,
                "total_chunks": 0,
                "languages": {},
                "chunk_types": {},
                "last_indexed": None,
                "error": "IndexingService not available",
            }
        else:
            try:
                # Get real stats from singleton service
                indexing_stats = await indexing_service.get_stats()

            except Exception as e:
                logger.warning("Failed to get indexing stats", error=str(e))
                indexing_stats = {"error": "Unable to fetch stats", "details": str(e)}

        # Storage statistics
        try:
            # Size of SQLite database
            db_path = config.get("database.path", ".acolyte.db")
            logger.info(f"[HEALTH] Using database path: {db_path}")
            db_size_mb = 0.0

            if os.path.exists(db_path):
                db_size_mb = os.path.getsize(db_path) / (1024 * 1024)

            storage_stats = {
                "database": {"size_mb": round(db_size_mb, 2)},
                "vectors": {"count": 0, "size_mb": 0.0},  # TODO: Stats de Weaviate
                "total_size_mb": round(db_size_mb, 2),
            }

        except Exception as e:
            logger.warning("Failed to get storage stats", error=str(e))
            storage_stats = {"error": "Unable to fetch stats"}

        return {
            "conversations": conversation_stats,
            "indexing": indexing_stats,
            "performance": {
                "uptime_seconds": int(time.time() - SERVICE_START_TIME),
                "average_response_time_ms": 0,  # TODO: Implement tracking
                "p95_response_time_ms": 0,
                "cache_hit_rate": 0.0,
            },
            "optimization": {
                "fatigue_level": 0.0,  # TODO: Implement when Dream is ready
                "last_optimization": None,
                "next_recommended": None,
                "optimizations_completed": 0,
            },
            "storage": storage_stats,
        }

    except Exception as e:
        logger.error("Stats retrieval failed", error=str(e), exc_info=True)
        error_response = internal_error(
            message="Failed to retrieve system statistics", context={"error_type": type(e).__name__}
        )
        return {"error": error_response.model_dump()}


@router.get("/websocket-stats")
async def websocket_stats() -> Dict[str, Any]:
    """
    Active WebSocket connection statistics.
    Useful for debugging and monitoring progress connections.
    """
    try:
        from acolyte.api.websockets.progress import get_connection_stats, get_active_tasks

        # Get connection statistics
        connection_stats = get_connection_stats()
        active_tasks = get_active_tasks()

        return {
            "active_connections": len(active_tasks),
            "active_task_ids": active_tasks,
            "connection_details": connection_stats,
            "timestamp": utc_now_iso(),
        }

    except ImportError:
        logger.warning("WebSocket progress module not available", module="websocket")
        return {
            "error": "WebSocket stats not available",
            "reason": "Progress module not imported",
        }
    except Exception as e:
        logger.error("WebSocket stats failed", error=str(e), exc_info=True)
        error_response = internal_error(
            message="Failed to retrieve WebSocket statistics",
            context={"error_type": type(e).__name__},
        )
        return {"error": error_response.model_dump()}


# ============================================================================
# INDIVIDUAL CHECK FUNCTIONS
# ============================================================================


async def _check_ollama() -> Dict[str, Any]:
    """
    Check the status of Ollama and the acolyte:latest model.
    """
    try:
        ollama_start = time.time()
        ollama_client = OllamaClient()
        try:
            logger.info("[HEALTH] Probing Ollama/acolyte:latest with test generation...")
            test_response = await asyncio.wait_for(
                ollama_client.generate(prompt="Hello", max_tokens=5), timeout=300
            )
            generation_works = bool(test_response)
        except asyncio.TimeoutError:
            logger.error("Ollama test generation timed out (300s)", exc_info=True)
            generation_works = False
        except Exception as e:
            logger.warning("Ollama test generation failed", error=str(e), exc_info=True)
            generation_works = False
        finally:
            await ollama_client.close()
        response_time = int((time.time() - ollama_start) * 1000)
        return {
            "status": "healthy" if generation_works else "unhealthy",
            "model": "acolyte:latest",
            "generation_test": "passed" if generation_works else "failed",
            "response_time_ms": response_time,
            "user_message": "Si Ollama falla, revisa que el contenedor esté corriendo y que la red esté disponible. Si es la primera vez, puede estar construyendo el modelo (tarda varios minutos).",
        }
    except Exception as e:
        logger.error("Ollama check failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "suggestion": "Ollama o el modelo 'acolyte:latest' no están disponibles. Ejecuta 'acolyte install' para preparar los modelos y asegúrate de que los servicios están corriendo. Si el problema persiste, revisa los logs de instalación y arranque.",
            "user_message": "No se pudo conectar con Ollama. Verifica la red, el contenedor y el espacio en disco.",
        }


async def _check_database() -> Dict[str, Any]:
    """
    Check the status of the SQLite database (síncrono para evitar deadlocks en health check).
    """
    config = Settings()
    logger.info("[HEALTH] Starting database check (sync mode)...")
    try:
        db_start = time.time()
        db_path = config.get("database.path", ".acolyte.db")
        logger.info(f"[HEALTH] Using database path: {db_path}")
        size_mb = 0.0
        import os

        if os.path.exists(db_path):
            try:
                size_mb = os.path.getsize(db_path) / (1024 * 1024)
            except Exception as e:
                logger.error("[HEALTH] Error getting DB file size", error=str(e), exc_info=True)
                return {
                    "status": "unhealthy",
                    "error": "No se pudo leer el tamaño de la base de datos. Revisa permisos y espacio en disco.",
                }
        else:
            logger.error("[HEALTH] Database file not found")
            return {
                "status": "unhealthy",
                "error": "Database file not found",
                "user_message": "No se encontró la base de datos. Ejecuta 'acolyte install' o revisa la configuración.",
            }
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            c = conn.cursor()
            logger.info("[HEALTH] Querying tables in the database (sync)...")
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_rows = c.fetchall()
            tables = [row[0] for row in table_rows]
            required_tables = {
                "sessions",
                "tasks",
                "technical_decisions",
                "dream_state",
                "runtime_state",
                "job_states",
            }
            missing_tables = required_tables - set(tables)
            counts = {}
            for table in ["sessions", "tasks", "technical_decisions"]:
                if table in tables:
                    try:
                        logger.info(f"[HEALTH] Counting records in table {table} (sync)...")
                        c.execute(f"SELECT COUNT(*) as count FROM {table}")
                        count = c.fetchone()[0]
                        counts[table] = count
                    except Exception as e:
                        logger.error(
                            f"[HEALTH] Exception counting records in table {table}: {e}",
                            exc_info=True,
                        )
                        counts[table] = f"exception: {e}"
            conn.close()
        except Exception as e:
            logger.error(f"[HEALTH] Exception querying tables in the database: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": f"Exception querying tables: {e}",
                "user_message": "No se pudo consultar la base de datos. Revisa permisos, integridad y espacio en disco.",
            }
        response_time = int((time.time() - db_start) * 1000)
        status = "healthy"
        warnings = []
        if missing_tables:
            status = "healthy"
            warnings.append(f"Missing tables: {', '.join(sorted(missing_tables))}")
        logger.info(f"[HEALTH] Database check finished in {response_time} ms. Status: {status}")
        return {
            "status": status,
            "response_time_ms": response_time,
            "size_mb": round(size_mb, 2),
            "tables": {
                "total": len(tables),
                "required_present": len(required_tables - missing_tables),
                "missing": list(missing_tables) if missing_tables else None,
            },
            "record_counts": counts,
            "warnings": warnings if warnings else None,
        }
    except Exception as e:
        logger.error("Database check failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "suggestion": "Check database file permissions and integrity",
            "user_message": "Error grave accediendo a la base de datos. Revisa permisos, integridad y espacio en disco.",
        }


async def _check_embeddings() -> Dict[str, Any]:
    """
    Check the status of the UniXcoder embeddings service.
    Optimized to avoid loading the full model during health check.
    """
    embeddings_start = time.time()

    try:
        from pathlib import Path
        import os

        # Use same cache directory logic as unixcoder.py
        cache_dir = Path(
            os.environ.get('HF_HOME')
            or os.environ.get('TRANSFORMERS_CACHE')
            or str(Path.home() / '.cache' / 'huggingface' / 'hub')
        )

        # For HF_HOME, the model is stored in hub subdirectory
        if os.environ.get('HF_HOME'):
            model_dir = cache_dir / "hub" / "models--microsoft--unixcoder-base"
        else:
            model_dir = cache_dir / "models--microsoft--unixcoder-base"

        logger.info(f"[HEALTH] Checking embeddings model at: {model_dir}")

        if not model_dir.exists():
            logger.info("[HEALTH] UniXcoder model not downloaded yet")
            return {
                "status": "degraded",
                "error": "model_not_downloaded",
                "suggestion": "Run 'acolyte install' to download the model",
                "model": "microsoft/unixcoder-base",
                "user_message": "El modelo de embeddings no está descargado. Ejecuta 'acolyte install' para descargarlo.",
            }

        logger.info("[HEALTH] UniXcoder model found, service ready")

        # Simple check: if model exists on disk, report as healthy
        # The actual model loading will happen on first use
        response_time = int((time.time() - embeddings_start) * 1000)
        return {
            "status": "healthy",
            "model": "microsoft/unixcoder-base",
            "dimensions": 768,
            "model_loaded": False,
            "model_available": True,
            "info": "Model will load on first use (~10-15 seconds)",
            "response_time_ms": response_time,
            "user_message": "El modelo de embeddings está disponible y se cargará automáticamente al primer uso.",
        }

    except Exception as e:
        logger.error("Embeddings check failed", error=str(e), exc_info=True)
        logger.info("[UNTESTED PATH] Embeddings service check failed")
        error_type = "unknown"
        if "CUDA" in str(e) or "device" in str(e).lower():
            error_type = "gpu_unavailable"
        elif "memory" in str(e).lower() or "OOM" in str(e):
            error_type = "out_of_memory"
        elif "model" in str(e).lower() or "load" in str(e).lower():
            error_type = "model_load_failed"
        return {
            "status": "degraded",  # Changed from unhealthy to degraded (non-critical)
            "error": str(e),
            "error_type": error_type,
            "suggestion": _get_embeddings_suggestion(error_type),
            "user_message": "Error en embeddings. Revisa los logs, la memoria y el espacio en disco.",
        }


async def _check_weaviate() -> Dict[str, Any]:
    """
    Check the status of Weaviate (síncrono para evitar deadlocks en health check).
    """
    config = Settings()
    logger.info("[HEALTH] Starting Weaviate check (sync mode)...")
    weaviate_start = time.time()
    try:
        import weaviate

        # (WeaviateBaseError no se usa, eliminar importación)
    except ImportError:
        logger.error("[HEALTH] weaviate-client not installed")
        return {
            "status": "degraded",
            "error": "weaviate_client_not_installed",
            "suggestion": "Install weaviate-client: pip install weaviate-client",
            "response_time_ms": int((time.time() - weaviate_start) * 1000),
        }
    weaviate_url = os.getenv(
        "WEAVIATE_URL", f"http://localhost:{config.get('ports.weaviate', 8080)}"
    )
    try:
        client = weaviate.Client(weaviate_url)
        logger.info(f"[HEALTH] Created Weaviate client for {weaviate_url}")
        logger.info("[HEALTH] Checking Weaviate readiness (sync, timeout=30s)...")
        # (socket no se usa, eliminar importación)
        ready = False
        for _ in range(30):
            try:
                if client.is_ready():
                    ready = True
                    break
            except Exception as e:
                logger.warning(f"[HEALTH] Weaviate not ready yet: {e}")
            time.sleep(1)
        if not ready:
            logger.error("[HEALTH] Weaviate is not ready after 30s")
            return {
                "status": "unhealthy",
                "error": "weaviate_not_ready (sync, 30s)",
                "url": weaviate_url,
                "suggestion": "Ensure Weaviate service is running",
                "response_time_ms": int((time.time() - weaviate_start) * 1000),
            }
    except Exception as e:
        logger.error("[HEALTH] Failed to create or check Weaviate client", error=str(e))
        return {
            "status": "unhealthy",
            "error": f"client_creation_or_ready_failed: {e}",
            "url": weaviate_url,
            "suggestion": "Check Weaviate URL configuration",
            "response_time_ms": int((time.time() - weaviate_start) * 1000),
        }
    logger.info(
        f"[HEALTH] Weaviate check finished in {int((time.time() - weaviate_start) * 1000)} ms. Status: healthy"
    )
    return {
        "status": "healthy",
        "response_time_ms": int((time.time() - weaviate_start) * 1000),
    }


async def _check_system() -> Dict[str, Any]:
    """
    Check system resources (CPU, memory, disk).
    """
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()

        # Memory
        memory = psutil.virtual_memory()

        # Disk (current directory)
        disk = psutil.disk_usage(".")

        # Determine status based on resource usage
        status = "healthy"
        warnings = []

        if cpu_percent > 90:
            status = "degraded"
            warnings.append("High CPU usage")

        if memory.percent > 90:
            status = "degraded"
            warnings.append("High memory usage")

        if disk.percent > 90:
            status = "degraded"
            warnings.append("Low disk space")

        return {
            "status": status,
            "warnings": warnings if warnings else None,
            "cpu": {
                "percent": round(cpu_percent, 1),
                "cores": cpu_count,
            },
            "memory": {
                "percent": round(memory.percent, 1),
                "used_gb": round(memory.used / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
            },
            "disk": {
                "percent": round(disk.percent, 1),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
            },
        }

    except Exception as e:
        logger.error("System resource check failed", error=str(e))
        return {
            "status": "degraded",
            "error": str(e),
        }


def _get_embeddings_suggestion(error_type: str) -> str:
    """
    Get specific suggestion based on the type of embedding error.
    """
    suggestions = {
        "gpu_unavailable": "GPU not available, will fallback to CPU",
        "out_of_memory": "Insufficient memory, try reducing batch size",
        "model_load_failed": "Check if UniXcoder model files are available",
        "unknown": "Check embeddings service configuration",
    }
    return suggestions.get(error_type, suggestions["unknown"])
