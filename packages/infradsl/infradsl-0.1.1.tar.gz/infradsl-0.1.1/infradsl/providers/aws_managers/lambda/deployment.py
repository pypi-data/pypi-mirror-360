"""
Lambda Deployment and Code Management

This module handles Lambda function deployment, code packaging,
container image management, and deployment operations.
"""

from typing import Dict, Any, List, Optional
import zipfile
import io
import base64
import os
import time
from pathlib import Path


class LambdaDeploymentManager:
    """
    Lambda Deployment and Code Management
    
    Handles:
    - Function creation and updating
    - ZIP package preparation and deployment
    - Container image building and pushing
    - ECR repository management
    - Code deployment strategies
    """
    
    def __init__(self, aws_client):
        """Initialize the deployment manager with AWS client."""
        self.aws_client = aws_client
    
    def create_function(
        self,
        function_name: str,
        runtime: str,
        handler: str,
        execution_role_arn: str,
        code: Dict[str, Any],
        memory_size: int = 128,
        timeout: int = 30,
        environment_variables: Optional[Dict[str, str]] = None,
        vpc_config: Optional[Dict[str, Any]] = None,
        package_type: str = "Zip",
        description: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Lambda function.
        
        Args:
            function_name: Name of the function
            runtime: Runtime environment
            handler: Function handler
            execution_role_arn: IAM role ARN
            code: Code configuration (ZipFile, S3Bucket/S3Key, or ImageUri)
            memory_size: Memory allocation in MB
            timeout: Timeout in seconds
            environment_variables: Environment variables
            vpc_config: VPC configuration
            package_type: Package type (Zip or Image)
            description: Function description
            tags: Function tags
            
        Returns:
            Function creation result
        """
        try:
            print(f"⚡ Creating Lambda function: {function_name}")
            
            # Build function configuration
            function_config = {
                'FunctionName': function_name,
                'Role': execution_role_arn,
                'Code': code,
                'MemorySize': memory_size,
                'Timeout': timeout,
                'PackageType': package_type,
                'Publish': True  # Publish a version
            }
            
            # Add runtime and handler for Zip packages
            if package_type == "Zip":
                function_config['Runtime'] = runtime
                function_config['Handler'] = handler
            
            # Add optional configurations
            if description:
                function_config['Description'] = description
            
            if environment_variables:
                function_config['Environment'] = {'Variables': environment_variables}
            
            if vpc_config:
                function_config['VpcConfig'] = vpc_config
            
            if tags:
                function_config['Tags'] = tags
            
            # Create the function
            response = self.aws_client.lambda_client.create_function(**function_config)
            
            # Wait for function to become active
            self._wait_for_function_active(function_name)
            
            print(f"✅ Lambda function created: {function_name}")
            
            return {
                'function_arn': response['FunctionArn'],
                'function_name': function_name,
                'state': response.get('State'),
                'version': response.get('Version'),
                'last_modified': response.get('LastModified'),
                'code_size': response.get('CodeSize', 0)
            }
            
        except Exception as e:
            print(f"❌ Failed to create function '{function_name}': {str(e)}")
            raise
    
    def update_function_code(
        self,
        function_name: str,
        code: Dict[str, Any],
        publish: bool = True
    ) -> Dict[str, Any]:
        """
        Update Lambda function code.
        
        Args:
            function_name: Name of the function
            code: New code configuration
            publish: Whether to publish a new version
            
        Returns:
            Update result
        """
        try:
            print(f"🔄 Updating function code: {function_name}")
            
            update_params = {
                'FunctionName': function_name,
                'Publish': publish,
                **code
            }
            
            response = self.aws_client.lambda_client.update_function_code(**update_params)
            
            # Wait for update to complete
            self._wait_for_function_update_complete(function_name)
            
            print(f"✅ Function code updated: {function_name}")
            
            return {
                'function_arn': response['FunctionArn'],
                'version': response.get('Version'),
                'last_modified': response.get('LastModified'),
                'code_size': response.get('CodeSize', 0),
                'state': response.get('State')
            }
            
        except Exception as e:
            print(f"❌ Failed to update function code: {str(e)}")
            raise
    
    def update_function_configuration(
        self,
        function_name: str,
        runtime: Optional[str] = None,
        handler: Optional[str] = None,
        memory_size: Optional[int] = None,
        timeout: Optional[int] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        vpc_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update Lambda function configuration.
        
        Args:
            function_name: Name of the function
            runtime: New runtime
            handler: New handler
            memory_size: New memory size
            timeout: New timeout
            environment_variables: New environment variables
            vpc_config: New VPC configuration
            description: New description
            
        Returns:
            Update result
        """
        try:
            print(f"⚙️  Updating function configuration: {function_name}")
            
            update_params = {'FunctionName': function_name}
            
            # Add only the parameters that are provided
            if runtime is not None:
                update_params['Runtime'] = runtime
            if handler is not None:
                update_params['Handler'] = handler
            if memory_size is not None:
                update_params['MemorySize'] = memory_size
            if timeout is not None:
                update_params['Timeout'] = timeout
            if description is not None:
                update_params['Description'] = description
            
            if environment_variables is not None:
                update_params['Environment'] = {'Variables': environment_variables}
            
            if vpc_config is not None:
                update_params['VpcConfig'] = vpc_config
            
            response = self.aws_client.lambda_client.update_function_configuration(**update_params)
            
            # Wait for update to complete
            self._wait_for_function_update_complete(function_name)
            
            print(f"✅ Function configuration updated: {function_name}")
            
            return {
                'function_arn': response['FunctionArn'],
                'last_modified': response.get('LastModified'),
                'state': response.get('State')
            }
            
        except Exception as e:
            print(f"❌ Failed to update function configuration: {str(e)}")
            raise
    
    def delete_function(self, function_name: str) -> Dict[str, Any]:
        """
        Delete Lambda function.
        
        Args:
            function_name: Name of the function to delete
            
        Returns:
            Deletion result
        """
        try:
            print(f"🗑️  Deleting Lambda function: {function_name}")
            
            self.aws_client.lambda_client.delete_function(FunctionName=function_name)
            
            print(f"✅ Lambda function deleted: {function_name}")
            
            return {'deleted': True, 'function_name': function_name}
            
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                print(f"⚠️  Function not found: {function_name}")
                return {'deleted': False, 'reason': 'Function not found'}
            else:
                print(f"❌ Failed to delete function: {str(e)}")
                raise
    
    def prepare_zip_package(
        self,
        source_path: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> bytes:
        """
        Prepare ZIP package from source directory or file.
        
        Args:
            source_path: Path to source code
            exclude_patterns: Patterns to exclude from ZIP
            
        Returns:
            ZIP package as bytes
        """
        try:
            print(f"📦 Preparing ZIP package from: {source_path}")
            
            source = Path(source_path)
            exclude_patterns = exclude_patterns or [
                '*.pyc', '__pycache__', '.git', '.gitignore', 
                '*.log', '.DS_Store', 'node_modules', '.env'
            ]
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                if source.is_file():
                    # Single file
                    zip_file.write(source, source.name)
                else:
                    # Directory
                    for file_path in source.rglob('*'):
                        if file_path.is_file() and not self._should_exclude(file_path, exclude_patterns):
                            arcname = file_path.relative_to(source)
                            zip_file.write(file_path, arcname)
            
            zip_bytes = zip_buffer.getvalue()
            print(f"✅ ZIP package prepared: {len(zip_bytes)} bytes")
            
            return zip_bytes
            
        except Exception as e:
            print(f"❌ Failed to prepare ZIP package: {str(e)}")
            raise
    
    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded from ZIP."""
        import fnmatch
        
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False
    
    def prepare_code_from_string(self, code_string: str, handler_filename: str = "lambda_function.py") -> bytes:
        """
        Prepare ZIP package from code string.
        
        Args:
            code_string: Source code as string
            handler_filename: Name of the handler file
            
        Returns:
            ZIP package as bytes
        """
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(handler_filename, code_string)
            
            return zip_buffer.getvalue()
            
        except Exception as e:
            print(f"❌ Failed to prepare code from string: {str(e)}")
            raise
    
    def create_ecr_repository(
        self,
        repository_name: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create ECR repository for container images.
        
        Args:
            repository_name: Name of the repository
            tags: Repository tags
            
        Returns:
            Repository creation result
        """
        try:
            # Check if repository already exists
            try:
                response = self.aws_client.ecr.describe_repositories(repositoryNames=[repository_name])
                print(f"📦 ECR repository '{repository_name}' already exists")
                return {
                    'repository_uri': response['repositories'][0]['repositoryUri'],
                    'repository_name': repository_name,
                    'created': False
                }
            except:
                pass
            
            print(f"🏗️  Creating ECR repository: {repository_name}")
            
            create_params = {'repositoryName': repository_name}
            if tags:
                create_params['tags'] = [
                    {'Key': key, 'Value': value}
                    for key, value in tags.items()
                ]
            
            response = self.aws_client.ecr.create_repository(**create_params)
            repository = response['repository']
            
            print(f"✅ ECR repository created: {repository_name}")
            
            return {
                'repository_uri': repository['repositoryUri'],
                'repository_name': repository_name,
                'repository_arn': repository['repositoryArn'],
                'created': True
            }
            
        except Exception as e:
            print(f"❌ Failed to create ECR repository: {str(e)}")
            raise
    
    def build_and_push_container_image(
        self,
        repository_uri: str,
        dockerfile_path: str = "Dockerfile",
        build_context: str = ".",
        tag: str = "latest"
    ) -> Dict[str, Any]:
        """
        Build and push container image to ECR.
        
        Args:
            repository_uri: ECR repository URI
            dockerfile_path: Path to Dockerfile
            build_context: Build context directory
            tag: Image tag
            
        Returns:
            Build and push result
        """
        try:
            print(f"🔨 Building container image for Lambda...")
            
            # Get ECR login token
            token_response = self.aws_client.ecr.get_authorization_token()
            token_data = token_response['authorizationData'][0]
            username, password = base64.b64decode(token_data['authorizationToken']).decode().split(':')
            registry_url = token_data['proxyEndpoint']
            
            # Full image URI with tag
            image_uri = f"{repository_uri}:{tag}"
            
            # Build using docker (simplified - in reality would use container engine)
            import subprocess
            
            # Docker login
            login_cmd = ["docker", "login", "--username", username, "--password-stdin", registry_url]
            login_process = subprocess.run(login_cmd, input=password.encode(), capture_output=True)
            
            if login_process.returncode != 0:
                raise Exception(f"Docker login failed: {login_process.stderr.decode()}")
            
            # Build image
            build_cmd = [
                "docker", "build",
                "-f", dockerfile_path,
                "-t", image_uri,
                build_context
            ]
            
            build_process = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if build_process.returncode != 0:
                raise Exception(f"Docker build failed: {build_process.stderr}")
            
            # Push image
            print(f"📤 Pushing image to ECR...")
            push_cmd = ["docker", "push", image_uri]
            push_process = subprocess.run(push_cmd, capture_output=True, text=True)
            
            if push_process.returncode != 0:
                raise Exception(f"Docker push failed: {push_process.stderr}")
            
            print(f"✅ Container image built and pushed: {image_uri}")
            
            return {
                'image_uri': image_uri,
                'repository_uri': repository_uri,
                'tag': tag,
                'pushed': True
            }
            
        except Exception as e:
            print(f"❌ Failed to build and push container image: {str(e)}")
            raise
    
    def create_default_dockerfile(self, runtime: str, handler: str) -> str:
        """
        Create a default Dockerfile for the given runtime.
        
        Args:
            runtime: Lambda runtime
            handler: Function handler
            
        Returns:
            Dockerfile content
        """
        if runtime.startswith('python'):
            version = runtime.replace('python', '').replace('.', '')
            return f"""FROM public.ecr.aws/lambda/python:{version}

# Copy function code
COPY lambda_function.py ${{LAMBDA_TASK_ROOT}}

# Copy requirements if exists
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

CMD ["{handler}"]
"""
        elif runtime.startswith('nodejs'):
            version = runtime.replace('nodejs', '')
            return f"""FROM public.ecr.aws/lambda/nodejs:{version}

# Copy function code
COPY index.js package*.json ./

# Install dependencies
RUN npm install

CMD ["{handler}"]
"""
        else:
            return f"""FROM public.ecr.aws/lambda/{runtime}

# Copy function code
COPY . ./

CMD ["{handler}"]
"""
    
    def _wait_for_function_active(self, function_name: str, timeout: int = 300):
        """Wait for function to become active."""
        print(f"⏳ Waiting for function to become active...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
                state = response['Configuration'].get('State')
                
                if state == 'Active':
                    print(f"✅ Function is active")
                    return
                elif state == 'Failed':
                    reason = response['Configuration'].get('StateReason', 'Unknown error')
                    raise Exception(f"Function creation failed: {reason}")
                
            except Exception as e:
                if 'ResourceNotFoundException' not in str(e):
                    raise
            
            time.sleep(5)
        
        raise TimeoutError(f"Function did not become active within {timeout} seconds")
    
    def _wait_for_function_update_complete(self, function_name: str, timeout: int = 300):
        """Wait for function update to complete."""
        print(f"⏳ Waiting for update to complete...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
                last_update_status = response['Configuration'].get('LastUpdateStatus')
                
                if last_update_status == 'Successful':
                    print(f"✅ Update completed successfully")
                    return
                elif last_update_status == 'Failed':
                    reason = response['Configuration'].get('LastUpdateStatusReason', 'Unknown error')
                    raise Exception(f"Function update failed: {reason}")
                
            except Exception as e:
                if 'ResourceNotFoundException' not in str(e):
                    raise
            
            time.sleep(3)
        
        raise TimeoutError(f"Function update did not complete within {timeout} seconds")
    
    def get_deployment_package_info(self, function_name: str) -> Dict[str, Any]:
        """
        Get information about the current deployment package.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Deployment package information
        """
        try:
            response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            
            configuration = response['Configuration']
            code = response.get('Code', {})
            
            package_info = {
                'package_type': configuration.get('PackageType'),
                'code_size': configuration.get('CodeSize'),
                'last_modified': configuration.get('LastModified'),
                'version': configuration.get('Version')
            }
            
            if configuration.get('PackageType') == 'Image':
                package_info['image_uri'] = code.get('ImageUri')
            else:
                package_info.update({
                    'repository_type': code.get('RepositoryType'),
                    'location': code.get('Location')
                })
            
            return package_info
            
        except Exception as e:
            print(f"❌ Failed to get deployment package info: {str(e)}")
            return {}