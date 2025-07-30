"""
Main CLI application for fp-admin.

This module provides the main CLI interface with commands organized by functionality.
"""

from importlib.metadata import version as metadata_version

import typer

from .commands import database_app, project_app, system_app, user_app
from .commands.database import make_migrations as db_make_migrations
from .commands.database import migrate as db_migrate
from .commands.project import startapp as project_startapp
from .commands.project import startproject as project_startproject
from .commands.system import run as system_run
from .commands.system import version as system_version
from .commands.user import createsuperuser as user_createsuperuser

# Create the main CLI app
admin_cli = typer.Typer(
    name="fp-admin",
    help="FastAPI Admin Framework CLI - A powerful admin "
    "interface for FastAPI applications",
    add_completion=False,
    rich_markup_mode="markdown",
)

# Add subcommand groups
admin_cli.add_typer(system_app, help="System information and utilities")
admin_cli.add_typer(project_app, help="Project and app management")
admin_cli.add_typer(database_app, help="Database migration and management")
admin_cli.add_typer(user_app, help="User and authentication management")


@admin_cli.command()
def info() -> None:
    """Show fp-admin information and common usage patterns.

    Examples:
        fp-admin info
    """

    typer.echo("🚀 **fp-admin** - FastAPI Admin Framework")
    typer.echo(f"Version: {metadata_version('fp-admin')}")
    typer.echo()
    typer.echo("**Common Commands:**")
    typer.echo("  fp-admin startproject myproject    # Create new project")
    typer.echo("  fp-admin startapp blog             # Create new app")
    typer.echo("  fp-admin make-migrations initial   # Create migration")
    typer.echo("  fp-admin migrate                   # Apply migrations")
    typer.echo("  fp-admin createsuperuser           # Create admin user")
    typer.echo("  fp-admin run                       # Run the server")
    typer.echo()
    typer.echo("**Command Groups:**")
    typer.echo("  fp-admin system --help             # System commands")
    typer.echo("  fp-admin project --help            # Project commands")
    typer.echo("  fp-admin database --help           # Database commands")
    typer.echo("  fp-admin user --help               # User commands")
    typer.echo()
    typer.echo("**Quick Start:**")
    typer.echo("  1. fp-admin startproject myapp")
    typer.echo("  2. cd myapp")
    typer.echo("  3. fp-admin startapp blog")
    typer.echo("  4. fp-admin make-migrations initial")
    typer.echo("  5. fp-admin migrate")
    typer.echo("  6. fp-admin createsuperuser")
    typer.echo("  7. fp-admin run")


# For backward compatibility, add direct commands
@admin_cli.command()
def version() -> None:
    """Show fp-admin version (alias for system version)."""

    system_version()


@admin_cli.command()
def startproject(name: str) -> None:
    """Create a new project (alias for project startproject)."""

    project_startproject(name)


@admin_cli.command()
def startapp(name: str) -> None:
    """Create a new app (alias for project startapp)."""

    project_startapp(name)


@admin_cli.command()
def make_migrations(name: str) -> None:
    """Generate a new Alembic migration (alias for database make-migrations)."""

    db_make_migrations(name)


@admin_cli.command()
def migrate() -> None:
    """Apply latest Alembic migrations (alias for database migrate)."""

    db_migrate()


@admin_cli.command()
def createsuperuser() -> None:
    """Create a superuser account (alias for user createsuperuser)."""

    user_createsuperuser()


@admin_cli.command()
def run(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    log_level: str = typer.Option("info", "--log-level", "-l", help="Log level"),
    app: str = typer.Option(
        "app:app",
        "--app",
        "-a",
        help="ASGI application to run (e.g., app:app, main:app)",
    ),
) -> None:
    """Run the FastAPI application using uvicorn (alias for system run).

    Examples:
        fp-admin run
        fp-admin run --host 0.0.0.0 --port 8080
        fp-admin run --no-reload --log-level info
        fp-admin run --app main:app
    """
    system_run(host=host, port=port, reload=reload, log_level=log_level, app=app)
