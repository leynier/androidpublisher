from json import loads
from mimetypes import add_type
from typing import Optional

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials
from typer import echo


def upload(
    package_name: str,
    aab_file: str = "app.aab",
    track: str = "internal",
    json_key: str = "credential.json",
    json_content: Optional[str] = None,
):
    add_type("application/octet-stream", ".aab")
    if json_content:
        content_file = json_content
    else:
        json_file = open(json_key, encoding="utf-8")
        content_file = json_file.read()
        json_file.close()
    print("= credential.json =====================================")
    print(content_file)
    print("=======================================================")
    json_data = loads(content_file)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json_data,
        scopes="https://www.googleapis.com/auth/androidpublisher",
    )
    http = Http()
    http = credentials.authorize(http)

    service = build("androidpublisher", "v3", http=http)

    try:
        edit_request = service.edits().insert(  # type: ignore
            body={},
            packageName=package_name,
        )
        result = edit_request.execute()
        edit_id = result["id"]

        aab_response = (
            service.edits()  # type: ignore
            .bundles()
            .upload(
                editId=edit_id,
                packageName=package_name,
                media_body=aab_file,
            )
            .execute()
        )

        version_code = str(aab_response["versionCode"])

        echo(f"Version code {version_code} has been uploaded")

        track_response = (
            service.edits()  # type: ignore
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

        echo(track_message)

        commit_request = (
            service.edits()  # type: ignore
            .commit(
                editId=edit_id,
                packageName=package_name,
            )
            .execute()
        )

        echo(f"Edit \"{commit_request['id']}\" has been committed")

    except AccessTokenRefreshError:
        error_message = "The credentials have been revoked or expired, "
        error_message += "please re-run the application to re-authorize"
        echo(error_message)
