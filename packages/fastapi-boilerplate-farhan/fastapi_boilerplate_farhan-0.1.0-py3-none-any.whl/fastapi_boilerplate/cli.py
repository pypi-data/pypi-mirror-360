import os
import shutil
import click

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

@click.command()
@click.argument("project_name")
@click.option("--db", type=click.Choice(["base", "mysql", "postgresql"]), default="base")
def main(project_name, db):
    """Scaffold a FastAPI project with optional DB support."""
    src = os.path.join(TEMPLATE_PATH, db)
    dst = os.path.join(os.getcwd(), project_name)

    if os.path.exists(dst):
        click.echo("❌ Folder already exists.")
        return

    shutil.copytree(src, dst)
    click.echo(f"✅ Created FastAPI project '{project_name}' with {db} setup.")
