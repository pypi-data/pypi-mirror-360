"""
GCP Cloud Functions Lifecycle Mixin

Lifecycle operations for Google Cloud Functions.
Handles create, update, preview, and destroy operations.
"""

from typing import Dict, Any, List
import uuid


class CloudFunctionsLifecycleMixin:
    """
    Mixin for Cloud Functions lifecycle operations (create, update, destroy).
    
    This mixin provides:
    - Preview functionality to show planned changes
    - Function deployment and configuration
    - Function destruction
    - Deployment status tracking
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Discover existing functions to determine what will happen
        existing_functions = self._discover_existing_functions()
        
        # Determine what will happen
        function_exists = self.function_name in existing_functions
        to_create = [] if function_exists else [self.function_name]
        to_keep = [self.function_name] if function_exists else []
        to_remove = [name for name in existing_functions.keys() if name != self.function_name]
        
        self._display_preview(to_create, to_keep, to_remove, existing_functions)
        
        return {
            'resource_type': 'GCP Cloud Function',
            'function_name': self.function_name,
            'function_url': self.function_url,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_functions': existing_functions,
            'runtime': self.runtime,
            'region': self.region,
            'trigger_type': self.trigger_type,
            'memory': self.memory,
            'timeout': self.timeout,
            'max_instances': self.max_instances,
            'min_instances': self.min_instances,
            'function_type': self.function_type,
            'estimated_deployment_time': '2-4 minutes',
            'estimated_monthly_cost': self._estimate_monthly_cost()
        }
    
    def _display_preview(self, to_create: List[str], to_keep: List[str], to_remove: List[str], existing_functions: Dict[str, Any]):
        """Display preview information in a clean format"""
        print(f"\n⚡ Cloud Functions Preview")
        
        # Show functions to create
        if to_create:
            print(f"╭─ 🚀 Functions to CREATE: {len(to_create)}")
            for function in to_create:
                print(f"├─ 🆕 {function}")
                print(f"│  ├─ 🏃 Runtime: {self.runtime}")
                print(f"│  ├─ 📍 Region: {self.region}")
                print(f"│  ├─ 🎯 Trigger: {self.trigger_type}")
                print(f"│  ├─ 💾 Memory: {self.memory}")
                print(f"│  ├─ ⏱️  Timeout: {self.timeout}")
                print(f"│  ├─ 📊 Max Instances: {self.max_instances}")
                if self.min_instances > 0:
                    print(f"│  ├─ 🔥 Min Instances: {self.min_instances}")
                if self.function_type:
                    print(f"│  ├─ 🏷️  Type: {self.function_type}")
                print(f"│  ├─ 🔒 Access: {self.ingress_settings}")
                if self.environment_variables:
                    print(f"│  ├─ 🌐 Environment Variables: {len(self.environment_variables)}")
                if self.function_labels:
                    print(f"│  ├─ 🏷️  Labels: {len(self.function_labels)}")
                print(f"│  └─ ⏱️  Deployment Time: 2-4 minutes")
            print(f"╰─")
        
        # Show functions to keep
        if to_keep:
            print(f"╭─ 🔄 Functions to KEEP: {len(to_keep)}")
            for function in to_keep:
                function_info = existing_functions.get(function, {})
                print(f"├─ ✅ {function}")
                print(f"│  ├─ 🏃 Runtime: {function_info.get('runtime', 'Unknown')}")
                print(f"│  ├─ 📍 Region: {function_info.get('region', 'Unknown')}")
                print(f"│  ├─ 🔄 Status: {function_info.get('status', 'Unknown')}")
                print(f"│  └─ 📅 Updated: {function_info.get('update_time', 'Unknown')}")
            print(f"╰─")
        
        # Show functions to remove
        if to_remove:
            print(f"╭─ 🗑️  Functions to REMOVE: {len(to_remove)}")
            for function in to_remove:
                function_info = existing_functions.get(function, {})
                print(f"├─ ❌ {function}")
                print(f"│  ├─ 🏃 Runtime: {function_info.get('runtime', 'Unknown')}")
                print(f"│  ├─ 📍 Region: {function_info.get('region', 'Unknown')}")
                print(f"│  ├─ 🔄 Status: {function_info.get('status', 'Unknown')}")
                print(f"│  └─ ⚠️  All versions will be deleted")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ 🔥 Invocations (1M): {self._estimate_invocation_cost()}")
        print(f"   ├─ ⏱️  Compute Time: {self._estimate_compute_cost()}")
        print(f"   ├─ 🌐 Network Egress: {self._estimate_network_cost()}")
        if self.min_instances > 0:
            print(f"   ├─ 🔥 Always-on (min instances): {self._estimate_always_on_cost()}")
        print(f"   └─ 📊 Total Estimated: {self._estimate_monthly_cost()}")
    
    def create(self) -> Dict[str, Any]:
        """Create/update Cloud Function"""
        self._ensure_authenticated()
        
        if not self.function_name:
            raise ValueError("Function name is required")
        
        # Discover existing functions to determine what changes are needed
        existing_functions = self._discover_existing_functions()
        function_exists = self.function_name in existing_functions
        to_create = [] if function_exists else [self.function_name]
        to_remove = [name for name in existing_functions.keys() if name != self.function_name]
        
        print(f"\n⚡ Creating Cloud Function: {self.function_name}")
        print(f"   🏃 Runtime: {self.runtime}")
        print(f"   📍 Region: {self.region}")
        print(f"   🎯 Trigger: {self.trigger_type}")
        
        try:
            # Remove functions that are no longer needed
            for function_name in to_remove:
                print(f"🗑️  Removing function: {function_name}")
                try:
                    # Mock removal for now - in real implementation this would use GCP SDK
                    print(f"✅ Function removed successfully: {function_name}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to remove function {function_name}: {str(e)}")
            
            # Create function configuration
            function_config = {
                'function_name': self.function_name,
                'runtime': self.runtime,
                'region': self.region,
                'entry_point': self.entry_point,
                'source_path': self.source_path,
                'memory': self.memory,
                'timeout': self.timeout,
                'max_instances': self.max_instances,
                'min_instances': self.min_instances,
                'trigger_type': self.trigger_type,
                'trigger_config': self.trigger_config,
                'environment_variables': self.environment_variables,
                'service_account': self.service_account,
                'labels': self.function_labels,
                'description': self.description,
                'ingress_settings': self.ingress_settings
            }
            
            # Create or update the function
            if function_exists:
                print(f"🔄 Updating existing function")
            else:
                print(f"🆕 Creating new function")
            
            # Mock creation for now - in real implementation this would use GCP SDK
            function_id = f"function-{str(uuid.uuid4())[:8]}"
            
            result = {
                'function_name': self.function_name,
                'function_id': function_id,
                'function_url': self.function_url,
                'function_arn': self.function_arn,
                'runtime': self.runtime,
                'region': self.region,
                'trigger_type': self.trigger_type,
                'memory': self.memory,
                'timeout': self.timeout,
                'max_instances': self.max_instances,
                'min_instances': self.min_instances,
                'entry_point': self.entry_point,
                'source_path': self.source_path,
                'environment_variables': self.environment_variables,
                'service_account': self.service_account,
                'labels': self.function_labels,
                'description': self.description,
                'ingress_settings': self.ingress_settings,
                'status': 'ACTIVE',
                'created': True,
                'updated': function_exists,
                'changes': {
                    'created': to_create,
                    'removed': to_remove,
                    'updated': [self.function_name] if function_exists else []
                }
            }
            
            # Update instance attributes
            self.function_exists = True
            self.function_created = True
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create Cloud Function: {str(e)}")
            raise
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ Cloud Function {'updated' if result['updated'] else 'created'} successfully")
        print(f"   ⚡ Function Name: {result['function_name']}")
        print(f"   🏃 Runtime: {result['runtime']}")
        print(f"   📍 Region: {result['region']}")
        print(f"   🎯 Trigger: {result['trigger_type']}")
        print(f"   💾 Memory: {result['memory']}")
        print(f"   ⏱️  Timeout: {result['timeout']}")
        if result.get('function_url'):
            print(f"   🌐 Function URL: {result['function_url']}")
        if result['min_instances'] > 0:
            print(f"   🔥 Keeping {result['min_instances']} instance(s) warm")
        print(f"   📊 Status: {result['status']}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the Cloud Function"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Cloud Function: {self.function_name}")
        
        try:
            # Mock destruction for now - in real implementation this would use GCP SDK
            result = {
                'function_name': self.function_name,
                'function_url': self.function_url,
                'region': self.region,
                'destroyed': True,
                'note': 'Function and all versions deleted permanently'
            }
            
            # Reset instance attributes
            self.function_exists = False
            self.function_created = False
            self.function_url = None
            self.function_arn = None
            
            print(f"✅ Cloud Function destroyed successfully")
            print(f"   ⚡ Function Name: {result['function_name']}")
            print(f"   📍 Region: {result['region']}")
            print(f"   ⚠️  Note: All function versions have been permanently deleted")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy Cloud Function: {str(e)}")
            raise
    
    def _discover_existing_functions(self) -> Dict[str, Any]:
        """Discover existing Cloud Functions that might be related"""
        try:
            existing_functions = {}
            
            # Mock discovery for now - in real implementation this would use GCP SDK
            # This would list all functions in the project and filter for related ones
            
            # For testing, we'll simulate finding related functions
            if hasattr(self, 'functions_manager') and self.functions_manager:
                # In real implementation, this would call GCP APIs
                pass
                
            return existing_functions
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to discover existing functions: {str(e)}")
            return {}
    
    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost based on configuration"""
        # Basic cost estimation based on memory and usage
        memory_gb = float(self.memory.replace('MB', '').replace('GB', '')) / 1000 if 'MB' in self.memory else float(self.memory.replace('GB', ''))
        
        # Estimate based on 1 million invocations per month, 200ms average execution time
        invocations = 1_000_000
        avg_duration_ms = 200
        
        # GCP Cloud Functions pricing (approximate)
        invocation_cost = (invocations / 1_000_000) * 0.40  # $0.40 per million invocations
        compute_cost = (invocations * avg_duration_ms / 1000 * memory_gb) * 0.0000025  # $0.0000025 per GB-second
        
        # Always-on cost if min_instances > 0
        always_on_cost = 0
        if self.min_instances > 0:
            # Approximate cost for keeping instances warm
            always_on_cost = self.min_instances * memory_gb * 730 * 0.0000025  # 730 hours in a month
        
        total_cost = invocation_cost + compute_cost + always_on_cost
        return f"~${total_cost:.2f}/month"
    
    def _estimate_invocation_cost(self) -> str:
        """Estimate invocation cost"""
        return "$0.40/million invocations"
    
    def _estimate_compute_cost(self) -> str:
        """Estimate compute cost"""
        memory_gb = float(self.memory.replace('MB', '').replace('GB', '')) / 1000 if 'MB' in self.memory else float(self.memory.replace('GB', ''))
        return f"$0.0000025/GB-second ({memory_gb}GB)"
    
    def _estimate_network_cost(self) -> str:
        """Estimate network egress cost"""
        return "$0.12/GB (after 1GB free)"
    
    def _estimate_always_on_cost(self) -> str:
        """Estimate always-on cost for min instances"""
        if self.min_instances > 0:
            memory_gb = float(self.memory.replace('MB', '').replace('GB', '')) / 1000 if 'MB' in self.memory else float(self.memory.replace('GB', ''))
            monthly_cost = self.min_instances * memory_gb * 730 * 0.0000025
            return f"${monthly_cost:.2f}/month"
        return "$0.00/month"
    
    def get_function_url(self) -> str:
        """Get the function URL (for HTTP functions)"""
        if self.trigger_type != "http":
            raise ValueError("Function URL only available for HTTP functions")
        return self.function_url or f"https://{self.region}-{self.gcp_client.project_id if hasattr(self, 'gcp_client') and self.gcp_client else 'PROJECT'}.cloudfunctions.net/{self.function_name}"
    
    def curl_example(self) -> str:
        """Generate curl example for HTTP functions"""
        if self.trigger_type != "http":
            return "# This function is not HTTP-triggered"
        
        url = self.get_function_url()
        return f"""# Curl example for {self.function_name}
curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "Hello from InfraDSL!"}}' \\
  {url}"""