"""
Doctor command for ACOLYTE: advanced diagnostics and repair.
"""

import sys
import subprocess
import time
from pathlib import Path
import shutil
import yaml

from rich.console import Console


class DiagnoseSystem:
    """System-level diagnostics."""

    def __init__(self, console: Console, fix: bool):
        self.console = console
        self.fix = fix

    def check_docker_daemon(self):
        """Check if Docker daemon is running."""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.console.print("[red]✗ Docker daemon is not running[/red]")
                if self.fix:
                    self.fix_docker_daemon()
            else:
                self.console.print("[green]✓ Docker daemon is running[/green]")
        except Exception:
            self.console.print("[red]✗ Docker is not accessible[/red]")

    def fix_docker_daemon(self):
        """Attempt to start Docker daemon."""
        import shutil

        if sys.platform == "win32":
            docker_desktop = shutil.which("Docker Desktop.exe")
            tried_paths = []
            if not docker_desktop:
                # Try common install paths
                possible_paths = [
                    r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                    r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Docker\Docker Desktop.exe",
                ]
                for path in possible_paths:
                    tried_paths.append(path)
                    if Path(path).exists():
                        docker_desktop = path
                        break
            try:
                if docker_desktop:
                    subprocess.Popen([docker_desktop])
                    self.console.print("[yellow]⚠ Starting Docker Desktop...[/yellow]")
                    time.sleep(10)
                else:
                    self.console.print(
                        f"[red]Could not find Docker Desktop executable. Tried: {tried_paths}[/red]"
                    )
            except Exception as e:
                self.console.print(f"[red]Could not start Docker Desktop: {e}[/red]")
        elif sys.platform == "darwin":
            try:
                subprocess.run(["open", "-a", "Docker"])
                self.console.print("[yellow]⚠ Starting Docker...[/yellow]")
                time.sleep(10)
            except Exception as e:
                self.console.print(f"[red]Could not start Docker.app: {e}[/red]")
        else:
            try:
                subprocess.run(["sudo", "systemctl", "start", "docker"])
                self.console.print("[yellow]⚠ Starting Docker service...[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Could not start Docker service: {e}[/red]")

    def check_disk_space(self):
        """Check available disk space."""
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        if free_gb < 5:
            self.console.print(f"[red]✗ Low disk space: {free_gb}GB free[/red]")
            self.console.print("  You need at least 10GB for ACOLYTE")
            if self.fix:
                self.suggest_cleanup()
        else:
            self.console.print(f"[green]✓ Disk space: {free_gb}GB free[/green]")

    def suggest_cleanup(self):
        """Suggest user to clean up disk space."""
        self.console.print(
            "[yellow]Suggestion: clean up temporary files or uninstall unnecessary programs.[/yellow]"
        )

    def check_basic_requirements(self):
        """Check basic system requirements."""
        import shutil

        # Check acolyte command
        acolyte_path = shutil.which('acolyte')
        if acolyte_path is None:
            self.console.print("[red]✗ ACOLYTE command not found in PATH[/red]")
            self.console.print("  Fix: Add Scripts/ or bin/ directory to your PATH")
        else:
            self.console.print(f"[green]✓ ACOLYTE command: Found at {acolyte_path}[/green]")

        # Check Docker
        docker_path = shutil.which('docker')
        if docker_path is None:
            self.console.print("[red]✗ Docker not installed[/red]")
            self.console.print("  Fix: Install Docker Desktop from https://docker.com")
        else:
            self.console.print("[green]✓ Docker: Available[/green]")

        # Check Git
        git_path = shutil.which('git')
        if git_path is None:
            self.console.print("[red]✗ Git not installed[/red]")
            self.console.print("  Fix: Install Git from https://git-scm.com")
        else:
            self.console.print("[green]✓ Git: Available[/green]")

        # Check Python version
        if sys.version_info < (3, 11):
            self.console.print(
                f"[red]✗ Python {sys.version_info.major}.{sys.version_info.minor} found, 3.11+ required[/red]"
            )
            self.console.print("  Fix: Upgrade to Python 3.11 or newer")
        else:
            self.console.print("[green]✓ Python version: Compatible[/green]")

        # Check ACOLYTE home
        acolyte_home = Path.home() / ".acolyte"
        if not acolyte_home.exists():
            self.console.print("[red]✗ ~/.acolyte directory not found[/red]")
            self.console.print("  Fix: Reinstall ACOLYTE or run 'acolyte init'")
            if self.fix:
                acolyte_home.mkdir(parents=True, exist_ok=True)
                self.console.print("[green]✓ Created ~/.acolyte directory[/green]")
        else:
            self.console.print("[green]✓ ACOLYTE home: Found[/green]")

    def check_ports(self):
        """Check common ACOLYTE ports."""
        ports = {42000: "Backend API", 42080: "Weaviate", 42434: "Ollama"}
        for port, service in ports.items():
            if self.is_port_in_use(port):
                self.console.print(f"[yellow]⚠ Port {port} ({service}) is in use[/yellow]")
                if self.fix:
                    free_port = self.find_next_free_port(port)
                    self.console.print(f"  Suggestion: use port {free_port}")
            else:
                self.console.print(f"[green]✓ Port {port} is free ({service})[/green]")

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if a port is in use on localhost."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    @staticmethod
    def find_next_free_port(start_port: int) -> int:
        """Find the next available port after start_port."""
        import socket

        port = start_port + 1
        while port < 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", port)) != 0:
                    return port
            port += 1
        return -1

    def check_docker_resources(self, min_memory_gb: float = 4.0, min_cpus: int = 2):
        _check_docker_resources(self.console, min_memory_gb, min_cpus)


