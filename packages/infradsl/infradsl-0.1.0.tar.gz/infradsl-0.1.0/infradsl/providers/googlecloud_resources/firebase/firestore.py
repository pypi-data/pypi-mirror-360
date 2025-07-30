"""
Firestore Resource for InfraDSL
NoSQL database with real-time synchronization

Features:
- Document database with collections
- Real-time synchronization
- Offline support
- Security rules
- Data migration and backup
"""

import json
import subprocess
from typing import Dict, List, Optional, Any
from ..base_resource import BaseGcpResource


class Firestore(BaseGcpResource):
    """
    Firestore NoSQL database for real-time applications
    
    Example:
        db = (Firestore("my-app-db")
              .project("my-project")
              .mode("native")  # or "datastore"
              .location("us-central1")
              .collections(["users", "posts", "comments"])
              .security_rules("rules/firestore.rules"))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._project_id = None
        self._database_id = None
        self._location = "us-central1"
        self._mode = "firestore-native"
        self._collections = []
        self._security_rules = None
        self._backup_enabled = False
        self._indexes = []
        
    def _initialize_managers(self):
        """Initialize Firestore managers"""
        # Firestore doesn't require additional managers
        pass
        
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Firestore doesn't require post-auth setup
        pass

    def _discover_existing_databases(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firestore databases"""
        existing_databases = {}
        
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.gcp_client or not hasattr(self.gcp_client, 'credentials'):
                print(f"⚠️  No GCP credentials available for Firestore discovery")
                return existing_databases
            
            # Refresh credentials if needed
            if hasattr(self.gcp_client.credentials, 'refresh'):
                self.gcp_client.credentials.refresh(Request())
            
            # Get project ID
            project_id = self._project_id or (self.gcp_client.project_id if hasattr(self.gcp_client, 'project_id') else self.gcp_client.project)
            if not project_id:
                print(f"⚠️  Project ID required for Firestore discovery")
                return existing_databases
            
            # Use Firestore Admin API to list databases
            firestore_api_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases"
            headers = {
                'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(firestore_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                databases = data.get('databases', [])
                
                for database in databases:
                    database_id = database.get('name', '').split('/')[-1]
                    
                    # Extract database configuration
                    location_id = database.get('locationId', 'unknown')
                    database_type = database.get('type', 'FIRESTORE_NATIVE')
                    concurrency_mode = database.get('concurrencyMode', 'OPTIMISTIC')
                    app_engine_integration_mode = database.get('appEngineIntegrationMode', 'DISABLED')
                    
                    # Convert database type to readable format
                    mode = 'native' if database_type == 'FIRESTORE_NATIVE' else 'datastore'
                    
                    # Get database state
                    state = database.get('state', 'UNKNOWN')
                    
                    # Get creation time
                    create_time = database.get('createTime', '')
                    
                    # Get etag (version)
                    etag = database.get('etag', '')
                    
                    database_info = {
                        'database_id': database_id,
                        'full_name': database['name'],
                        'location_id': location_id,
                        'mode': mode,
                        'database_type': database_type,
                        'concurrency_mode': concurrency_mode,
                        'app_engine_integration_mode': app_engine_integration_mode,
                        'state': state,
                        'create_time': create_time[:10] if create_time else 'unknown',
                        'etag': etag,
                        'project_id': project_id
                    }
                    
                    # Try to get collection information
                    try:
                        # List collections (this requires Firestore client library)
                        collections_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/{database_id}/documents"
                        collections_response = requests.get(collections_url, headers=headers)
                        
                        collections = []
                        document_count = 0
                        
                        if collections_response.status_code == 200:
                            collections_data = collections_response.json()
                            documents = collections_data.get('documents', [])
                            
                            # Extract collection names from document paths
                            collection_names = set()
                            for doc in documents:
                                doc_name = doc.get('name', '')
                                if '/documents/' in doc_name:
                                    # Extract collection name from document path
                                    doc_path = doc_name.split('/documents/')[-1]
                                    if '/' in doc_path:
                                        collection_name = doc_path.split('/')[0]
                                        collection_names.add(collection_name)
                            
                            collections = list(collection_names)
                            document_count = len(documents)
                        
                        database_info['collections'] = collections
                        database_info['collection_count'] = len(collections)
                        database_info['document_count'] = document_count
                        
                    except Exception as e:
                        print(f"⚠️  Failed to get collections for database {database_id}: {str(e)}")
                        database_info['collections'] = []
                        database_info['collection_count'] = 0
                        database_info['document_count'] = 0
                    
                    # Try to get security rules information
                    try:
                        rules_url = f"https://firebaserules.googleapis.com/v1/projects/{project_id}/rulesets"
                        rules_response = requests.get(rules_url, headers=headers)
                        
                        has_custom_rules = False
                        rules_count = 0
                        
                        if rules_response.status_code == 200:
                            rules_data = rules_response.json()
                            rulesets = rules_data.get('rulesets', [])
                            rules_count = len(rulesets)
                            
                            # Check if there are custom rules (more than default)
                            has_custom_rules = rules_count > 1
                        
                        database_info['has_custom_rules'] = has_custom_rules
                        database_info['rules_count'] = rules_count
                        
                    except Exception as e:
                        print(f"⚠️  Failed to get security rules for database {database_id}: {str(e)}")
                        database_info['has_custom_rules'] = False
                        database_info['rules_count'] = 0
                    
                    # Try to get indexes information
                    try:
                        indexes_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/{database_id}/collectionGroups/-/indexes"
                        indexes_response = requests.get(indexes_url, headers=headers)
                        
                        indexes = []
                        composite_index_count = 0
                        
                        if indexes_response.status_code == 200:
                            indexes_data = indexes_response.json()
                            all_indexes = indexes_data.get('indexes', [])
                            
                            # Count composite indexes (exclude single-field indexes)
                            for index in all_indexes:
                                fields = index.get('fields', [])
                                if len(fields) > 1:  # Composite index
                                    composite_index_count += 1
                                    indexes.append({
                                        'collection_group': index.get('collectionGroup', ''),
                                        'field_count': len(fields),
                                        'state': index.get('state', 'UNKNOWN')
                                    })
                        
                        database_info['indexes'] = indexes
                        database_info['composite_index_count'] = composite_index_count
                        
                    except Exception as e:
                        print(f"⚠️  Failed to get indexes for database {database_id}: {str(e)}")
                        database_info['indexes'] = []
                        database_info['composite_index_count'] = 0
                    
                    existing_databases[database_id] = database_info
                    
            elif response.status_code == 403:
                print(f"⚠️  Firestore API access denied. Enable Firestore API in the console.")
            elif response.status_code == 404:
                print(f"⚠️  No Firestore databases found for project {project_id}")
            else:
                print(f"⚠️  Failed to list Firestore databases: HTTP {response.status_code}")
                
        except ImportError:
            print(f"⚠️  'requests' library required for Firestore discovery. Install with: pip install requests")
        except Exception as e:
            print(f"⚠️  Failed to discover existing Firestore databases: {str(e)}")
        
        return existing_databases
        
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self._project_id = project_id
        return self
        
    def mode(self, mode: str):
        """Set Firestore mode (native or datastore)"""
        if mode not in ["native", "datastore"]:
            raise ValueError("Mode must be 'native' or 'datastore'")
        self._mode = mode
        return self
        
    def location(self, location: str):
        """Set Firestore location"""
        self._location = location
        return self
        
    def collections(self, collections: List[str]):
        """Define collections to create"""
        self._collections = collections
        return self
        
    def collection(self, name: str):
        """Add a single collection"""
        self._collections.append(name)
        return self
        
    def security_rules(self, rules_file: str):
        """Set security rules file path"""
        self._security_rules = rules_file
        return self
        
    def backup(self, enabled: bool = True):
        """Enable automatic backups"""
        self._backup_enabled = enabled
        return self
        
    def indexes(self, indexes: List[Dict[str, Any]]):
        """Define composite indexes"""
        self._indexes = indexes
        return self
        
    def index(self, collection: str, fields: List[str], query_scope: str = "COLLECTION"):
        """Add a composite index"""
        self._indexes.append({
            "collection": collection,
            "fields": fields,
            "query_scope": query_scope
        })
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview the Firestore configuration"""
        return {
            "resource_type": "Firestore Database",
            "name": self.name,
            "project_id": self._project_id,
            "mode": self._mode,
            "location": self._location,
            "collections": self._collections,
            "security_rules": self._security_rules,
            "backup_enabled": self._backup_enabled,
            "indexes": self._indexes
        }

    def create(self) -> Dict[str, Any]:
        """Create Firestore database"""
        try:
            if not self._project_id:
                raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
                
            print(f"🗄️  Creating Firestore database...")
            
            # Create Firestore database
            cmd = ["firebase", "firestore:databases:create", "--project", self._project_id, "--location", self._location]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0 and "already exists" not in result.stderr.lower():
                raise Exception(f"Failed to create Firestore database: {result.stderr}")
                
            print(f"✅ Firestore database created in {self._location}")
            
            # Deploy security rules if provided
            if self._security_rules:
                try:
                    print(f"🔒 Deploying security rules...")
                    rules_cmd = ["firebase", "deploy", "--only", "firestore:rules", "--project", self._project_id]
                    rules_result = subprocess.run(rules_cmd, capture_output=True, text=True)
                    
                    if rules_result.returncode == 0:
                        print(f"✅ Security rules deployed")
                    else:
                        print(f"⚠️  Security rules deployment failed: {rules_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not deploy security rules: {str(e)}")
            
            # Deploy indexes if defined
            if self._indexes:
                try:
                    print(f"📊 Creating composite indexes...")
                    # Create firestore.indexes.json
                    indexes_config = {
                        "indexes": self._indexes,
                        "fieldOverrides": []
                    }
                    
                    with open("firestore.indexes.json", 'w') as f:
                        json.dump(indexes_config, f, indent=2)
                    
                    indexes_cmd = ["firebase", "deploy", "--only", "firestore:indexes", "--project", self._project_id]
                    indexes_result = subprocess.run(indexes_cmd, capture_output=True, text=True)
                    
                    if indexes_result.returncode == 0:
                        print(f"✅ Composite indexes created")
                    else:
                        print(f"⚠️  Index creation failed: {indexes_result.stderr}")
                except Exception as e:
                    print(f"⚠️  Could not create indexes: {str(e)}")
            
            # Create sample data for collections
            if self._collections:
                print(f"📝 Creating collections: {', '.join(self._collections)}")
                # Collections are created automatically when first document is added
                print(f"💡 Collections will be created when you add the first document")
            
            # Create configuration file
            config = {
                "firestore": {
                    "mode": self._mode,
                    "location": self._location,
                    "collections": self._collections,
                    "backup_enabled": self._backup_enabled,
                    "indexes": self._indexes
                }
            }
            
            config_path = "firestore-config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            print(f"✅ Firestore database setup complete!")
            
            # Provide usage instructions
            print(f"\n📖 Next Steps:")
            print(f"   1. Go to Firestore Console: https://console.firebase.google.com/project/{self._project_id}/firestore/")
            print(f"   2. Add your first documents to create collections")
            print(f"   3. Configure security rules for production")
            
            return {
                "status": "created",
                "project_id": self._project_id,
                "mode": self._mode,
                "location": self._location,
                "collections": self._collections,
                "console_url": f"https://console.firebase.google.com/project/{self._project_id}/firestore/"
            }
            
        except Exception as e:
            raise Exception(f"Firestore database creation failed: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Delete Firestore database"""
        try:
            print(f"⚠️  Firestore database deletion requires manual confirmation")
            print(f"🔧 To delete the database:")
            print(f"   1. Go to Firestore Console: https://console.firebase.google.com/project/{self._project_id}/firestore/")
            print(f"   2. Click 'Settings' → 'General'")
            print(f"   3. Click 'Delete database'")
            print(f"   4. Type the database name to confirm")
            
            return {
                "status": "manual_action_required",
                "message": "Visit Firestore Console to delete database"
            }
            
        except Exception as e:
            raise Exception(f"Firestore database destroy failed: {str(e)}")

    def update(self) -> Dict[str, Any]:
        """Update Firestore configuration"""
        return self.create() 