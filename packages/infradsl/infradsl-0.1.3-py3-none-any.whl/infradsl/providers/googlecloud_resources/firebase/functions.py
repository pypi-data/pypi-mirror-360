"""
Firebase Functions Resource for InfraDSL
Serverless functions with automatic scaling

Features:
- HTTP functions
- Background functions (Firestore, Storage triggers)
- Scheduled functions
- Callable functions
- Local development and testing
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any
from ..base_resource import BaseGcpResource


class FirebaseFunctions(BaseGcpResource):
    """
    Firebase Functions for serverless backend
    
    Example:
        api = (FirebaseFunctions("my-api")
               .project("my-project")
               .runtime("nodejs18")
               .region("us-central1")
               .http_function("hello", "functions/hello.js")
               .firestore_trigger("onUserCreate", "functions/user.js", "users/{userId}")
               .scheduled_function("dailyBackup", "functions/backup.js", "0 2 * * *"))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._project_id = None
        self._functions_dir = "functions"
        self._runtime = "nodejs18"
        self._region = "us-central1"
        self._functions = []
        self._environment_vars = {}
        self._memory = "256MB"
        self._timeout = 60
        self._package_json = None
        self._dependencies = []
        
    def _initialize_managers(self):
        """Initialize Firebase Functions managers"""
        # Firebase Functions doesn't require additional managers
        pass
        
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Firebase Functions doesn't require post-auth setup
        pass

    def _discover_existing_functions(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firebase Functions"""
        existing_functions = {}
        
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.gcp_client or not hasattr(self.gcp_client, 'credentials'):
                print(f"⚠️  No GCP credentials available for Firebase Functions discovery")
                return existing_functions
            
            # Refresh credentials if needed
            if hasattr(self.gcp_client.credentials, 'refresh'):
                self.gcp_client.credentials.refresh(Request())
            
            # Get project ID
            project_id = self._project_id or (self.gcp_client.project_id if hasattr(self.gcp_client, 'project_id') else self.gcp_client.project)
            if not project_id:
                print(f"⚠️  Project ID required for Firebase Functions discovery")
                return existing_functions
            
            # Use Cloud Functions API to list functions (Firebase Functions are Cloud Functions)
            region = self._region or 'us-central1'
            functions_api_url = f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/{region}/functions"
            headers = {
                'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(functions_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                functions = data.get('functions', [])
                
                for function in functions:
                    function_name = function.get('name', '').split('/')[-1]
                    
                    # Extract function configuration
                    source_archive_url = function.get('sourceArchiveUrl', '')
                    entry_point = function.get('entryPoint', 'main')
                    runtime = function.get('runtime', 'unknown')
                    
                    # Get trigger information
                    trigger_type = 'unknown'
                    trigger_config = {}
                    
                    if 'httpsTrigger' in function:
                        trigger_type = 'http'
                        trigger_config = {
                            'url': function['httpsTrigger'].get('url', ''),
                            'security_level': function['httpsTrigger'].get('securityLevel', 'SECURE_ALWAYS')
                        }
                    elif 'eventTrigger' in function:
                        event_trigger = function['eventTrigger']
                        trigger_type = 'event'
                        trigger_config = {
                            'event_type': event_trigger.get('eventType', ''),
                            'resource': event_trigger.get('resource', ''),
                            'service': event_trigger.get('service', ''),
                            'failure_policy': event_trigger.get('failurePolicy', {})
                        }
                        
                        # Determine specific trigger type from event type
                        event_type = event_trigger.get('eventType', '')
                        if 'firestore' in event_type.lower():
                            trigger_type = 'firestore'
                        elif 'storage' in event_type.lower():
                            trigger_type = 'storage'
                        elif 'pubsub' in event_type.lower():
                            trigger_type = 'pubsub'
                        elif 'scheduler' in event_type.lower():
                            trigger_type = 'scheduled'
                    
                    # Get resource allocation
                    available_memory_mb = function.get('availableMemoryMb', 256)
                    timeout = function.get('timeout', '60s')
                    timeout_seconds = int(timeout.rstrip('s')) if timeout.endswith('s') else 60
                    
                    # Get environment variables
                    env_vars = function.get('environmentVariables', {})
                    
                    # Get status and other metadata
                    status = function.get('status', 'UNKNOWN')
                    update_time = function.get('updateTime', '')
                    version_id = function.get('versionId', 'unknown')
                    
                    # Get labels
                    labels = function.get('labels', {})
                    
                    # Check if this is likely a Firebase function
                    # Firebase functions typically have certain labels or source patterns
                    is_firebase_function = (
                        'firebase-functions-hash' in labels or
                        'deployment-tool' in labels and labels.get('deployment-tool') == 'firebase-tools' or
                        'firebase' in source_archive_url.lower()
                    )
                    
                    existing_functions[function_name] = {
                        'function_name': function_name,
                        'full_name': function['name'],
                        'entry_point': entry_point,
                        'runtime': runtime,
                        'trigger_type': trigger_type,
                        'trigger_config': trigger_config,
                        'available_memory_mb': available_memory_mb,
                        'timeout_seconds': timeout_seconds,
                        'status': status,
                        'update_time': update_time[:10] if update_time else 'unknown',
                        'version_id': version_id,
                        'environment_variables': env_vars,
                        'env_var_count': len(env_vars),
                        'labels': labels,
                        'label_count': len(labels),
                        'is_firebase_function': is_firebase_function,
                        'source_archive_url': source_archive_url,
                        'project_id': project_id,
                        'region': region
                    }
                    
            elif response.status_code == 403:
                print(f"⚠️  Cloud Functions API access denied. Enable Cloud Functions API in the console.")
            elif response.status_code == 404:
                print(f"⚠️  No functions found in region {region} for project {project_id}")
            else:
                print(f"⚠️  Failed to list Cloud Functions: HTTP {response.status_code}")
                
        except ImportError:
            print(f"⚠️  'requests' library required for Firebase Functions discovery. Install with: pip install requests")
        except Exception as e:
            print(f"⚠️  Failed to discover existing Firebase Functions: {str(e)}")
        
        return existing_functions
        
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self._project_id = project_id
        return self
        
    def runtime(self, runtime: str):
        """Set function runtime (nodejs18, python311, etc.)"""
        self._runtime = runtime
        return self
        
    def region(self, region: str):
        """Set function region"""
        self._region = region
        return self
        
    def http_function(self, name: str, source_file: str, memory: str = "256Mi", timeout: int = 60):
        """Add HTTP function"""
        self._functions.append({
            "type": "http",
            "name": name,
            "source": source_file,
            "memory": memory,
            "timeout": timeout
        })
        return self
        
    def callable_function(self, name: str, source_file: str, memory: str = "256Mi"):
        """Add callable function"""
        self._functions.append({
            "type": "callable",
            "name": name,
            "source": source_file,
            "memory": memory
        })
        return self
        
    def firestore_trigger(self, name: str, source_file: str, document_path: str, event: str = "create"):
        """Add Firestore trigger function"""
        self._functions.append({
            "type": "firestore",
            "name": name,
            "source": source_file,
            "document_path": document_path,
            "event": event
        })
        return self
        
    def storage_trigger(self, name: str, source_file: str, bucket: str = None, event: str = "finalize"):
        """Add Storage trigger function"""
        self._functions.append({
            "type": "storage",
            "name": name,
            "source": source_file,
            "bucket": bucket,
            "event": event
        })
        return self
        
    def scheduled_function(self, name: str, source_file: str, schedule: str = "0 2 * * *"):
        """Add scheduled function (cron-like)"""
        self._functions.append({
            "type": "scheduled",
            "name": name,
            "source": source_file,
            "schedule": schedule
        })
        return self
        
    def pubsub_trigger(self, name: str, source_file: str, topic: str):
        """Add Pub/Sub trigger function"""
        self._functions.append({
            "type": "pubsub",
            "name": name,
            "source": source_file,
            "topic": topic
        })
        return self
        
    def dependencies(self, deps: List[str]):
        """Add npm dependencies"""
        self._dependencies = deps
        return self
        
    def package_json(self, package_file: str):
        """Set custom package.json file"""
        self._package_json = package_file
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        try:
            self._ensure_authenticated()
        except:
            # Firebase Functions can work without full GCP authentication in some cases
            pass

        # Discover existing functions
        existing_functions = self._discover_existing_functions()
        
        # Categorize functions
        functions_to_create = []
        functions_to_keep = []
        functions_to_remove = []
        
        # Check which functions exist and which need to be created
        for function_config in self._functions:
            function_name = function_config['name']
            if function_name not in existing_functions:
                functions_to_create.append(function_config)
            else:
                # Only include Firebase functions in "keep" list
                if existing_functions[function_name].get('is_firebase_function', False):
                    existing_function = existing_functions[function_name]
                    existing_function.update(function_config)  # Merge configs
                    functions_to_keep.append(existing_function)

        print(f"\n⚡ Firebase Functions Preview")
        
        # Show functions to create
        if functions_to_create:
            print(f"╭─ ⚡ Functions to CREATE: {len(functions_to_create)}")
            for func in functions_to_create:
                trigger_icon = {
                    'http': '🌐',
                    'callable': '📞',
                    'firestore': '🔥',
                    'storage': '📁',
                    'scheduled': '⏰',
                    'pubsub': '📡'
                }.get(func['type'], '⚡')
                
                print(f"├─ 🆕 {func['name']} ({trigger_icon} {func['type']})")
                print(f"│  ├─ 📋 Project: {self._project_id}")
                print(f"│  ├─ 🔧 Runtime: {self._runtime}")
                print(f"│  ├─ 📍 Region: {self._region}")
                print(f"│  ├─ 📄 Source: {func['source']}")
                
                # Show trigger-specific configuration
                if func['type'] == 'http':
                    memory = func.get('memory', self._memory)
                    timeout = func.get('timeout', self._timeout)
                    print(f"│  ├─ 🌐 HTTP Trigger: HTTPS endpoint")
                    print(f"│  ├─ 💾 Memory: {memory}")
                    print(f"│  ├─ ⏱️  Timeout: {timeout}s")
                    print(f"│  └─ 🔗 URL: https://{self._region}-{self._project_id}.cloudfunctions.net/{func['name']}")
                    
                elif func['type'] == 'callable':
                    memory = func.get('memory', self._memory)
                    print(f"│  ├─ 📞 Callable: SDK callable function")
                    print(f"│  ├─ 💾 Memory: {memory}")
                    print(f"│  └─ 🔒 Auth: Firebase Auth required")
                    
                elif func['type'] == 'firestore':
                    doc_path = func.get('document_path', 'unknown')
                    event = func.get('event', 'create')
                    print(f"│  ├─ 🔥 Firestore Trigger: {event}")
                    print(f"│  ├─ 📄 Document: {doc_path}")
                    print(f"│  └─ 🔄 Auto-scaling: Based on document changes")
                    
                elif func['type'] == 'storage':
                    bucket = func.get('bucket', f"{self._project_id}.appspot.com")
                    event = func.get('event', 'finalize')
                    print(f"│  ├─ 📁 Storage Trigger: {event}")
                    print(f"│  ├─ 🪣 Bucket: {bucket}")
                    print(f"│  └─ 🔄 Auto-scaling: Based on file events")
                    
                elif func['type'] == 'scheduled':
                    schedule = func.get('schedule', '0 2 * * *')
                    print(f"│  ├─ ⏰ Scheduled: {schedule}")
                    print(f"│  ├─ 🔄 Cron Expression")
                    print(f"│  └─ ⚡ Cloud Scheduler integration")
                    
                elif func['type'] == 'pubsub':
                    topic = func.get('topic', 'unknown')
                    print(f"│  ├─ 📡 Pub/Sub Trigger: {topic}")
                    print(f"│  ├─ 📩 Message processing")
                    print(f"│  └─ 🔄 Auto-scaling: Based on message volume")
            print(f"╰─")

        # Show existing functions being kept
        if functions_to_keep:
            print(f"\n╭─ ⚡ Existing Functions to KEEP: {len(functions_to_keep)}")
            for func in functions_to_keep:
                status_icon = "🟢" if func['status'] == 'ACTIVE' else "🟡" if func['status'] == 'DEPLOYING' else "🔴"
                trigger_icon = {
                    'http': '🌐',
                    'callable': '📞',
                    'firestore': '🔥',
                    'storage': '📁',
                    'scheduled': '⏰',
                    'pubsub': '📡',
                    'event': '🔄'
                }.get(func['trigger_type'], '⚡')
                
                print(f"├─ {status_icon} {func['function_name']} ({trigger_icon} {func['trigger_type']})")
                print(f"│  ├─ 🔧 Runtime: {func['runtime']}")
                print(f"│  ├─ 💾 Memory: {func['available_memory_mb']}MB")
                print(f"│  ├─ ⏱️  Timeout: {func['timeout_seconds']}s")
                print(f"│  ├─ 📊 Status: {func['status']}")
                
                # Show trigger-specific information
                trigger_config = func.get('trigger_config', {})
                if func['trigger_type'] == 'http' and 'url' in trigger_config:
                    print(f"│  ├─ 🌐 URL: {trigger_config['url']}")
                elif func['trigger_type'] in ['firestore', 'storage', 'pubsub'] and 'resource' in trigger_config:
                    print(f"│  ├─ 🎯 Resource: {trigger_config['resource']}")
                
                if func['env_var_count'] > 0:
                    print(f"│  ├─ 🔧 Environment Variables: {func['env_var_count']}")
                
                if func['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {func['label_count']}")
                
                print(f"│  ├─ 📅 Updated: {func['update_time']}")
                print(f"│  └─ 📝 Version: {func['version_id']}")
            print(f"╰─")

        # Show deployment information
        if functions_to_create:
            print(f"\n🚀 Firebase Functions Deployment:")
            print(f"   ├─ 📁 Functions Directory: {self._functions_dir}")
            print(f"   ├─ 🔧 Runtime: {self._runtime}")
            print(f"   ├─ 📦 Dependencies: {len(self._dependencies)} packages")
            
            # Show function type distribution
            function_types = {}
            for func in functions_to_create:
                func_type = func['type']
                function_types[func_type] = function_types.get(func_type, 0) + 1
            
            print(f"   ├─ 📊 Function Types:")
            for func_type, count in function_types.items():
                type_icon = {
                    'http': '🌐',
                    'callable': '📞',
                    'firestore': '🔥',
                    'storage': '📁',
                    'scheduled': '⏰',
                    'pubsub': '📡'
                }.get(func_type, '⚡')
                print(f"   │  ├─ {type_icon} {func_type}: {count}")
            
            print(f"   └─ 🚀 Deploy: firebase deploy --only functions")

        # Show cost information
        print(f"\n💰 Firebase Functions Costs:")
        if functions_to_create:
            total_functions = len(functions_to_create)
            print(f"   ├─ ⚡ Invocations: Free tier (2M/month)")
            print(f"   ├─ ⏱️  Compute time: Free tier (400K GB-seconds/month)")
            print(f"   ├─ 📡 Outbound data: Free tier (5GB/month)")
            print(f"   ├─ 📊 Additional invocations: $0.40/million")
            print(f"   ├─ ⏱️  Additional compute: $0.0000025/GB-second")
            print(f"   ├─ 📡 Additional data: $0.12/GB")
            print(f"   └─ 📊 Est. cost ({total_functions} functions): Free for most apps")
        else:
            print(f"   ├─ ⚡ Invocations: Free tier (2M/month), then $0.40/million")
            print(f"   ├─ ⏱️  Compute time: Free tier (400K GB-seconds/month)")
            print(f"   ├─ 📡 Outbound data: Free tier (5GB/month), then $0.12/GB")
            print(f"   └─ 🔄 Auto-scaling: Pay only for usage")

        return {
            'resource_type': 'firebase_functions',
            'name': self.name,
            'functions_to_create': functions_to_create,
            'functions_to_keep': functions_to_keep,
            'functions_to_remove': functions_to_remove,
            'existing_functions': existing_functions,
            'project_id': self._project_id,
            'runtime': self._runtime,
            'region': self._region,
            'function_count': len(self._functions),
            'dependency_count': len(self._dependencies),
            'estimated_cost': "Free (within limits)"
        }

    def create(self) -> Dict[str, Any]:
        """Deploy Firebase Functions"""
        try:
            if not self._project_id:
                raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
                
            print(f"⚡ Deploying Firebase Functions...")
            
            # Create functions directory structure
            os.makedirs(self._functions_dir, exist_ok=True)
            
            # Create package.json for functions
            package_json = {
                "name": f"{self.name}-functions",
                "version": "1.0.0",
                "description": f"Firebase Functions for {self.name}",
                "main": "index.js",
                "engines": {
                    "node": "18"
                },
                "scripts": {
                    "serve": "firebase emulators:start --only functions",
                    "shell": "firebase functions:shell",
                    "start": "npm run shell",
                    "deploy": "firebase deploy --only functions",
                    "logs": "firebase functions:log"
                },
                "dependencies": {
                    "firebase-admin": "^11.0.0",
                    "firebase-functions": "^4.0.0"
                }
            }
            
            # Add custom dependencies
            for dep in self._dependencies:
                if ":" in dep:
                    name, version = dep.split(":")
                    package_json["dependencies"][name] = version
                else:
                    package_json["dependencies"][dep] = "latest"
            
            with open(f"{self._functions_dir}/package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Create index.js with all functions
            index_content = f"""const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Initialize Firebase Admin
admin.initializeApp();

// Export all functions
"""
            
            for func in self._functions:
                func_name = func["name"]
                source_file = func["source"]
                
                # Read source file if it exists
                if os.path.exists(source_file):
                    with open(source_file, 'r') as f:
                        source_content = f.read()
                    index_content += f"\n// {func_name} function\n{source_content}\n"
                else:
                    # Create placeholder function
                    if func["type"] == "http":
                        index_content += f"""
// HTTP function: {func_name}
exports.{func_name} = functions.https.onRequest((req, res) => {{
    res.json({{ message: "Hello from {func_name}!" }});
}});
"""
                    elif func["type"] == "callable":
                        index_content += f"""
// Callable function: {func_name}
exports.{func_name} = functions.https.onCall((data, context) => {{
    return {{ message: "Hello from {func_name}!" }};
}});
"""
                    elif func["type"] == "firestore":
                        index_content += f"""
// Firestore trigger: {func_name}
exports.{func_name} = functions.firestore
    .document('{func["document_path"]}')
    .on{func["event"].title()}((snap, context) => {{
        console.log('{func_name} triggered for document:', context.params);
    }});
"""
                    elif func["type"] == "storage":
                        index_content += f"""
// Storage trigger: {func_name}
exports.{func_name} = functions.storage
    .object()
    .on{func["event"].title()}((object) => {{
        console.log('{func_name} triggered for file:', object.name);
    }});
"""
                    elif func["type"] == "scheduled":
                        index_content += f"""
// Scheduled function: {func_name}
exports.{func_name} = functions.pubsub
    .schedule('{func["schedule"]}')
    .onRun((context) => {{
        console.log('{func_name} scheduled function executed');
    }});
"""
                    elif func["type"] == "pubsub":
                        index_content += f"""
// Pub/Sub trigger: {func_name}
exports.{func_name} = functions.pubsub
    .topic('{func["topic"]}')
    .onPublish((message) => {{
        console.log('{func_name} triggered for topic:', message.data);
    }});
"""
            
            with open(f"{self._functions_dir}/index.js", 'w') as f:
                f.write(index_content)
            
            # Install dependencies
            print(f"📦 Installing dependencies...")
            install_cmd = ["npm", "install"]
            result = subprocess.run(install_cmd, cwd=self._functions_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️  Dependency installation failed: {result.stderr}")
            else:
                print(f"✅ Dependencies installed")
            
            # Deploy functions
            print(f"🚀 Deploying functions...")
            deploy_cmd = ["firebase", "deploy", "--only", "functions", "--project", self._project_id]
            deploy_result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if deploy_result.returncode != 0:
                raise Exception(f"Function deployment failed: {deploy_result.stderr}")
            
            # Parse deployment output for function URLs
            function_urls = {}
            output_lines = deploy_result.stdout.split('\n')
            
            for line in output_lines:
                if "Function URL" in line:
                    parts = line.split("Function URL")
                    if len(parts) > 1:
                        url_part = parts[1].strip()
                        if ":" in url_part:
                            func_name = url_part.split(":")[0].strip()
                            url = url_part.split(":")[1].strip()
                            function_urls[func_name] = url
            
            print(f"✅ Firebase Functions deployed successfully!")
            
            # Show function URLs
            if function_urls:
                print(f"\n🌐 Function URLs:")
                for func_name, url in function_urls.items():
                    print(f"   {func_name}: {url}")
            
            return {
                "status": "deployed",
                "project_id": self._project_id,
                "runtime": self._runtime,
                "region": self._region,
                "functions": self._functions,
                "function_urls": function_urls,
                "console_url": f"https://console.firebase.google.com/project/{self._project_id}/functions/"
            }
            
        except Exception as e:
            raise Exception(f"Firebase Functions deployment failed: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Remove Firebase Functions"""
        try:
            print(f"🗑️  Removing Firebase Functions...")
            
            # Delete functions
            delete_cmd = ["firebase", "functions:delete", "--project", self._project_id, "--force"]
            result = subprocess.run(delete_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Functions removed successfully")
                return {"status": "removed"}
            else:
                print(f"⚠️  Automatic deletion failed: {result.stderr}")
                print(f"🔧 To delete manually:")
                print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self._project_id}/functions/")
                print(f"   2. Delete functions manually")
                
                return {
                    "status": "manual_action_required",
                    "message": "Visit Firebase Console to delete functions"
                }
                
        except Exception as e:
            raise Exception(f"Firebase Functions destroy failed: {str(e)}")

    def update(self) -> Dict[str, Any]:
        """Update Firebase Functions"""
        return self.create() 