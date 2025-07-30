"""
AWS S3 Buckets Operations

Focused module for S3 bucket lifecycle management.
Handles creation, deletion, configuration, and listing of S3 buckets.
"""

import json
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..aws_client import AwsClient

if TYPE_CHECKING:
    try:
        from botocore.client import BaseClient
    except ImportError:
        BaseClient = Any


class S3Buckets:
    """Handles S3 bucket operations"""

    def __init__(self, aws_client: AwsClient):
        self.aws_client = aws_client
        self.s3_client: Optional['BaseClient'] = None

    def _ensure_clients(self):
        """Ensure S3 clients are initialized"""
        if not self.s3_client:
            self.s3_client = self.aws_client.get_client('s3')

        if not self.s3_client:
            raise RuntimeError("Failed to initialize S3 client")

    def create(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        public_read: bool = False,
        versioning: bool = False,
        encryption: bool = True,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create an S3 bucket.

        Args:
            bucket_name: Name of the bucket to create
            region: AWS region (default: current region)
            public_read: Whether to allow public read access
            versioning: Whether to enable versioning
            encryption: Whether to enable server-side encryption
            tags: Tags to apply to the bucket

        Returns:
            Dict containing bucket information
        """
        self._ensure_clients()

        target_region = region or self.aws_client.get_region()

        print(f"🪣 Creating S3 bucket: {bucket_name}")
        print(f"   - Region: {target_region}")
        print(f"   - Public Read: {public_read}")
        print(f"   - Versioning: {versioning}")
        print(f"   - Encryption: {encryption}")

        # Create bucket
        create_params = {'Bucket': bucket_name}

        # Only add location constraint if not us-east-1
        if target_region != 'us-east-1':
            create_params['CreateBucketConfiguration'] = {
                'LocationConstraint': target_region
            }

        try:
            self.s3_client.create_bucket(**create_params)
        except Exception as e:
            print(f"❌ Failed to create bucket: {str(e)}")
            raise
        print(f"✅ Bucket {bucket_name} created successfully")

        # Configure versioning
        if versioning:
            self._enable_versioning(bucket_name)

        # Configure encryption
        if encryption:
            self._enable_encryption(bucket_name)

        # Configure public access
        if public_read:
            self._enable_public_read(bucket_name)
        else:
            self._block_public_access(bucket_name)

        # Add tags
        if tags:
            self._add_tags(bucket_name, tags)

        return {
            'bucket_name': bucket_name,
            'region': target_region,
            'status': 'created',
            'public_read': public_read,
            'versioning': versioning,
            'encryption': encryption,
            'url': f"https://{bucket_name}.s3.{target_region}.amazonaws.com/"
        }

    def delete(self, bucket_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete an S3 bucket.

        Args:
            bucket_name: Name of the bucket to delete
            force: Whether to force delete (empty bucket first)

        Returns:
            Dict containing deletion information
        """
        self._ensure_clients()

        print(f"🗑️  Deleting S3 bucket: {bucket_name}")

        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=bucket_name)

            if force:
                print("   - Force deletion enabled, emptying bucket first...")
                self._empty_bucket(bucket_name)

            # Delete bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
        except Exception as e:
            print(f"❌ Failed to delete bucket: {str(e)}")
            raise
        print(f"✅ Bucket {bucket_name} deleted successfully")

        return {
            'bucket_name': bucket_name,
            'status': 'deleted'
        }

    def list(self) -> List[Dict[str, Any]]:
        """
        List all S3 buckets.

        Returns:
            List of bucket information
        """
        self._ensure_clients()

        try:
            response = self.s3_client.list_buckets()
            buckets = []

            for bucket in response['Buckets']:
                bucket_name = bucket['Name']

                # Get bucket location
                try:
                    location = self.s3_client.get_bucket_location(Bucket=bucket_name)
                    region = location['LocationConstraint'] or 'us-east-1'
                except Exception:
                    region = 'unknown'

                buckets.append({
                    'name': bucket_name,
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'region': region
                })

            return buckets
        except Exception as e:
            print(f"❌ Failed to list buckets: {str(e)}")
            raise

    def get_info(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a bucket.

        Args:
            bucket_name: Name of the bucket

        Returns:
            Dict containing detailed bucket information
        """
        self._ensure_clients()

        try:
            # Get basic bucket info
            response = self.s3_client.head_bucket(Bucket=bucket_name)

            # Get bucket location
            location = self.s3_client.get_bucket_location(Bucket=bucket_name)
            region = location['LocationConstraint'] or 'us-east-1'

            # Get versioning status
            try:
                versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                versioning_status = versioning.get('Status', 'Disabled')
            except Exception:
                versioning_status = 'Unknown'

            # Get encryption status
            try:
                self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                encryption_enabled = True
            except Exception:
                encryption_enabled = False

            # Get public access block
            try:
                self.s3_client.get_public_access_block(Bucket=bucket_name)
                public_access_blocked = True
            except Exception:
                public_access_blocked = False

            return {
                'name': bucket_name,
                'region': region,
                'versioning': versioning_status,
                'encryption': encryption_enabled,
                'public_access_blocked': public_access_blocked,
                'creation_date': response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('date')
            }
        except Exception as e:
            print(f"❌ Failed to get bucket info: {str(e)}")
            raise

    def enable_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Enable versioning on a bucket"""
        self._ensure_clients()
        self._enable_versioning(bucket_name)
        return {'bucket_name': bucket_name, 'versioning': 'enabled'}

    def disable_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Disable versioning on a bucket"""
        self._ensure_clients()
        self.s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Suspended'}
        )
        print(f"✅ Versioning disabled for bucket {bucket_name}")
        return {'bucket_name': bucket_name, 'versioning': 'disabled'}

    def enable_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Enable server-side encryption on a bucket"""
        self._ensure_clients()
        self._enable_encryption(bucket_name)
        return {'bucket_name': bucket_name, 'encryption': 'enabled'}

    def _enable_versioning(self, bucket_name: str):
        """Internal method to enable versioning"""
        self.s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("   - Versioning enabled")

    def _enable_encryption(self, bucket_name: str):
        """Internal method to enable encryption"""
        self.s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        print("   - Server-side encryption enabled")

    def _enable_public_read(self, bucket_name: str):
        """Internal method to enable public read access"""
        # Remove public access block
        self.s3_client.delete_public_access_block(Bucket=bucket_name)

        # Set bucket policy for public read
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

        self.s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("   - Public read access configured")

    def _block_public_access(self, bucket_name: str):
        """Internal method to block public access"""
        self.s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("   - Public access blocked")

    def _add_tags(self, bucket_name: str, tags: Dict[str, str]):
        """Internal method to add tags to bucket"""
        tag_set = [{'Key': k, 'Value': v} for k, v in tags.items()]
        self.s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': tag_set}
        )
        print(f"   - Tags applied: {len(tags)} tags")

    def _empty_bucket(self, bucket_name: str):
        """Internal method to empty all objects from a bucket"""
        try:
            # List and delete all objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name)

            for page in pages:
                if 'Contents' in page:
                    objects = [{'Key': obj['Key']} for obj in page['Contents']]
                    self.s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects}
                    )
                    print(f"   - Deleted {len(objects)} objects")

            # List and delete all object versions
            paginator = self.s3_client.get_paginator('list_object_versions')
            pages = paginator.paginate(Bucket=bucket_name)

            for page in pages:
                versions = []
                if 'Versions' in page:
                    versions.extend([
                        {'Key': obj['Key'], 'VersionId': obj['VersionId']}
                        for obj in page['Versions']
                    ])
                if 'DeleteMarkers' in page:
                    versions.extend([
                        {'Key': obj['Key'], 'VersionId': obj['VersionId']}
                        for obj in page['DeleteMarkers']
                    ])

                if versions:
                    self.s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': versions}
                    )
                    print(f"   - Deleted {len(versions)} object versions")
        except Exception as e:
            print(f"❌ Failed to empty bucket: {str(e)}")
            # Don't re-raise here as this is called during force delete
