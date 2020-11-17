from enum import Enum
from mimetypes import add_type
from pathlib import Path

import typer
from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


class Track(str, Enum):
    internal = "internal"
    alpha = "alpha"
    beta = "beta"
    production = "production"
    rollout = "rollout"


app = typer.Typer()
add_type("application/octet-stream", ".aab")


@app.callback()
def callback():
    """
    Android Publisher
    """


@app.command()
def upload(
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
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        str(json_key),
        scopes="https://www.googleapis.com/auth/androidpublisher",
    )
    http = Http()
    http = credentials.authorize(http)

    service = build("androidpublisher", "v3", http=http)

    try:
        edit_request = service.edits().insert(
            body={},
            packageName=package_name,
        )
        result = edit_request.execute()
        typer.echo(result)
        edit_id = result["id"]

        aab_response = (
            service.edits()
            .bundles()
            .upload(
                editId=edit_id,
                packageName=package_name,
                media_body=str(aab_file),
            )
            .execute()
        )

        typer.echo(
            f"Version code {aab_response['versionCode']} has been uploaded",
        )

        track_response = (
            service.edits()
            .tracks()
            .update(
                editId=edit_id,
                track=track.value,
                packageName=package_name,
                body={
                    "releases": [
                        {
                            "name": "My first API release",
                            "versionCodes": [str(aab_response["versionCode"])],
                            "status": "completed",
                        }
                    ]
                },
            )
            .execute()
        )

        typer.echo(
            f"Track {track_response['track']} is set with releases: \
            {track_response['releases']}",
        )

        commit_request = (
            service.edits()
            .commit(
                editId=edit_id,
                packageName=package_name,
            )
            .execute()
        )

        typer.echo(f"Edit \"{commit_request['id']}\" has been committed")

    except AccessTokenRefreshError:
        typer.echo(
            "The credentials have been revoked or expired, please \
            re-run the application to re-authorize",
        )
