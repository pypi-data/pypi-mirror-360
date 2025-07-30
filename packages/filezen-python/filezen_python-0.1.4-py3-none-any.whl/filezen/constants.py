"""Constants for the FileZen Python SDK."""

DEFAULT_API_URL = "https://api.filezen.dev"
DEFAULT_SIGN_URL = "/files/upload"
MULTIPART_THRESHOLD = 10 * 1024 * 1024  # 10MB threshold for multipart upload
MULTIPART_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks
