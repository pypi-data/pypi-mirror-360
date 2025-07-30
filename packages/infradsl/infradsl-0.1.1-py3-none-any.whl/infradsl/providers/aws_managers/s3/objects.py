"""
AWS S3 Objects Operations

Focused module for S3 object lifecycle management.
Handles upload, download, deletion, and listing of S3 objects.
"""

import os
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..aws_client import AwsClient

if TYPE_CHECKING:
    try:
        from botocore.client import BaseClient
        from boto3.resources.base import ServiceResource
    except ImportError:
        BaseClient = Any
        ServiceResource = Any


class S3Objects:
    """Handles S3 object operations"""

    def __init__(self, aws_client: AwsClient):
        self.aws_client = aws_client
        self.s3_client: Optional['BaseClient'] = None
        self.s3_resource: Optional['ServiceResource'] = None

    def _ensure_clients(self):
        """Ensure S3 clients are initialized"""
        if not self.s3_client:
            self.s3_client = self.aws_client.get_client('s3')
            self.s3_resource = self.aws_client.get_resource('s3')

        if not self.s3_client:
            raise RuntimeError("Failed to initialize S3 client")

    def upload(
        self,
        bucket_name: str,
        file_path: str,
        key: Optional[str] = None,
        public_read: bool = False,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to S3.

        Args:
            bucket_name: Name of the bucket
            file_path: Local file path to upload
            key: S3 object key (default: filename)
            public_read: Whether to make the object publicly readable
            metadata: Additional metadata for the object
            content_type: Content type for the object

        Returns:
            Dict containing upload information
        """
        self._ensure_clients()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        object_key = key or os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        print("📤 Uploading file to S3")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Key: {object_key}")
        print(f"   - Size: {file_size:,} bytes")

        extra_args = {}

        if public_read:
            extra_args['ACL'] = 'public-read'

        if metadata:
            extra_args['Metadata'] = metadata

        if content_type:
            extra_args['ContentType'] = content_type

        try:
            # Upload file
            self.s3_client.upload_file(
                file_path,
                bucket_name,
                object_key,
                ExtraArgs=extra_args
            )

            print("✅ File uploaded successfully")
        except Exception as e:
            print(f"❌ Failed to upload file: {str(e)}")
            raise

        # Get object URL
        region = self.aws_client.get_region()
        object_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"

        return {
            'bucket_name': bucket_name,
            'key': object_key,
            'size': file_size,
            'url': object_url,
            'public_read': public_read
        }

    def download(
        self,
        bucket_name: str,
        key: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Download a file from S3.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key
            file_path: Local file path to save to

        Returns:
            Dict containing download information
        """
        self._ensure_clients()

        print("📥 Downloading file from S3")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Key: {key}")
        print(f"   - Local path: {file_path}")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Download file
            self.s3_client.download_file(bucket_name, key, file_path)

            file_size = os.path.getsize(file_path)
            print(f"✅ File downloaded successfully ({file_size:,} bytes)")
        except Exception as e:
            print(f"❌ Failed to download file: {str(e)}")
            raise

        return {
            'bucket_name': bucket_name,
            'key': key,
            'local_path': file_path,
            'size': file_size
        }

    def delete(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """
        Delete an object from S3.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            Dict containing deletion information
        """
        self._ensure_clients()

        print("🗑️  Deleting S3 object")
        print(f"   - Bucket: {bucket_name}")
        print(f"   - Key: {key}")

        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            print("✅ Object deleted successfully")
        except Exception as e:
            print(f"❌ Failed to delete object: {str(e)}")
            raise

        return {
            'bucket_name': bucket_name,
            'key': key,
            'status': 'deleted'
        }

    def list(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List objects in an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            prefix: Object key prefix filter
            max_keys: Maximum number of objects to return

        Returns:
            List of object information
        """
        self._ensure_clients()

        params = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }

        if prefix:
            params['Prefix'] = prefix

        try:
            response = self.s3_client.list_objects_v2(**params)
            objects = []

            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"'),
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    })

            return objects
        except Exception as e:
            print(f"❌ Failed to list objects: {str(e)}")
            raise

    def get_info(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific object.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            Dict containing detailed object information
        """
        self._ensure_clients()

        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)

            return {
                'bucket_name': bucket_name,
                'key': key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'].strip('"'),
                'content_type': response.get('ContentType'),
                'cache_control': response.get('CacheControl'),
                'content_disposition': response.get('ContentDisposition'),
                'content_encoding': response.get('ContentEncoding'),
                'content_language': response.get('ContentLanguage'),
                'expires': response.get('Expires'),
                'metadata': response.get('Metadata', {}),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'version_id': response.get('VersionId')
            }
        except Exception as e:
            print(f"❌ Failed to get object info: {str(e)}")
            raise

    def copy(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Copy an object from one location to another.

        Args:
            source_bucket: Source bucket name
            source_key: Source object key
            dest_bucket: Destination bucket name
            dest_key: Destination object key
            metadata: Optional metadata for the copied object

        Returns:
            Dict containing copy information
        """
        self._ensure_clients()

        print("📋 Copying S3 object")
        print(f"   - Source: s3://{source_bucket}/{source_key}")
        print(f"   - Destination: s3://{dest_bucket}/{dest_key}")

        copy_source = {
            'Bucket': source_bucket,
            'Key': source_key
        }

        extra_args = {}
        if metadata:
            extra_args['Metadata'] = metadata
            extra_args['MetadataDirective'] = 'REPLACE'

        try:
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket,
                Key=dest_key,
                **extra_args
            )

            print("✅ Object copied successfully")
        except Exception as e:
            print(f"❌ Failed to copy object: {str(e)}")
            raise

        return {
            'source_bucket': source_bucket,
            'source_key': source_key,
            'dest_bucket': dest_bucket,
            'dest_key': dest_key,
            'status': 'copied'
        }

    def generate_presigned_url(
        self,
        bucket_name: str,
        key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """
        Generate a presigned URL for an S3 object.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the URL (GET, PUT, DELETE)

        Returns:
            Presigned URL string
        """
        self._ensure_clients()

        client_method = {
            'GET': 'get_object',
            'PUT': 'put_object',
            'DELETE': 'delete_object'
        }.get(http_method.upper(), 'get_object')

        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod=client_method,
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=expiration
            )

            print(f"🔗 Generated presigned URL for {key}")
            print(f"   - Method: {http_method}")
            print(f"   - Expires in: {expiration} seconds")

            return url
        except Exception as e:
            print(f"❌ Failed to generate presigned URL: {str(e)}")
            raise

    def set_public_read(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """
        Make an object publicly readable.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            Dict containing operation status
        """
        self._ensure_clients()

        try:
            self.s3_client.put_object_acl(
                Bucket=bucket_name,
                Key=key,
                ACL='public-read'
            )

            region = self.aws_client.get_region()
            public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"

            print(f"✅ Object {key} is now publicly readable")
            print(f"   - Public URL: {public_url}")
        except Exception as e:
            print(f"❌ Failed to set object public: {str(e)}")
            raise

        return {
            'bucket_name': bucket_name,
            'key': key,
            'status': 'public',
            'public_url': public_url
        }

    def set_private(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """
        Make an object private (remove public access).

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            Dict containing operation status
        """
        self._ensure_clients()

        try:
            self.s3_client.put_object_acl(
                Bucket=bucket_name,
                Key=key,
                ACL='private'
            )

            print(f"✅ Object {key} is now private")
        except Exception as e:
            print(f"❌ Failed to set object private: {str(e)}")
            raise

        return {
            'bucket_name': bucket_name,
            'key': key,
            'status': 'private'
        }

    def exists(self, bucket_name: str, key: str) -> bool:
        """
        Check if an object exists in S3.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            True if object exists, False otherwise
        """
        self._ensure_clients()

        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=key)
            return True
        except Exception:
            return False

    def get_size(self, bucket_name: str, key: str) -> int:
        """
        Get the size of an object in bytes.

        Args:
            bucket_name: Name of the bucket
            key: S3 object key

        Returns:
            Object size in bytes
        """
        self._ensure_clients()

        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)
            return response['ContentLength']
        except Exception as e:
            print(f"❌ Failed to get object size: {str(e)}")
            raise
