"""Type definitions for the FileZen Python SDK."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# File types
class FileType(str, Enum):
    FILE = "file"
    FOLDER = "folder"


class FileState(str, Enum):
    DELETING = "deleting"
    UPLOADING = "uploading"
    COMPLETED = "completed"


# API types
ZenMetadata = Dict[str, Any]

# Upload types
ZenUploadSource = Union[bytes, str]


@dataclass
class ZenUploaderParams:
    """Parameters for file upload operations."""

    name: str
    size: Optional[int] = None
    mime_type: Optional[str] = None
    metadata: Optional[ZenMetadata] = None
    folder_id: Optional[str] = None
    project_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenUploaderParams":
        """Create from dictionary."""
        # Handle both camelCase (API) and snake_case (Python) parameter names
        converted_data = {}
        for key, value in data.items():
            if key == "mimeType":
                converted_data["mime_type"] = value
            elif key == "folderId":
                converted_data["folder_id"] = value
            elif key == "projectId":
                converted_data["project_id"] = value
            else:
                converted_data[key] = value
        return cls(**converted_data)


@dataclass
class ZenStorageUploadOptions:
    """Options for storage uploads."""

    name: Optional[str] = None
    folder: Optional[str] = None
    folder_id: Optional[str] = None
    project_id: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[ZenMetadata] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenStorageUploadOptions":
        """Create from dictionary."""
        # Handle both camelCase (API) and snake_case (Python) parameter names
        converted_data = {}
        for key, value in data.items():
            if key == "mimeType":
                converted_data["mime_type"] = value
            elif key == "folderId":
                converted_data["folder_id"] = value
            elif key == "projectId":
                converted_data["project_id"] = value
            else:
                converted_data[key] = value
        return cls(**converted_data)


@dataclass
class ZenStorageBulkItem:
    """Bulk upload item."""

    source: ZenUploadSource
    options: Optional[ZenStorageUploadOptions] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenStorageBulkItem":
        """Create from dictionary."""
        options = None
        if "options" in data and data["options"]:
            if isinstance(data["options"], dict):
                options = ZenStorageUploadOptions.from_dict(data["options"])
            else:
                options = data["options"]
        return cls(source=data["source"], options=options)


# Multipart types
class UploadMode(str, Enum):
    CHUNKED = "chunked"  # Known file size, sequential chunks
    STREAMING = "streaming"  # Unknown file size, any order chunks


@dataclass
class StartMultipartUploadParams:
    """Parameters for starting multipart upload."""

    file_name: str
    mime_type: str
    total_size: Optional[int] = None
    chunk_size: Optional[int] = None
    metadata: Optional[ZenMetadata] = None
    upload_mode: Optional[UploadMode] = None
    parent_id: Optional[str] = None
    project_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StartMultipartUploadParams":
        """Create from dictionary."""
        upload_mode = None
        if "uploadMode" in data and data["uploadMode"]:
            upload_mode = UploadMode(data["uploadMode"])
        return cls(
            file_name=data["fileName"],
            mime_type=data["mimeType"],
            total_size=data.get("totalSize"),
            chunk_size=data.get("chunkSize"),
            metadata=data.get("metadata"),
            upload_mode=upload_mode,
            parent_id=data.get("parentId"),
            project_id=data.get("projectId"),
        )


@dataclass
class MultipartUploadChunkParams:
    """Parameters for uploading a multipart chunk."""

    session_id: str
    chunk: bytes
    chunk_index: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultipartUploadChunkParams":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MultipartChunkUploadResult:
    """Result of chunk upload."""

    is_complete: bool
    file: Optional["ZenFile"] = None
    next_chunk_index: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultipartChunkUploadResult":
        """Create from dictionary."""
        file = None
        if "file" in data and data["file"]:
            file = ZenFile.from_dict(data["file"])
        return cls(
            is_complete=data.get("isComplete", False),
            file=file,
            next_chunk_index=data.get("nextChunkIndex"),
        )


@dataclass
class FinishMultipartUploadParams:
    """Parameters for finishing multipart upload."""

    session_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinishMultipartUploadParams":
        """Create from dictionary."""
        return cls(**data)


# API response data types
@dataclass
class ZenProjectData:
    """Raw project data from API response."""

    id: str
    created_at: str
    updated_at: str
    name: str
    organisation_id: str
    region: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenProjectData":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            name=data.get("name", ""),
            organisation_id=data.get("organisationId", ""),
            region=data.get("region", ""),
        )


@dataclass
class ZenFileData:
    """Raw file data from API response."""

    id: str
    created_at: str
    updated_at: str
    type: str
    state: str
    name: str
    mime_type: str
    size: int
    region: str
    url: Optional[str] = None
    project_id: str = ""
    project: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    parent: Optional[Dict[str, Any]] = None
    metadata: Optional[ZenMetadata] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenFileData":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            type=data.get("type", "file"),
            state=data.get("state", "completed"),
            name=data.get("name", ""),
            mime_type=data.get("mimeType", ""),
            size=data.get("size", 0),
            region=data.get("region", ""),
            url=data.get("url"),
            project_id=data.get("projectId", ""),
            project=data.get("project"),
            parent_id=data.get("parentId"),
            parent=data.get("parent"),
            metadata=data.get("metadata"),
        )


@dataclass
class ZenProject:
    """Represents a project in FileZen."""

    id: str
    created_at: str
    updated_at: str
    name: str
    organisation_id: str
    region: str

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], ZenProjectData]) -> "ZenProject":
        """Create from dictionary or ZenProjectData."""
        if isinstance(data, ZenProjectData):
            return cls(
                id=data.id,
                created_at=data.created_at,
                updated_at=data.updated_at,
                name=data.name,
                organisation_id=data.organisation_id,
                region=data.region,
            )
        else:
            raw_data = ZenProjectData.from_dict(data)
            return cls.from_dict(raw_data)


@dataclass
class ZenFile:
    """Represents a file in FileZen."""

    id: str
    created_at: str
    updated_at: str
    type: FileType
    state: FileState
    name: str
    mime_type: str
    size: int
    region: str
    url: Optional[str] = None
    project_id: str = ""
    project: Optional[ZenProject] = None
    parent_id: Optional[str] = None
    parent: Optional["ZenFile"] = None
    metadata: Optional[ZenMetadata] = None

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], ZenFileData]) -> "ZenFile":
        """Create from dictionary or ZenFileData."""
        if isinstance(data, ZenFileData):
            raw_data = data
        else:
            raw_data = ZenFileData.from_dict(data)

        project = None
        if raw_data.project:
            project = ZenProject.from_dict(raw_data.project)

        parent = None
        if raw_data.parent:
            parent = ZenFile.from_dict(raw_data.parent)

        return cls(
            id=raw_data.id,
            created_at=raw_data.created_at,
            updated_at=raw_data.updated_at,
            type=FileType(raw_data.type),
            state=FileState(raw_data.state),
            name=raw_data.name,
            mime_type=raw_data.mime_type,
            size=raw_data.size,
            region=raw_data.region,
            url=raw_data.url,
            project_id=raw_data.project_id,
            project=project,
            parent_id=raw_data.parent_id,
            parent=parent,
            metadata=raw_data.metadata,
        )


@dataclass
class ZenList:
    """Represents a list of files."""

    data: List[ZenFile]
    page: int
    page_count: int
    count: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenList":
        """Create from dictionary."""
        return cls(
            data=[ZenFile.from_dict(item) for item in data.get("data", [])],
            page=data.get("page", 0),
            page_count=data.get("pageCount", 0),
            count=data.get("count", 0),
            total=data.get("total", 0),
        )


# API response types
@dataclass
class ZenApiResponse:
    """Base API response."""

    data: Union[Dict[str, Any], List[Any], str, int, float, bool, None]
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenApiResponse":
        """Create from dictionary."""
        return cls(data=data.get("data"), error=data.get("error"))


@dataclass
class ZenUploadResponse(ZenApiResponse):
    """Upload response."""

    file: Optional[ZenFile] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenUploadResponse":
        """Create from dictionary."""
        response = super().from_dict(data)
        file = None
        if response.data and isinstance(response.data, dict):
            file = ZenFile.from_dict(response.data)
        return cls(data=response.data, error=response.error, file=file)


@dataclass
class ZenMultipartInitResponse(ZenApiResponse):
    """Multipart initialization response."""

    id: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenMultipartInitResponse":
        """Create from dictionary."""
        response = super().from_dict(data)
        id_value = ""
        if response.data and isinstance(response.data, dict):
            id_value = response.data.get("id", "")
        return cls(data=response.data, error=response.error, id=id_value)


@dataclass
class ZenMultipartChunkResponse(ZenApiResponse):
    """Multipart chunk response."""

    is_complete: bool = False
    file: Optional[ZenFile] = None
    next_chunk_index: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZenMultipartChunkResponse":
        """Create from dictionary."""
        response = super().from_dict(data)
        is_complete = False
        file = None
        next_chunk_index = None

        if response.data and isinstance(response.data, dict):
            is_complete = response.data.get("isComplete", False)
            if "file" in response.data and response.data["file"]:
                file = ZenFile.from_dict(response.data["file"])
            next_chunk_index = response.data.get("nextChunkIndex")

        return cls(
            data=response.data,
            error=response.error,
            is_complete=is_complete,
            file=file,
            next_chunk_index=next_chunk_index,
        )


# Helper function to convert dict to dataclass
def to_dataclass(cls: type, data: Union[Dict[str, Any], Any]) -> Any:
    """Convert dict to dataclass instance if needed."""
    if isinstance(data, dict) and hasattr(cls, "from_dict"):
        return cls.from_dict(data)
    return data
