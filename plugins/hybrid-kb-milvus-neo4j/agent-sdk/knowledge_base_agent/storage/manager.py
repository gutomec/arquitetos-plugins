"""
Storage Manager - Minio File Storage
=====================================
"""

import io
import zipfile
from datetime import timedelta
from typing import List, Tuple, BinaryIO
import logging

from minio import Minio
from minio.error import S3Error

from ..core.config import KBConfig

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages file storage in Minio."""

    MIME_TYPES = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain',
        'md': 'text/markdown',
        'csv': 'text/csv',
        'json': 'application/json',
        'html': 'text/html',
        'zip': 'application/zip',
    }

    def __init__(self, config: KBConfig):
        self.config = config
        self.bucket = config.minio_bucket

        self.client = Minio(
            config.minio_endpoint,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=config.minio_secure
        )

        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")

    def generate_object_key(self, user_id: str, kb_id: str, file_id: str, filename: str) -> str:
        """Generate structured object key."""
        return f"users/{user_id}/kbs/{kb_id}/files/{file_id}/{filename}"

    def get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return self.MIME_TYPES.get(ext, 'application/octet-stream')

    def get_presigned_upload_url(
        self,
        object_key: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Get presigned URL for upload."""
        return self.client.presigned_put_object(self.bucket, object_key, expires=expires)

    def get_presigned_download_url(
        self,
        object_key: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Get presigned URL for download."""
        return self.client.presigned_get_object(self.bucket, object_key, expires=expires)

    def upload_file(
        self,
        object_key: str,
        content: bytes,
        content_type: str = None
    ) -> str:
        """Upload file content."""
        if content_type is None:
            content_type = self.get_mime_type(object_key)

        result = self.client.put_object(
            self.bucket,
            object_key,
            io.BytesIO(content),
            len(content),
            content_type=content_type
        )
        logger.info(f"Uploaded: {object_key}")
        return result.etag

    def download_file(self, object_key: str) -> bytes:
        """Download file content."""
        response = self.client.get_object(self.bucket, object_key)
        data = response.read()
        response.close()
        response.release_conn()
        return data

    def delete_file(self, object_key: str):
        """Delete a file."""
        self.client.remove_object(self.bucket, object_key)
        logger.info(f"Deleted: {object_key}")

    def delete_kb_files(self, user_id: str, kb_id: str) -> int:
        """Delete all files for a KB."""
        prefix = f"users/{user_id}/kbs/{kb_id}/"
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        count = 0
        for obj in objects:
            self.client.remove_object(self.bucket, obj.object_name)
            count += 1
        logger.info(f"Deleted {count} objects for KB {kb_id}")
        return count

    def extract_zip(self, object_key: str) -> List[Tuple[str, bytes, str]]:
        """Extract ZIP file contents."""
        zip_data = self.download_file(object_key)
        extracted = []

        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir() or file_info.filename.startswith('__MACOSX'):
                    continue

                filename = file_info.filename.split('/')[-1]
                if not filename or filename.startswith('.'):
                    continue

                content = zip_ref.read(file_info.filename)
                mime_type = self.get_mime_type(filename)
                extracted.append((filename, content, mime_type))

        return extracted

    def health_check(self) -> dict:
        """Check Minio health."""
        try:
            self.client.list_buckets()
            return {"status": "healthy", "endpoint": self.config.minio_endpoint}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
