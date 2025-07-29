import typer

from src.utils.binaries import resolve_modukit_binary

modukit_binary_path: str = None  # Ensure this is always defined


def get_modukit_binary_path() -> str:
    """
    Get the path to the modukit binary.
    This function is used to resolve the path to the modukit binary.
    """
    if modukit_binary_path is None:
        raise ValueError("modukit_binary_path is not initialized.")
    return modukit_binary_path


def init_binaries():
    global modukit_binary_path
    try:
        modukit_binary_path = resolve_modukit_binary()
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        typer.Exit()
        exit(1)
