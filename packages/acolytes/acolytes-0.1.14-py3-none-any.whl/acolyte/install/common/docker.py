#!/usr/bin/env python3
"""
Docker and GPU detection utilities for ACOLYTE
"""

from pathlib import Path
from typing import Dict, List, cast, Any

import yaml
from acolyte.core.logging import logger


class GPUDetector:
    """Detects GPU libraries for Docker volume mounting"""

    @staticmethod
    def find_nvidia_libraries() -> Dict[str, List[str]]:
        """Find NVIDIA libraries and devices"""
        libraries: Dict[str, List[str]] = {"volumes": [], "devices": []}

        # Common NVIDIA library paths
        lib_paths = [
            "/usr/lib/x86_64-linux-gnu",
            "/usr/lib64",
            "/usr/local/cuda/lib64",
            "/usr/lib",
            "/lib/x86_64-linux-gnu",
        ]

        # Libraries to find
        required_libs = ["libcuda.so", "libnvidia-ml.so"]

        for lib_path in lib_paths:
            lib_dir = Path(lib_path)
            if not lib_dir.exists():
                continue

            for lib_name in required_libs:
                # Find all versions of the library
                lib_files = list(lib_dir.glob(f"{lib_name}*"))
                if lib_files:
                    # Get the actual library file (follow symlinks)
                    for lib_file in lib_files:
                        if lib_file.is_file():
                            actual_file = lib_file.resolve()
                            # Mount both the actual file and symlinks
                            libraries["volumes"].append(f"{actual_file}:{lib_file}")
                            if lib_file != actual_file:
                                libraries["volumes"].append(f"{actual_file}:{actual_file}")
                            break

        # NVIDIA devices
        nvidia_devices = [
            "/dev/nvidia0",
            "/dev/nvidiactl",
            "/dev/nvidia-modeset",
            "/dev/nvidia-uvm",
        ]

        for device in nvidia_devices:
            if Path(device).exists():
                libraries["devices"].append(f"{device}:{device}")

        return libraries


