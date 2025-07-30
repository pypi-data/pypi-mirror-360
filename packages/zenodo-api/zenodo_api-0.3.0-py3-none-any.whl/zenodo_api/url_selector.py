def url_selector(tests=False):
    if tests:
        return "https://sandbox.zenodo.org/api"

    return "https://zenodo.org/api"
