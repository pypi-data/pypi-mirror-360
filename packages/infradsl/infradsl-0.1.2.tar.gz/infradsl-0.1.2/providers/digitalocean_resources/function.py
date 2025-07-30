"""
DigitalOcean Function Resource for InfraDSL

Rails-like DigitalOcean Functions management with intelligent defaults.
Provides a simple, chainable API for serverless function deployment.
"""

from typing import Dict, Any, Optional
from .base_resource import BaseDigitalOceanResource
from ..digitalocean_managers.functions_manager import FunctionsManager, FunctionConfig
from ..digitalocean_managers.do_client import DoClient


class Function(BaseDigitalOceanResource):
    """
    DigitalOcean Function Resource

    Rails-like Function management with intelligent defaults.
    Provides simple deployment and management of serverless functions.
    """

    def __init__(self, name: str):
        """
        Initialize Function resource.

        Args:
            name: Function name
        """
        self.config = FunctionConfig(name=name)

        # Initialize managers
        self.do_client = DoClient()
        self.functions_manager = None

        # Function state
        self.function_url = None
        self.namespace_id = None
        self.deployment_result = None
        super().__init__(name)

    def _initialize_managers(self):
        """Initialize function managers after authentication"""
        if not self.functions_manager:
            self.functions_manager = FunctionsManager(self.do_client)

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Managers are initialized in _initialize_managers, which is called after authentication
        pass

    # Authentication methods
    def authenticate(self, token: Optional[str] = None) -> 'Function':
        """
        Set the DigitalOcean API token.

        Args:
            token: DigitalOcean API token (optional, will search for .env file if not provided)

        Returns:
            Function: Self for chaining
        """
        self.do_client.authenticate(token)
        return self

    # Runtime configuration methods
    def python(self, version: str = "3.11") -> 'Function':
        """
        Set Python runtime.

        Args:
            version: Python version ("3.9" or "3.11")

        Returns:
            Function: Self for chaining
        """
        self.config.runtime = f"python:{version}"
        return self

    def python39(self) -> 'Function':
        """Set Python 3.9 runtime."""
        return self.python("3.9")

    def python311(self) -> 'Function':
        """Set Python 3.11 runtime."""
        return self.python("3.11")

    def nodejs(self, version: str = "18") -> 'Function':
        """
        Set Node.js runtime.

        Args:
            version: Node.js version ("18" or "20")

        Returns:
            Function: Self for chaining
        """
        self.config.runtime = f"nodejs:{version}"
        return self

    def nodejs18(self) -> 'Function':
        """Set Node.js 18 runtime."""
        return self.nodejs("18")

    def nodejs20(self) -> 'Function':
        """Set Node.js 20 runtime."""
        return self.nodejs("20")

    def go(self, version: str = "1.21") -> 'Function':
        """
        Set Go runtime.

        Args:
            version: Go version

        Returns:
            Function: Self for chaining
        """
        self.config.runtime = f"go:{version}"
        return self

    def php(self, version: str = "8.2") -> 'Function':
        """
        Set PHP runtime.

        Args:
            version: PHP version

        Returns:
            Function: Self for chaining
        """
        self.config.runtime = f"php:{version}"
        return self

    # Memory and timeout configuration
    def memory(self, memory_mb: int) -> 'Function':
        """
        Set function memory limit.

        Args:
            memory_mb: Memory in MB (128-1024)

        Returns:
            Function: Self for chaining
        """
        self.config.memory_mb = memory_mb
        return self

    def memory_128mb(self) -> 'Function':
        """Set memory to 128MB (minimum)."""
        return self.memory(128)

    def memory_256mb(self) -> 'Function':
        """Set memory to 256MB."""
        return self.memory(256)

    def memory_512mb(self) -> 'Function':
        """Set memory to 512MB."""
        return self.memory(512)

    def memory_1gb(self) -> 'Function':
        """Set memory to 1GB (maximum)."""
        return self.memory(1024)

    def timeout(self, seconds: int) -> 'Function':
        """
        Set function timeout.

        Args:
            seconds: Timeout in seconds (1-900)

        Returns:
            Function: Self for chaining
        """
        self.config.timeout_ms = seconds * 1000
        return self

    def timeout_30s(self) -> 'Function':
        """Set timeout to 30 seconds."""
        return self.timeout(30)

    def timeout_1m(self) -> 'Function':
        """Set timeout to 1 minute."""
        return self.timeout(60)

    def timeout_5m(self) -> 'Function':
        """Set timeout to 5 minutes."""
        return self.timeout(300)

    def timeout_15m(self) -> 'Function':
        """Set timeout to 15 minutes (maximum)."""
        return self.timeout(900)

    # Source code configuration
    def source(self, path: str) -> 'Function':
        """
        Set function source code path.

        Args:
            path: Path to source file or directory

        Returns:
            Function: Self for chaining
        """
        self.config.source_path = path
        return self

    def handler(self, function_name: str) -> 'Function':
        """
        Set main function handler name.

        Args:
            function_name: Name of the main function

        Returns:
            Function: Self for chaining
        """
        self.config.main_function = function_name
        return self

    def description(self, desc: str) -> 'Function':
        """
        Set function description.

        Args:
            desc: Function description

        Returns:
            Function: Self for chaining
        """
        self.config.description = desc
        return self

    # Environment and configuration
    def env(self, key: str, value: str) -> 'Function':
        """
        Set environment variable.

        Args:
            key: Environment variable name
            value: Environment variable value

        Returns:
            Function: Self for chaining
        """
        self.config.environment_variables[key] = value
        return self

    def env_vars(self, variables: Dict[str, str]) -> 'Function':
        """
        Set multiple environment variables.

        Args:
            variables: Dictionary of environment variables

        Returns:
            Function: Self for chaining
        """
        self.config.environment_variables.update(variables)
        return self

    # Trigger configuration
    def trigger(self, trigger_type: str = "http") -> 'Function':
        """
        Configure function trigger.

        Args:
            trigger_type: Type of trigger ("http" for web functions)

        Returns:
            Function: Self for chaining
        """
        if trigger_type == "http":
            self.config.web = True
        return self

    def http(self) -> 'Function':
        """Enable HTTP trigger (web function)."""
        return self.trigger("http")

    def web(self) -> 'Function':
        """Enable web access (alias for http)."""
        return self.trigger("http")

    # Convenience preset methods
    def api_function(self) -> 'Function':
        """
        Configure as an API function with sensible defaults.

        Returns:
            Function: Self for chaining
        """
        return (self
                .python311()
                .memory_256mb()
                .timeout_30s()
                .http()
                .description(f"API function: {self.config.name}"))

    def processor_function(self) -> 'Function':
        """
        Configure as a data processing function.

        Returns:
            Function: Self for chaining
        """
        return (self
                .python311()
                .memory_512mb()
                .timeout_5m()
                .description(f"Data processor: {self.config.name}"))

    def quick_function(self) -> 'Function':
        """
        Configure as a lightweight quick function.

        Returns:
            Function: Self for chaining
        """
        return (self
                .python311()
                .memory_128mb()
                .timeout_30s()
                .http()
                .description(f"Quick function: {self.config.name}"))

    # Template methods for common patterns
    def from_template(self, template_name: str) -> 'Function':
        """
        Load function from a template directory.

        Args:
            template_name: Name of template directory

        Returns:
            Function: Self for chaining
        """
        template_path = f"templates/{template_name}"
        return self.source(template_path)

    def hello_world(self) -> 'Function':
        """
        Create a simple hello world function.

        Returns:
            Function: Self for chaining
        """
        return (self
                .python311()
                .memory_128mb()
                .timeout_30s()
                .http()
                .description("Simple hello world function"))

    # Management operations
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created without actually creating it.

        Returns:
            Dict containing preview information
        """
        self._ensure_authenticated()
        self._initialize_managers()

        print(f"🔍 Preview: DigitalOcean Function '{self.config.name}'")
        print("=" * 50)

        preview_data = {
            'resource_type': 'digitalocean_function',
            'name': self.config.name,
            'runtime': self.config.runtime,
            'memory_mb': self.config.memory_mb,
            'timeout_ms': self.config.timeout_ms,
            'main_function': self.config.main_function,
            'web_enabled': self.config.web,
            'environment_variables': self.config.environment_variables,
            'source_path': self.config.source_path,
            'description': self.config.description
        }

        print(f"Function Name: {preview_data['name']}")
        print(f"Runtime: {preview_data['runtime']}")
        print(f"Memory: {preview_data['memory_mb']} MB")
        print(f"Timeout: {preview_data['timeout_ms']} ms ({preview_data['timeout_ms']/1000:.1f}s)")
        print(f"Handler: {preview_data['main_function']}")
        print(f"Web Function: {preview_data['web_enabled']}")

        if preview_data['description']:
            print(f"Description: {preview_data['description']}")

        if preview_data['source_path']:
            print(f"Source Path: {preview_data['source_path']}")
        else:
            print("Source: Default generated code")

        if preview_data['environment_variables']:
            print(f"Environment Variables: {len(preview_data['environment_variables'])} set")

        print("=" * 50)
        return preview_data

    def create(self) -> Dict[str, Any]:
        """
        Deploy the function to DigitalOcean.

        Returns:
            Dict containing deployment information
        """
        self._ensure_authenticated()
        self._initialize_managers()

        try:
            print(f"🚀 Creating DigitalOcean Function: {self.config.name}")

            # Deploy the function
            result = self.functions_manager.deploy_function(self.config)

            # Store deployment information
            self.deployment_result = result
            self.function_url = result.get('function_url')
            self.namespace_id = result.get('namespace_id')

            print(f"✅ Function '{self.config.name}' created successfully!")

            return result

        except Exception as e:
            print(f"❌ Failed to create function: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """
        Delete the function from DigitalOcean.

        Returns:
            Dict containing destruction information
        """
        self._ensure_authenticated()
        self._initialize_managers()

        try:
            print(f"🗑️  Destroying DigitalOcean Function: {self.config.name}")

            success = self.functions_manager.delete_function(self.config.name)

            if success:
                print(f"✅ Function '{self.config.name}' destroyed successfully!")
                return {
                    "name": self.config.name,
                    "status": "destroyed",
                    "success": True
                }
            else:
                print(f"⚠️  Function '{self.config.name}' may not exist or failed to destroy")
                return {
                    "name": self.config.name,
                    "status": "not_found_or_failed",
                    "success": False
                }

        except Exception as e:
            print(f"❌ Failed to destroy function: {str(e)}")
            raise

    def invoke(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke the function for testing.

        Args:
            parameters: Parameters to pass to the function

        Returns:
            Dict containing function response
        """
        self._ensure_authenticated()
        self._initialize_managers()

        try:
            print(f"⚡ Invoking function: {self.config.name}")

            result = self.functions_manager.invoke_function(self.config.name, parameters)

            print(f"✅ Function invoked successfully!")
            return result

        except Exception as e:
            print(f"❌ Failed to invoke function: {str(e)}")
            raise

    def status(self) -> Dict[str, Any]:
        """
        Get function status and information.

        Returns:
            Dict containing function status
        """
        self._ensure_authenticated()
        self._initialize_managers()

        try:
            functions = self.functions_manager.list_functions()

            for func in functions:
                if func.get('name') == f"infradsl/{self.config.name}":
                    return {
                        "name": self.config.name,
                        "status": "deployed",
                        "url": func.get('url'),
                        "namespace": func.get('namespace'),
                        "runtime": func.get('runtime'),
                        "memory": func.get('memory'),
                        "timeout": func.get('timeout')
                    }

            return {
                "name": self.config.name,
                "status": "not_deployed"
            }

        except Exception as e:
            return {
                "name": self.config.name,
                "status": "error",
                "error": str(e)
            }

    def url(self) -> Optional[str]:
        """
        Get the function URL if deployed.

        Returns:
            Function URL or None if not deployed
        """
        if self.function_url:
            return self.function_url

        try:
            status = self.status()
            return status.get('url')
        except:
            return None

    def __str__(self) -> str:
        """String representation of the function"""
        return f"DigitalOcean.Function('{self.config.name}')"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"DigitalOcean.Function(name='{self.config.name}', runtime='{self.config.runtime}', memory={self.config.memory_mb}MB)"