class DiagnoseProject:
    """Project-level diagnostics."""

    def __init__(self, console: Console, fix: bool, project_dir: Path):
        self.console = console
        self.fix = fix
        self.project_dir = project_dir

    def check_installation_state(self):
        """Check the installation state file for incomplete installs."""
        state_file = self.project_dir / "install_state.yaml"
        if state_file.exists():
            with open(state_file) as f:
                state = yaml.safe_load(f)
            current_step = state.get('current_step')
            if current_step:
                self.console.print(
                    f"[yellow]⚠ Incomplete installation at step: {current_step}[/yellow]"
                )
                if self.fix:
                    self.console.print("  Run: [cyan]acolyte install --repair[/cyan]")

    def check_corrupted_files(self):
        """Check for empty or corrupted critical files."""
        critical_files = [".acolyte", "infra/docker-compose.yml", "data/acolyte.db"]
        for file_path in critical_files:
            full_path = self.project_dir / file_path
            if full_path.exists() and full_path.stat().st_size == 0:
                self.console.print(f"[red]✗ Empty file: {file_path}[/red]")
                if self.fix:
                    self.fix_corrupted_file(full_path)

    def fix_corrupted_file(self, path: Path):
        """Delete a corrupted or empty file."""
        try:
            path.unlink()
            self.console.print(f"[green]✓ File deleted: {path}[/green]")
        except Exception:
            self.console.print(f"[red]Could not delete: {path}[/red]")

    def check_docker_images(self):
        """Check for required Docker images."""
        required_images = ["weaviate/weaviate:latest", "ollama/ollama:latest"]
        for image in required_images:
            result = subprocess.run(
                ["docker", "images", "-q", image], capture_output=True, text=True
            )
            if not result.stdout.strip():
                self.console.print(f"[yellow]⚠ Missing image: {image}[/yellow]")
                if self.fix:
                    self.console.print(f"  Downloading {image}...")
                    subprocess.run(["docker", "pull", image], text=True)


