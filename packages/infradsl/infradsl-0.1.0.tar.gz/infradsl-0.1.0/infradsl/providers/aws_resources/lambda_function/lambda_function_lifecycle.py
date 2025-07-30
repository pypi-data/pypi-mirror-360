from typing import Dict, Any, List, Optional
import json
import time
import os
import zipfile
import io


class LambdaFunctionLifecycleMixin:
    def create(self) -> Dict[str, Any]:
        self._ensure_authenticated()

        existing_functions = self._discover_existing_functions()
        function_exists = self.function_name in existing_functions
        to_create = [] if function_exists else [self.function_name]
        to_remove = [name for name in existing_functions.keys() if name != self.function_name]

        print(f"\n🔍 Lambda Function")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 FUNCTIONS to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  FUNCTIONS to REMOVE:")
                for function_name in to_remove:
                    function_info = existing_functions.get(function_name)
                    if function_info:
                        runtime = function_info.get('runtime', 'unknown')
                        memory = function_info.get('memory_size', 'unknown')
                        last_modified = function_info.get('last_modified', 'unknown')
                        
                        print(f"   ╭─ ⚡ {function_name}")
                        print(f"   ├─ 🏗️  Runtime: {runtime}")
                        print(f"   ├─ 💾 Memory: {memory} MB")
                        print(f"   ├─ 📅 Modified: {last_modified}")
                        print(f"   ╰─ ⚠️  Will remove all triggers and permissions")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        try:
            for function_name in to_remove:
                print(f"🗑️  Removing function: {function_name}")
                try:
                    self.lambda_client.delete_function(FunctionName=function_name)
                    print(f"✅ Function removed successfully: {function_name}")
                except Exception as e:
                    if "ResourceNotFoundException" not in str(e):
                        print(f"⚠️  Warning: Failed to remove function {function_name}: {str(e)}")

            if function_exists:
                print(f"🔄 Updating function: {self.function_name}")
                existing_function = self._find_existing_function()
                result = self._update_existing_function(existing_function)
            else:
                print(f"🆕 Creating function: {self.function_name}")
                result = self._create_new_function()

            print(f"✅ Function ready: {self.function_name}")
            if result.get("api_gateway_url"):
                print(f"   🌐 API Gateway URL: {result['api_gateway_url']}")

            result["changes"] = {
                "created": to_create,
                "removed": to_remove,
                "updated": [self.function_name] if function_exists else []
            }

            return result

        except Exception as e:
            print(f"❌ Failed to manage Lambda function: {str(e)}")
            raise

    def _create_new_function(self) -> Dict[str, Any]:
        try:
            execution_role_arn = self._ensure_execution_role()
            
            if self.deployment_package_type == "Image":
                container_image_uri = self._build_and_push_container()
                if not container_image_uri:
                    return {"success": False, "error": "Failed to build container image"}
                
                function_config = {
                    'FunctionName': self.function_name,
                    'Role': execution_role_arn,
                    'Code': {'ImageUri': container_image_uri},
                    'PackageType': 'Image',
                    'MemorySize': self.memory_size,
                    'Timeout': self.timeout_seconds,
                    'Description': self.description or f"Lambda function {self.function_name}",
                    'Environment': {'Variables': self.environment_variables},
                    'Tags': self._get_all_tags()
                }
            else:
                code_content = self._prepare_zip_package()
                function_config = {
                    'FunctionName': self.function_name,
                    'Runtime': self.runtime,
                    'Role': execution_role_arn,
                    'Handler': self.handler,
                    'Code': {'ZipFile': code_content},
                    'MemorySize': self.memory_size,
                    'Timeout': self.timeout_seconds,
                    'Description': self.description or f"Lambda function {self.function_name}",
                    'Environment': {'Variables': self.environment_variables},
                    'Tags': self._get_all_tags()
                }

            response = self.lambda_client.create_function(**function_config)
            
            self.function_arn = response['FunctionArn']
            self.state = response['State']
            
            print("⏳ Waiting for function to be active...")
            self._wait_for_function_active()
            
            self._configure_triggers()
            
            print(f"✅ Lambda function created successfully!")
            
            result = {
                "success": True,
                "function_name": self.function_name,
                "function_arn": self.function_arn,
                "state": self.state
            }
            
            if self.api_gateway_url:
                result["api_gateway_url"] = self.api_gateway_url
                print(f"🌐 API Gateway URL: {self.api_gateway_url}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to create Lambda function: {str(e)}")
            return {"success": False, "error": str(e)}

    def _update_existing_function(self, existing_function: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.function_arn = existing_function['function_arn']
            
            update_config = {
                'FunctionName': self.function_name,
                'MemorySize': self.memory_size,
                'Timeout': self.timeout_seconds,
                'Description': self.description or f"Lambda function {self.function_name}",
                'Environment': {'Variables': self.environment_variables}
            }
            
            if self.deployment_package_type == "Zip":
                update_config['Runtime'] = self.runtime
                update_config['Handler'] = self.handler
            
            response = self.lambda_client.update_function_configuration(**update_config)
            
            if self.deployment_package_type == "Image":
                container_image_uri = self._build_and_push_container()
                if container_image_uri:
                    self.lambda_client.update_function_code(
                        FunctionName=self.function_name,
                        ImageUri=container_image_uri
                    )
            else:
                code_content = self._prepare_zip_package()
                self.lambda_client.update_function_code(
                    FunctionName=self.function_name,
                    ZipFile=code_content
                )
            
            print("⏳ Waiting for function update to complete...")
            self._wait_for_function_active()
            
            self._configure_triggers()
            
            print(f"✅ Lambda function updated successfully!")
            
            result = {
                "success": True,
                "function_name": self.function_name,
                "function_arn": self.function_arn,
                "updated": True
            }
            
            if self.api_gateway_url:
                result["api_gateway_url"] = self.api_gateway_url
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to update Lambda function: {str(e)}")
            return {"success": False, "error": str(e)}

    def _build_and_push_container(self) -> Optional[str]:
        if not self.container_template:
            return None
            
        try:
            ecr_client = self.get_ecr_client()
            repository_name = f"lambda-{self.function_name}"
            
            try:
                ecr_client.create_repository(repositoryName=repository_name)
                print(f"📦 Created ECR repository: {repository_name}")
            except Exception as e:
                if "RepositoryAlreadyExistsException" in str(e):
                    print(f"📦 Using existing ECR repository: {repository_name}")
                else:
                    raise
            
            response = ecr_client.describe_repositories(repositoryNames=[repository_name])
            repository_uri = response['repositories'][0]['repositoryUri']
            
            if self.container_manager:
                image_name = f"{repository_uri}:latest"
                success = self.container_manager.build_with_template(
                    image_name=image_name,
                    template_name=self.container_template,
                    context_path=".",
                    variables={"port": self.container_port or 8080}
                )
                
                if success:
                    success = self.container_manager.push(image_name, repository_uri)
                    if success:
                        return image_name
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to build/push container: {str(e)}")
            return None

    def get_ecr_client(self):
        try:
            import boto3
            return boto3.client('ecr', region_name=self.region)
        except Exception as e:
            print(f"⚠️  Failed to create ECR client: {e}")
            return None

    def _prepare_zip_package(self) -> bytes:
        if self.code_zip_file:
            with open(self.code_zip_file, 'rb') as f:
                return f.read()
        else:
            default_code = '''
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'function': context.function_name
        })
    }
'''
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('lambda_function.py', default_code)
            
            return zip_buffer.getvalue()

    def _ensure_execution_role(self) -> str:
        if self.execution_role_arn:
            return self.execution_role_arn
            
        role_name = f"lambda-execution-role-{self.function_name}"
        
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"📋 Using existing execution role: {role_name}")
            return role_arn
        except Exception as e:
            if "NoSuchEntity" not in str(e):
                raise
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Lambda execution role for {self.function_name}",
                Tags=[{"Key": "Name", "Value": role_name}]
            )
            role_arn = response['Role']['Arn']
            
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            print(f"📋 Created Lambda execution role: {role_name}")
            
            time.sleep(5)
            
            return role_arn
            
        except Exception as e:
            print(f"❌ Failed to create execution role: {str(e)}")
            raise

    def _configure_triggers(self):
        if self.api_gateway_integration:
            self._create_api_gateway_integration()
        
        for trigger_config in self.trigger_configurations:
            self._create_trigger(trigger_config)

    def _create_api_gateway_integration(self):
        try:
            response = self.apigateway_client.create_rest_api(
                name=f"{self.function_name}-api",
                description=f"API Gateway for Lambda function {self.function_name}",
                endpointConfiguration={'types': ['REGIONAL']}
            )
            
            api_id = response['id']
            
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            root_resource_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
            
            proxy_resource = self.apigateway_client.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='{proxy+}'
            )
            
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                authorizationType='NONE'
            )
            
            integration_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{self.function_arn}/invocations"
            
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=integration_uri
            )
            
            self.lambda_client.add_permission(
                FunctionName=self.function_name,
                StatementId=f"apigateway-invoke-{int(time.time())}",
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{self.region}:*:{api_id}/*/*"
            )
            
            deployment = self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod'
            )
            
            self.api_gateway_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
            
            print(f"✅ API Gateway integration created successfully!")
            
        except Exception as e:
            print(f"⚠️  Failed to create API Gateway integration: {str(e)}")

    def _create_trigger(self, trigger_config: Dict[str, Any]):
        trigger_type = trigger_config.get('type')

        if trigger_type == 's3':
            self._create_s3_trigger(trigger_config)
        elif trigger_type == 'sqs':
            self._create_sqs_trigger(trigger_config)
        elif trigger_type == 'eventbridge':
            self._create_eventbridge_trigger(trigger_config)
        elif trigger_type == 'cloudwatch':
            self._create_cloudwatch_trigger(trigger_config)

    def _create_s3_trigger(self, trigger_config: Dict[str, Any]):
        print(f"   Configuring S3 trigger for bucket: {trigger_config.get('bucket')}")
        print(f"   S3 trigger for bucket '{trigger_config.get('bucket')}' created (mock)")

    def _create_sqs_trigger(self, trigger_config: Dict[str, Any]):
        print(f"   Configuring SQS trigger for queue: {trigger_config.get('queue_arn')}")
        print(f"   SQS trigger for queue '{trigger_config.get('queue_arn')}' created (mock)")

    def _create_eventbridge_trigger(self, trigger_config: Dict[str, Any]):
        print(f"   Configuring EventBridge trigger for rule: {trigger_config.get('rule_name')}")
        print(f"   EventBridge trigger for rule '{trigger_config.get('rule_name')}' created (mock)")

    def _create_cloudwatch_trigger(self, trigger_config: Dict[str, Any]):
        print(f"   Configuring CloudWatch trigger for rule: {trigger_config.get('rule_name')}")
        print(f"   CloudWatch trigger for rule '{trigger_config.get('rule_name')}' created (mock)")

    def _wait_for_function_active(self):
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = self.lambda_client.get_function(FunctionName=self.function_name)
                state = response['Configuration']['State']
                
                if state == 'Active':
                    self.state = state
                    return
                elif state == 'Failed':
                    raise Exception(f"Function entered Failed state: {response['Configuration'].get('StateReason', 'Unknown')}")
                
                time.sleep(2)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Function did not become active within expected time")

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        
        try:
            self.lambda_client.delete_function(FunctionName=self.function_name)
            
            print(f"✅ Lambda function '{self.function_name}' destroyed!")
            return {"success": True, "message": f"Lambda function '{self.function_name}' destroyed"}
            
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                print(f"✅ Lambda function '{self.function_name}' already destroyed")
                return {"success": True, "message": f"Lambda function '{self.function_name}' already destroyed"}
            
            print(f"❌ Failed to destroy Lambda function: {str(e)}")
            return {"success": False, "error": str(e)}