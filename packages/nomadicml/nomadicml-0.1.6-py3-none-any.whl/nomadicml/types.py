"""Type definitions for the NomadicML SDK."""

from enum import Enum
class VideoSource(str, Enum):
    """Video source types."""
    
    FILE = "file"
    SAVED = "saved"  # Note: Upload from saved videos is not supported. Use analyze() for existing videos.
    VIDEO_URL = "video_url"


class ProcessingStatus(str, Enum):
    """Video processing status types."""
    
    UPLOADING = "uploading"
    UPLOADING_FAILED = "uploading_failed"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"




