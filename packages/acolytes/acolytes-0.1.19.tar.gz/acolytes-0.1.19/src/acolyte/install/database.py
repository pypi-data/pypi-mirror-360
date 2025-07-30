"""
ACOLYTE Database Initialization Module

Provides functions for initializing SQLite and Weaviate databases.
Converted from scripts/init_database.py to be importable.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from typing import cast
import os
import aiosqlite

from acolyte.core.logging import logger
from acolyte.install.common import print_error, print_info, print_success, show_spinner
from acolyte.core.exceptions import VersionIncompatibilityError
from acolyte.core.utils.retry import retry_async, retry_sync
from acolyte.core.exceptions import SQLiteBusyError, ExternalServiceError

# Version constants
CURRENT_CHUNKING_MODEL_VERSION = "2.0.0"
CURRENT_EMBEDDING_MODEL_VERSION = "unixcoder-1.2.0"
CURRENT_WEAVIATE_SCHEMA_VERSION = "1.3.0"

# Try to import weaviate, but make it optional
try:
    from weaviate import Client
    from weaviate.exceptions import UnexpectedStatusCodeException

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    Client = None
    UnexpectedStatusCodeException = None


class DatabaseInitializer:
    """Initialize both SQLite and Weaviate for ACOLYTE"""

    def __init__(self, project_path: Path, project_id: str, global_dir: Optional[Path] = None):
        """
        Initialize the database installer.

        Args:
            project_path: Path to the user's project
            project_id: Unique project ID
            global_dir: Global ACOLYTE directory (default: ~/.acolyte)
        """
        self.project_path = project_path.resolve()
        self.project_id = project_id
        self.global_dir = global_dir or Path.home() / ".acolyte"

        # Database paths
        self.project_data_dir = self.global_dir / "projects" / project_id / "data"
        self.db_path = self.project_data_dir / "acolyte.db"
        # Use importlib.resources for packaged files
        try:
            import importlib.resources as resources

            # For schemas.sql
            if hasattr(resources, 'files'):
                core_files = resources.files('acolyte.core.database_schemas')
                self.schemas_path = Path(str(core_files / 'schemas.sql'))
                rag_files = resources.files('acolyte.rag.collections')
                self.weaviate_schemas_path = Path(str(rag_files / 'schemas.json'))
            else:
                # Fallback for older Python
                with resources.path('acolyte.core.database_schemas', 'schemas.sql') as p:
                    self.schemas_path = Path(p)
                with resources.path('acolyte.rag.collections', 'schemas.json') as p:
                    self.weaviate_schemas_path = Path(p)
        except Exception:
            # Improved fallback for both development and pip installations
            import site

            schema_found = False
            weaviate_schema_found = False

            # Search in multiple possible locations
            search_paths = [
                Path(__file__).parent.parent,  # Development path
                *[Path(p) for p in site.getsitepackages()],  # System site-packages
                (
                    Path(site.getusersitepackages()) if site.getusersitepackages() else None
                ),  # User site-packages
            ]

            for base_path in filter(None, search_paths):
                if not schema_found:
                    potential_schema = (
                        base_path / "acolyte" / "core" / "database_schemas" / "schemas.sql"
                    )
                    if potential_schema.exists():
                        self.schemas_path = potential_schema
                        schema_found = True

                if not weaviate_schema_found:
                    potential_weaviate = (
                        base_path / "acolyte" / "rag" / "collections" / "schemas.json"
                    )
                    if potential_weaviate.exists():
                        self.weaviate_schemas_path = potential_weaviate
                        weaviate_schema_found = True

                if schema_found and weaviate_schema_found:
                    break

            # Final fallback if nothing found
            if not schema_found:
                self.schemas_path = (
                    Path(__file__).parent.parent / "core" / "database_schemas" / "schemas.sql"
                )
            if not weaviate_schema_found:
                self.weaviate_schemas_path = (
                    Path(__file__).parent.parent / "rag" / "collections" / "schemas.json"
                )

    def ensure_directories(self) -> bool:
        """Ensure all necessary directories exist"""
        try:
            self.project_data_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error("Failed to create data directory", error=str(e))
            return False

    async def _create_connection(self):
        async def connect_sqlite():
            return await aiosqlite.connect(self.db_path)

        conn = await retry_async(
            connect_sqlite,
            max_attempts=4,
            retry_on=(SQLiteBusyError, ExternalServiceError, Exception),
            logger=logger,
        )
        await conn.execute("PRAGMA journal_mode=WAL")
        return conn

    async def init_sqlite(self) -> bool:
        """
        Initialize the SQLite database with the complete schema.
        Uso: await db.init_sqlite() o asyncio.run(db.init_sqlite())
        """
        try:
            show_spinner("Initializing SQLite database...", 1.0)
            if not self.ensure_directories():
                return False
            if not self.schemas_path.exists():
                logger.error(f"Schema file not found at: {self.schemas_path}")
                print_error("Schema file not found. Please ensure schemas.sql exists.")
                return False
            with open(self.schemas_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn = await self._create_connection()
            cursor = await conn.cursor()
            # Retry critical schema operations
            await retry_async(
                lambda: cursor.execute("PRAGMA foreign_keys = ON;"),
                max_attempts=3,
                retry_on=(SQLiteBusyError, ExternalServiceError, Exception),
                logger=logger,
            )
            await retry_async(
                lambda: cursor.executescript(schema_sql),
                max_attempts=3,
                retry_on=(SQLiteBusyError, ExternalServiceError, Exception),
                logger=logger,
            )
            await cursor.execute('SELECT COUNT(*) FROM dream_state')
            row = await cursor.fetchone()
            count = row[0] if row else 0
            if count == 0:
                await cursor.execute(
                    """
                    INSERT INTO dream_state (id, fatigue_level, optimization_count)
                    VALUES (1, 0.0, 0)
                    """
                )
            elif count == 1:
                pass
            else:
                print_error(
                    'The dream_state table has more than one row. Please repair it manually.'
                )
                logger.error('dream_state has multiple rows, possible corruption')
                await conn.close()
                return False
            await cursor.execute('SELECT COUNT(*) FROM code_graph_metrics')
            row = await cursor.fetchone()
            count = row[0] if row else 0
            if count == 0:
                await cursor.execute(
                    """
                    INSERT INTO code_graph_metrics (id, total_nodes, total_edges)
                    VALUES (1, 0, 0)
                    """
                )
            elif count == 1:
                pass
            else:
                print_error(
                    'The code_graph_metrics table has more than one row. Please repair it manually.'
                )
                logger.error('code_graph_metrics has multiple rows, possible corruption')
                await conn.close()
                return False
            await conn.commit()
            await cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name;
                """
            )
            tables = [row[0] for row in await cursor.fetchall()]
            expected_tables = [
                "code_graph_edges",
                "code_graph_metrics",
                "code_graph_nodes",
                "sessions",
                "dream_insights",
                "dream_state",
                "task_sessions",
                "tasks",
                "technical_decisions",
                "runtime_state",
                "job_states",
            ]
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                print_error(f"Some tables were not created: {missing_tables}")
                return False
            logger.info(f"SQLite initialized with {len(tables)} tables")
            print_success(f"✅ SQLite database created with {len(tables)} tables")
            print_info(f"   Database location: {self.db_path}")

            # Store current system versions
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_versions (
                    id INTEGER PRIMARY KEY,
                    chunking_model TEXT,
                    embedding_model TEXT,
                    weaviate_schema TEXT
                )
            """
            )
            await cursor.execute("SELECT COUNT(*) FROM system_versions")
            row = await cursor.fetchone()
            count = row[0] if row else 0
            if count == 0:
                await cursor.execute(
                    "INSERT INTO system_versions (id, chunking_model, embedding_model, weaviate_schema) VALUES (1, ?, ?, ?)",
                    (
                        CURRENT_CHUNKING_MODEL_VERSION,
                        CURRENT_EMBEDDING_MODEL_VERSION,
                        CURRENT_WEAVIATE_SCHEMA_VERSION,
                    ),
                )
            await conn.commit()

            await conn.close()
            return True
        except Exception as e:
            logger.error("Error initializing SQLite", error=str(e))
            print_error(f"Failed to initialize SQLite: {e}")
            return False

    def load_weaviate_port(self) -> int:
        """Load Weaviate port from configuration"""
        try:
            config_file = self.global_dir / "projects" / self.project_id / ".acolyte"
            if config_file.exists():
                with open(config_file, "r") as f:
                    import yaml

                    config = yaml.safe_load(f)
                    return config.get("ports", {}).get("weaviate", 8080)
        except Exception:
            pass
        return 8080

    def init_weaviate(self) -> bool:
        """
        Initialize Weaviate with the necessary collections.

        Returns:
            True if initialization was successful
        """
        if not WEAVIATE_AVAILABLE:
            print_error("❌ Weaviate client not installed!")
            print_info("Install with: pip install weaviate-client")
            return False

        try:
            show_spinner("Initializing Weaviate collections...", 1.0)

            # Check if schemas file exists
            if not self.weaviate_schemas_path.exists():
                logger.error(f"Weaviate schema file not found at: {self.weaviate_schemas_path}")
                print_error("Weaviate schema file not found.")
                return False

            # Read Weaviate schemas
            with open(self.weaviate_schemas_path, "r", encoding="utf-8") as f:
                weaviate_config = json.load(f)

            # Connect to Weaviate (retry connection)
            weaviate_port = self.load_weaviate_port()
            weaviate_url = os.getenv("WEAVIATE_URL", f"http://localhost:{weaviate_port}")
            if Client is None:
                logger.error("Weaviate client is not available (import failed)")
                print_error("❌ Weaviate client is not available (import failed)!")
                return False
            ClientType = cast(type, Client)
            client = retry_sync(
                lambda: ClientType(url=weaviate_url),
                max_attempts=4,
                retry_on=(Exception,),
                logger=logger,
            )
            if client is None:
                logger.error("Weaviate client could not be created after retries")
                print_error("❌ Weaviate client could not be created after retries!")
                return False

            # Check connection
            if not client.is_ready():
                logger.error("Weaviate not available")
                print_error("❌ Weaviate is not running!")
                print_info("Start Weaviate with: docker-compose up -d weaviate")
                return False

            # Get existing collections
            try:
                existing_schema = client.schema.get()
                classes = cast(List[Dict[str, Any]], existing_schema.get("classes", []))
                existing_classes = {cls["class"] for cls in classes}
            except Exception:
                existing_classes = set()

            # Create each collection if it doesn't exist
            collections_created = 0
            collections_skipped = 0

            for collection_config in weaviate_config["collections"]:
                class_name = collection_config["class"]

                if class_name in existing_classes:
                    logger.info(f"Collection '{class_name}' already exists")
                    collections_skipped += 1
                    continue

                try:
                    # Add indexing config if present
                    if "indexing_config" in weaviate_config:
                        collection_config["vectorIndexType"] = weaviate_config[
                            "indexing_config"
                        ].get("vectorIndexType", "hnsw")
                        collection_config["vectorIndexConfig"] = weaviate_config[
                            "indexing_config"
                        ].get("vectorIndexConfig", {})

                    # Add replication config if present
                    if "replication_config" in weaviate_config:
                        collection_config["replicationConfig"] = weaviate_config[
                            "replication_config"
                        ]

                    # Add sharding config if present
                    if "sharding_config" in weaviate_config:
                        collection_config["shardingConfig"] = weaviate_config["sharding_config"]

                    # Construir tuple de excepciones solo con tipos válidos
                    retry_exceptions = (Exception,)
                    if UnexpectedStatusCodeException is not None:
                        retry_exceptions = (UnexpectedStatusCodeException, Exception)

                    retry_sync(
                        lambda: client.schema.create_class(collection_config),
                        max_attempts=3,
                        retry_on=retry_exceptions,
                        logger=logger,
                    )
                    logger.info(f"Created collection '{class_name}'")
                    collections_created += 1

                except UnexpectedStatusCodeException as e:  # type: ignore
                    logger.error(f"Error creating collection '{class_name}'", error=str(e))
                    print_error(f"Failed to create collection '{class_name}': {e}")
                    return False

            print_success(
                f"✅ Weaviate initialized: {collections_created} new, {collections_skipped} existing"
            )
            print_info(f"   Weaviate URL: {weaviate_url}")

            return True

        except Exception as e:
            logger.error("Error initializing Weaviate", error=str(e))
            print_error(f"Failed to initialize Weaviate: {e}")
            return False

    async def verify_installation(self) -> Dict[str, Any]:
        """
        Verify that both databases are correctly installed.
        Uso: await db.verify_installation() o asyncio.run(db.verify_installation())
        """
        status = {
            "sqlite": {"ok": False, "tables": 0, "error": None},
            "weaviate": {"ok": False, "collections": 0, "error": None},
        }
        try:
            if self.db_path.exists():
                conn = await self._create_connection()
                cursor = await conn.cursor()
                await cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                row = await cursor.fetchone()
                table_count = row[0] if row else 0
                await conn.close()
                status["sqlite"]["ok"] = table_count >= 12
                status["sqlite"]["tables"] = table_count
                # Check version compatibility as part of verification
                try:
                    await self.check_version_compatibility()
                except VersionIncompatibilityError as e:
                    # Don't fail verification, but report the incompatibility
                    status["sqlite"]["version_warning"] = str(e)
                    logger.warning(
                        "Version incompatibility detected during verification", error=str(e)
                    )
            else:
                status["sqlite"]["error"] = "Database file does not exist"
        except Exception as e:
            status["sqlite"]["error"] = str(e)
        if WEAVIATE_AVAILABLE and Client is not None:
            try:
                weaviate_port = self.load_weaviate_port()
                weaviate_url = os.getenv("WEAVIATE_URL", f"http://localhost:{weaviate_port}")
                client = Client(url=weaviate_url)  # type: ignore
                if client.is_ready():
                    schema = client.schema.get()
                    collection_count = len(schema.get("classes", []))
                    status["weaviate"]["ok"] = collection_count >= 5
                    status["weaviate"]["collections"] = collection_count
                else:
                    status["weaviate"]["error"] = "Weaviate is not available"
            except Exception as e:
                status["weaviate"]["error"] = str(e)
        return status

    async def run(self, skip_weaviate: bool = False) -> bool:
        """
        Run the complete database initialization.

        Args:
            skip_weaviate: Skip Weaviate initialization (for testing)

        Returns:
            True if all initializations were successful
        """
        print_info("🗄️ Initializing ACOLYTE databases...")

        # Initialize SQLite
        sqlite_ok = await self.init_sqlite()
        if not sqlite_ok:
            logger.error("SQLite initialization failed")
            return False

        # Initialize Weaviate (unless skipped)
        if not skip_weaviate:
            weaviate_ok = self.init_weaviate()
            if not weaviate_ok:
                logger.warning("Weaviate initialization failed - continuing anyway")
                print_info("⚠️ Weaviate initialization failed but SQLite is ready")
                print_info("You can initialize Weaviate later when Docker is running")
                return True  # Still return True as SQLite is the critical component
        else:
            print_info("Skipping Weaviate initialization")

        # Verify installation
        print_info("\n📊 Verifying installation...")
        status = await self.verify_installation()

        if status["sqlite"]["ok"]:
            print_success(f"✅ SQLite: {status['sqlite']['tables']} tables")
        else:
            print_error(f"❌ SQLite: {status['sqlite']['error']}")

        if not skip_weaviate:
            if status["weaviate"]["ok"]:
                print_success(f"✅ Weaviate: {status['weaviate']['collections']} collections")
            else:
                print_error(f"❌ Weaviate: {status['weaviate']['error']}")

        success = status["sqlite"]["ok"] and (skip_weaviate or status["weaviate"]["ok"])

        if success:
            print_success("\n✅ Database initialization complete!")
        else:
            print_error("\n❌ Database initialization incomplete")

        return success

    async def check_version_compatibility(self) -> bool:
        """Check if stored system versions match current config.

        Returns:
            True if versions are compatible

        Raises:
            VersionIncompatibilityError: If versions don't match
        """
        try:
            conn = await self._create_connection()
            cursor = await conn.cursor()

            # Check if system_versions table exists
            await cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='system_versions'"
            )
            if not await cursor.fetchone():
                logger.warning("system_versions table does not exist, skipping version check")
                await conn.close()
                return True

            await cursor.execute(
                "SELECT chunking_model, embedding_model, weaviate_schema FROM system_versions WHERE id=1"
            )
            row = await cursor.fetchone()
            await conn.close()

            current = {
                "chunking_model": CURRENT_CHUNKING_MODEL_VERSION,
                "embedding_model": CURRENT_EMBEDDING_MODEL_VERSION,
                "weaviate_schema": CURRENT_WEAVIATE_SCHEMA_VERSION,
            }

            if row:
                stored = {
                    "chunking_model": row[0],
                    "embedding_model": row[1],
                    "weaviate_schema": row[2],
                }

                if stored != current:
                    logger.error(
                        "Version incompatibility detected",
                        stored_versions=stored,
                        current_versions=current,
                    )
                    stored_str = {k: str(v) for k, v in stored.items()}
                    current_str = {k: str(v) for k, v in current.items()}
                    raise VersionIncompatibilityError(stored_str, current_str)

                logger.info("Version compatibility check passed", versions=current)
            else:
                logger.warning("No version information found in database")

            return True

        except VersionIncompatibilityError:
            # Re-raise our custom exception
            raise
        except Exception as e:
            logger.error("Error checking version compatibility", error=str(e))
            # Don't fail on version check errors, just warn
            return True


async def initialize_databases(
    project_path: Path,
    project_id: str,
    global_dir: Optional[Path] = None,
    skip_weaviate: bool = False,
) -> bool:
    """
    Inicializa las bases de datos. Uso: await initialize_databases(...) o asyncio.run(...)

    Raises:
        VersionIncompatibilityError: If version mismatch is detected
    """
    db = DatabaseInitializer(project_path, project_id, global_dir)
    ok = await db.init_sqlite()
    if not ok:
        return False
    # Check version compatibility after init
    # This may raise VersionIncompatibilityError which the caller should handle
    await db.check_version_compatibility()
    if not skip_weaviate:
        ok = db.init_weaviate()
        if not ok:
            return False
    return True
