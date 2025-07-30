# FileZen Python SDK

A Python SDK for FileZen, providing easy-to-use file upload and management capabilities with **full IDE support** and **type safety**.

## Features

- ✅ **File Upload**: Upload single files efficiently
- ✅ **Bulk Upload**: Upload multiple files concurrently
- ✅ **URL Upload**: Upload files directly from URLs with streaming
- ✅ **Base64 Upload**: Upload from base64 encoded data
- ✅ **Text Upload**: Upload text content directly
- ✅ **Signed URLs**: Generate secure signed URLs for direct uploads
- ✅ **Multipart Upload**: Automatic multipart upload for large files (>10MB)
- ✅ **Manual Multipart Control**: Fine-grained control over multipart uploads
- ✅ **File Deletion**: Delete files by URL
- ✅ **Error Handling**: Comprehensive error handling with detailed messages
- ✅ **Progress Tracking**: Real-time upload progress monitoring
- ✅ **Full IDE Support**: Complete autocomplete and type checking
- ✅ **Flexible Parameters**: Accept both dataclasses and dictionaries
- ✅ **Backend Optimized**: Designed for server-side usage without UI dependencies

## Installation

```bash
pip install filezen-python
```

## Quick Start

### Basic Usage

```python
import asyncio
from filezen import ZenStorage, ZenStorageUploadOptions

async def main():
    # Initialize storage with full IDE support
    storage = ZenStorage(
        api_key="your_api_key_here",  # Optional: can use FILEZEN_API_KEY env var
        keep_uploads=True  # Optional: track uploads in memory
    )
    
    # ✅ RECOMMENDED: Using dataclass for full IDE support
    options = ZenStorageUploadOptions(
        name="example.txt",
        mime_type="text/plain",
        metadata={"category": "documents"}
    )
    
    # Upload a file with bytes
    with open("example.txt", "rb") as f:
        upload = await storage.upload(f.read(), options)
    
    print(f"Uploaded: {upload.file.url}")
    
    await storage.close()

asyncio.run(main())
```

## Configuration Options

The FileZen Python SDK provides a clean, simple constructor with **full IDE support**:

### Direct Parameters (Recommended)

```python
from filezen import ZenStorage

# ✅ RECOMMENDED: Direct parameters with full IDE support
storage = ZenStorage(
    api_key="your_api_key_here",
    api_url="https://api.filezen.dev",  # Optional: defaults to https://api.filezen.dev
    keep_uploads=True  # Optional: defaults to False
)
```

### Environment Variables (Most Secure)

For security, use environment variables instead of hardcoding API keys:

```bash
export FILEZEN_API_KEY=your_api_key_here
```

```python
# No API key needed - automatically uses environment variable
storage = ZenStorage()

# Or with other options
storage = ZenStorage(
    api_url="https://api.filezen.dev",  # Optional custom endpoint
    keep_uploads=True  # Optional: track uploads in memory
)
```

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `api_key` | `str` | FileZen API key | Required (or `FILEZEN_API_KEY` env var) |
| `api_url` | `str` | Custom API URL | `https://api.filezen.dev` |
| `keep_uploads` | `bool` | Keep upload records in memory | `False` |

### IDE Benefits

The constructor provides:
- ✅ **Autocomplete** for all parameters
- ✅ **Type checking** for each parameter
- ✅ **Error detection** for typos
- ✅ **Self-documenting** code
- ✅ **Clean, simple interface**

## Features

### 1. Metadata Support

