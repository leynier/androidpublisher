from mimetypes import add_type

import typer
from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


def upload(
    package_name: str,
    aab_file: str = "app.aab",
    track: str = "internal",
    json_key: str = "credential.json",
):
    add_type("application/octet-stream", ".aab")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_key,
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
        edit_id = result["id"]

        aab_response = (
            service.edits()
            .bundles()
            .upload(
                editId=edit_id,
                packageName=package_name,
                media_body=aab_file,
            )
            .execute()
        )

        version_code = str(aab_response["versionCode"])

        typer.echo(f"Version code {version_code} has been uploaded")

        track_response = (
            service.edits()
            .tracks()
            .update(
                editId=edit_id,
                track=track,
                packageName=package_name,
                body={
                    "releases": [
                        {
                            "name": f"Version {version_code}",
                            "versionCodes": [version_code],
                            "status": "completed",
                        }
                    ]
                },
            )
            .execute()
        )

        track_message = f"Track {track_response['track']} is set with "
        track_message += f"releases: {track_response['releases']}"

        typer.echo(track_message)

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
        error_message = "The credentials have been revoked or expired, "
        error_message += "please re-run the application to re-authorize"
        typer.echo(error_message)
