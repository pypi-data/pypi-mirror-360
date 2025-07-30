from daydream.cli._app import app


@app.command()
def version() -> None:
    """
    Display the version of the Daydream CLI.
    """
    from daydream import __version__

    print(f"daydream {__version__}")
