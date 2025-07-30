"""
Google Cloud Storage Bucket Manager

Rails-like bucket management with intelligent defaults, security best practices,
and developer-friendly operations. Follows InfraDSL's convention over configuration
philosophy.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Union
from google.cloud import storage
from google.cloud.exceptions import NotFound, Conflict
from pydantic import BaseModel
from ..gcp_client import GcpClient


class BucketConfig(BaseModel):
    """Configuration for Google Cloud Storage bucket"""
    name: str
    location: str = "US"  # Multi-region by default for best availability
    storage_class: str = "STANDARD"  # Standard for general use
    public_access_prevention: str = "enforced"  # Security by default
    uniform_bucket_level_access: bool = True  # Simplified permissions
    versioning_enabled: bool = False
    lifecycle_rules: List[Dict[str, Any]] = []
    cors_rules: List[Dict[str, Any]] = []
    labels: Optional[Dict[str, str]] = None
    retention_period: Optional[int] = None  # In seconds
    encryption_key: Optional[str] = None  # Customer-managed encryption key


class BucketManager:
    """
    Manages Google Cloud Storage bucket operations with Rails-like conventions.

    Features:
    - Smart defaults for security and performance
    - Intelligent lifecycle management
    - Convention-based naming and organization
    - Developer-friendly error messages
    """

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        self._storage_client = None
        self._project_id = None

    @property
    def storage_client(self):
        """Get the storage client (lazy loading after authentication)"""
        if not self._storage_client:
            self._storage_client = storage.Client(
                project=self.gcp_client.project,
                credentials=self.gcp_client.credentials
            )
        return self._storage_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    def create_bucket(self, config: BucketConfig) -> Dict[str, Any]:
        """
        Create a Cloud Storage bucket with Rails-like conventions.

        Args:
            config: Bucket configuration

        Returns:
            Dict containing bucket information

        Raises:
            Exception: If bucket creation fails
        """
        if not self.gcp_client.check_authenticated():
            raise ValueError("Authentication not set. Use .authenticate() first.")

        try:
            # Check if bucket already exists
            existing_bucket = self._get_bucket(config.name)
            if existing_bucket:
                print(f"🔄 Bucket '{config.name}' already exists")
                return self._bucket_to_dict(existing_bucket, config)

            print(f"🪣 Creating Cloud Storage bucket: {config.name}")
            print(f"   📍 Location: {config.location}")
            print(f"   🏷️  Storage Class: {config.storage_class}")

            # Create bucket with Rails-like smart defaults
            bucket = storage.Bucket(self.storage_client, name=config.name)

            # Set location and storage class
            bucket.location = config.location
            bucket.storage_class = config.storage_class

            # Security defaults (Rails philosophy: secure by default)
            bucket.iam_configuration.public_access_prevention = config.public_access_prevention
            bucket.iam_configuration.uniform_bucket_level_access_enabled = config.uniform_bucket_level_access

            # Enable versioning if requested
            bucket.versioning_enabled = config.versioning_enabled

            # Set labels for organization
            if config.labels:
                bucket.labels = config.labels

            # Set retention policy if specified
            if config.retention_period:
                bucket.retention_period = config.retention_period

            # Create the bucket
            created_bucket = self.storage_client.create_bucket(bucket)
            print(f"✅ Bucket created successfully: {config.name}")

            # Apply lifecycle rules if specified
            if config.lifecycle_rules:
                self._apply_lifecycle_rules(created_bucket, config.lifecycle_rules)

            # Apply CORS rules if specified
            if config.cors_rules:
                self._apply_cors_rules(created_bucket, config.cors_rules)

            return self._bucket_to_dict(created_bucket, config)

        except Conflict:
            # Bucket name already taken globally
            raise Exception(
                f"Bucket name '{config.name}' is already taken globally. "
                f"Try: {config.name}-{self.project_id[:8]} or choose a different name."
            )
        except Exception as e:
            raise Exception(f"Failed to create bucket: {str(e)}")

    def get_bucket_info(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        """Get bucket information"""
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                return None

            return self._bucket_to_dict(bucket)
        except Exception as e:
            raise Exception(f"Failed to get bucket info: {str(e)}")

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete a Cloud Storage bucket.

        Args:
            bucket_name: Name of bucket to delete
            force: If True, delete all objects first

        Returns:
            bool: True if deletion successful
        """
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                print(f"✅ Bucket '{bucket_name}' doesn't exist - nothing to delete")
                return True

            print(f"🗑️  Deleting bucket: {bucket_name}")

            # Check if bucket has objects
            blobs = list(bucket.list_blobs(max_results=1))
            if blobs and not force:
                print(f"⚠️  Bucket '{bucket_name}' contains objects")
                print(f"   Use force=True to delete all objects first")
                return False

            # Delete all objects if force is True
            if force and blobs:
                print(f"🗑️  Deleting all objects in bucket...")
                bucket.delete_blobs(bucket.list_blobs())

            # Delete the bucket
            bucket.delete()
            print(f"✅ Bucket deleted: {bucket_name}")
            return True

        except Exception as e:
            print(f"⚠️  Failed to delete bucket {bucket_name}: {str(e)}")
            return False

    def upload_file(
        self,
        bucket_name: str,
        source_path: str,
        destination_name: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a file to bucket with Rails-like convenience.

        Args:
            bucket_name: Target bucket name
            source_path: Local file path
            destination_name: Name in bucket (defaults to filename)
            **kwargs: Additional options (content_type, metadata, etc.)

        Returns:
            Dict containing upload information
        """
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")

            bucket = self._get_bucket(bucket_name)
            if not bucket:
                raise Exception(f"Bucket '{bucket_name}' not found")

            # Default destination name to filename
            if not destination_name:
                destination_name = os.path.basename(source_path)

            print(f"📤 Uploading file to bucket: {bucket_name}")
            print(f"   📁 Source: {source_path}")
            print(f"   📦 Destination: {destination_name}")

            # Create blob and upload
            blob = bucket.blob(destination_name)

            # Set content type if provided
            if 'content_type' in kwargs:
                blob.content_type = kwargs['content_type']

            # Set metadata if provided
            if 'metadata' in kwargs:
                blob.metadata = kwargs['metadata']

            # Upload file
            blob.upload_from_filename(source_path)

            print(f"✅ File uploaded successfully")
            print(f"   📊 Size: {blob.size} bytes")
            print(f"   🔗 URI: gs://{bucket_name}/{destination_name}")

            return {
                'bucket_name': bucket_name,
                'object_name': destination_name,
                'size': blob.size,
                'content_type': blob.content_type,
                'uri': f"gs://{bucket_name}/{destination_name}",
                'public_url': blob.public_url,
                'uploaded': True
            }

        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        destination_path: str
    ) -> Dict[str, Any]:
        """Download a file from bucket"""
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                raise Exception(f"Bucket '{bucket_name}' not found")

            blob = bucket.blob(object_name)
            if not blob.exists():
                raise Exception(f"Object '{object_name}' not found in bucket")

            print(f"📥 Downloading file from bucket: {bucket_name}")
            print(f"   📦 Source: {object_name}")
            print(f"   📁 Destination: {destination_path}")

            # Create destination directory if needed
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            # Download file
            blob.download_to_filename(destination_path)

            print(f"✅ File downloaded successfully")
            print(f"   📊 Size: {blob.size} bytes")

            return {
                'bucket_name': bucket_name,
                'object_name': object_name,
                'local_path': destination_path,
                'size': blob.size,
                'downloaded': True
            }

        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")

    def list_objects(self, bucket_name: str, prefix: str = None) -> List[Dict[str, Any]]:
        """List objects in bucket with optional prefix filter"""
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                raise Exception(f"Bucket '{bucket_name}' not found")

            blobs = bucket.list_blobs(prefix=prefix)
            objects = []

            for blob in blobs:
                objects.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created.isoformat() if blob.time_created else None,
                    'updated': blob.updated.isoformat() if blob.updated else None,
                    'uri': f"gs://{bucket_name}/{blob.name}",
                    'public_url': blob.public_url
                })

            return objects

        except Exception as e:
            raise Exception(f"Failed to list objects: {str(e)}")

    def make_public(self, bucket_name: str, object_name: str = None) -> Dict[str, Any]:
        """
        Make bucket or specific object publicly accessible.

        Args:
            bucket_name: Bucket name
            object_name: Specific object (if None, makes entire bucket public)

        Returns:
            Dict containing public access information
        """
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                raise Exception(f"Bucket '{bucket_name}' not found")

            if object_name:
                # Make specific object public
                blob = bucket.blob(object_name)
                if not blob.exists():
                    raise Exception(f"Object '{object_name}' not found")

                blob.make_public()
                print(f"✅ Object made public: gs://{bucket_name}/{object_name}")
                print(f"   🔗 Public URL: {blob.public_url}")

                return {
                    'bucket_name': bucket_name,
                    'object_name': object_name,
                    'public_url': blob.public_url,
                    'public': True
                }
            else:
                # Make entire bucket public (remove public access prevention)
                bucket.iam_configuration.public_access_prevention = "inherited"
                bucket.patch()

                # Add public read policy
                policy = bucket.get_iam_policy(requested_policy_version=3)
                policy.bindings.append({
                    "role": "roles/storage.objectViewer",
                    "members": {"allUsers"}
                })
                bucket.set_iam_policy(policy)

                print(f"✅ Bucket made public: {bucket_name}")
                print(f"   ⚠️  All objects are now publicly readable")

                return {
                    'bucket_name': bucket_name,
                    'public': True,
                    'warning': 'All objects in bucket are now publicly readable'
                }

        except Exception as e:
            raise Exception(f"Failed to make public: {str(e)}")

    def _get_bucket(self, bucket_name: str) -> Optional[storage.Bucket]:
        """Get bucket by name"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.reload()  # Check if bucket exists
            return bucket
        except NotFound:
            return None
        except Exception:
            return None

    def _bucket_to_dict(self, bucket: storage.Bucket, config: BucketConfig = None) -> Dict[str, Any]:
        """Convert bucket object to dictionary"""
        return {
            'name': bucket.name,
            'location': bucket.location,
            'storage_class': bucket.storage_class,
            'created': bucket.time_created.isoformat() if bucket.time_created else None,
            'updated': bucket.updated.isoformat() if bucket.updated else None,
            'versioning_enabled': bucket.versioning_enabled,
            'public_access_prevention': bucket.iam_configuration.public_access_prevention,
            'uniform_bucket_level_access': bucket.iam_configuration.uniform_bucket_level_access_enabled,
            'labels': bucket.labels or {},
            'uri': f"gs://{bucket.name}",
            'project_id': self.project_id,
            'self_link': bucket.self_link
        }

    def _apply_lifecycle_rules(self, bucket: storage.Bucket, rules: List[Dict[str, Any]]):
        """Apply lifecycle rules to bucket"""
        try:
            print(f"📋 Applying {len(rules)} lifecycle rules...")
            bucket.lifecycle_rules = rules
            bucket.patch()
            print(f"✅ Lifecycle rules applied")
        except Exception as e:
            print(f"⚠️  Failed to apply lifecycle rules: {e}")

    def _apply_cors_rules(self, bucket: storage.Bucket, rules: List[Dict[str, Any]]):
        """Apply CORS rules to bucket"""
        try:
            print(f"🌐 Applying {len(rules)} CORS rules...")
            bucket.cors = rules
            bucket.patch()
            print(f"✅ CORS rules applied")
        except Exception as e:
            print(f"⚠️  Failed to apply CORS rules: {e}")

    def get_smart_lifecycle_rules(self, bucket_type: str = "general") -> List[Dict[str, Any]]:
        """
        Get smart lifecycle rules based on bucket type (Rails convention).

        Args:
            bucket_type: Type of bucket ("general", "logs", "backup", "temp")

        Returns:
            List of lifecycle rules
        """
        if bucket_type == "logs":
            return [
                {
                    "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                    "condition": {"age": 30}
                },
                {
                    "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                    "condition": {"age": 90}
                },
                {
                    "action": {"type": "Delete"},
                    "condition": {"age": 365}
                }
            ]
        elif bucket_type == "backup":
            return [
                {
                    "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                    "condition": {"age": 90}
                },
                {
                    "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
                    "condition": {"age": 365}
                }
            ]
        elif bucket_type == "temp":
            return [
                {
                    "action": {"type": "Delete"},
                    "condition": {"age": 7}
                }
            ]
        else:  # general
            return [
                {
                    "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                    "condition": {"age": 30}
                }
            ]

    def get_smart_cors_rules(self, cors_type: str = "web") -> List[Dict[str, Any]]:
        """
        Get smart CORS rules based on use case (Rails convention).

        Args:
            cors_type: Type of CORS ("web", "api", "cdn")

        Returns:
            List of CORS rules
        """
        if cors_type == "api":
            return [
                {
                    "origin": ["*"],
                    "method": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "responseHeader": ["Content-Type", "Authorization"],
                    "maxAgeSeconds": 3600
                }
            ]
        elif cors_type == "cdn":
            return [
                {
                    "origin": ["*"],
                    "method": ["GET", "HEAD"],
                    "responseHeader": ["Content-Type", "Cache-Control"],
                    "maxAgeSeconds": 86400
                }
            ]
        else:  # web
            return [
                {
                    "origin": ["*"],
                    "method": ["GET", "POST", "OPTIONS"],
                    "responseHeader": ["Content-Type"],
                    "maxAgeSeconds": 3600
                }
            ]
