"""
DigitalOcean Functions Resource

Rails-like Functions management with intelligent defaults and consistent API.
Provides serverless computing capabilities on DigitalOcean platform.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_resource import BaseDigitalOceanResource
from ..digitalocean_managers.functions_manager import FunctionsManager, FunctionConfig


class Function(BaseDigitalOceanResource):
    """
    DigitalOcean Functions Resource

    Rails-like serverless function management with intelligent defaults.
    Supports multiple runtimes and HTTP triggers.
    """

    def __init__(self, name: str):
        """
        Initialize Function resource.

        Args:
            name: Function name
        """
        super().__init__(name)

        # Core Function configuration
        self.config = FunctionConfig(name=name)
        self.functions_manager = None

        # Function state
        self.function_url = None
        self.last_deployed = None
        self.status = None

    def _initialize_managers(self):
        """Initialize Function-specific managers"""
        self.functions_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        if not self.functions_manager:
            self.functions_manager = FunctionsManager(self.do_client)

    def runtime(self, runtime: str) -> 'Function':
        """
        Set the runtime environment.
        
        Args:
            runtime: Runtime (python:3.9, python:3.11, nodejs:18, nodejs:20, go:1.21, php:8.2)
        """
        self.config.runtime = runtime
        return self

    def memory(self, memory_mb: int) -> 'Function':
        """
        Set memory allocation in MB.
        
        Args:
            memory_mb: Memory in MB (128-1024)
        """
        self.config.memory_mb = memory_mb
        return self

    def timeout(self, timeout_ms: int) -> 'Function':
        """
        Set function timeout in milliseconds.
        
        Args:
            timeout_ms: Timeout in milliseconds (1000-900000)
        """
        self.config.timeout_ms = timeout_ms
        return self

    def source(self, source_path: str) -> 'Function':
        """
        Set source code path.
        
        Args:
            source_path: Path to source code directory
        """
        self.config.source_path = source_path
        return self

    def main_function(self, function_name: str) -> 'Function':
        """
        Set the main function name.
        
        Args:
            function_name: Name of the main function (default: main)
        """
        self.config.main_function = function_name
        return self

    def environment(self, variables: Dict[str, str]) -> 'Function':
        """
        Set environment variables.
        
        Args:
            variables: Dictionary of environment variables
        """
        self.config.environment_variables = variables
        return self

    def env(self, key: str, value: str) -> 'Function':
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable key
            value: Environment variable value
        """
        if not self.config.environment_variables:
            self.config.environment_variables = {}
        self.config.environment_variables[key] = value
        return self

    def description(self, desc: str) -> 'Function':
        """
        Set function description.
        
        Args:
            desc: Function description
        """
        self.config.description = desc
        return self

    def web(self, enabled: bool = True) -> 'Function':
        """
        Enable/disable web access (HTTP triggers).
        
        Args:
            enabled: Whether to enable web access
        """
        self.config.web = enabled
        return self

    # Rails-like convenience methods
    def python(self, version: str = "3.11") -> 'Function':
        """Rails convenience: Set Python runtime"""
        return self.runtime(f"python:{version}")

    def nodejs(self, version: str = "20") -> 'Function':
        """Rails convenience: Set Node.js runtime"""
        return self.runtime(f"nodejs:{version}")

    def go(self, version: str = "1.21") -> 'Function':
        """Rails convenience: Set Go runtime"""
        return self.runtime(f"go:{version}")

    def php(self, version: str = "8.2") -> 'Function':
        """Rails convenience: Set PHP runtime"""
        return self.runtime(f"php:{version}")

    # Rails-like function type conventions
    def api_function(self) -> 'Function':
        """Configure for API workloads (Rails convention)"""
        return (self
                .memory(512)
                .timeout(60000)  # 60 seconds
                .web(True)
                .description("API function"))

    def processor_function(self) -> 'Function':
        """Configure for data processing workloads"""
        return (self
                .memory(1024)
                .timeout(300000)  # 5 minutes
                .web(False)
                .description("Data processor function"))

    def webhook_function(self) -> 'Function':
        """Configure for webhook workloads"""
        return (self
                .memory(256)
                .timeout(30000)  # 30 seconds
                .web(True)
                .description("Webhook function"))

    # Trigger configuration - HTTP only for DigitalOcean Functions
    def trigger(self, trigger_type: str = "http", **kwargs) -> 'Function':
        """
        Configure function trigger.
        
        Note: DigitalOcean Functions currently only support HTTP triggers.
        
        Args:
            trigger_type: Type of trigger (only "http" supported)
        """
        if trigger_type != "http":
            print(f"⚠️  Warning: DigitalOcean Functions only support HTTP triggers. Ignoring '{trigger_type}' trigger.")
        
        self.config.web = True
        return self

    def http_trigger(self) -> 'Function':
        """Configure HTTP trigger (default for DigitalOcean Functions)"""
        return self.trigger("http")

    def _discover_existing_functions(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DigitalOcean Functions"""
        existing_functions = {}
        
        try:
            if not self.functions_manager:
                return existing_functions
                
            # Get all functions from the account
            functions = self.functions_manager.list_functions()
            
            for func in functions:
                if func.get("name") == self.name:
                    existing_functions[self.name] = {
                        "name": func.get("name"),
                        "runtime": func.get("runtime"),
                        "memory": func.get("memory_mb", 128),
                        "timeout": func.get("timeout_ms", 30000),
                        "status": func.get("status", "unknown"),
                        "url": func.get("url"),
                        "namespace": func.get("namespace"),
                        "created_at": func.get("created_at"),
                        "last_deployed": func.get("updated_at")
                    }
                    break
                    
        except Exception as e:
            # Silently handle discovery errors
            pass
            
        return existing_functions

    def preview(self) -> Dict[str, Any]:
        """Preview DigitalOcean Function with smart state management"""
        self._ensure_authenticated()

        print(f"╭─ ⚡ DigitalOcean Function Preview: {self.name}")
        print(f"├─ 🔧 Runtime: {self.config.runtime}")
        print(f"├─ 💾 Memory: {self.config.memory_mb} MB")
        print(f"├─ ⏱️  Timeout: {self.config.timeout_ms} ms")
        print(f"├─ 🌍 Cost: {self._estimate_monthly_cost()}")

        # Discover existing functions
        existing_functions = self._discover_existing_functions()

        # Determine changes needed
        to_create = []
        to_update = []
        to_keep = []

        if self.name not in existing_functions:
            to_create.append(self.name)
        else:
            existing_func = existing_functions[self.name]
            # Check if update is needed
            needs_update = (
                existing_func.get("runtime") != self.config.runtime or
                existing_func.get("memory") != self.config.memory_mb or
                existing_func.get("timeout") != self.config.timeout_ms
            )
            
            if needs_update:
                to_update.append(self.name)
            else:
                to_keep.append(self.name)

        # Show only actionable changes
        if to_create:
            print(f"├─ 🔧 Functions to CREATE:")
            for func_name in to_create:
                print(f"│  ├─ ⚡ {func_name}")

        if to_update:
            print(f"├─ 🔄 Functions to UPDATE:")
            for func_name in to_update:
                existing_func = existing_functions[func_name]
                print(f"│  ├─ 🔄 {func_name}")
                print(f"│  │  ├─ Runtime: {existing_func.get('runtime')} → {self.config.runtime}")
                print(f"│  │  ├─ Memory: {existing_func.get('memory')}MB → {self.config.memory_mb}MB")
                print(f"│  │  ╰─ Timeout: {existing_func.get('timeout')}ms → {self.config.timeout_ms}ms")

        if existing_functions and self.name in existing_functions:
            existing_func = existing_functions[self.name]
            print(f"├─ ✅ Current status: {existing_func.get('status', 'unknown')}")
            if existing_func.get('url'):
                print(f"├─ 🌐 Current URL: {existing_func['url']}")

        print(f"╰─ 💡 Run .create() to deploy function")

        return {
            "resource_type": "digitalocean_function",
            "name": self.name,
            "to_create": to_create,
            "to_update": to_update,
            "existing_functions": existing_functions,
            "config": {
                "runtime": self.config.runtime,
                "memory_mb": self.config.memory_mb,
                "timeout_ms": self.config.timeout_ms,
                "web_enabled": self.config.web
            },
            "changes": len(to_create) + len(to_update) > 0
        }

    def create(self) -> Dict[str, Any]:
        """Create or update the Function with smart state management"""
        self._ensure_authenticated()

        # Discover existing functions first
        existing_functions = self._discover_existing_functions()

        # Determine changes needed
        action = "CREATE"
        existing_func = None
        if self.name in existing_functions:
            existing_func = existing_functions[self.name]
            # Check if update is needed
            needs_update = (
                existing_func.get("runtime") != self.config.runtime or
                existing_func.get("memory") != self.config.memory_mb or
                existing_func.get("timeout") != self.config.timeout_ms
            )
            action = "UPDATE" if needs_update else "KEEP"

        print(f"⚡ {action}ING DigitalOcean Function: {self.config.name}")

        if action == "KEEP":
            print(f"✅ Function already exists with desired configuration")
            return {
                'success': True,
                'function_name': self.config.name,
                'function_url': existing_func.get('url'),
                'status': existing_func.get('status'),
                'action': 'kept',
                'changes': False
            }

        try:
            # Deploy or update the function using the manager
            result = self.functions_manager.deploy_function(self.config)
            
            if result.get('success'):
                self.function_url = result.get('url')
                self.last_deployed = result.get('deployed_at')
                self.status = 'active'
                
                if action == "CREATE":
                    print(f"╭─ ✅ Function created successfully!")
                else:
                    print(f"╭─ ✅ Function updated successfully!")
                    
                print(f"├─ 🌐 Function URL: {self.function_url}")
                print(f"├─ 🔧 Runtime: {self.config.runtime}")
                print(f"├─ 💾 Memory: {self.config.memory_mb} MB")
                print(f"╰─ ⏱️  Timeout: {self.config.timeout_ms} ms")
                
                return {
                    'success': True,
                    'function_name': self.config.name,
                    'function_url': self.function_url,
                    'status': self.status,
                    'runtime': self.config.runtime,
                    'memory_mb': self.config.memory_mb,
                    'timeout_ms': self.config.timeout_ms,
                    'deployed_at': self.last_deployed,
                    'action': action.lower(),
                    'changes': True
                }
            else:
                print(f"❌ Function {action.lower()} failed: {result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'action': action.lower(),
                    'changes': False
                }

        except Exception as e:
            print(f"❌ Failed to {action.lower()} function: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'action': action.lower(),
                'changes': False
            }

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Function"""
        self._ensure_authenticated()

        print(f"🗑️  Destroying DigitalOcean Function: {self.config.name}")

        try:
            success = self.functions_manager.delete_function(self.config.name)
            
            if success:
                print(f"✅ Function '{self.config.name}' destroyed successfully!")
                self.function_url = None
                self.status = 'deleted'
                
                return {
                    'success': True,
                    'function_name': self.config.name,
                    'status': 'deleted'
                }
            else:
                print(f"⚠️  Function '{self.config.name}' may not exist or could not be deleted")
                return {
                    'success': False,
                    'error': 'Function not found or deletion failed'
                }

        except Exception as e:
            print(f"❌ Failed to destroy function: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def invoke(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke the function with optional parameters.
        
        Args:
            parameters: Parameters to pass to the function
        """
        self._ensure_authenticated()

        try:
            result = self.functions_manager.invoke_function(self.config.name, parameters)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost based on configuration"""
        # Very rough estimation for DigitalOcean Functions
        # Based on $0.000018 per GB-second and $0.0000025 per request
        
        # Assume 1M requests per month and average 500ms execution time
        monthly_requests = 1_000_000
        avg_execution_time_seconds = 0.5
        memory_gb = self.config.memory_mb / 1024
        
        # GB-seconds cost
        gb_seconds_per_month = monthly_requests * avg_execution_time_seconds * memory_gb
        gb_seconds_cost = gb_seconds_per_month * 0.000018
        
        # Request cost
        request_cost = monthly_requests * 0.0000025
        
        total_cost = gb_seconds_cost + request_cost
        
        if total_cost > 100:
            return f"~${total_cost:.0f}/month"
        elif total_cost > 10:
            return f"~${total_cost:.2f}/month"
        else:
            return f"~${total_cost:.3f}/month"

    def info(self) -> Dict[str, Any]:
        """Get function information"""
        return {
            'name': self.config.name,
            'runtime': self.config.runtime,
            'memory_mb': self.config.memory_mb,
            'timeout_ms': self.config.timeout_ms,
            'web_enabled': self.config.web,
            'function_url': self.function_url,
            'status': self.status,
            'last_deployed': self.last_deployed
        }

    def url(self) -> Optional[str]:
        """Get the function URL"""
        return self.function_url

    def curl_example(self) -> str:
        """Generate a curl example for testing the function"""
        if not self.function_url:
            return "Function not deployed yet. Run .create() first."
        
        return f"curl -X POST {self.function_url} -H 'Content-Type: application/json' -d '{{\"key\": \"value\"}}'" 