"""API communication for the FileZen Python SDK."""

import os
from typing import Any, Dict, Optional, Union, cast

import httpx

from .constants import DEFAULT_API_URL
from .types import (
    StartMultipartUploadParams,
    ZenFile,
    ZenList,
    ZenMetadata,
    ZenMultipartChunkResponse,
    ZenMultipartInitResponse,
    ZenUploaderParams,
    ZenUploadResponse,
    to_dataclass,
)
from .zen_error import ZenError, build_zen_error


class ZenApi:
    """Handles API communication with FileZen."""

    def __init__(
        self, *, api_key: Optional[str] = None, api_url: Optional[str] = None
    ) -> None:
        """Initialize ZenApi.

        Args:
            api_key: FileZen API key. If not provided, will use FILEZEN_API_KEY environment variable.
            api_url: Custom API URL. Defaults to https://api.filezen.dev
        """
        # Get API key from parameter or environment
        self.api_key = (
            api_key
            or os.getenv("FILEZEN_API_KEY")
            or os.getenv("REACT_APP_FILEZEN_API_KEY")
            or os.getenv("NEXT_PUBLIC_FILEZEN_API_KEY")
        )

        if not self.api_key:
            raise ZenError(
                "No API key provided. Set FILEZEN_API_KEY environment variable or pass api_key parameter.",
                code="AUTH_ERROR",
            )

        # Get API URL with fallback
        self.api_url = api_url or DEFAULT_API_URL

        # Ensure we have a valid API URL
        if not self.api_url:
            raise ValueError("No API URL provided and DEFAULT_API_URL is not set")

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "ApiKey": self.api_key,
            },
            timeout=httpx.Timeout(
                connect=30.0,  # Connection timeout
                read=300.0,  # Read timeout (5 minutes for large files)
                write=300.0,  # Write timeout (5 minutes for large files)
                pool=30.0,  # Pool timeout
            ),
        )

    def set_authorization(self, authorization: Optional[str] = None) -> None:
        """Set authorization header.

        Args:
            authorization: Authorization header value
        """
        if authorization:
            self.client.headers["Authorization"] = authorization
        else:
            self.client.headers.pop("Authorization", None)

    async def upload_file(
        self, source: bytes, params: Union[Dict[str, Any], ZenUploaderParams]
    ) -> ZenUploadResponse:
        """Upload a file to FileZen.

        Args:
            source: File content as bytes
            params: Upload parameters as dict or ZenUploaderParams

        Returns:
            Upload result
        """
        # Convert dict to dataclass if needed
        params = to_dataclass(ZenUploaderParams, params)
        params = cast(ZenUploaderParams, params)

        try:
            # Prepare multipart form data
            files = {
                "file": (
                    params.name,
                    source,
                    params.mime_type or "application/octet-stream",
                )
            }

            # Additional form data
            data = {}
            if params.mime_type:
                data["mimeType"] = params.mime_type
            if params.metadata:
                # Serialize metadata to JSON string for form data
                import json

                data["metadata"] = json.dumps(params.metadata)
            if params.project_id:
                data["projectId"] = params.project_id
            if params.folder_id:
                data["folderId"] = params.folder_id

            response = await self.client.post("/files/upload", files=files, data=data)
            response.raise_for_status()

            return ZenUploadResponse.from_dict({"data": response.json()})

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def initialize_multipart_upload(
        self, params: Union[Dict[str, Any], StartMultipartUploadParams]
    ) -> ZenMultipartInitResponse:
        """Initialize a multipart upload.

        Args:
            params: Multipart upload parameters as dict or StartMultipartUploadParams

        Returns:
            Multipart upload initialization result
        """
        # Convert dict to dataclass if needed
        params = to_dataclass(StartMultipartUploadParams, params)
        params = cast(StartMultipartUploadParams, params)

        try:
            # Convert dataclass to dict for API
            api_params = {
                "fileName": params.file_name,
                "mimeType": params.mime_type,
            }
            if params.total_size is not None:
                api_params["totalSize"] = str(params.total_size)
            if params.chunk_size is not None:
                api_params["chunkSize"] = str(params.chunk_size)
            if params.metadata is not None:
                import json

                api_params["metadata"] = json.dumps(params.metadata)
            if params.upload_mode is not None:
                api_params["uploadMode"] = params.upload_mode.value
            if params.parent_id is not None:
                api_params["parentId"] = params.parent_id
            if params.project_id is not None:
                api_params["projectId"] = params.project_id

            response = await self.client.post(
                "/files/chunk-upload/initialize", json=api_params
            )
            response.raise_for_status()

            return ZenMultipartInitResponse.from_dict({"data": response.json()})

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def upload_chunk(
        self, session_id: str, chunk: bytes, chunk_index: int, chunk_size: int
    ) -> ZenMultipartChunkResponse:
        """Upload a chunk in multipart upload.

        Args:
            session_id: Multipart upload session ID
            chunk: Chunk data
            chunk_index: Index of the chunk
            chunk_size: Size of the chunk

        Returns:
            Chunk upload result
        """
        try:
            files = {
                "chunk": (f"chunk_{chunk_index}", chunk, "application/octet-stream")
            }
            headers = {
                "Chunk-Session-Id": session_id,
                "Chunk-Size": str(chunk_size),
                "Chunk-Index": str(chunk_index),
            }

            response = await self.client.post(
                "/files/chunk-upload/part", files=files, headers=headers
            )
            response.raise_for_status()

            return ZenMultipartChunkResponse.from_dict({"data": response.json()})

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def finish_multipart_upload(self, session_id: str) -> ZenFile:
        """Finish a multipart upload session.

        Args:
            session_id: Multipart upload session ID

        Returns:
            Finish result with file information
        """
        try:
            response = await self.client.post(
                f"/files/chunk-upload/finish/{session_id}"
            )
            response.raise_for_status()

            return ZenFile.from_dict(response.json())

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def delete_file_by_url(self, url: str) -> bool:
        """Delete a file by URL.

        Args:
            url: File URL to delete

        Returns:
            Delete result
        """
        try:
            response = await self.client.delete(
                "/files/delete-by-url", params={"url": url}
            )
            response.raise_for_status()

            return True

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def list_files(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> ZenList:
        """List files.

        Args:
            limit: Number of files to return (default: 20)
            offset: Number of files to skip (default: 0)

        Returns:
            List of files
        """
        try:
            params = {
                "limit": limit or 20,
                "offset": offset or 0,
            }
            response = await self.client.get("/files", params=params)
            response.raise_for_status()

            return ZenList.from_dict(response.json())

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def file_info(self, file_id: str) -> ZenFile:
        """Get file information.

        Args:
            file_id: File ID

        Returns:
            File information
        """
        try:
            response = await self.client.get(f"/files/{file_id}")
            response.raise_for_status()

            return ZenFile.from_dict(response.json())

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def update_file(
        self,
        file_id: str,
        params: Dict[str, Union[str, int, float, bool, None, ZenMetadata]],
    ) -> ZenFile:
        """Update file information.

        Args:
            file_id: File ID
            params: Update parameters

        Returns:
            Updated file information
        """
        try:
            response = await self.client.patch(f"/files/{file_id}", json=params)
            response.raise_for_status()

            return ZenFile.from_dict(response.json())

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID.

        Args:
            file_id: File ID to delete

        Returns:
            True if successful
        """
        try:
            response = await self.client.delete(f"/files/{file_id}")
            response.raise_for_status()

            return True

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise build_zen_error(e) from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "ZenApi":
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
