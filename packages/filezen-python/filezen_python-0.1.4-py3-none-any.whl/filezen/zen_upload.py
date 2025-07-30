"""Upload functionality for the FileZen Python SDK."""

import base64
import re
from typing import Optional, Union

from .constants import MULTIPART_CHUNK_SIZE, MULTIPART_THRESHOLD
from .types import ZenFile, ZenMetadata
from .utils import generate_local_id, is_base64, is_url
from .zen_api import ZenApi
from .zen_error import ZenError, ZenUploadError, build_zen_error

# Type alias for upload sources
ZenUploadSource = Union[bytes, str]


class ZenUpload:
    """Represents a file upload operation."""

    def __init__(
        self,
        name: str,
        mime_type: str,
        api: ZenApi,
        source: ZenUploadSource,
        folder: Optional[str] = None,
        metadata: Optional[ZenMetadata] = None,
        project_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ):
        # Upload configuration
        self.local_id = generate_local_id()
        self.name = name
        self.mime_type = mime_type
        self.folder = folder
        self.metadata = metadata
        self.project_id = project_id
        self.folder_id = folder_id

        # Upload state (default values)
        self.file: Optional[ZenFile] = None
        self.error: Optional[ZenError] = None
        self.is_completed: bool = False
        self.is_cancelled: bool = False

        # Internal state
        self.api = api
        self.source = source

    async def upload(self) -> "ZenUpload":
        """Perform the upload operation.

        Returns:
            Self with updated file information
        """
        if self.api is None:
            raise ZenUploadError("Upload not properly initialized: api is None")
        if self.source is None:
            raise ZenUploadError("Upload not properly initialized: source is None")

        try:
            # Handle different source types
            if isinstance(self.source, str):
                # String sources - route to appropriate handlers
                if is_url(self.source):
                    await self._url_upload()
                elif is_base64(self.source):
                    await self._base64_upload()
                else:
                    await self._text_upload()
            else:
                # Bytes source - route to bytes handler
                await self._upload_from_bytes(self.source)

            self.is_completed = True

        except Exception as e:
            if isinstance(e, ZenError):
                self.error = e
            else:
                self.error = ZenUploadError(str(e))
            raise

        return self

    async def _upload_from_bytes(self, source: bytes) -> None:
        """Handle bytes sources - decide between single vs multipart upload."""
        # For small files, use single upload
        if len(source) <= MULTIPART_THRESHOLD:
            await self._single_upload_from_bytes(source)
        else:
            await self._multipart_upload_from_bytes(source)

    async def _single_upload_from_bytes(self, source: bytes) -> None:
        """Perform a single upload for small bytes sources."""
        assert self.api is not None

        result = await self.api.upload_file(
            source,
            {
                "name": self.name,
                "mimeType": self.mime_type or "application/octet-stream",
                "metadata": self.metadata,
                "projectId": self.project_id,
                "folderId": self.folder_id,
            },
        )

        if result.error:
            raise ZenUploadError(result.error.get("message", "Upload failed"))

        # Use the API response directly - it should already match ZenFile structure
        self.file = result.file

    async def _multipart_upload_from_bytes(self, source: bytes) -> None:
        """Perform a multipart upload for large bytes sources."""
        assert self.api is not None

        file_size = len(source)
        # Initialize multipart upload
        init_result = await self.api.initialize_multipart_upload(
            {
                "fileName": self.name,
                "mimeType": self.mime_type or "application/octet-stream",
                "totalSize": file_size,
                "chunkSize": MULTIPART_CHUNK_SIZE,
                "metadata": self.metadata,
                "projectId": self.project_id,
                "parentId": self.folder_id,
            }
        )

        if init_result.error:
            raise ZenUploadError(
                init_result.error.get(
                    "message", "Multipart upload initialization failed"
                )
            )

        session_id = init_result.id
        total_chunks = (file_size + MULTIPART_CHUNK_SIZE - 1) // MULTIPART_CHUNK_SIZE
        current_chunk_index = 0

        while current_chunk_index < total_chunks:
            # Calculate chunk boundaries
            start = current_chunk_index * MULTIPART_CHUNK_SIZE
            end = min(start + MULTIPART_CHUNK_SIZE, file_size)
            chunk = source[start:end]
            chunk_size = len(chunk)

            # Upload chunk
            chunk_result = await self.api.upload_chunk(
                session_id, chunk, current_chunk_index, chunk_size
            )

            if chunk_result.error:
                raise ZenUploadError(
                    chunk_result.error.get(
                        "message", f"Chunk {current_chunk_index} upload failed"
                    )
                )

            # Check if upload is complete
            if chunk_result.is_complete:
                if chunk_result.file:
                    self.file = chunk_result.file
                break

            # Move to next chunk
            current_chunk_index = (
                chunk_result.next_chunk_index or current_chunk_index + 1
            )

        if not self.file:
            raise ZenUploadError("Multipart upload did not complete as expected")

    async def _url_upload(self) -> None:
        """Perform upload from URL string source using streaming."""
        assert self.api is not None
        assert self.source is not None
        assert isinstance(self.source, str)

        # For URLs, we'll use streaming multipart upload since we don't know the size
        session_result = await self.api.initialize_multipart_upload(
            {
                "fileName": self.name,
                "mimeType": self.mime_type or "application/octet-stream",
                "uploadMode": "streaming",
                "metadata": self.metadata,
                "projectId": self.project_id,
                "parentId": self.folder_id,
            }
        )

        if session_result.error:
            raise build_zen_error(session_result.error)

        session_id = session_result.id

        # Stream from URL - fetch and upload chunks as they arrive
        async with self.api.client.stream("GET", self.source) as response:
            response.raise_for_status()

            # Stream file content in chunks and upload immediately
            async for chunk in response.aiter_bytes(MULTIPART_CHUNK_SIZE):
                if chunk:
                    # Upload chunk immediately without storing chunk_index
                    chunk_result = await self.api.upload_chunk(
                        session_id, chunk, 0, len(chunk)
                    )
                    if chunk_result.error:
                        raise build_zen_error(chunk_result.error)

                    if chunk_result.is_complete:
                        self.file = chunk_result.file
                        return

        # Finish multipart upload for streaming mode
        finish_result = await self.api.finish_multipart_upload(session_id)
        self.file = finish_result

    async def _base64_upload(self) -> None:
        """Perform upload from base64 string source."""
        assert self.api is not None
        assert self.source is not None
        assert isinstance(self.source, str)

        params = {
            "name": self.name,
            "mimeType": self.mime_type or "application/octet-stream",
            "metadata": self.metadata,
            "projectId": self.project_id,
            "folderId": self.folder_id,
        }

        try:
            # Handle data URL format
            if self.source.startswith("data:"):
                header, data = self.source.split(",", 1)
                # Extract MIME type from data URL
                mime_match = re.search(r"data:([^;]+)", header)
                if mime_match and not params.get("mimeType"):
                    params["mimeType"] = mime_match.group(1)
            else:
                data = self.source

            # Decode base64
            file_bytes = base64.b64decode(data)

            # Upload the decoded bytes
            result = await self.api.upload_file(file_bytes, params)

        except Exception as e:
            raise ZenUploadError(f"Failed to decode base64: {str(e)}") from e

        if result.error:
            raise ZenUploadError(result.error.get("message", "Base64 upload failed"))

        self.file = result.file

    async def _text_upload(self) -> None:
        """Perform upload from text string source."""
        assert self.api is not None
        assert self.source is not None
        assert isinstance(self.source, str)

        params = {
            "name": self.name,
            "mimeType": self.mime_type
            or "text/plain",  # Default to text/plain for text uploads
            "metadata": self.metadata,
            "projectId": self.project_id,
            "folderId": self.folder_id,
        }

        # Convert text to bytes
        file_bytes = self.source.encode("utf-8")

        # Upload the text as bytes
        result = await self.api.upload_file(file_bytes, params)

        if result.error:
            raise ZenUploadError(result.error.get("message", "Text upload failed"))

        self.file = result.file

    def cancel(self) -> None:
        """Cancel the upload operation."""
        self.is_cancelled = True
