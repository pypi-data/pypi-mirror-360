"""
System information commands for fp-admin CLI.
"""

from importlib.metadata import version as metadata_version
from pathlib import Path

import typer
import uvicorn

system_app = typer.Typer(name="system", help="System information commands")


@system_app.command()
def version() -> None:
    """Show fp-admin version.

    Examples:
        fp-admin system version
        fp-admin version
    """
    typer.echo(metadata_version("fp-admin"))


@system_app.command()
def run(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(True, "--reload", "-r", help="Enable auto-reload"),
    log_level: str = typer.Option("debug", "--log-level", "-l", help="Log level"),
    app: str = typer.Option(
        "app:app",
        "--app",
        "-a",
        help="ASGI application to run (e.g., app:app, main:app)",
    ),
) -> None:
    """Run the FastAPI application using uvicorn.

    Examples:
        fp-admin system run
        fp-admin system run --host 0.0.0.0 --port 8080
        fp-admin system run --no-reload --log-level info
        fp-admin system run --app main:app
    """
    # Check if we're in a project directory
    current_dir = Path.cwd()
    app_files = ["app.py", "main.py"]
    found_app_file = None

    for app_file in app_files:
        if (current_dir / app_file).exists():
            found_app_file = app_file
            break

    if not found_app_file:
        typer.echo("❌ Error: No app.py or main.py found in current directory")
        typer.echo(
            "💡 Make sure you're in your project directory and have an app.py "
            "or main.py file"
        )
        raise typer.Exit(1)

    # Auto-detect app if not specified
    if app == "app:app":
        if found_app_file == "main.py":
            app = "main:app"
        else:
            app = "app:app"

    typer.echo(f"🚀 Starting fp-admin server on {host}:{port}")
    typer.echo(f"📝 Log level: {log_level}")
    typer.echo(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    typer.echo(f"📁 App file: {found_app_file}")
    typer.echo(f"🔧 ASGI app: {app}")
    typer.echo(f"📂 Working directory: {current_dir}")
    typer.echo("Press Ctrl+C to stop the server")
    typer.echo()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        app_dir=current_dir.as_posix(),
    )
