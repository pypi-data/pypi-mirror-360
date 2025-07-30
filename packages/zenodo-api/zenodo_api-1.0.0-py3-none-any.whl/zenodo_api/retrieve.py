import requests
from zenodo_api.upload_files import load_access_token
from zenodo_api.url_selector import url_selector


def search_record_by_two_parameters(parameter_1, parameter_2, url_api):
    query = f'"{parameter_1}" AND "{parameter_2}"'
    response_info = requests.get(
        url_api + "/records",
        params={"q": query},
        headers={"Authorization": f"Bearer {load_access_token()}"},
    )
    return response_info


def search_deposition_by_title(title_word, is_sandbox):
    query = f'"{title_word}"'
    url_api = url_selector(is_sandbox)
    response_info = requests.get(
        url_api + "/deposit/depositions",
        params={"q": query},
        headers={"Authorization": f"Bearer {load_access_token()}"},
    )
    latest_draft_link = response_info.json()[0]["links"]["latest_draft"]
    return latest_draft_link


def search_by_doi(doi, url_api):
    query = f"conceptdoi:{doi}"
    response_info = requests.get(
        url_api + "/records",
        params={"q": query},
        headers={"Authorization": f"Bearer {load_access_token()}"},
    )
    return response_info


def download_file_by_doi(doi, is_sandbox):
    url_api = url_selector(tests=is_sandbox)
    response_info = search_by_doi(doi, url_api)
    extracted_id = extract_record_id_and_file_id(response_info.json())
    for file in extracted_id["file_id"]:
        downloaded_file = download_file(extracted_id["record_id"], file, url_api)
    return downloaded_file


def download_file(id, id_file, url_api):
    download_info = get_download(id, id_file, url_api)
    download_response = requests.get(
        download_info["url"],
        headers={"Authorization": f"Bearer {load_access_token()}"},
    )

    with open(download_info["filename"], mode="wb") as file:
        file.write(download_response.content)

    return download_response


def get_download(id, id_file, url_api):
    response_info = retrieve_file_info(id, id_file, url_api)
    url = response_info.json()["links"]["download"]
    filename = response_info.json()["filename"]

    return {"url": url, "filename": filename}


def retrieve_file_info(id, id_file, url_api):
    ACCESS_TOKEN = load_access_token()
    url = url_api + f"/deposit/depositions/{id}/files/{id_file}"
    response_info = requests.get(
        url,
        [("access_token", ACCESS_TOKEN), ("size", 1000)],
    )

    return response_info


def extract_record_id_and_file_id(search_response):
    record_id = search_response["hits"]["hits"][0]["id"]
    access_token = load_access_token()
    response_info = requests.get(
        search_response["hits"]["hits"][0]["links"]["files"],
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response_files = response_info.json()
    file_id = [file_entry["file_id"] for file_entry in response_files["entries"]]

    return {"record_id": record_id, "file_id": file_id}
