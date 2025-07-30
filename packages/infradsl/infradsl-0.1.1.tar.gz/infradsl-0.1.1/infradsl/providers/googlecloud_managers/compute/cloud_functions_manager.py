"""
Cloud Functions Manager - Rails-like serverless function operations

This module provides Rails-like conventions for Google Cloud Functions operations,
including function deployment, trigger configuration, and lifecycle management.
"""

import os
import json
import time
import zipfile
import tempfile
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from google.cloud import functions_v1
from google.cloud.exceptions import NotFound, Conflict
from ..status_reporter import GcpStatusReporter


class FunctionConfig(BaseModel):
    """Configuration for Cloud Function"""
    function_name: str
    project_id: Optional[str] = None
    region: str = "us-central1"  # Rails-like default
    runtime: str = "python39"  # Modern default
    entry_point: str = "main"  # Convention over configuration
    source_path: Optional[str] = None
    source_archive_url: Optional[str] = None

    # Trigger configuration
    trigger_type: str = "http"  # http, storage, pubsub, firestore, etc.
    trigger_config: Dict[str, Any] = {}

    # Resource configuration
    memory: str = "256MB"  # Rails-like sensible default
    timeout: str = "60s"  # Default timeout
    max_instances: Optional[int] = None
    min_instances: int = 0  # Scale to zero by default

    # Environment and security
    environment_variables: Dict[str, str] = {}
    service_account: Optional[str] = None
    ingress_settings: str = "ALLOW_ALL"  # ALLOW_ALL, ALLOW_INTERNAL_ONLY, ALLOW_INTERNAL_AND_GCLB

    # Rails-like function types
    function_type: str = "general"  # general, api, processor, scheduled, webhook

    # Labels and metadata
    labels: Optional[Dict[str, str]] = None
    description: Optional[str] = None


