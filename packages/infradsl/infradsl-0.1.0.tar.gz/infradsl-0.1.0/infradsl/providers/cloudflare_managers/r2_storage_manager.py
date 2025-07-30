"""
Cloudflare R2 Storage Manager

Handles Cloudflare R2 S3-compatible object storage operations with the Cloudflare API.
Provides methods for creating, managing, and monitoring R2 buckets.
"""

import os
import requests
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional


class R2StorageManager:
    """Manager for Cloudflare R2 Storage operations"""

    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.r2_access_key_id = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
        self.r2_secret_access_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for authentication"""
        if not self.api_token:
            raise ValueError("Cloudflare API token required for R2 operations")
        
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _get_account_id(self) -> str:
        """Get account ID"""
        if self.account_id:
            return self.account_id
        
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/accounts", headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()["result"]
            if accounts:
                return accounts[0]["id"]
        
        raise ValueError("Cloudflare account not found")

    def _get_s3_client(self):
        """Get S3-compatible client for R2"""
        if not self.r2_access_key_id or not self.r2_secret_access_key:
            raise ValueError("R2 access credentials required for S3 operations")
        
        account_id = self._get_account_id()
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        
        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=self.r2_access_key_id,
            aws_secret_access_key=self.r2_secret_access_key,
            region_name='auto'
        )

    def create_bucket(self, bucket_name: str, location: str, public_access: bool,
                      website_hosting: bool, index_document: str, error_document: str,
                      custom_domain: Optional[str], cors_rules: List[Dict],
                      lifecycle_rules: List[Dict], event_notifications: List[Dict]) -> Dict[str, Any]:
        """Create R2 bucket"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            s3_client = self._get_s3_client()
            
            # Create bucket using S3 API
            try:
                s3_client.create_bucket(Bucket=bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise Exception(f"Failed to create bucket: {str(e)}")
            
            # Configure public access if requested
            if public_access:
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }
                
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=str(bucket_policy).replace("'", '"')
                )
            
            # Configure website hosting
            if website_hosting:
                s3_client.put_bucket_website(
                    Bucket=bucket_name,
                    WebsiteConfiguration={
                        'IndexDocument': {'Suffix': index_document},
                        'ErrorDocument': {'Key': error_document}
                    }
                )
            
            # Configure CORS
            if cors_rules:
                cors_configuration = {'CORSRules': []}
                for rule in cors_rules:
                    cors_configuration['CORSRules'].append({
                        'AllowedOrigins': rule['allowed_origins'],
                        'AllowedMethods': rule['allowed_methods'],
                        'AllowedHeaders': rule.get('allowed_headers', []),
                        'MaxAgeSeconds': rule.get('max_age', 3600)
                    })
                
                s3_client.put_bucket_cors(
                    Bucket=bucket_name,
                    CORSConfiguration=cors_configuration
                )
            
            # Configure lifecycle rules
            if lifecycle_rules:
                lifecycle_configuration = {'Rules': []}
                for i, rule in enumerate(lifecycle_rules):
                    lifecycle_rule = {
                        'ID': f'Rule{i}',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': rule.get('prefix', '')},
                    }
                    
                    if rule['type'] == 'expire':
                        lifecycle_rule['Expiration'] = {'Days': rule['days']}
                    elif rule['type'] == 'delete':
                        lifecycle_rule['Expiration'] = {'Days': rule['days']}
                    
                    lifecycle_configuration['Rules'].append(lifecycle_rule)
                
                s3_client.put_bucket_lifecycle_configuration(
                    Bucket=bucket_name,
                    LifecycleConfiguration=lifecycle_configuration
                )
            
            # Configure custom domain using Cloudflare API
            custom_domain_result = None
            if custom_domain:
                custom_domain_result = self._configure_custom_domain(account_id, bucket_name, custom_domain, headers)
            
            return {
                "bucket_name": bucket_name,
                "account_id": account_id,
                "location": location,
                "public_access": public_access,
                "website_hosting": website_hosting,
                "custom_domain": custom_domain_result,
                "cors_rules_count": len(cors_rules),
                "lifecycle_rules_count": len(lifecycle_rules),
                "status": "created"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create R2 bucket: {str(e)}")

    def _configure_custom_domain(self, account_id: str, bucket_name: str, custom_domain: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Configure custom domain for R2 bucket"""
        try:
            # Create custom domain mapping
            response = requests.post(
                f"{self.base_url}/accounts/{account_id}/r2/buckets/{bucket_name}/custom_domains",
                headers=headers,
                json={"domain": custom_domain}
            )
            
            if response.status_code in [200, 201]:
                return response.json()["result"]
            else:
                raise Exception(f"Failed to configure custom domain: {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to configure custom domain: {str(e)}")

    def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Delete R2 bucket"""
        try:
            s3_client = self._get_s3_client()
            
            # Delete all objects in bucket first
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects:
                    delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
                    if delete_keys:
                        s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': delete_keys}
                        )
            except ClientError:
                pass  # Bucket might be empty
            
            # Delete bucket
            s3_client.delete_bucket(Bucket=bucket_name)
            
            return {
                "bucket_name": bucket_name,
                "status": "deleted"
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete R2 bucket: {str(e)}")

    def get_bucket_status(self, bucket_name: str) -> Dict[str, Any]:
        """Get R2 bucket status"""
        try:
            s3_client = self._get_s3_client()
            
            # Get bucket location
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                location_constraint = location.get('LocationConstraint', 'auto')
            except ClientError:
                location_constraint = 'unknown'
            
            # Get bucket policy (public access)
            public_access = False
            try:
                s3_client.get_bucket_policy(Bucket=bucket_name)
                public_access = True
            except ClientError:
                pass
            
            # Get website configuration
            website_hosting = False
            website_config = None
            try:
                website_config = s3_client.get_bucket_website(Bucket=bucket_name)
                website_hosting = True
            except ClientError:
                pass
            
            # Get CORS configuration
            cors_rules = []
            try:
                cors_config = s3_client.get_bucket_cors(Bucket=bucket_name)
                cors_rules = cors_config.get('CORSRules', [])
            except ClientError:
                pass
            
            # Get lifecycle configuration
            lifecycle_rules = []
            try:
                lifecycle_config = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                lifecycle_rules = lifecycle_config.get('Rules', [])
            except ClientError:
                pass
            
            # Count objects
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name)
                object_count = objects.get('KeyCount', 0)
                total_size = sum(obj.get('Size', 0) for obj in objects.get('Contents', []))
            except ClientError:
                object_count = 0
                total_size = 0
            
            return {
                "bucket_name": bucket_name,
                "location": location_constraint,
                "public_access": public_access,
                "website_hosting": website_hosting,
                "website_config": website_config,
                "cors_rules": cors_rules,
                "lifecycle_rules": lifecycle_rules,
                "object_count": object_count,
                "total_size_bytes": total_size,
                "status": "active"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get R2 bucket status: {str(e)}")

    def upload_file(self, bucket_name: str, local_path: str, object_key: str) -> Dict[str, Any]:
        """Upload file to R2 bucket"""
        try:
            s3_client = self._get_s3_client()
            
            # Upload file
            s3_client.upload_file(local_path, bucket_name, object_key)
            
            # Get object info
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            
            return {
                "bucket_name": bucket_name,
                "object_key": object_key,
                "local_path": local_path,
                "size": response['ContentLength'],
                "etag": response['ETag'],
                "last_modified": response['LastModified'].isoformat(),
                "status": "uploaded"
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def list_objects(self, bucket_name: str, prefix: str = "") -> Dict[str, Any]:
        """List objects in R2 bucket"""
        try:
            s3_client = self._get_s3_client()
            
            kwargs = {'Bucket': bucket_name}
            if prefix:
                kwargs['Prefix'] = prefix
            
            response = s3_client.list_objects_v2(**kwargs)
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'],
                    'storage_class': obj.get('StorageClass', 'STANDARD')
                })
            
            return {
                "bucket_name": bucket_name,
                "prefix": prefix,
                "object_count": len(objects),
                "objects": objects,
                "truncated": response.get('IsTruncated', False),
                "status": "listed"
            }
            
        except Exception as e:
            raise Exception(f"Failed to list objects: {str(e)}") 