import requests
import os
import json
import pathlib
from datetime import date
from zenodo_api.url_selector import url_selector


def call_depositions(is_sandbox):
    ACCESS_TOKEN = load_access_token()
    url_api = url_selector(is_sandbox)
    empty_upload = requests.get(
        url_api + "/deposit/depositions",
        [("access_token", ACCESS_TOKEN), ("size", 200), ("all_versions", "true")],
    )
    return empty_upload


def load_access_token():
    return os.environ.get("ACCESS_TOKEN")


def create_deposition_in_new_record(is_sandbox):
    url_api = url_selector(is_sandbox)
    headers = {"Authorization": f"Bearer {load_access_token()}", "Content-Type": "application/json"}
    response = requests.post(
        url_api + "/deposit/depositions",
        json={},
        headers=headers,
    )
    return response


def upload_file_in_new_record(file_path, is_sandbox):
    empty_upload = create_deposition_in_new_record(is_sandbox)

    bucket_url = empty_upload.json()["links"]["bucket"]

    response_upload = upload_file(bucket_url, file_path)
    return {
        "response_upload": response_upload,
        "latest_draft": empty_upload.json()["links"]["latest_draft"],
    }


def upload_file(bucket_url, file_path):
    headers = {"Authorization": f"Bearer {load_access_token()}"}
    path = pathlib.Path(file_path)
    with open(path, "rb") as file_content:
        response_upload = requests.put(
            f"{bucket_url}/{path.name}",
            data=file_content,
            headers=headers,
        )

    return response_upload


def upload_metadata_in_new_record(data_dict, is_sandbox):
    empty_upload = create_deposition_in_new_record(is_sandbox)
    deposition_id = empty_upload.json()["id"]
    response = upload_metadata(data_dict["metadata"], deposition_id, is_sandbox)
    return response


def upload_metadata(previous_metadata, deposition_id, is_sandbox):
    default_metadata = {
        "creators": [{"name": "Grupo de Ecología y Conservación de Islas"}],
        "publication_date": str(date.today()),
    }
    previous_metadata.update(default_metadata)
    new_metadata = {"metadata": previous_metadata}
    headers = {"Authorization": f"Bearer {load_access_token()}", "Content-Type": "application/json"}
    url_api = url_selector(is_sandbox)
    response = requests.put(
        url_api + f"/deposit/depositions/{deposition_id}",
        data=json.dumps(new_metadata),
        headers=headers,
    )

    return response
