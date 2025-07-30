import requests
from zenodo_api.upload_files import load_access_token, upload_file, upload_metadata
from zenodo_api.url_selector import url_selector


def _publish_new_version(concept_rec_id, file_path, is_sandbox):
    new_deposition = open_new_deposition(concept_rec_id, is_sandbox)

    new_deposition_json = new_deposition.json()
    upload_file_in_new_deposition(new_deposition_json, file_path, is_sandbox)

    access_token = load_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = url_selector(tests=is_sandbox) + "/deposit/depositions"
    response = requests.post(
        f"{base_url}/{new_deposition_json['id']}/actions/publish",
        headers=headers,
    )

    return response


def open_new_deposition(concept_rec_id, is_test):
    latest_version_id = get_latest_version_id(concept_rec_id, is_sandbox=is_test)
    new_deposition = create_draft_of_new_version(latest_version_id, is_sandbox=is_test)
    return new_deposition


def upload_file_in_new_deposition(new_deposition_json, file_path, is_sandbox):
    upload_new_deposition_metadata(new_deposition_json, is_sandbox)
    delete_previous_files(new_deposition_json)
    bucket_url = new_deposition_json["links"]["bucket"]
    response = upload_file(bucket_url, file_path)
    return response


def get_latest_version_id(concept_rec_id, is_sandbox):
    access_token = load_access_token()
    base_url = url_selector(tests=is_sandbox) + "/records"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{base_url}/{concept_rec_id}", headers=headers)

    return response.json()["id"]


def create_draft_of_new_version(latest_version_id, is_sandbox):
    access_token = load_access_token()
    base_url = url_selector(tests=is_sandbox) + "/deposit/depositions"

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.post(f"{base_url}/{latest_version_id}/actions/newversion", headers=headers)

    return response


def upload_new_deposition_metadata(new_deposition_json, is_sandbox):
    new_deposition_id = new_deposition_json["id"]
    previous_metadata = new_deposition_json["metadata"]
    upload_metadata(previous_metadata, new_deposition_id, is_sandbox)


def delete_previous_files(new_deposition_json):
    access_token = load_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    for files in new_deposition_json["files"]:
        requests.delete(files["links"]["self"], headers=headers)
