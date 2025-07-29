import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
from .app_types import SharePointConfig

load_dotenv()


def get_graph_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scopes = ["https://graph.microsoft.com/.default"]

    app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    token_response = app.acquire_token_for_client(scopes=scopes)

    if "access_token" not in token_response:
        raise Exception(f"Auth failed: {token_response}")

    return token_response["access_token"]


def get_site_id(headers: dict, sharepoint_host: str, site_name: str) -> str:
    url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_host}:/sites/{site_name}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Site lookup failed: {resp.text}")
    return resp.json()["id"]


def get_drive_id(headers: dict, site_id: str, document_library_name: str) -> str:
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Drive lookup failed: {resp.text}")

    for drive in resp.json()["value"]:
        if drive["name"].lower() == document_library_name.lower():
            return drive["id"]

    raise Exception(f"Document library '{document_library_name}' not found.")


def list_files(headers: dict, drive_id: str) -> list[dict]:
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"File list failed: {resp.text}")
    return resp.json().get("value", [])


def find_file_by_name(files: list[dict], target_name: str) -> dict | None:
    return next((item for item in files if item["name"] == target_name), None)


def download_file(download_url: str) -> bytes:
    resp = requests.get(download_url)
    resp.raise_for_status()
    return resp.content


def download_file_from_sharepoint(config: SharePointConfig) -> bytes:
    # Auth
    access_token = get_graph_access_token(config.get("tenant_id"), config.get("client_id"), config.get("client_secret"))
    headers = {"Authorization": f"Bearer {access_token}"}

    # Resolve site and drive
    site_id = get_site_id(headers, config.get("sharepoint_host"), config.get("site_name"))
    drive_id = get_drive_id(headers, site_id, config.get("document_library_name"))

    # Locate file
    files = list_files(headers, drive_id)
    target_file = find_file_by_name(files, config.get("target_file_name"))
    if not target_file:
        raise Exception("File  not found in SharePoint.")

    # Download content
    download_url = target_file["@microsoft.graph.downloadUrl"]
    return download_file(download_url)


def get_sharepoint_configuration(site_name: str, folder: str, file_name: str) -> SharePointConfig:
    return SharePointConfig(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        sharepoint_host=os.getenv("SHAREPOINT_HOST"),
        site_name=site_name,
        document_library_name=folder,
        target_file_name=file_name,
    )


# if __name__ == "__main__":
# file_bytes = download_file_from_sharepoint(
#     tenant_id=os.getenv("AZURE_TENANT_ID"),
#     client_id=os.getenv("AZURE_CLIENT_ID"),
#     client_secret=os.getenv("AZURE_CLIENT_SECRET"),
#     sharepoint_host=os.getenv("SHAREPOINT_HOST"),
#     site_name="KnowledgeCenter",
#     document_library_name="CIQDocs",
#     target_file_name="BOFA-CC-Elite.pdf"
# )

# with open("downloaded_file.pdf", "wb") as f:
#     f.write(file_bytes)
