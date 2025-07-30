"""
Firebase Functions Lifecycle Mixin

Lifecycle operations for Firebase Functions.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Union


class FirebaseFunctionsLifecycleMixin:
    """
    Mixin for Firebase Functions lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Firebase Functions configuration
    - destroy(): Clean up Firebase Functions configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Discover existing functions
        existing_functions = self._discover_existing_functions()
        
        # Categorize functions
        functions_to_create = []
        functions_to_keep = []
        functions_to_update = []
        
        # Check each configured function
        for function_config in self.functions:
            function_name = function_config['name']
            function_exists = function_name in existing_functions
            
            if not function_exists:
                functions_to_create.append(function_config)
            else:
                existing_function = existing_functions[function_name]
                # Only include Firebase functions in keep list
                if existing_function.get('is_firebase_function', False):
                    functions_to_keep.append(existing_function)

        print(f"\n⚡ Firebase Functions Preview")
        
        # Show functions to create
        if functions_to_create:
            print(f"╭─ ⚡ Functions to CREATE: {len(functions_to_create)}")
            for func in functions_to_create:
                trigger_icon = self._get_function_icon(func['type'])
                
                print(f"├─ 🆕 {func['name']} ({trigger_icon} {func['type']})")
                print(f"│  ├─ 📁 Firebase Project: {self.firebase_project_id}")
                print(f"│  ├─ 🔧 Runtime: {self.runtime}")
                print(f"│  ├─ 📍 Region: {self.region}")
                print(f"│  ├─ 📄 Source: {func.get('source_file', 'generated')}")
                
                # Show function-specific configuration
                print(f"│  ├─ ⚙️  Configuration:")
                print(f"│  │  ├─ 💾 Memory: {func.get('memory', self.default_memory)}")
                print(f"│  │  ├─ ⏱️  Timeout: {func.get('timeout', self.default_timeout)}s")
                print(f"│  │  ├─ 📈 Max Instances: {func.get('max_instances', self.default_max_instances)}")
                print(f"│  │  └─ 📉 Min Instances: {func.get('min_instances', self.default_min_instances)}")
                
                # Show trigger-specific configuration
                if func['type'] == 'http':
                    cors_status = "✅ Enabled" if func.get('cors', self.cors_enabled) else "❌ Disabled"
                    auth_status = "✅ Required" if func.get('auth_required', False) else "❌ Not Required"
                    print(f"│  ├─ 🌐 HTTP Configuration:")
                    print(f"│  │  ├─ 🔗 URL: https://{self.region}-{self.firebase_project_id}.cloudfunctions.net/{func['name']}")
                    print(f"│  │  ├─ 🌍 CORS: {cors_status}")
                    print(f"│  │  └─ 🔐 Auth: {auth_status}")
                    
                elif func['type'] == 'callable':
                    print(f"│  ├─ 📞 Callable Configuration:")
                    print(f"│  │  ├─ 🔐 Auth: Required (Firebase SDK)")
                    print(f"│  │  └─ 📱 SDK Access: firebase.functions().httpsCallable('{func['name']}')")
                    
                elif func['type'] == 'firestore':
                    print(f"│  ├─ 🔥 Firestore Trigger:")
                    print(f"│  │  ├─ 📄 Document Path: {func.get('document_path', 'unknown')}")
                    print(f"│  │  ├─ 🔄 Event: {func.get('event', 'create')}")
                    print(f"│  │  └─ ⚡ Auto-scaling: Based on document changes")
                    
                elif func['type'] == 'storage':
                    print(f"│  ├─ 📁 Storage Trigger:")
                    print(f"│  │  ├─ 🪣 Bucket: {func.get('bucket', f'{self.firebase_project_id}.appspot.com')}")
                    print(f"│  │  ├─ 🔄 Event: {func.get('event', 'finalize')}")
                    print(f"│  │  └─ ⚡ Auto-scaling: Based on file events")
                    
                elif func['type'] == 'scheduled':
                    print(f"│  ├─ ⏰ Scheduled Function:")
                    print(f"│  │  ├─ 📅 Schedule: {func.get('schedule', '0 2 * * *')}")
                    print(f"│  │  ├─ 🌐 Timezone: {func.get('timezone', 'UTC')}")
                    print(f"│  │  └─ 🔄 Cloud Scheduler integration")
                    
                elif func['type'] == 'auth':
                    print(f"│  ├─ 🔐 Auth Trigger:")
                    print(f"│  │  ├─ 🔄 Event: {func.get('event', 'create')}")
                    print(f"│  │  └─ 👤 User lifecycle events")
                    
                elif func['type'] == 'pubsub':
                    print(f"│  ├─ 📡 Pub/Sub Trigger:")
                    print(f"│  │  ├─ 📢 Topic: {func.get('topic', 'unknown')}")
                    print(f"│  │  └─ 📩 Message processing")
                
                # Show Firebase Functions features
                print(f"│  ├─ 🚀 Firebase Features:")
                print(f"│  │  ├─ 🆓 Free tier available (2M invocations/month)")
                print(f"│  │  ├─ ⚡ Auto-scaling (0 to {func.get('max_instances', self.default_max_instances)})")
                print(f"│  │  ├─ 🔐 Built-in Firebase integration")
                print(f"│  │  └─ 📊 Real-time monitoring and logs")
                
                cost = self._estimate_firebase_functions_cost()
                if cost > 0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")

        # Show existing functions being kept
        if functions_to_keep:
            print(f"\n╭─ ⚡ Existing Functions to KEEP: {len(functions_to_keep)}")
            for func in functions_to_keep:
                status_icon = "🟢" if func['status'] == 'ACTIVE' else "🟡" if func['status'] == 'DEPLOYING' else "🔴"
                trigger_icon = self._get_function_icon(func['trigger_type'])
                
                print(f"├─ {status_icon} {func['function_name']} ({trigger_icon} {func['trigger_type']})")
                print(f"│  ├─ 📁 Firebase Project: {func['firebase_project_id']}")
                print(f"│  ├─ 🔧 Runtime: {func['runtime']}")
                print(f"│  ├─ 📍 Region: {func['region']}")
                print(f"│  ├─ 💾 Memory: {func['available_memory_mb']}MB")
                print(f"│  ├─ ⏱️  Timeout: {func['timeout']}")
                print(f"│  ├─ 📊 Status: {func['status']}")
                
                # Show trigger-specific information
                trigger_config = func.get('trigger_config', {})
                if func['trigger_type'] == 'http' and 'url' in trigger_config:
                    print(f"│  ├─ 🌐 URL: {trigger_config['url']}")
                elif trigger_config.get('resource'):
                    print(f"│  ├─ 🎯 Resource: {trigger_config['resource']}")
                
                env_vars = func.get('environment_variables', {})
                if env_vars:
                    print(f"│  ├─ 🔧 Environment Variables: {len(env_vars)}")
                
                labels = func.get('labels', {})
                if labels:
                    print(f"│  ├─ 🏷️  Labels: {len(labels)}")
                
                print(f"│  ├─ 📅 Updated: {func['update_time']}")
                print(f"│  └─ 📝 Version: {func['version_id']}")
            print(f"╰─")

        # Show deployment information
        if functions_to_create:
            print(f"\n🚀 Firebase Functions Deployment:")
            print(f"   ├─ 📁 Source Directory: {self.source_directory}")
            print(f"   ├─ 🔧 Runtime: {self.runtime}")
            print(f"   ├─ 📦 Dependencies: {len(self.dependencies)} packages")
            
            # Show function type distribution
            function_types = self.get_function_types()
            if function_types:
                print(f"   ├─ 📊 Function Types:")
                for func_type, count in function_types.items():
                    type_icon = self._get_function_icon(func_type)
                    print(f"   │  ├─ {type_icon} {func_type}: {count}")
            
            # Show environment variables
            if self.environment_variables:
                print(f"   ├─ 🔧 Environment Variables: {len(self.environment_variables)}")
            
            # Show secrets
            if self.secrets:
                print(f"   ├─ 🔐 Secrets: {len(self.secrets)}")
            
            print(f"   └─ 🚀 Deploy: firebase deploy --only functions")

        # Show cost information
        print(f"\n💰 Firebase Functions Costs:")
        if functions_to_create:
            total_functions = len(functions_to_create)
            cost = self._estimate_firebase_functions_cost()
            
            print(f"   ├─ ⚡ Invocations: 2M/month free, then $0.40/million")
            print(f"   ├─ ⏱️  Compute: 400K GB-seconds/month free, then $0.0000025/GB-second")
            print(f"   ├─ 📡 Outbound data: 5GB/month free, then $0.12/GB")
            print(f"   ├─ 📊 Function count: {total_functions}")
            
            if cost > 0:
                print(f"   └─ 📊 Estimated: ${cost:.2f}/month")
            else:
                print(f"   └─ 📊 Total: Free tier (most apps)")
        else:
            print(f"   ├─ ⚡ Free tier: 2M invocations, 400K GB-seconds, 5GB outbound")
            print(f"   ├─ 💰 Pay-as-you-go: Only pay for what you use")
            print(f"   └─ 🔄 Auto-scaling: Zero cost when not in use")

        return {
            'resource_type': 'firebase_functions',
            'name': self.functions_name,
            'functions_to_create': functions_to_create,
            'functions_to_keep': functions_to_keep,
            'functions_to_update': functions_to_update,
            'existing_functions': existing_functions,
            'firebase_project_id': self.firebase_project_id,
            'runtime': self.runtime,
            'region': self.region,
            'function_count': len(self.functions),
            'estimated_cost': f"${self._estimate_firebase_functions_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update Firebase Functions"""
        if not self.firebase_project_id:
            raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
        
        existing_state = self._find_existing_functions()
        if existing_state and existing_state.get("exists", False):
            print(f"🔄 Firebase Functions '{self.functions_name}' already exist")
            return self._update_existing_functions(existing_state)
        
        print(f"🚀 Creating Firebase Functions: {self.functions_name}")
        return self._create_new_functions()

    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Functions"""
        print(f"🗑️  Destroying Firebase Functions: {self.functions_name}")

        try:
            print(f"⚠️  Firebase Functions cannot be automatically destroyed")
            print(f"🔧 To delete functions:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self.firebase_project_id}/functions/")
            print(f"   2. Delete functions manually")
            print(f"   3. Or use: firebase functions:delete [FUNCTION_NAME] --project {self.firebase_project_id}")
            
            # Remove local source files
            source_files = []
            if os.path.exists(self.source_directory):
                for func in self.functions:
                    source_file = func.get('source_file')
                    if source_file and os.path.exists(source_file):
                        source_files.append(source_file)
            
            # Remove local config files
            config_files = ["firebase.json", f"{self.source_directory}/package.json", f"{self.source_directory}/index.js"]
            removed_files = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    os.remove(config_file)
                    removed_files.append(config_file)
            
            if removed_files:
                print(f"   🗑️  Removed local files: {', '.join(removed_files)}")
            
            return {
                'success': True, 
                'functions_name': self.functions_name, 
                'status': 'manual_action_required',
                'removed_files': removed_files,
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/functions/"
            }

        except Exception as e:
            print(f"❌ Failed to destroy Firebase Functions: {str(e)}")
            return {'success': False, 'error': str(e)}

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Firebase Functions configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use minimal memory allocation
        self.memory("128MB")
        
        # Reduce timeout to minimum needed
        self.timeout(60)
        
        # Limit max instances
        self.max_instances(10)
        
        # Keep min instances at 0 (cold starts acceptable)
        self.min_instances(0)
        
        # Use cost-effective region
        self.region("us-central1")
        
        # Add cost optimization labels
        self.functions_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "tier": "free"
        })
        
        print("   ├─ 💾 Set minimal memory (128MB)")
        print("   ├─ ⏱️  Set minimal timeout (60s)")
        print("   ├─ 📈 Limited max instances (10)")
        print("   ├─ 📉 Zero min instances (cold starts)")
        print("   ├─ 🌍 Using cost-effective region")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use more memory for better performance
        self.memory("512MB")
        
        # Increase timeout for complex operations
        self.timeout(300)
        
        # Higher concurrency
        self.concurrency(80)
        
        # Keep some instances warm
        self.min_instances(1)
        
        # Higher max instances for scaling
        self.max_instances(1000)
        
        # Use execution environment gen2
        self.execution_environment = "gen2"
        
        # Add performance labels
        self.functions_labels.update({
            "optimization": "performance",
            "execution_env": "gen2",
            "warm_instances": "enabled"
        })
        
        print("   ├─ 💾 Increased memory (512MB)")
        print("   ├─ ⏱️  Extended timeout (300s)")
        print("   ├─ 🔄 Higher concurrency (80 requests/instance)")
        print("   ├─ 🔥 Warm instances (min: 1)")
        print("   ├─ 📈 Higher scaling (max: 1000)")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Require authentication
        self.require_authentication(True)
        
        # Restrict ingress
        self.ingress("ALLOW_INTERNAL_AND_GCLB")
        
        # Restrict egress
        self.egress("PRIVATE_RANGES_ONLY")
        
        # Disable CORS or restrict origins
        self.cors(False)
        
        # Use VPC connector if available
        # self.vpc_connector("projects/PROJECT/locations/REGION/connectors/CONNECTOR")
        
        # Add security labels
        self.functions_labels.update({
            "optimization": "security",
            "security_level": "maximum",
            "network_policy": "restricted",
            "auth_required": "true"
        })
        
        print("   ├─ 🔐 Required authentication")
        print("   ├─ 🌐 Restricted ingress (internal + GCLB)")
        print("   ├─ 🔒 Restricted egress (private ranges)")
        print("   ├─ 🚫 Disabled CORS")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self

    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Use moderate memory for good response times
        self.memory("256MB")
        
        # Reasonable timeout
        self.timeout(120)
        
        # Keep instances warm to avoid cold starts
        self.min_instances(1)
        
        # Allow good scaling
        self.max_instances(100)
        
        # Enable CORS for web apps
        self.cors(True)
        
        # Use optimal region (assume US-based users)
        self.region("us-central1")
        
        # Add UX labels
        self.functions_labels.update({
            "optimization": "user_experience",
            "ux_focused": "true",
            "cold_starts": "minimized",
            "response_time": "optimized"
        })
        
        print("   ├─ 💾 Balanced memory (256MB)")
        print("   ├─ ⏱️  Reasonable timeout (120s)")
        print("   ├─ 🔥 Warm instances (min: 1)")
        print("   ├─ 📈 Good scaling (max: 100)")
        print("   ├─ 🌍 Enabled CORS for web apps")
        print("   ├─ 🌐 Optimal region for users")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self

    def _find_existing_functions(self) -> Optional[Dict[str, Any]]:
        """Find existing Firebase Functions"""
        return self._fetch_current_functions_state()

    def _create_new_functions(self) -> Dict[str, Any]:
        """Create new Firebase Functions"""
        try:
            if not self.functions:
                print("⚠️  No functions configured. Use function methods like .http_function() or .firestore_trigger()")
                return {"status": "no_functions", "functions": []}
            
            print(f"   📋 Project: {self.firebase_project_id}")
            print(f"   🔧 Runtime: {self.runtime}")
            print(f"   📍 Region: {self.region}")
            print(f"   ⚡ Functions: {len(self.functions)}")
            
            # Create source directory
            os.makedirs(self.source_directory, exist_ok=True)
            
            # Create package.json
            package_json = self._create_package_json()
            package_path = os.path.join(self.source_directory, "package.json")
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            print(f"   📦 Created package.json")
            
            # Create index.js with all functions
            index_content = self._create_index_js()
            index_path = os.path.join(self.source_directory, "index.js")
            with open(index_path, 'w') as f:
                f.write(index_content)
            
            print(f"   📄 Created index.js with {len(self.functions)} functions")
            
            # Create firebase.json configuration
            firebase_config = self._create_firebase_config()
            with open("firebase.json", 'w') as f:
                json.dump(firebase_config, f, indent=2)
            
            print(f"   ⚙️  Created firebase.json")
            
            # Create .env file if environment variables exist
            if self.environment_variables:
                env_content = "\n".join([f"{key}={value}" for key, value in self.environment_variables.items()])
                env_path = os.path.join(self.source_directory, ".env")
                with open(env_path, 'w') as f:
                    f.write(env_content)
                print(f"   🔧 Created .env with {len(self.environment_variables)} variables")
            
            # Show configured functions
            print(f"   ⚡ Configured Functions:")
            function_types = self.get_function_types()
            for func_type, count in function_types.items():
                type_icon = self._get_function_icon(func_type)
                print(f"      {type_icon} {func_type}: {count}")
            
            console_url = f"https://console.firebase.google.com/project/{self.firebase_project_id}/functions/"
            print(f"✅ Firebase Functions configured successfully!")
            print(f"🚀 Deploy with: firebase deploy --only functions")
            print(f"🌐 Console: {console_url}")
            
            return self._get_functions_info()

        except Exception as e:
            print(f"❌ Failed to create Firebase Functions: {str(e)}")
            raise

    def _update_existing_functions(self, existing_state: Dict[str, Any]):
        """Update existing Firebase Functions"""
        print(f"   🔄 Updating existing configuration")
        # For Firebase Functions, we typically recreate the config
        return self._create_new_functions()

    def _create_package_json(self) -> Dict[str, Any]:
        """Create package.json for functions"""
        package_json = {
            "name": f"{self.functions_name}-functions",
            "version": "1.0.0",
            "description": f"Firebase Functions for {self.functions_name}",
            "main": "index.js",
            "engines": {
                "node": "18" if self.runtime.startswith("nodejs18") else "16"
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
            },
            "devDependencies": {}
        }
        
        # Add custom dependencies
        package_json["dependencies"].update(self.dependencies)
        package_json["devDependencies"].update(self.dev_dependencies)
        
        return package_json

    def _create_index_js(self) -> str:
        """Create index.js with all functions"""
        content = f"""const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Initialize Firebase Admin
admin.initializeApp();

// Get Firestore reference
const db = admin.firestore();

"""
        
        for func in self.functions:
            func_name = func["name"]
            func_type = func["type"]
            
            if func_type == "http":
                content += self._generate_http_function(func)
            elif func_type == "callable":
                content += self._generate_callable_function(func)
            elif func_type == "firestore":
                content += self._generate_firestore_function(func)
            elif func_type == "storage":
                content += self._generate_storage_function(func)
            elif func_type == "scheduled":
                content += self._generate_scheduled_function(func)
            elif func_type == "auth":
                content += self._generate_auth_function(func)
            elif func_type == "pubsub":
                content += self._generate_pubsub_function(func)
        
        return content

    def _generate_http_function(self, func: Dict[str, Any]) -> str:
        """Generate HTTP function code"""
        return f"""
// HTTP function: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)},
        maxInstances: {func.get('max_instances', self.default_max_instances)},
        minInstances: {func.get('min_instances', self.default_min_instances)}
    }})
    .https.onRequest(async (req, res) => {{
        try {{
            // Add CORS headers if enabled
            {self._generate_cors_headers() if self.cors_enabled else ''}
            
            // Your function logic here
            res.json({{
                message: "Hello from {func['name']}!",
                timestamp: admin.firestore.FieldValue.serverTimestamp(),
                method: req.method,
                path: req.path
            }});
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            res.status(500).json({{ error: 'Internal server error' }});
        }}
    }});
