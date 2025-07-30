"""
User management commands for fp-admin CLI.
"""

from getpass import getpass

import typer
from sqlmodel import select

from fp_admin.core.database import db_manager

user_app = typer.Typer(name="user", help="User management commands")


@user_app.command()
def createsuperuser() -> None:
    """Create a superuser account.

    Examples:
        fp-admin user createsuperuser
        fp-admin createsuperuser

    This will:
        1. Prompt for username, email, and password
        2. Validate password confirmation
        3. Check for existing users
        4. Create superuser with full admin privileges

    Note:
        Password input is hidden for security
    """
    from fp_admin.apps.auth.models import User  # Local import to ensure model is loaded

    username = typer.prompt("Username")
    email = typer.prompt("Email")
    password = getpass("Password: ")
    confirm = getpass("Confirm Password: ")
    # password = bcrypt.hash(password)

    if password != confirm:
        typer.echo("❌ Passwords do not match.")
        raise typer.Exit(code=1)

    with db_manager.get_session() as session:
        stmt = select(User).where(User.username == username)
        exists = session.exec(stmt).first()
        if exists:
            typer.echo("❌ A user with that username already exists.")
            raise typer.Exit(code=1)

        user = User(
            username=username,
            email=email,
            password=password,  # You should hash this in production
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        session.commit()
        typer.echo("✅ Superuser created successfully.")