class CloudFunctionsManager:
    """
    Manages Google Cloud Functions operations with Rails-like conventions.

    Provides intelligent defaults, convention-based configurations, and
    developer-friendly abstractions for serverless function deployment.
    """

    def __init__(self, gcp_client):
        self.gcp_client = gcp_client
        self.status_reporter = GcpStatusReporter()
        self._client = None

    @property
    def functions_client(self) -> functions_v1.CloudFunctionsServiceClient:
        """Get authenticated Cloud Functions client"""
        if self._client is None:
            self._client = functions_v1.CloudFunctionsServiceClient(
                credentials=self.gcp_client.credentials
            )
        return self._client

    @property
    def project_id(self) -> str:
        """Get the current project ID"""
        return self.gcp_client.project

    def deploy_function(self, config: FunctionConfig) -> Dict[str, Any]:
        """
        Deploy a Cloud Function with Rails-like conventions.

        Args:
            config: Function configuration

        Returns:
            Dict containing function information
        """
        try:
            # Set project if not specified
            if not config.project_id:
                config.project_id = self.project_id

            function_name = f"projects/{config.project_id}/locations/{config.region}/functions/{config.function_name}"

            # Check if function exists
            try:
                existing_function = self.functions_client.get_function(name=function_name)
                self.status_reporter.info(f"⚡ Function '{config.function_name}' already exists - updating...")
                return self._update_function(config, existing_function)
            except NotFound:
                pass  # Function doesn't exist, create it

            # Create function
            self.status_reporter.info(f"⚡ Creating Cloud Function '{config.function_name}'...")

            location_path = f"projects/{config.project_id}/locations/{config.region}"

            # Build function configuration
            function_config = self._build_function_config(config)

            # Create the function
            operation = self.functions_client.create_function(
                parent=location_path,
                function=function_config
            )

            # Wait for operation to complete
            self.status_reporter.info("🔄 Deploying function... (this may take a few minutes)")
            result = self._wait_for_operation(operation)

            self.status_reporter.success(f"✅ Function '{config.function_name}' deployed successfully")
            return self._function_to_dict(result)

        except Exception as e:
            self.status_reporter.error(f"❌ Failed to deploy function '{config.function_name}': {str(e)}")
            raise

    def get_function_info(self, function_name: str, region: str = "us-central1") -> Dict[str, Any]:
        """Get information about a function"""
        try:
            full_name = f"projects/{self.project_id}/locations/{region}/functions/{function_name}"
            function = self.functions_client.get_function(name=full_name)
            return self._function_to_dict(function)
        except NotFound:
            raise ValueError(f"Function '{function_name}' not found")

    def delete_function(self, function_name: str, region: str = "us-central1") -> bool:
        """Delete a function"""
        try:
            full_name = f"projects/{self.project_id}/locations/{region}/functions/{function_name}"
            operation = self.functions_client.delete_function(name=full_name)

            self.status_reporter.info(f"🗑️ Deleting function '{function_name}'...")
            self._wait_for_operation(operation)

            self.status_reporter.success(f"✅ Function '{function_name}' deleted")
            return True
        except NotFound:
            self.status_reporter.warning(f"⚠️ Function '{function_name}' not found")
            return False
        except Exception as e:
            self.status_reporter.error(f"❌ Failed to delete function '{function_name}': {str(e)}")
            raise

    def _update_function(self, config: FunctionConfig, existing_function) -> Dict[str, Any]:
        """Update an existing function"""
        try:
            # Build updated function configuration
            function_config = self._build_function_config(config)
            function_config.name = existing_function.name

            # Update the function
            operation = self.functions_client.update_function(function=function_config)

            self.status_reporter.info("🔄 Updating function... (this may take a few minutes)")
            result = self._wait_for_operation(operation)

            self.status_reporter.success(f"✅ Function '{config.function_name}' updated successfully")
            return self._function_to_dict(result)

        except Exception as e:
            self.status_reporter.error(f"❌ Failed to update function '{config.function_name}': {str(e)}")
            raise

    def _build_function_config(self, config: FunctionConfig) -> functions_v1.CloudFunction:
        """Build Cloud Function configuration from config"""
        function = functions_v1.CloudFunction()

        # Basic configuration
        function.name = f"projects/{config.project_id}/locations/{config.region}/functions/{config.function_name}"
        function.description = config.description or f"Rails-generated {config.function_type} function"
        function.runtime = config.runtime
        function.entry_point = config.entry_point
        function.timeout = config.timeout
        function.available_memory_mb = self._parse_memory(config.memory)

        # Source configuration
        if config.source_path:
            # Create source archive from local path
            function.source_archive_url = self._create_source_archive(config.source_path, config.function_name)
        elif config.source_archive_url:
            function.source_archive_url = config.source_archive_url
        else:
            raise ValueError("Either source_path or source_archive_url must be provided")

        # Configure trigger
        self._configure_trigger(function, config)

        # Environment variables
        if config.environment_variables:
            function.environment_variables = config.environment_variables

        # Service account
        if config.service_account:
            function.service_account_email = config.service_account

        # Scaling configuration
        if config.max_instances:
            function.max_instances = config.max_instances
        if config.min_instances:
            function.min_instances = config.min_instances

        # Ingress settings
        function.ingress_settings = getattr(
            functions_v1.CloudFunction.IngressSettings,
            config.ingress_settings
        )

        # Labels
        if config.labels:
            function.labels = config.labels

        return function

    def _configure_trigger(self, function: functions_v1.CloudFunction, config: FunctionConfig):
        """Configure function trigger based on type"""
        if config.trigger_type == "http":
            function.https_trigger = functions_v1.HttpsTrigger()

        elif config.trigger_type == "storage":
            event_trigger = functions_v1.EventTrigger()
            bucket = config.trigger_config.get("bucket")
            event_type = config.trigger_config.get("event_type", "google.storage.object.finalize")

            if not bucket:
                raise ValueError("Storage trigger requires 'bucket' in trigger_config")

            event_trigger.event_type = event_type
            event_trigger.resource = f"projects/{config.project_id}/buckets/{bucket}"
            function.event_trigger = event_trigger

        elif config.trigger_type == "pubsub":
            event_trigger = functions_v1.EventTrigger()
            topic = config.trigger_config.get("topic")

            if not topic:
                raise ValueError("Pub/Sub trigger requires 'topic' in trigger_config")

            event_trigger.event_type = "google.pubsub.topic.publish"
            event_trigger.resource = f"projects/{config.project_id}/topics/{topic}"
            function.event_trigger = event_trigger

        elif config.trigger_type == "firestore":
            event_trigger = functions_v1.EventTrigger()
            document = config.trigger_config.get("document")
            event_type = config.trigger_config.get("event_type", "providers/cloud.firestore/eventTypes/document.create")

            if not document:
                raise ValueError("Firestore trigger requires 'document' in trigger_config")

            event_trigger.event_type = event_type
            event_trigger.resource = f"projects/{config.project_id}/databases/(default)/documents/{document}"
            function.event_trigger = event_trigger

        else:
            raise ValueError(f"Unsupported trigger type: {config.trigger_type}")

    def _create_source_archive(self, source_path: str, function_name: str) -> str:
        """Create source archive from local directory and upload to Cloud Storage"""
        # This is a simplified version - in production you'd want to:
        # 1. Create a zip file from the source directory
        # 2. Upload to a Cloud Storage bucket
        # 3. Return the gs:// URL

        # For now, we'll create a basic implementation
        if not os.path.exists(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")

        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_path)
                        zipf.write(file_path, arcname)

            # Upload to Cloud Storage bucket (simplified - would need proper implementation)
            bucket_name = f"{self.project_id}-cloud-functions-source"
            blob_name = f"{function_name}-{int(time.time())}.zip"

            # Return the expected Cloud Storage URL
            return f"gs://{bucket_name}/{blob_name}"

    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to MB integer"""
        memory_str = memory_str.upper()
        if memory_str.endswith('MB'):
            return int(memory_str[:-2])
        elif memory_str.endswith('GB'):
            return int(memory_str[:-2]) * 1024
        else:
            return int(memory_str)  # Assume MB if no unit

    def _wait_for_operation(self, operation, timeout: int = 600) -> Any:
        """Wait for long-running operation to complete"""
        start_time = time.time()

        while not operation.done():
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")

            time.sleep(5)
            operation = self.functions_client.get_operation(name=operation.name)

        if operation.error:
            raise Exception(f"Operation failed: {operation.error}")

        return operation.response

    def _function_to_dict(self, function: functions_v1.CloudFunction) -> Dict[str, Any]:
        """Convert Cloud Function to dictionary"""
        return {
            "function_name": function.name.split('/')[-1],
            "project": function.name.split('/')[1],
            "region": function.name.split('/')[3],
            "runtime": function.runtime,
            "status": function.status.name if function.status else "UNKNOWN",
            "entry_point": function.entry_point,
            "timeout": function.timeout,
            "memory_mb": function.available_memory_mb,
            "max_instances": function.max_instances,
            "min_instances": function.min_instances,
            "trigger_type": self._get_trigger_type(function),
            "https_url": function.https_trigger.url if function.https_trigger else None,
            "service_account": function.service_account_email,
            "labels": dict(function.labels) if function.labels else {},
            "update_time": function.update_time.isoformat() if function.update_time else None,
        }

    def _get_trigger_type(self, function: functions_v1.CloudFunction) -> str:
        """Determine trigger type from function configuration"""
        if function.https_trigger:
            return "http"
        elif function.event_trigger:
            if "storage" in function.event_trigger.event_type:
                return "storage"
            elif "pubsub" in function.event_trigger.event_type:
                return "pubsub"
            elif "firestore" in function.event_trigger.event_type:
                return "firestore"
            else:
                return "event"
        else:
            return "unknown"

    def get_smart_function_configuration(self, function_type: str = "general") -> Dict[str, Any]:
        """Get smart configuration recommendations for different function types"""
        configurations = {
            "api": {
                "memory": "512MB",
                "timeout": "60s",
                "max_instances": 100,
                "min_instances": 0,
                "ingress_settings": "ALLOW_ALL",
                "suggested_labels": {"function_type": "api", "scaling": "demand"}
            },
            "processor": {
                "memory": "1GB",
                "timeout": "540s",  # 9 minutes
                "max_instances": 10,
                "min_instances": 0,
                "ingress_settings": "ALLOW_INTERNAL_ONLY",
                "suggested_labels": {"function_type": "processor", "workload": "batch"}
            },
            "webhook": {
                "memory": "256MB",
                "timeout": "30s",
                "max_instances": 50,
                "min_instances": 1,  # Keep warm for webhooks
                "ingress_settings": "ALLOW_ALL",
                "suggested_labels": {"function_type": "webhook", "latency": "low"}
            },
            "scheduled": {
                "memory": "512MB",
                "timeout": "300s",  # 5 minutes
                "max_instances": 1,  # Only one instance for scheduled tasks
                "min_instances": 0,
                "ingress_settings": "ALLOW_INTERNAL_ONLY",
                "suggested_labels": {"function_type": "scheduled", "trigger": "cron"}
            },
            "etl": {
                "memory": "2GB",
                "timeout": "540s",
                "max_instances": 5,
                "min_instances": 0,
                "ingress_settings": "ALLOW_INTERNAL_ONLY",
                "suggested_labels": {"function_type": "etl", "workload": "data-processing"}
            }
        }

        return configurations.get(function_type, configurations["api"])
