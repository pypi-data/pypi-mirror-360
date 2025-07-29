import json
import subprocess

import typer
from dotenv import load_dotenv

from src.commands.install import install_module
from src.modukit_binary import get_modukit_binary_path
from src.utils.modules import save_module

add_app = typer.Typer()


@add_app.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
def add(ctx: typer.Context):
    """
    Add a module to the local environment.
    """
    add_module(args=(ctx.args or []))
    typer.echo("[modukit] Module add process finished.")


def add_module(args: list[str] = None, path: str = None):
    # Load environment variables from .env file
    load_dotenv()
    # check if path is None and set it to the current directory
    if path is None:
        path = "."

    # Run the modukit binary with the provided arguments
    modukit_binary = get_modukit_binary_path()
    result = subprocess.run(
        [modukit_binary, 'add', *(args or []), '-j'],
        capture_output=True,
        text=True,
    )

    # Check if the command was successful
    if result.returncode != 0:
        typer.echo(f"[modukit] Error running modukit add command: {result.stderr}")
        raise typer.Exit(code=result.returncode)

    typer.echo("[modukit] Parsing modukit output...")
    # Parse the JSON output
    modukit_json = json.loads(result.stdout)
    module_path = "."

    # Save the module to the specified path
    if modukit_json is not None and modukit_json['tempDir'] is not None:
        module_path = save_module(modukit_json['tempDir'], modukit_json['moduspec'], path)
        typer.echo(f"[modukit] Module {modukit_json['moduspec']['name']} added successfully")

    # Check if the module has dependencies and install them recursively
    moduspec = modukit_json['moduspec']
    if moduspec['dependencies']:
        typer.echo(f"[modukit] Module has dependencies: {moduspec['dependencies']}. Installing dependencies...")
        for dep in moduspec['dependencies']:
            install_module(args=[], path=module_path)
        typer.echo("[modukit] All dependencies installed.")