```python
from filezen import ZenStorage, ZenStorageUploadOptions

storage = ZenStorage(api_key="your_api_key_here")  # Optional: can use env var

# ✅ RECOMMENDED: Using dataclass for full IDE support
options = ZenStorageUploadOptions(
    name="greeting.txt",
    metadata={
        "author": "John Doe",
        "version": "1.0",
        "tags": ["greeting", "sample"]
    }
)
upload = await storage.upload(b"Hello, world!", options)

# ✅ DICT: Also supported for flexibility
upload = await storage.upload(
    b"Hello, world!",
    {
        "name": "greeting.txt",
        "metadata": {
            "author": "John Doe",
            "version": "1.0",
            "tags": ["greeting", "sample"]
        }
    }
)

# ✅ KEYWORD ARGS: Quick and simple
upload = await storage.upload(
    b"Hello, world!",
    name="greeting.txt",
    metadata={
        "author": "John Doe", 
        "version": "1.0",
        "tags": ["greeting", "sample"]
    }
)
```

### 2. URL and Base64 Upload Support

```python
from filezen import ZenStorage, ZenStorageUploadOptions

storage = ZenStorage(api_key="your_api_key_here")

# Upload from URL - using dataclass
options = ZenStorageUploadOptions(
    name="downloaded_image.jpg",
    folder_id="downloads",
    metadata={"source": "url"}
)
url_upload = await storage.upload("https://example.com/image.jpg", options)

# Upload from URL - using dict
url_upload = await storage.upload(
    "https://example.com/image.jpg",
    {"name": "downloaded_image.jpg"}
)

# Upload from URL - using kwargs
url_upload = await storage.upload(
    "https://example.com/image.jpg",
    name="downloaded_image.jpg"
)

# Upload from base64
base64_data = "data:text/plain;base64,SGVsbG8gV29ybGQ="
b64_upload = await storage.upload(base64_data, name="base64_file.txt")

# Upload plain text
text_upload = await storage.upload(
    "Hello, World!",
    name="text_file.txt",
    mime_type="text/plain"
)
```

### 3. Manual Multipart Upload Control

```python
from filezen import ZenStorage, StartMultipartUploadParams, MultipartUploadChunkParams, FinishMultipartUploadParams, UploadMode

storage = ZenStorage(api_key="your_api_key_here")  # Optional: can use env var

# ✅ RECOMMENDED: Using dataclass for multipart parameters
start_params = StartMultipartUploadParams(
    file_name="large_file.bin",
    mime_type="application/octet-stream", 
    total_size=10 * 1024 * 1024,  # 10MB
    upload_mode=UploadMode.CHUNKED,
    metadata={"type": "binary", "source": "custom"}
)

# Start multipart upload
session = await storage.multipart.start(start_params)

# Alternative: Using dict (also supported)
session = await storage.multipart.start({
    "file_name": "large_file.bin",
    "mime_type": "application/octet-stream", 
    "total_size": 10 * 1024 * 1024,  # 10MB
    "metadata": {"type": "binary", "source": "custom"}
})

session_id = session["id"]

# Upload chunks - using dataclass
chunk_size = 1024 * 1024  # 1MB chunks
with open("large_file.bin", "rb") as f:
    chunk_index = 0
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        
        chunk_params = MultipartUploadChunkParams(
            session_id=session_id,
            chunk=chunk,
            chunk_index=chunk_index
        )
        result = await storage.multipart.upload_part(chunk_params)
        
        # Alternative: Using dict
        # result = await storage.multipart.upload_part({
        #     "session_id": session_id,
        #     "chunk": chunk,
        #     "chunk_index": chunk_index
        # })
        
        if result.is_complete:
            print(f"Upload completed: {result.file.url}")
            break
        
        chunk_index += 1

# For streaming mode (unknown size)
streaming_params = StartMultipartUploadParams(
    file_name="stream_file.bin",
    mime_type="application/octet-stream",
    upload_mode=UploadMode.STREAMING  # No total_size needed
)
streaming_session = await storage.multipart.start(streaming_params)

# Finish multipart upload - multiple ways
finish_params = FinishMultipartUploadParams(session_id=streaming_session["id"])
final_file = await storage.multipart.finish(finish_params)

# Alternative: Pass session_id directly
final_file = await storage.multipart.finish(streaming_session["id"])
```