"""

    def _generate_callable_function(self, func: Dict[str, Any]) -> str:
        """Generate callable function code"""
        return f"""
// Callable function: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .https.onCall(async (data, context) => {{
        try {{
            // Check authentication
            if (!context.auth) {{
                throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
            }}
            
            const uid = context.auth.uid;
            
            // Your function logic here
            return {{
                message: "Hello from {func['name']}!",
                uid: uid,
                data: data,
                timestamp: admin.firestore.FieldValue.serverTimestamp()
            }};
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw new functions.https.HttpsError('internal', 'Internal server error');
        }}
    }});
"""

    def _generate_firestore_function(self, func: Dict[str, Any]) -> str:
        """Generate Firestore trigger function code"""
        event = func.get('event', 'create')
        document_path = func.get('document_path', 'collection/{docId}')
        
        if event == 'write':
            trigger = 'onWrite'
        elif event == 'create':
            trigger = 'onCreate'
        elif event == 'update':
            trigger = 'onUpdate'
        elif event == 'delete':
            trigger = 'onDelete'
        else:
            trigger = 'onCreate'
        
        return f"""
// Firestore trigger: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .firestore
    .document('{document_path}')
    .{trigger}(async (snap, context) => {{
        try {{
            const docId = context.params.docId || context.params.userId || 'unknown';
            console.log('{func['name']} triggered for document:', docId);
            
            // Get document data
            const data = snap.data ? snap.data() : null;
            const previousData = snap.before ? snap.before.data() : null;
            
            // Your function logic here
            console.log('Document data:', data);
            
            return null;
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw error;
        }}
    }});
