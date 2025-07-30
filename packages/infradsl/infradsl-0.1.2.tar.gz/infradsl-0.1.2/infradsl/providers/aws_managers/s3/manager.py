"""
AWS S3 Manager

Main coordinator for S3 operations. This manager orchestrates
different S3 components like buckets and objects.
"""

from typing import Dict, Any, List, Optional
from ..aws_client import AwsClient
from .buckets import S3Buckets
from .objects import S3Objects


class S3Manager:
    """Main S3 manager that coordinates bucket and object operations"""

    def __init__(self, aws_client: Optional[AwsClient] = None):
        self.aws_client = aws_client or AwsClient()

        # Initialize component managers
        self.buckets = S3Buckets(self.aws_client)
        self.objects = S3Objects(self.aws_client)

    def _ensure_authenticated(self):
        """Ensure AWS authentication"""
        if not self.aws_client.is_authenticated:
            self.aws_client.authenticate(silent=True)

    # Bucket operations - delegate to buckets component
    def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create an S3 bucket"""
        self._ensure_authenticated()
        return self.buckets.create(bucket_name, region, **kwargs)

    def delete_bucket(self, bucket_name: str, force: bool = False) -> Dict[str, Any]:
        """Delete an S3 bucket"""
        self._ensure_authenticated()
        return self.buckets.delete(bucket_name, force)

    def list_buckets(self) -> List[Dict[str, Any]]:
        """List all S3 buckets"""
        self._ensure_authenticated()
        return self.buckets.list()

    def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """Get detailed information about a bucket"""
        self._ensure_authenticated()
        return self.buckets.get_info(bucket_name)

    def enable_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Enable versioning on a bucket"""
        self._ensure_authenticated()
        return self.buckets.enable_versioning(bucket_name)

    def disable_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Disable versioning on a bucket"""
        self._ensure_authenticated()
        return self.buckets.disable_versioning(bucket_name)

    def enable_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Enable server-side encryption on a bucket"""
        self._ensure_authenticated()
        return self.buckets.enable_encryption(bucket_name)

    # Object operations - delegate to objects component
    def upload_file(
        self,
        bucket_name: str,
        file_path: str,
        key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload a file to S3"""
        self._ensure_authenticated()
        return self.objects.upload(bucket_name, file_path, key, **kwargs)

    def download_file(
        self,
        bucket_name: str,
        key: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Download a file from S3"""
        self._ensure_authenticated()
        return self.objects.download(bucket_name, key, file_path)

    def delete_object(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Delete an object from S3"""
        self._ensure_authenticated()
        return self.objects.delete(bucket_name, key)

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """List objects in an S3 bucket"""
        self._ensure_authenticated()
        return self.objects.list(bucket_name, prefix, max_keys)

    def get_object_info(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Get detailed information about a specific object"""
        self._ensure_authenticated()
        return self.objects.get_info(bucket_name, key)

    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Copy an object from one location to another"""
        self._ensure_authenticated()
        return self.objects.copy(source_bucket, source_key, dest_bucket, dest_key, **kwargs)

    def generate_presigned_url(
        self,
        bucket_name: str,
        key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """Generate a presigned URL for an S3 object"""
        self._ensure_authenticated()
        return self.objects.generate_presigned_url(bucket_name, key, expiration, http_method)

    def set_object_public(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Make an object publicly readable"""
        self._ensure_authenticated()
        return self.objects.set_public_read(bucket_name, key)

    def set_object_private(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Make an object private"""
        self._ensure_authenticated()
        return self.objects.set_private(bucket_name, key)

    def object_exists(self, bucket_name: str, key: str) -> bool:
        """Check if an object exists in S3"""
        self._ensure_authenticated()
        return self.objects.exists(bucket_name, key)

    def get_object_size(self, bucket_name: str, key: str) -> int:
        """Get the size of an object in bytes"""
        self._ensure_authenticated()
        return self.objects.get_size(bucket_name, key)

    # Convenience methods for common workflows
    def quick_upload(
        self,
        bucket_name: str,
        file_path: str,
        public: bool = False
    ) -> Dict[str, Any]:
        """
        Quick upload a file with sensible defaults.

        Args:
            bucket_name: Name of the bucket
            file_path: Local file path to upload
            public: Whether to make the file publicly accessible

        Returns:
            Upload information
        """
        self._ensure_authenticated()

        import os
        filename = os.path.basename(file_path)

        print(f"🚀 Quick uploading file: {filename}")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Public: {public}")

        result = self.upload_file(
            bucket_name=bucket_name,
            file_path=file_path,
            public_read=public
        )

        if public:
            self.set_object_public(bucket_name, result['key'])

        return result

    def sync_directory(
        self,
        bucket_name: str,
        local_dir: str,
        prefix: str = "",
        public: bool = False
    ) -> Dict[str, Any]:
        """
        Sync a local directory to S3.

        Args:
            bucket_name: Name of the bucket
            local_dir: Local directory to sync
            prefix: S3 key prefix for uploaded files
            public: Whether to make files publicly accessible

        Returns:
            Sync operation summary
        """
        self._ensure_authenticated()

        import os

        print(f"📁 Syncing directory to S3")
        print(f"   - Local: {local_dir}")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Prefix: {prefix}")

        uploaded_files = []
        total_size = 0

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_dir)

                # Convert Windows paths to S3-compatible paths
                s3_key = prefix + relative_path.replace('\\', '/')

                result = self.upload_file(
                    bucket_name=bucket_name,
                    file_path=local_file_path,
                    key=s3_key,
                    public_read=public
                )

                uploaded_files.append(result)
                total_size += result['size']

        print(f"✅ Directory sync completed")
        print(f"   - Files uploaded: {len(uploaded_files)}")
        print(f"   - Total size: {total_size:,} bytes")

        return {
            'bucket_name': bucket_name,
            'files_uploaded': len(uploaded_files),
            'total_size': total_size,
            'files': uploaded_files
        }

    def get_region(self) -> str:
        """Get current AWS region"""
        return self.aws_client.get_region()

    def get_account_id(self) -> str:
        """Get current AWS account ID"""
        return self.aws_client.get_account_id()
