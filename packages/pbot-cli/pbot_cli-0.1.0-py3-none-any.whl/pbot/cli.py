# src/pbot/cli.py
import typer
from pbot.commands.init import base, python
from pbot.errors.sentry import init_sentry
from pbot.logging.logger import setup_logger
from pbot.metrics.prometheus import start_metrics_server, count_command

logger = setup_logger()
init_sentry()
start_metrics_server()

app = typer.Typer()
init_app = base.app
init_app.command("python")(python.python_project_init)

app.add_typer(init_app, name="init")
