"""
Cloudflare Workers Manager

Handles Workers operations via Cloudflare API with error handling and validation.
"""

import json
from typing import Dict, Any, List, Optional
from ..cloudflare_resources.auth_service import CloudflareAuthenticationService


class WorkersManager:
    """Manager for Cloudflare Workers operations"""

    def __init__(self):
        self.auth_service = CloudflareAuthenticationService

    def _get_account_id(self) -> str:
        """
        Get account ID for Workers operations

        Returns:
            str: Account ID

        Raises:
            ValueError: If account not found
        """
        response = self.auth_service.make_request('GET', 'accounts')

        if not response.ok:
            raise ValueError(f"Failed to get accounts: {response.text}")

        data = response.json()
        if not data.get('success') or not data.get('result'):
            raise ValueError("No accounts found")

        # Use the first account
        return data['result'][0]['id']

    def deploy_worker(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a worker script

        Args:
            config: Worker configuration including script content

        Returns:
            Dict containing deployment result
        """
        account_id = self._get_account_id()
        worker_name = config['name']

        # Prepare the script content
        script_content = config['script']

        # Prepare metadata for environment variables and bindings
        metadata = {
            'compatibility_date': config.get('compatibility_date', '2023-05-18'),
            'compatibility_flags': config.get('compatibility_flags', [])
        }

        # Add environment variables
        if config.get('env_vars'):
            metadata['vars'] = config['env_vars']

        # Add KV namespace bindings
        if config.get('kv_namespaces'):
            kv_bindings = []
            for binding_name, namespace_id in config['kv_namespaces'].items():
                kv_bindings.append({
                    'name': binding_name,
                    'namespace_id': namespace_id,
                    'type': 'kv_namespace'
                })
            metadata['bindings'] = kv_bindings

        # Create multipart form data
        files = {
            'script': (f'{worker_name}.js', script_content, 'application/javascript'),
            'metadata': (None, json.dumps(metadata), 'application/json')
        }

        # Make the request without the default JSON content-type header
        headers = self.auth_service.get_headers()
        headers.pop('Content-Type', None)  # Remove JSON content-type for multipart

        response = self.auth_service.make_request(
            'PUT',
            f'accounts/{account_id}/workers/scripts/{worker_name}',
            files=files,
            headers=headers
        )

        if not response.ok:
            raise Exception(f"Failed to deploy worker: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Worker deployment failed: {error_msg}")

        # Handle secrets separately
        if config.get('secrets'):
            for secret_name, secret_value in config['secrets'].items():
                self.set_secret(worker_name, secret_name, secret_value)

        return {
            'worker_name': worker_name,
            'script_size': len(script_content),
            'deployed_on': result['result'].get('created_on'),
            'modified_on': result['result'].get('modified_on'),
            'etag': result['result'].get('etag')
        }

    def set_secret(self, worker_name: str, secret_name: str, secret_value: str) -> Dict[str, Any]:
        """
        Set a secret for a worker

        Args:
            worker_name: Name of the worker
            secret_name: Name of the secret
            secret_value: Value of the secret

        Returns:
            Dict containing result
        """
        account_id = self._get_account_id()

        response = self.auth_service.make_request(
            'PUT',
            f'accounts/{account_id}/workers/scripts/{worker_name}/secrets',
            json={
                'name': secret_name,
                'text': secret_value,
                'type': 'secret_text'
            }
        )

        if not response.ok:
            raise Exception(f"Failed to set secret: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to set worker secret")

        return {
            'secret_name': secret_name,
            'worker_name': worker_name,
            'set': True
        }

    def create_route(self, worker_name: str, pattern: str, zone_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a route for a worker

        Args:
            worker_name: Name of the worker
            pattern: Route pattern
            zone_name: Zone name (optional)

        Returns:
            Dict containing route creation result
        """
        # If zone_name not provided, try to extract from pattern
        if not zone_name and '.' in pattern:
            # Extract domain from pattern (e.g., "api.example.com/*" -> "example.com")
            domain_part = pattern.split('/')[0]
            parts = domain_part.split('.')
            if len(parts) >= 2:
                zone_name = '.'.join(parts[-2:])

        if not zone_name:
            raise ValueError("Zone name is required for route creation")

        # Get zone ID
        zone_response = self.auth_service.make_request('GET', f'zones?name={zone_name}')
        if not zone_response.ok:
            raise Exception(f"Failed to find zone: {zone_response.text}")

        zone_data = zone_response.json()
        if not zone_data.get('success') or not zone_data.get('result'):
            raise Exception(f"Zone not found: {zone_name}")

        zone_id = zone_data['result'][0]['id']

        # Create the route
        response = self.auth_service.make_request(
            'POST',
            f'zones/{zone_id}/workers/routes',
            json={
                'pattern': pattern,
                'script': worker_name
            }
        )

        if not response.ok:
            raise Exception(f"Failed to create route: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Route creation failed: {error_msg}")

        return {
            'route_id': result['result']['id'],
            'pattern': pattern,
            'worker_name': worker_name,
            'zone_name': zone_name
        }

    def create_cron_trigger(self, worker_name: str, schedule: str) -> Dict[str, Any]:
        """
        Create a cron trigger for a worker

        Args:
            worker_name: Name of the worker
            schedule: Cron schedule expression

        Returns:
            Dict containing cron trigger result
        """
        account_id = self._get_account_id()

        response = self.auth_service.make_request(
            'PUT',
            f'accounts/{account_id}/workers/scripts/{worker_name}/schedules',
            json={
                'cron': schedule
            }
        )

        if not response.ok:
            raise Exception(f"Failed to create cron trigger: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Cron trigger creation failed: {error_msg}")

        return {
            'worker_name': worker_name,
            'schedule': schedule,
            'created': True
        }

    def delete_worker(self, worker_name: str) -> Dict[str, Any]:
        """
        Delete a worker

        Args:
            worker_name: Name of the worker to delete

        Returns:
            Dict containing deletion result
        """
        account_id = self._get_account_id()

        response = self.auth_service.make_request(
            'DELETE',
            f'accounts/{account_id}/workers/scripts/{worker_name}'
        )

        if not response.ok:
            raise Exception(f"Failed to delete worker: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Worker deletion failed: {error_msg}")

        return {
            'worker_name': worker_name,
            'deleted': True
        }

    def get_worker_status(self, worker_name: str) -> Dict[str, Any]:
        """
        Get worker status and information

        Args:
            worker_name: Name of the worker

        Returns:
            Dict containing worker status
        """
        account_id = self._get_account_id()

        response = self.auth_service.make_request(
            'GET',
            f'accounts/{account_id}/workers/scripts/{worker_name}'
        )

        if not response.ok:
            if response.status_code == 404:
                return {
                    'worker_name': worker_name,
                    'exists': False,
                    'status': 'not_found'
                }
            raise Exception(f"Failed to get worker status: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to get worker status")

        worker_data = result['result']

        return {
            'worker_name': worker_name,
            'exists': True,
            'status': 'deployed',
            'created_on': worker_data.get('created_on'),
            'modified_on': worker_data.get('modified_on'),
            'etag': worker_data.get('etag'),
            'size': len(worker_data.get('script', ''))
        }

    def get_worker_logs(self, worker_name: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get worker logs (note: this is limited by Cloudflare API)

        Args:
            worker_name: Name of the worker
            limit: Maximum number of log entries

        Returns:
            Dict containing log information
        """
        # Note: Cloudflare Workers logs are typically accessed via the dashboard
        # or the wrangler CLI. The REST API has limited log access.
        return {
            'worker_name': worker_name,
            'message': 'Worker logs are available via Cloudflare dashboard or wrangler CLI',
            'dashboard_url': f'https://dash.cloudflare.com/workers',
            'cli_command': f'wrangler tail {worker_name}',
            'note': 'Real-time logs require wrangler CLI or dashboard access'
        }

    def list_workers(self) -> List[Dict[str, Any]]:
        """
        List all workers in the account

        Returns:
            List of worker information
        """
        account_id = self._get_account_id()

        response = self.auth_service.make_request(
            'GET',
            f'accounts/{account_id}/workers/scripts'
        )

        if not response.ok:
            raise Exception(f"Failed to list workers: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to list workers")

        return [
            {
                'name': worker.get('id'),
                'created_on': worker.get('created_on'),
                'modified_on': worker.get('modified_on'),
                'etag': worker.get('etag')
            }
            for worker in result.get('result', [])
        ]
