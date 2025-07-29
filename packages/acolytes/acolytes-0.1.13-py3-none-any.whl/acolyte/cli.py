#!/usr/bin/env python3
"""
ACOLYTE CLI - Command Line Interface
Global tool for managing ACOLYTE in user projects
"""

import asyncio
import hashlib
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any

import click
import yaml
import requests

# LAZY IMPORTS - Only import when needed to speed up simple commands
logger = None


def get_logger():
    """Get logger instance lazily - only import when actually needed"""
    global logger
    if logger is None:
        from acolyte.core.logging import logger as _logger

        logger = _logger
    return logger


class ProjectManager:
    """Manages ACOLYTE projects and their configurations"""

    def __init__(self):
        self.global_dir = self._get_global_dir()
        self.projects_dir = self.global_dir / "projects"

        # Initialize global directory structure if needed
        self._ensure_global_structure()

    def _ensure_global_structure(self):
        """Ensure ACOLYTE global directory structure exists"""
        # Create directories
        self.global_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)

        # Create other necessary directories
        (self.global_dir / "models").mkdir(exist_ok=True)
        (self.global_dir / "logs").mkdir(exist_ok=True)

        # Copy essential files if this is first run
        if not (self.global_dir / ".initialized").exists():
            self._first_run_setup()

    def _first_run_setup(self):
        """Setup ACOLYTE on first run after pip install"""
        # Only log if we're actually doing initialization work
        log = get_logger()
        log.info("First run detected, initializing ACOLYTE...")

        # Copy example configurations
        examples_dir = Path(__file__).parent.parent.parent / "examples"
        if examples_dir.exists():
            dest_examples = self.global_dir / "examples"
            if dest_examples.exists():
                shutil.rmtree(dest_examples)
            shutil.copytree(examples_dir, dest_examples)

        # Mark as initialized
        (self.global_dir / ".initialized").touch()
        log.info(f"ACOLYTE initialized at {self.global_dir}")

    def _get_global_dir(self) -> Path:
        """Get the global ACOLYTE directory"""
        if os.name == 'nt':  # Windows
            return Path.home() / ".acolyte"
        else:  # Linux/Mac
            # Check if running from development or installed
            if 'ACOLYTE_DEV' in os.environ:
                return Path.home() / ".acolyte-dev"
            return Path.home() / ".acolyte"

    def get_project_id(self, project_path: Path) -> str:
        """Generate unique project ID from path and git remote"""
        # Try to get git remote
        git_remote = ""
        git_dir = project_path / ".git"
        if git_dir.exists():
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    git_remote = result.stdout.strip()
            except Exception:
                pass

        # Generate hash from absolute path + git remote
        abs_path = str(project_path.resolve())
        unique_string = f"{git_remote}:{abs_path}"
        project_id = hashlib.sha256(unique_string.encode()).hexdigest()[:12]

        return project_id

    def get_project_dir(self, project_id: str) -> Path:
        """Get the directory for a specific project"""
        return self.projects_dir / project_id

    def is_project_initialized(self, project_path: Path) -> bool:
        """Check if project is already initialized"""
        project_file = project_path / ".acolyte.project"
        return project_file.exists()

    def load_project_info(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Load project info from .acolyte.project"""
        project_file = project_path / ".acolyte.project"
        if not project_file.exists():
            return None

        try:
            with open(project_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Only log errors when we have actual errors
            log = get_logger()
            log.error(f"Failed to load project info: {e}")
            return None

    def save_project_info(self, project_path: Path, info: Dict[str, Any]) -> bool:
        """Save project info to .acolyte.project"""
        project_file = project_path / ".acolyte.project"
        try:
            with open(project_file, 'w') as f:
                yaml.dump(info, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            # Only log errors when we have actual errors
            log = get_logger()
            log.error(f"Failed to save project info: {e}")
            return False


def validate_project_directory(ctx, param, value):
    """Validate that we're in a valid project directory"""
    project_path = Path(value or ".")

    # Check if it's a git repository or has project files
    markers = [
        ".git",
        "package.json",
        "pyproject.toml",
        "setup.py",  # Python
        "Cargo.toml",  # Rust
        "go.mod",  # Go
        "pom.xml",
        "build.gradle",  # Java
        "composer.json",  # PHP
        "Gemfile",  # Ruby
    ]

    has_marker = any((project_path / marker).exists() for marker in markers)

    if not has_marker:
        raise click.BadParameter(
            "Not a valid project directory. Please run from a project with version control or project file."
        )

    return project_path


def detect_docker_compose_cmd() -> list[str]:
    """Detect the correct docker compose command"""
    # Try docker compose (newer versions)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return ["docker", "compose"]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback to docker-compose (older versions)
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return ["docker-compose"]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    raise click.ClickException(
        "Docker Compose not found. Please install Docker Desktop or docker-compose."
    )


def ensure_acolyte_model_exists(config: Dict[str, Any], infra_dir: Path, console) -> bool:
    """
    Ensure the acolyte model exists in Ollama.
    This function handles model creation in a centralized way.

    Returns:
        True if model exists or was created successfully, False otherwise
    """
    try:
        # Check if acolyte:latest exists
        model_check = subprocess.run(
            ["docker", "exec", "acolyte-ollama", "ollama", "list"],
            capture_output=True,
            text=True,
        )

        if model_check.returncode != 0:
            console.print("[yellow]⚠[/yellow] Could not check Ollama models")
            return False

        if "acolyte:latest" in model_check.stdout:
            console.print("[green]✓[/green] Model acolyte:latest already exists")
            return True

        # Model doesn't exist, create it
        console.print("[yellow]⚠[/yellow] Model 'acolyte:latest' not found, creating...")

        # Get base model name from config
        model_name = config.get('model', {}).get('name', 'qwen2.5-coder:3b')
        if model_name.startswith('acolyte:'):
            model_name = 'qwen2.5-coder:3b'  # Default base model

        # Pull base model if needed
        if model_name not in model_check.stdout:
            console.print(f"[dim]• Pulling base model {model_name}...[/dim]")
            pull_result = subprocess.run(
                ["docker", "exec", "acolyte-ollama", "ollama", "pull", model_name],
                text=True,
            )
            if pull_result.returncode != 0:
                console.print(f"[bold red]✗ Failed to pull {model_name}[/bold red]")
                return False
            console.print(f"[green]✓[/green] Base model {model_name} ready")

        # Copy Modelfile to container
        modelfile_path = infra_dir / "Modelfile"
        if not modelfile_path.exists():
            console.print("[yellow]⚠[/yellow] Modelfile not found at expected location")
            console.print(f"[dim]Expected: {modelfile_path}[/dim]")
            return False

        copy_result = subprocess.run(
            ["docker", "cp", str(modelfile_path), "acolyte-ollama:/tmp/Modelfile"],
            capture_output=True,
            text=True,
        )

        if copy_result.returncode != 0:
            console.print("[yellow]⚠[/yellow] Could not copy Modelfile to container")
            return False

        # Create the model
        console.print("[dim]• Creating acolyte:latest model...[/dim]")
        create_result = subprocess.run(
            [
                "docker",
                "exec",
                "acolyte-ollama",
                "ollama",
                "create",
                "acolyte:latest",
                "-f",
                "/tmp/Modelfile",
            ],
            text=True,
        )

        if create_result.returncode == 0:
            console.print("[green]✓[/green] Model acolyte:latest created successfully")
            return True
        else:
            console.print("[bold red]✗ Failed to create acolyte:latest model[/bold red]")
            return False

    except Exception as e:
        console.print(f"[bold red]✗ Error creating model: {e}[/bold red]")
        return False


# Lazy version loading for CLI
def _get_version():
    try:
        from acolyte._version import __version__

        return __version__
    except Exception:
        return "0.1.5"  # fallback


@click.group()
@click.version_option(version=_get_version(), prog_name="ACOLYTE")
def cli():
    """
    ACOLYTE - AI Programming Assistant

    Your local AI assistant with infinite memory for code projects.
    """
    pass


@cli.command()
@click.option('--path', default=".", help='Project path')
def index_tasks(path: str):
    """List resumable indexing tasks"""
    # Lazy import
    from acolyte.core.health import ServiceHealthChecker
    from rich.table import Table
    from rich.console import Console

    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        click.echo("Run 'acolyte init' first")
        sys.exit(1)

    # Load project info and config
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)
    config_file = project_dir / ".acolyte"

    if not config_file.exists():
        click.echo(click.style("✗ Project not configured!", fg="red"))
        click.echo("Run 'acolyte install' first")
        sys.exit(1)

    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        click.echo(click.style(f"✗ Failed to load configuration: {e}", fg="red"))
        sys.exit(1)

    # Check if backend is ready
    health_checker = ServiceHealthChecker(config)
    if not health_checker.wait_for_backend():
        click.echo(click.style("✗ Backend is not ready. Run 'acolyte start' first.", fg="red"))
        sys.exit(1)

    # Get resumable tasks
    try:
        backend_port = config['ports']['backend']
        url = f"http://localhost:{backend_port}/api/index/tasks"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])

            if not tasks:
                click.echo("No resumable indexing tasks found.")
                return

            # Create table
            console = Console()
            table = Table(title="Resumable Indexing Tasks")

            table.add_column("Task ID", style="cyan")
            table.add_column("Started", style="yellow")
            table.add_column("Progress", style="green")
            table.add_column("Pending Files", style="magenta")
            table.add_column("Last Checkpoint", style="blue")

            for task in tasks:
                progress_pct = (
                    task['processed_files'] / task['total_files'] * 100
                    if task['total_files'] > 0
                    else 0
                )
                progress_str = (
                    f"{task['processed_files']}/{task['total_files']} ({progress_pct:.1f}%)"
                )

                table.add_row(
                    task['task_id'],
                    task.get('started_at', 'Unknown'),
                    progress_str,
                    str(task.get('pending_files', 0)),
                    task.get('last_checkpoint', 'Unknown'),
                )

            console.print(table)
            console.print("\nTo resume a task, use: [cyan]acolyte index --resume TASK_ID[/cyan]")

        else:
            click.echo(click.style(f"✗ Failed to get tasks: {response.text}", fg="red"))
            sys.exit(1)

    except requests.RequestException as e:
        click.echo(click.style(f"✗ Failed to connect to backend: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    '--path',
    default=".",
    callback=validate_project_directory,
    help='Project path (default: current directory)',
)
@click.option('--name', help='Project name (default: directory name)')
@click.option('--force', is_flag=True, help='Force re-initialization')
def init(path: str, name: Optional[str], force: bool):
    """Initialize ACOLYTE in the current project"""
    # Lazy import heavy dependencies
    from acolyte.install.init import ProjectInitializer
    from acolyte.install.common import ACOLYTE_LOGO, animate_text

    project_path = Path(path)
    manager = ProjectManager()

    # Show logo with animation
    print(ACOLYTE_LOGO)
    animate_text(
        click.style("ACOLYTE INIT - Quick Project Setup", fg="cyan", bold=True),
        duration=1.0,
    )
    print("\n")

    click.echo(click.style("🤖 ACOLYTE Project Initialization", fg="cyan", bold=True))
    click.echo(f"Project path: {project_path.resolve()}")

    # Generate project ID
    project_id = manager.get_project_id(project_path)
    click.echo(f"Project ID: {project_id}")

    # Get project name
    if not name:
        name = click.prompt("Project name", default=project_path.name)

    # Get user name
    default_user = os.environ.get('USER', os.environ.get('USERNAME', 'developer'))
    user_name = click.prompt("Your name/username", default=default_user)

    # Create initializer and run
    initializer = ProjectInitializer(project_path, manager.global_dir)

    # The initializer already handles all the initialization logic
    success = initializer.run(project_name=name, user_name=user_name, force=force)

    if success:
        # Project info is saved by init.py to .acolyte.project
        click.echo(click.style("✓ Project initialized successfully!", fg="green"))
        click.echo(f"Configuration stored in: {manager.get_project_dir(project_id)}")
    else:
        click.echo(click.style("✗ Initialization failed!", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--path', default=".", help='Project path')
def install(path: str):
    """Install and configure ACOLYTE services for the project"""
    # Lazy import heavy dependencies
    from acolyte.install.installer import ProjectInstaller
    from acolyte.install.common import ACOLYTE_LOGO

    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        click.echo("Run 'acolyte init' first")
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)

    # Show logo
    print(ACOLYTE_LOGO)
    click.echo(click.style("🔧 ACOLYTE Installation", fg="cyan", bold=True))

    # Run installer
    try:
        installer = ProjectInstaller(project_path, manager.global_dir)
        success = asyncio.run(installer.run())

        if success:
            click.echo(click.style("✓ Installation completed successfully!", fg="green"))
            click.echo(f"Configuration saved to: {project_dir}")
        else:
            # User cancelled or installation failed
            # The installer already printed appropriate messages
            sys.exit(0)

    except Exception as e:
        click.echo(click.style(f"✗ Installation error: {e}", fg="red"))
        if os.environ.get('ACOLYTE_DEBUG'):
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--path', default=".", help='Project path')
def start(path: str):
    """Start ACOLYTE services"""
    # Lazy import for Rich and health checker
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from acolyte.core.health import ServiceHealthChecker

    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        click.echo("Run 'acolyte init' first")
        sys.exit(1)

    # Load project info and config
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)
    config_file = project_dir / ".acolyte"

    if not config_file.exists():
        click.echo(click.style("✗ Project not configured!", fg="red"))
        click.echo("Run 'acolyte install' first")
        sys.exit(1)

    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        click.echo(click.style(f"✗ Failed to load configuration: {e}", fg="red"))
        sys.exit(1)

    # Start services
    console = Console()
    console.print("[bold cyan]🚀 Starting ACOLYTE services...[/bold cyan]")

    try:
        docker_cmd = detect_docker_compose_cmd()
        infra_dir = project_dir / "infra"

        if not (infra_dir / "docker-compose.yml").exists():
            console.print("[bold red]✗ Docker configuration not found![/bold red]")
            console.print("Run 'acolyte install' first")
            sys.exit(1)

        # Task 1: Stop existing containers
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task1 = progress.add_task("[yellow]Stopping existing containers...", total=100)
            subprocess.run(
                docker_cmd + ["down", "--remove-orphans"],
                cwd=infra_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
            )
            progress.update(task1, completed=100)

        # Task 2: Start Docker services
        # First check if images need to be downloaded
        console.print("\n[yellow]Checking Docker images...[/yellow]")

        # Check if images exist
        check_images = subprocess.run(
            ["docker", "images", "-q", "weaviate/weaviate:latest"],
            capture_output=True,
            text=True,
        )

        if not check_images.stdout.strip():
            # Images need to be downloaded
            console.print("[yellow]📥 First time setup detected![/yellow]")
            console.print(
                "[yellow]Downloading Docker images (this may take 5-10 minutes)...[/yellow]"
            )
            console.print("[dim]• Weaviate vector database (~500MB)[/dim]")
            console.print("[dim]• Backend runtime environment[/dim]")
            console.print("[dim]• Ollama model server[/dim]")
            console.print("[dim]• Qwen2.5-Coder model (~2GB on first run)[/dim]")
            console.print("\n[cyan]☕ This is a good time for a coffee break![/cyan]")
            console.print("[dim]Tip: You'll see Docker's download progress below...[/dim]\n")

            # Run WITHOUT capture_output to show Docker's download progress
            result = subprocess.run(
                docker_cmd + ["up", "-d", "--force-recreate"],
                cwd=infra_dir,
                text=True,
                encoding='utf-8',
            )

            if result.returncode != 0:
                console.print("[bold red]✗ Failed to start services[/bold red]")
                sys.exit(1)

            # Wait for services without progress bar for first time setup
            console.print("\n[yellow]Waiting for services to be ready...[/yellow]")
            health_checker = ServiceHealthChecker(config)

            # Simple status messages for first time
            console.print("[dim]• Checking Weaviate...[/dim]")
            for i in range(120):
                if health_checker._check_service_once(
                    "Weaviate", config['ports']['weaviate'], "/v1/.well-known/ready"
                ):
                    console.print("[green]✓[/green] Weaviate is ready")
                    break
                time.sleep(1)
            else:
                console.print("[bold red]✗ Weaviate failed to start[/bold red]")
                sys.exit(1)

            # Check if Ollama is ready first
            console.print("[dim]• Checking Ollama...[/dim]")
            ollama_ready = False
            for i in range(120):
                try:
                    ollama_check = subprocess.run(
                        ["docker", "exec", "acolyte-ollama", "ollama", "list"],
                        capture_output=True,
                        text=True,
                    )
                    if ollama_check.returncode == 0:
                        console.print("[green]✓[/green] Ollama is ready")
                        ollama_ready = True
                        break
                except (subprocess.SubprocessError, FileNotFoundError, OSError):
                    pass
                time.sleep(1)
            else:
                console.print("[bold red]✗ Ollama failed to start[/bold red]")
                sys.exit(1)

            # Create the acolyte model if it doesn't exist
            if ollama_ready:
                console.print("[dim]• Checking for acolyte model...[/dim]")
                if not ensure_acolyte_model_exists(config, infra_dir, console):
                    console.print("[bold red]✗ Failed to create acolyte model[/bold red]")
                    console.print(
                        "[yellow]Continuing anyway - backend will use base model[/yellow]"
                    )

            console.print("[dim]• Checking Backend API...[/dim]")
            for i in range(120):
                if health_checker._check_service_once(
                    "Backend", config['ports']['backend'], "/api/health"
                ):
                    console.print("[green]✓[/green] Backend API is ready")
                    break
                time.sleep(1)
            else:
                console.print("[bold red]✗ Backend failed to start[/bold red]")
                sys.exit(1)

        else:
            # Images already exist, use progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task2 = progress.add_task("[cyan]Starting Docker containers...", total=100)
                result = subprocess.run(
                    docker_cmd + ["up", "-d", "--force-recreate"],
                    cwd=infra_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                )
                progress.update(task2, completed=100)

                if result.returncode != 0:
                    console.print("[bold red]✗ Failed to start services[/bold red]")
                    if hasattr(result, 'stderr'):
                        console.print(f"[red]Error: {result.stderr}[/red]")
                    sys.exit(1)

                # Task 3: Wait for services
                health_checker = ServiceHealthChecker(config)

                # Weaviate
                task3 = progress.add_task("[green]Waiting for Weaviate...", total=120)
                for i in range(120):
                    if health_checker._check_service_once(
                        "Weaviate", config['ports']['weaviate'], "/v1/.well-known/ready"
                    ):
                        progress.update(task3, completed=120)
                        break
                    progress.update(task3, advance=1)
                    time.sleep(1)
                else:
                    console.print("[bold red]✗ Weaviate failed to start[/bold red]")
                    # Show last 5 log lines from weaviate
                    try:
                        logs = subprocess.check_output(
                            docker_cmd + ["logs", "--tail", "5", "weaviate"], cwd=infra_dir
                        ).decode(errors="replace")
                        console.print("[yellow]Last 5 log lines from Weaviate:[/yellow]")
                        console.print(logs)
                    except Exception as e:
                        console.print(f"[red]Could not fetch Weaviate logs: {e}[/red]")
                    sys.exit(1)

                # Ollama model check and creation
                task_ollama = progress.add_task("[green]Checking Ollama model...", total=100)

                # Use the centralized function to ensure model exists
                if ensure_acolyte_model_exists(config, infra_dir, console):
                    progress.update(task_ollama, completed=100, description="[green]Model ready")
                else:
                    progress.update(
                        task_ollama, completed=100, description="[yellow]Model creation failed"
                    )
                    console.print(
                        "[yellow]Continuing anyway - backend will use base model[/yellow]"
                    )

                # Backend
                task4 = progress.add_task("[green]Waiting for Backend API...", total=120)
                for i in range(120):
                    if health_checker._check_service_once(
                        "Backend", config['ports']['backend'], "/api/health"
                    ):
                        progress.update(task4, completed=120)
                        break
                    progress.update(task4, advance=1)
                    time.sleep(1)
                else:
                    console.print("[bold red]✗ Backend failed to start[/bold red]")
                    # Show last 5 log lines from backend
                    try:
                        logs = subprocess.check_output(
                            docker_cmd + ["logs", "--tail", "5", "backend"], cwd=infra_dir
                        ).decode(errors="replace")
                        console.print("[yellow]Last 5 log lines from Backend:[/yellow]")
                        console.print(logs)
                    except Exception as e:
                        console.print(f"[red]Could not fetch Backend logs: {e}[/red]")
                    sys.exit(1)

        console.print("[bold green]✓ All services are ready![/bold green]")
        console.print(f"\n[dim]Backend API: http://localhost:{config['ports']['backend']}[/dim]")
        console.print(f"[dim]Weaviate: http://localhost:{config['ports']['weaviate']}[/dim]")
        console.print(f"[dim]Ollama: http://localhost:{config['ports']['ollama']}[/dim]")
        console.print(
            "\n[bold cyan]ACOLYTE is ready! Use 'acolyte status' to check services.[/bold cyan]"
        )

    except Exception as e:
        click.echo(click.style(f"✗ Error starting services: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--path', default=".", help='Project path')
def stop(path: str):
    """Stop ACOLYTE services"""
    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)
    infra_dir = project_dir / "infra"

    if not (infra_dir / "docker-compose.yml").exists():
        click.echo(click.style("✗ Docker configuration not found!", fg="red"))
        sys.exit(1)

    # Stop services
    click.echo(click.style("🛑 Stopping ACOLYTE services...", fg="cyan"))

    try:
        docker_cmd = detect_docker_compose_cmd()
        result = subprocess.run(
            docker_cmd + ["down"],
            cwd=infra_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            click.echo(click.style(f"✗ Failed to stop services: {result.stderr}", fg="red"))
            sys.exit(1)

        click.echo(click.style("✓ Services stopped successfully!", fg="green"))

    except Exception as e:
        click.echo(click.style(f"✗ Error stopping services: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--path', default=".", help='Project path')
def status(path: str):
    """Check ACOLYTE status for the project"""
    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        click.echo("Run 'acolyte init' first")
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)
    config_file = project_dir / ".acolyte"

    click.echo(click.style("📊 ACOLYTE Status", fg="cyan", bold=True))
    click.echo(f"Project: {project_info.get('name', 'Unknown')}")
    click.echo(f"Project ID: {project_id}")
    click.echo(f"Path: {project_path.resolve()}")

    # Check configuration
    if config_file.exists():
        click.echo(click.style("✓ Configuration: Found", fg="green"))
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            ports = config.get('ports', {})
            click.echo(f"  Backend: localhost:{ports.get('backend', 'N/A')}")
            click.echo(f"  Weaviate: localhost:{ports.get('weaviate', 'N/A')}")
            click.echo(f"  Ollama: localhost:{ports.get('ollama', 'N/A')}")
        except Exception:
            click.echo(click.style("⚠ Configuration: Invalid", fg="yellow"))
    else:
        click.echo(click.style("✗ Configuration: Not found", fg="red"))
        click.echo("  Run 'acolyte install' to configure")

    # Check Docker services
    infra_dir = project_dir / "infra"
    if (infra_dir / "docker-compose.yml").exists():
        click.echo(click.style("✓ Docker: Configured", fg="green"))

        try:
            docker_cmd = detect_docker_compose_cmd()
            result = subprocess.run(
                docker_cmd + ["ps"],
                cwd=infra_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Has services
                    click.echo("  Services:")
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            click.echo(f"    {line.strip()}")
                else:
                    click.echo("  No services running")
            else:
                click.echo(click.style("⚠ Docker: Error checking status", fg="yellow"))

        except Exception:
            click.echo(click.style("⚠ Docker: Error checking status", fg="yellow"))
    else:
        click.echo(click.style("✗ Docker: Not configured", fg="red"))


@cli.command()
@click.option('--path', default=".", help='Project path')
@click.option('--full', is_flag=True, help='Full project indexing')
@click.option('--progress/--no-progress', default=True, help='Show live progress')
@click.option('--verbose', is_flag=True, help='Show detailed progress')
@click.option('--resume', help='Resume previous indexing task by ID')
def index(path: str, full: bool, progress: bool, verbose: bool, resume: Optional[str]):
    """Index project files"""
    # Lazy import
    from acolyte.core.health import ServiceHealthChecker

    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        click.echo("Run 'acolyte init' first")
        sys.exit(1)

    # Load project info and config
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)
    config_file = project_dir / ".acolyte"

    if not config_file.exists():
        click.echo(click.style("✗ Project not configured!", fg="red"))
        click.echo("Run 'acolyte install' first")
        sys.exit(1)

    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        click.echo(click.style(f"✗ Failed to load configuration: {e}", fg="red"))
        sys.exit(1)

    # Check if backend is ready before indexing
    health_checker = ServiceHealthChecker(config)
    if not health_checker.wait_for_backend():
        click.echo(click.style("✗ Backend is not ready. Run 'acolyte start' first.", fg="red"))
        sys.exit(1)

    # Start indexing
    click.echo(click.style("📚 Starting project indexing...", fg="cyan"))

    try:
        backend_port = config['ports']['backend']
        url = f"http://localhost:{backend_port}/api/index/project"

        # Prepare request data
        request_data = {
            "patterns": [
                "*.py",
                "*.js",
                "*.ts",
                "*.tsx",
                "*.jsx",
                "*.java",
                "*.go",
                "*.rs",
                "*.cpp",
                "*.c",
                "*.h",
                "*.hpp",
                "*.cs",
                "*.rb",
                "*.php",
                "*.swift",
                "*.kt",
                "*.scala",
                "*.r",
                "*.m",
                "*.mm",
                "*.sql",
                "*.sh",
                "*.yaml",
                "*.yml",
                "*.json",
                "*.xml",
                "*.toml",
                "*.ini",
                "*.cfg",
                "*.conf",
                "*.md",
                "*.rst",
                "*.txt",
            ],
            "exclude_patterns": [
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/.git/**",
                "**/venv/**",
                "**/.venv/**",
                "**/build/**",
                "**/target/**",
            ],
            "respect_gitignore": True,
            "respect_acolyteignore": True,
            "force_reindex": full,
            "resume_task_id": resume,  # Add resume task ID if provided
        }

        response = requests.post(url, json=request_data, timeout=300)  # 5 minutes timeout

        if response.status_code == 200:
            result = response.json()
            click.echo(click.style("✓ Indexing started successfully!", fg="green"))
            click.echo(f"Task ID: {result.get('task_id', 'N/A')}")
            click.echo(f"Estimated files: {result.get('estimated_files', 'N/A')}")

            # Show initial file collection info if available
            if result.get('patterns'):
                click.echo(f"Patterns: {len(result['patterns'])} file types")

            # Warn if very few files
            if result.get('estimated_files', 1000) < 10:
                click.echo(
                    click.style(
                        "\n⚠ Only a few files found to index. Check your project structure.",
                        fg="yellow",
                    )
                )

            # Connect to WebSocket for live progress if requested
            if progress and result.get('websocket_url'):
                click.echo("\nConnecting to progress monitor...")
                # Run async progress monitoring
                asyncio.run(
                    monitor_indexing_progress(
                        backend_port=backend_port,
                        websocket_path=result['websocket_url'],
                        task_id=result.get('task_id'),
                        total_files=result.get('estimated_files', 0),
                        verbose=verbose,
                    )
                )
            else:
                click.echo(f"\nWebSocket URL: {result.get('websocket_url', 'N/A')}")
                click.echo("Use WebSocket to monitor progress or check logs with 'acolyte logs'.")
        else:
            error_text = response.text
            try:
                error_json = response.json()
                if 'detail' in error_json:
                    error_text = error_json['detail']
            except ValueError:
                pass
            click.echo(click.style(f"✗ Indexing failed: {error_text}", fg="red"))
            sys.exit(1)

    except requests.RequestException as e:
        click.echo(click.style(f"✗ Failed to connect to backend: {e}", fg="red"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Indexing error: {e}", fg="red"))
        sys.exit(1)


@cli.command()
def projects():
    """List all ACOLYTE projects"""
    manager = ProjectManager()

    click.echo(click.style("📁 ACOLYTE Projects", fg="cyan", bold=True))

    if not manager.projects_dir.exists():
        click.echo("No projects found")
        return

    projects_found = False
    for project_dir in manager.projects_dir.iterdir():
        if project_dir.is_dir():
            projects_found = True
            project_id = project_dir.name

            # Try to load project info
            config_file = project_dir / ".acolyte"
            project_name = "Unknown"
            project_path = "Unknown"

            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    project_name = config.get('project', {}).get('name', 'Unknown')
                    # Don't use the relative path from config
                    # project_path = config.get('project', {}).get('path', 'Unknown')
                except Exception:
                    pass

            # Try to find the real project path by searching for .acolyte.project files
            # that contain this project_id
            real_project_path = None

            # First check common locations
            home = Path.home()
            common_dirs = [
                home / "Desktop",
                home / "Documents",
                home / "Projects",
                home / "repos",
                home / "dev",
                home / "workspace",
                home / "code",
                home,
            ]

            for base_dir in common_dirs:
                if base_dir.exists():
                    try:
                        # Search for .acolyte.project files
                        for acolyte_project_file in base_dir.rglob(".acolyte.project"):
                            try:
                                with open(acolyte_project_file) as f:
                                    project_data = yaml.safe_load(f)
                                    if project_data.get('project_id') == project_id:
                                        # Found it!
                                        real_project_path = project_data.get('project_path')
                                        if not real_project_path:
                                            # Fallback to parent directory of .acolyte.project
                                            real_project_path = str(acolyte_project_file.parent)
                                        break
                            except Exception:
                                continue

                        if real_project_path:
                            break
                    except Exception:
                        continue

            if real_project_path:
                project_path = real_project_path
            elif config_file.exists():
                # Fallback to showing relative path from config
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    project_path = config.get('project', {}).get('path', 'Unknown')
                except Exception:
                    pass

            click.echo(f"\nProject ID: {project_id}")
            click.echo(f"Name: {project_name}")
            click.echo(f"Path: {project_path}")

            # Check if services are running
            try:
                docker_cmd = detect_docker_compose_cmd()
                result = subprocess.run(
                    docker_cmd + ["ps", "--quiet"],
                    cwd=project_dir / "infra",
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    click.echo(click.style("Status: Running", fg="green"))
                else:
                    click.echo(click.style("Status: Stopped", fg="yellow"))
            except Exception:
                click.echo(click.style("Status: Unknown", fg="yellow"))

    if not projects_found:
        click.echo("No projects found")


@cli.command()
@click.option('--path', default=".", help='Project path')
def clean(path: str):
    """Clean ACOLYTE cache and temporary files"""
    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)

    click.echo(click.style("🧹 Cleaning ACOLYTE cache...", fg="cyan"))

    # Clean cache directories
    cache_dirs = [
        project_dir / "data" / "embeddings_cache",
        project_dir / "data" / "logs",
    ]

    cleaned = 0
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                click.echo(f"✓ Cleaned: {cache_dir.name}")
                cleaned += 1
            except Exception as e:
                click.echo(click.style(f"⚠ Failed to clean {cache_dir.name}: {e}", fg="yellow"))

    if cleaned > 0:
        click.echo(click.style(f"✓ Cleaned {cleaned} cache directories", fg="green"))
    else:
        click.echo("No cache directories found to clean")


@cli.command()
@click.option('--path', default=".", help='Project path')
@click.option('-f', '--follow', is_flag=True, help='Follow log output (like tail -f)')
@click.option('-n', '--lines', default=100, help='Number of lines to show (default: 100)')
@click.option(
    '-s',
    '--service',
    type=click.Choice(['backend', 'weaviate', 'ollama', 'all']),
    default='all',
    help='Service to show logs for',
)
@click.option('--file', is_flag=True, help='Show project log file instead of Docker logs')
@click.option('-g', '--grep', help='Filter logs containing text')
@click.option(
    '--level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help='Filter by log level (only for --file)',
)
def logs(
    path: str,
    follow: bool,
    lines: int,
    service: str,
    file: bool,
    grep: Optional[str],
    level: Optional[str],
):
    """View ACOLYTE service logs"""
    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)

    if file:
        # Show log file
        log_file = project_dir / "data" / "logs" / f"{project_id}.log"
        if not log_file.exists():
            click.echo(click.style("✗ Log file not found!", fg="red"))
            sys.exit(1)

        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()

            # Apply filters
            if level:
                log_lines = [line for line in log_lines if level in line]
            if grep:
                log_lines = [line for line in log_lines if grep in line]

            # Show last N lines
            log_lines = log_lines[-lines:]

            for line in log_lines:
                click.echo(line.rstrip())

        except Exception as e:
            click.echo(click.style(f"✗ Error reading log file: {e}", fg="red"))
            sys.exit(1)
    else:
        # Show Docker logs
        infra_dir = project_dir / "infra"
        if not (infra_dir / "docker-compose.yml").exists():
            click.echo(click.style("✗ Docker configuration not found!", fg="red"))
            sys.exit(1)

        try:
            docker_cmd = detect_docker_compose_cmd()

            if service == 'all':
                cmd = docker_cmd + ["logs", "--tail", str(lines)]
                if follow:
                    cmd.append("-f")
            else:
                cmd = docker_cmd + ["logs", "--tail", str(lines), service]
                if follow:
                    cmd.append("-f")

            # Run docker logs
            process = subprocess.Popen(
                cmd,
                cwd=infra_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Stream output
            if process.stdout:
                for line in process.stdout:
                    if grep is None or grep in line:
                        click.echo(line.rstrip())

            process.wait()

        except Exception as e:
            click.echo(click.style(f"✗ Error showing logs: {e}", fg="red"))
            sys.exit(1)


@cli.command()
@click.option('--path', default=".", help='Project path')
@click.option('--force', is_flag=True, help='Force reset without confirmation')
def reset(path: str, force: bool):
    """Reset ACOLYTE installation for this project"""
    project_path = Path(path)
    manager = ProjectManager()

    # Check if project is initialized
    if not manager.is_project_initialized(project_path):
        click.echo(click.style("✗ Project not initialized!", fg="red"))
        sys.exit(1)

    # Load project info
    project_info = manager.load_project_info(project_path)
    if not project_info:
        click.echo(click.style("✗ Failed to load project info!", fg="red"))
        sys.exit(1)

    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)

    click.echo(click.style("🔄 ACOLYTE Project Reset", fg="cyan", bold=True))
    click.echo(f"Project: {project_info.get('name', 'Unknown')}")
    click.echo(f"Project ID: {project_id}")
    click.echo(f"Reset directory: {project_dir}")

    if not force:
        if not click.confirm("This will delete all ACOLYTE data for this project. Continue?"):
            click.echo("Reset cancelled.")
            return

    try:
        # Stop services if running
        infra_dir = project_dir / "infra"
        if (infra_dir / "docker-compose.yml").exists():
            click.echo("Stopping services...")
            try:
                docker_cmd = detect_docker_compose_cmd()
                # Force stop with timeout
                result = subprocess.run(
                    docker_cmd + ["down", "--timeout", "30"],
                    cwd=infra_dir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    click.echo("✓ Services stopped")
                else:
                    click.echo("⚠️  Some services may still be running")

                # Wait a bit for file handles to be released
                import time

                time.sleep(3)

            except subprocess.TimeoutExpired:
                click.echo("⚠️  Services stop timed out, trying to force stop...")
                try:
                    if docker_cmd:  # Check if docker_cmd is not None
                        subprocess.run(
                            docker_cmd + ["down", "--volumes", "--remove-orphans"],
                            cwd=infra_dir,
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        time.sleep(2)
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass  # Ignore errors if services not running

        # Try to remove project directory with retry logic
        if project_dir.exists():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.rmtree(project_dir)
                    click.echo("✓ Project data removed")
                    break
                except PermissionError:
                    if attempt < max_retries - 1:
                        click.echo(
                            f"⚠️  Retry {attempt + 1}/{max_retries}: Waiting for files to be released..."
                        )
                        time.sleep(2)
                    else:
                        click.echo("⚠️  Some files could not be removed (may be in use)")
                        click.echo("   You may need to restart your terminal or computer")
                        # Try to remove individual files that might be locked
                        try:
                            for root, dirs, files in os.walk(project_dir, topdown=False):
                                for file in files:
                                    try:
                                        os.remove(os.path.join(root, file))
                                    except (PermissionError, FileNotFoundError, OSError):
                                        pass
                                for dir in dirs:
                                    try:
                                        os.rmdir(os.path.join(root, dir))
                                    except (PermissionError, FileNotFoundError, OSError):
                                        pass
                            click.echo("✓ Partial cleanup completed")
                        except (PermissionError, FileNotFoundError, OSError):
                            pass
                except Exception as e:
                    click.echo(f"✗ Error removing project directory: {e}")
                    break

        # Remove project marker and any init logs
        project_file = project_path / ".acolyte.project"
        if project_file.exists():
            project_file.unlink()
            click.echo("✓ Project marker removed")

        # Remove any init log files that might have been created in the past
        init_log_file = project_path / ".acolyte.init.log"
        if init_log_file.exists():
            try:
                init_log_file.unlink()
                click.echo("✓ Old init log file removed")
            except (PermissionError, FileNotFoundError, OSError):
                pass  # Ignore if can't remove

        click.echo(click.style("✅ Project reset completed!", fg="green"))
        click.echo("Run 'acolyte init' to reinitialize the project")

    except Exception as e:
        click.echo(click.style(f"✗ Reset failed: {e}", fg="red"))
        sys.exit(1)


@cli.command()
def doctor():
    """Diagnose and fix common ACOLYTE issues"""
    import shutil

    click.echo(click.style("🔍 ACOLYTE Doctor - System Diagnosis", fg="cyan", bold=True))

    issues = []
    fixes = []

    # Check if acolyte command is in PATH
    acolyte_path = shutil.which('acolyte')
    if acolyte_path is None:
        issues.append("acolyte command not found in PATH")
        fixes.append("Add Scripts/ or bin/ directory to your PATH")
    else:
        click.echo(f"✓ ACOLYTE command: Found at {acolyte_path}")

    # Check Docker
    docker_path = shutil.which('docker')
    if docker_path is None:
        issues.append("Docker not installed")
        fixes.append("Install Docker Desktop from https://docker.com")
    else:
        click.echo("✓ Docker: Available")

    # Check Docker Compose
    try:
        detect_docker_compose_cmd()
        click.echo("✓ Docker Compose: Available")
    except Exception:
        issues.append("Docker Compose not found")
        fixes.append("Install Docker Compose or update Docker Desktop")

    # Check Git
    git_path = shutil.which('git')
    if git_path is None:
        issues.append("Git not installed")
        fixes.append("Install Git from https://git-scm.com")
    else:
        click.echo("✓ Git: Available")

    # Check ACOLYTE home directory
    acolyte_home = Path.home() / ".acolyte"
    if not acolyte_home.exists():
        issues.append("~/.acolyte directory not found")
        fixes.append("Reinstall ACOLYTE or run 'acolyte init'")
    else:
        click.echo("✓ ACOLYTE home: Found")

    # Check Python version
    if sys.version_info < (3, 11):
        issues.append(
            f"Python {sys.version_info.major}.{sys.version_info.minor} found, 3.11+ required"
        )
        fixes.append("Upgrade to Python 3.11 or newer")
    else:
        click.echo("✓ Python version: Compatible")

    # Check if we can import ACOLYTE modules - without importing heavy ones
    try:
        # Only check lightweight imports
        import acolyte  # noqa: F401

        click.echo("✓ ACOLYTE modules: Importable")
    except ImportError as e:
        issues.append(f"ACOLYTE modules not importable: {e}")
        fixes.append("Reinstall ACOLYTE with 'pip install --force-reinstall acolytes'")

    # Report issues
    if issues:
        click.echo("\n" + click.style("⚠️  Issues found:", fg="yellow"))
        for i, issue in enumerate(issues, 1):
            click.echo(f"  {i}. {issue}")
            click.echo(f"     Fix: {fixes[i-1]}")

        click.echo("\n" + click.style("💡 Tips:", fg="cyan"))
        click.echo("• Restart your terminal after adding to PATH")
        click.echo("• Run 'acolyte doctor' again after fixing issues")
        click.echo("• Check logs with 'acolyte logs' for more details")
    else:
        click.echo("\n" + click.style("✅ All checks passed! ACOLYTE is ready to use.", fg="green"))


async def monitor_indexing_progress(
    backend_port: int, websocket_path: str, task_id: str, total_files: int, verbose: bool = False
):
    """Monitor indexing progress via WebSocket with Rich progress bar."""
    # Lazy imports
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.console import Console
    from rich.table import Table
    import websockets
    import json

    console = Console()

    # WebSocket URL - using urllib.parse for safe URL construction
    from urllib.parse import urlunparse

    ws_url = urlunparse(('ws', f"localhost:{backend_port}", websocket_path, '', '', ''))

    try:
        # First try WebSocket
        async with websockets.connect(ws_url, timeout=5) as websocket:
            console.print("[green]✓[/green] Connected to progress monitor")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("{task.fields[current_file]}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:

                main_task = progress.add_task(
                    "[cyan]Indexing files...", total=total_files or 100, current_file="Starting..."
                )

                # Statistics tracking
                stats = {
                    "chunks_created": 0,
                    "embeddings_generated": 0,
                    "files_skipped": 0,
                    "errors": 0,
                }

                async for message in websocket:
                    try:
                        data = json.loads(message)

                        # Handle different message types
                        if data.get('type') == 'progress':
                            # Update progress bar
                            current = data.get('current', 0)
                            total = data.get('total', total_files)
                            current_file = data.get('current_file', data.get('message', ''))

                            # Update statistics if available
                            if 'chunks_created' in data:
                                stats['chunks_created'] = data['chunks_created']
                            if 'embeddings_generated' in data:
                                stats['embeddings_generated'] = data['embeddings_generated']
                            if 'files_skipped' in data:
                                stats['files_skipped'] = data['files_skipped']
                            if 'errors' in data:
                                stats['errors'] = data['errors']

                            progress.update(
                                main_task, completed=current, total=total, current_file=current_file
                            )

                            # Show detailed stats if verbose
                            if verbose and current % 10 == 0:  # Every 10 files
                                console.print(
                                    f"[dim]Chunks: {stats['chunks_created']} | "
                                    f"Embeddings: {stats['embeddings_generated']} | "
                                    f"Skipped: {stats['files_skipped']} | "
                                    f"Errors: {stats['errors']}[/dim]"
                                )

                            # Check if complete
                            if current >= total:
                                progress.update(main_task, completed=total)
                                break

                        elif data.get('type') == 'error':
                            console.print(
                                f"[red]Error: {data.get('message', 'Unknown error')}[/red]"
                            )

                        elif data.get('type') == 'complete':
                            progress.update(main_task, completed=total_files)
                            break

                    except json.JSONDecodeError:
                        # Handle non-JSON messages (like ping/pong)
                        pass
                    except Exception as e:
                        if verbose:
                            console.print(f"[yellow]Warning: {e}[/yellow]")

            # Final statistics
            console.print("\n[bold green]✓ Indexing completed![/bold green]")

            # Show final stats table
            if stats['chunks_created'] > 0 or verbose:
                table = Table(title="Indexing Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Files Processed", str(total_files - stats['files_skipped']))
                table.add_row("Files Skipped", str(stats['files_skipped']))
                table.add_row("Chunks Created", str(stats['chunks_created']))
                table.add_row("Embeddings Generated", str(stats['embeddings_generated']))

                if stats['errors'] > 0:
                    table.add_row("Errors", f"[red]{stats['errors']}[/red]")

                console.print(table)

                if stats['errors'] > 0:
                    console.print(
                        "\n[yellow]⚠ Some files had errors. Check logs for details.[/yellow]"
                    )

    except (websockets.ConnectionClosedError, asyncio.TimeoutError):
        # WebSocket failed, fallback to polling
        console.print("[yellow]⚠[/yellow] WebSocket connection failed, using HTTP polling")
        await monitor_via_polling(backend_port, task_id, total_files, console)

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Progress monitoring cancelled. Indexing continues in background.[/yellow]"
        )

    except Exception as e:
        console.print(f"[red]Error monitoring progress: {e}[/red]")
        if os.environ.get('ACOLYTE_DEBUG'):
            import traceback

            traceback.print_exc()


async def monitor_via_polling(backend_port: int, task_id: str, total_files: int, console):
    """Fallback monitoring via HTTP polling."""
    # Simple polling implementation
    console.print("[dim]Polling for progress updates...[/dim]")

    # TODO: Implement HTTP polling endpoint and logic
    # For now, just inform user
    console.print(f"\nTask ID: {task_id}")
    console.print("Check progress with 'acolyte logs' or wait for completion.")


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        if os.environ.get('ACOLYTE_DEBUG'):
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
