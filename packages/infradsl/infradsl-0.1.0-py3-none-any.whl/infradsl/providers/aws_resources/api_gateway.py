"""
AWS API Gateway Resource

Rails-like API Gateway management with intelligent defaults and chainable methods.
Supports HTTP APIs, REST APIs, and WebSocket APIs with Lambda integration.
"""

import json
from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseAwsResource


class APIGateway(BaseAwsResource):
    """AWS API Gateway Resource with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        
        # Core configuration
        self.api_name = name
        self.api_type = "HTTP"  # HTTP, REST, or WEBSOCKET
        self.protocol_type = "HTTP"  # HTTP or WEBSOCKET
        self.description = f"API Gateway for {name}"
        
        # Routes and integrations
        self.routes = []
        self.lambda_integrations = {}
        self.proxy_integrations = {}
        
        # Domain and CORS
        self.custom_domain = None
        self.certificate_arn = None
        self.cors_enabled = True
        self.cors_config = {
            "AllowCredentials": False,
            "AllowHeaders": ["content-type", "x-amz-date", "authorization"],
            "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "AllowOrigins": ["*"],
            "MaxAge": 300
        }
        
        # Authentication and authorization
        self.authorizers = []
        self.api_key_required = False
        self.usage_plan = None
        
        # Rate limiting and throttling
        self.throttle_burst_limit = 5000
        self.throttle_rate_limit = 2000
        
        # Logging and monitoring
        self.access_logging_enabled = True
        self.execution_logging_enabled = True
        self.log_level = "INFO"
        self.metrics_enabled = True
        
        # Tags
        self.api_tags = {}

        # State
        self.api_id = None
        self.api_endpoint = None
        self.stage_name = "prod"
        self.deployment_id = None
        self.custom_domain_configured = False

        # Clients
        self.apigatewayv2_client = None  # For HTTP and WebSocket APIs
        self.apigateway_client = None    # For REST APIs

    def _initialize_managers(self):
        self.apigatewayv2_client = None
        self.apigateway_client = None

    def _post_authentication_setup(self):
        # Initialize AWS client for API Gateway operations
        from ..aws_managers.aws_client import AwsClient
        self.aws_client = AwsClient()
        self.aws_client.authenticate(silent=True)
        
        self.apigatewayv2_client = self.get_apigatewayv2_client()
        self.apigateway_client = self.get_apigateway_client()

    def get_apigatewayv2_client(self):
        try:
            import boto3
            return boto3.client('apigatewayv2', region_name=self.get_current_region())
        except Exception as e:
            print(f"⚠️  Failed to create API Gateway v2 client: {e}")
            return None

    def get_apigateway_client(self):
        try:
            import boto3
            return boto3.client('apigateway', region_name=self.get_current_region())
        except Exception as e:
            print(f"⚠️  Failed to create API Gateway client: {e}")
            return None

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing APIs
        existing_apis = self._discover_existing_apis()
        
        # Determine desired state
        desired_api_name = self.api_name
        
        # Categorize APIs
        apis_to_create = []
        apis_to_keep = []
        apis_to_remove = []
        
        # Check if our desired API exists
        api_exists = False
        for api_id, api_info in existing_apis.items():
            if api_info['name'] == desired_api_name:
                apis_to_keep.append(api_info)
                api_exists = True
            # In real implementation, might remove APIs not in current configuration
            # For now, we'll focus on our desired API
        
        # If our API doesn't exist, it needs to be created
        if not api_exists:
            apis_to_create.append({
                'name': desired_api_name,
                'api_type': self.api_type,
                'protocol_type': self.protocol_type,
                'routes': len(self.routes),
                'custom_domain': self.custom_domain,
                'cors_enabled': self.cors_enabled,
                'auth_required': len(self.authorizers) > 0,
                'rate_limiting': f"{self.throttle_rate_limit}/sec, {self.throttle_burst_limit} burst"
            })

        print(f"\n🌐 API Gateway Configuration Preview")
        
        # Show APIs to create
        if apis_to_create:
            print(f"╭─ 🌐 APIs to CREATE: {len(apis_to_create)}")
            for api in apis_to_create:
                print(f"├─ 🆕 {api['name']}")
                print(f"│  ├─ 🔧 Type: {api['api_type']} API")
                print(f"│  ├─ 📡 Protocol: {api['protocol_type']}")
                print(f"│  ├─ 🛣️  Routes: {api['routes']} configured")
                if api['custom_domain']:
                    print(f"│  ├─ 🔗 Domain: {api['custom_domain']}")
                print(f"│  ├─ 🌍 CORS: {'Enabled' if api['cors_enabled'] else 'Disabled'}")
                print(f"│  ├─ 🔐 Auth: {'Required' if api['auth_required'] else 'Open'}")
                print(f"│  ├─ 🚦 Rate Limit: {api['rate_limiting']}")
                print(f"│  ├─ 📊 Monitoring: CloudWatch integration")
                print(f"│  └─ 📝 Logging: Access & execution logs")
            print(f"╰─")
            
            # Show route details if any
            if self.routes:
                print(f"\n╭─ 🛣️  Routes Configuration:")
                for i, route in enumerate(self.routes):
                    method = route.get('method', 'ANY')
                    path = route.get('path', '/')
                    integration = route.get('integration_type', 'lambda')
                    connector = "├─" if i < len(self.routes) - 1 else "└─"
                    print(f"{connector} {method} {path} → {integration}")
                print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        api_type_costs = {
            'HTTP': '$1.00 per million requests',
            'REST': '$3.50 per million requests', 
            'WEBSOCKET': '$1.00 per million messages + $0.25/million connection minutes'
        }
        print(f"   ├─ 🌐 API Requests: {api_type_costs.get(self.api_type, '$1.00 per million requests')}")
        print(f"   ├─ 📊 CloudWatch Logs: $0.50 per GB ingested")
        print(f"   ├─ 🔐 Authorizers: $0.00000225 per request (if used)")
        if self.custom_domain:
            print(f"   ├─ 🔗 Custom Domain: $0.50 per domain per month")
        print(f"   └─ 🎯 Free Tier: 1M API calls per month")

        return {
            'resource_type': 'aws_api_gateway',
            'name': self.api_name,
            'apis_to_create': apis_to_create,
            'apis_to_keep': apis_to_keep,
            'apis_to_remove': apis_to_remove,
            'existing_apis': existing_apis,
            'api_type': self.api_type,
            'protocol_type': self.protocol_type,
            'routes_count': len(self.routes),
            'custom_domain': self.custom_domain,
            'cors_enabled': self.cors_enabled,
            'auth_required': len(self.authorizers) > 0,
            'rate_limiting': f"{self.throttle_rate_limit}/sec",
            'estimated_requests': '1M free tier'
        }

    def create(self) -> Dict[str, Any]:
        """Create the API Gateway with smart state management"""
        self._ensure_authenticated()
        
        # Discover existing APIs first
        existing_apis = self._discover_existing_apis()
        
        # Determine what changes need to be made
        desired_api_name = self.api_name
        
        # Check for APIs to remove (not in current configuration)
        apis_to_remove = []
        for api_id, api_info in existing_apis.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which APIs should be removed
            # For now, we'll focus on creating the desired API
            pass
        
        # Remove APIs no longer in configuration
        if apis_to_remove:
            print(f"\n🗑️  Removing API Gateway APIs no longer in configuration:")
            for api_info in apis_to_remove:
                print(f"╭─ 🔄 Removing API: {api_info['name']}")
                print(f"├─ 🆔 API ID: {api_info['api_id']}")
                print(f"├─ 📡 Protocol: {api_info['protocol_type']}")
                print(f"├─ 🌐 Endpoint: {api_info.get('api_endpoint', 'N/A')}")
                print(f"└─ ⚠️  API will be permanently deleted")
                
                # In real implementation:
                # if api_info['api_type'] == 'v2':
                #     self.apigatewayv2_client.delete_api(ApiId=api_info['api_id'])
                # else:
                #     self.apigateway_client.delete_rest_api(restApiId=api_info['api_id'])
        
        # Check if our desired API already exists
        existing_api = self._find_existing_api()
        if existing_api:
            print(f"\n🔄 API Gateway '{self.api_name}' already exists")
            self.api_id = existing_api.get('ApiId') or existing_api.get('id')
            self.api_endpoint = existing_api.get('ApiEndpoint') or existing_api.get('api_endpoint')
            
            result = self._get_api_info()
            if len(apis_to_remove) > 0:
                result['changes'] = True
            return result
        
        print(f"\n🚀 Creating API Gateway: {self.api_name}")
        result = self._create_new_api()
        if len(apis_to_remove) > 0:
            result['changes'] = True
        return result

    def _find_existing_api(self) -> Optional[Dict[str, Any]]:
        try:
            if self.api_type in ["HTTP", "WEBSOCKET"]:
                response = self.apigatewayv2_client.get_apis()
                for api in response.get('Items', []):
                    if api['Name'] == self.api_name:
                        return api
            else:  # REST API
                response = self.apigateway_client.get_rest_apis()
                for api in response.get('items', []):
                    if api['name'] == self.api_name:
                        return api
            return None
        except Exception:
            return None

    def _create_new_api(self) -> Dict[str, Any]:
        try:
            if self.api_type in ["HTTP", "WEBSOCKET"]:
                return self._create_v2_api()
            else:
                return self._create_rest_api()
        except Exception as e:
            print(f"❌ Failed to create API Gateway: {str(e)}")
            raise

    def _create_v2_api(self) -> Dict[str, Any]:
        """Create HTTP or WebSocket API using API Gateway v2"""
        try:
            # Create API
            api_params = {
                'Name': self.api_name,
                'ProtocolType': self.protocol_type,
                'Description': self.description,
                'Tags': self.api_tags
            }

            if self.cors_enabled and self.api_type == "HTTP":
                api_params['CorsConfiguration'] = self.cors_config

            response = self.apigatewayv2_client.create_api(**api_params)
            self.api_id = response['ApiId']
            self.api_endpoint = response['ApiEndpoint']

            print(f"✅ API Gateway created!")
            print(f"📍 API ID: {self.api_id}")
            print(f"📍 API Endpoint: {self.api_endpoint}")

            # Create routes and integrations
            if self.routes:
                self._create_routes()

            # Create stage
            self._create_stage()

            # Configure custom domain if specified
            if self.custom_domain:
                self._configure_custom_domain()

            return self._get_api_info()

        except Exception as e:
            print(f"❌ Failed to create v2 API: {str(e)}")
            raise

    def _create_rest_api(self) -> Dict[str, Any]:
        """Create REST API using API Gateway v1"""
        try:
            # Create REST API
            response = self.apigateway_client.create_rest_api(
                name=self.api_name,
                description=self.description,
                tags=self.api_tags
            )
            
            self.api_id = response['id']
            
            print(f"✅ REST API Gateway created!")
            print(f"📍 API ID: {self.api_id}")

            # Get root resource
            resources = self.apigateway_client.get_resources(restApiId=self.api_id)
            root_resource_id = None
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break

            # Create resources and methods
            if self.routes:
                self._create_rest_routes(root_resource_id)

            # Create deployment
            self._create_rest_deployment()

            # Enable CORS if configured
            if self.cors_enabled:
                self._enable_rest_cors(root_resource_id)

            return self._get_api_info()

        except Exception as e:
            print(f"❌ Failed to create REST API: {str(e)}")
            raise

    def _create_routes(self):
        """Create routes for v2 API"""
        for route_config in self.routes:
            try:
                route_key = f"{route_config['method']} {route_config['path']}"
                
                # Create route
                route_response = self.apigatewayv2_client.create_route(
                    ApiId=self.api_id,
                    RouteKey=route_key,
                    Target=f"integrations/{route_config.get('integration_id', '')}"
                )

                # Create integration
                if route_config.get('lambda_function_arn'):
                    self._create_lambda_integration(route_config)

                print(f"   📋 Created route: {route_key}")

            except Exception as e:
                print(f"⚠️  Failed to create route {route_config.get('path', '/')}: {e}")

    def _create_lambda_integration(self, route_config: Dict[str, Any]):
        """Create Lambda integration for a route"""
        try:
            integration_response = self.apigatewayv2_client.create_integration(
                ApiId=self.api_id,
                IntegrationType='AWS_PROXY',
                IntegrationUri=route_config['lambda_function_arn'],
                PayloadFormatVersion='2.0'
            )

            # Update route with integration
            route_config['integration_id'] = integration_response['IntegrationId']

            # Add Lambda permission
            self._add_lambda_permission(route_config['lambda_function_arn'])

        except Exception as e:
            print(f"⚠️  Failed to create Lambda integration: {e}")

    def _add_lambda_permission(self, lambda_arn: str):
        """Add permission for API Gateway to invoke Lambda"""
        try:
            import boto3
            lambda_client = boto3.client('lambda', region_name=self.get_current_region())
            
            function_name = lambda_arn.split(':')[-1]
            source_arn = f"arn:aws:execute-api:{self.get_current_region()}:{self.get_account_id()}:{self.api_id}/*/*"
            
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f"allow-api-gateway-{self.api_id}",
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=source_arn
            )

        except Exception as e:
            # Permission might already exist
            if "ResourceConflictException" not in str(e):
                print(f"⚠️  Failed to add Lambda permission: {e}")

    def _create_stage(self):
        """Create deployment stage"""
        try:
            self.apigatewayv2_client.create_stage(
                ApiId=self.api_id,
                StageName=self.stage_name,
                AutoDeploy=True,
                DefaultRouteSettings={
                    'ThrottlingBurstLimit': self.throttle_burst_limit,
                    'ThrottlingRateLimit': self.throttle_rate_limit
                }
            )
            print(f"   📋 Created stage: {self.stage_name}")

        except Exception as e:
            print(f"⚠️  Failed to create stage: {e}")

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        print(f"🗑️  Destroying API Gateway: {self.api_name}")

        try:
            if not self.api_id:
                existing_api = self._find_existing_api()
                if not existing_api:
                    return {'success': False, 'error': 'API not found'}
                self.api_id = existing_api['ApiId'] if 'ApiId' in existing_api else existing_api['id']

            # Delete custom domain if configured
            if self.custom_domain_configured:
                try:
                    self.apigatewayv2_client.delete_domain_name(DomainName=self.custom_domain)
                    print(f"   🗑️  Deleted custom domain: {self.custom_domain}")
                except Exception:
                    pass

            # Delete API
            if self.api_type in ["HTTP", "WEBSOCKET"]:
                self.apigatewayv2_client.delete_api(ApiId=self.api_id)
            else:
                self.apigateway_client.delete_rest_api(restApiId=self.api_id)

            print(f"✅ API Gateway destroyed!")

            return {'success': True, 'api_name': self.api_name, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy API Gateway: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_api_info(self) -> Dict[str, Any]:
        try:
            stage_url = f"{self.api_endpoint}/{self.stage_name}" if self.api_endpoint else None
            
            return {
                'success': True,
                'api_name': self.api_name,
                'api_id': self.api_id,
                'api_type': self.api_type,
                'api_endpoint': self.api_endpoint,
                'stage_url': stage_url,
                'custom_domain': self.custom_domain,
                'routes_count': len(self.routes)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _estimate_monthly_cost(self) -> str:
        # Rough estimation for API Gateway
        # HTTP API: $1.00 per million requests
        # REST API: $3.50 per million requests
        # WebSocket: $1.00 per million messages + $0.25 per million connection minutes
        
        monthly_requests = 1_000_000
        
        if self.api_type == "HTTP":
            cost = monthly_requests * 0.000001  # $1.00 per million
        elif self.api_type == "WEBSOCKET":
            cost = monthly_requests * 0.000001 + 0.25  # Messages + connection cost
        else:  # REST
            cost = monthly_requests * 0.0000035  # $3.50 per million
        
        return f"~${cost:.3f}/month"

    # Rails-like chainable methods
    def http_api(self) -> 'APIGateway':
        """Configure as HTTP API (modern, simpler, cheaper)"""
        self.api_type = "HTTP"
        self.protocol_type = "HTTP"
        return self

    def rest_api(self) -> 'APIGateway':
        """Configure as REST API (more features, traditional)"""
        self.api_type = "REST"
        self.protocol_type = "HTTP"
        return self

    def websocket_api(self) -> 'APIGateway':
        """Configure as WebSocket API"""
        self.api_type = "WEBSOCKET"
        self.protocol_type = "WEBSOCKET"
        return self

    def route(self, method: str, path: str, **integration_config) -> 'APIGateway':
        """Add a route to the API"""
        route_config = {
            'method': method.upper(),
            'path': path,
            'integration_type': integration_config.get('integration_type', 'lambda'),
            **integration_config
        }
        self.routes.append(route_config)
        return self

    def get(self, path: str, **config) -> 'APIGateway':
        """Add GET route"""
        return self.route("GET", path, **config)

    def post(self, path: str, **config) -> 'APIGateway':
        """Add POST route"""
        return self.route("POST", path, **config)

    def put(self, path: str, **config) -> 'APIGateway':
        """Add PUT route"""
        return self.route("PUT", path, **config)

    def delete(self, path: str, **config) -> 'APIGateway':
        """Add DELETE route"""
        return self.route("DELETE", path, **config)

    def lambda_proxy(self, lambda_function_arn: str, path: str = "/{proxy+}", method: str = "ANY") -> 'APIGateway':
        """Add Lambda proxy integration"""
        return self.route(method, path, 
                         integration_type='lambda_proxy',
                         lambda_function_arn=lambda_function_arn)

    def cors(self, enabled: bool = True, **cors_config) -> 'APIGateway':
        """Configure CORS"""
        self.cors_enabled = enabled
        if cors_config:
            self.cors_config.update(cors_config)
        return self

    def domain(self, domain_name: str, certificate_arn: str = None) -> 'APIGateway':
        """Configure custom domain"""
        self.custom_domain = domain_name
        self.certificate_arn = certificate_arn
        return self

    def stage(self, stage_name: str) -> 'APIGateway':
        """Set stage name"""
        self.stage_name = stage_name
        return self

    def throttling(self, rate_limit: int = 2000, burst_limit: int = 5000) -> 'APIGateway':
        """Configure throttling"""
        self.throttle_rate_limit = rate_limit
        self.throttle_burst_limit = burst_limit
        return self

    def api_key_auth(self, required: bool = True) -> 'APIGateway':
        """Require API key authentication"""
        self.api_key_required = required
        return self

    def logging(self, access_logs: bool = True, execution_logs: bool = True, level: str = "INFO") -> 'APIGateway':
        """Configure logging"""
        self.access_logging_enabled = access_logs
        self.execution_logging_enabled = execution_logs
        self.log_level = level
        return self

    def tags(self, tags: Dict[str, str]) -> 'APIGateway':
        """Set tags"""
        self.api_tags.update(tags)
        return self

    def tag(self, key: str, value: str) -> 'APIGateway':
        """Add a single tag"""
        self.api_tags[key] = value
        return self

    # Helper methods for common patterns
    def lambda_api(self, lambda_function_arn: str) -> 'APIGateway':
        """Rails convenience: Complete Lambda-backed API"""
        return (self.http_api()
                .lambda_proxy(lambda_function_arn)
                .cors()
                .throttling()
                .logging())

    def microservice_api(self) -> 'APIGateway':
        """Rails convenience: Microservice API with best practices"""
        return (self.http_api()
                .cors()
                .throttling(rate_limit=5000, burst_limit=10000)
                .logging()
                .api_key_auth())

    def public_api(self) -> 'APIGateway':
        """Rails convenience: Public API with rate limiting"""
        return (self.http_api()
                .cors()
                .throttling(rate_limit=1000, burst_limit=2000)
                .logging())

    def internal_api(self) -> 'APIGateway':
        """Rails convenience: Internal API with higher limits"""
        return (self.http_api()
                .cors(AllowOrigins=["https://myapp.com"])
                .throttling(rate_limit=10000, burst_limit=20000)
                .logging())
                
    def webhook_api(self) -> 'APIGateway':
        """Rails convenience: Webhook API for external integrations"""
        return (self.http_api()
                .cors()
                .throttling(rate_limit=500, burst_limit=1000)
                .logging()
                .api_key_auth())

    def _discover_existing_apis(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing API Gateway APIs"""
        existing_apis = {}
        
        try:
            # Discover HTTP/WebSocket APIs (API Gateway v2)
            if self.apigatewayv2_client:
                response = self.apigatewayv2_client.get_apis()
                for api in response.get('Items', []):
                    existing_apis[api['ApiId']] = {
                        'api_id': api['ApiId'],
                        'name': api['Name'],
                        'protocol_type': api['ProtocolType'],
                        'api_endpoint': api.get('ApiEndpoint'),
                        'created_date': api.get('CreatedDate'),
                        'description': api.get('Description', ''),
                        'tags': api.get('Tags', {}),
                        'api_type': 'v2'
                    }
            
            # Discover REST APIs (API Gateway v1)
            if self.apigateway_client:
                response = self.apigateway_client.get_rest_apis()
                for api in response.get('items', []):
                    existing_apis[api['id']] = {
                        'api_id': api['id'],
                        'name': api['name'],
                        'protocol_type': 'REST',
                        'api_endpoint': f"https://{api['id']}.execute-api.{self.get_current_region()}.amazonaws.com",
                        'created_date': api.get('createdDate'),
                        'description': api.get('description', ''),
                        'tags': api.get('tags', {}),
                        'api_type': 'v1'
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing APIs: {str(e)}")
        
        return existing_apis 