class DiagnoseServices:
    """Service-level diagnostics."""

    def __init__(self, console: Console, fix: bool):
        self.console = console
        self.fix = fix

    def check_container_health(self):
        """Check the health of running containers."""
        containers = ["acolyte-backend", "acolyte-weaviate", "acolyte-ollama"]
        for container in containers:
            result = subprocess.run(
                ["docker", "inspect", container, "--format={{.State.Health.Status}}"],
                capture_output=True,
                text=True,
            )
            if "unhealthy" in result.stdout:
                self.console.print(f"[red]✗ Unhealthy container: {container}[/red]")
                if self.fix:
                    self.restart_container(container)
            else:
                self.console.print(f"[green]✓ Healthy container: {container}[/green]")

    def restart_container(self, container: str):
        """Restart a Docker container."""
        try:
            subprocess.run(["docker", "restart", container])
            self.console.print(f"[yellow]Restarting container: {container}[/yellow]")
        except Exception:
            self.console.print(f"[red]Could not restart: {container}[/red]")

    def check_logs_for_errors(self):
        """Check logs for common error patterns in containers."""
        error_patterns = {
            "OOMKilled": "Out of memory",
            "permission denied": "Permission denied",
            "address already in use": "Port already in use",
            "no space left": "No space left on device",
        }
        for container in ["acolyte-backend", "acolyte-weaviate", "acolyte-ollama"]:
            logs = self.get_container_logs(container, lines=50)
            for pattern, description in error_patterns.items():
                if pattern in logs:
                    self.console.print(f"[red]✗ Error in {container}: {description}[/red]")
                    if self.fix:
                        self.suggest_fix_for_error(pattern, container)

    def get_container_logs(self, container: str, lines: int = 50) -> str:
        """Get the last N lines of logs from a container."""
        try:
            result = subprocess.run(
                ["docker", "logs", container, f"--tail={lines}"], capture_output=True, text=True
            )
            return result.stdout
        except Exception:
            return ""

    def suggest_fix_for_error(self, pattern: str, container: str):
        """Suggest a fix for a detected error pattern."""
        self.console.print(
            f"[yellow]Suggestion: check the configuration or restart the container {container}.[/yellow]"
        )


def get_model_requirements(model_name: str) -> dict:
    """Return required memory (GB) and CPUs for a given model name."""
    docker_requirements = {
        "qwen2.5-coder:3b": {"memory_gb": 4, "cpus": 2},
        "qwen2.5-coder:7b": {"memory_gb": 8, "cpus": 4},
        "qwen2.5-coder:14b": {"memory_gb": 16, "cpus": 8},
        "qwen2.5-coder:32b": {"memory_gb": 32, "cpus": 16},
        # Add more models as needed
    }
    return docker_requirements.get(model_name, {"memory_gb": 4, "cpus": 2})  # Default fallback


def _check_docker_resources(console, min_memory_gb: float, min_cpus: int, model_name: str = ""):
    """Check Docker Desktop assigned resources and warn if below recommended/required."""
    import subprocess
    import re

    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[Warning] Could not get Docker info. Is Docker running?")
            return
        mem_match = re.search(r"Total Memory:\s+([0-9.]+)GiB", result.stdout)
        cpu_match = re.search(r"CPUs:\s+(\d+)", result.stdout)
        if mem_match:
            mem_gb = float(mem_match.group(1))
            if mem_gb < min_memory_gb:
                if model_name:
                    console.print(
                        f"[Warning] Docker has only {mem_gb}GB assigned. Required for {model_name}: {min_memory_gb}GB or more."
                    )
                else:
                    console.print(
                        f"[Warning] Docker has only {mem_gb}GB assigned. Recommended: {min_memory_gb}GB or more."
                    )
        if cpu_match:
            cpus = int(cpu_match.group(1))
            if cpus < min_cpus:
                if model_name:
                    console.print(
                        f"[Warning] Docker has only {cpus} CPUs assigned. Required for {model_name}: {min_cpus} or more."
                    )
                else:
                    console.print(
                        f"[Warning] Docker has only {cpus} CPUs assigned. Recommended: {min_cpus} or more."
                    )
    except Exception as e:
        console.print(f"[Warning] Could not check Docker resources: {e}")


def check_docker_resources_dynamic(model_name: str, console=None):
    """Check Docker Desktop assigned resources against model requirements."""
    if console is None:
        from rich.console import Console

        console = Console()
    reqs = get_model_requirements(model_name)
    min_memory_gb = reqs["memory_gb"]
    min_cpus = reqs["cpus"]
    _check_docker_resources(console, min_memory_gb, min_cpus, model_name or "")


