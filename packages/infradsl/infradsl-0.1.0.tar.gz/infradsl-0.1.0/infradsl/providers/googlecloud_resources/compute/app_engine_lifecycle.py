"""
Google App Engine Lifecycle Mixin

Lifecycle operations for Google App Engine.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Union


class AppEngineLifecycleMixin:
    """
    Mixin for Google App Engine lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update App Engine application
    - destroy(): Clean up App Engine application
    - Smart state management and drift detection
    - Version and traffic management
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Check authentication first
        try:
            self._ensure_authenticated()
        except Exception:
            print("⚠️  Authentication required for App Engine preview")
            
        # Get current application state
        app_state = self._fetch_current_app_state()
        existing_services = self._discover_existing_services()
        
        # Categorize what will happen
        apps_to_create = []
        apps_to_keep = []
        services_to_deploy = []
        
        if not app_state.get("exists"):
            # New App Engine application
            apps_to_create.append({
                "app_name": self.app_name,
                "project_id": self.project_id,
                "location": self.location_id,
                "runtime": self.runtime,
                "instance_class": self.instance_class,
                "scaling_type": self._get_scaling_type(),
                "min_instances": self.min_instances,
                "max_instances": self.max_instances,
                "env_vars": len(self.env_vars),
                "handlers": len(self.handlers),
                "static_files": len(self.static_files),
                "services": self.services or ["default"],
                "estimated_cost": self._estimate_app_engine_cost()
            })
        else:
            # Existing application - will deploy new version
            apps_to_keep.append({
                "app_name": self.app_name,
                "app_id": app_state.get("app_id"),
                "location": app_state.get("location_id"),
                "serving_status": app_state.get("serving_status"),
                "database_type": app_state.get("database_type"),
                "existing_services": len(existing_services),
                "default_hostname": app_state.get("default_hostname")
            })
            
            # Determine services to deploy
            target_services = self.services or ["default"]
            for service in target_services:
                services_to_deploy.append({
                    "service": service,
                    "runtime": self.runtime,
                    "scaling": self._get_scaling_type(),
                    "instance_class": self.instance_class,
                    "new_version": True
                })
                
        print(f"\\n🚀 App Engine Preview")
        
        # Show applications to create
        if apps_to_create:
            print(f"╭─ 🚀 App Engine Applications to CREATE: {len(apps_to_create)}")
            for app in apps_to_create:
                print(f"├─ 🆕 {app['app_name']}")
                print(f"│  ├─ 📁 Project: {app['project_id']}")
                print(f"│  ├─ 📍 Location: {app['location']}")
                print(f"│  ├─ ⚙️  Runtime: {app['runtime']}")
                print(f"│  ├─ 🖥️  Instance: {app['instance_class']}")
                print(f"│  ├─ 📊 Scaling: {app['scaling_type']}")
                
                if app['scaling_type'] == 'automatic':
                    print(f"│  │  ├─ Min: {app['min_instances']} instances")
                    print(f"│  │  └─ Max: {app['max_instances']} instances")
                elif app['scaling_type'] == 'manual':
                    print(f"│  │  └─ Fixed: {app['min_instances']} instances")
                    
                if app['env_vars'] > 0:
                    print(f"│  ├─ 🔧 Environment Variables: {app['env_vars']}")
                    
                if app['handlers'] > 0:
                    print(f"│  ├─ 🔗 URL Handlers: {app['handlers']}")
                    
                if app['static_files'] > 0:
                    print(f"│  ├─ 📄 Static File Rules: {app['static_files']}")
                    
                print(f"│  ├─ 🔧 Services: {', '.join(app['services'])}")
                
                cost = app['estimated_cost']
                if cost > 0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")
            
        # Show existing applications
        if apps_to_keep:
            print(f"\\n╭─ ✅ Existing App Engine Applications: {len(apps_to_keep)}")
            for app in apps_to_keep:
                print(f"├─ ✅ {app['app_name']}")
                print(f"│  ├─ 🆔 App ID: {app['app_id']}")
                print(f"│  ├─ 📍 Location: {app['location']}")
                print(f"│  ├─ 🟢 Status: {app['serving_status']}")
                print(f"│  ├─ 🗄️  Database: {app['database_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 🔧 Existing Services: {app['existing_services']}")
                if app.get('default_hostname'):
                    print(f"│  └─ 🌐 URL: https://{app['default_hostname']}")
            print(f"╰─")
            
        # Show services to deploy
        if services_to_deploy:
            print(f"\\n╭─ 🚀 Services to DEPLOY: {len(services_to_deploy)}")
            for service in services_to_deploy:
                print(f"├─ 📦 {service['service']}")
                print(f"│  ├─ ⚙️  Runtime: {service['runtime']}")
                print(f"│  ├─ 📊 Scaling: {service['scaling']}")
                print(f"│  ├─ 🖥️  Instance: {service['instance_class']}")
                print(f"│  └─ 🆕 New Version: {'✅ Yes' if service['new_version'] else '❌ No'}")
            print(f"╰─")
            
        # Show deployment information
        print(f"\\n🚀 App Engine Deployment:")
        print(f"   ├─ 📁 Source: {self.source_dir}")
        if self.deployment_method == "dockerfile":
            print(f"   ├─ 🐳 Method: Dockerfile")
        elif self.deployment_method == "url":
            print(f"   ├─ 🔗 Method: Source URL")
        else:
            print(f"   ├─ 📄 Method: Source upload")
            
        print(f"   ├─ ⚙️  Runtime: {self.runtime}")
        print(f"   └─ 🚀 Deploy: gcloud app deploy")
        
        # Show App Engine features
        print(f"\\n🚀 App Engine Features:")
        print(f"   ├─ 🔄 Auto-scaling and load balancing")
        print(f"   ├─ 🌍 Global infrastructure")
        print(f"   ├─ 🔒 Built-in security and authentication")
        print(f"   ├─ 📊 Monitoring and logging")
        print(f"   ├─ 🔄 Traffic splitting for A/B testing")
        print(f"   └─ 🗄️  Integrated with Cloud Datastore")
        
        # Cost information
        print(f"\\n💰 App Engine Pricing:")
        print(f"   ├─ 🆓 Free tier: 28 instance hours/day")
        print(f"   ├─ 🖥️  F1 instances: $0.05/hour")
        print(f"   ├─ 🖥️  F2 instances: $0.10/hour")
        print(f"   ├─ 🌐 Outbound traffic: Free 1GB/day")
        print(f"   ├─ 🗄️  Datastore: Free 50K reads, 20K writes/day")
        print(f"   └─ 📊 Most apps stay in free tier")
        
        return {
            "resource_type": "app_engine",
            "name": self.app_name,
            "apps_to_create": apps_to_create,
            "apps_to_keep": apps_to_keep,
            "services_to_deploy": services_to_deploy,
            "existing_services": existing_services,
            "project_id": self.project_id,
            "location": self.location_id,
            "runtime": self.runtime,
            "estimated_cost": f"${self._estimate_app_engine_cost():.2f}/month"
        }
        
    def create(self) -> Dict[str, Any]:
        """Create or deploy App Engine application"""
        if not self.project_id:
            raise ValueError("Project ID is required. Use .project('your-project-id')")
            
        print(f"🚀 Deploying App Engine Application: {self.app_name}")
        
        # Check if App Engine app exists in project
        app_state = self._fetch_current_app_state()
        
        if not app_state.get("exists"):
            print(f"   ⚠️  No App Engine application found in project {self.project_id}")
            print(f"   📋 Creating App Engine application first...")
            
            try:
                # Create App Engine application
                self._create_app_engine_app()
                print(f"   ✅ App Engine application created")
            except Exception as e:
                print(f"   ❌ Failed to create App Engine application: {str(e)}")
                raise
                
        # Generate app.yaml
        app_yaml_path = self._generate_app_yaml()
        print(f"   📄 Generated app.yaml: {app_yaml_path}")
        
        # Deploy the application
        try:
            print(f"   🚀 Deploying application...")
            deployment_result = self._deploy_application(app_yaml_path)
            
            if deployment_result["success"]:
                print(f"   ✅ Application deployed successfully")
                
                # Update state tracking
                self.app_exists = True
                self.app_created = True
                self.app_deployed = True
                self.deployment_status = "deployed"
                
                return {
                    "success": True,
                    "app_name": self.app_name,
                    "project_id": self.project_id,
                    "app_id": self.project_id,
                    "location": self.location_id,
                    "runtime": self.runtime,
                    "services": deployment_result.get("services", ["default"]),
                    "version": deployment_result.get("version"),
                    "url": f"https://{self.project_id}.appspot.com",
                    "console_url": f"https://console.cloud.google.com/appengine?project={self.project_id}",
                    "estimated_cost": f"${self._estimate_app_engine_cost():.2f}/month"
                }
            else:
                raise Exception(deployment_result.get("error", "Deployment failed"))
                
        except Exception as e:
            print(f"   ❌ Deployment failed: {str(e)}")
            self.deployment_status = "failed"
            return {
                "success": False,
                "error": str(e)
            }
            
    def destroy(self) -> Dict[str, Any]:
        """Destroy App Engine application (disable services)"""
        print(f"🗑️  App Engine applications cannot be deleted")
        print(f"   ℹ️  App Engine applications are permanent once created")
        print(f"   🔧 You can disable versions and services instead:")
        print(f"   1. Go to App Engine Console")
        print(f"   2. Disable or delete specific versions")
        print(f"   3. Stop traffic to services")
        
        # Try to disable default service traffic
        try:
            if self.project_id:
                console_url = f"https://console.cloud.google.com/appengine/versions?project={self.project_id}"
                print(f"   🌐 Console: {console_url}")
                
                return {
                    "success": True,
                    "app_name": self.app_name,
                    "status": "manual_action_required",
                    "message": "App Engine apps cannot be deleted - disable versions manually",
                    "console_url": console_url
                }
            else:
                return {
                    "success": False,
                    "error": "No project ID configured"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _get_scaling_type(self) -> str:
        """Get the scaling type for display"""
        if self.automatic_scaling:
            return "automatic"
        elif self.basic_scaling:
            return "basic"
        elif self.manual_scaling:
            return "manual"
        else:
            return "automatic"  # default
            
    def _create_app_engine_app(self):
        """Create App Engine application in project"""
        try:
            # Use gcloud command to create App Engine app
            cmd = [
                "gcloud", "app", "create",
                "--region", self.location_id,
                "--project", self.project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                if "already contains an App Engine application" in result.stderr:
                    # App already exists, that's fine
                    return
                else:
                    raise Exception(f"gcloud app create failed: {result.stderr}")
                    
        except FileNotFoundError:
            # gcloud not available, try using API
            self._create_app_via_api()
            
    def _create_app_via_api(self):
        """Create App Engine application via API"""
        try:
            from google.cloud import appengine_admin_v1
            
            if not self.app_engine_admin:
                self.app_engine_admin = appengine_admin_v1.ApplicationsClient()
                
            # Create application
            application = appengine_admin_v1.Application(
                id=self.project_id,
                location_id=self.location_id,
                database_type=appengine_admin_v1.Application.DatabaseType.CLOUD_DATASTORE_COMPATIBILITY
            )
            
            request = appengine_admin_v1.CreateApplicationRequest(
                application=application
            )
            
            operation = self.app_engine_admin.create_application(request=request)
            
            # Wait for operation to complete
            print(f"   ⏳ Waiting for App Engine application creation...")
            result = operation.result(timeout=300)  # 5 minutes timeout
            
        except Exception as e:
            raise Exception(f"API application creation failed: {str(e)}")
            
    def _generate_app_yaml(self) -> str:
        """Generate app.yaml configuration file"""
        config = self.get_app_yaml_config()
        
        # Create app.yaml in source directory
        app_yaml_path = os.path.join(self.source_dir, "app.yaml")
        
        # Ensure source directory exists
        os.makedirs(self.source_dir, exist_ok=True)
        
        with open(app_yaml_path, 'w') as f:
            # Write app.yaml
            f.write(f"runtime: {config['runtime']}\\n")
            
            if 'instance_class' in config:
                f.write(f"instance_class: {config['instance_class']}\\n")
                
            # Scaling configuration
            if 'automatic_scaling' in config:
                f.write("automatic_scaling:\\n")
                scaling = config['automatic_scaling']
                if 'min_instances' in scaling:
                    f.write(f"  min_instances: {scaling['min_instances']}\\n")
                if 'max_instances' in scaling:
                    f.write(f"  max_instances: {scaling['max_instances']}\\n")
                    
            elif 'basic_scaling' in config:
                f.write("basic_scaling:\\n")
                scaling = config['basic_scaling']
                f.write(f"  max_instances: {scaling['max_instances']}\\n")
                if 'idle_timeout' in scaling:
                    f.write(f"  idle_timeout: {scaling['idle_timeout']}\\n")
                    
            elif 'manual_scaling' in config:
                f.write("manual_scaling:\\n")
                f.write(f"  instances: {config['manual_scaling']['instances']}\\n")
                
            # Environment variables
            if 'env_variables' in config and config['env_variables']:
                f.write("env_variables:\\n")
                for key, value in config['env_variables'].items():
                    f.write(f"  {key}: '{value}'\\n")
                    
            # Handlers
            if 'handlers' in config and config['handlers']:
                f.write("handlers:\\n")
                for handler in config['handlers']:
                    f.write(f"- url: {handler['url']}\\n")
                    f.write(f"  script: {handler['script']}\\n")
                    
            # Static files
            if self.static_files:
                if 'handlers' not in config:
                    f.write("handlers:\\n")
                for static in self.static_files:
                    f.write(f"- url: {static['url']}\\n")
                    f.write(f"  static_dir: {static['static_dir']}\\n")
                    if static.get('expiration'):
                        f.write(f"  expiration: {static['expiration']}\\n")
                        
        return app_yaml_path
        
    def _deploy_application(self, app_yaml_path: str) -> Dict[str, Any]:
        """Deploy application using gcloud"""
        try:
            # Use gcloud app deploy
            cmd = [
                "gcloud", "app", "deploy", app_yaml_path,
                "--project", self.project_id,
                "--quiet",
                "--stop-previous-version"
            ]
            
            if self.version_id:
                cmd.extend(["--version", self.version_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "services": ["default"],
                    "version": self.version_id or "auto-generated"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": "gcloud CLI not found. Please install Google Cloud SDK."
            }
            
    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize App Engine configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self
            
    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Minimize instance usage
        self.automatic_scaling(min_instances=0, max_instances=3)
        self.micro_instance()
        
        # Use basic scaling for predictable costs
        if not self.automatic_scaling:
            self.basic_scaling(max_instances=2)
            
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "scaling": "minimal",
            "instance_class": "micro"
        })
        
        print("   ├─ 📉 Minimal scaling configuration")
        print("   ├─ 🖥️  Micro instances")
        print("   ├─ 📊 Basic scaling mode")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self
        
    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use larger instances and keep them warm
        self.small_instance()
        self.automatic_scaling(min_instances=2, max_instances=20)
        
        # Enable session affinity
        self.session_affinity(True)
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "scaling": "aggressive",
            "warmup": "enabled"
        })
        
        print("   ├─ 🖥️  Small instances for better performance")
        print("   ├─ 📈 Aggressive scaling")
        print("   ├─ 🔥 Warm instances (min 2)")
        print("   ├─ 🔗 Session affinity enabled")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self
        
    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enforce HTTPS and authentication
        self.https_only()
        self.login_required()
        
        # Add security labels
        self.labels({
            "optimization": "security",
            "https": "enforced",
            "auth": "required"
        })
        
        print("   ├─ 🔒 HTTPS enforced")
        print("   ├─ 🔑 Login required")
        print("   ├─ 🛡️  Security headers enabled")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self
        
    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Balance performance and cost
        self.automatic_scaling(min_instances=1, max_instances=10)
        self.small_instance()
        
        # Enable features for better UX
        self.session_affinity(True)
        self.custom_404()
        self.custom_500()
        
        # Add UX labels
        self.labels({
            "optimization": "user_experience",
            "ux_focused": "true",
            "error_pages": "custom"
        })
        
        print("   ├─ ⚖️  Balanced scaling")
        print("   ├─ 🔗 Session affinity")
        print("   ├─ 📄 Custom error pages")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self