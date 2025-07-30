"""
Lambda Security and IAM Management

This module handles Lambda execution roles, IAM policies, VPC configuration,
and security-related operations.
"""

from typing import Dict, Any, List, Optional
import json


class LambdaSecurityManager:
    """
    Lambda Security and IAM Management
    
    Handles:
    - IAM execution role creation and management
    - Policy creation and attachment
    - Security group and VPC configuration
    - Permission management for function access
    """
    
    def __init__(self, aws_client):
        """Initialize the security manager with AWS client."""
        self.aws_client = aws_client
    
    def create_execution_role(
        self,
        role_name: str,
        additional_policies: Optional[List[str]] = None,
        custom_policy: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create or ensure Lambda execution role exists.
        
        Args:
            role_name: Name of the IAM role
            additional_policies: Additional AWS managed policy ARNs
            custom_policy: Custom inline policy document
            tags: Tags to apply to the role
            
        Returns:
            Role creation result with ARN
        """
        try:
            # Check if role already exists
            try:
                response = self.aws_client.iam.get_role(RoleName=role_name)
                print(f"📋 IAM role '{role_name}' already exists")
                return {
                    'role_arn': response['Role']['Arn'],
                    'role_name': role_name,
                    'created': False
                }
            except:
                pass
            
            print(f"🔐 Creating IAM execution role: {role_name}")
            
            # Trust policy for Lambda
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # Create the role
            create_params = {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': json.dumps(trust_policy),
                'Description': f'Execution role for Lambda function managed by InfraDSL'
            }
            
            if tags:
                create_params['Tags'] = [
                    {'Key': key, 'Value': value}
                    for key, value in tags.items()
                ]
            
            response = self.aws_client.iam.create_role(**create_params)
            role_arn = response['Role']['Arn']
            
            # Attach basic Lambda execution policy
            self.aws_client.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach additional policies if provided
            if additional_policies:
                for policy_arn in additional_policies:
                    self.aws_client.iam.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
            
            # Create custom inline policy if provided
            if custom_policy:
                self.aws_client.iam.put_role_policy(
                    RoleName=role_name,
                    PolicyName=f'{role_name}-custom-policy',
                    PolicyDocument=json.dumps(custom_policy)
                )
            
            print(f"✅ IAM execution role created: {role_name}")
            
            return {
                'role_arn': role_arn,
                'role_name': role_name,
                'created': True
            }
            
        except Exception as e:
            print(f"❌ Failed to create execution role '{role_name}': {str(e)}")
            raise
    
    def get_default_execution_role_name(self, function_name: str) -> str:
        """Get default execution role name for a function."""
        return f"{function_name}-execution-role"
    
    def create_vpc_execution_role(
        self,
        role_name: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create execution role with VPC permissions.
        
        Args:
            role_name: Name of the IAM role
            tags: Tags to apply to the role
            
        Returns:
            Role creation result
        """
        vpc_policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole'
        ]
        
        return self.create_execution_role(
            role_name=role_name,
            additional_policies=vpc_policies,
            tags=tags
        )
    
    def create_s3_access_role(
        self,
        role_name: str,
        bucket_names: List[str],
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create execution role with S3 access permissions.
        
        Args:
            role_name: Name of the IAM role
            bucket_names: List of S3 bucket names to access
            tags: Tags to apply to the role
            
        Returns:
            Role creation result
        """
        # Create custom S3 policy
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket}/*" for bucket in bucket_names
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket}" for bucket in bucket_names
                    ]
                }
            ]
        }
        
        return self.create_execution_role(
            role_name=role_name,
            custom_policy=s3_policy,
            tags=tags
        )
    
    def create_dynamodb_access_role(
        self,
        role_name: str,
        table_names: List[str],
        permissions: List[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create execution role with DynamoDB access permissions.
        
        Args:
            role_name: Name of the IAM role
            table_names: List of DynamoDB table names
            permissions: List of DynamoDB permissions (default: read/write)
            tags: Tags to apply to the role
            
        Returns:
            Role creation result
        """
        if not permissions:
            permissions = [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ]
        
        # Create custom DynamoDB policy
        dynamodb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": permissions,
                    "Resource": [
                        f"arn:aws:dynamodb:*:*:table/{table}" for table in table_names
                    ] + [
                        f"arn:aws:dynamodb:*:*:table/{table}/index/*" for table in table_names
                    ]
                }
            ]
        }
        
        return self.create_execution_role(
            role_name=role_name,
            custom_policy=dynamodb_policy,
            tags=tags
        )
    
    def configure_vpc_settings(
        self,
        security_group_ids: List[str],
        subnet_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Configure VPC settings for Lambda function.
        
        Args:
            security_group_ids: List of security group IDs
            subnet_ids: List of subnet IDs
            
        Returns:
            VPC configuration
        """
        if not security_group_ids or not subnet_ids:
            raise ValueError("Both security group IDs and subnet IDs are required for VPC configuration")
        
        return {
            'SubnetIds': subnet_ids,
            'SecurityGroupIds': security_group_ids
        }
    
    def create_resource_based_policy(
        self,
        function_name: str,
        principal: str,
        action: str = "lambda:InvokeFunction",
        source_arn: Optional[str] = None,
        statement_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add resource-based policy to Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            principal: Principal (service or account) to grant permission
            action: Action to allow (default: lambda:InvokeFunction)
            source_arn: Source ARN for the permission
            statement_id: Statement ID (auto-generated if not provided)
            
        Returns:
            Permission addition result
        """
        try:
            if not statement_id:
                statement_id = f"allow-{principal.replace('.', '-').replace(':', '-')}"
            
            params = {
                'FunctionName': function_name,
                'StatementId': statement_id,
                'Action': action,
                'Principal': principal
            }
            
            if source_arn:
                params['SourceArn'] = source_arn
            
            response = self.aws_client.lambda_client.add_permission(**params)
            
            print(f"✅ Permission added for {principal} to invoke {function_name}")
            
            return {
                'added': True,
                'statement_id': statement_id,
                'statement': response.get('Statement')
            }
            
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                print(f"⚠️  Permission already exists for {principal}")
                return {'added': False, 'reason': 'Permission already exists'}
            else:
                print(f"❌ Failed to add permission: {str(e)}")
                raise
    
    def remove_resource_based_policy(
        self,
        function_name: str,
        statement_id: str
    ) -> Dict[str, Any]:
        """
        Remove resource-based policy from Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            statement_id: Statement ID to remove
            
        Returns:
            Permission removal result
        """
        try:
            self.aws_client.lambda_client.remove_permission(
                FunctionName=function_name,
                StatementId=statement_id
            )
            
            print(f"✅ Permission removed: {statement_id}")
            
            return {'removed': True, 'statement_id': statement_id}
            
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                print(f"⚠️  Permission not found: {statement_id}")
                return {'removed': False, 'reason': 'Permission not found'}
            else:
                print(f"❌ Failed to remove permission: {str(e)}")
                raise
    
    def get_function_permissions(self, function_name: str) -> Dict[str, Any]:
        """
        Get current resource-based permissions for a function.
        
        Args:
            function_name: Name of the Lambda function
            
        Returns:
            Function permissions
        """
        try:
            response = self.aws_client.lambda_client.get_policy(FunctionName=function_name)
            policy = json.loads(response['Policy'])
            
            permissions = []
            for statement in policy.get('Statement', []):
                permissions.append({
                    'sid': statement.get('Sid'),
                    'effect': statement.get('Effect'),
                    'principal': statement.get('Principal'),
                    'action': statement.get('Action'),
                    'resource': statement.get('Resource'),
                    'condition': statement.get('Condition')
                })
            
            return {
                'has_permissions': True,
                'permissions': permissions,
                'policy_document': policy
            }
            
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                return {'has_permissions': False, 'permissions': []}
            else:
                print(f"❌ Failed to get function permissions: {str(e)}")
                return {'has_permissions': False, 'error': str(e)}
    
    def validate_execution_role(self, role_arn: str) -> Dict[str, Any]:
        """
        Validate that the execution role exists and has required permissions.
        
        Args:
            role_arn: ARN of the execution role
            
        Returns:
            Validation result
        """
        try:
            # Extract role name from ARN
            role_name = role_arn.split('/')[-1]
            
            # Check if role exists
            role_response = self.aws_client.iam.get_role(RoleName=role_name)
            role = role_response['Role']
            
            # Get attached policies
            policies_response = self.aws_client.iam.list_attached_role_policies(RoleName=role_name)
            attached_policies = policies_response.get('AttachedPolicies', [])
            
            # Get inline policies
            inline_policies_response = self.aws_client.iam.list_role_policies(RoleName=role_name)
            inline_policies = inline_policies_response.get('PolicyNames', [])
            
            # Check for basic Lambda execution policy
            has_basic_execution = any(
                'AWSLambdaBasicExecutionRole' in policy['PolicyArn']
                for policy in attached_policies
            )
            
            return {
                'valid': True,
                'role_name': role_name,
                'role_arn': role_arn,
                'created_date': role['CreateDate'],
                'attached_policies': len(attached_policies),
                'inline_policies': len(inline_policies),
                'has_basic_execution_role': has_basic_execution,
                'policies': [policy['PolicyName'] for policy in attached_policies]
            }
            
        except Exception as e:
            return {
                'valid': False,
                'role_arn': role_arn,
                'error': str(e)
            }
    
    def delete_execution_role(self, role_name: str) -> Dict[str, Any]:
        """
        Delete Lambda execution role and its policies.
        
        Args:
            role_name: Name of the IAM role to delete
            
        Returns:
            Deletion result
        """
        try:
            print(f"🗑️  Deleting IAM execution role: {role_name}")
            
            # Detach all managed policies
            policies_response = self.aws_client.iam.list_attached_role_policies(RoleName=role_name)
            for policy in policies_response.get('AttachedPolicies', []):
                self.aws_client.iam.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy['PolicyArn']
                )
            
            # Delete all inline policies
            inline_policies_response = self.aws_client.iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies_response.get('PolicyNames', []):
                self.aws_client.iam.delete_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name
                )
            
            # Delete the role
            self.aws_client.iam.delete_role(RoleName=role_name)
            
            print(f"✅ IAM execution role deleted: {role_name}")
            
            return {'deleted': True, 'role_name': role_name}
            
        except Exception as e:
            if 'NoSuchEntity' in str(e):
                print(f"⚠️  IAM role not found: {role_name}")
                return {'deleted': False, 'reason': 'Role not found'}
            else:
                print(f"❌ Failed to delete execution role: {str(e)}")
                raise