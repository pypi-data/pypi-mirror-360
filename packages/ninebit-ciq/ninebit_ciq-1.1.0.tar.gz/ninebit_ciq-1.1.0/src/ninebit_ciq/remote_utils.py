import requests
import tempfile


def download_from_sharepoint(url: str, access_token: str) -> tempfile._TemporaryFileWrapper:
    """
    Downloads a file from SharePoint and returns a temporary file object.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp.write(response.content)
    tmp.flush()
    return tmp