"""

    def _generate_storage_function(self, func: Dict[str, Any]) -> str:
        """Generate Storage trigger function code"""
        event = func.get('event', 'finalize')
        bucket = func.get('bucket', f"{self.firebase_project_id}.appspot.com")
        
        return f"""
// Storage trigger: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .storage
    .bucket('{bucket}')
    .object()
    .on{event.title()}(async (object) => {{
        try {{
            const fileName = object.name;
            const bucketName = object.bucket;
            const contentType = object.contentType;
            
            console.log('{func['name']} triggered for file:', fileName);
            
            // Your function logic here
            console.log('File info:', {{ fileName, bucketName, contentType }});
            
            return null;
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw error;
        }}
    }});
"""

    def _generate_scheduled_function(self, func: Dict[str, Any]) -> str:
        """Generate scheduled function code"""
        schedule = func.get('schedule', '0 2 * * *')
        timezone = func.get('timezone', 'UTC')
        
        return f"""
// Scheduled function: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .pubsub
    .schedule('{schedule}')
    .timeZone('{timezone}')
    .onRun(async (context) => {{
        try {{
            console.log('{func['name']} scheduled function executed at:', new Date().toISOString());
            
            // Your scheduled task logic here
            
            return null;
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw error;
        }}
    }});
"""

    def _generate_auth_function(self, func: Dict[str, Any]) -> str:
        """Generate Auth trigger function code"""
        event = func.get('event', 'create')
        
        if event == 'create':
            trigger = 'beforeCreate'
            event_type = 'onCreate'
        else:
            trigger = 'beforeDelete'
            event_type = 'onDelete'
        
        return f"""
