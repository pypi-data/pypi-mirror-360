import json
import subprocess

import typer

from src.modukit_binary import get_modukit_binary_path
from src.utils.modules import save_module

install_app = typer.Typer()


@install_app.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
def install(ctx: typer.Context):
    """
    install a module to the local environment.
    """
    install_module(args=(ctx.args or []))
    typer.echo("[modukit] Module installation finished.")


def install_module(args: list[str] = None, path: str = None):
    # check if path is None and set it to the current directory
    if path is None:
        path = "."

    # Run the modukit binary with the provided arguments
    modukit_binary = get_modukit_binary_path()
    result = subprocess.run(
        [modukit_binary, 'install', *args, '-j'],
        capture_output=True,
        text=True,
        cwd=path,
    )

    # Check if the command was successful
    if result.returncode != 0:
        typer.echo(f"[modukit] Error running modukit install command: {result.stderr}")
        raise typer.Exit(code=result.returncode)

    typer.echo("[modukit] Parsing modukit output...")
    # Parse the JSON output
    stdout_json = json.loads(result.stdout)
    module_path = "."

    for dependency in stdout_json:
        # Save the module to the specified path
        if dependency is not None and dependency['tempDir'] is not None:
            module_path = save_module(dependency['tempDir'], dependency['moduspec'], path)
            typer.echo(f"[modukit] Dependency {dependency['moduspec']['name']} installed successfully")

        # Check if the module has dependencies and install them recursively
        moduspec = dependency['moduspec']
        if moduspec['dependencies']:
            typer.echo(f"[modukit] Dependency has sub-dependencies: {moduspec['dependencies']}. Start Installing...")
            install_module(args=[], path=module_path)
