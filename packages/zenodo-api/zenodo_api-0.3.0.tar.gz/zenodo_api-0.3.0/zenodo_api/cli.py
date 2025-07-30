import typer
from zenodo_api.retrieve import download_file_by_doi
from zenodo_api.new_version import _publish_new_version

cli = typer.Typer()


@cli.command()
def version():
    pass


@cli.command()
def download_from_geci_zenodo(
    doi: str = typer.Option(), is_sandbox: bool = typer.Option(False, "--is-sandbox")
):
    download_file_by_doi(doi, is_sandbox)


@cli.command()
def publish_new_version(
    concept_record_id: int = typer.Option(),
    file_path: str = typer.Option(),
    is_sandbox: bool = typer.Option(False, "--is-sandbox"),
):
    """
    Publish a new version of a file in Zenodo.
    """
    response = _publish_new_version(concept_record_id, file_path, is_sandbox)
    print(response.status_code)
