import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import json
import os


class S3LifecycleMixin:
    """
    Mixin for S3 bucket lifecycle operations (create, update, destroy, uploads).
    """
    def create(self) -> Dict[str, Any]:
        """Create/update S3 bucket and remove any that are no longer needed"""
        self._ensure_authenticated()
        
        if not self.bucket_name:
            raise ValueError("Bucket name is required. Use .bucket_name('your-bucket-name')")
        
        try:
            # Initialize S3 client if not already done
            if not self.s3_client:
                self.s3_client = self.get_s3_client(self.region_name)
                self.s3_resource = self.get_s3_resource(self.region_name)
            
            # Check if bucket exists
            bucket_exists = self._bucket_exists()
            
            if not bucket_exists:
                # Create bucket
                self._create_bucket()
                print(f"✅ Created S3 bucket: {self.bucket_name}")
            else:
                print(f"📦 S3 bucket exists: {self.bucket_name}")
            
            # Configure bucket settings
            self._configure_bucket()
            
            # Process any file uploads
            if self._files_to_upload or self._directories_to_upload:
                self._process_file_uploads()
            
            # Get bucket info for return
            bucket_info = self._get_bucket_info()
            
            # Cache state for drift detection
            self._cache_resource_state(
                resource_config={
                    "bucket_name": self.bucket_name,
                    "region": self.region_name,
                    "storage_class": self.storage_class,
                    "public_access": self.public_access,
                    "versioning_enabled": self.versioning_enabled,
                    "encryption_enabled": self.encryption_enabled,
                    "website_enabled": self.website_enabled,
                    "cors_enabled": self.cors_enabled,
                    "lifecycle_rules": self.lifecycle_rules
                },
                current_state=bucket_info
            )
            
            return bucket_info
            
        except Exception as e:
            print(f"❌ Error creating S3 bucket: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the S3 bucket"""
        self._ensure_authenticated()
        
        if not self.bucket_name:
            raise ValueError("Bucket name is required to destroy bucket")
        
        try:
            if not self.s3_client:
                self.s3_client = self.get_s3_client(self.region_name)
                self.s3_resource = self.get_s3_resource(self.region_name)
            
            # Check if bucket exists
            if not self._bucket_exists():
                print(f"⚠️ Bucket {self.bucket_name} does not exist")
                return {"status": "not_found", "bucket_name": self.bucket_name}
            
            # Delete all objects in bucket first
            self._empty_bucket()
            
            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=self.bucket_name)
            print(f"🗑️ Destroyed S3 bucket: {self.bucket_name}")
            
            return {
                "status": "destroyed",
                "bucket_name": self.bucket_name,
                "region": self.region_name
            }
            
        except Exception as e:
            print(f"❌ Error destroying S3 bucket: {str(e)}")
            raise

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        return {
            "resource_type": "AWS S3 Bucket",
            "bucket_name": self.bucket_name,
            "region": self.region_name or "us-east-1",
            "storage_class": self.storage_class,
            "public_access": self.public_access,
            "versioning_enabled": self.versioning_enabled,
            "encryption_enabled": self.encryption_enabled,
            "website_enabled": self.website_enabled,
            "cors_enabled": self.cors_enabled,
            "lifecycle_rules_count": len(self.lifecycle_rules),
            "files_to_upload": len(self._files_to_upload),
            "directories_to_upload": len(self._directories_to_upload),
            "estimated_cost": self._estimate_storage_cost()
        }

    def _process_file_uploads(self):
        """Process queued file uploads"""
        if not self.s3_client:
            return
        
        # Upload individual files
        for file_info in self._files_to_upload:
            self._upload_file(
                file_info['local_path'],
                file_info.get('s3_key', os.path.basename(file_info['local_path'])),
                file_info.get('storage_class', self.storage_class)
            )
        
        # Upload directories
        for dir_info in self._directories_to_upload:
            self._upload_directory(
                dir_info['local_path'],
                dir_info.get('s3_prefix', ''),
                dir_info.get('storage_class', self.storage_class)
            )

    def _create_bucket(self):
        """Create the S3 bucket"""
        create_params = {'Bucket': self.bucket_name}
        
        # Add location constraint for regions other than us-east-1
        if self.region_name and self.region_name != 'us-east-1':
            create_params['CreateBucketConfiguration'] = {
                'LocationConstraint': self.region_name
            }
        
        self.s3_client.create_bucket(**create_params)

    def _configure_bucket(self):
        """Configure bucket settings"""
        # Configure versioning
        if self.versioning_enabled:
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
        
        # Configure encryption
        if self.encryption_enabled:
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
        
        # Configure public access block
        if not self.public_access:
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        
        # Configure website hosting
        if self.website_enabled:
            self._configure_website()
        
        # Configure CORS
        if self.cors_enabled:
            self._configure_cors()
        
        # Configure lifecycle rules
        if self.lifecycle_rules:
            self._configure_lifecycle()

    def _bucket_exists(self) -> bool:
        """Check if bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            raise

    def _empty_bucket(self):
        """Empty all objects from bucket before deletion"""
        bucket = self.s3_resource.Bucket(self.bucket_name)
        
        # Delete all object versions
        bucket.object_versions.delete()
        
        # Delete all objects
        bucket.objects.delete()

    def _get_bucket_info(self) -> Dict[str, Any]:
        """Get bucket information"""
        try:
            location = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            region = location.get('LocationConstraint') or 'us-east-1'
            
            # Get bucket URL
            bucket_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com"
            if region == 'us-east-1':
                bucket_url = f"https://{self.bucket_name}.s3.amazonaws.com"
            
            # Get website URL if website hosting is enabled
            website_url = None
            if self.website_enabled:
                website_url = f"http://{self.bucket_name}.s3-website-{region}.amazonaws.com"
                if region == 'us-east-1':
                    website_url = f"http://{self.bucket_name}.s3-website.amazonaws.com"
            
            return {
                "bucket_name": self.bucket_name,
                "region": region,
                "bucket_url": bucket_url,
                "website_url": website_url,
                "bucket_arn": f"arn:aws:s3:::{self.bucket_name}",
                "storage_class": self.storage_class,
                "public_access": self.public_access,
                "versioning_enabled": self.versioning_enabled,
                "encryption_enabled": self.encryption_enabled,
                "website_enabled": self.website_enabled,
                "cors_enabled": self.cors_enabled
            }
        except Exception as e:
            return {"error": str(e)}

    def _upload_file(self, local_path: str, s3_key: str, storage_class: str = None):
        """Upload a single file to S3"""
        try:
            extra_args = {}
            if storage_class:
                extra_args['StorageClass'] = storage_class
            
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            print(f"📤 Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
        except Exception as e:
            print(f"❌ Error uploading {local_path}: {str(e)}")

    def _upload_directory(self, local_path: str, s3_prefix: str = '', storage_class: str = None):
        """Upload a directory to S3"""
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, local_path)
                s3_key = os.path.join(s3_prefix, relative_path).replace('\\', '/')
                self._upload_file(local_file, s3_key, storage_class)

    def _configure_website(self):
        """Configure static website hosting"""
        self.s3_client.put_bucket_website(
            Bucket=self.bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'error.html'}
            }
        )

    def _configure_cors(self):
        """Configure CORS settings"""
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],
                'AllowedOrigins': ['*'],
                'MaxAgeSeconds': 3000
            }]
        }
        self.s3_client.put_bucket_cors(
            Bucket=self.bucket_name,
            CORSConfiguration=cors_configuration
        )

    def _configure_lifecycle(self):
        """Configure lifecycle rules"""
        if self.lifecycle_rules:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration={'Rules': self.lifecycle_rules}
            )

    def _estimate_storage_cost(self) -> str:
        """Estimate monthly storage cost"""
        # Simple cost estimation - this could be enhanced
        base_cost = 0.023  # USD per GB per month for Standard storage
        estimated_gb = 1  # Default estimate
        
        if self.storage_class == 'STANDARD_IA':
            base_cost = 0.0125
        elif self.storage_class == 'GLACIER':
            base_cost = 0.004
        
        return f"${base_cost * estimated_gb:.2f}/month (estimated for {estimated_gb}GB)" 