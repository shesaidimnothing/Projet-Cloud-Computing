import io
from azure.storage.blob import BlobServiceClient, ContentSettings
from flask import current_app


def get_blob_service():
    conn_str = current_app.config["AZURE_STORAGE_CONNECTION_STRING"]
    return BlobServiceClient.from_connection_string(conn_str)


def upload_file_to_blob(file_obj, container, blob_name, content_type="application/octet-stream"):
    """Upload a file to Azure Blob Storage. Returns True on success."""
    try:
        blob_service = get_blob_service()
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(
            file_obj,
            overwrite=True,
            content_settings=content_settings,
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Blob upload error: {e}")
        return False


def download_file_from_blob(container, blob_name):
    """Download a file from Azure Blob Storage. Returns (bytes, content_type) or (None, None)."""
    try:
        blob_service = get_blob_service()
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        download = blob_client.download_blob()
        data = download.readall()
        content_type = download.properties.content_settings.content_type
        return data, content_type
    except Exception as e:
        current_app.logger.error(f"Blob download error: {e}")
        return None, None


def delete_file_from_blob(container, blob_name):
    """Delete a file from Azure Blob Storage. Returns True on success."""
    try:
        blob_service = get_blob_service()
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        current_app.logger.error(f"Blob delete error: {e}")
        return False


def list_blobs(container, prefix=""):
    """List all blobs in a container with optional prefix."""
    try:
        blob_service = get_blob_service()
        container_client = blob_service.get_container_client(container)
        blobs = container_client.list_blobs(name_starts_with=prefix if prefix else None)
        return [
            {
                "name": blob.name,
                "container": container,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat(),
                "content_type": blob.content_settings.content_type,
            }
            for blob in blobs
        ]
    except Exception as e:
        current_app.logger.error(f"Blob list error: {e}")
        return []


def list_containers():
    """List all containers in the storage account."""
    try:
        blob_service = get_blob_service()
        return [
            {"name": c.name, "last_modified": c.last_modified.isoformat()}
            for c in blob_service.list_containers()
        ]
    except Exception as e:
        current_app.logger.error(f"Container list error: {e}")
        return []
