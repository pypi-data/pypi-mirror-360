import typer

version_app = typer.Typer()


@version_app.command()
def version():
    print("My CLI Version 1.0")