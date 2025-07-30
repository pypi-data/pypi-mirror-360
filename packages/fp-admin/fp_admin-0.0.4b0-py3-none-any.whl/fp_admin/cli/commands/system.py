"""
System information commands for fp-admin CLI.
"""

from importlib.metadata import version as metadata_version

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
) -> None:
    """Run the FastAPI application using uvicorn.

    Examples:
        fp-admin system run
        fp-admin system run --host 0.0.0.0 --port 8080
        fp-admin system run --no-reload --log-level info
    """
    typer.echo(f"🚀 Starting fp-admin server on {host}:{port}")
    typer.echo(f"📝 Log level: {log_level}")
    typer.echo(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    typer.echo("Press Ctrl+C to stop the server")
    typer.echo()

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )
