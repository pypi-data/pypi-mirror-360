"""
Firebase Functions Complete Implementation

Complete Firebase Functions implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .firebase_functions_core import FirebaseFunctionsCore
from .firebase_functions_configuration import FirebaseFunctionsConfigurationMixin
from .firebase_functions_lifecycle import FirebaseFunctionsLifecycleMixin


class FirebaseFunctions(FirebaseFunctionsCore, FirebaseFunctionsConfigurationMixin, FirebaseFunctionsLifecycleMixin):
    """
    Complete Firebase Functions implementation.
    
    This class combines:
    - FirebaseFunctionsCore: Basic functions attributes and authentication
    - FirebaseFunctionsConfigurationMixin: Chainable configuration methods
    - FirebaseFunctionsLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent serverless configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete serverless support (HTTP, callable, triggers, scheduled)
    - Multiple trigger types (Firestore, Storage, Auth, Pub/Sub)
    - Runtime configuration (Node.js, Python, Go, Java)
    - Resource optimization (memory, timeout, scaling)
    - Common serverless patterns (API, webhook, trigger-based, microservices)
    - Application-specific configurations (mobile, web, analytics)
    - Environment-specific settings (development, staging, production)
    
    Example:
        # Simple API backend
        api = FirebaseFunctions("my-api")
        api.project("my-firebase-project").simple_api()
        api.create()
        
        # Microservices backend
        services = FirebaseFunctions("microservices")
        services.project("my-project").microservices_api()
        services.create()
        
        # Event-driven processing
        processor = FirebaseFunctions("event-processor")
        processor.project("my-project").event_processor()
        processor.create()
        
        # Scheduled tasks
        tasks = FirebaseFunctions("background-tasks")
        tasks.project("my-project").scheduled_tasks()
        tasks.create()
        
        # Custom configuration
        funcs = FirebaseFunctions("custom-funcs")
        funcs.project("my-project").nodejs18()
        funcs.http_function("api").callable_function("getUserData")
        funcs.firestore_trigger("onUserCreate", "users/{userId}")
        funcs.scheduled_function("dailyBackup", "0 2 * * *")
        funcs.memory("512MB").timeout(180)
        funcs.create()
        
        # Mobile backend
        mobile = FirebaseFunctions("mobile-backend")
        mobile.project("mobile-project").mobile_backend()
        mobile.create()
        
        # Image processing
        processor = FirebaseFunctions("image-processor")
        processor.project("media-project").image_processor()
        processor.create()
        
        # Cross-Cloud Magic optimization
        optimized = FirebaseFunctions("optimized-funcs")
        optimized.project("my-project").microservices_api()
        optimized.optimize_for("performance")
        optimized.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Firebase Functions with project name.
        
        Args:
            name: Functions project name
        """
        # Initialize all parent classes
        FirebaseFunctionsCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Firebase Functions instance"""
        functions_type = self._get_functions_type_from_config()
        function_count = len(self.functions)
        runtime_info = f"{self.runtime}@{self.region}"
        status = "configured" if function_count > 0 or self.firebase_project_id else "unconfigured"
        
        return (f"FirebaseFunctions(name='{self.functions_name}', "
                f"type='{functions_type}', "
                f"functions={function_count}, "
                f"runtime='{runtime_info}', "
                f"project='{self.firebase_project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Firebase Functions configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze function configuration
        function_types = self.get_function_types()
        trigger_functions = []
        api_functions = []
        
        for func in self.functions:
            func_type = func.get("type", "unknown")
            if func_type in ["firestore", "storage", "auth", "pubsub"]:
                trigger_functions.append(func["name"])
            elif func_type in ["http", "callable"]:
                api_functions.append(func["name"])
        
        # Categorize by function purpose
        function_categories = []
        if api_functions:
            function_categories.append("api_backend")
        if trigger_functions:
            function_categories.append("event_processing")
        if self.has_scheduled_functions():
            function_categories.append("background_tasks")
        
        # Resource analysis
        total_memory_mb = 0
        memory_allocations = set()
        timeouts = set()
        
        for func in self.functions:
            memory = func.get("memory", self.default_memory)
            memory_mb = int(memory.replace("MB", "").replace("GB", "000"))
            total_memory_mb += memory_mb
            memory_allocations.add(memory)
            
            timeout = func.get("timeout", self.default_timeout)
            timeouts.add(timeout)
        
        summary = {
            "functions_name": self.functions_name,
            "firebase_project_id": self.firebase_project_id,
            "functions_description": self.functions_description,
            "functions_type": self._get_functions_type_from_config(),
            "function_categories": function_categories,
            
            # Runtime configuration
            "runtime": self.runtime,
            "region": self.region,
            "source_directory": self.source_directory,
            "execution_environment": self.execution_environment,
            
            # Functions
            "functions": self.functions,
            "function_count": len(self.functions),
            "function_types": function_types,
            "api_functions": api_functions,
            "trigger_functions": trigger_functions,
            "function_configs": self.function_configs,
            
            # Resource allocation
            "default_memory": self.default_memory,
            "default_timeout": self.default_timeout,
            "default_max_instances": self.default_max_instances,
            "default_min_instances": self.default_min_instances,
            "concurrency": self.concurrency,
            "cpu": self.cpu,
            "total_memory_mb": total_memory_mb,
            "memory_allocations": list(memory_allocations),
            "timeout_range": [min(timeouts), max(timeouts)] if timeouts else [self.default_timeout],
            
            # Environment and dependencies
            "environment_variables": self.environment_variables,
            "env_var_count": len(self.environment_variables),
            "secrets": self.secrets,
            "dependencies": self.dependencies,
            "dependency_count": len(self.dependencies),
            "dev_dependencies": self.dev_dependencies,
            
            # Security and networking
            "require_auth": self.require_auth,
            "cors_enabled": self.cors_enabled,
            "cors_origins": self.cors_origins,
            "ingress_settings": self.ingress_settings,
            "egress_settings": self.egress_settings,
            "vpc_connector": self.vpc_connector,
            
            # Feature analysis
            "has_http_functions": self.has_http_functions(),
            "has_trigger_functions": self.has_trigger_functions(),
            "has_scheduled_functions": self.has_scheduled_functions(),
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.functions_labels,
            "label_count": len(self.functions_labels),
            "annotations": self.functions_annotations,
            
            # State
            "state": {
                "deployed": self.functions_deployed,
                "deployment_status": self.deployment_status,
                "deployment_time": self.deployment_time,
                "last_updated": self.last_updated
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_firebase_functions_cost():.2f}",
            "is_free_tier": self._estimate_firebase_functions_cost() == 0.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n⚡ Firebase Functions Configuration: {self.functions_name}")
        print(f"   📁 Firebase Project: {self.firebase_project_id}")
        print(f"   📝 Description: {self.functions_description}")
        print(f"   🎯 Functions Type: {self._get_functions_type_from_config().replace('_', ' ').title()}")
        print(f"   🔧 Runtime: {self.runtime}")
        print(f"   📍 Region: {self.region}")
        print(f"   📁 Source Directory: {self.source_directory}")
        
        # Functions
        if self.functions:
            print(f"\n⚡ Functions ({len(self.functions)}):")
            function_types = self.get_function_types()
            for func_type, count in function_types.items():
                type_icon = self._get_function_icon(func_type)
                print(f"   {type_icon} {func_type.title()}: {count}")
            
            print(f"\n📋 Function Details:")
            for func in self.functions:
                func_icon = self._get_function_icon(func['type'])
                print(f"   {func_icon} {func['name']} ({func['type']})")
                print(f"      ├─ 📄 Source: {func.get('source_file', 'generated')}")
                print(f"      ├─ 💾 Memory: {func.get('memory', self.default_memory)}")
                print(f"      ├─ ⏱️  Timeout: {func.get('timeout', self.default_timeout)}s")
                
                # Show trigger-specific details
                if func['type'] == 'firestore':
                    print(f"      ├─ 📄 Document: {func.get('document_path', 'unknown')}")
                    print(f"      └─ 🔄 Event: {func.get('event', 'create')}")
                elif func['type'] == 'storage':
                    print(f"      ├─ 🪣 Bucket: {func.get('bucket', f'{self.firebase_project_id}.appspot.com')}")
                    print(f"      └─ 🔄 Event: {func.get('event', 'finalize')}")
                elif func['type'] == 'scheduled':
                    print(f"      ├─ 📅 Schedule: {func.get('schedule', '0 2 * * *')}")
                    print(f"      └─ 🌐 Timezone: {func.get('timezone', 'UTC')}")
                elif func['type'] == 'pubsub':
                    print(f"      └─ 📢 Topic: {func.get('topic', 'unknown')}")
                elif func['type'] == 'http':
                    print(f"      └─ 🔗 URL: https://{self.region}-{self.firebase_project_id}.cloudfunctions.net/{func['name']}")
        else:
            print(f"\n⚡ Functions: None configured")
        
        # Resource configuration
        print(f"\n⚙️  Resource Configuration:")
        print(f"   💾 Default Memory: {self.default_memory}")
        print(f"   ⏱️  Default Timeout: {self.default_timeout}s")
        print(f"   📈 Max Instances: {self.default_max_instances}")
        print(f"   📉 Min Instances: {self.default_min_instances}")
        print(f"   🔄 Concurrency: {self.concurrency} requests/instance")
        print(f"   🖥️  CPU: {self.cpu}")
        print(f"   🏗️  Execution Environment: {self.execution_environment}")
        
        # Environment and dependencies
        if self.environment_variables:
            print(f"\n🔧 Environment Variables ({len(self.environment_variables)}):")
            for key, value in list(self.environment_variables.items())[:5]:
                print(f"   • {key}: {'***' if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower() else value}")
            if len(self.environment_variables) > 5:
                print(f"   • ... and {len(self.environment_variables) - 5} more")
        
        if self.dependencies:
            print(f"\n📦 Dependencies ({len(self.dependencies)}):")
            for package, version in list(self.dependencies.items())[:5]:
                print(f"   • {package}: {version}")
            if len(self.dependencies) > 5:
                print(f"   • ... and {len(self.dependencies) - 5} more")
        
        # Security configuration
        print(f"\n🔒 Security Configuration:")
        print(f"   🔐 Authentication Required: {'✅ Yes' if self.require_auth else '❌ No'}")
        print(f"   🌍 CORS: {'✅ Enabled' if self.cors_enabled else '❌ Disabled'}")
        if self.cors_enabled and self.cors_origins != ["*"]:
            print(f"      └─ Origins: {', '.join(self.cors_origins[:3])}")
        print(f"   📥 Ingress: {self.ingress_settings}")
        print(f"   📤 Egress: {self.egress_settings}")
        if self.vpc_connector:
            print(f"   🔗 VPC Connector: {self.vpc_connector}")
        
        # Labels
        if self.functions_labels:
            print(f"\n🏷️  Labels ({len(self.functions_labels)}):")
            for key, value in list(self.functions_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.functions_labels) > 5:
                print(f"   • ... and {len(self.functions_labels) - 5} more")
        
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs attention'}")
        if not production_ready:
            issues = []
            if len(self.functions) == 0:
                issues.append("No functions configured")
            if self.default_memory == "128MB":
                issues.append("Consider more memory for production")
            if self.default_timeout < 60:
                issues.append("Consider longer timeout for production")
            if not self.firebase_project_id:
                issues.append("Firebase project ID required")
            
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
        
        # Cost
        cost = self._estimate_firebase_functions_cost()
        if cost > 0:
            print(f"\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\n💰 Cost: Free tier")
        
        # Console link
        if self.firebase_project_id:
            print(f"\n🌐 Firebase Console:")
            print(f"   🔗 https://console.firebase.google.com/project/{self.firebase_project_id}/functions/")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Firebase Functions performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_features": [],
            "bottlenecks": []
        }
        
        # Memory allocation analysis
        memory_mb = int(self.default_memory.replace("MB", "").replace("GB", "000"))
        if memory_mb >= 512:
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Adequate memory allocation")
        elif memory_mb >= 256:
            analysis["performance_score"] += 15
            analysis["performance_features"].append("Basic memory allocation")
        else:
            analysis["bottlenecks"].append("Low memory allocation may cause performance issues")
            analysis["recommendations"].append("Consider increasing memory to 256MB or higher")
        
        # Timeout analysis
        if self.default_timeout >= 120:
            analysis["performance_score"] += 15
            analysis["performance_features"].append("Sufficient timeout allocation")
        else:
            analysis["recommendations"].append("Consider increasing timeout for complex operations")
        
        # Scaling configuration
        if self.default_min_instances > 0:
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Warm instances to avoid cold starts")
        else:
            analysis["bottlenecks"].append("Cold starts may affect performance")
            analysis["recommendations"].append("Consider setting min instances > 0 for critical functions")
        
        if self.default_max_instances >= 100:
            analysis["performance_score"] += 15
            analysis["performance_features"].append("Good scaling capacity")
        
        # Concurrency analysis
        if self.concurrency >= 80:
            analysis["performance_score"] += 15
            analysis["performance_features"].append("High concurrency per instance")
        elif self.concurrency >= 40:
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Moderate concurrency")
        
        # Execution environment
        if self.execution_environment == "gen2":
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Next-generation execution environment")
        
        # Region optimization
        if self.region in ["us-central1", "us-east1"]:
            analysis["performance_score"] += 5
            analysis["performance_features"].append("Low-latency region")
        
        return analysis
    
    def analyze_cost(self) -> Dict[str, Any]:
        """
        Analyze Firebase Functions cost configuration and provide recommendations.
        
        Returns:
            Dict containing cost analysis and recommendations
        """
        analysis = {
            "cost_score": 0,
            "max_score": 100,
            "recommendations": [],
            "cost_features": [],
            "cost_concerns": []
        }
        
        estimated_cost = self._estimate_firebase_functions_cost()
        
        # Cost level analysis
        if estimated_cost == 0:
            analysis["cost_score"] += 30
            analysis["cost_features"].append("Free tier usage")
        elif estimated_cost <= 10:
            analysis["cost_score"] += 25
            analysis["cost_features"].append("Low monthly cost")
        elif estimated_cost <= 50:
            analysis["cost_score"] += 15
            analysis["cost_features"].append("Moderate monthly cost")
        else:
            analysis["cost_concerns"].append("High monthly cost")
            analysis["recommendations"].append("Review resource allocation and scaling settings")
        
        # Memory efficiency
        memory_mb = int(self.default_memory.replace("MB", "").replace("GB", "000"))
        if memory_mb <= 256:
            analysis["cost_score"] += 20
            analysis["cost_features"].append("Cost-efficient memory allocation")
        elif memory_mb <= 512:
            analysis["cost_score"] += 15
            analysis["cost_features"].append("Balanced memory allocation")
        else:
            analysis["recommendations"].append("Consider if high memory allocation is necessary")
        
        # Timeout efficiency
        if self.default_timeout <= 120:
            analysis["cost_score"] += 15
            analysis["cost_features"].append("Efficient timeout settings")
        else:
            analysis["recommendations"].append("Review if long timeouts are necessary")
        
        # Min instances impact
        if self.default_min_instances == 0:
            analysis["cost_score"] += 20
            analysis["cost_features"].append("No always-on instances")
        else:
            analysis["cost_concerns"].append("Always-on instances increase base cost")
            analysis["recommendations"].append("Consider if warm instances are necessary")
        
        # Function count impact
        if len(self.functions) <= 5:
            analysis["cost_score"] += 10
            analysis["cost_features"].append("Manageable function count")
        elif len(self.functions) > 20:
            analysis["recommendations"].append("Consider consolidating functions to reduce complexity")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def _get_function_icon(self, function_type: str) -> str:
        """Get icon for function type"""
        icons = {
            "http": "🌐",
            "callable": "📞",
            "firestore": "🔥",
            "storage": "📁",
            "scheduled": "⏰",
            "auth": "🔐",
            "pubsub": "📡",
            "event": "🔄"
        }
        return icons.get(function_type, "⚡")
    
    def get_status(self) -> Dict[str, Any]:
        """Get functions status for backwards compatibility"""
        return {
            "functions_name": self.functions_name,
            "firebase_project_id": self.firebase_project_id,
            "functions_type": self._get_functions_type_from_config(),
            "runtime": self.runtime,
            "region": self.region,
            "functions": self.functions,
            "function_count": len(self.functions),
            "function_types": self.get_function_types(),
            "has_http_functions": self.has_http_functions(),
            "has_trigger_functions": self.has_trigger_functions(),
            "has_scheduled_functions": self.has_scheduled_functions(),
            "is_production_ready": self.is_production_ready(),
            "estimated_cost": f"${self._estimate_firebase_functions_cost():.2f}/month"
        }


# Convenience function for creating Firebase Functions instances
def create_firebase_functions(name: str) -> FirebaseFunctions:
    """
    Create a new Firebase Functions instance.
    
    Args:
        name: Functions project name
        
    Returns:
        FirebaseFunctions instance
    """
    return FirebaseFunctions(name)


# Export the class for easy importing
__all__ = ['FirebaseFunctions', 'create_firebase_functions']