### 4. Streaming Upload Support

For uploads where the total size is unknown or when uploading data as it becomes available:

```python
from filezen import ZenStorage, StartMultipartUploadParams, UploadMode
import asyncio

storage = ZenStorage(api_key="your_api_key_here")  # Optional: can use env var

# Example 1: Manual streaming upload (unknown total size)
streaming_params = StartMultipartUploadParams(
    file_name="stream_data.bin",
    mime_type="application/octet-stream",
    upload_mode=UploadMode.STREAMING  # No total_size needed for streaming
)
streaming_session = await storage.multipart.start(streaming_params)

session_id = streaming_session["id"]

# Upload data as it becomes available
async def stream_data_generator():
    """Simulate streaming data source"""
    for i in range(5):
        yield f"Chunk {i} data content\n".encode()
        await asyncio.sleep(0.1)  # Simulate data arrival delay

chunk_index = 0
async for chunk_data in stream_data_generator():
    result = await storage.multipart.upload_part(
        session_id=session_id,
        chunk=chunk_data,
        chunk_index=chunk_index
    )
    
    print(f"Uploaded chunk {chunk_index}")
    chunk_index += 1

# Finish the streaming upload
final_file = await storage.multipart.finish(session_id)
print(f"Streaming upload completed: {final_file.url}")

# Example 2: URL uploads automatically use streaming
# This downloads and uploads the file in chunks without knowing total size
url_upload = await storage.upload(
    "https://example.com/large-video.mp4",
    name="downloaded_video.mp4"
)
# URLs automatically use streaming mode regardless of file size

# Example 3: Streaming from file-like object
async def upload_from_stream(file_stream, filename):
    """Upload data from any file-like stream"""
    session = await storage.multipart.start(
        file_name=filename,
        mime_type="application/octet-stream",
        upload_mode=UploadMode.STREAMING
    )
    
    chunk_index = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    while True:
        chunk = file_stream.read(chunk_size)
        if not chunk:
            break
            
        await storage.multipart.upload_part(
            session_id=session["id"],
            chunk=chunk,
            chunk_index=chunk_index
        )
        
        chunk_index += 1
    
    return await storage.multipart.finish(session["id"])

# Usage with file stream
with open("unknown_size_file.bin", "rb") as f:
    result = await upload_from_stream(f, "uploaded_file.bin")
    print(f"Stream upload completed: {result.url}")
```

### 5. Event Listeners and Progress Tracking

```python
from filezen import ZenStorage, ZenUploadListener, ZenProgress

class MyUploadListener(ZenUploadListener):
    def on_upload_start(self, upload):
        print(f"Started uploading: {upload.name}")
    
    def on_upload_progress(self, upload, progress: ZenProgress):
        if progress.percent:
            print(f"Progress: {upload.name} - {progress.percent:.1f}%")
    
    def on_upload_complete(self, upload):
        print(f"Completed: {upload.file.url}")
    
    def on_upload_error(self, upload, error):
        print(f"Error: {error}")

storage = ZenStorage(api_key="your_api_key_here", keep_uploads=True)  # Optional: can use env var
storage.add_listener(MyUploadListener())

# Uploads will now trigger events
upload = await storage.upload(
    "https://example.com/file.pdf",
    name="document.pdf"
)
```

### 6. Bulk Upload Support

