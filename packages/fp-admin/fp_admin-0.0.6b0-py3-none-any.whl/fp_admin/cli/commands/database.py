"""
Database management commands for fp-admin CLI.
"""

import subprocess
from pathlib import Path

import typer

database_app = typer.Typer(name="database", help="Database management commands")

ALEMBIC = "alembic.ini"


def run(cmd: list[str]) -> None:
    """Run a command and display output."""
    typer.echo(f"🔧 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


@database_app.command()
def make_migrations(
    name: str = typer.Option(..., "--name", "-n", help="Migration name")
) -> None:
    """Generate a new Alembic migration.

    Examples:
        fp-admin database make-migrations --name initial
        fp-admin database make-migrations -n add_user_model
        fp-admin make-migrations --name update_schema

    This will:
        1. Create migrations/ directory if it doesn't exist
        2. Generate a new migration file with the given name
        3. Auto-detect model changes
    """
    if not Path("migrations").exists():
        template_path = (
            Path(__file__).parent.parent.parent / "core" / "alembic_template"
        ).as_posix()
        run(["alembic", "init", "migrations", "-t", template_path])
    run(["alembic", "-c", str(ALEMBIC), "revision", "--autogenerate", "-m", name])
    typer.echo(f"✅ Migration '{name}' created successfully")
    typer.echo("📁 Next step: fp-admin migrate")


@database_app.command()
def migrate() -> None:
    """Apply latest Alembic migrations.

    Examples:
        fp-admin database migrate
        fp-admin migrate

    This will:
        1. Apply all pending migrations
        2. Update database schema to latest version
        3. Show migration progress
    """
    run(["alembic", "-c", str(ALEMBIC), "upgrade", "head"])
    typer.echo("✅ Database migrations applied successfully")
    typer.echo("📁 Next step: fp-admin createsuperuser")
