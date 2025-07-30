from typing import Dict, Any, List, Optional
from datetime import datetime


class LambdaFunctionDiscoveryMixin:
    def _discover_existing_functions(self) -> Dict[str, Any]:
        try:
            existing_functions = {}
            
            paginator = self.lambda_client.get_paginator('list_functions')
            page_iterator = paginator.paginate()
            
            base_name = self.name.lower().replace('_', '-')
            
            for page in page_iterator:
                for function in page['Functions']:
                    function_name = function['FunctionName']
                    
                    is_related = False
                    
                    if function_name == self.function_name:
                        is_related = True
                    
                    elif base_name in function_name.lower():
                        is_related = True
                    
                    try:
                        tags_response = self.lambda_client.list_tags(Resource=function['FunctionArn'])
                        tags = tags_response.get('Tags', {})
                        if any(tag_key.lower() in ['infradsl', 'managedby'] for tag_key in tags.keys()):
                            is_related = True
                    except Exception:
                        pass
                    
                    if is_related:
                        last_modified = function.get('LastModified', 'unknown')
                        if last_modified != 'unknown':
                            try:
                                dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                                last_modified = dt.strftime('%Y-%m-%d %H:%M')
                            except Exception:
                                pass
                        
                        existing_functions[function_name] = {
                            'function_name': function_name,
                            'function_arn': function['FunctionArn'],
                            'runtime': function.get('Runtime', 'Container'),
                            'handler': function.get('Handler', 'N/A'),
                            'memory_size': function['MemorySize'],
                            'timeout': function['Timeout'],
                            'last_modified': last_modified,
                            'state': function['State'],
                            'package_type': function.get('PackageType', 'Zip')
                        }
            
            return existing_functions
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing Lambda functions: {str(e)}")
            return {}

    def _find_existing_function(self) -> Optional[Dict[str, Any]]:
        try:
            response = self.lambda_client.get_function(FunctionName=self.function_name)
            function_config = response['Configuration']
            
            return {
                'function_arn': function_config['FunctionArn'],
                'function_name': function_config['FunctionName'],
                'runtime': function_config.get('Runtime', 'Container'),
                'handler': function_config.get('Handler'),
                'memory_size': function_config['MemorySize'],
                'timeout': function_config['Timeout'],
                'last_modified': function_config['LastModified'],
                'state': function_config['State'],
                'package_type': function_config.get('PackageType', 'Zip')
            }
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                return None
            print(f"⚠️  Failed to check for existing function: {str(e)}")
            return None