class DockerGenerator:
    """Generates Docker Compose configuration for project infrastructure"""

    def __init__(self, config: Dict, project_dir: Path):
        self.config = config
        self.project_dir = project_dir  # This is ~/.acolyte/projects/{project_id}/
        self.user_project_path = Path(config['project']['path'])  # User's actual project

    def _get_pip_install_command(self, use_testpypi: bool = False) -> str:
        """Generate appropriate pip install command based on environment"""
        if use_testpypi:
            # For TestPyPI, install dependencies from PyPI first, then acolytes without deps
            return """# Install dependencies from PyPI (TestPyPI has unreliable packages)
RUN pip install --no-cache-dir \\
    fastapi>=0.110.0 \\
    pydantic>=2.6.0 \\
    loguru>=0.7.2 \\
    gitpython>=3.1.40 \\
    "uvicorn[standard]>=0.29.0" \\
    pyyaml>=6.0.0 \\
    numpy>=2.3.0 \\
    transformers>=4.52.4 \\
    aiohttp>=3.9.0 \\
    asyncio>=3.4.3 \\
    psutil>=7.0.0 \\
    tree-sitter>=0.20.4 \\
    tree-sitter-languages>=1.10.2 \\
    torch>=2.7.1 \\
    click>=8.1.0 \\
    rich>=13.0.0 \\
    tqdm>=4.66.0 \\
    requests>=2.31.0 \\
    "weaviate-client>=3.26.7,<4.0.0"

# Install acolytes from TestPyPI without dependencies
RUN pip install --index-url https://test.pypi.org/simple/ --no-deps acolytes"""
        else:
            # For production PyPI, simple install
            return "RUN pip install --no-cache-dir acolytes"

    def generate_compose(self) -> Dict:
        """Generate docker-compose.yml configuration"""
        docker_config = self.config["docker"]
        gpu_config = self.config["hardware"].get("gpu")

        # Get port configuration
        weaviate_port = self.config.get("ports", {}).get("weaviate", 42080)
        ollama_port = self.config.get("ports", {}).get("ollama", 42434)
        backend_port = self.config.get("ports", {}).get("backend", 42000)

        # Get ACOLYTE source directory (always ~/.acolyte)
        acolyte_src = str(Path.home() / ".acolyte")

        # Base compose configuration
        compose = {
            "services": {
                "weaviate": {
                    "image": "cr.weaviate.io/semitechnologies/weaviate:1.24.1",
                    "container_name": "acolyte-weaviate",
                    "restart": "unless-stopped",
                    "ports": [f"{weaviate_port}:8080", "50051:50051"],
                    "environment": [
                        "QUERY_DEFAULTS_LIMIT=25",
                        "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true",
                        "PERSISTENCE_DATA_PATH=/var/lib/weaviate",
                        "DEFAULT_VECTORIZER_MODULE=none",
                        "ENABLE_MODULES=none",
                        "ENABLE_API_BASED_MODULES=true",
                        "CLUSTER_HOSTNAME=node1",
                        "LOG_LEVEL=warn",
                    ],
                    "volumes": ["./weaviate:/var/lib/weaviate"],
                    "healthcheck": {
                        "test": [
                            "CMD",
                            "wget",
                            "-qO-",
                            "http://localhost:8080/v1/.well-known/ready",
                        ],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    },
                },
                "ollama": {
                    "image": "ollama/ollama:latest",
                    "container_name": "acolyte-ollama",
                    "restart": "unless-stopped",
                    "ports": [f"{ollama_port}:11434"],
                    "volumes": ["./ollama:/root/.ollama"],
                    "environment": [
                        "NVIDIA_VISIBLE_DEVICES=all",
                        "GODEBUG=x509ignoreCN=0",
                        "OLLAMA_DEBUG=INFO",
                        "OLLAMA_CONTEXT_LENGTH=4096",
                    ],
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": docker_config["cpu_limit"],
                                "memory": docker_config["memory_limit"],
                            },
                            "reservations": {
                                "devices": (
                                    [{"driver": "nvidia", "count": "all", "capabilities": ["gpu"]}]
                                    if docker_config.get("gpu_enabled") and gpu_config
                                    else []
                                )
                            },
                        }
                    },
                },
                "backend": {
                    "build": self._get_backend_build_config(acolyte_src),
                    "container_name": "acolyte-backend",
                    "restart": "unless-stopped",
                    "ports": [f"{backend_port}:8000"],
                    "environment": [
                        "WEAVIATE_URL=http://weaviate:8080",
                        "OLLAMA_URL=http://ollama:11434",
                        "OLLAMA_MODEL=acolyte",
                        "PYTHONUNBUFFERED=1",
                        f"ACOLYTE_PROJECT_ROOT={self.user_project_path}",
                        "DATA_DIR=/data",
                    ],
                    "volumes": self._get_backend_volumes(acolyte_src),
                    "depends_on": {"weaviate": {"condition": "service_healthy"}},
                    "healthcheck": {
                        "test": [
                            "CMD",
                            "curl",
                            "-f",
                            "http://localhost:8000/api/health",
                        ],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    },
                },
            },
            "volumes": {
                "weaviate-data": {"driver": "local"},
                "ollama-models": {"driver": "local"},
            },
            "networks": {"acolyte-network": {"driver": "bridge"}},
        }

        # Add GPU support if available
        if docker_config.get("gpu_enabled") and gpu_config:
            if gpu_config["type"] == "nvidia":
                # Add nvidia runtime for GPU support
                services = cast(Dict[str, Any], compose["services"])
                ollama_service = cast(Dict[str, Any], services["ollama"])

                # Add runtime for nvidia-docker
                ollama_service["runtime"] = "nvidia"

                # Auto-detect GPU libraries
                gpu_libs = GPUDetector.find_nvidia_libraries()
                gpu_libs = cast(Dict[str, List[str]], gpu_libs)

                if isinstance(gpu_libs, dict) and "volumes" in gpu_libs and gpu_libs["volumes"]:
                    ollama_service["volumes"].extend(gpu_libs["volumes"])
                    logger.info(f"Added {len(gpu_libs['volumes'])} GPU library volumes")

                if isinstance(gpu_libs, dict) and "devices" in gpu_libs and gpu_libs["devices"]:
                    ollama_service["devices"] = gpu_libs["devices"]
                    logger.info(f"Added {len(gpu_libs['devices'])} GPU devices")

        # Add network to all services
        services = cast(Dict[str, Any], compose["services"])
        for service in services.values():
            service["networks"] = ["acolyte-network"]

        compose = cast(Dict[str, Any], compose)
        return compose

    def _get_backend_build_config(self, acolyte_src: str) -> Dict[str, str]:
        """Get backend build configuration based on installation mode."""
        # Check common development locations
        possible_locations = [
            Path.home() / "Desktop" / "acolyte-project",
            Path.home() / "Documents" / "acolyte-project",
            Path.home() / "dev" / "acolyte-project",
            Path.home() / "projects" / "acolyte-project",
        ]

        for location in possible_locations:
            if location.exists() and (location / "src" / "acolyte").exists():
                # Development mode - build from source project
                return {
                    "context": str(location),
                    "dockerfile": str(Path(acolyte_src) / "Dockerfile"),
                }

        # Production mode - build from ACOLYTE installation
        return {
            "context": acolyte_src,
            "dockerfile": "./Dockerfile",
        }

    def _get_backend_volumes(self, acolyte_src: str) -> List[str]:
        """Get backend volumes based on installation mode."""
        volumes = [
            f"{self.project_dir}/.acolyte:/.acolyte:ro",  # Project config
            f"{self.project_dir}/data:/data",  # Project data
            f"{self.user_project_path}:/project:ro",  # User's project (read-only)
        ]

        # Only mount source code if it exists (development mode)
        src_path = Path(acolyte_src) / "src"
        if src_path.exists():
            volumes.insert(0, f"{acolyte_src}/src:/app/src:ro")  # ACOLYTE source code (read-only)

        return volumes

    def save_compose(self, compose: Dict) -> bool:
        """Save docker-compose.yml file"""
        try:
            # Create infra directory
            infra_dir = self.project_dir / "infra"
            infra_dir.mkdir(parents=True, exist_ok=True)

            compose_file = infra_dir / "docker-compose.yml"

            # Backup if exists
            if compose_file.exists():
                backup_file = compose_file.with_suffix(".yml.backup")
                import shutil

                shutil.copy2(compose_file, backup_file)
                logger.info(f"Created backup: {backup_file}")

            with open(compose_file, "w", encoding="utf-8") as f:
                yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Docker compose file saved: {compose_file}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Error saving docker-compose.yml: {type(e).__name__}: {e}")
            return False
        except yaml.YAMLError as e:
            logger.error(f"Error serializing docker-compose.yml: {e}")
            return False

    def generate_global_dockerfile(self, use_testpypi: bool = False) -> bool:
        """Generate Dockerfile for backend service in ACOLYTE installation"""
        try:
            # This goes in the global ACOLYTE installation, not in project
            acolyte_src = str(Path.home() / ".acolyte")

            # Find the actual ACOLYTE source code directory
            # First check if running from source (development)
            acolyte_project_dir = None

            # Check common development locations
            possible_locations = [
                Path.home() / "Desktop" / "acolyte-project",
                Path.home() / "Documents" / "acolyte-project",
                Path.home() / "dev" / "acolyte-project",
                Path.home() / "projects" / "acolyte-project",
                Path.cwd().parent if Path.cwd().name == "acolyte-project" else None,
            ]

            for location in possible_locations:
                if location and location.exists() and (location / "src" / "acolyte").exists():
                    acolyte_project_dir = location
                    logger.info(f"Found ACOLYTE source at: {acolyte_project_dir}")
                    break

            # Check if src directory exists (development mode)
            src_exists = (Path(acolyte_src) / "src").exists() or acolyte_project_dir is not None

            if src_exists and acolyte_project_dir:
                # Development mode - build from local source
                dockerfile_content = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    gcc \\
    g++ \\
    make \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 acolyte