// Auth trigger: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .auth
    .user()
    .{event_type}(async (user) => {{
        try {{
            const uid = user.uid;
            const email = user.email;
            
            console.log('{func['name']} triggered for user:', uid);
            
            // Your auth event logic here
            console.log('User info:', {{ uid, email }});
            
            return null;
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw error;
        }}
    }});
"""

    def _generate_pubsub_function(self, func: Dict[str, Any]) -> str:
        """Generate Pub/Sub trigger function code"""
        topic = func.get('topic', 'my-topic')
        
        return f"""
// Pub/Sub trigger: {func['name']}
exports.{func['name']} = functions
    .region('{self.region}')
    .runWith({{
        memory: '{func.get('memory', self.default_memory)}',
        timeoutSeconds: {func.get('timeout', self.default_timeout)}
    }})
    .pubsub
    .topic('{topic}')
    .onPublish(async (message) => {{
        try {{
            const data = message.data ? Buffer.from(message.data, 'base64').toString() : null;
            const attributes = message.attributes;
            
            console.log('{func['name']} triggered with message:', data);
            
            // Your message processing logic here
            console.log('Message attributes:', attributes);
            
            return null;
        }} catch (error) {{
            console.error('Error in {func['name']}:', error);
            throw error;
        }}
    }});
"""

    def _generate_cors_headers(self) -> str:
        """Generate CORS headers"""
        origins = ', '.join([f'"{origin}"' for origin in self.cors_origins])
        return f"""
            res.set('Access-Control-Allow-Origin', '*');
            res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
            res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
            
            if (req.method === 'OPTIONS') {{
                res.status(204).send('');
                return;
            }}
