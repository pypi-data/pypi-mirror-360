"""
GCP Cloud Functions Configuration Mixin

Chainable configuration methods for Google Cloud Functions.
Provides Rails-like method chaining for fluent function configuration.
"""

from typing import Dict, Any, List, Optional


class CloudFunctionsConfigurationMixin:
    """
    Mixin for Cloud Functions configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Runtime and execution settings
    - Trigger configuration
    - Scaling and performance settings
    - Security and access control
    - Environment variables and labels
    """
    
    def function(self, name: str):
        """Set function name (Rails-like method chaining)"""
        self.function_name = name
        return self
        
    def runtime(self, runtime_version: str):
        """Set runtime (e.g., 'python39', 'nodejs16', 'go119')"""
        if not self._is_valid_runtime(runtime_version):
            print(f"⚠️  Warning: Unusual runtime '{runtime_version}' - verify this is supported")
        self.function_runtime = runtime_version
        return self
        
    def region(self, region_name: str):
        """Set deployment region"""
        if not self._is_valid_region(region_name):
            print(f"⚠️  Warning: Unusual region '{region_name}' - verify this is correct")
        self.function_region = region_name
        return self
        
    def entry_point(self, entry_point_name: str):
        """Set entry point function name"""
        self.function_entry_point = entry_point_name
        return self
        
    def source(self, source_path: str):
        """Set source code path"""
        self.source_path = source_path
        return self
        
    def memory(self, memory_size: str):
        """Set memory allocation (e.g., '256MB', '1GB')"""
        if not self._is_valid_memory(memory_size):
            raise ValueError(f"Invalid memory allocation: {memory_size}")
        self.function_memory = memory_size
        return self
        
    def timeout(self, timeout_duration: str):
        """Set function timeout (e.g., '60s', '5m')"""
        if not self._is_valid_timeout(timeout_duration):
            raise ValueError(f"Invalid timeout: {timeout_duration}")
        self.function_timeout = timeout_duration
        return self
        
    def max_instances(self, instances: int):
        """Set maximum concurrent instances"""
        if instances < 1:
            raise ValueError("Max instances must be at least 1")
        self.max_instances = instances
        return self
        
    def min_instances(self, instances: int):
        """Set minimum instances (keep warm)"""
        if instances < 0:
            raise ValueError("Min instances cannot be negative")
        self.min_instances = instances
        return self
        
    def environment(self, env_vars: Dict[str, str]):
        """Set environment variables"""
        self.environment_variables.update(env_vars)
        return self
        
    def env(self, key: str, value: str):
        """Set individual environment variable (Rails convenience)"""
        self.environment_variables[key] = value
        return self
        
    def service_account(self, email: str):
        """Set service account for function execution"""
        self.service_account = email
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add labels to the function"""
        self.function_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label (Rails convenience)"""
        self.function_labels[key] = value
        return self
        
    def description(self, description: str):
        """Set function description"""
        self.description = description
        return self
        
    # Trigger configuration methods
    def trigger(self, trigger_type: str, **kwargs):
        """Configure function trigger with flexible options"""
        if not self._is_valid_trigger_type(trigger_type):
            raise ValueError(f"Invalid trigger type: {trigger_type}")
            
        self.trigger_type = trigger_type
        self.trigger_config = kwargs
        
        # Set function type based on common trigger patterns
        if trigger_type == "http":
            self.function_type = "api"
        elif trigger_type in ["storage", "pubsub", "firestore"]:
            self.function_type = "processor"
        elif trigger_type == "schedule":
            self.function_type = "scheduled"
            
        return self
        
    def http_trigger(self):
        """Configure HTTP trigger (Rails convention)"""
        return self.trigger("http")
        
    def storage_trigger(self, bucket: str, event_type: str = "google.storage.object.finalize"):
        """Configure Cloud Storage trigger"""
        return self.trigger("storage", bucket=bucket, event_type=event_type)
        
    def pubsub_trigger(self, topic: str):
        """Configure Pub/Sub trigger"""
        return self.trigger("pubsub", topic=topic)
        
    def firestore_trigger(self, document: str, event_type: str = "providers/cloud.firestore/eventTypes/document.create"):
        """Configure Firestore trigger"""
        return self.trigger("firestore", document=document, event_type=event_type)
        
    def schedule_trigger(self, schedule: str):
        """Configure scheduled trigger (cron-like)"""
        topic_name = f"{self.function_name}-schedule"
        return self.trigger("schedule", topic=topic_name, schedule=schedule)
        
    # Security and access control
    def public_access(self):
        """Allow public access (Rails convention)"""
        self.ingress_settings = "ALLOW_ALL"
        return self
        
    def internal_only(self):
        """Allow internal access only"""
        self.ingress_settings = "ALLOW_INTERNAL_ONLY"
        return self
        
    def load_balancer_only(self):
        """Allow access from load balancer only"""
        self.ingress_settings = "ALLOW_INTERNAL_AND_GCLB"
        return self
        
    def private(self):
        """Make function private (Rails convention)"""
        return self.internal_only()
        
    # Runtime convenience methods
    def python(self, version: str = "39"):
        """Set Python runtime (Rails convention)"""
        self.function_runtime = f"python{version}"
        return self
        
    def nodejs(self, version: str = "16"):
        """Set Node.js runtime (Rails convention)"""
        self.function_runtime = f"nodejs{version}"
        return self
        
    def go(self, version: str = "119"):
        """Set Go runtime (Rails convention)"""
        self.function_runtime = f"go{version}"
        return self
        
    def java(self, version: str = "11"):
        """Set Java runtime (Rails convention)"""
        self.function_runtime = f"java{version}"
        return self
        
    # Scaling convenience methods
    def scale_to_zero(self):
        """Configure to scale to zero when not used"""
        self.min_instances = 0
        return self
        
    def keep_warm(self, instances: int = 1):
        """Keep minimum instances warm"""
        self.min_instances = instances
        return self
        
    def high_availability(self):
        """Configure for high availability"""
        self.min_instances = 2
        self.max_instances = 100
        return self
        
    def auto_scale(self, min_instances: int = 0, max_instances: int = 100):
        """Configure auto-scaling parameters"""
        self.min_instances = min_instances
        self.max_instances = max_instances
        return self
        
    # Function type convenience methods
    def api_function(self):
        """Configure for API workloads (Rails convention)"""
        self.function_type = "api"
        self.function_memory = "512MB"
        self.function_timeout = "60s"
        self.max_instances = 100
        self.ingress_settings = "ALLOW_ALL"
        self.function_labels.update({
            "function_type": "api",
            "scaling": "demand"
        })
        return self
        
    def processor_function(self):
        """Configure for data processing workloads"""
        self.function_type = "processor"
        self.function_memory = "1GB"
        self.function_timeout = "540s"  # 9 minutes
        self.max_instances = 10
        self.ingress_settings = "ALLOW_INTERNAL_ONLY"
        self.function_labels.update({
            "function_type": "processor",
            "workload": "batch"
        })
        return self
        
    def webhook_function(self):
        """Configure for webhook workloads"""
        self.function_type = "webhook"
        self.function_memory = "256MB"
        self.function_timeout = "30s"
        self.max_instances = 50
        self.min_instances = 1  # Keep warm
        self.ingress_settings = "ALLOW_ALL"
        self.function_labels.update({
            "function_type": "webhook",
            "latency": "low"
        })
        return self
        
    def scheduled_function(self):
        """Configure for scheduled tasks"""
        self.function_type = "scheduled"
        self.function_memory = "512MB"
        self.function_timeout = "300s"  # 5 minutes
        self.max_instances = 1  # Only one instance
        self.ingress_settings = "ALLOW_INTERNAL_ONLY"
        self.function_labels.update({
            "function_type": "scheduled",
            "trigger": "cron"
        })
        return self
        
    def etl_function(self):
        """Configure for ETL workloads"""
        self.function_type = "etl"
        self.function_memory = "2GB"
        self.function_timeout = "540s"
        self.max_instances = 5
        self.ingress_settings = "ALLOW_INTERNAL_ONLY"
        self.function_labels.update({
            "function_type": "etl",
            "workload": "data-processing"
        })
        return self
        
    # Rails-like convenience methods
    def http(self):
        """Rails convenience: HTTP trigger with API optimizations"""
        return self.http_trigger().api_function()
        
    def webhook(self):
        """Rails convenience: Webhook with fast response optimizations"""
        return self.http_trigger().webhook_function()
        
    def processor(self):
        """Rails convenience: Data processor with higher memory"""
        return self.processor_function()
        
    def scheduled(self, schedule: str = "0 2 * * *"):
        """Rails convenience: Scheduled function (daily at 2 AM by default)"""
        return self.schedule_trigger(schedule).scheduled_function()
        
    def microservice(self):
        """Rails convenience: Microservice configuration"""
        return self.http_trigger().api_function().keep_warm(1)
        
    def batch_job(self):
        """Rails convenience: Batch processing job"""
        return self.processor_function().scale_to_zero()
        
    def cron_job(self, schedule: str = "0 0 * * *"):
        """Rails convenience: Cron job (daily at midnight by default)"""
        return self.schedule_trigger(schedule).scheduled_function()
        
    # Performance and resource optimization
    def fast_startup(self):
        """Optimize for fast startup times"""
        self.function_memory = "128MB"
        self.min_instances = 1
        return self
        
    def high_memory(self):
        """Configure for high memory workloads"""
        self.function_memory = "4GB"
        self.function_timeout = "540s"
        return self
        
    def low_latency(self):
        """Configure for low latency requirements"""
        self.min_instances = 2
        self.function_memory = "512MB"
        return self