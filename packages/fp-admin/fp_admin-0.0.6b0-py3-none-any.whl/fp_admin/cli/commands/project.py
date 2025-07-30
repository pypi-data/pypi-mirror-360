"""
Project management commands for fp-admin CLI.
"""

from pathlib import Path

import typer

project_app = typer.Typer(name="project", help="Project management commands")


@project_app.command()
def startproject(name: str) -> None:
    """Create a new project with models.py, views.py, admin.py,
    routers.py and apps.py.

    Examples:
        fp-admin project startproject myproject
        fp-admin startproject myproject

    This will create:
        myproject/
        ├── app.py
        ├── settings.py
        └── apps/
    """
    project_dir = Path(name)
    if project_dir.exists():
        typer.echo("❌ Project already exists.")
        raise typer.Exit(code=1)

    def render_template(template_name: str) -> None:
        (project_dir / f"{template_name}.py").write_text(
            (
                Path(__file__).parent.parent
                / "templates"
                / "startproject"
                / f"{template_name}.tpl"
            )
            .read_text()
            .format(app_name=name, App=name.title())
        )

    project_dir.mkdir(parents=True)
    Path(project_dir / "apps").mkdir()
    for template in ["app", "settings", "requirements"]:
        render_template(template)

    typer.echo(f"✅ Project '{name}' created")
    typer.echo("📁 Next steps:")
    typer.echo(f"   cd {name}")
    typer.echo("   pip install -r requirements.txt")
    typer.echo("   fp-admin startapp <app_name>")
    typer.echo("   fp-admin make-migrations initial")
    typer.echo("   fp-admin migrate")
    typer.echo("   fp-admin run")


@project_app.command()
def startapp(name: str) -> None:
    """Create a new app with models.py, views.py, admin.py, routers.py and apps.py.

    Examples:
        fp-admin project startapp blog
        fp-admin startapp blog

    This will create:
        apps/blog/
        ├── __init__.py
        ├── admin.py
        ├── models.py
        ├── views.py
        ├── routers.py
        └── apps.py
    """
    app_dir = Path("apps") / name
    if app_dir.exists():
        typer.echo("❌ App already exists.")
        raise typer.Exit(code=1)
    if not Path("apps").exists():
        typer.echo("❌ Apps directory does not exist.")
        typer.echo(
            "💡 Run 'fp-admin startproject <name>' first to create a project structure."
        )
        raise typer.Exit(code=1)

    def render_template(template_name: str) -> None:
        (app_dir / f"{template_name}.py").write_text(
            (
                Path(__file__).parent.parent
                / "templates"
                / "startapp"
                / f"{template_name}.tpl"
            )
            .read_text()
            .format(app_name=name, App=name.title())
        )

    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").touch()
    for template in ["admin", "models", "views", "routers", "apps"]:
        render_template(template)

    typer.echo(f"✅ App '{name}' created at apps/{name}/")
    typer.echo("📁 Next steps:")
    typer.echo(f"   Edit apps/{name}/models.py to define your models")
    typer.echo(f"   Edit apps/{name}/admin.py to configure admin interface")
    typer.echo("   fp-admin make-migrations add_{name}_models")
    typer.echo("   fp-admin migrate")
