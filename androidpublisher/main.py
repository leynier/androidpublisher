from enum import Enum
from pathlib import Path

import typer

from .upload import upload


class Track(str, Enum):
    internal = "internal"
    alpha = "alpha"
    beta = "beta"
    production = "production"
    rollout = "rollout"


app = typer.Typer()


@app.callback()
def callback():
    """
    Android Publisher
    """


@app.command(name="upload")
def upload_command(
    package_name: str,
    aab_file: Path = typer.Option(
        "app.aab",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    track: Track = typer.Option(Track.internal),
    json_key: Path = typer.Option(
        "credential.json",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
):
    upload(
        package_name=package_name,
        aab_file=str(aab_file),
        track=track.value,
        json_key=str(json_key),
    )
