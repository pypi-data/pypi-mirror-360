"""
Cloudflare KV Storage Resource

Rails-like interface for managing Cloudflare Workers KV edge key-value storage.
Provides chainable methods for easy namespace configuration and management.
"""

from typing import Dict, Any, Optional, List, Union
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.kv_storage_manager import KVStorageManager


class KVStorage(BaseCloudflareResource):
    """
    Cloudflare KV Storage resource with Rails-like simplicity.

    Examples:
        # Session storage
        sessions = (Cloudflare.KV("user-sessions")
                    .session_store()
                    .create())

        # Configuration cache
        config = (Cloudflare.KV("app-config")
                  .configuration_cache()
                  .create())

        # Feature flags
        flags = (Cloudflare.KV("feature-flags")
                 .feature_flags()
                 .create())
    """

    def __init__(self, namespace: str):
        """
        Initialize KV Storage resource for a namespace

        Args:
            namespace: The name of the KV namespace
        """
        super().__init__(namespace)
        self.namespace = namespace
        self._preview_mode = False
        self._bindings = []
        self._initial_data = {}
        self._ttl_seconds = None

    def _initialize_managers(self):
        """Initialize KV-specific managers"""
        self.kv_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.kv_manager = KVStorageManager()

    def preview_mode(self, enabled: bool = True) -> 'KVStorage':
        """
        Enable preview mode for testing

        Args:
            enabled: Whether to enable preview mode

        Returns:
            KVStorage: Self for method chaining
        """
        self._preview_mode = enabled
        return self

    def bind_to_worker(self, worker_name: str, binding_name: str = None) -> 'KVStorage':
        """
        Bind KV namespace to a Worker

        Args:
            worker_name: Name of the Worker
            binding_name: Binding name (defaults to namespace name)

        Returns:
            KVStorage: Self for method chaining
        """
        self._bindings.append({
            "worker": worker_name,
            "binding": binding_name or self.namespace
        })
        return self

    def initial_data(self, data: Dict[str, Union[str, Dict, List]]) -> 'KVStorage':
        """
        Set initial data for the namespace

        Args:
            data: Initial key-value pairs

        Returns:
            KVStorage: Self for method chaining
        """
        self._initial_data.update(data)
        return self

    def default_ttl(self, seconds: int) -> 'KVStorage':
        """
        Set default TTL for keys

        Args:
            seconds: TTL in seconds (minimum 60)

        Returns:
            KVStorage: Self for method chaining
        """
        if seconds < 60:
            raise ValueError("TTL must be at least 60 seconds")
        self._ttl_seconds = seconds
        return self

    # Rails-like convenience methods
    def session_store(self, ttl_hours: int = 24) -> 'KVStorage':
        """
        Configure namespace for session storage

        Args:
            ttl_hours: Session TTL in hours

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_hours * 3600)

    def configuration_cache(self, ttl_minutes: int = 30) -> 'KVStorage':
        """
        Configure namespace for configuration caching

        Args:
            ttl_minutes: Cache TTL in minutes

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_minutes * 60)

    def feature_flags(self) -> 'KVStorage':
        """
        Configure namespace for feature flags (no TTL)

        Returns:
            KVStorage: Self for method chaining
        """
        # Feature flags typically don't expire
        return self

    def api_cache(self, ttl_minutes: int = 15) -> 'KVStorage':
        """
        Configure namespace for API response caching

        Args:
            ttl_minutes: Cache TTL in minutes

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_minutes * 60)

    def user_preferences(self) -> 'KVStorage':
        """
        Configure namespace for user preferences (no TTL)

        Returns:
            KVStorage: Self for method chaining
        """
        # User preferences typically don't expire
        return self

    def rate_limiting(self, ttl_minutes: int = 60) -> 'KVStorage':
        """
        Configure namespace for rate limiting

        Args:
            ttl_minutes: Rate limit window in minutes

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_minutes * 60)

    def analytics_buffer(self, ttl_hours: int = 1) -> 'KVStorage':
        """
        Configure namespace for analytics data buffering

        Args:
            ttl_hours: Buffer TTL in hours

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_hours * 3600)

    def geolocation_cache(self, ttl_days: int = 7) -> 'KVStorage':
        """
        Configure namespace for geolocation data caching

        Args:
            ttl_days: Cache TTL in days

        Returns:
            KVStorage: Self for method chaining
        """
        return self.default_ttl(ttl_days * 24 * 3600)

    def preview(self) -> Dict[str, Any]:
        """Preview KV namespace configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "namespace": self.namespace,
            "preview_mode": self._preview_mode
        }

        if self._ttl_seconds:
            preview_data["default_ttl_seconds"] = self._ttl_seconds

        if self._bindings:
            preview_data["worker_bindings"] = self._bindings

        if self._initial_data:
            preview_data["initial_data_keys"] = list(self._initial_data.keys())
            preview_data["initial_data_count"] = len(self._initial_data)

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create KV namespace"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.create_namespace(
                namespace=self.namespace,
                preview_mode=self._preview_mode,
                bindings=self._bindings,
                initial_data=self._initial_data,
                default_ttl=self._ttl_seconds
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete KV namespace"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.delete_namespace(self.namespace)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get KV namespace status"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.get_namespace_status(self.namespace)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def put_value(self, key: str, value: Union[str, Dict, List], ttl: Optional[int] = None) -> Dict[str, Any]:
        """Put value in KV store"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.put_value(
                namespace=self.namespace,
                key=key,
                value=value,
                ttl=ttl or self._ttl_seconds
            )
            return self._format_response("put", result)
        except Exception as e:
            return self._format_error_response("put", str(e))

    def get_value(self, key: str) -> Dict[str, Any]:
        """Get value from KV store"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.get_value(self.namespace, key)
            return self._format_response("get", result)
        except Exception as e:
            return self._format_error_response("get", str(e))

    def delete_value(self, key: str) -> Dict[str, Any]:
        """Delete value from KV store"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.delete_value(self.namespace, key)
            return self._format_response("delete_value", result)
        except Exception as e:
            return self._format_error_response("delete_value", str(e))

    def list_keys(self, prefix: str = "") -> Dict[str, Any]:
        """List keys in KV namespace"""
        self._ensure_authenticated()
        
        try:
            result = self.kv_manager.list_keys(self.namespace, prefix)
            return self._format_response("list_keys", result)
        except Exception as e:
            return self._format_error_response("list_keys", str(e))

    def help(self) -> str:
        """Return help information for KVStorage resource"""
        return f"""
KVStorage Resource Help
=======================

Namespace: {self.namespace}
Provider: Cloudflare

Configuration:
- preview_mode(enabled): Enable preview mode for testing
- bind_to_worker(worker, binding): Bind namespace to Worker
- initial_data(data): Set initial key-value pairs
- default_ttl(seconds): Set default TTL for keys

Convenience Methods:
- session_store(ttl_hours): Configure for session storage
- configuration_cache(ttl_minutes): Configure for configuration caching
- feature_flags(): Configure for feature flags
- api_cache(ttl_minutes): Configure for API response caching
- user_preferences(): Configure for user preferences
- rate_limiting(ttl_minutes): Configure for rate limiting
- analytics_buffer(ttl_hours): Configure for analytics buffering
- geolocation_cache(ttl_days): Configure for geolocation caching

Methods:
- preview(): Preview namespace configuration
- create(): Create namespace
- delete(): Delete namespace
- status(): Get namespace status
- put_value(key, value, ttl): Put value in KV store
- get_value(key): Get value from KV store
- delete_value(key): Delete value from KV store
- list_keys(prefix): List keys in namespace
        """ 