# Create necessary directories with correct permissions
RUN mkdir -p /data/logs /data/dreams /data/embeddings_cache && \\
    chown -R acolyte:acolyte /data

# Set working directory
WORKDIR /app

# Copy only necessary files first for better caching
COPY --chown=acolyte:acolyte requirements.txt* pyproject.toml* README.md* /app/

# Install dependencies using requirements.txt if it exists
RUN if [ -f requirements.txt ]; then \\
        pip install --no-cache-dir -r requirements.txt; \\
    else \\
        pip install --no-cache-dir poetry && \\
        poetry config virtualenvs.create false && \\
        poetry install --no-interaction --no-ansi; \\
    fi

# Copy the rest of the project
COPY --chown=acolyte:acolyte . /app/

USER acolyte

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/data
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Expose port (API always runs on 8000 internally)
EXPOSE 8000

# Set working directory to root for database path resolution
WORKDIR /

# Run the API using the local code
CMD ["python", "-m", "acolyte.api"]
"""
            else:
                # Production mode - install from pip
                dockerfile_content = f"""FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    gcc \\
    g++ \\
    make \\
    && rm -rf /var/lib/apt/lists/*

# Install acolytes
{self._get_pip_install_command(use_testpypi)}

# Create non-root user
RUN useradd -m -u 1000 acolyte

# Create necessary directories with correct permissions
RUN mkdir -p /data/logs /data/dreams /data/embeddings_cache && \\
    chown -R acolyte:acolyte /data

USER acolyte

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/data

# Expose port (API always runs on 8000 internally)
EXPOSE 8000

# Set working directory to root for database path resolution  
WORKDIR /

# Run the API using the installed acolyte module
CMD ["python", "-m", "acolyte.api"]
"""

            dockerfile_path = Path(acolyte_src) / "Dockerfile"

            # Backup if exists
            if dockerfile_path.exists():
                backup_path = dockerfile_path.with_suffix(".backup")
                import shutil

                shutil.copy2(dockerfile_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

            with open(dockerfile_path, "w", encoding="utf-8") as f:
                f.write(dockerfile_content)

            logger.info(f"Dockerfile created: {dockerfile_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating Dockerfile: {e}")
            return False
