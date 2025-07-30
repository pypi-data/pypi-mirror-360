"""Main storage class for the FileZen Python SDK."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, cast

from .types import (
    FinishMultipartUploadParams,
    MultipartChunkUploadResult,
    MultipartUploadChunkParams,
    StartMultipartUploadParams,
    ZenFile,
    ZenStorageBulkItem,
    ZenStorageUploadOptions,
    ZenUploadSource,
    to_dataclass,
)
from .zen_api import ZenApi
from .zen_error import ZenError
from .zen_upload import ZenUpload


@dataclass
class ZenProgress:
    """Progress information for uploads."""

    bytes: Optional[int] = None
    total: Optional[int] = None
    percent: Optional[float] = None


class ZenUploadListener:
    """Listener interface for upload and storage events."""

    def on_upload_start(self, upload: ZenUpload) -> None:
        """Called when upload starts."""
        pass

    def on_upload_progress(self, upload: ZenUpload, progress: ZenProgress) -> None:
        """Called on upload progress."""
        pass

    def on_upload_complete(self, upload: ZenUpload) -> None:
        """Called when upload completes."""
        pass

    def on_upload_error(self, upload: ZenUpload, error: ZenError) -> None:
        """Called on upload error."""
        pass

    def on_upload_cancel(self, upload: ZenUpload) -> None:
        """Called when upload is cancelled."""
        pass

    def on_uploads_change(self, uploads: List[ZenUpload]) -> None:
        """Called when the uploads list changes."""
        pass


class ZenMultipartControl:
    """Manual multipart upload control."""

    def __init__(self, api: ZenApi):
        self.api = api

    async def start(
        self,
        params: Union[StartMultipartUploadParams, Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Start a multipart upload session.

        Args:
            params: Parameters as StartMultipartUploadParams or dict
            **kwargs: Parameters as keyword arguments (file_name, mime_type, etc.)
        """
        # Handle different parameter formats
        if params is None and kwargs:
            api_params = {
                "fileName": kwargs["file_name"],
                "mimeType": kwargs["mime_type"],
            }
            for key, api_key in [
                ("total_size", "totalSize"),
                ("chunk_size", "chunkSize"),
                ("metadata", "metadata"),
                ("upload_mode", "uploadMode"),
                ("parent_id", "parentId"),
                ("project_id", "projectId"),
            ]:
                if key in kwargs:
                    api_params[api_key] = kwargs[key]
        elif isinstance(params, dict):
            api_params = {
                "fileName": params["file_name"],
                "mimeType": params["mime_type"],
            }
            for key, api_key in [
                ("total_size", "totalSize"),
                ("chunk_size", "chunkSize"),
                ("metadata", "metadata"),
                ("upload_mode", "uploadMode"),
                ("parent_id", "parentId"),
                ("project_id", "projectId"),
            ]:
                if key in params:
                    api_params[api_key] = params[key]
        else:
            # StartMultipartUploadParams object
            api_params = {
                "fileName": params.file_name,
                "mimeType": params.mime_type,
            }

            if params.total_size is not None:
                api_params["totalSize"] = params.total_size
            if params.chunk_size is not None:
                api_params["chunkSize"] = params.chunk_size
            if params.metadata is not None:
                api_params["metadata"] = params.metadata
            if params.upload_mode is not None:
                api_params["uploadMode"] = params.upload_mode.value
            if params.parent_id is not None:
                api_params["parentId"] = params.parent_id
            if params.project_id is not None:
                api_params["projectId"] = params.project_id

        result = await self.api.initialize_multipart_upload(api_params)

        if result.error:
            raise ZenError(
                result.error.get("message", "Failed to start multipart upload")
            )

        return {"id": result.id}

    async def upload_part(
        self,
        params: Union[MultipartUploadChunkParams, Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MultipartChunkUploadResult:
        """Upload a part of the multipart upload.

        Args:
            params: Parameters as MultipartUploadChunkParams or dict
            **kwargs: Parameters as keyword arguments (session_id, chunk, etc.)
        """
        # Handle different parameter formats
        if params is None and kwargs:
            session_id = kwargs["session_id"]
            chunk = kwargs["chunk"]
            chunk_index = kwargs.get("chunk_index", 0)
        elif isinstance(params, dict):
            session_id = params["session_id"]
            chunk = params["chunk"]
            chunk_index = params.get("chunk_index", 0)
        else:
            # MultipartUploadChunkParams object
            session_id = params.session_id
            chunk = params.chunk
            chunk_index = params.chunk_index or 0

        result = await self.api.upload_chunk(session_id, chunk, chunk_index, len(chunk))

        if result.error:
            raise ZenError(result.error.get("message", "Failed to upload chunk"))

        return MultipartChunkUploadResult(
            is_complete=result.is_complete,
            file=result.file,
            next_chunk_index=result.next_chunk_index,
        )

    async def finish(
        self,
        params: Union[FinishMultipartUploadParams, Dict[str, Any], str] = None,
        **kwargs: Any,
    ) -> ZenFile:
        """Finish the multipart upload.

        Args:
            params: Parameters as FinishMultipartUploadParams, dict, or session_id string
            **kwargs: Parameters as keyword arguments (session_id)
        """
        # Handle different parameter formats
        if params is None and kwargs:
            session_id = kwargs["session_id"]
        elif isinstance(params, str):
            session_id = params
        elif isinstance(params, dict):
            session_id = params["session_id"]
        else:
            # FinishMultipartUploadParams object
            session_id = params.session_id

        result = await self.api.finish_multipart_upload(session_id)
        return result


class ZenStorage:
    """Storage client for FileZen with upload capabilities."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        keep_uploads: bool = False,
    ):
        """Initialize ZenStorage.

        Args:
            api_key: FileZen API key. If not provided, will use FILEZEN_API_KEY environment variable.
            api_url: Custom API URL. Defaults to https://api.filezen.dev
            keep_uploads: Whether to keep upload records in memory for tracking. Defaults to False.

        Examples:
            # ✅ RECOMMENDED: Direct parameters with full IDE support
            storage = ZenStorage(api_key="your_key", keep_uploads=True)

            # ✅ ENVIRONMENT VARIABLES: Most secure approach
            storage = ZenStorage()  # Uses FILEZEN_API_KEY env var

            # ✅ MINIMAL: Just what you need
            storage = ZenStorage(api_key="your_key")
        """
        # Initialize ZenApi with direct parameters
        self.api = ZenApi(api_key=api_key, api_url=api_url)
        self._keep_uploads = keep_uploads
        self.listeners: List[ZenUploadListener] = []
        self.uploads: Dict[str, ZenUpload] = {}

    @property
    def multipart(self) -> ZenMultipartControl:
        """Get multipart upload control."""
        return ZenMultipartControl(self.api)

    def add_listener(self, listener: ZenUploadListener) -> None:
        """Add an event listener.

        Args:
            listener: Listener to add
        """
        self.listeners.append(listener)

    def remove_listener(self, listener: ZenUploadListener) -> None:
        """Remove an event listener.

        Args:
            listener: Listener to remove
        """
        if listener in self.listeners:
            self.listeners.remove(listener)

    @property
    def get_uploads(self) -> List[ZenUpload]:
        """Get all uploads."""
        return list(self.uploads.values())

    @property
    def active_uploads(self) -> List[ZenUpload]:
        """Get active uploads."""
        return [
            upload
            for upload in self.uploads.values()
            if not upload.error and not upload.is_completed
        ]

    def _notify_listeners(self, event: str, *args: Any) -> None:
        """Notify all listeners of an event.

        Args:
            event: Event name
            args: Event arguments
        """
        for listener in self.listeners:
            callback = getattr(listener, event, None)
            if callback:
                try:
                    callback(*args)
                except Exception as e:
                    # Log error but don't break the upload process
                    print(f"Error in listener {event}: {e}")

    def build_upload(
        self,
        source: ZenUploadSource,
        options: Optional[Union[Dict[str, Any], ZenStorageUploadOptions]] = None,
    ) -> ZenUpload:
        """Build an upload object without starting it.

        Args:
            source: File source (bytes, string URL, base64, or text)
            options: Upload options as dict or ZenStorageUploadOptions

        Returns:
            ZenUpload instance ready for upload

        Examples:
            # ✅ RECOMMENDED: Using dataclass for full IDE support
            options = ZenStorageUploadOptions(
                name="my_file.txt",
                folder_id="folder123",
                metadata={"category": "documents"}
            )
            upload = storage.build_upload(file_bytes, options)

            # ✅ DICT: Also supported for flexibility
            upload = storage.build_upload(file_bytes, {
                "name": "my_file.txt",
                "folder_id": "folder123"
            })
        """
        # Convert options to dataclass if needed
        options = to_dataclass(ZenStorageUploadOptions, options)
        options = cast(ZenStorageUploadOptions, options)

        # Determine file name and MIME type
        name = options.name if options.name else "file"
        mime_type = (
            options.mime_type if options.mime_type else "application/octet-stream"
        )

        # Create upload instance
        upload = ZenUpload(
            name=name,
            mime_type=mime_type,
            api=self.api,
            source=source,
            folder=options.folder,
            metadata=options.metadata,
            project_id=options.project_id,
            folder_id=options.folder_id,
        )

        # Store upload if tracking is enabled
        if self._keep_uploads:
            self.uploads[upload.local_id] = upload
            self._notify_listeners("on_uploads_change", self.get_uploads)

        return upload

    async def upload(
        self,
        source: ZenUploadSource,
        options: Optional[Union[Dict[str, Any], ZenStorageUploadOptions]] = None,
        **kwargs: Any,
    ) -> ZenUpload:
        """Upload a file to FileZen.

        Args:
            source: File source (bytes, string URL, base64, or text)
            options: Upload options as dict or ZenStorageUploadOptions
            **kwargs: Additional options as keyword arguments

        Returns:
            ZenUpload instance with completed upload

        Examples:
            # ✅ RECOMMENDED: Using dataclass for full IDE support
            options = ZenStorageUploadOptions(
                name="my_file.txt",
                folder_id="folder123",
                metadata={"category": "documents"}
            )
            upload = await storage.upload(file_bytes, options)

            # ✅ DICT: Also supported for flexibility
            upload = await storage.upload(file_bytes, {
                "name": "my_file.txt",
                "folder_id": "folder123"
            })

            # ✅ KEYWORD ARGS: Quick and simple
            upload = await storage.upload(file_bytes, name="my_file.txt")
        """
        # Handle keyword arguments
        if kwargs and options is None:
            options = kwargs
        elif kwargs and isinstance(options, dict):
            options.update(kwargs)

        # Build and execute upload
        upload = self.build_upload(source, options)

        # Notify listeners
        self._notify_listeners("on_upload_start", upload)

        try:
            # Perform upload
            await upload.upload()

            # Notify completion
            self._notify_listeners("on_upload_complete", upload)

        except Exception as e:
            # Notify error
            self._notify_listeners("on_upload_error", upload, e)
            raise

        return upload

    async def bulk_upload(
        self, *uploads: Union[Dict[str, Any], ZenStorageBulkItem]
    ) -> List[ZenUpload]:
        """Upload multiple files in parallel.

        Args:
            *uploads: Upload items as dicts or ZenStorageBulkItem instances

        Returns:
            List of completed uploads

        Examples:
            # ✅ RECOMMENDED: Using dataclasses for full IDE support
            items = [
                ZenStorageBulkItem(
                    source=file1_bytes,
                    options=ZenStorageUploadOptions(name="file1.txt")
                ),
                ZenStorageBulkItem(
                    source=file2_bytes,
                    options=ZenStorageUploadOptions(name="file2.txt")
                )
            ]
            uploads = await storage.bulk_upload(*items)

            # ✅ DICT: Also supported for flexibility
            uploads = await storage.bulk_upload(
                {"source": file1_bytes, "options": {"name": "file1.txt"}},
                {"source": file2_bytes, "options": {"name": "file2.txt"}}
            )
        """
        # Convert dicts to dataclasses if needed
        bulk_items = []
        for item in uploads:
            if isinstance(item, dict):
                bulk_items.append(ZenStorageBulkItem.from_dict(item))
            else:
                bulk_items.append(item)

        # Create uploads
        upload_objects = []
        for item in bulk_items:
            upload = self.build_upload(item.source, item.options)
            upload_objects.append(upload)

        # Notify listeners
        for upload in upload_objects:
            self._notify_listeners("on_upload_start", upload)

        # Execute uploads in parallel
        import asyncio

        try:
            results = await asyncio.gather(
                *[upload.upload() for upload in upload_objects], return_exceptions=True
            )

            # Handle results
            completed_uploads = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Notify error
                    self._notify_listeners("on_upload_error", upload_objects[i], result)
                    raise result
                else:
                    # Notify completion
                    self._notify_listeners("on_upload_complete", result)
                    completed_uploads.append(result)

            # Filter out exceptions from the result list for correct return type
            return [u for u in completed_uploads if isinstance(u, ZenUpload)]

        except Exception as e:
            # Notify errors for all uploads
            for upload in upload_objects:
                self._notify_listeners("on_upload_error", upload, e)
            raise

    def generate_signed_url(self, options: Dict[str, Any]) -> str:
        """Generate a signed URL for direct file access.

        Args:
            options: URL generation options

        Returns:
            Signed URL string

        Note:
            This is a placeholder method. Implement based on your FileZen API.
        """
        # This would typically call the FileZen API to generate a signed URL
        # For now, return a placeholder
        return f"https://api.filezen.dev/signed-url?{options}"

    async def delete_by_url(self, url: str) -> bool:
        """Delete a file by its URL.

        Args:
            url: File URL to delete

        Returns:
            True if successful

        Examples:
            # Delete a file by URL
            success = await storage.delete_by_url("https://api.filezen.dev/files/123")
        """
        return await self.api.delete_file_by_url(url)

    async def close(self) -> None:
        """Close the storage client and cleanup resources."""
        await self.api.close()

    async def __aenter__(self) -> "ZenStorage":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.close()
