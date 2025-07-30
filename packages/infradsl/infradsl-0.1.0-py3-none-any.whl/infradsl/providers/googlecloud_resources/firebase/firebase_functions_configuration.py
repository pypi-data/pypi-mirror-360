"""
Firebase Functions Configuration Mixin

Configuration methods for Firebase Functions.
Provides Rails-like method chaining for fluent serverless functions configuration.
"""

from typing import Dict, Any, List, Optional, Union


class FirebaseFunctionsConfigurationMixin:
    """
    Configuration mixin for Firebase Functions.
    
    This mixin provides:
    - Chainable configuration methods for functions setup
    - HTTP, callable, and trigger function management
    - Runtime and resource configuration
    - Security and networking configuration
    - Common serverless patterns (API, webhook, trigger-based, scheduled)
    - Application-specific configurations (mobile, web, microservices)
    - Environment-specific settings (development, staging, production)
    """
    
    # ========== Project and Runtime Configuration ==========
    
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self.firebase_project_id = project_id
        self.label("project", project_id)
        return self
    
    def runtime(self, runtime: str):
        """Set function runtime"""
        if not self._is_valid_runtime(runtime):
            raise ValueError(f"Invalid runtime: {runtime}")
        self.runtime = runtime
        self.label("runtime", runtime)
        return self
    
    def nodejs18(self):
        """Set runtime to Node.js 18"""
        return self.runtime("nodejs18")
    
    def nodejs16(self):
        """Set runtime to Node.js 16"""
        return self.runtime("nodejs16")
    
    def python311(self):
        """Set runtime to Python 3.11"""
        return self.runtime("python311")
    
    def python39(self):
        """Set runtime to Python 3.9"""
        return self.runtime("python39")
    
    def go119(self):
        """Set runtime to Go 1.19"""
        return self.runtime("go119")
    
    def java17(self):
        """Set runtime to Java 17"""
        return self.runtime("java17")
    
    def region(self, region: str):
        """Set deployment region"""
        if not self._is_valid_region(region):
            raise ValueError(f"Invalid region: {region}")
        self.region = region
        self.label("region", region)
        return self
    
    def source_directory(self, directory: str):
        """Set source code directory"""
        self.source_directory = directory
        return self
    
    def description(self, description: str):
        """Set functions description"""
        self.functions_description = description
        return self
    
    # ========== Resource Configuration ==========
    
    def memory(self, memory: str):
        """Set default memory allocation"""
        if not self._is_valid_memory(memory):
            raise ValueError(f"Invalid memory: {memory}")
        self.default_memory = memory
        self.label("memory", memory)
        return self
    
    def timeout(self, seconds: int):
        """Set default timeout in seconds"""
        if seconds < 1 or seconds > 540:
            raise ValueError("Timeout must be between 1 and 540 seconds")
        self.default_timeout = seconds
        self.label("timeout", str(seconds))
        return self
    
    def max_instances(self, count: int):
        """Set maximum instances for scaling"""
        self.default_max_instances = count
        self.label("max_instances", str(count))
        return self
    
    def min_instances(self, count: int):
        """Set minimum instances (always warm)"""
        self.default_min_instances = count
        self.label("min_instances", str(count))
        return self
    
    def concurrency(self, requests_per_instance: int):
        """Set concurrent requests per instance"""
        if requests_per_instance < 1 or requests_per_instance > 1000:
            raise ValueError("Concurrency must be between 1 and 1000")
        self.concurrency = requests_per_instance
        return self
    
    def cpu(self, cpu_count: int):
        """Set CPU allocation"""
        if cpu_count not in [1, 2, 4, 8]:
            raise ValueError("CPU must be 1, 2, 4, or 8")
        self.cpu = cpu_count
        return self
    
    # ========== HTTP Functions ==========
    
    def http_function(self, name: str, source_file: str = None, **kwargs):
        """Add HTTP function"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        function_config = {
            "type": "http",
            "name": name,
            "source_file": source_file or f"src/{name}.js",
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout),
            "max_instances": kwargs.get("max_instances", self.default_max_instances),
            "min_instances": kwargs.get("min_instances", self.default_min_instances),
            "cors": kwargs.get("cors", self.cors_enabled),
            "auth_required": kwargs.get("auth_required", False)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    def api_endpoint(self, name: str, path: str = None, **kwargs):
        """Add API endpoint function"""
        return self.http_function(name, **kwargs).label("type", "api")
    
    def webhook(self, name: str, source_file: str = None, **kwargs):
        """Add webhook function"""
        return self.http_function(name, source_file, **kwargs).label("type", "webhook")
    
    # ========== Callable Functions ==========
    
    def callable_function(self, name: str, source_file: str = None, **kwargs):
        """Add callable function (Firebase SDK only)"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        function_config = {
            "type": "callable",
            "name": name,
            "source_file": source_file or f"src/{name}.js",
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout),
            "max_instances": kwargs.get("max_instances", self.default_max_instances),
            "auth_required": True  # Callable functions always require auth
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    # ========== Firestore Triggers ==========
    
    def firestore_trigger(self, name: str, document_path: str, event: str = "create", **kwargs):
        """Add Firestore trigger function"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        valid_events = ["create", "update", "delete", "write"]
        if event not in valid_events:
            raise ValueError(f"Event must be one of: {', '.join(valid_events)}")
        
        function_config = {
            "type": "firestore",
            "name": name,
            "source_file": kwargs.get("source_file", f"src/{name}.js"),
            "document_path": document_path,
            "event": event,
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    def on_user_create(self, name: str = "onUserCreate", **kwargs):
        """Trigger when user document is created"""
        return self.firestore_trigger(name, "users/{userId}", "create", **kwargs)
    
    def on_user_update(self, name: str = "onUserUpdate", **kwargs):
        """Trigger when user document is updated"""
        return self.firestore_trigger(name, "users/{userId}", "update", **kwargs)
    
    def on_post_create(self, name: str = "onPostCreate", **kwargs):
        """Trigger when post document is created"""
        return self.firestore_trigger(name, "posts/{postId}", "create", **kwargs)
    
    def on_order_create(self, name: str = "onOrderCreate", **kwargs):
        """Trigger when order document is created"""
        return self.firestore_trigger(name, "orders/{orderId}", "create", **kwargs)
    
    # ========== Storage Triggers ==========
    
    def storage_trigger(self, name: str, event: str = "finalize", bucket: str = None, **kwargs):
        """Add Storage trigger function"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        valid_events = ["finalize", "delete", "archive", "metadataUpdate"]
        if event not in valid_events:
            raise ValueError(f"Event must be one of: {', '.join(valid_events)}")
        
        function_config = {
            "type": "storage",
            "name": name,
            "source_file": kwargs.get("source_file", f"src/{name}.js"),
            "event": event,
            "bucket": bucket or f"{self.firebase_project_id}.appspot.com",
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    def on_file_upload(self, name: str = "onFileUpload", **kwargs):
        """Trigger when file is uploaded"""
        return self.storage_trigger(name, "finalize", **kwargs)
    
    def on_file_delete(self, name: str = "onFileDelete", **kwargs):
        """Trigger when file is deleted"""
        return self.storage_trigger(name, "delete", **kwargs)
    
    def on_image_upload(self, name: str = "onImageUpload", **kwargs):
        """Trigger when image is uploaded (for processing)"""
        return self.storage_trigger(name, "finalize", **kwargs).label("purpose", "image_processing")
    
    # ========== Scheduled Functions ==========
    
    def scheduled_function(self, name: str, schedule: str, **kwargs):
        """Add scheduled function (cron)"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        function_config = {
            "type": "scheduled",
            "name": name,
            "source_file": kwargs.get("source_file", f"src/{name}.js"),
            "schedule": schedule,
            "timezone": kwargs.get("timezone", "UTC"),
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    def daily_task(self, name: str, hour: int = 2, **kwargs):
        """Schedule daily task"""
        schedule = f"0 {hour} * * *"
        return self.scheduled_function(name, schedule, **kwargs)
    
    def weekly_task(self, name: str, day: int = 0, hour: int = 2, **kwargs):
        """Schedule weekly task (0=Sunday, 6=Saturday)"""
        schedule = f"0 {hour} * * {day}"
        return self.scheduled_function(name, schedule, **kwargs)
    
    def hourly_task(self, name: str, minute: int = 0, **kwargs):
        """Schedule hourly task"""
        schedule = f"{minute} * * * *"
        return self.scheduled_function(name, schedule, **kwargs)
    
    # ========== Auth Triggers ==========
    
    def auth_trigger(self, name: str, event: str = "create", **kwargs):
        """Add Authentication trigger function"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        valid_events = ["create", "delete"]
        if event not in valid_events:
            raise ValueError(f"Event must be one of: {', '.join(valid_events)}")
        
        function_config = {
            "type": "auth",
            "name": name,
            "source_file": kwargs.get("source_file", f"src/{name}.js"),
            "event": event,
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    def on_user_signup(self, name: str = "onUserSignup", **kwargs):
        """Trigger when user signs up"""
        return self.auth_trigger(name, "create", **kwargs)
    
    def on_user_delete(self, name: str = "onUserDelete", **kwargs):
        """Trigger when user is deleted"""
        return self.auth_trigger(name, "delete", **kwargs)
    
    # ========== Pub/Sub Triggers ==========
    
    def pubsub_trigger(self, name: str, topic: str, **kwargs):
        """Add Pub/Sub trigger function"""
        if not self._is_valid_function_name(name):
            raise ValueError(f"Invalid function name: {name}")
        
        function_config = {
            "type": "pubsub",
            "name": name,
            "source_file": kwargs.get("source_file", f"src/{name}.js"),
            "topic": topic,
            "memory": kwargs.get("memory", self.default_memory),
            "timeout": kwargs.get("timeout", self.default_timeout)
        }
        
        self.functions.append(function_config)
        self.function_configs[name] = function_config
        self.label("function_count", str(len(self.functions)))
        return self
    
    # ========== Environment and Dependencies ==========
    
    def environment_variable(self, key: str, value: str):
        """Add environment variable"""
        self.environment_variables[key] = value
        return self
    
    def environment_variables(self, env_vars: Dict[str, str]):
        """Add multiple environment variables"""
        self.environment_variables.update(env_vars)
        return self
    
    def secret(self, key: str, secret_name: str, version: str = "latest"):
        """Add secret from Secret Manager"""
        self.secrets[key] = {"name": secret_name, "version": version}
        return self
    
    def dependency(self, package: str, version: str = "latest"):
        """Add npm/pip dependency"""
        self.dependencies[package] = version
        return self
    
    def dependencies(self, deps: Dict[str, str]):
        """Add multiple dependencies"""
        self.dependencies.update(deps)
        return self
    
    def dev_dependency(self, package: str, version: str = "latest"):
        """Add development dependency"""
        self.dev_dependencies[package] = version
        return self
    
    # ========== Security Configuration ==========
    
    def require_authentication(self, required: bool = True):
        """Require authentication for all functions"""
        self.require_auth = required
        return self
    
    def cors(self, enabled: bool = True, origins: List[str] = None):
        """Configure CORS"""
        self.cors_enabled = enabled
        if origins:
            self.cors_origins = origins
        return self
    
    def ingress(self, setting: str):
        """Set ingress settings"""
        valid_settings = ["ALLOW_ALL", "ALLOW_INTERNAL_ONLY", "ALLOW_INTERNAL_AND_GCLB"]
        if setting not in valid_settings:
            raise ValueError(f"Ingress setting must be one of: {', '.join(valid_settings)}")
        self.ingress_settings = setting
        return self
    
    def egress(self, setting: str):
        """Set egress settings"""
        valid_settings = ["PRIVATE_RANGES_ONLY", "ALL"]
        if setting not in valid_settings:
            raise ValueError(f"Egress setting must be one of: {', '.join(valid_settings)}")
        self.egress_settings = setting
        return self
    
    def vpc_connector(self, connector_name: str):
        """Set VPC connector for private network access"""
        self.vpc_connector = connector_name
        return self
    
    # ========== Common Patterns ==========
    
    def simple_api(self):
        """Rails convenience: Simple REST API backend"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("256MB")
                .http_function("api")
                .cors(True)
                .label("type", "simple_api")
                .label("complexity", "basic"))
    
    def microservices_api(self):
        """Rails convenience: Microservices API backend"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("512MB")
                .max_instances(100)
                .http_function("users")
                .http_function("posts")
                .http_function("orders")
                .cors(True)
                .require_authentication()
                .label("type", "microservices")
                .label("complexity", "medium"))
    
    def event_processor(self):
        """Rails convenience: Event-driven processing"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("512MB")
                .on_user_create()
                .on_post_create()
                .on_file_upload()
                .label("type", "event_processor")
                .label("complexity", "medium"))
    
    def scheduled_tasks(self):
        """Rails convenience: Scheduled background tasks"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("256MB")
                .daily_task("dailyBackup", 2)
                .weekly_task("weeklyReport", 0, 9)
                .hourly_task("dataSync", 0)
                .label("type", "scheduled_tasks")
                .label("complexity", "basic"))
    
    def webhook_handler(self):
        """Rails convenience: Webhook processing"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("256MB")
                .webhook("stripeWebhook")
                .webhook("githubWebhook")
                .webhook("slackWebhook")
                .cors(False)
                .label("type", "webhook_handler")
                .label("complexity", "basic"))
    
    def image_processor(self):
        """Rails convenience: Image processing pipeline"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("1GB")
                .timeout(300)
                .on_image_upload("processImage")
                .on_image_upload("generateThumbnails")
                .dependency("sharp", "^0.32.0")
                .label("type", "image_processor")
                .label("complexity", "medium"))
    
    # ========== Application-Specific Configurations ==========
    
    def mobile_backend(self):
        """Rails convenience: Mobile app backend"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("256MB")
                .callable_function("getUserProfile")
                .callable_function("updateUserData")
                .callable_function("sendNotification")
                .on_user_create("createUserProfile")
                .require_authentication()
                .label("platform", "mobile")
                .label("type", "mobile_backend"))
    
    def web_app_backend(self):
        """Rails convenience: Web application backend"""
        return (self.simple_api()
                .http_function("auth")
                .http_function("dashboard")
                .on_user_signup("sendWelcomeEmail")
                .cors(True, ["https://yourdomain.com"])
                .label("platform", "web"))
    
    def ecommerce_backend(self):
        """Rails convenience: E-commerce backend"""
        return (self.microservices_api()
                .http_function("cart")
                .http_function("checkout")
                .http_function("payments")
                .on_order_create("processOrder")
                .on_order_create("sendOrderConfirmation")
                .webhook("paymentWebhook")
                .memory("512MB")
                .label("type", "ecommerce"))
    
    def analytics_processor(self):
        """Rails convenience: Analytics processing"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("1GB")
                .timeout(300)
                .pubsub_trigger("processEvents", "analytics-events")
                .scheduled_function("generateReports", "0 6 * * *")
                .dependency("@google-cloud/bigquery", "latest")
                .label("type", "analytics"))
    
    # ========== Environment-Specific Configurations ==========
    
    def development_functions(self):
        """Rails convenience: Development environment"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("128MB")
                .timeout(60)
                .max_instances(10)
                .cors(True)
                .ingress("ALLOW_ALL")
                .label("environment", "development")
                .label("cost_optimized", "true"))
    
    def staging_functions(self):
        """Rails convenience: Staging environment"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("256MB")
                .timeout(120)
                .max_instances(50)
                .cors(True)
                .require_authentication()
                .label("environment", "staging")
                .label("testing", "true"))
    
    def production_functions(self):
        """Rails convenience: Production environment"""
        return (self.nodejs18()
                .region("us-central1")
                .memory("512MB")
                .timeout(300)
                .max_instances(1000)
                .min_instances(1)
                .require_authentication()
                .ingress("ALLOW_INTERNAL_AND_GCLB")
                .egress("PRIVATE_RANGES_ONLY")
                .label("environment", "production")
                .label("high_availability", "true"))
    
    # ========== Labels and Metadata ==========
    
    def label(self, key: str, value: str):
        """Add a label to the functions"""
        self.functions_labels[key] = value
        return self
    
    def labels(self, labels_dict: Dict[str, str]):
        """Add multiple labels to the functions"""
        self.functions_labels.update(labels_dict)
        return self
    
    def annotation(self, key: str, value: str):
        """Add an annotation to the functions"""
        self.functions_annotations[key] = value
        return self
    
    def annotations(self, annotations_dict: Dict[str, str]):
        """Add multiple annotations to the functions"""
        self.functions_annotations.update(annotations_dict)
        return self
    
    # ========== Utility Methods ==========
    
    def get_function_count(self) -> int:
        """Get the number of configured functions"""
        return len(self.functions)
    
    def get_function_types(self) -> Dict[str, int]:
        """Get count of functions by type"""
        types = {}
        for func in self.functions:
            func_type = func.get("type", "unknown")
            types[func_type] = types.get(func_type, 0) + 1
        return types
    
    def has_http_functions(self) -> bool:
        """Check if HTTP functions are configured"""
        return any(func.get("type") == "http" for func in self.functions)
    
    def has_trigger_functions(self) -> bool:
        """Check if trigger functions are configured"""
        trigger_types = ["firestore", "storage", "auth", "pubsub"]
        return any(func.get("type") in trigger_types for func in self.functions)
    
    def has_scheduled_functions(self) -> bool:
        """Check if scheduled functions are configured"""
        return any(func.get("type") == "scheduled" for func in self.functions)
    
    def is_production_ready(self) -> bool:
        """Check if functions are configured for production"""
        return (self.get_function_count() > 0 and 
                self.default_memory != "128MB" and
                self.default_timeout >= 60 and
                self.firebase_project_id is not None)
    
    def get_functions_type(self) -> str:
        """Get functions type from configuration"""
        return self._get_functions_type_from_config()