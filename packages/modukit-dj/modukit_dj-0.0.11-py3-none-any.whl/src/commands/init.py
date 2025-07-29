import subprocess

import typer

from src.modukit_binary import get_modukit_binary_path

init_app = typer.Typer()


@init_app.command()
def init(
        ctx: typer.Context,
        name: str = typer.Option(None, "--name", "-n", help="Module name")
):
    typer.echo("[modukit] Initializing new module...")
    modukit_binary = get_modukit_binary_path()
    cmd = [modukit_binary, 'init']
    if name:
        typer.echo(f"[modukit] Using module name: {name}")
        cmd += ["--name", name]
    cmd += [*ctx.args, '-j']

    result = subprocess.run(
        cmd,
        capture_output=False  # Allow interactive prompts
    )

    if result.returncode != 0:
        typer.echo(f"[modukit] Error initializing module. Exit code: {result.returncode}")
        raise typer.Exit(code=result.returncode)
    typer.echo("[modukit] Module initialization complete.")
