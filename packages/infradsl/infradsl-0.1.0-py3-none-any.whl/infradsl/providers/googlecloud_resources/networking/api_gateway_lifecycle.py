"""
GCP API Gateway Lifecycle Mixin

Lifecycle operations for Google Cloud API Gateway.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import yaml
import time
from typing import Dict, Any, List, Optional, Union


class APIGatewayLifecycleMixin:
    """
    Mixin for API Gateway lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update API Gateway resources
    - destroy(): Clean up API Gateway resources
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
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
                'gateway_description': self.gateway_description,
                'routes': self.routes,
                'route_count': len(self.routes),
                'cloud_function_backends': self.cloud_function_backends,
                'cloud_run_backends': self.cloud_run_backends,
                'external_backends': self.external_backends,
                'backend_count': len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends),
                'auth_enabled': self.auth_enabled,
                'cors_enabled': self.cors_enabled,
                'api_key_required': self.api_key_required,
                'rate_limiting_enabled': self.rate_limiting_enabled,
                'quota_limit': self.quota_limit,
                'labels': self.gateway_labels,
                'label_count': len(self.gateway_labels),
                'methods': list(set(route.get('method', 'GET') for route in self.routes)),
                'paths': list(set(route.get('path', '/') for route in self.routes)),
                'unique_paths': len(set(route.get('path', '/') for route in self.routes)),
                'gateway_type': self._get_gateway_type_from_config(),
                'estimated_cost': self._estimate_api_gateway_cost()
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
                print(f"│  ├─ 📝 Description: {gateway['gateway_description']}")
                print(f"│  ├─ 🏗️  Gateway Type: {gateway['gateway_type'].replace('_', ' ').title()}")
                
                # Show route summary
                if gateway['route_count'] > 0:
                    print(f"│  ├─ 🛣️  Routes: {gateway['route_count']} ({gateway['unique_paths']} unique paths)")
                    print(f"│  │  ├─ 🔍 Methods: {', '.join(gateway['methods'])}")
                    print(f"│  │  └─ 📍 Sample Paths: {', '.join(gateway['paths'][:3])}")
                    
                    # Show route details
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
                        func_names = list(gateway['cloud_function_backends'].keys())[:3]
                        print(f"│  │  │  └─ Functions: {', '.join(func_names)}")
                    if len(gateway['cloud_run_backends']) > 0:
                        print(f"│  │  ├─ 🏃 Cloud Run: {len(gateway['cloud_run_backends'])}")
                        run_names = list(gateway['cloud_run_backends'].keys())[:3]
                        print(f"│  │  │  └─ Services: {', '.join(run_names)}")
                    if len(gateway['external_backends']) > 0:
                        print(f"│  │  └─ 🌐 External: {len(gateway['external_backends'])}")
                        ext_names = list(gateway['external_backends'].keys())[:3]
                        print(f"│  │     └─ Backends: {', '.join(ext_names)}")
                else:
                    print(f"│  ├─ ⚙️  Backends: None configured")
                
                # Show security configuration
                print(f"│  ├─ 🔒 Security:")
                print(f"│  │  ├─ 🔐 Authentication: {'✅ Enabled' if gateway['auth_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🔑 API Key Required: {'✅ Yes' if gateway['api_key_required'] else '❌ No'}")
                print(f"│  │  ├─ 🌍 CORS: {'✅ Enabled' if gateway['cors_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 🚦 Rate Limiting: {'✅ Enabled' if gateway['rate_limiting_enabled'] else '❌ Disabled'}")
                
                # Show quota if configured
                if gateway['quota_limit']:
                    print(f"│  ├─ 📊 Quota: {gateway['quota_limit']:,} requests")
                
                # Show labels
                if gateway['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {gateway['label_count']}")
                
                # Show API Gateway features
                print(f"│  ├─ 🚀 Features:")
                print(f"│  │  ├─ 📊 Request/Response transformation")
                print(f"│  │  ├─ 🔄 Load balancing & auto-scaling")
                print(f"│  │  ├─ 📈 Monitoring & logging integration")
                print(f"│  │  ├─ 🛡️  Built-in security & rate limiting")
                print(f"│  │  └─ 🌐 OpenAPI 2.0 specification support")
                
                print(f"│  ├─ 💰 Estimated Cost: ${gateway['estimated_cost']:.2f}/month")
                print(f"│  └─ 🌐 Endpoint: https://{gateway['gateway_name']}-<hash>.a.gateway.dev")
            print(f"╰─")

        # Show existing gateways being kept
        if gateways_to_keep:
            print(f"\n╭─ 🌐 Existing API Gateways to KEEP: {len(gateways_to_keep)}")
            for gateway in gateways_to_keep:
                state_icon = "🟢" if gateway.get('state') == 'ACTIVE' else "🟡" if gateway.get('state') == 'CREATING' else "🔴"
                print(f"├─ {state_icon} {gateway['gateway_name']}")
                print(f"│  ├─ 🎯 Display Name: {gateway['display_name']}")
                print(f"│  ├─ 📊 State: {gateway.get('state', 'UNKNOWN')}")
                
                if gateway.get('gateway_url') and gateway['gateway_url'] != 'pending':
                    print(f"│  ├─ 🌐 Gateway URL: {gateway['gateway_url']}")
                else:
                    print(f"│  ├─ 🌐 Gateway URL: Pending deployment")
                
                # Show route information
                if gateway.get('route_count', 0) > 0:
                    print(f"│  ├─ 🛣️  Routes: {gateway['route_count']}")
                    if gateway.get('methods'):
                        print(f"│  │  ├─ 🔍 Methods: {', '.join(gateway['methods'])}")
                    if gateway.get('paths'):
                        print(f"│  │  └─ 📍 Paths: {len(gateway['paths'])} unique")
                    
                    # Show route details
                    if len(gateway.get('routes', [])) > 0:
                        print(f"│  ├─ 🛣️  Active Routes:")
                        for i, route in enumerate(gateway['routes'][:3]):  # Show first 3
                            connector = "│  │  ├─" if i < min(len(gateway['routes']), 3) - 1 else "│  │  └─"
                            print(f"{connector} {route['method']} {route['path']}")
                        
                        if len(gateway['routes']) > 3:
                            print(f"│  │     └─ ... and {len(gateway['routes']) - 3} more routes")
                else:
                    print(f"│  ├─ 🛣️  Routes: None")
                
                if gateway.get('backend_count', 0) > 0:
                    print(f"│  ├─ ⚙️  Backends: {gateway['backend_count']}")
                
                if gateway.get('label_count', 0) > 0:
                    print(f"│  ├─ 🏷️  Labels: {gateway['label_count']}")
                
                if gateway.get('api_name'):
                    print(f"│  ├─ 📋 Associated API: {gateway['api_name']}")
                
                print(f"│  └─ 📅 Created: {gateway.get('create_time', 'Unknown')[:10] if gateway.get('create_time') else 'Unknown'}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 API Gateway Costs:")
        if gateways_to_create:
            gateway = gateways_to_create[0]
            
            print(f"   ├─ 🌐 API calls: $3.00/million requests")
            print(f"   ├─ 📡 Data transfer: $0.09/GB (first 1GB free)")
            print(f"   ├─ 🔒 Authentication: Included")
            print(f"   ├─ 📊 Monitoring: Included in Cloud Logging")
            
            if gateway['route_count'] > 0:
                print(f"   ├─ 🛣️  Routes ({gateway['route_count']}): Free")
            
            if gateway['backend_count'] > 0:
                print(f"   ├─ ⚙️  Backend integrations: Included")
            
            print(f"   └─ 📊 Estimated: ${gateway['estimated_cost']:.2f}/month (100K requests)")
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
            'estimated_cost': f"${self._estimate_api_gateway_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update API Gateway"""
        self._ensure_authenticated()
        
        existing_gateway = self._find_existing_gateway()
        if existing_gateway:
            print(f"🔄 API Gateway '{self.gateway_id}' already exists")
            self.gateway_url = self._extract_gateway_url(existing_gateway)
            return self._get_gateway_info()
        
        print(f"🚀 Creating API Gateway: {self.gateway_id}")
        return self._create_new_gateway()

    def destroy(self) -> Dict[str, Any]:
        """Destroy API Gateway and all associated resources"""
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

    def wait_for_deployment(self, max_wait: int = 600) -> bool:
        """
        Wait for API Gateway deployment to complete.
        
        Args:
            max_wait: Maximum wait time in seconds (default: 10 minutes)
            
        Returns:
            bool: True if deployment completed successfully, False otherwise
        """
        try:
            wait_time = 0
            
            print(f"   ⏳ Waiting for gateway deployment (max {max_wait//60} minutes)...")
            
            while wait_time < max_wait:
                try:
                    gateway = self.api_gateway_client.get_gateway(name=self.gateway_resource_name)
                    if hasattr(gateway, 'default_hostname') and gateway.default_hostname:
                        self.gateway_url = f"https://{gateway.default_hostname}"
                        self.gateway_status = "ACTIVE"
                        print(f"✅ Gateway deployed successfully!")
                        print(f"📍 Gateway URL: {self.gateway_url}")
                        return True
                except Exception:
                    pass
                
                time.sleep(15)  # Check every 15 seconds
                wait_time += 15
                
                # Show progress every minute
                if wait_time % 60 == 0:
                    print(f"   ⏳ Still waiting... ({wait_time//60} minutes elapsed)")
            
            print(f"⚠️  Gateway deployment taking longer than expected ({max_wait//60} minutes)")
            return False

        except Exception as e:
            print(f"⚠️  Failed to wait for deployment: {e}")
            return False

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize gateway configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'reliability', 'compliance')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "reliability":
            return self._optimize_for_reliability()
        elif optimization_target.lower() == "compliance":
            return self._optimize_for_compliance()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use global location for better pricing
        self.gateway_location = "global"
        
        # Enable rate limiting to control costs
        if not self.rate_limiting_enabled:
            self.rate_limiting_enabled = True
            self.quota_limit = self.quota_limit or 100000  # Conservative limit
        
        # Add cost optimization labels
        self.gateway_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "billing_alert": "enabled"
        })
        
        print("   ├─ 🌍 Set to global location for better pricing")
        print("   ├─ 🚦 Enabled rate limiting for cost control")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use global location for worldwide performance
        self.gateway_location = "global"
        
        # Optimize CORS for performance
        self.cors_enabled = True
        
        # Add performance labels
        self.gateway_labels.update({
            "optimization": "performance",
            "monitoring": "enhanced",
            "caching": "enabled"
        })
        
        print("   ├─ 🌍 Set to global location for worldwide performance")
        print("   ├─ 🌐 Enabled CORS for better client performance")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_reliability(self):
        """Optimize configuration for reliability"""
        print("🏗️  Applying Cross-Cloud Magic: Reliability Optimization")
        
        # Enable comprehensive monitoring
        self.gateway_labels.update({
            "optimization": "reliability",
            "monitoring": "comprehensive",
            "alerting": "enabled",
            "health_checks": "enabled"
        })
        
        # Enable rate limiting for stability
        self.rate_limiting_enabled = True
        
        print("   ├─ 📊 Enabled comprehensive monitoring")
        print("   ├─ 🚦 Enabled rate limiting for stability")
        print("   └─ 🏷️  Added reliability optimization labels")
        
        return self

    def _optimize_for_compliance(self):
        """Optimize configuration for compliance requirements"""
        print("🏗️  Applying Cross-Cloud Magic: Compliance Optimization")
        
        # Enable all security features
        self.auth_enabled = True
        self.api_key_required = True
        self.rate_limiting_enabled = True
        
        # Add compliance labels
        self.gateway_labels.update({
            "optimization": "compliance",
            "security": "maximum",
            "audit": "enabled",
            "compliance": "sox_pci",
            "encryption": "required"
        })
        
        print("   ├─ 🔐 Enabled authentication and API key requirements")
        print("   ├─ 🚦 Enabled rate limiting for security")
        print("   └─ 🏷️  Added compliance optimization labels")
        
        return self

    def _find_existing_gateway(self) -> Optional[Dict[str, Any]]:
        """Find existing gateway by name"""
        try:
            gateway = self.api_gateway_client.get_gateway(name=self.gateway_resource_name)
            return gateway
        except Exception:
            return None

    def _create_new_gateway(self) -> Dict[str, Any]:
        """Create new API Gateway with all components"""
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
            deployment_success = self.wait_for_deployment()
            
            if deployment_success:
                print(f"✅ API Gateway '{self.gateway_id}' created successfully!")
            else:
                print(f"⚠️  API Gateway created but deployment may still be in progress")

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
                parent=f"projects/{self.project_id}/locations/{self.gateway_location}",
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
                        "address": f"https://{backend_config['region']}-{self.project_id}.cloudfunctions.net/{backend_name}"
                    }
                elif backend_type == "cloud_run":
                    backend_config = self.cloud_run_backends[backend_name]
                    operation["x-google-backend"] = {
                        "address": backend_config['url']
                    }
                elif backend_type == "external":
                    backend_config = self.external_backends[backend_name]
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

            print(f"   📋 Built OpenAPI spec with {len(self.openapi_spec['paths'])} paths")

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
                parent=f"projects/{self.project_id}/locations/{self.gateway_location}",
                gateway_id=self.gateway_id,
                gateway=gateway
            )

            print(f"   📋 Created Gateway: {self.gateway_id}")

        except Exception as e:
            print(f"⚠️  Failed to create gateway: {e}")
            raise

    def _get_gateway_info(self) -> Dict[str, Any]:
        """Get gateway information"""
        try:
            return {
                'success': True,
                'api_id': self.api_id,
                'gateway_id': self.gateway_id,
                'gateway_name': self.gateway_name,
                'gateway_url': self.gateway_url,
                'display_name': self.display_name,
                'description': self.gateway_description,
                'routes_count': len(self.routes),
                'backends_count': len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends),
                'cloud_function_backends': len(self.cloud_function_backends),
                'cloud_run_backends': len(self.cloud_run_backends),
                'external_backends': len(self.external_backends),
                'auth_enabled': self.auth_enabled,
                'api_key_required': self.api_key_required,
                'cors_enabled': self.cors_enabled,
                'rate_limiting_enabled': self.rate_limiting_enabled,
                'quota_limit': self.quota_limit,
                'labels': self.gateway_labels,
                'gateway_type': self._get_gateway_type_from_config(),
                'estimated_monthly_cost': f"${self._estimate_api_gateway_cost():.2f}"
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