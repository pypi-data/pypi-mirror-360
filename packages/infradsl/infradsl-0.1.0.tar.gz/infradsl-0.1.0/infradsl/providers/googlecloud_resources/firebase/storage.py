"""
Firebase Storage Resource for InfraDSL
File storage with security rules and CDN

Features:
- File upload and download
- Security rules
- CDN distribution
- Image transformations
- Backup and versioning
"""

import json
import subprocess
from typing import Dict, List, Optional, Any
from ..base_resource import BaseGcpResource


class FirebaseStorage(BaseGcpResource):
    """
    Firebase Storage for file management
    
    Example:
        storage = (FirebaseStorage("my-app-storage")
                  .project("my-project")
                  .location("us-central1")
                  .bucket("my-app-files")
                  .public_access(True)
                  .security_rules("rules/storage.rules"))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._project_id = None
        self._location = "us-central1"
        self._bucket_name = None
        self._public_access = False
        self._security_rules = None
        self._cors_config = None
        self._lifecycle_rules = []
        
    def _initialize_managers(self):
        """Initialize Firebase Storage managers"""
        # Firebase Storage doesn't require additional managers
        pass
        
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Firebase Storage doesn't require post-auth setup
        pass

    def _discover_existing_buckets(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firebase Storage buckets"""
        existing_buckets = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            if not self.gcp_client or not hasattr(self.gcp_client, 'credentials'):
                print(f"⚠️  No GCP credentials available for Firebase Storage discovery")
                return existing_buckets
            
            # Firebase Storage buckets are actually Google Cloud Storage buckets
            service = discovery.build('storage', 'v1', credentials=self.gcp_client.credentials)
            
            # Get project ID
            project_id = self._project_id or (self.gcp_client.project_id if hasattr(self.gcp_client, 'project_id') else self.gcp_client.project)
            if not project_id:
                print(f"⚠️  Project ID required for Firebase Storage discovery")
                return existing_buckets
            
            # List buckets in the project
            request = service.buckets().list(project=project_id)
            response = request.execute()
            
            buckets = response.get('items', [])
            
            for bucket in buckets:
                bucket_name = bucket.get('name', '')
                
                try:
                    # Check if this is likely a Firebase Storage bucket
                    # Firebase buckets typically end with .appspot.com or .firebaseapp.com
                    is_firebase_bucket = (
                        bucket_name.endswith('.appspot.com') or 
                        bucket_name.endswith('.firebaseapp.com') or
                        bucket_name.startswith(project_id)
                    )
                    
                    # Get detailed bucket information
                    bucket_details = service.buckets().get(bucket=bucket_name).execute()
                    
                    # Extract bucket configuration
                    location = bucket_details.get('location', 'unknown')
                    storage_class = bucket_details.get('storageClass', 'STANDARD')
                    creation_time = bucket_details.get('timeCreated', '')
                    updated_time = bucket_details.get('updated', '')
                    
                    # Get versioning configuration
                    versioning = bucket_details.get('versioning', {})
                    versioning_enabled = versioning.get('enabled', False)
                    
                    # Get CORS configuration
                    cors_config = bucket_details.get('cors', [])
                    cors_enabled = len(cors_config) > 0
                    
                    # Get lifecycle configuration
                    lifecycle = bucket_details.get('lifecycle', {})
                    lifecycle_rules = lifecycle.get('rule', [])
                    lifecycle_rule_count = len(lifecycle_rules)
                    
                    # Get IAM configuration (public access)
                    public_access = False
                    try:
                        iam_policy = service.buckets().getIamPolicy(bucket=bucket_name).execute()
                        bindings = iam_policy.get('bindings', [])
                        for binding in bindings:
                            if 'allUsers' in binding.get('members', []) or 'allAuthenticatedUsers' in binding.get('members', []):
                                public_access = True
                                break
                    except Exception:
                        pass  # IAM access might be restricted
                    
                    # Get bucket size and object count
                    bucket_size_bytes = 0
                    object_count = 0
                    try:
                        # Get bucket usage (this requires special permissions)
                        objects_request = service.objects().list(bucket=bucket_name, maxResults=1000)
                        objects_response = objects_request.execute()
                        objects = objects_response.get('items', [])
                        object_count = len(objects)
                        bucket_size_bytes = sum(int(obj.get('size', 0)) for obj in objects)
                    except Exception:
                        pass  # Objects access might be restricted
                    
                    # Calculate storage costs (simplified)
                    size_gb = bucket_size_bytes / (1024**3) if bucket_size_bytes > 0 else 0
                    
                    existing_buckets[bucket_name] = {
                        'bucket_name': bucket_name,
                        'is_firebase_bucket': is_firebase_bucket,
                        'project_id': project_id,
                        'location': location,
                        'storage_class': storage_class,
                        'creation_time': creation_time[:10] if creation_time else 'unknown',
                        'updated_time': updated_time[:10] if updated_time else 'unknown',
                        'versioning_enabled': versioning_enabled,
                        'cors_enabled': cors_enabled,
                        'cors_config': cors_config,
                        'lifecycle_rule_count': lifecycle_rule_count,
                        'lifecycle_rules': lifecycle_rules,
                        'public_access': public_access,
                        'object_count': object_count,
                        'size_bytes': bucket_size_bytes,
                        'size_gb': round(size_gb, 2),
                        'estimated_monthly_cost': round(size_gb * 0.02, 2) if size_gb > 0 else 0.0  # $0.02/GB/month for standard storage
                    }
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        continue
                    else:
                        print(f"⚠️  Failed to get details for bucket {bucket_name}: {str(e)}")
                        existing_buckets[bucket_name] = {
                            'bucket_name': bucket_name,
                            'error': str(e)
                        }
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing Firebase Storage buckets: {str(e)}")
        
        return existing_buckets
        
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self._project_id = project_id
        return self
        
    def location(self, location: str):
        """Set storage location"""
        self._location = location
        return self
        
    def bucket(self, bucket_name: str):
        """Set bucket name"""
        self._bucket_name = bucket_name
        return self
        
    def public_access(self, enabled: bool = True):
        """Enable public access to files"""
        self._public_access = enabled
        return self
        
    def security_rules(self, rules_file: str):
        """Set security rules file path"""
        self._security_rules = rules_file
        return self
        
    def cors(self, origins: List[str] = None, methods: List[str] = None):
        """Configure CORS for the bucket"""
        self._cors_config = {
            "origins": origins or ["*"],
            "methods": methods or ["GET", "POST", "PUT", "DELETE"],
            "maxAgeSeconds": 3600
        }
        return self
        
    def lifecycle_rule(self, action: str, condition: Dict[str, Any]):
        """Add lifecycle rule (delete, archive, etc.)"""
        self._lifecycle_rules.append({
            "action": action,
            "condition": condition
        })
        return self
        
    def delete_after_days(self, days: int):
        """Delete files after specified days"""
        return self.lifecycle_rule("Delete", {
            "age": days
        })
        
    def archive_after_days(self, days: int):
        """Archive files after specified days"""
        return self.lifecycle_rule("SetStorageClass", {
            "storageClass": "ARCHIVE",
            "age": days
        })

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        try:
            self._ensure_authenticated()
        except:
            # Firebase Storage can work without full GCP authentication in some cases
            pass

        # Discover existing buckets
        existing_buckets = self._discover_existing_buckets()
        
        # Categorize buckets
        buckets_to_create = []
        buckets_to_keep = []
        buckets_to_remove = []
        
        # Determine bucket name
        desired_bucket_name = self._bucket_name or f"{self._project_id}.appspot.com" if self._project_id else f"{self.name}.appspot.com"
        bucket_exists = desired_bucket_name in existing_buckets
        
        if not bucket_exists:
            buckets_to_create.append({
                'bucket_name': desired_bucket_name,
                'project_id': self._project_id,
                'location': self._location,
                'public_access': self._public_access,
                'security_rules': self._security_rules,
                'cors_config': self._cors_config,
                'cors_enabled': self._cors_config is not None,
                'lifecycle_rules': self._lifecycle_rules,
                'lifecycle_rule_count': len(self._lifecycle_rules),
                'is_firebase_bucket': True,
                'storage_class': 'STANDARD'
            })
        else:
            # Only include Firebase-related buckets in "keep" list
            if existing_buckets[desired_bucket_name].get('is_firebase_bucket', False):
                buckets_to_keep.append(existing_buckets[desired_bucket_name])

        print(f"\n📁 Firebase Storage Preview")
        
        # Show buckets to create
        if buckets_to_create:
            print(f"╭─ 📁 Storage Buckets to CREATE: {len(buckets_to_create)}")
            for bucket in buckets_to_create:
                print(f"├─ 🆕 {bucket['bucket_name']}")
                
                if bucket['project_id']:
                    print(f"│  ├─ 📋 Project: {bucket['project_id']}")
                
                print(f"│  ├─ 📍 Location: {bucket['location']}")
                print(f"│  ├─ 💾 Storage Class: {bucket['storage_class']}")
                print(f"│  ├─ 🌐 Public Access: {'✅ Enabled' if bucket['public_access'] else '❌ Disabled'}")
                
                # Show security configuration
                if bucket['security_rules']:
                    print(f"│  ├─ 🔒 Security Rules: {bucket['security_rules']}")
                else:
                    print(f"│  ├─ 🔒 Security Rules: Default (authenticated users only)")
                
                # Show CORS configuration
                if bucket['cors_enabled']:
                    cors = bucket['cors_config']
                    origins = cors.get('origins', ['*'])
                    methods = cors.get('methods', ['GET', 'POST'])
                    print(f"│  ├─ 🌍 CORS: ✅ Enabled")
                    print(f"│  │  ├─ 🌐 Origins: {', '.join(origins[:3])}" + (f" (+{len(origins)-3})" if len(origins) > 3 else ""))
                    print(f"│  │  └─ 🔧 Methods: {', '.join(methods)}")
                else:
                    print(f"│  ├─ 🌍 CORS: ❌ Disabled")
                
                # Show lifecycle rules
                if bucket['lifecycle_rule_count'] > 0:
                    print(f"│  ├─ ⏰ Lifecycle Rules: {bucket['lifecycle_rule_count']}")
                    for i, rule in enumerate(bucket['lifecycle_rules'][:3]):  # Show first 3
                        action = rule.get('action', 'unknown')
                        condition = rule.get('condition', {})
                        connector = "│  │  ├─" if i < min(len(bucket['lifecycle_rules']), 3) - 1 else "│  │  └─"
                        
                        if 'age' in condition:
                            print(f"{connector} {action} after {condition['age']} days")
                        else:
                            print(f"{connector} {action} rule")
                    
                    if len(bucket['lifecycle_rules']) > 3:
                        print(f"│  │     └─ ... and {len(bucket['lifecycle_rules']) - 3} more rules")
                else:
                    print(f"│  ├─ ⏰ Lifecycle Rules: None")
                
                # Show Firebase features
                print(f"│  ├─ 🔥 Firebase Features:")
                print(f"│  │  ├─ 📱 Mobile SDK integration")
                print(f"│  │  ├─ 🖼️  Automatic image transformations")
                print(f"│  │  ├─ 🌍 Global CDN")
                print(f"│  │  └─ 🔄 Real-time upload progress")
                
                print(f"│  └─ 🌐 Access: gs://{bucket['bucket_name']}")
            print(f"╰─")

        # Show existing buckets being kept
        if buckets_to_keep:
            print(f"\n╭─ 📁 Existing Storage Buckets to KEEP: {len(buckets_to_keep)}")
            for bucket in buckets_to_keep:
                print(f"├─ ✅ {bucket['bucket_name']}")
                print(f"│  ├─ 📋 Project: {bucket['project_id']}")
                print(f"│  ├─ 📍 Location: {bucket['location']}")
                print(f"│  ├─ 💾 Storage Class: {bucket['storage_class']}")
                print(f"│  ├─ 🌐 Public Access: {'✅ Enabled' if bucket['public_access'] else '❌ Disabled'}")
                
                # Show current usage
                if bucket['object_count'] > 0:
                    print(f"│  ├─ 📊 Objects: {bucket['object_count']:,}")
                    if bucket['size_gb'] > 0:
                        if bucket['size_gb'] < 1:
                            print(f"│  ├─ 💾 Size: {bucket['size_bytes']:,} bytes")
                        else:
                            print(f"│  ├─ 💾 Size: {bucket['size_gb']} GB")
                else:
                    print(f"│  ├─ 📊 Objects: Empty bucket")
                
                # Show configuration
                print(f"│  ├─ 🔄 Versioning: {'✅ Enabled' if bucket['versioning_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🌍 CORS: {'✅ Enabled' if bucket['cors_enabled'] else '❌ Disabled'}")
                
                if bucket['lifecycle_rule_count'] > 0:
                    print(f"│  ├─ ⏰ Lifecycle Rules: {bucket['lifecycle_rule_count']}")
                
                if bucket['estimated_monthly_cost'] > 0:
                    print(f"│  ├─ 💰 Est. Cost: ${bucket['estimated_monthly_cost']:.2f}/month")
                
                print(f"│  ├─ 📅 Created: {bucket['creation_time']}")
                print(f"│  └─ 🌐 Access: gs://{bucket['bucket_name']}")
            print(f"╰─")

        # Show cost information
        print(f"\n💰 Firebase Storage Costs:")
        if buckets_to_create:
            bucket = buckets_to_create[0]
            print(f"   ├─ 📁 Storage: Free tier (5GB)")
            print(f"   ├─ 📡 Downloads: Free tier (1GB/day)")
            print(f"   ├─ 🔄 Operations: Free tier (50K/day)")
            print(f"   ├─ 📊 Additional storage: $0.026/GB/month")
            print(f"   ├─ 📡 Additional downloads: $0.12/GB")
            print(f"   ├─ 🔄 Additional operations: $0.05/10K operations")
            print(f"   └─ 📊 Typical cost: Free for most apps")
        else:
            print(f"   ├─ 📁 Storage: Free tier (5GB), then $0.026/GB/month")
            print(f"   ├─ 📡 Downloads: Free tier (1GB/day), then $0.12/GB")
            print(f"   ├─ 🔄 Operations: Free tier (50K/day), then $0.05/10K")
            print(f"   └─ 🌍 Global CDN: Included")

        return {
            'resource_type': 'firebase_storage',
            'name': self.name,
            'buckets_to_create': buckets_to_create,
            'buckets_to_keep': buckets_to_keep,
            'buckets_to_remove': buckets_to_remove,
            'existing_buckets': existing_buckets,
            'bucket_name': desired_bucket_name,
            'project_id': self._project_id,
            'location': self._location,
            'public_access': self._public_access,
            'lifecycle_rule_count': len(self._lifecycle_rules),
            'estimated_cost': "Free (within limits)"
        }

    def create(self) -> Dict[str, Any]:
        """Create Firebase Storage bucket"""
        try:
            if not self._project_id:
                raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
                
            if not self._bucket_name:
                self._bucket_name = f"{self._project_id}.appspot.com"
                
            print(f"📁 Creating Firebase Storage bucket...")
            
            # Create storage bucket
            bucket_cmd = ["firebase", "storage:buckets:create", "--project", self._project_id, "--location", self._location]
            if self._bucket_name != f"{self._project_id}.appspot.com":
                bucket_cmd.extend(["--bucket", self._bucket_name])
                
            result = subprocess.run(bucket_cmd, capture_output=True, text=True)
            
            if result.returncode != 0 and "already exists" not in result.stderr.lower():
                raise Exception(f"Failed to create storage bucket: {result.stderr}")
                
            print(f"✅ Storage bucket created: {self._bucket_name}")
            
            # Deploy security rules if provided
            if self._security_rules:
                try:
                    print(f"🔒 Deploying storage security rules...")
                    rules_cmd = ["firebase", "deploy", "--only", "storage", "--project", self._project_id]
                    rules_result = subprocess.run(rules_cmd, capture_output=True, text=True)
                    
                    if rules_result.returncode == 0:
                        print(f"✅ Security rules deployed")
                    else:
                        print(f"⚠️  Security rules deployment failed: {rules_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not deploy security rules: {str(e)}")
            
            # Configure CORS if specified
            if self._cors_config:
                try:
                    print(f"🌐 Configuring CORS...")
                    cors_file = "cors.json"
                    with open(cors_file, 'w') as f:
                        json.dump([self._cors_config], f, indent=2)
                    
                    cors_cmd = ["gsutil", "cors", "set", cors_file, f"gs://{self._bucket_name}"]
                    cors_result = subprocess.run(cors_cmd, capture_output=True, text=True)
                    
                    if cors_result.returncode == 0:
                        print(f"✅ CORS configured")
                    else:
                        print(f"⚠️  CORS configuration failed: {cors_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not configure CORS: {str(e)}")
            
            # Configure lifecycle rules if specified
            if self._lifecycle_rules:
                try:
                    print(f"⏰ Configuring lifecycle rules...")
                    lifecycle_file = "lifecycle.json"
                    lifecycle_config = {
                        "rule": [
                            {
                                "action": {"type": rule["action"]},
                                "condition": rule["condition"]
                            }
                            for rule in self._lifecycle_rules
                        ]
                    }
                    
                    with open(lifecycle_file, 'w') as f:
                        json.dump(lifecycle_config, f, indent=2)
                    
                    lifecycle_cmd = ["gsutil", "lifecycle", "set", lifecycle_file, f"gs://{self._bucket_name}"]
                    lifecycle_result = subprocess.run(lifecycle_cmd, capture_output=True, text=True)
                    
                    if lifecycle_result.returncode == 0:
                        print(f"✅ Lifecycle rules configured")
                    else:
                        print(f"⚠️  Lifecycle configuration failed: {lifecycle_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not configure lifecycle rules: {str(e)}")
            
            # Make bucket public if requested
            if self._public_access:
                try:
                    print(f"🌍 Making bucket publicly accessible...")
                    public_cmd = ["gsutil", "iam", "ch", "allUsers:objectViewer", f"gs://{self._bucket_name}"]
                    public_result = subprocess.run(public_cmd, capture_output=True, text=True)
                    
                    if public_result.returncode == 0:
                        print(f"✅ Bucket made public")
                    else:
                        print(f"⚠️  Public access configuration failed: {public_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not configure public access: {str(e)}")
            
            # Create configuration file
            config = {
                "storage": {
                    "bucket": self._bucket_name,
                    "location": self._location,
                    "public_access": self._public_access,
                    "cors": self._cors_config,
                    "lifecycle_rules": self._lifecycle_rules
                }
            }
            
            config_path = "storage-config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            print(f"✅ Firebase Storage setup complete!")
            
            # Provide usage instructions
            bucket_url = f"https://storage.googleapis.com/{self._bucket_name}"
            console_url = f"https://console.firebase.google.com/project/{self._project_id}/storage"
            
            print(f"\n📖 Next Steps:")
            print(f"   1. Go to Storage Console: {console_url}")
            print(f"   2. Upload your first files")
            print(f"   3. Configure security rules for production")
            print(f"   4. Bucket URL: {bucket_url}")
            
            return {
                "status": "created",
                "project_id": self._project_id,
                "bucket_name": self._bucket_name,
                "location": self._location,
                "public_access": self._public_access,
                "bucket_url": bucket_url,
                "console_url": console_url
            }
            
        except Exception as e:
            raise Exception(f"Firebase Storage creation failed: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Delete Firebase Storage bucket"""
        try:
            print(f"🗑️  Removing Firebase Storage bucket...")
            
            if not self._bucket_name:
                self._bucket_name = f"{self._project_id}.appspot.com"
            
            # Delete bucket
            delete_cmd = ["gsutil", "rm", "-r", f"gs://{self._bucket_name}"]
            result = subprocess.run(delete_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Storage bucket removed successfully")
                return {"status": "removed"}
            else:
                print(f"⚠️  Automatic deletion failed: {result.stderr}")
                print(f"🔧 To delete manually:")
                print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self._project_id}/storage/")
                print(f"   2. Delete bucket manually")
                print(f"   3. Or use: gsutil rm -r gs://{self._bucket_name}")
                
                return {
                    "status": "manual_action_required",
                    "message": "Visit Firebase Console to delete storage bucket"
                }
                
        except Exception as e:
            raise Exception(f"Firebase Storage destroy failed: {str(e)}")

    def update(self) -> Dict[str, Any]:
        """Update Firebase Storage configuration"""
        return self.create() 