def run_doctor(fix: bool = False, project: str = "."):
    """Main entry point for the doctor command."""
    console = Console()
    console.print("[bold cyan]🩺 ACOLYTE Doctor - Advanced Diagnostics[/bold cyan]\n")

    # 1. Basic requirements check
    console.print("[bold]1. Basic Requirements[/bold]")
    system_health = DiagnoseSystem(console, fix)
    system_health.check_basic_requirements()

    # 2. System diagnostics
    console.print("\n[bold]2. System Diagnostics[/bold]")
    system_health.check_docker_daemon()
    system_health.check_disk_space()
    system_health.check_ports()
    # Detect model name from config or Modelfile
    import yaml
    from pathlib import Path

    model_name = None
    config_path = Path.cwd() / '.acolyte'
    if config_path.exists():
        try:
            with config_path.open('r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            model_name = config.get('model', {}).get('name')
        except yaml.YAMLError as e:
            console.print(f"[yellow]Warning: Could not parse .acolyte YAML: {e}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Warning: Error reading .acolyte: {e}[/yellow]")
    if not model_name:
        # Try to read from Modelfile (robust parsing)
        modelfile_path = Path.cwd() / 'Modelfile'
        if modelfile_path.exists():
            try:
                with modelfile_path.open('r', encoding='utf-8') as f:
                    for line in f:
                        if 'FROM' in line:
                            candidate = line.split('FROM', 1)[-1].strip()
                            if candidate:
                                model_name = candidate
                                break
                if not model_name:
                    console.print(
                        "[yellow]Warning: No valid model name found in Modelfile.[/yellow]"
                    )
            except Exception as e:
                console.print(f"[yellow]Warning: Error reading Modelfile: {e}[/yellow]")
    if not model_name:
        console.print(
            "[yellow]Warning: Could not detect model, using default 'qwen2.5-coder:3b'.[/yellow]"
        )
        model_name = 'qwen2.5-coder:3b'  # Default fallback
    check_docker_resources_dynamic(model_name, console)

    # 3. Project diagnostics (if in a project directory)
    project_path = Path(project)
    # Check if it's an ACOLYTE project
    if (project_path / ".acolyte.project").exists():
        console.print("\n[bold]3. Project Diagnostics[/bold]")
        # Find the global project directory
        try:
            with open(project_path / ".acolyte.project") as f:
                project_info = yaml.safe_load(f)
            project_id = project_info.get('project_id')
            if project_id:
                global_project_dir = Path.home() / ".acolyte" / "projects" / project_id
                if global_project_dir.exists():
                    project_health = DiagnoseProject(console, fix, global_project_dir)
                    project_health.check_installation_state()
                    project_health.check_corrupted_files()
                    project_health.check_docker_images()
                else:
                    console.print("[yellow]⚠ Project directory not found in ~/.acolyte[/yellow]")
        except Exception as e:
            console.print(f"[red]Error reading project info: {e}[/red]")
    else:
        console.print("\n[dim]No ACOLYTE project found in current directory[/dim]")

    # 4. Service diagnostics (only if Docker is running)
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=5)
        console.print("\n[bold]4. Service Diagnostics[/bold]")
        service_health = DiagnoseServices(console, fix)
        service_health.check_container_health()
        service_health.check_logs_for_errors()
    except Exception:
        console.print("\n[dim]Skipping service diagnostics (Docker not running)[/dim]")

    # Summary
    console.print("\n[bold green]✔ Diagnostics complete![/bold green]")
    if fix:
        console.print("[yellow]Auto-fix was enabled. Some issues may have been resolved.[/yellow]")
    console.print("\n[bold cyan]Tips:[/bold cyan]")
    console.print("• Run 'acolyte doctor --fix' to attempt automatic repairs")
    console.print("• Check logs with 'acolyte logs' for more details")
    console.print("• Use 'acolyte status' to check service status")
