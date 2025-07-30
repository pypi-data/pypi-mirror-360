"""
Cloudflare Workers Resource

Rails-like interface for managing Cloudflare Workers (Edge Functions).
Provides chainable methods for easy configuration and deployment.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.workers_manager import WorkersManager


class Workers(BaseCloudflareResource):
    """
    Cloudflare Workers resource with Rails-like simplicity.

    Examples:
        # Simple API endpoint
        worker = (Cloudflare.Workers("api-endpoint")
                  .script("./worker.js")
                  .route("api.myapp.com/*")
                  .create())

        # Worker with environment variables
        auth_worker = (Cloudflare.Workers("auth-service")
                       .script("./auth-worker.js")
                       .env_var("JWT_SECRET", "your-secret")
                       .env_var("API_URL", "https://api.example.com")
                       .route("auth.myapp.com/*")
                       .create())

        # Worker with KV namespace
        cache_worker = (Cloudflare.Workers("cache-worker")
                        .script("./cache.js")
                        .kv_namespace("CACHE", "my-cache-namespace")
                        .route("cache.myapp.com/*")
                        .create())
    """

    def __init__(self, name: str):
        """
        Initialize Workers resource

        Args:
            name: The worker name
        """
        super().__init__(name)
        self.worker_name = name
        self.script_content = None
        self.script_file = None
        self.routes = []
        self.env_vars = {}
        self.kv_namespaces = {}
        self.secrets = {}
        self.compatibility_date = None
        self.compatibility_flags = []
        self.cron_triggers = []

    def _initialize_managers(self):
        """Initialize Workers-specific managers"""
        self.workers_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.workers_manager = WorkersManager()

    def script(self, script_path_or_content: str) -> 'Workers':
        """
        Set the worker script from file or content

        Args:
            script_path_or_content: Path to script file or script content

        Returns:
            Workers: Self for method chaining
        """
        if script_path_or_content.startswith('./') or script_path_or_content.endswith('.js'):
            # Treat as file path
            self.script_file = script_path_or_content
        else:
            # Treat as content
            self.script_content = script_path_or_content
        return self

    def route(self, pattern: str, zone_name: Optional[str] = None) -> 'Workers':
        """
        Add a route pattern for the worker

        Args:
            pattern: Route pattern (e.g., "api.example.com/*")
            zone_name: Zone name (optional, will be inferred from pattern)

        Returns:
            Workers: Self for method chaining
        """
        self.routes.append({
            'pattern': pattern,
            'zone_name': zone_name
        })
        return self

    def env_var(self, name: str, value: str) -> 'Workers':
        """
        Add an environment variable

        Args:
            name: Variable name
            value: Variable value

        Returns:
            Workers: Self for method chaining
        """
        self.env_vars[name] = value
        return self

    def secret(self, name: str, value: str) -> 'Workers':
        """
        Add a secret (encrypted environment variable)

        Args:
            name: Secret name
            value: Secret value

        Returns:
            Workers: Self for method chaining
        """
        self.secrets[name] = value
        return self

    def kv_namespace(self, binding_name: str, namespace_id_or_name: str) -> 'Workers':
        """
        Bind a KV namespace to the worker

        Args:
            binding_name: Name to use in worker code
            namespace_id_or_name: KV namespace ID or name

        Returns:
            Workers: Self for method chaining
        """
        self.kv_namespaces[binding_name] = namespace_id_or_name
        return self

    def compatibility_date(self, date: str) -> 'Workers':
        """
        Set compatibility date

        Args:
            date: Compatibility date (YYYY-MM-DD format)

        Returns:
            Workers: Self for method chaining
        """
        self.compatibility_date = date
        return self

    def compatibility_flag(self, flag: str) -> 'Workers':
        """
        Add compatibility flag

        Args:
            flag: Compatibility flag name

        Returns:
            Workers: Self for method chaining
        """
        self.compatibility_flags.append(flag)
        return self

    def cron_trigger(self, schedule: str) -> 'Workers':
        """
        Add a cron trigger

        Args:
            schedule: Cron schedule expression

        Returns:
            Workers: Self for method chaining
        """
        self.cron_triggers.append(schedule)
        return self

    # Convenience methods for common patterns
    def api_endpoint(self, domain: str, script_path: str) -> 'Workers':
        """
        Quick setup for an API endpoint

        Args:
            domain: Domain for the API
            script_path: Path to the worker script

        Returns:
            Workers: Self for method chaining
        """
        return self.script(script_path).route(f"{domain}/*")

    def static_site_handler(self, domain: str, script_path: str) -> 'Workers':
        """
        Quick setup for static site handling

        Args:
            domain: Domain for the site
            script_path: Path to the worker script

        Returns:
            Workers: Self for method chaining
        """
        return self.script(script_path).route(f"{domain}/*")

    def auth_middleware(self, domain: str, script_path: str, jwt_secret: str) -> 'Workers':
        """
        Quick setup for authentication middleware

        Args:
            domain: Domain to protect
            script_path: Path to the auth worker script
            jwt_secret: JWT secret for token validation

        Returns:
            Workers: Self for method chaining
        """
        return (self.script(script_path)
                .route(f"{domain}/*")
                .secret("JWT_SECRET", jwt_secret))

    def cache_worker(self, domain: str, script_path: str, kv_namespace: str) -> 'Workers':
        """
        Quick setup for caching worker

        Args:
            domain: Domain for caching
            script_path: Path to the cache worker script
            kv_namespace: KV namespace for cache storage

        Returns:
            Workers: Self for method chaining
        """
        return (self.script(script_path)
                .route(f"{domain}/*")
                .kv_namespace("CACHE", kv_namespace))

    def scheduled_worker(self, script_path: str, schedule: str) -> 'Workers':
        """
        Quick setup for scheduled worker

        Args:
            script_path: Path to the worker script
            schedule: Cron schedule expression

        Returns:
            Workers: Self for method chaining
        """
        return self.script(script_path).cron_trigger(schedule)

    def preview(self) -> Dict[str, Any]:
        """Preview the worker configuration"""
        self._ensure_authenticated()

        script_source = "inline content" if self.script_content else self.script_file

        return self._format_response("preview", {
            "worker_name": self.worker_name,
            "script_source": script_source,
            "routes": self.routes,
            "env_vars": list(self.env_vars.keys()),
            "secrets": list(self.secrets.keys()),
            "kv_namespaces": self.kv_namespaces,
            "cron_triggers": self.cron_triggers,
            "compatibility_date": self.compatibility_date,
            "compatibility_flags": self.compatibility_flags
        })

    def create(self) -> Dict[str, Any]:
        """Deploy the worker"""
        self._ensure_authenticated()

        if not self.script_content and not self.script_file:
            raise ValueError("Worker script is required. Use .script() method to set it.")

        try:
            # Load script content if file path provided
            if self.script_file:
                try:
                    with open(self.script_file, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                except FileNotFoundError:
                    raise ValueError(f"Script file not found: {self.script_file}")
            else:
                script_content = self.script_content

            worker_config = {
                'name': self.worker_name,
                'script': script_content,
                'env_vars': self.env_vars,
                'secrets': self.secrets,
                'kv_namespaces': self.kv_namespaces,
                'compatibility_date': self.compatibility_date,
                'compatibility_flags': self.compatibility_flags
            }

            # Deploy the worker
            result = self.workers_manager.deploy_worker(worker_config)

            # Set up routes
            route_results = []
            for route in self.routes:
                route_result = self.workers_manager.create_route(
                    self.worker_name,
                    route['pattern'],
                    route.get('zone_name')
                )
                route_results.append(route_result)

            # Set up cron triggers
            cron_results = []
            for schedule in self.cron_triggers:
                cron_result = self.workers_manager.create_cron_trigger(
                    self.worker_name,
                    schedule
                )
                cron_results.append(cron_result)

            return self._format_response("create", {
                "worker": result,
                "routes": route_results,
                "cron_triggers": cron_results
            })

        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete the worker and its routes"""
        self._ensure_authenticated()

        try:
            result = self.workers_manager.delete_worker(self.worker_name)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get worker status and metrics"""
        self._ensure_authenticated()

        try:
            status = self.workers_manager.get_worker_status(self.worker_name)
            return self._format_response("status", status)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def logs(self, limit: int = 100) -> Dict[str, Any]:
        """Get worker logs"""
        self._ensure_authenticated()

        try:
            logs = self.workers_manager.get_worker_logs(self.worker_name, limit)
            return self._format_response("logs", logs)
        except Exception as e:
            return self._format_error_response("logs", str(e))

    def update(self) -> Dict[str, Any]:
        """Update the worker with current configuration"""
        self._ensure_authenticated()

        try:
            # This is essentially the same as create for workers
            return self.create()
        except Exception as e:
            return self._format_error_response("update", str(e))

    def tail(self) -> Dict[str, Any]:
        """Start tailing worker logs (returns setup info)"""
        self._ensure_authenticated()

        return self._format_response("tail", {
            "worker_name": self.worker_name,
            "message": "Use the Cloudflare dashboard or wrangler CLI for real-time log tailing",
            "dashboard_url": f"https://dash.cloudflare.com/workers/view/{self.worker_name}",
            "cli_command": f"wrangler tail {self.worker_name}"
        })
