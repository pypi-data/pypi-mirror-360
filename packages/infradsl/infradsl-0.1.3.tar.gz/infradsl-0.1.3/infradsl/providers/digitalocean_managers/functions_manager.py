"""
DigitalOcean Functions Manager

Manages DigitalOcean Functions deployment using doctl CLI.
Since DigitalOcean Functions are managed via doctl and project.yml files,
this manager wraps the CLI interface to provide Rails-like simplicity.
"""

import os
import json
import subprocess
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class FunctionConfig(BaseModel):
    """Configuration for a DigitalOcean Function"""
    name: str
    runtime: str = "python:3.11"
    memory_mb: int = 128
    timeout_ms: int = 30000
    environment_variables: Dict[str, str] = {}
    source_path: Optional[str] = None
    main_function: str = "main"
    description: str = ""
    web: bool = True  # Web functions are HTTP-accessible


class FunctionsManager:
    """Manager for DigitalOcean Functions deployment"""

    def __init__(self, do_client):
        self.do_client = do_client
        self.namespace_id = None
        self.api_host = None

    def _ensure_doctl_available(self) -> bool:
        """Check if doctl CLI is available"""
        try:
            result = subprocess.run(['doctl', 'version'],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _ensure_serverless_extension(self) -> bool:
        """Check if doctl serverless extension is installed"""
        try:
            result = subprocess.run(['doctl', 'serverless', 'status'],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _setup_doctl_auth(self) -> bool:
        """Setup doctl authentication using the same token as our client"""
        if not self.do_client.is_authenticated():
            return False

        try:
            # Get the token from our client
            token = self.do_client.token
            if not token:
                return False

            # Configure doctl with the token
            result = subprocess.run(['doctl', 'auth', 'init', '--access-token', token],
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def _ensure_namespace_connected(self) -> bool:
        """Ensure we're connected to a Functions namespace"""
        try:
            # Check if already connected
            result = subprocess.run(['doctl', 'serverless', 'status'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and 'Connected to functions namespace' in result.stdout:
                # Parse namespace info from status
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Connected to functions namespace' in line:
                        # Extract namespace ID from output like:
                        # "Connected to functions namespace 'fn-abc123...' on API host 'https://...'"
                        parts = line.split("'")
                        if len(parts) >= 4:
                            self.namespace_id = parts[1]
                            self.api_host = parts[3]
                            return True

            # Not connected, try to connect to default namespace
            # First, list available namespaces
            result = subprocess.run(['doctl', 'serverless', 'namespaces', 'list', '--format', 'json'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                namespaces = json.loads(result.stdout)
                if namespaces:
                    # Use the first available namespace
                    namespace_id = namespaces[0]['namespace']
                    api_host = namespaces[0]['api_host']

                    # Connect to it
                    connect_result = subprocess.run(['doctl', 'serverless', 'connect', namespace_id],
                                                  capture_output=True, text=True, timeout=30)

                    if connect_result.returncode == 0:
                        self.namespace_id = namespace_id
                        self.api_host = api_host
                        return True
                else:
                    # No namespaces exist, create one
                    return self._create_default_namespace()

            return False
        except Exception:
            return False

    def _create_default_namespace(self) -> bool:
        """Create a default Functions namespace"""
        try:
            result = subprocess.run(['doctl', 'serverless', 'namespaces', 'create', '--label', 'infradsl-functions'],
                                  capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # Parse the created namespace ID from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'fn-' in line:
                        self.namespace_id = line.strip()
                        break

                # Connect to the new namespace
                if self.namespace_id:
                    connect_result = subprocess.run(['doctl', 'serverless', 'connect', self.namespace_id],
                                                  capture_output=True, text=True, timeout=30)
                    return connect_result.returncode == 0

            return False
        except Exception:
            return False

    def _validate_function_config(self, config: FunctionConfig) -> None:
        """Validate function configuration"""
        if not config.name:
            raise ValueError("Function name is required")

        if not config.name.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Function name must contain only letters, numbers, hyphens, and underscores")

        if config.memory_mb < 128 or config.memory_mb > 1024:
            raise ValueError("Memory must be between 128MB and 1024MB")

        if config.timeout_ms < 1000 or config.timeout_ms > 900000:  # 15 minutes max
            raise ValueError("Timeout must be between 1 second and 15 minutes")

        valid_runtimes = ["python:3.9", "python:3.11", "nodejs:18", "nodejs:20", "go:1.21", "php:8.2"]
        if config.runtime not in valid_runtimes:
            raise ValueError(f"Runtime must be one of: {', '.join(valid_runtimes)}")

    def _create_function_structure(self, config: FunctionConfig, temp_dir: Path) -> Path:
        """Create the function project structure in a temporary directory"""
        project_dir = temp_dir / f"function-{config.name}"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create package directory structure
        package_dir = project_dir / "packages" / "infradsl" / config.name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create project.yml
        project_yml = {
            "parameters": {},
            "environment": config.environment_variables,
            "packages": {
                "infradsl": {
                    "environment": config.environment_variables,
                    "functions": {
                        config.name: {
                            "runtime": config.runtime,
                            "main": config.main_function,
                            "limits": {
                                "memory": config.memory_mb,
                                "timeout": config.timeout_ms
                            },
                            "web": config.web,
                            "environment": config.environment_variables
                        }
                    }
                }
            }
        }

        # Write project.yml
        with open(project_dir / "project.yml", "w") as f:
            yaml.dump(project_yml, f, default_flow_style=False)

        # Copy or create function source code
        if config.source_path and os.path.exists(config.source_path):
            # Copy existing source
            if os.path.isfile(config.source_path):
                shutil.copy2(config.source_path, package_dir / "__main__.py")
            else:
                # Copy directory contents
                for item in os.listdir(config.source_path):
                    src = os.path.join(config.source_path, item)
                    dst = package_dir / item
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst)
        else:
            # Create default function based on runtime
            self._create_default_function_code(config, package_dir)

        return project_dir

    def _create_default_function_code(self, config: FunctionConfig, package_dir: Path) -> None:
        """Create default function code based on runtime"""
        if config.runtime.startswith("python"):
            code = f'''def {config.main_function}(event, context):
    """
    {config.description or f'DigitalOcean Function: {config.name}'}

    Args:
        event (dict): The event data passed to the function
        context (object): Runtime context information

    Returns:
        dict: The response object
    """
    return {{
        "statusCode": 200,
        "headers": {{
            "Content-Type": "application/json"
        }},
        "body": {{
            "message": "Hello from {config.name}!",
            "event": event,
            "context": {{
                "function_name": context.function_name,
                "function_version": context.function_version,
                "request_id": context.request_id
            }}
        }}
    }}
'''
        elif config.runtime.startswith("nodejs"):
            code = f'''function {config.main_function}(event, context) {{
    // {config.description or f'DigitalOcean Function: {config.name}'}

    return {{
        statusCode: 200,
        headers: {{
            'Content-Type': 'application/json'
        }},
        body: {{
            message: 'Hello from {config.name}!',
            event: event,
            context: {{
                functionName: context.functionName,
                functionVersion: context.functionVersion,
                requestId: context.requestId
            }}
        }}
    }};
}}

exports.{config.main_function} = {config.main_function};
'''
        else:
            # Generic placeholder for other runtimes
            code = f'''// {config.description or f'DigitalOcean Function: {config.name}'}
// Generated function code - please implement your logic here
'''

        # Write the main function file
        if config.runtime.startswith("python"):
            with open(package_dir / "__main__.py", "w") as f:
                f.write(code)
        elif config.runtime.startswith("nodejs"):
            with open(package_dir / "index.js", "w") as f:
                f.write(code)
        else:
            with open(package_dir / "main.txt", "w") as f:
                f.write(code)

    def deploy_function(self, config: FunctionConfig) -> Dict[str, Any]:
        """Deploy a function to DigitalOcean"""
        try:
            # Validate configuration
            self._validate_function_config(config)

            # Check prerequisites
            if not self._ensure_doctl_available():
                raise Exception("doctl CLI is not available. Please install doctl first.")

            if not self._ensure_serverless_extension():
                raise Exception("doctl serverless extension is not installed. Run 'doctl serverless install' first.")

            # Setup authentication
            if not self._setup_doctl_auth():
                raise Exception("Failed to authenticate doctl with DigitalOcean")

            # Ensure namespace connection
            if not self._ensure_namespace_connected():
                raise Exception("Failed to connect to Functions namespace")

            print(f"🚀 Deploying function '{config.name}' to namespace {self.namespace_id}")

            # Create temporary project structure
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                project_dir = self._create_function_structure(config, temp_path)

                # Deploy the function
                deploy_result = subprocess.run(['doctl', 'serverless', 'deploy', str(project_dir)],
                                             capture_output=True, text=True, timeout=300)

                if deploy_result.returncode != 0:
                    raise Exception(f"Function deployment failed: {deploy_result.stderr}")

                # Get function URL
                function_url = self._get_function_url(config.name)

                print(f"✅ Function '{config.name}' deployed successfully")
                if function_url:
                    print(f"🌐 Function URL: {function_url}")

                return {
                    "name": config.name,
                    "namespace_id": self.namespace_id,
                    "api_host": self.api_host,
                    "function_url": function_url,
                    "runtime": config.runtime,
                    "memory_mb": config.memory_mb,
                    "timeout_ms": config.timeout_ms,
                    "status": "deployed",
                    "web_enabled": config.web
                }

        except Exception as e:
            print(f"❌ Function deployment failed: {str(e)}")
            raise

    def _get_function_url(self, function_name: str) -> Optional[str]:
        """Get the URL for a deployed function"""
        try:
            result = subprocess.run(['doctl', 'serverless', 'functions', 'list', '--format', 'json'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                functions = json.loads(result.stdout)
                for func in functions:
                    if func.get('name') == f"infradsl/{function_name}":
                        return func.get('url')

            return None
        except Exception:
            return None

    def list_functions(self) -> List[Dict[str, Any]]:
        """List all deployed functions"""
        try:
            if not self._ensure_namespace_connected():
                return []

            result = subprocess.run(['doctl', 'serverless', 'functions', 'list', '--format', 'json'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                functions = json.loads(result.stdout)
                return [func for func in functions if func.get('name', '').startswith('infradsl/')]

            return []
        except Exception:
            return []

    def delete_function(self, function_name: str) -> bool:
        """Delete a function"""
        try:
            if not self._ensure_namespace_connected():
                return False

            # Use doctl to delete the function
            result = subprocess.run(['doctl', 'serverless', 'functions', 'delete', f"infradsl/{function_name}", '--force'],
                                  capture_output=True, text=True, timeout=60)

            return result.returncode == 0
        except Exception:
            return False

    def invoke_function(self, function_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke a function for testing"""
        try:
            if not self._ensure_namespace_connected():
                raise Exception("Not connected to Functions namespace")

            cmd = ['doctl', 'serverless', 'functions', 'invoke', f"infradsl/{function_name}"]

            if parameters:
                cmd.extend(['--param', json.dumps(parameters)])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"output": result.stdout}
            else:
                raise Exception(f"Function invocation failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to invoke function: {str(e)}")
