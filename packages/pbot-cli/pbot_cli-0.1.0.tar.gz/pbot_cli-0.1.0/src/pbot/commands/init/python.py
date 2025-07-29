# src/pbot/commands/init/python.py
import typer
from pbot.commands.init.github_init import create_repo, upload_file
from pbot.logging.logger import setup_logger
from pbot.metrics.prometheus import count_command
from sentry_sdk import capture_exception

logger = setup_logger()

def python_project_init():
    typer.secho("🐍 Python Project Initializer (GitHub)", fg=typer.colors.BLUE)
    count_command("init_python")  # Prometheus

    try:
        project_name = typer.prompt("Enter project name (e.g., my_awesome_tool)")
        description = typer.prompt("Project description")
        private = typer.confirm("Private repo?", default=True)

        repo_info = create_repo(project_name, description, private)
        owner = repo_info["owner"]["login"]
        repo = repo_info["name"]

        logger.info(f"Creating repo {repo} for {owner}")

        # Upload initial files
        readme = f"# {project_name}\n\n{description}"
        main_py = 'def main():\n    print("Hello from PBOT!")\n\nif __name__ == "__main__":\n    main()'
        pyproject = f"""\
[tool.poetry]
name = "{project_name.replace('-', '_')}"
version = "0.1.0"
description = "{description}"
authors = ["pbot-cli <cli@yourorg.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

        upload_file(owner, repo, "README.md", readme)
        upload_file(owner, repo, "src/main.py", main_py)
        upload_file(owner, repo, "pyproject.toml", pyproject)

        typer.secho(f"🎉 Project ready: {repo_info['html_url']}", fg=typer.colors.GREEN)
        logger.info(f"Project created at: {repo_info['html_url']}")

    except Exception as e:
        typer.secho("❌ Something went wrong during project creation.", fg=typer.colors.RED)
        logger.exception("Project creation failed.")
        capture_exception(e)
        raise typer.Exit(1)
