from typing import TypedDict


class SharePointConfig(TypedDict):
    tenant_id: str
    client_id: str
    client_secret: str
    sharepoint_host: str
    site_name: str
    document_library_name: str
    target_file_name: str
