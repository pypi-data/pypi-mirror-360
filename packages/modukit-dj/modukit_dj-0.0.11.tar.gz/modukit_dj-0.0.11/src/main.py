import typer
from dotenv import load_dotenv

from src.commands.add import add_app
from src.commands.init import init_app
from src.commands.list import list_app
from src.commands.version import version_app
from src.commands.install import install_app
from src.modukit_binary import init_binaries

app = typer.Typer()

# Load environment variables from .env file
load_dotenv()

# Resolve required binaries
init_binaries()

# Add subcommands
app.add_typer(version_app)
app.add_typer(add_app)
app.add_typer(list_app)
app.add_typer(init_app)
app.add_typer(install_app)

if __name__ == "__main__":
    # Run the app
    app()