```python
from filezen import ZenStorage, ZenStorageBulkItem, ZenStorageUploadOptions

storage = ZenStorage(api_key="your_api_key_here")

# ✅ RECOMMENDED: Using dataclasses for bulk upload
bulk_items = [
    ZenStorageBulkItem(
        source=b"File 1 content",
        options=ZenStorageUploadOptions(name="file1.txt")
    ),
    ZenStorageBulkItem(
        source="https://example.com/image.jpg", 
        options=ZenStorageUploadOptions(
            name="downloaded.jpg",
            metadata={"source": "url"}
        )
    ),
    ZenStorageBulkItem(
        source="data:text/plain;base64,SGVsbG8=",
        options=ZenStorageUploadOptions(name="encoded.txt")
    )
]

uploads = await storage.bulk_upload(*bulk_items)

# ✅ DICT: Also supported for flexibility
uploads = await storage.bulk_upload(
    {
        "source": b"File 1 content",
        "options": {"name": "file1.txt"}
    },
    {
        "source": "https://example.com/image.jpg", 
        "options": {
            "name": "downloaded.jpg",
            "metadata": {"source": "url"}
        }
    },
    {
        "source": "data:text/plain;base64,SGVsbG8=",
        "options": {"name": "encoded.txt"}
    }
)

for upload in uploads:
    print(f"Uploaded: {upload.file.url}")
```

### 7. Flexible API - Use What You Prefer

The API supports multiple ways to pass parameters for maximum flexibility:

```python
from filezen import ZenStorage, ZenStorageUploadOptions, ZenStorageBulkItem

storage = ZenStorage()

# Method 1: Keyword arguments (most concise)
upload1 = await storage.upload(
    b"content",
    name="file1.txt",
    metadata={"type": "text"}
)

# Method 2: Dictionary (familiar to most Python developers)
upload2 = await storage.upload(
    b"content",
    {
        "name": "file2.txt", 
        "metadata": {"type": "text"}
    }
)

# Method 3: Typed classes (best for IDE support and type checking)
upload3 = await storage.upload(
    b"content",
    ZenStorageUploadOptions(
        name="file3.txt",
        metadata={"type": "text"}
    )
)

# Same flexibility applies to multipart uploads
session = await storage.multipart.start(
    file_name="test.bin", 
    mime_type="application/octet-stream"
)
# session = await storage.multipart.start({
#     "file_name": "test.bin", 
#     "mime_type": "application/octet-stream"
# })

# And bulk uploads
uploads = await storage.bulk_upload(
    {"source": b"data1", "options": {"name": "file1.txt"}},  # Dict
    ZenStorageBulkItem(source=b"data2", options={"name": "file2.txt"})  # Typed class
)
```

## Type Definitions

The SDK now includes comprehensive type support with **full IDE autocomplete**:

```python
from filezen import (
    # Main classes
    ZenStorage,           # Main storage class
    ZenUpload,            # Upload operation class
    ZenApi,               # Low-level API client
    
    # Upload types
    ZenUploadSource,      # Union[bytes, str] for upload sources  
    ZenMetadata,          # Dict[str, Any] for metadata
    ZenStorageUploadOptions,  # Upload configuration
    ZenStorageBulkItem,   # Bulk upload item
    
    # Multipart types
    UploadMode,           # Enum: CHUNKED, STREAMING
    StartMultipartUploadParams,  # Multipart start parameters
    MultipartUploadChunkParams,  # Chunk upload parameters
    FinishMultipartUploadParams, # Multipart finish parameters
    MultipartChunkUploadResult,  # Chunk upload result
    
    # Response types
    ZenFile,              # File information
    ZenProject,           # Project information
    ZenList,              # File list response
    
    # Progress and events
    ZenProgress,          # Progress tracking
    ZenUploadListener,    # Upload event listener
    
    # Error types
    ZenError,             # Base error class
    ZenUploadError,       # Upload-specific errors
    ZenApiError,          # API-specific errors
    
    # Helper function
    to_dataclass,         # Convert dict to dataclass
)
```

## Error Handling

```python
from filezen import ZenError, ZenUploadError, ZenStorageUploadOptions

try:
    options = ZenStorageUploadOptions(name="test.txt")
    upload = await storage.upload(
        "https://invalid-url.com/file.txt",
        options
    )
except ZenError as e:
    print(f"Upload failed: {e}")
    print(f"Error code: {e.code}")
    print(f"Error message: {e.message}")
```

## Requirements

