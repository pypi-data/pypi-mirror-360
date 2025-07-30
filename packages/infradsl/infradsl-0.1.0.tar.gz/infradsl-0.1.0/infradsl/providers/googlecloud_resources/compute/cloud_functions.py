from typing import Dict, Any, Optional, List
from ..base_resource import BaseGcpResource
from ...googlecloud_managers.compute.cloud_functions_manager import CloudFunctionsManager, FunctionConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter


class CloudFunctions(BaseGcpResource):
    """Rails-like Cloud Functions orchestrator - serverless computing made simple"""

    def __init__(self, function_name: str):
        self.config = FunctionConfig(function_name=function_name)
        self.status_reporter = GcpStatusReporter()
        super().__init__(function_name)

    def _initialize_managers(self):
        """Initialize Cloud Functions specific managers"""
        self.functions_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.functions_manager = CloudFunctionsManager(self.gcp_client)

    def source(self, source_path: str) -> 'CloudFunctions':
        """Set source code path"""
        self.config.source_path = source_path
        return self

    def runtime(self, runtime: str) -> 'CloudFunctions':
        """Set runtime (e.g., 'python39', 'nodejs16', 'go119')"""
        self.config.runtime = runtime
        return self

    def entry_point(self, entry_point: str) -> 'CloudFunctions':
        """Set entry point function name"""
        self.config.entry_point = entry_point
        return self

    def region(self, region: str) -> 'CloudFunctions':
        """Set deployment region"""
        self.config.region = region
        return self

    def memory(self, memory: str) -> 'CloudFunctions':
        """Set memory allocation (e.g., '256MB', '1GB')"""
        self.config.memory = memory
        return self

    def timeout(self, timeout: str) -> 'CloudFunctions':
        """Set function timeout (e.g., '60s', '5m')"""
        self.config.timeout = timeout
        return self

    def max_instances(self, instances: int) -> 'CloudFunctions':
        """Set maximum concurrent instances"""
        self.config.max_instances = instances
        return self

    def min_instances(self, instances: int) -> 'CloudFunctions':
        """Set minimum instances (keep warm)"""
        self.config.min_instances = instances
        return self

    def environment(self, env_vars: Dict[str, str]) -> 'CloudFunctions':
        """Set environment variables"""
        self.config.environment_variables = env_vars
        return self

    def service_account(self, email: str) -> 'CloudFunctions':
        """Set service account for function execution"""
        self.config.service_account = email
        return self

    def labels(self, labels: Dict[str, str]) -> 'CloudFunctions':
        """Add labels to the function"""
        self.config.labels = labels
        return self

    def description(self, description: str) -> 'CloudFunctions':
        """Set function description"""
        self.config.description = description
        return self

    def trigger(self, trigger_type: str, **kwargs) -> 'CloudFunctions':
        """Configure function trigger with flexible options."""
        self.config.trigger_type = trigger_type
        self.config.trigger_config = kwargs

        # Set function type based on common trigger patterns
        if trigger_type == "http":
            self.config.function_type = "api"
        elif trigger_type in ["storage", "pubsub", "firestore"]:
            self.config.function_type = "processor"
        elif trigger_type == "schedule":
            self.config.function_type = "scheduled"

        return self

    # Trigger configuration methods (now use the generic trigger method)
    def http_trigger(self) -> 'CloudFunctions':
        """Configure HTTP trigger (Rails convention)"""
        return self.trigger("http")

    def storage_trigger(self, bucket: str, event_type: str = "google.storage.object.finalize") -> 'CloudFunctions':
        """Configure Cloud Storage trigger"""
        return self.trigger("storage", bucket=bucket, event_type=event_type)

    def pubsub_trigger(self, topic: str) -> 'CloudFunctions':
        """Configure Pub/Sub trigger"""
        return self.trigger("pubsub", topic=topic)

    def firestore_trigger(self, document: str, event_type: str = "providers/cloud.firestore/eventTypes/document.create") -> 'CloudFunctions':
        """Configure Firestore trigger"""
        return self.trigger("firestore", document=document, event_type=event_type)

    def schedule_trigger(self, schedule: str) -> 'CloudFunctions':
        """Configure scheduled trigger (cron-like)"""
        # Note: This requires Cloud Scheduler + Pub/Sub setup
        # For simplicity, we'll create a topic and schedule
        topic_name = f"{self.config.function_name}-schedule"
        return self.trigger("schedule", topic=topic_name, schedule=schedule)

    # Rails-like convenience methods
    def http(self) -> 'CloudFunctions':
        """Rails convenience: HTTP trigger with API optimizations"""
        return self.http_trigger().api_function()

    def webhook(self) -> 'CloudFunctions':
        """Rails convenience: Webhook with fast response optimizations"""
        return self.http_trigger().webhook_function()

    def processor(self) -> 'CloudFunctions':
        """Rails convenience: Data processor with higher memory"""
        return self.processor_function()

    def scheduled(self, schedule: str = "0 2 * * *") -> 'CloudFunctions':
        """Rails convenience: Scheduled function (daily at 2 AM by default)"""
        return self.schedule_trigger(schedule).scheduled_function()

    # Rails-like function type conventions
    def api_function(self) -> 'CloudFunctions':
        """Configure for API workloads (Rails convention)"""
        self.config.function_type = "api"
        self.config.memory = "512MB"
        self.config.timeout = "60s"
        self.config.max_instances = 100
        self.config.ingress_settings = "ALLOW_ALL"
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update({
            "function_type": "api",
            "scaling": "demand"
        })
        return self

    def processor_function(self) -> 'CloudFunctions':
        """Configure for data processing workloads"""
        self.config.function_type = "processor"
        self.config.memory = "1GB"
        self.config.timeout = "540s"  # 9 minutes
        self.config.max_instances = 10
        self.config.ingress_settings = "ALLOW_INTERNAL_ONLY"
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update({
            "function_type": "processor",
            "workload": "batch"
        })
        return self

    def webhook_function(self) -> 'CloudFunctions':
        """Configure for webhook workloads"""
        self.config.function_type = "webhook"
        self.config.memory = "256MB"
        self.config.timeout = "30s"
        self.config.max_instances = 50
        self.config.min_instances = 1  # Keep warm
        self.config.ingress_settings = "ALLOW_ALL"
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update({
            "function_type": "webhook",
            "latency": "low"
        })
        return self

    def scheduled_function(self) -> 'CloudFunctions':
        """Configure for scheduled tasks"""
        self.config.function_type = "scheduled"
        self.config.memory = "512MB"
        self.config.timeout = "300s"  # 5 minutes
        self.config.max_instances = 1  # Only one instance
        self.config.ingress_settings = "ALLOW_INTERNAL_ONLY"
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update({
            "function_type": "scheduled",
            "trigger": "cron"
        })
        return self

    def etl_function(self) -> 'CloudFunctions':
        """Configure for ETL workloads"""
        self.config.function_type = "etl"
        self.config.memory = "2GB"
        self.config.timeout = "540s"
        self.config.max_instances = 5
        self.config.ingress_settings = "ALLOW_INTERNAL_ONLY"
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update({
            "function_type": "etl",
            "workload": "data-processing"
        })
        return self

    # Runtime convenience methods
    def python(self, version: str = "39") -> 'CloudFunctions':
        """Set Python runtime (Rails convention)"""
        self.config.runtime = f"python{version}"
        return self

    def nodejs(self, version: str = "16") -> 'CloudFunctions':
        """Set Node.js runtime (Rails convention)"""
        self.config.runtime = f"nodejs{version}"
        return self

    def go(self, version: str = "119") -> 'CloudFunctions':
        """Set Go runtime (Rails convention)"""
        self.config.runtime = f"go{version}"
        return self

    def java(self, version: str = "11") -> 'CloudFunctions':
        """Set Java runtime (Rails convention)"""
        self.config.runtime = f"java{version}"
        return self

    # Scaling convenience methods
    def scale_to_zero(self) -> 'CloudFunctions':
        """Configure to scale to zero when not used"""
        self.config.min_instances = 0
        return self

    def keep_warm(self, instances: int = 1) -> 'CloudFunctions':
        """Keep minimum instances warm"""
        self.config.min_instances = instances
        return self

    def high_availability(self) -> 'CloudFunctions':
        """Configure for high availability"""
        self.config.min_instances = 2
        self.config.max_instances = 100
        return self

    # Security convenience methods
    def public_access(self) -> 'CloudFunctions':
        """Allow public access (Rails convention)"""
        self.config.ingress_settings = "ALLOW_ALL"
        return self

    def internal_only(self) -> 'CloudFunctions':
        """Allow internal access only"""
        self.config.ingress_settings = "ALLOW_INTERNAL_ONLY"
        return self

    def load_balancer_only(self) -> 'CloudFunctions':
        """Allow access from load balancer only"""
        self.config.ingress_settings = "ALLOW_INTERNAL_AND_GCLB"
        return self

    # Rails-like optimization methods
    def optimize_for(self, workload: str) -> 'CloudFunctions':
        """Apply optimization for specific workload type"""
        if not self.functions_manager:
            try:
                self._ensure_authenticated()
            except:
                # For testing without authentication, use default optimization
                pass

        if self.functions_manager:
            optimization = self.functions_manager.get_smart_function_configuration(workload)
        else:
            # Default optimization for testing
            optimization = {
                "memory": "512MB",
                "timeout": "60s",
                "max_instances": 10,
                "suggested_labels": {"optimization": workload}
            }

        # Apply optimization settings
        if optimization.get("memory"):
            self.config.memory = optimization["memory"]
        if optimization.get("timeout"):
            self.config.timeout = optimization["timeout"]
        if optimization.get("max_instances"):
            self.config.max_instances = optimization["max_instances"]
        if optimization.get("min_instances"):
            self.config.min_instances = optimization["min_instances"]
        if optimization.get("ingress_settings"):
            self.config.ingress_settings = optimization["ingress_settings"]

        # Add optimization labels
        if not self.config.labels:
            self.config.labels = {}
        self.config.labels.update(optimization.get("suggested_labels", {}))

        return self

    # Preview and creation methods
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed"""
        try:
            self._ensure_authenticated()

            # Discover existing functions to determine what will happen
            existing_functions = self._discover_existing_functions()
            
            # Determine what will happen
            function_exists = self.config.function_name in existing_functions
            to_create = [] if function_exists else [self.config.function_name]
            to_keep = [self.config.function_name] if function_exists else []
            to_remove = [name for name in existing_functions.keys() if name != self.config.function_name]

            # Print simple header without formatting
            print(f"🔍 Cloud Functions Preview")

            # Show infrastructure changes (only actionable changes)
            changes_needed = to_create or to_remove
            
            if changes_needed:
                print(f"📋 Infrastructure Changes:")
                
                if to_create:
                    print(f"🆕 FUNCTIONS to CREATE:  {', '.join(to_create)}")
                    # Show details about function being created
                    print(f"   ╭─ ⚡ {self.config.function_name}")
                    print(f"   ├─ 🏃 Runtime: {self.config.runtime}")
                    print(f"   ├─ 🎯 Trigger: {self.config.trigger_type}")
                    print(f"   ├─ 💾 Memory: {self.config.memory}")
                    print(f"   ├─ ⏱️  Timeout: {self.config.timeout}")
                    print(f"   ├─ 📍 Region: {self.config.region}")
                    print(f"   ├─ 📊 Max Instances: {self.config.max_instances}")
                    if self.config.min_instances > 0:
                        print(f"   ├─ 🔥 Min Instances: {self.config.min_instances}")
                    if self.config.function_type:
                        print(f"   ├─ 🏷️  Type: {self.config.function_type}")
                    print(f"   ╰─ 📂 Source: {self.config.source_path or 'inline'}")
                    print()
                    
                if to_remove:
                    print(f"🗑️  FUNCTIONS to REMOVE:")
                    # Show details about functions being removed
                    for function_name in to_remove:
                        function_info = existing_functions.get(function_name)
                        if function_info:
                            runtime = function_info.get('runtime', 'unknown')
                            status = function_info.get('status', 'unknown')
                            update_time = function_info.get('update_time', 'unknown')
                            
                            # Pretty format with box drawing
                            print(f"   ╭─ ⚡ {function_name}")
                            print(f"   ├─ 🏃 Runtime: {runtime}")
                            print(f"   ├─ 🔄 Status: {status}")
                            print(f"   ├─ 📅 Updated: {update_time}")
                            print(f"   ╰─ ⚠️  Will delete function and all versions")
                            print()
            else:
                print(f"✨ No changes needed - infrastructure matches configuration")

            # Show unchanged functions summary
            if to_keep:
                print(f"📋 Unchanged: {len(to_keep)} function(s) remain the same")

            return {
                "function_name": self.config.function_name,
                "to_create": to_create,
                "to_keep": to_keep,
                "to_remove": to_remove,
                "existing_functions": existing_functions,
                "runtime": self.config.runtime,
                "trigger_type": self.config.trigger_type,
                "trigger_config": self.config.trigger_config,
                "memory": self.config.memory,
                "timeout": self.config.timeout,
                "max_instances": self.config.max_instances,
                "min_instances": self.config.min_instances,
                "function_type": self.config.function_type,
                "region": self.config.region,
                "source_path": self.config.source_path,
                "environment_variables": self.config.environment_variables,
                "service_account": self.config.service_account,
                "ingress_settings": self.config.ingress_settings,
                "labels": self.config.labels or {},
                "description": self.config.description
            }

        except Exception as e:
            print(f"❌ Preview failed: {str(e)}")
            raise

    def create(self) -> Dict[str, Any]:
        """Create/update Cloud Function and remove any that are no longer needed"""
        self._ensure_authenticated()

        # Discover existing functions to determine what changes are needed
        existing_functions = self._discover_existing_functions()
        function_exists = self.config.function_name in existing_functions
        to_create = [] if function_exists else [self.config.function_name]
        to_remove = [name for name in existing_functions.keys() if name != self.config.function_name]

        # Show infrastructure changes
        print(f"\n🔍 Cloud Functions")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 FUNCTIONS to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  FUNCTIONS to REMOVE:")
                # Show details about functions being removed
                for function_name in to_remove:
                    function_info = existing_functions.get(function_name)
                    if function_info:
                        runtime = function_info.get('runtime', 'unknown')
                        status = function_info.get('status', 'unknown')
                        update_time = function_info.get('update_time', 'unknown')
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ ⚡ {function_name}")
                        print(f"   ├─ 🏃 Runtime: {runtime}")
                        print(f"   ├─ 🔄 Status: {status}")
                        print(f"   ├─ 📅 Updated: {update_time}")
                        print(f"   ╰─ ⚠️  Will delete function and all versions")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        try:
            # Remove functions that are no longer needed
            for function_name in to_remove:
                print(f"🗑️  Removing function: {function_name}")
                try:
                    if self.functions_manager is not None:
                        self.functions_manager.delete_function(function_name, self.config.region)
                        print(f"✅ Function removed successfully: {function_name}")
                    else:
                        raise RuntimeError("Functions manager not initialized")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to remove function {function_name}: {str(e)}")

            # Create/update the function that is in the configuration
            if function_exists:
                print(f"🔄 Updating function: {self.config.function_name}")
            else:
                print(f"🆕 Creating function: {self.config.function_name}")

            # Deploy function
            if self.functions_manager is not None:
                function_result = self.functions_manager.deploy_function(self.config)
            else:
                raise RuntimeError("Functions manager not initialized")

            print(f"✅ Function ready: {self.config.function_name}")
            print(f"   🎯 Trigger: {self.config.trigger_type}")
            if function_result.get("https_url"):
                print(f"   🌐 URL: {function_result['https_url']}")

            # Add change tracking to result
            function_result["changes"] = {
                "created": to_create,
                "removed": to_remove,
                "updated": [self.config.function_name] if function_exists else []
            }

            return function_result

        except Exception as e:
            print(f"❌ Cloud Function deployment failed: {str(e)}")
            raise

    def _discover_existing_functions(self) -> Dict[str, Any]:
        """Discover existing Cloud Functions that might be related to this configuration"""
        try:
            existing_functions = {}
            
            if not self.functions_manager:
                return existing_functions
            
            # List all Cloud Functions in the current project and region
            # For Google Cloud Functions, we need to check specific regions or all regions
            regions_to_check = [self.config.region] if self.config.region else ['us-central1', 'us-east1', 'europe-west1']
            
            for region in regions_to_check:
                try:
                    # Get functions in this region using the functions manager
                    functions_in_region = self.functions_manager.list_functions(region)
                    
                    # Filter functions that might be related to this configuration
                    # We look for functions that either:
                    # 1. Have the exact same name as our function
                    # 2. Match our naming pattern (same base name with different suffixes)
                    # 3. Have InfraDSL-related labels
                    
                    base_name = self.config.function_name.lower().replace('_', '-')
                    
                    for function_data in functions_in_region:
                        function_name = function_data.get('name', '')
                        # Extract function name from full resource name if needed
                        if '/' in function_name:
                            function_name = function_name.split('/')[-1]
                        
                        # Check if this function might be related
                        is_related = False
                        
                        # 1. Exact match
                        if function_name == self.config.function_name:
                            is_related = True
                        
                        # 2. Naming pattern match (same base name)
                        elif base_name in function_name.lower():
                            is_related = True
                        
                        # 3. Check labels for InfraDSL managed functions
                        labels = function_data.get('labels', {})
                        if any(label_key.lower() in ['infradsl', 'managedby'] for label_key in labels.keys()):
                            is_related = True
                        
                        if is_related:
                            # Parse update time
                            update_time = 'unknown'
                            if function_data.get('updateTime'):
                                try:
                                    from datetime import datetime
                                    # Google Cloud timestamps are in RFC3339 format
                                    dt = datetime.fromisoformat(function_data['updateTime'].replace('Z', '+00:00'))
                                    update_time = dt.strftime('%Y-%m-%d %H:%M')
                                except Exception:
                                    pass
                            
                            existing_functions[function_name] = {
                                'function_name': function_name,
                                'runtime': function_data.get('runtime', 'unknown'),
                                'status': function_data.get('status', 'unknown'),
                                'update_time': update_time,
                                'region': region,
                                'trigger': function_data.get('trigger', {}),
                                'labels': labels,
                                'source_archive_url': function_data.get('sourceArchiveUrl', ''),
                                'https_trigger': function_data.get('httpsTrigger', {}),
                                'environment_variables': function_data.get('environmentVariables', {})
                            }
                            
                except Exception as e:
                    # Skip regions that fail (might not have functions or permissions)
                    print(f"   ⚠️  Warning: Failed to list functions in {region}: {str(e)}")
                    continue
            
            return existing_functions
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing Cloud Functions: {str(e)}")
            return {}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Cloud Function (required by BaseGcpResource)"""
        try:
            result = self.delete(force=True)
            return {
                "function_name": self.config.function_name,
                "destroyed": result,
                "status": "destroyed" if result else "failed"
            }
        except Exception as e:
            return {
                "function_name": self.config.function_name,
                "destroyed": False,
                "status": "failed",
                "error": str(e)
            }

    def delete(self, force: bool = False) -> bool:
        """Delete the Cloud Function"""
        self._ensure_authenticated()

        try:
            if not force:
                self.status_reporter.warning("⚠️ This will delete the Cloud Function")
                self.status_reporter.warning("⚠️ Use .delete(force=True) to confirm")
                return False

            if self.functions_manager is not None:
                result = self.functions_manager.delete_function(
                    self.config.function_name,
                    self.config.region
                )
            else:
                raise RuntimeError("Functions manager not initialized")

            if result:
                self.status_reporter.success(f"✅ Function '{self.config.function_name}' deleted")

            return result

        except Exception as e:
            self.status_reporter.error(f"❌ Delete failed: {str(e)}")
            raise

    def info(self) -> Dict[str, Any]:
        """Get information about the function"""
        self._ensure_authenticated()

        try:
            if self.functions_manager is not None:
                return self.functions_manager.get_function_info(
                    self.config.function_name,
                    self.config.region
                )
            else:
                raise RuntimeError("Functions manager not initialized")
        except Exception as e:
            self.status_reporter.error(f"❌ Failed to get function info: {str(e)}")
            raise

    # Rails-like connection and integration methods
    def trigger_url(self) -> str:
        """Get the trigger URL for HTTP functions"""
        if self.config.trigger_type != "http":
            raise ValueError("trigger_url() only available for HTTP functions")

        try:
            info = self.info()
            return info.get("https_url", "")
        except:
            # Return expected URL format if not deployed yet
            return f"https://{self.config.region}-{self.gcp_client.project if self.gcp_client else 'PROJECT'}.cloudfunctions.net/{self.config.function_name}"

    def curl_example(self) -> str:
        """Generate curl example for HTTP functions"""
        if self.config.trigger_type != "http":
            return "# This function is not HTTP-triggered"

        url = self.trigger_url()
        return f"""# Curl example for {self.config.function_name}
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{{"message": "Hello from InfraDSL!"}}' \
  {url}"""

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the function from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get function info if it exists
            if self.functions_manager:
                function_info = self.functions_manager.get_function_info(
                    self.config.function_name,
                    self.config.region
                )
                
                if function_info.get("exists", False):
                    return {
                        "exists": True,
                        "function_name": self.config.function_name,
                        "runtime": function_info.get("runtime"),
                        "status": function_info.get("status"),
                        "region": function_info.get("region", self.config.region),
                        "memory": function_info.get("available_memory_mb"),
                        "timeout": function_info.get("timeout"),
                        "entry_point": function_info.get("entry_point"),
                        "source_archive_url": function_info.get("source_archive_url"),
                        "https_url": function_info.get("https_url"),
                        "trigger_type": "http" if function_info.get("https_trigger") else "other",
                        "environment_variables": function_info.get("environment_variables", {}),
                        "labels": function_info.get("labels", {}),
                        "update_time": function_info.get("update_time"),
                        "version_id": function_info.get("version_id")
                    }
                else:
                    return {
                        "exists": False,
                        "function_name": self.config.function_name
                    }
            else:
                return {
                    "exists": False,
                    "function_name": self.config.function_name,
                    "error": "Functions manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch function state: {str(e)}")
            return {
                "exists": False,
                "function_name": self.config.function_name,
                "error": str(e)
            }
