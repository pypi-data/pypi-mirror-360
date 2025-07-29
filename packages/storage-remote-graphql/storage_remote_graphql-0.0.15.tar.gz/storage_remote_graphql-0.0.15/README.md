# RemoteCirclesStorage Class

The `RemoteCirclesStorage` class provides methods for interacting with the remote storage service.  
It allows you to upload and download files from the remote storage.

## Installation

```bash
pip install storage-remote
```

Usage Example:

```python
from storage_remote.remote_circles_storage import RemoteCirclesStorage

created_user_id = entity_type_id = profile_id = 0  # TODO: Replace with your values

# Uploading a file
remote_storage = RemoteCirclesStorage()
remote_path = remote_storage.put("file.txt", "/local/path/file.txt", created_user_id, entity_type_id, profile_id)
print(f"Uploaded file to remote path: {remote_path}")

# Downloading a file
downloaded_contents = remote_storage.download("file.txt", "/local/path/file.txt", entity_type_id, profile_id)
print(f"Downloaded file contents: {downloaded_contents}")
```