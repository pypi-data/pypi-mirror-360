import pandas as pd
import fsspec
import threading
import uuid
import hashlib
import base64
import json
from typing import List, Optional, Set, Dict, Any

from sibi_dst.utils import Logger


class MissingManifestManager:
    """
    Thread-safe manager for a “missing-partitions” manifest (Parquet file).
    """

    def __init__(
            self,
            fs: fsspec.AbstractFileSystem,
            manifest_path: str,
            clear_existing: bool = False,
            **kwargs: Any,
    ):
        self.fs = fs
        self.manifest_path = manifest_path.rstrip("/")
        self.clear_existing = clear_existing

        self.debug: bool = kwargs.get("debug", False)
        self.logger = kwargs.get(
            "logger",
            Logger.default_logger(logger_name="missing_manifest_manager")
        )
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

        self._new_records: List[Dict[str, str]] = []
        self._loaded_paths: Optional[Set[str]] = None
        self._lock = threading.RLock()

    def _safe_exists(self, path: str) -> bool:
        try:
            return self.fs.exists(path)
        except Exception as e:
            self.logger.warning(f"Error checking existence of '{path}': {e}")
            return False

    def load_existing(self) -> Set[str]:
        with self._lock:
            if self._loaded_paths is not None:
                return self._loaded_paths

            if not self._safe_exists(self.manifest_path):
                self._loaded_paths = set()
                return self._loaded_paths

            try:
                df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                paths = (
                    df.get("path", pd.Series(dtype=str))
                    .dropna().astype(str)
                    .loc[lambda s: s.str.strip().astype(bool)]
                )
                self._loaded_paths = set(paths.tolist())
            except Exception as e:
                self.logger.warning(f"Failed to load manifest '{self.manifest_path}': {e}")
                self._loaded_paths = set()

            return self._loaded_paths

    def record(self, full_path: str) -> None:
        if not full_path or not isinstance(full_path, str):
            return
        with self._lock:
            self._new_records.append({"path": full_path})

    def save(self) -> None:
        with self._lock:
            new_df = pd.DataFrame(self._new_records)
            should_overwrite = self.clear_existing or not self._safe_exists(self.manifest_path)
            if new_df.empty and not should_overwrite:
                return

            new_df = (
                new_df.get("path", pd.Series(dtype=str))
                .dropna().astype(str)
                .loc[lambda s: s.str.strip().astype(bool)]
                .to_frame()
            )

            if should_overwrite:
                out_df = new_df
            else:
                try:
                    old_df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                    old_paths = (
                        old_df.get("path", pd.Series(dtype=str))
                        .dropna().astype(str)
                        .loc[lambda s: s.str.strip().astype(bool)]
                        .to_frame()
                    )
                    out_df = pd.concat([old_paths, new_df], ignore_index=True)
                except Exception as e:
                    self.logger.warning(f"Could not merge manifest, overwriting: {e}")
                    out_df = new_df

            out_df = out_df.drop_duplicates(subset=["path"]).reset_index(drop=True)

            parent = self.manifest_path.rsplit("/", 1)[0]
            try:
                self.fs.makedirs(parent, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Could not create manifest directory '{parent}': {e}")

            temp_path = f"{self.manifest_path}.tmp-{uuid.uuid4().hex}"
            try:
                out_df.to_parquet(
                    temp_path,
                    filesystem=self.fs,
                    index=False
                )
                self.fs.copy(temp_path, self.manifest_path)
                self.logger.info(f"Copied manifest to {self.manifest_path} (temp: {temp_path})")
            except Exception as e:
                self.logger.error(f"Failed to write or copy manifest: {e}")
                raise

            self.logger.debug(f"Temp file left behind: {temp_path}")
            self._new_records.clear()
            self._loaded_paths = set(out_df["path"].tolist())

    def cleanup_temp_manifests(self) -> None:
        if not hasattr(self.fs, "s3"):
            self.logger.info("Filesystem is not s3fs; skipping temp cleanup.")
            return

        try:
            bucket, prefix = self._parse_s3_path(self.manifest_path.rsplit("/", 1)[0])
            files = self.fs.ls(f"s3://{bucket}/{prefix}", detail=True)
            temp_files = [
                f for f in files
                if f["name"].endswith(".parquet") and ".tmp-" in f["name"]
            ]
            if not temp_files:
                return

            objects = [{"Key": f["name"].replace(f"{bucket}/", "", 1)} for f in temp_files]
            delete_payload = {
                "Objects": objects,
                "Quiet": True
            }

            json_payload = json.dumps(delete_payload).encode("utf-8")
            content_md5 = base64.b64encode(hashlib.md5(json_payload).digest()).decode("utf-8")

            self.fs.s3.meta.client.delete_objects(
                Bucket=bucket,
                Delete=delete_payload,
                ContentMD5=content_md5
            )
            self.logger.info(f"Deleted {len(objects)} temp manifest files in s3://{bucket}/{prefix}")
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp manifest files: {e}")

    @staticmethod
    def _parse_s3_path(s3_path: str):
        if not s3_path.startswith("s3://"):
            raise ValueError("Invalid S3 path. Must start with 's3://'.")
        path_parts = s3_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ""
        return bucket_name, prefix

# import pandas as pd
# import fsspec
# import threading
# import uuid
# from typing import List, Optional, Set, Dict, Any
#
# from sibi_dst.utils import Logger
#
#
# class MissingManifestManager:
#     """
#     Thread-safe manager for a “missing-partitions” manifest (Parquet file).
#     """
#
#     def __init__(
#         self,
#         fs: fsspec.AbstractFileSystem,
#         manifest_path: str,
#         clear_existing: bool = False,
#         **kwargs: Any,
#     ):
#         self.fs = fs
#         self.manifest_path = manifest_path.rstrip("/")
#         self.clear_existing = clear_existing
#
#         self.debug: bool = kwargs.get("debug", False)
#         self.logger = kwargs.get(
#             "logger",
#             Logger.default_logger(logger_name="missing_manifest_manager")
#         )
#         self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
#
#         # In-memory list for new paths
#         self._new_records: List[Dict[str, str]] = []
#         # Cached set of existing paths
#         self._loaded_paths: Optional[Set[str]] = None
#
#         # Use a reentrant lock so save() can call load_existing() safely
#         self._lock = threading.RLock()
#
#     def _safe_exists(self, path: str) -> bool:
#         try:
#             return self.fs.exists(path)
#         except PermissionError:
#             if self.debug:
#                 self.logger.debug(f"Permission denied checking existence of '{path}'")
#             return False
#         except Exception as e:
#             self.logger.warning(f"Error checking existence of '{path}': {e}")
#             return False
#
#     def load_existing(self) -> Set[str]:
#         """
#         Load and cache existing manifest paths.
#         """
#         with self._lock:
#             if self._loaded_paths is not None:
#                 return self._loaded_paths
#
#             if not self._safe_exists(self.manifest_path):
#                 self._loaded_paths = set()
#                 return self._loaded_paths
#
#             try:
#                 df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
#                 paths = (
#                     df.get("path", pd.Series(dtype=str))
#                       .dropna().astype(str)
#                       .loc[lambda s: s.str.strip().astype(bool)]
#                 )
#                 self._loaded_paths = set(paths.tolist())
#             except Exception as e:
#                 self.logger.warning(f"Failed to load manifest '{self.manifest_path}': {e}")
#                 self._loaded_paths = set()
#
#             return self._loaded_paths
#
#     def record(self, full_path: str) -> None:
#         """
#         Register a missing file path.
#         """
#         if not full_path or not isinstance(full_path, str):
#             return
#         with self._lock:
#             self._new_records.append({"path": full_path})
#
#     def save(self) -> None:
#         """
#         Merge new records into the manifest and write it out atomically.
#         """
#         with self._lock:
#             # Build DataFrame of new entries
#             new_df = pd.DataFrame(self._new_records)
#             should_overwrite = self.clear_existing or not self._safe_exists(self.manifest_path)
#             if new_df.empty and not should_overwrite:
#                 return
#
#             # Clean new_df
#             new_df = (
#                 new_df.get("path", pd.Series(dtype=str))
#                       .dropna().astype(str)
#                       .loc[lambda s: s.str.strip().astype(bool)]
#                       .to_frame()
#             )
#
#             # Merge or overwrite
#             if should_overwrite:
#                 out_df = new_df
#             else:
#                 try:
#                     old_df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
#                     old_paths = (
#                         old_df.get("path", pd.Series(dtype=str))
#                               .dropna().astype(str)
#                               .loc[lambda s: s.str.strip().astype(bool)]
#                               .to_frame()
#                     )
#                     out_df = pd.concat([old_paths, new_df], ignore_index=True)
#                 except Exception as e:
#                     self.logger.warning(f"Could not merge manifest, overwriting: {e}")
#                     out_df = new_df
#
#             out_df = out_df.drop_duplicates(subset=["path"]).reset_index(drop=True)
#
#             # Ensure parent dir
#             parent = self.manifest_path.rsplit("/", 1)[0]
#             try:
#                 self.fs.makedirs(parent, exist_ok=True)
#             except Exception as e:
#                 self.logger.warning(f"Could not create manifest directory '{parent}': {e}")
#
#             # Write atomically: temp file + rename
#             temp_path = f"{self.manifest_path}.tmp-{uuid.uuid4().hex}"
#             try:
#                 out_df.to_parquet(
#                     temp_path,
#                     filesystem=self.fs,
#                     index=False
#                 )
#                 # rename into place (atomic in most filesystems)
#                 #self.fs.mv(temp_path, self.manifest_path, recursive=False)
#                 try:
#                     self.fs.copy(temp_path, self.manifest_path)
#                     self.fs.rm(temp_path)
#                 except Exception as e:
#                     self.logger.error(f"Failed to copy or delete manifest: {e}")
#                     raise
#             except Exception as e:
#                 self.logger.error(f"Failed to write or rename manifest: {e}")
#                 # Clean up temp if it exists
#                 try:
#                     if self.fs.exists(temp_path):
#                         self.fs.rm(temp_path, recursive=True)
#                 except Exception:
#                     pass
#                 raise
#
#             # Reset memory & cache
#             self._new_records.clear()
#             self._loaded_paths = set(out_df["path"].tolist())
# import pandas as pd
# import fsspec
# import threading
# import uuid
# from typing import List, Optional, Set, Dict, Any
#
# from sibi_dst.utils import Logger
#
#
# class MissingManifestManager:
#     """
#     Thread-safe manager for a “missing-partitions” manifest (Parquet file).
#     """
#
#     def __init__(
#         self,
#         fs: fsspec.AbstractFileSystem,
#         manifest_path: str,
#         clear_existing: bool = False,
#         **kwargs: Any,
#     ):
#         self.fs = fs
#         self.manifest_path = manifest_path.rstrip("/")
#         self.clear_existing = clear_existing
#
#         self.debug: bool = kwargs.get("debug", False)
#         self.logger = kwargs.get(
#             "logger",
#             Logger.default_logger(logger_name="missing_manifest_manager")
#         )
#         self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
#
#         # In-memory list for new paths
#         self._new_records: List[Dict[str, str]] = []
#         # Cached set of existing paths
#         self._loaded_paths: Optional[Set[str]] = None
#
#         # Use a reentrant lock so save() can call load_existing() safely
#         self._lock = threading.RLock()
#
#     def _safe_exists(self, path: str) -> bool:
#         try:
#             return self.fs.exists(path)
#         except PermissionError:
#             if self.debug:
#                 self.logger.debug(f"Permission denied checking existence of '{path}'")
#             return False
#         except Exception as e:
#             self.logger.warning(f"Error checking existence of '{path}': {e}")
#             return False
#
#     def load_existing(self) -> Set[str]:
#         """
#         Load and cache existing manifest paths.
#         """
#         with self._lock:
#             if self._loaded_paths is not None:
#                 return self._loaded_paths
#
#             if not self._safe_exists(self.manifest_path):
#                 self._loaded_paths = set()
#                 return self._loaded_paths
#
#             try:
#                 df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
#                 paths = (
#                     df.get("path", pd.Series(dtype=str))
#                       .dropna().astype(str)
#                       .loc[lambda s: s.str.strip().astype(bool)]
#                 )
#                 self._loaded_paths = set(paths.tolist())
#             except Exception as e:
#                 self.logger.warning(f"Failed to load manifest '{self.manifest_path}': {e}")
#                 self._loaded_paths = set()
#
#             return self._loaded_paths
#
#     def record(self, full_path: str) -> None:
#         """
#         Register a missing file path.
#         """
#         if not full_path or not isinstance(full_path, str):
#             return
#         with self._lock:
#             self._new_records.append({"path": full_path})
#
#     def save(self) -> None:
#         """
#         Merge new records into the manifest and write it out atomically.
#         """
#         with self._lock:
#             # Build DataFrame of new entries
#             new_df = pd.DataFrame(self._new_records)
#             should_overwrite = self.clear_existing or not self._safe_exists(self.manifest_path)
#             if new_df.empty and not should_overwrite:
#                 return
#
#             # Clean new_df
#             new_df = (
#                 new_df.get("path", pd.Series(dtype=str))
#                       .dropna().astype(str)
#                       .loc[lambda s: s.str.strip().astype(bool)]
#                       .to_frame()
#             )
#
#             # Merge or overwrite
#             if should_overwrite:
#                 out_df = new_df
#             else:
#                 try:
#                     old_df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
#                     old_paths = (
#                         old_df.get("path", pd.Series(dtype=str))
#                               .dropna().astype(str)
#                               .loc[lambda s: s.str.strip().astype(bool)]
#                               .to_frame()
#                     )
#                     out_df = pd.concat([old_paths, new_df], ignore_index=True)
#                 except Exception as e:
#                     self.logger.warning(f"Could not merge manifest, overwriting: {e}")
#                     out_df = new_df
#
#             out_df = out_df.drop_duplicates(subset=["path"]).reset_index(drop=True)
#
#             # Ensure parent dir
#             parent = self.manifest_path.rsplit("/", 1)[0]
#             try:
#                 self.fs.makedirs(parent, exist_ok=True)
#             except Exception as e:
#                 self.logger.warning(f"Could not create manifest directory '{parent}': {e}")
#
#             # Write atomically: temp file + rename
#             temp_path = f"{self.manifest_path}.tmp-{uuid.uuid4().hex}"
#             try:
#                 out_df.to_parquet(
#                     temp_path,
#                     filesystem=self.fs,
#                     index=False
#                 )
#                 # rename into place (atomic in most filesystems)
#                 self.fs.mv(temp_path, self.manifest_path, recursive=False)
#             except Exception as e:
#                 self.logger.error(f"Failed to write or rename manifest: {e}")
#                 # Clean up temp if it exists
#                 try:
#                     if self.fs.exists(temp_path):
#                         self.fs.rm(temp_path, recursive=True)
#                 except Exception:
#                     pass
#                 raise
#
#             # Reset memory & cache
#             self._new_records.clear()
#             self._loaded_paths = set(out_df["path"].tolist())