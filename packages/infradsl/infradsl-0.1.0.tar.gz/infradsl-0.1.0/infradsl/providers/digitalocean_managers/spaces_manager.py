"""
DigitalOcean Spaces Manager

Handles creation and management of DigitalOcean Spaces (object storage) with CDN integration.
"""

import os
import boto3
import mimetypes
from typing import Dict, Any, List, Optional
from pathlib import Path


class SpacesManager:
    """Manager for DigitalOcean Spaces and CDN"""

    def __init__(self, do_client):
        self.do_client = do_client
        self.client = do_client.client
        self.spaces_client = None
        self.cdn_client = None

    def _init_spaces_client(self, region: str):
        """Initialize Spaces client (S3-compatible)"""
        if not self.spaces_client:
            # Use environment variables or default credentials
            access_key = os.getenv('DIGITALOCEAN_SPACES_ACCESS_KEY') or os.getenv('DO_SPACES_ACCESS_KEY')
            secret_key = os.getenv('DIGITALOCEAN_SPACES_SECRET_KEY') or os.getenv('DO_SPACES_SECRET_KEY')
            
            if not access_key or not secret_key:
                raise ValueError(
                    "DigitalOcean Spaces credentials not found. Please set:\n"
                    "DIGITALOCEAN_SPACES_ACCESS_KEY and DIGITALOCEAN_SPACES_SECRET_KEY\n"
                    "or DO_SPACES_ACCESS_KEY and DO_SPACES_SECRET_KEY"
                )
            
            self.spaces_client = boto3.client(
                's3',
                region_name=region,
                endpoint_url=f'https://{region}.digitaloceanspaces.com',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )

    def preview_spaces_cdn(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview Spaces CDN configuration"""
        # Check if Space already exists
        existing_space = self._find_space_by_name(config["name"], config["region"])
        existing_cdn = self._find_cdn_by_origin(config["name"], config["region"])
        
        preview = {
            "action": "UPDATE" if existing_space else "CREATE",
            "name": config["name"],
            "region": config["region"],
            "acl": config["acl"],
            "versioning_enabled": config["versioning_enabled"],
            "cdn_enabled": config["cdn_enabled"],
            "cdn_domain": config.get("cdn_domain"),
            "cdn_ttl": config["cdn_ttl"],
            "cors_rules": len(config.get("cors_rules", [])),
            "lifecycle_rules": len(config.get("lifecycle_rules", [])),
            "tags": config.get("tags", []),
            "existing_space": bool(existing_space),
            "existing_cdn": bool(existing_cdn)
        }

        if existing_space:
            preview["space_endpoint"] = self._get_space_endpoint(config["name"], config["region"])
        
        if existing_cdn:
            preview["cdn_endpoint"] = existing_cdn.get("endpoint")

        self._print_spaces_preview(preview)
        return preview

    def create_spaces_cdn(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Spaces bucket with CDN configuration"""
        try:
            self._init_spaces_client(config["region"])
            
            # Check if Space already exists
            existing_space = self._find_space_by_name(config["name"], config["region"])
            
            if existing_space:
                print(f"🔄 Space '{config['name']}' already exists, updating configuration...")
                result = self._update_existing_space(config)
            else:
                print(f"🚀 Creating new Space...")
                result = self._create_new_space(config)
            
            # Handle CDN if enabled
            if config["cdn_enabled"]:
                cdn_result = self._setup_cdn(config, result)
                result.update(cdn_result)
            
            self._print_spaces_result(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create Spaces CDN: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}

    def destroy_spaces_cdn(self, name: str) -> Dict[str, Any]:
        """Destroy Spaces bucket and CDN"""
        try:
            destroyed_resources = {
                "space": False,
                "cdn": False
            }
            
            # Find and destroy CDN first
            cdns = self.client.get_all_cdn_endpoints()
            for cdn in cdns:
                if name in cdn.origin:
                    print(f"🗑️  Destroying CDN endpoint...")
                    cdn.destroy()
                    destroyed_resources["cdn"] = True
                    break
            
            # Find and destroy Space
            # Note: We need to empty the bucket first before destroying it
            try:
                # List all regions to find the space
                regions = ["nyc3", "ams3", "sgp1", "fra1", "sfo3"]
                space_found = False
                
                for region in regions:
                    try:
                        self._init_spaces_client(region)
                        
                        # Check if bucket exists in this region
                        self.spaces_client.head_bucket(Bucket=name)
                        
                        print(f"🗑️  Emptying Space contents...")
                        # Empty the bucket first
                        objects = self.spaces_client.list_objects_v2(Bucket=name).get('Contents', [])
                        if objects:
                            delete_keys = [{'Key': obj['Key']} for obj in objects]
                            self.spaces_client.delete_objects(
                                Bucket=name,
                                Delete={'Objects': delete_keys}
                            )
                        
                        # Delete the bucket
                        print(f"🗑️  Destroying Space...")
                        self.spaces_client.delete_bucket(Bucket=name)
                        destroyed_resources["space"] = True
                        space_found = True
                        break
                        
                    except Exception:
                        continue
                
                if not space_found:
                    print(f"⚠️  Space '{name}' not found")
                    
            except Exception as e:
                print(f"⚠️  Error destroying Space: {e}")
            
            success = destroyed_resources["space"] or destroyed_resources["cdn"]
            return {
                "success": success,
                "name": name,
                "destroyed_resources": destroyed_resources,
                "message": "Spaces CDN destruction completed"
            }
            
        except Exception as e:
            error_msg = f"Failed to destroy Spaces CDN: {str(e)}"
            return {"error": error_msg, "success": False}

    def upload_file(self, space_name: str, file_path: str, key: Optional[str] = None, 
                   content_type: Optional[str] = None, public: bool = True) -> Dict[str, Any]:
        """Upload file to Space"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Use filename if key not provided
            if not key:
                key = os.path.basename(file_path)
            
            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'binary/octet-stream'
            
            # Upload parameters
            extra_args = {'ContentType': content_type}
            if public:
                extra_args['ACL'] = 'public-read'
            
            # Perform upload
            with open(file_path, 'rb') as file_data:
                self.spaces_client.upload_fileobj(
                    file_data,
                    space_name,
                    key,
                    ExtraArgs=extra_args
                )
            
            # Build result
            space_endpoint = self._get_space_endpoint(space_name, "nyc3")  # Default region
            file_url = f"{space_endpoint}/{key}"
            
            return {
                "success": True,
                "key": key,
                "url": file_url,
                "content_type": content_type,
                "public": public,
                "size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

    def upload_directory(self, space_name: str, directory_path: str, 
                        prefix: str = "", public: bool = True) -> Dict[str, Any]:
        """Upload entire directory to Space"""
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            uploaded_files = []
            total_size = 0
            
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Calculate relative path for key
                    relative_path = os.path.relpath(file_path, directory_path)
                    key = os.path.join(prefix, relative_path).replace(os.sep, '/')
                    
                    # Upload file
                    result = self.upload_file(space_name, file_path, key, public=public)
                    
                    if result.get("success"):
                        uploaded_files.append(result)
                        total_size += result.get("size", 0)
                    else:
                        print(f"⚠️  Failed to upload {file_path}: {result.get('error')}")
            
            return {
                "success": True,
                "uploaded_files": len(uploaded_files),
                "total_size": total_size,
                "prefix": prefix,
                "files": uploaded_files
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

    def _find_space_by_name(self, name: str, region: str) -> Optional[Dict[str, Any]]:
        """Find Space by name"""
        try:
            self._init_spaces_client(region)
            self.spaces_client.head_bucket(Bucket=name)
            return {"name": name, "region": region}
        except Exception:
            return None

    def _find_cdn_by_origin(self, space_name: str, region: str) -> Optional[Dict[str, Any]]:
        """Find CDN endpoint by origin"""
        try:
            cdns = self.client.get_all_cdn_endpoints()
            origin = f"{space_name}.{region}.digitaloceanspaces.com"
            
            for cdn in cdns:
                if origin in cdn.origin:
                    return {
                        "id": cdn.id,
                        "endpoint": cdn.endpoint,
                        "origin": cdn.origin,
                        "ttl": cdn.ttl
                    }
            return None
        except Exception:
            return None

    def _create_new_space(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new Space"""
        # Create the bucket
        if config["region"] == "nyc3":
            self.spaces_client.create_bucket(Bucket=config["name"])
        else:
            self.spaces_client.create_bucket(
                Bucket=config["name"],
                CreateBucketConfiguration={'LocationConstraint': config["region"]}
            )
        
        # Configure bucket settings
        self._configure_space_settings(config)
        
        space_endpoint = self._get_space_endpoint(config["name"], config["region"])
        
        return {
            "name": config["name"],
            "region": config["region"],
            "endpoint": space_endpoint,
            "acl": config["acl"],
            "created": True,
            "versioning_enabled": config["versioning_enabled"],
            "cors_rules": len(config.get("cors_rules", [])),
            "lifecycle_rules": len(config.get("lifecycle_rules", []))
        }

    def _update_existing_space(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing Space configuration"""
        self._configure_space_settings(config)
        
        space_endpoint = self._get_space_endpoint(config["name"], config["region"])
        
        return {
            "name": config["name"],
            "region": config["region"],
            "endpoint": space_endpoint,
            "acl": config["acl"],
            "updated": True,
            "versioning_enabled": config["versioning_enabled"],
            "cors_rules": len(config.get("cors_rules", [])),
            "lifecycle_rules": len(config.get("lifecycle_rules", []))
        }

    def _configure_space_settings(self, config: Dict[str, Any]):
        """Configure Space settings (versioning, CORS, lifecycle)"""
        bucket_name = config["name"]
        
        # Configure versioning
        if config["versioning_enabled"]:
            self.spaces_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
        
        # Configure CORS
        if config.get("cors_rules"):
            cors_config = {
                'CORSRules': []
            }
            
            for rule in config["cors_rules"]:
                cors_rule = {
                    'AllowedOrigins': rule["allowed_origins"],
                    'AllowedMethods': rule["allowed_methods"],
                    'AllowedHeaders': rule["allowed_headers"],
                    'MaxAgeSeconds': rule["max_age_seconds"]
                }
                cors_config['CORSRules'].append(cors_rule)
            
            self.spaces_client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_config
            )
        
        # Configure lifecycle
        if config.get("lifecycle_rules"):
            lifecycle_config = {
                'Rules': []
            }
            
            for rule in config["lifecycle_rules"]:
                lifecycle_rule = {
                    'ID': rule["id"],
                    'Status': rule["status"],
                    'Filter': {'Prefix': rule["prefix"]}
                }
                
                if rule.get("expiration"):
                    lifecycle_rule['Expiration'] = rule["expiration"]
                
                if rule.get("noncurrent_version_expiration"):
                    lifecycle_rule['NoncurrentVersionExpiration'] = rule["noncurrent_version_expiration"]
                
                if rule.get("abort_incomplete_multipart_upload"):
                    lifecycle_rule['AbortIncompleteMultipartUpload'] = rule["abort_incomplete_multipart_upload"]
                
                lifecycle_config['Rules'].append(lifecycle_rule)
            
            self.spaces_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )

    def _setup_cdn(self, config: Dict[str, Any], space_result: Dict[str, Any]) -> Dict[str, Any]:
        """Setup CDN for the Space"""
        try:
            origin = f"{config['name']}.{config['region']}.digitaloceanspaces.com"
            
            # Check if CDN already exists
            existing_cdn = self._find_cdn_by_origin(config["name"], config["region"])
            
            if existing_cdn:
                print(f"🔄 CDN already exists, updating configuration...")
                return {
                    "cdn_enabled": True,
                    "cdn_endpoint": existing_cdn["endpoint"],
                    "cdn_origin": existing_cdn["origin"],
                    "cdn_ttl": existing_cdn["ttl"],
                    "cdn_updated": True
                }
            
            print(f"🌐 Creating CDN endpoint...")
            
            # Create CDN endpoint
            cdn_params = {
                "origin": origin,
                "ttl": config["cdn_ttl"]
            }
            
            if config.get("cdn_domain"):
                cdn_params["custom_domain"] = config["cdn_domain"]
            
            if config.get("cdn_certificate_id"):
                cdn_params["certificate_id"] = config["cdn_certificate_id"]
            
            # Create CDN using DigitalOcean API
            cdn_data = {
                "origin": origin,
                "ttl": config["cdn_ttl"]
            }
            
            response = self.client._perform_request("POST", "/v2/cdn/endpoints", cdn_data)
            cdn_info = response["endpoint"]
            
            return {
                "cdn_enabled": True,
                "cdn_endpoint": cdn_info["endpoint"],
                "cdn_origin": cdn_info["origin"],
                "cdn_ttl": cdn_info["ttl"],
                "cdn_created": True
            }
            
        except Exception as e:
            print(f"⚠️  Failed to setup CDN: {e}")
            return {
                "cdn_enabled": False,
                "cdn_error": str(e)
            }

    def _get_space_endpoint(self, name: str, region: str) -> str:
        """Get Space endpoint URL"""
        return f"https://{name}.{region}.digitaloceanspaces.com"

    def _print_spaces_preview(self, preview: Dict[str, Any]):
        """Print formatted Spaces preview"""
        print(f"\n╭─ 🪣 Spaces CDN Preview: {preview['name']}")
        print(f"├─ 🔧 Action: {preview['action']}")
        print(f"├─ 📍 Region: {preview['region']}")
        print(f"├─ 🔒 Access: {preview['acl']}")
        print(f"├─ 📦 Versioning: {'Enabled' if preview['versioning_enabled'] else 'Disabled'}")
        print(f"├─ 🌐 CDN: {'Enabled' if preview['cdn_enabled'] else 'Disabled'}")
        
        if preview['cdn_enabled']:
            if preview.get('cdn_domain'):
                print(f"├─ 🌍 Custom Domain: {preview['cdn_domain']}")
            print(f"├─ ⏱️  TTL: {preview['cdn_ttl']} seconds")
        
        if preview['cors_rules'] > 0:
            print(f"├─ 🔄 CORS Rules: {preview['cors_rules']}")
        
        if preview['lifecycle_rules'] > 0:
            print(f"├─ ♻️  Lifecycle Rules: {preview['lifecycle_rules']}")
        
        if preview.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(preview['tags'])}")
        
        if preview['existing_space']:
            print(f"├─ 📊 Space Exists: {preview.get('space_endpoint', 'Yes')}")
        
        if preview['existing_cdn']:
            print(f"├─ 🌐 CDN Exists: {preview.get('cdn_endpoint', 'Yes')}")
        
        print(f"╰─ 🎯 Action: {'Update existing resources' if preview['existing_space'] else 'Create new Spaces CDN'}")

    def _print_spaces_result(self, result: Dict[str, Any]):
        """Print formatted Spaces creation result"""
        print(f"\n╭─ 🪣 Spaces: {result['name']}")
        print(f"├─ 📍 Region: {result['region']}")
        print(f"├─ 🔗 Endpoint: {result['endpoint']}")
        print(f"├─ 🔒 Access: {result['acl']}")
        print(f"├─ 📦 Versioning: {'Enabled' if result['versioning_enabled'] else 'Disabled'}")
        
        if result.get('cors_rules', 0) > 0:
            print(f"├─ 🔄 CORS Rules: {result['cors_rules']}")
        
        if result.get('lifecycle_rules', 0) > 0:
            print(f"├─ ♻️  Lifecycle Rules: {result['lifecycle_rules']}")
        
        if result.get('cdn_enabled'):
            print(f"├─ 🌐 CDN Enabled: {result['cdn_endpoint']}")
            print(f"├─ 🌍 CDN Origin: {result['cdn_origin']}")
            print(f"├─ ⏱️  CDN TTL: {result['cdn_ttl']} seconds")
        
        action = "Created" if result.get('created') else "Updated"
        print(f"╰─ ✨ Action: {action} Spaces CDN")