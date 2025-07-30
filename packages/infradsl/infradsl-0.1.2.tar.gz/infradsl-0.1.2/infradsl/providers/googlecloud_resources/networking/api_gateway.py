"""
Google Cloud API Gateway Resource

Rails-like API Gateway management with OpenAPI spec configuration and Cloud Functions integration.
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class APIGateway(BaseGcpResource):
    """Google Cloud API Gateway Resource with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        
        # Core configuration
        self.api_id = name
        self.gateway_id = f"{name}-gateway"
        self.config_id = f"{name}-config"
        self.display_name = name
        self.description = f"API Gateway for {name}"
        
        # OpenAPI specification
        self.openapi_spec = {
            "swagger": "2.0",
            "info": {
                "title": name,
                "description": self.description,
                "version": "1.0.0"
            },
            "produces": ["application/json"],
            "schemes": ["https"],
            "paths": {},
            "x-google-backend": {}
        }
        
        # Routes and backends
        self.routes = []
        self.cloud_function_backends = {}
        self.cloud_run_backends = {}
        self.external_backends = {}
        
        # Authentication and security
        self.auth_enabled = False
        self.api_key_required = False
        self.cors_enabled = True
        
        # Labels and configuration
        self.gateway_labels = {}
        self.managed_service = True
        
        # State
        self.api_resource_name = None
        self.gateway_resource_name = None
        self.config_resource_name = None
        self.gateway_url = None
        self.managed_service_name = None

        # Client
        self.api_gateway_client = None

    def _initialize_managers(self):
        self.api_gateway_client = None

    def _post_authentication_setup(self):
        self.api_gateway_client = self.get_api_gateway_client()
        
        # Set resource names
        project_id = self.gcp_client.project
        self.api_resource_name = f"projects/{project_id}/locations/global/apis/{self.api_id}"
        self.gateway_resource_name = f"projects/{project_id}/locations/global/gateways/{self.gateway_id}"
        self.config_resource_name = f"projects/{project_id}/locations/global/gateways/{self.gateway_id}/configs/{self.config_id}"

    def _discover_existing_gateways(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing API Gateway resources"""
        existing_gateways = {}
        
        try:
            from google.cloud import apigateway_v1
            from google.api_core.exceptions import GoogleAPIError
            
            parent = f"projects/{self.gcp_client.project}/locations/global"
            
            # List all gateways in the project
            gateways = self.api_gateway_client.list_gateways(parent=parent)
            
            for gateway in gateways:
                gateway_name = gateway.name.split('/')[-1]
                
                try:
                    # Get gateway details
                    gateway_details = self.api_gateway_client.get_gateway(name=gateway.name)
                    
                    # Extract gateway information
                    display_name = gateway_details.display_name
                    state = gateway_details.state.name if hasattr(gateway_details, 'state') else 'UNKNOWN'
                    labels = dict(gateway_details.labels) if gateway_details.labels else {}
                    
                    # Get the default hostname (gateway URL)
                    default_hostname = gateway_details.default_hostname if hasattr(gateway_details, 'default_hostname') else 'unknown'
                    gateway_url = f"https://{default_hostname}" if default_hostname != 'unknown' else 'pending'
                    
                    # Get API Config information
                    api_config = None
                    api_config_name = None
                    routes = []
                    backend_count = 0
                    
                    if hasattr(gateway_details, 'api_config') and gateway_details.api_config:
                        api_config_name = gateway_details.api_config
                        
                        try:
                            # Get API config details
                            api_config_details = self.api_gateway_client.get_api_config(name=gateway_details.api_config)
                            
                            # Parse OpenAPI spec if available
                            if hasattr(api_config_details, 'openapi_documents'):
                                for doc in api_config_details.openapi_documents:
                                    if hasattr(doc, 'document') and hasattr(doc.document, 'contents'):
                                        try:
                                            spec_content = doc.document.contents.decode('utf-8')
                                            if spec_content.strip().startswith('{'):
                                                spec = json.loads(spec_content)
                                            else:
                                                spec = yaml.safe_load(spec_content)
                                            
                                            # Extract paths and backends
                                            if 'paths' in spec:
                                                for path, methods in spec['paths'].items():
                                                    for method, operation in methods.items():
                                                        if isinstance(operation, dict):
                                                            routes.append({
                                                                'method': method.upper(),
                                                                'path': path,
                                                                'operation_id': operation.get('operationId', 'unknown')
                                                            })
                                            
                                            # Count backends
                                            if 'x-google-backend' in spec:
                                                backend_count = len(spec['x-google-backend'])
                                            
                                        except Exception as e:
                                            print(f"⚠️  Failed to parse OpenAPI spec for gateway {gateway_name}: {str(e)}")
                                            
                        except Exception as e:
                            print(f"⚠️  Failed to get API config for gateway {gateway_name}: {str(e)}")
                    
                    # Get associated API information
                    api_name = None
                    managed_service = False
                    
                    try:
                        # List APIs to find the associated one
                        apis = self.api_gateway_client.list_apis(parent=parent)
                        for api in apis:
                            # Check if this API is associated with the gateway
                            api_details = self.api_gateway_client.get_api(name=api.name)
                            if hasattr(api_details, 'managed_service') and api_details.managed_service:
                                # This is likely the API for our gateway
                                api_name = api.name.split('/')[-1]
                                managed_service = True
                                break
                    except Exception as e:
                        print(f"⚠️  Failed to get API info for gateway {gateway_name}: {str(e)}")
                    
                    existing_gateways[gateway_name] = {
                        'gateway_name': gateway_name,
                        'full_name': gateway.name,
                        'display_name': display_name,
                        'state': state,
                        'gateway_url': gateway_url,
                        'default_hostname': default_hostname,
                        'labels': labels,
                        'label_count': len(labels),
                        'api_config_name': api_config_name,
                        'api_name': api_name,
                        'managed_service': managed_service,
                        'routes': routes,
                        'route_count': len(routes),
                        'backend_count': backend_count,
                        'methods': list(set(route['method'] for route in routes)),
                        'paths': list(set(route['path'] for route in routes)),
                        'create_time': gateway_details.create_time.isoformat() if hasattr(gateway_details, 'create_time') else None,
                        'update_time': gateway_details.update_time.isoformat() if hasattr(gateway_details, 'update_time') else None
                    }
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for gateway {gateway_name}: {str(e)}")
                    existing_gateways[gateway_name] = {
                        'gateway_name': gateway_name,
                        'error': str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing API Gateways: {str(e)}")
        
        return existing_gateways

    def get_api_gateway_client(self):
        try:
            from google.cloud import apigateway_v1
            return apigateway_v1.ApiGatewayServiceClient(credentials=self.gcp_client.credentials)
        except Exception as e:
            print(f"⚠️  Failed to create API Gateway client: {e}")
            return None

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing gateways
        existing_gateways = self._discover_existing_gateways()
        
        # Categorize gateways
        gateways_to_create = []
        gateways_to_keep = []
        gateways_to_remove = []
        
        # Check if our desired gateway exists
        desired_gateway_name = self.gateway_id
        gateway_exists = desired_gateway_name in existing_gateways
        
        if not gateway_exists:
            gateways_to_create.append({
                'gateway_name': desired_gateway_name,
                'api_id': self.api_id,
                'display_name': self.display_name,
                'routes': self.routes,
                'route_count': len(self.routes),
                'cloud_function_backends': self.cloud_function_backends,
                'cloud_run_backends': self.cloud_run_backends,
                'external_backends': self.external_backends,
                'backend_count': len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends),
                'auth_enabled': self.auth_enabled,
                'cors_enabled': self.cors_enabled,
                'api_key_required': self.api_key_required,
                'labels': self.gateway_labels,
                'label_count': len(self.gateway_labels),
                'methods': list(set(route.get('method', 'GET') for route in self.routes)),
                'paths': list(set(route.get('path', '/') for route in self.routes))
            })
        else:
            gateways_to_keep.append(existing_gateways[desired_gateway_name])

        print(f"\n🌐 Google Cloud API Gateway Preview")
        
        # Show gateways to create
        if gateways_to_create:
            print(f"╭─ 🌐 API Gateways to CREATE: {len(gateways_to_create)}")
            for gateway in gateways_to_create:
                print(f"├─ 🆕 {gateway['gateway_name']}")
                print(f"│  ├─ 📋 API ID: {gateway['api_id']}")
                print(f"│  ├─ 🎯 Display Name: {gateway['display_name']}")
                
                # Show route summary
                if gateway['route_count'] > 0:
                    print(f"│  ├─ 🛣️  Routes: {gateway['route_count']}")
                    print(f"│  │  ├─ 🔍 Methods: {', '.join(gateway['methods'])}")
                    print(f"│  │  └─ 📍 Paths: {len(gateway['paths'])} unique")
                    
                    # Show individual routes
                    print(f"│  ├─ 🛣️  Route Details:")
                    for i, route in enumerate(gateway['routes'][:5]):  # Show first 5 routes
                        method = route.get('method', 'GET')
                        path = route.get('path', '/')
                        backend = route.get('backend_type', 'function')
                        backend_name = route.get('backend_name', 'unknown')
                        connector = "│  │  ├─" if i < min(len(gateway['routes']), 5) - 1 else "│  │  └─"
                        print(f"{connector} {method} {path} → {backend}:{backend_name}")
                    
                    if len(gateway['routes']) > 5:
                        print(f"│  │     └─ ... and {len(gateway['routes']) - 5} more routes")
                else:
                    print(f"│  ├─ 🛣️  Routes: None configured")
                
                # Show backend summary
                if gateway['backend_count'] > 0:
                    print(f"│  ├─ ⚙️  Backends: {gateway['backend_count']} total")
                    if len(gateway['cloud_function_backends']) > 0:
                        print(f"│  │  ├─ ⚡ Cloud Functions: {len(gateway['cloud_function_backends'])}")
                    if len(gateway['cloud_run_backends']) > 0:
                        print(f"│  │  ├─ 🏃 Cloud Run: {len(gateway['cloud_run_backends'])}")
                    if len(gateway['external_backends']) > 0:
                        print(f"│  │  └─ 🌐 External: {len(gateway['external_backends'])}")
                else:
                    print(f"│  ├─ ⚙️  Backends: None configured")
                
                # Show security configuration
                print(f"│  ├─ 🔒 Security:")
                print(f"│  │  ├─ 🔐 Authentication: {'✅ Enabled' if gateway['auth_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🔑 API Key Required: {'✅ Yes' if gateway['api_key_required'] else '❌ No'}")
                print(f"│  │  └─ 🌍 CORS: {'✅ Enabled' if gateway['cors_enabled'] else '❌ Disabled'}")
                
                if gateway['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {gateway['label_count']}")
                
                # Show API Gateway features
                print(f"│  ├─ 🚀 Features:")
                print(f"│  │  ├─ 📊 Request/Response transformation")
                print(f"│  │  ├─ 🔄 Load balancing & auto-scaling")
                print(f"│  │  ├─ 📈 Monitoring & logging")
                print(f"│  │  └─ 🛡️  Rate limiting & security")
                
                print(f"│  └─ 🌐 Endpoint: https://{gateway['gateway_name']}-<hash>.execute-api.gcp.dev")
            print(f"╰─")

        # Show existing gateways being kept
        if gateways_to_keep:
            print(f"\n╭─ 🌐 Existing API Gateways to KEEP: {len(gateways_to_keep)}")
            for gateway in gateways_to_keep:
                state_icon = "🟢" if gateway['state'] == 'ACTIVE' else "🟡" if gateway['state'] == 'CREATING' else "🔴"
                print(f"├─ {state_icon} {gateway['gateway_name']}")
                print(f"│  ├─ 🎯 Display Name: {gateway['display_name']}")
                print(f"│  ├─ 📊 State: {gateway['state']}")
                
                if gateway['gateway_url'] != 'pending':
                    print(f"│  ├─ 🌐 Gateway URL: {gateway['gateway_url']}")
                else:
                    print(f"│  ├─ 🌐 Gateway URL: Pending deployment")
                
                # Show route information
                if gateway['route_count'] > 0:
                    print(f"│  ├─ 🛣️  Routes: {gateway['route_count']}")
                    if gateway['methods']:
                        print(f"│  │  ├─ 🔍 Methods: {', '.join(gateway['methods'])}")
                    if gateway['paths']:
                        print(f"│  │  └─ 📍 Paths: {len(gateway['paths'])} unique")
                    
                    # Show route details
                    if len(gateway['routes']) > 0:
                        print(f"│  ├─ 🛣️  Active Routes:")
                        for i, route in enumerate(gateway['routes'][:3]):  # Show first 3
                            connector = "│  │  ├─" if i < min(len(gateway['routes']), 3) - 1 else "│  │  └─"
                            print(f"{connector} {route['method']} {route['path']}")
                        
                        if len(gateway['routes']) > 3:
                            print(f"│  │     └─ ... and {len(gateway['routes']) - 3} more routes")
                else:
                    print(f"│  ├─ 🛣️  Routes: None")
                
                if gateway['backend_count'] > 0:
                    print(f"│  ├─ ⚙️  Backends: {gateway['backend_count']}")
                
                if gateway['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {gateway['label_count']}")
                
                if gateway['api_name']:
                    print(f"│  ├─ 📋 Associated API: {gateway['api_name']}")
                
                print(f"│  └─ 📅 Created: {gateway.get('create_time', 'Unknown')[:10] if gateway.get('create_time') else 'Unknown'}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 API Gateway Costs:")
        if gateways_to_create:
            gateway = gateways_to_create[0]
            
            # API Gateway costs: $3.00 per million API calls
            print(f"   ├─ 🌐 API calls: $3.00/million requests")
            print(f"   ├─ 📡 Data transfer: $0.09/GB (first 1GB free)")
            print(f"   ├─ 🔒 Authentication: Included")
            print(f"   ├─ 📊 Monitoring: Included in Cloud Logging")
            
            if gateway['route_count'] > 0:
                print(f"   ├─ 🛣️  Routes ({gateway['route_count']}): Free")
            
            if gateway['backend_count'] > 0:
                print(f"   ├─ ⚙️  Backend integrations: Included")
            
            print(f"   └─ 📊 Typical cost: $0.30-$3.00/month (100K requests)")
        else:
            print(f"   ├─ 🌐 API calls: $3.00/million requests")
            print(f"   ├─ 📡 Data transfer: $0.09/GB")
            print(f"   ├─ 🛣️  Routes: Free")
            print(f"   └─ ⚙️  Backend integrations: Included")

        return {
            'resource_type': 'gcp_api_gateway',
            'name': desired_gateway_name,
            'gateways_to_create': gateways_to_create,
            'gateways_to_keep': gateways_to_keep,
            'gateways_to_remove': gateways_to_remove,
            'existing_gateways': existing_gateways,
            'gateway_id': desired_gateway_name,
            'api_id': self.api_id,
            'route_count': len(self.routes),
            'backend_count': len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends),
            'estimated_cost': "$0.30-$3.00/month"
        }

    def create(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        
        existing_gateway = self._find_existing_gateway()
        if existing_gateway:
            print(f"🔄 API Gateway '{self.gateway_id}' already exists")
            self.gateway_url = self._extract_gateway_url(existing_gateway)
            return self._get_gateway_info()
        
        print(f"🚀 Creating API Gateway: {self.gateway_id}")
        return self._create_new_gateway()

    def _find_existing_gateway(self) -> Optional[Dict[str, Any]]:
        try:
            gateway = self.api_gateway_client.get_gateway(name=self.gateway_resource_name)
            return gateway
        except Exception:
            return None

    def _create_new_gateway(self) -> Dict[str, Any]:
        try:
            # Step 1: Create API
            self._create_api()
            
            # Step 2: Generate OpenAPI spec from routes
            self._build_openapi_spec()
            
            # Step 3: Create API Config  
            self._create_api_config()
            
            # Step 4: Create Gateway
            self._create_gateway()
            
            # Step 5: Wait for deployment
            self._wait_for_deployment()

            return self._get_gateway_info()

        except Exception as e:
            print(f"❌ Failed to create API Gateway: {str(e)}")
            raise

    def _create_api(self):
        """Create the API resource"""
        try:
            from google.cloud import apigateway_v1
            
            api = apigateway_v1.Api(
                name=self.api_resource_name,
                display_name=self.display_name,
                managed_service=self.managed_service,
                labels=self.gateway_labels
            )

            operation = self.api_gateway_client.create_api(
                parent=f"projects/{self.gcp_client.project}/locations/global",
                api_id=self.api_id,
                api=api
            )

            print(f"   📋 Created API: {self.api_id}")

        except Exception as e:
            print(f"⚠️  Failed to create API: {e}")
            raise

    def _build_openapi_spec(self):
        """Build OpenAPI specification from configured routes"""
        try:
            # Add paths from routes
            for route in self.routes:
                method = route['method'].lower()
                path = route['path']
                backend_type = route['backend_type']
                backend_name = route['backend_name']
                
                # Initialize path if not exists
                if path not in self.openapi_spec['paths']:
                    self.openapi_spec['paths'][path] = {}
                
                # Create operation
                operation = {
                    "operationId": f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "schema": {"type": "string"}
                        }
                    }
                }

                # Add backend configuration
                if backend_type == "cloud_function":
                    backend_config = self.cloud_function_backends[backend_name]
                    operation["x-google-backend"] = {
                        "address": f"https://us-central1-{self.gcp_client.project}.cloudfunctions.net/{backend_name}"
                    }
                elif backend_type == "cloud_run":
                    backend_config = self.cloud_run_backends[backend_name]
                    operation["x-google-backend"] = {
                        "address": backend_config['url']
                    }

                self.openapi_spec['paths'][path][method] = operation

            # Add CORS if enabled
            if self.cors_enabled:
                for path in self.openapi_spec['paths']:
                    if 'options' not in self.openapi_spec['paths'][path]:
                        self.openapi_spec['paths'][path]['options'] = {
                            "operationId": f"cors_{path.replace('/', '_')}",
                            "responses": {
                                "200": {
                                    "description": "CORS response",
                                    "headers": {
                                        "Access-Control-Allow-Origin": {"type": "string"},
                                        "Access-Control-Allow-Methods": {"type": "string"},
                                        "Access-Control-Allow-Headers": {"type": "string"}
                                    }
                                }
                            }
                        }

        except Exception as e:
            print(f"⚠️  Failed to build OpenAPI spec: {e}")
            raise

    def _create_api_config(self):
        """Create API config with OpenAPI specification"""
        try:
            from google.cloud import apigateway_v1
            
            # Convert OpenAPI spec to YAML
            openapi_yaml = yaml.dump(self.openapi_spec, default_flow_style=False)
            
            api_config = apigateway_v1.ApiConfig(
                name=self.config_resource_name,
                display_name=f"{self.display_name} Config",
                openapi_documents=[
                    apigateway_v1.ApiConfig.OpenApiDocument(
                        document=apigateway_v1.ApiConfig.File(
                            contents=openapi_yaml.encode('utf-8')
                        )
                    )
                ],
                labels=self.gateway_labels
            )

            operation = self.api_gateway_client.create_api_config(
                parent=self.api_resource_name,
                api_config_id=self.config_id,
                api_config=api_config
            )

            print(f"   📋 Created API Config: {self.config_id}")

        except Exception as e:
            print(f"⚠️  Failed to create API config: {e}")
            raise

    def _create_gateway(self):
        """Create the API Gateway"""
        try:
            from google.cloud import apigateway_v1
            
            gateway = apigateway_v1.Gateway(
                name=self.gateway_resource_name,
                display_name=self.display_name,
                api_config=self.config_resource_name,
                labels=self.gateway_labels
            )

            operation = self.api_gateway_client.create_gateway(
                parent=f"projects/{self.gcp_client.project}/locations/global",
                gateway_id=self.gateway_id,
                gateway=gateway
            )

            print(f"   📋 Created Gateway: {self.gateway_id}")

        except Exception as e:
            print(f"⚠️  Failed to create gateway: {e}")
            raise

    def _wait_for_deployment(self):
        """Wait for gateway deployment to complete"""
        try:
            import time
            max_wait = 300  # 5 minutes
            wait_time = 0
            
            print("   ⏳ Waiting for gateway deployment...")
            
            while wait_time < max_wait:
                try:
                    gateway = self.api_gateway_client.get_gateway(name=self.gateway_resource_name)
                    if hasattr(gateway, 'default_hostname') and gateway.default_hostname:
                        self.gateway_url = f"https://{gateway.default_hostname}"
                        print(f"✅ Gateway deployed!")
                        print(f"📍 Gateway URL: {self.gateway_url}")
                        return
                except Exception:
                    pass
                
                time.sleep(10)
                wait_time += 10
            
            print("⚠️  Gateway deployment taking longer than expected")

        except Exception as e:
            print(f"⚠️  Failed to wait for deployment: {e}")

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        print(f"🗑️  Destroying API Gateway: {self.gateway_id}")

        try:
            # Delete gateway
            try:
                self.api_gateway_client.delete_gateway(name=self.gateway_resource_name)
                print(f"   🗑️  Deleted gateway: {self.gateway_id}")
            except Exception as e:
                print(f"⚠️  Failed to delete gateway: {e}")

            # Delete API config
            try:
                self.api_gateway_client.delete_api_config(name=self.config_resource_name)
                print(f"   🗑️  Deleted API config: {self.config_id}")
            except Exception as e:
                print(f"⚠️  Failed to delete API config: {e}")

            # Delete API
            try:
                self.api_gateway_client.delete_api(name=self.api_resource_name)
                print(f"   🗑️  Deleted API: {self.api_id}")
            except Exception as e:
                print(f"⚠️  Failed to delete API: {e}")

            print(f"✅ API Gateway destroyed!")

            return {'success': True, 'gateway_id': self.gateway_id, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy API Gateway: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_gateway_info(self) -> Dict[str, Any]:
        try:
            return {
                'success': True,
                'api_id': self.api_id,
                'gateway_id': self.gateway_id,
                'gateway_url': self.gateway_url,
                'routes_count': len(self.routes),
                'backends_count': len(self.cloud_function_backends) + len(self.cloud_run_backends)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _extract_gateway_url(self, gateway) -> Optional[str]:
        """Extract gateway URL from gateway resource"""
        try:
            if hasattr(gateway, 'default_hostname') and gateway.default_hostname:
                return f"https://{gateway.default_hostname}"
        except Exception:
            pass
        return None

    def _estimate_monthly_cost(self) -> str:
        # Rough estimation for API Gateway
        # $3.00 per million API calls
        monthly_requests = 1_000_000
        cost = monthly_requests * 0.000003
        return f"~${cost:.3f}/month"

    # Rails-like chainable methods
    def route(self, method: str, path: str, backend_type: str, backend_name: str, **config) -> 'APIGateway':
        """Add a route to the API"""
        route_config = {
            'method': method.upper(),
            'path': path,
            'backend_type': backend_type,
            'backend_name': backend_name,
            **config
        }
        self.routes.append(route_config)
        return self

    def get(self, path: str, backend_type: str, backend_name: str, **config) -> 'APIGateway':
        """Add GET route"""
        return self.route("GET", path, backend_type, backend_name, **config)

    def post(self, path: str, backend_type: str, backend_name: str, **config) -> 'APIGateway':
        """Add POST route"""
        return self.route("POST", path, backend_type, backend_name, **config)

    def put(self, path: str, backend_type: str, backend_name: str, **config) -> 'APIGateway':
        """Add PUT route"""
        return self.route("PUT", path, backend_type, backend_name, **config)

    def delete_route(self, path: str, backend_type: str, backend_name: str, **config) -> 'APIGateway':
        """Add DELETE route"""
        return self.route("DELETE", path, backend_type, backend_name, **config)

    def cloud_function_backend(self, function_name: str, project_id: str = None, region: str = "us-central1") -> 'APIGateway':
        """Add Cloud Function backend"""
        project = project_id or self.gcp_client.project
        self.cloud_function_backends[function_name] = {
            'function_name': function_name,
            'project_id': project,
            'region': region,
            'url': f"https://{region}-{project}.cloudfunctions.net/{function_name}"
        }
        return self

    def cloud_run_backend(self, service_name: str, url: str, region: str = "us-central1") -> 'APIGateway':
        """Add Cloud Run backend"""
        self.cloud_run_backends[service_name] = {
            'service_name': service_name,
            'url': url,
            'region': region
        }
        return self

    def cors(self, enabled: bool = True) -> 'APIGateway':
        """Enable/disable CORS"""
        self.cors_enabled = enabled
        return self

    def auth(self, enabled: bool = True) -> 'APIGateway':
        """Enable/disable authentication"""
        self.auth_enabled = enabled
        return self

    def api_key(self, required: bool = True) -> 'APIGateway':
        """Require API key"""
        self.api_key_required = required
        return self

    def labels(self, labels: Dict[str, str]) -> 'APIGateway':
        """Set labels"""
        self.gateway_labels.update(labels)
        return self

    def label(self, key: str, value: str) -> 'APIGateway':
        """Add single label"""
        self.gateway_labels[key] = value
        return self

    # Rails convenience methods
    def function_api(self, function_name: str, paths: List[str] = None) -> 'APIGateway':
        """Rails convenience: API backed by single Cloud Function"""
        self.cloud_function_backend(function_name)
        
        # Add default routes if none specified
        if not paths:
            paths = ["/", "/{proxy+}"]
        
        for path in paths:
            self.get(path, "cloud_function", function_name)
            self.post(path, "cloud_function", function_name)
            self.put(path, "cloud_function", function_name)
            self.delete_route(path, "cloud_function", function_name)
        
        return self.cors()

    def microservice_api(self) -> 'APIGateway':
        """Rails convenience: Microservice API with auth"""
        return self.cors().auth().api_key()

    def public_api(self) -> 'APIGateway':
        """Rails convenience: Public API without auth"""
        return self.cors()

    def internal_api(self) -> 'APIGateway':
        """Rails convenience: Internal API with auth"""
        return self.auth().api_key()

    def rest_api(self, function_name: str) -> 'APIGateway':
        """Rails convenience: Complete REST API"""
        return (self.cloud_function_backend(function_name)
                .get("/api/{resource}", "cloud_function", function_name)
                .post("/api/{resource}", "cloud_function", function_name)
                .put("/api/{resource}/{id}", "cloud_function", function_name)
                .delete_route("/api/{resource}/{id}", "cloud_function", function_name)
                .cors()) 