- Python 3.8+
- httpx
- pydantic

## Multipart Upload

The SDK automatically uses multipart upload for files larger than 10MB. This provides:

- **Resumable uploads**: Upload can be resumed if interrupted
- **Better performance**: Parallel chunk uploads
- **Progress tracking**: Detailed progress for each chunk
- **Error recovery**: Automatic retry for failed chunks

```python
# Large files are automatically handled with multipart upload
with open("large_video.mp4", "rb") as f:
    options = ZenStorageUploadOptions(
        name="large_video.mp4",
        mime_type="video/mp4"
    )
    upload = await storage.upload(f.read(), options)
    # Automatically uses multipart upload for files > 10MB
```

## API Reference

### ZenStorage

Main storage class for FileZen operations.

#### Constructor

```python
ZenStorage(
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    keep_uploads: bool = False
)
```

#### Methods

- `upload(source: ZenUploadSource, options: Union[Dict, ZenStorageUploadOptions]) -> ZenUpload`: Upload a single file
- `bulk_upload(*uploads: Union[Dict, ZenStorageBulkItem]) -> List[ZenUpload]`: Upload multiple files
- `build_upload(source: ZenUploadSource, options: Union[Dict, ZenStorageUploadOptions]) -> ZenUpload`: Build upload without starting
- `generate_signed_url(options: Dict[str, Any]) -> str`: Generate a signed URL
- `delete_by_url(url: str) -> bool`: Delete a file by URL
- `add_listener(listener: ZenUploadListener) -> None`: Add upload event listener
- `remove_listener(listener: ZenUploadListener) -> None`: Remove upload event listener
- `close() -> None`: Close the storage client

#### Properties

- `multipart: ZenMultipartControl`: Manual multipart upload control
- `get_uploads: List[ZenUpload]`: Get all uploads (if tracking enabled)
- `active_uploads: List[ZenUpload]`: Get active uploads (if tracking enabled)

### ZenUpload

Represents a file upload operation.

#### Properties

- `file: Optional[ZenFile]`: Uploaded file information
- `error: Optional[ZenError]`: Upload error if any
- `is_completed: bool`: Whether upload is completed
- `is_cancelled: bool`: Whether upload is cancelled
- `local_id: str`: Unique upload identifier
- `name: str`: File name
- `mime_type: str`: MIME type

#### Methods

- `upload() -> ZenUpload`: Perform the upload operation
- `cancel()`: Cancel the upload

### ZenMultipartControl

Manual control over multipart uploads.

#### Methods

- `start(params: Union[Dict, StartMultipartUploadParams]) -> Dict[str, str]`: Start multipart upload
- `upload_part(params: Union[Dict, MultipartUploadChunkParams]) -> MultipartChunkUploadResult`: Upload a chunk
- `finish(params: Union[Dict, FinishMultipartUploadParams, str]) -> ZenFile`: Finish multipart upload

## Examples

See the [FastAPI example app](../../apps/python-fastapi-server) for a complete implementation with web interface.

## IDE Support Benefits

The SDK is designed for excellent IDE support:

- **Full Autocomplete**: All parameters and methods are fully typed
- **Type Checking**: Catch errors at development time, not runtime
- **Documentation**: Inline documentation for all parameters
- **Refactoring**: Safe refactoring with IDE support
- **Error Detection**: IDE will catch typos and invalid parameters

```python
# Your IDE will show all available parameters with documentation
options = ZenStorageUploadOptions(
    name="file.txt",        # IDE shows: name: str
    folder_id="123",        # IDE shows: folder_id: Optional[str]
    project_id="456",       # IDE shows: project_id: Optional[str]
    mime_type="text/plain", # IDE shows: mime_type: Optional[str]
    metadata={}             # IDE shows: metadata: Optional[Dict[str, Any]]
)
```

## Documentation

For detailed documentation, visit [docs.filezen.dev](https://docs.filezen.dev)

## License

MIT License