"""

    def _create_firebase_config(self) -> Dict[str, Any]:
        """Create firebase.json configuration"""
        return {
            "functions": {
                "source": self.source_directory,
                "runtime": self.runtime,
                "predeploy": [
                    "npm --prefix \"$RESOURCE_DIR\" run lint"
                ],
                "postdeploy": [
                    "npm --prefix \"$RESOURCE_DIR\" run test"
                ]
            },
            "emulators": {
                "functions": {
                    "port": 5001
                },
                "ui": {
                    "enabled": True
                }
            }
        }

    def _get_function_icon(self, function_type: str) -> str:
        """Get icon for function type"""
        icons = {
            "http": "🌐",
            "callable": "📞",
            "firestore": "🔥",
            "storage": "📁",
            "scheduled": "⏰",
            "auth": "🔐",
            "pubsub": "📡",
            "event": "🔄"
        }
        return icons.get(function_type, "⚡")

    def _get_functions_info(self) -> Dict[str, Any]:
        """Get functions information"""
        try:
            return {
                'success': True,
                'functions_name': self.functions_name,
                'firebase_project_id': self.firebase_project_id,
                'functions_description': self.functions_description,
                'runtime': self.runtime,
                'region': self.region,
                'functions': self.functions,
                'function_count': len(self.functions),
                'function_types': self.get_function_types(),
                'has_http_functions': self.has_http_functions(),
                'has_trigger_functions': self.has_trigger_functions(),
                'has_scheduled_functions': self.has_scheduled_functions(),
                'is_production_ready': self.is_production_ready(),
                'environment_variables': self.environment_variables,
                'dependencies': self.dependencies,
                'default_memory': self.default_memory,
                'default_timeout': self.default_timeout,
                'labels': self.functions_labels,
                'estimated_monthly_cost': f"${self._estimate_firebase_functions_cost():.2f}",
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/functions/"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}