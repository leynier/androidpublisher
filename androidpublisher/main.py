import typer


app = typer.Typer()


@app.callback()
def callback():
    """
    Android Publisher
    """


@app.command()
def hello():
    """
    Print 'Hello World!'
    """
    typer.echo("Hello World!")
