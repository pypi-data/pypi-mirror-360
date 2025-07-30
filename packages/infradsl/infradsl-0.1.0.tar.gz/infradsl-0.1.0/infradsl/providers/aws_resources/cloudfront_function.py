"""
AWS CloudFront Functions Resource

Rails-like edge function management with intelligent defaults and convention over configuration.
Supports viewer-request and viewer-response functions for edge computing at CloudFront.
"""

import os
from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseAwsResource


class CloudFrontFunction(BaseAwsResource):
    """
    AWS CloudFront Functions Resource
    
    Rails-like edge function management with intelligent defaults and common patterns.
    Supports JavaScript functions that run at CloudFront edge locations for request/response manipulation.
    """
    
    def __init__(self, name: str):
        """
        Initialize CloudFront Function resource.
        
        Args:
            name: Function name for identification
        """
        super().__init__(name)
        
        # Core function configuration
        self.function_name = name
        self.function_arn = None
        self.function_code = None
        self.function_comment = f"Managed by InfraDSL: {name}"
        
        # Event type configuration
        self.event_type = None  # viewer-request or viewer-response
        self.supported_event_types = ['viewer-request', 'viewer-response']
        
        # Distribution associations
        self.distribution_associations = []  # List of {distribution_id, path_pattern}
        
        # Code management
        self.code_source = 'inline'  # inline, file, template
        self.code_file_path = None
        self.code_template = None
        
        # Function state
        self.function_created = False
        self.function_published = False
        self.function_stage = 'DEVELOPMENT'
        self.function_status = None
        self.function_etag = None
        
        # Tags
        self.function_tags = {}
        
        # Managers (will be initialized after authentication)
        self.cloudfront_functions_manager = None
        
    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        # CloudFront Functions managers will be initialized after authentication
        pass
    
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize AWS client for CloudFront Functions operations
        from ..aws_managers.aws_client import AwsClient
        self.aws_client = AwsClient()
        self.aws_client.authenticate(silent=True)
        
        # Initialize the CloudFront Functions manager
        from ..aws_managers.cloudfront_functions import CloudFrontFunctionsManager
        self.cloudfront_functions_manager = CloudFrontFunctionsManager(self.aws_client)
        
        # Load code if from file
        if self.code_source == 'file' and self.code_file_path:
            self._load_code_from_file()
        elif self.code_source == 'template' and self.code_template:
            self._load_code_from_template()
    
    def _load_code_from_file(self):
        """Load JavaScript code from file"""
        if not os.path.exists(self.code_file_path):
            raise ValueError(f"Code file not found: {self.code_file_path}")
        
        with open(self.code_file_path, 'r', encoding='utf-8') as f:
            self.function_code = f.read()
    
    def _load_code_from_template(self):
        """Load code from predefined template"""
        if self.code_template == 'security-headers':
            if self.event_type == 'viewer-response':
                self.function_code = self.cloudfront_functions_manager.functions_core.get_default_viewer_response_code()
            else:
                self.function_code = self.cloudfront_functions_manager.functions_core.get_default_viewer_request_code()
        else:
            raise ValueError(f"Unknown code template: {self.code_template}")
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Use the manager for discovery
        existing_functions = self.cloudfront_functions_manager.discover_existing_functions()
        
        # Determine desired state
        desired_function_name = self.function_name
        
        # Categorize functions
        to_create = []
        to_keep = []
        to_remove = []
        
        # Check if our desired function exists
        function_exists = False
        for func_name, func_info in existing_functions.items():
            if func_name == desired_function_name:
                to_keep.append(func_info)
                function_exists = True
                break
        
        # If our function doesn't exist, it needs to be created
        if not function_exists:
            to_create.append({
                'name': desired_function_name,
                'event_type': self.event_type,
                'code_size': len(self.function_code.encode('utf-8')) if self.function_code else 0,
                'code_source': self.code_source,
                'associations': len(self.distribution_associations)
            })
        
        self._display_preview(to_create, to_keep, to_remove)
        
        return {
            'resource_type': 'aws_cloudfront_function',
            'name': self.function_name,
            'function_arn': f"arn:aws:cloudfront::function/{self.function_name}",  # Mock ARN for preview
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_functions': existing_functions,
            'event_type': self.event_type,
            'code_size': len(self.function_code.encode('utf-8')) if self.function_code else 0,
            'code_source': self.code_source,
            'associations': len(self.distribution_associations),
            'estimated_deployment_time': '2-3 minutes'
        }
    
    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n⚡ CloudFront Function Preview")
        
        # Show functions to create
        if to_create:
            print(f"╭─ 📦 Functions to CREATE: {len(to_create)}")
            for func in to_create:
                print(f"├─ 🆕 {func['name']}")
                print(f"│  ├─ 🎯 Event Type: {func['event_type']}")
                print(f"│  ├─ 📄 Code Size: {func['code_size']} bytes")
                print(f"│  ├─ 📝 Code Source: {func['code_source']}")
                print(f"│  ├─ 🔗 Associations: {func['associations']} distributions")
                print(f"│  └─ ⏱️  Deployment Time: 2-3 minutes")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ ⚡ Function Executions: $0.10 per 1M invocations")
        print(f"   ├─ 🖥️  Compute Time: $0.0000000417 per 128MB-ms")
        print(f"   └─ 📊 CloudFront Functions are extremely cost-effective")
    
    def create(self) -> Dict[str, Any]:
        """Create the CloudFront Function"""
        self._ensure_authenticated()
        
        if not self.cloudfront_functions_manager:
            raise Exception("CloudFront Functions manager not initialized")
        
        if not self.function_code:
            raise ValueError("Function code is required")
        
        if not self.event_type:
            raise ValueError("Event type is required (viewer-request or viewer-response)")
        
        # Check for existing functions first
        existing_functions = self.cloudfront_functions_manager.discover_existing_functions()
        print(f"🔍 Discovered {len(existing_functions)} existing CloudFront Functions")
        
        # Check if function already exists
        existing_func = self._find_existing_function(existing_functions)
        if existing_func:
            return existing_func
        
        print(f"\n⚡ Creating CloudFront Function: {self.function_name}")
        
        try:
            # Create the function using the manager
            result = self.cloudfront_functions_manager.create_function({
                'name': self.function_name,
                'code': self.function_code,
                'comment': self.function_comment
            })
            
            # Store the results
            self.function_arn = result['function_arn']
            self.function_status = result['status']
            self.function_stage = result['stage']
            self.function_etag = result['etag']
            self.function_created = True
            self.function_published = True
            
            final_result = {
                'function_arn': result['function_arn'],
                'function_name': self.function_name,
                'event_type': self.event_type,
                'status': result['status'],
                'stage': result['stage'],
                'code_size': len(self.function_code.encode('utf-8')),
                'created': True,
                'published': True
            }
            
            # Associate with distributions if specified
            if self.distribution_associations:
                self._associate_with_distributions()
                final_result['associations_created'] = len(self.distribution_associations)
            
            self._display_creation_success(final_result)
            return final_result
            
        except Exception as e:
            print(f"❌ Failed to create CloudFront Function: {str(e)}")
            raise
    
    def _find_existing_function(self, existing_functions: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find and potentially adopt existing functions"""
        if self.function_name in existing_functions:
            func_info = existing_functions[self.function_name]
            print(f"\n🔄 CloudFront Function '{self.function_name}' already exists")
            print(f"   📋 Function ARN: {func_info['arn']}")
            print(f"   🎯 Stage: {func_info['stage']}")
            print(f"   📊 Status: {func_info['status']}")
            
            return {
                'function_arn': func_info['arn'],
                'function_name': self.function_name,
                'event_type': self.event_type,
                'status': func_info['status'],
                'stage': func_info['stage'],
                'existing': True
            }
        
        return None
    
    def _associate_with_distributions(self):
        """Associate function with CloudFront distributions"""
        for association in self.distribution_associations:
            function_associations = [{
                'function_arn': self.function_arn,
                'event_type': self.event_type,
                'path_pattern': association.get('path_pattern', '/*')
            }]
            
            self.cloudfront_functions_manager.associate_with_distribution(
                association['distribution_id'],
                function_associations
            )
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ CloudFront Function created successfully")
        print(f"   📋 Function ARN: {result['function_arn']}")
        print(f"   🎯 Event Type: {result['event_type']}")
        print(f"   📄 Code Size: {result['code_size']} bytes")
        print(f"   📊 Status: {result['status']} ({result['stage']})")
        if result.get('associations_created'):
            print(f"   🔗 Associations: {result['associations_created']} distributions")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the CloudFront Function"""
        self._ensure_authenticated()
        
        print(f"🗑️ Destroying CloudFront Function: {self.function_name}")
        
        if self.function_etag:
            result = self.cloudfront_functions_manager.delete_function(
                self.function_name, 
                self.function_etag
            )
        else:
            result = {
                'name': self.function_name,
                'status': 'Not found',
                'deleted': False
            }
        
        print(f"✅ CloudFront Function destruction completed")
        return result
    
    def test(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the CloudFront Function with sample event data"""
        self._ensure_authenticated()
        
        if not self.function_created:
            raise ValueError("Function must be created before testing")
        
        return self.cloudfront_functions_manager.test_function(
            self.function_name,
            self.function_stage,
            event_data
        )
    
    # Rails-like chainable methods for configuration
    def viewer_request(self):
        """Configure as viewer-request function - chainable"""
        self.event_type = 'viewer-request'
        return self
    
    def viewer_response(self):
        """Configure as viewer-response function - chainable"""
        self.event_type = 'viewer-response'
        return self
    
    def javascript_code(self, code: str):
        """Set JavaScript code inline - chainable"""
        self.function_code = code
        self.code_source = 'inline'
        return self
    
    def code_from_file(self, file_path: str):
        """Load JavaScript code from file - chainable"""
        self.code_file_path = file_path
        self.code_source = 'file'
        return self
    
    def security_headers_template(self):
        """Use built-in security headers template - chainable"""
        self.code_template = 'security-headers'
        self.code_source = 'template'
        return self
    
    def comment(self, comment: str):
        """Set function comment - chainable"""
        self.function_comment = comment
        return self
    
    def attach_to_distribution(self, distribution_id: str, path_pattern: str = '/*'):
        """Attach function to CloudFront distribution - chainable"""
        self.distribution_associations.append({
            'distribution_id': distribution_id,
            'path_pattern': path_pattern
        })
        return self
    
    def tag(self, key: str, value: str):
        """Add a single tag to the function - chainable"""
        self.function_tags[key] = value
        return self
    
    def tags(self, tag_dict: Dict[str, str]):
        """Add multiple tags to the function - chainable"""
        self.function_tags.update(tag_dict)
        return self
    
    # Convenience methods for common patterns
    def auth_check(self, auth_header: str = 'Authorization'):
        """Create authentication check function - chainable"""
        self.viewer_request()
        auth_code = f"""function handler(event) {{
    var request = event.request;
    var headers = request.headers;
    
    // Check for authentication header
    if (!headers['{auth_header}']) {{
        return {{
            statusCode: 401,
            statusDescription: 'Unauthorized',
            headers: {{
                'www-authenticate': {{value: 'Basic realm="Restricted Area"'}}
            }}
        }};
    }}
    
    return request;
}}"""
        return self.javascript_code(auth_code)
    
    def redirect_to_https(self):
        """Create HTTPS redirect function - chainable"""
        self.viewer_request()
        redirect_code = """function handler(event) {
    var request = event.request;
    var uri = request.uri;
    var headers = request.headers;
    
    // Redirect HTTP to HTTPS
    if (headers['cloudfront-forwarded-proto'] && 
        headers['cloudfront-forwarded-proto'].value === 'http') {
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                'location': {value: 'https://' + headers.host.value + uri}
            }
        };
    }
    
    return request;
}"""
        return self.javascript_code(redirect_code)
    
    def add_security_headers(self):
        """Add comprehensive security headers - chainable"""
        self.viewer_response()
        return self.security_headers_template()
    
    def cache_control(self, max_age: int = 3600):
        """Add cache control headers - chainable"""
        self.viewer_response()
        cache_code = f"""function handler(event) {{
    var response = event.response;
    var headers = response.headers;
    
    // Add cache control headers
    headers['cache-control'] = {{value: 'public, max-age={max_age}'}};
    headers['expires'] = {{value: new Date(Date.now() + {max_age} * 1000).toUTCString()}};
    
    return response;
}}"""
        return self.javascript_code(cache_code)
    
    def url_rewrite(self, from_pattern: str, to_pattern: str):
        """Create URL rewrite function - chainable"""
        self.viewer_request()
        rewrite_code = f"""function handler(event) {{
    var request = event.request;
    var uri = request.uri;
    
    // URL rewriting
    if (uri.match(/{from_pattern}/)) {{
        request.uri = uri.replace(/{from_pattern}/, '{to_pattern}');
    }}
    
    return request;
}}"""
        return self.javascript_code(rewrite_code)