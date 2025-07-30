"""Type stubs for database module"""

from pathlib import Path
from typing import Dict, Any, Optional

class DatabaseInitializer:
    project_path: Path
    project_id: str
    global_dir: Path
    project_data_dir: Path
    db_path: Path
    schemas_path: Path
    weaviate_schemas_path: Path

    def __init__(
        self, project_path: Path, project_id: str, global_dir: Optional[Path] = None
    ) -> None: ...
    def ensure_directories(self) -> bool: ...
    def init_sqlite(self) -> bool: ...
    def load_weaviate_port(self) -> int: ...
    def init_weaviate(self) -> bool: ...
    async def verify_installation(self) -> Dict[str, Any]: ...
    async def run(self, skip_weaviate: bool = False) -> bool: ...
    async def check_version_compatibility(self) -> bool: ...

async def initialize_databases(
    project_path: Path,
    project_id: str,
    global_dir: Optional[Path] = None,
    skip_weaviate: bool = False,
) -> bool: ...
