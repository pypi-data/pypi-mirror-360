"""
WebDAV client implementation for storage manager.
"""
from webdav4.client import Client, ResourceNotFound
from webdav4.fsspec import WebdavFileSystem


class WebDAVClient:
    """
    WebDAV client wrapper for interacting with WebDAV servers like NextCloud.
    """

    def __init__(self, base_url, username=None, password=None, token=None, verify=True):
        """
        Initialize the WebDAV client.

        :param base_url: Base URL of the WebDAV server (e.g., "https://nextcloud.example.com/remote.php/dav/files/username/")
        :param username: Username for authentication
        :param password: Password for authentication
        :param token: Authentication token (alternative to username/password)
        :param verify: Whether to verify SSL certificates
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = token
        # Set up verification
        if isinstance(verify, str) and verify.lower() == 'false':
            self.verify = False
        else:
            self.verify = verify

        # Set up authentication
        if token:
            self.auth = token
        elif username and password:
            self.auth = (username, password)
        else:
            self.auth = None

        # Initialize the client
        self.client = Client(
            base_url,
            auth=self.auth,
            verify=self.verify
        )

        # Initialize the fsspec filesystem
        self.fs = WebdavFileSystem(
            base_url,
            auth=self.auth,
            verify=self.verify
        )

    def exists(self, path):
        """
        Check if a path exists on the WebDAV server.

        :param path: Path to check
        :return: True if exists, False otherwise
        """
        try:
            return self.client.exists(path)
        except Exception:
            return False

    def list_directory(self, path="", detail=False):
        """
        List contents of a directory.

        :param path: Directory path to list
        :param detail: Whether to return detailed information
        :return: List of files/directories or detailed information
        """
        try:
            return self.client.ls(path, detail=detail)
        except ResourceNotFound:
            # Return empty list if directory doesn't exist
            return [] if not detail else {}

    def ensure_directory_exists(self, path):
        """
        Ensure a directory exists, creating parent directories if needed.

        :param path: Directory path to ensure exists
        """
        if not path or path == "/" or path == ".":
            return

        # Check if the directory already exists
        if self.exists(path):
            return

        # Split the path into components
        parts = path.strip('/').split('/')
        current_path = ""

        # Create each directory in the path if it doesn't exist
        for part in parts:
            if not part:
                continue

            current_path = f"{current_path}/{part}" if current_path else part

            if not self.exists(current_path):
                try:
                    self.client.mkdir(current_path)
                except ResourceNotFound:
                    # If parent directory doesn't exist, create it first
                    parent_path = '/'.join(current_path.split('/')[:-1])
                    self.ensure_directory_exists(parent_path)
                    # Then try to create the directory again
                    self.client.mkdir(current_path)
                except Exception as e:
                    # If directory already exists or other error, log and continue
                    if self.exists(current_path):
                        pass  # Directory exists, which is fine
                    else:
                        raise e  # Re-raise if it's a different error

    def create_directory(self, path):
        """
        Create a directory on the WebDAV server.

        :param path: Directory path to create
        """
        self.ensure_directory_exists(path)

    def upload_file(self, local_path, remote_path):
        """
        Upload a file to the WebDAV server.

        :param local_path: Local file path
        :param remote_path: Remote file path
        """
        # Ensure parent directory exists
        parent_dir = '/'.join(remote_path.split('/')[:-1])
        if parent_dir:
            self.ensure_directory_exists(parent_dir)

        # Upload the file
        self.client.upload_file(local_path, remote_path)

    def download_file(self, remote_path, local_path):
        """
        Download a file from the WebDAV server.

        :param remote_path: Remote file path
        :param local_path: Local file path
        """
        self.client.download_file(remote_path, local_path)

    def delete(self, path, recursive=False):
        """
        Delete a file or directory on the WebDAV server.

        :param path: Path to delete
        :param recursive: Whether to delete recursively (for directories)
        """
        try:
            self.client.remove(path, recursive=recursive)
        except ResourceNotFound:
            # If the resource doesn't exist, that's fine - it's already gone
            pass
        except Exception as e:
            # Re-raise other exceptions
            raise e

    def get_fs(self):
        """
        Get the fsspec filesystem instance.

        :return: WebdavFileSystem instance
        """
        return self.fs

    # Add fsspec-compatible method aliases
    def mkdir(self, path, create_parents=True):
        """
        Create a directory (fsspec-compatible method).

        :param path: Directory path to create
        :param create_parents: Whether to create parent directories
        """
        if create_parents:
            self.ensure_directory_exists(path)
        else:
            try:
                self.client.mkdir(path)
            except ResourceNotFound:
                # If parent directory doesn't exist and create_parents is False, raise error
                raise

    def ls(self, path="", detail=False):
        """
        List contents of a directory (fsspec-compatible method).

        :param path: Directory path to list
        :param detail: Whether to return detailed information
        :return: List of files/directories or detailed information
        """
        return self.list_directory(path, detail=detail)

    def rm(self, path, recursive=False):
        """
        Delete a file or directory (fsspec-compatible method).

        :param path: Path to delete
        :param recursive: Whether to delete recursively (for directories)
        """
        self.delete(path, recursive=recursive)

    def makedirs(self, path, exist_ok=True):
        """
        Create a directory and all parent directories (fsspec-compatible method).

        :param path: Directory path to create
        :param exist_ok: Whether it's okay if the directory already exists
        """
        self.ensure_directory_exists(path)
