import typer

from daydream.cli.client._app import client_app
from daydream.cli.tools._app import tools_app

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)
app.add_typer(tools_app, name="tools")
app.add_typer(client_app, name="client")
