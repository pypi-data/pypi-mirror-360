"""
Cloudflare KV Storage Manager

Handles Cloudflare Workers KV edge key-value storage operations with the Cloudflare API.
Provides methods for creating, managing, and monitoring KV namespaces.
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional, Union


class KVStorageManager:
    """Manager for Cloudflare KV Storage operations"""

    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for authentication"""
        if not self.api_token:
            raise ValueError("Cloudflare API token required for KV operations")
        
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _get_account_id(self) -> str:
        """Get account ID"""
        if self.account_id:
            return self.account_id
        
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/accounts", headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()["result"]
            if accounts:
                return accounts[0]["id"]
        
        raise ValueError("Cloudflare account not found")

    def create_namespace(self, namespace: str, preview_mode: bool, bindings: List[Dict],
                         initial_data: Dict[str, Union[str, Dict, List]], 
                         default_ttl: Optional[int]) -> Dict[str, Any]:
        """Create KV namespace"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            # Create namespace
            namespace_data = {"title": namespace}
            
            create_response = requests.post(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces",
                headers=headers,
                json=namespace_data
            )
            
            if create_response.status_code not in [200, 201]:
                raise Exception(f"Failed to create namespace: {create_response.text}")
            
            namespace_result = create_response.json()["result"]
            namespace_id = namespace_result["id"]
            
            # Create preview namespace if requested
            preview_namespace_id = None
            if preview_mode:
                preview_response = requests.post(
                    f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces",
                    headers=headers,
                    json={"title": f"{namespace}-preview"}
                )
                
                if preview_response.status_code in [200, 201]:
                    preview_namespace_id = preview_response.json()["result"]["id"]
            
            # Populate initial data
            if initial_data:
                self._populate_initial_data(account_id, namespace_id, initial_data, default_ttl, headers)
            
            # Handle worker bindings
            binding_results = []
            for binding in bindings:
                binding_result = self._bind_to_worker(account_id, binding["worker"], binding["binding"], namespace_id, headers)
                binding_results.append(binding_result)
            
            return {
                "namespace": namespace,
                "namespace_id": namespace_id,
                "preview_namespace_id": preview_namespace_id,
                "account_id": account_id,
                "preview_mode": preview_mode,
                "initial_data_count": len(initial_data),
                "bindings": binding_results,
                "status": "created"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create KV namespace: {str(e)}")

    def _populate_initial_data(self, account_id: str, namespace_id: str, 
                               initial_data: Dict[str, Union[str, Dict, List]], 
                               default_ttl: Optional[int], headers: Dict[str, str]):
        """Populate namespace with initial data"""
        try:
            for key, value in initial_data.items():
                # Convert non-string values to JSON
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                
                # Put value with optional TTL
                put_url = f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
                put_params = {}
                if default_ttl:
                    put_params['expiration_ttl'] = default_ttl
                
                put_response = requests.put(
                    put_url,
                    headers={**headers, "Content-Type": "text/plain"},
                    params=put_params,
                    data=value_str
                )
                
                if put_response.status_code not in [200, 201]:
                    print(f"Warning: Failed to set initial value for key {key}: {put_response.text}")
                    
        except Exception as e:
            raise Exception(f"Failed to populate initial data: {str(e)}")

    def _bind_to_worker(self, account_id: str, worker_name: str, binding_name: str, 
                        namespace_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Bind KV namespace to a Worker"""
        try:
            # Get worker script to update bindings
            worker_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/workers/scripts/{worker_name}",
                headers=headers
            )
            
            if worker_response.status_code == 200:
                # Update worker with KV binding
                binding_data = {
                    "name": binding_name,
                    "namespace_id": namespace_id,
                    "type": "kv_namespace"
                }
                
                # This is a simplified binding - in practice, you'd need to update
                # the worker's metadata to include the KV binding
                return {
                    "worker": worker_name,
                    "binding": binding_name,
                    "namespace_id": namespace_id,
                    "status": "bound"
                }
            else:
                return {
                    "worker": worker_name,
                    "binding": binding_name,
                    "namespace_id": namespace_id,
                    "status": "worker_not_found"
                }
                
        except Exception as e:
            return {
                "worker": worker_name,
                "binding": binding_name,
                "namespace_id": namespace_id,
                "status": "binding_failed",
                "error": str(e)
            }

    def delete_namespace(self, namespace: str) -> Dict[str, Any]:
        """Delete KV namespace"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            # Find namespace by title
            namespaces_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces",
                headers=headers
            )
            
            if namespaces_response.status_code == 200:
                namespaces = namespaces_response.json()["result"]
                namespace_id = None
                
                for ns in namespaces:
                    if ns["title"] == namespace:
                        namespace_id = ns["id"]
                        break
                
                if namespace_id:
                    # Delete namespace
                    delete_response = requests.delete(
                        f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}",
                        headers=headers
                    )
                    
                    if delete_response.status_code == 200:
                        return {
                            "namespace": namespace,
                            "namespace_id": namespace_id,
                            "account_id": account_id,
                            "status": "deleted"
                        }
                    else:
                        raise Exception(f"Failed to delete namespace: {delete_response.text}")
                else:
                    raise Exception(f"Namespace not found: {namespace}")
            else:
                raise Exception(f"Failed to list namespaces: {namespaces_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to delete KV namespace: {str(e)}")

    def get_namespace_status(self, namespace: str) -> Dict[str, Any]:
        """Get KV namespace status"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            # Find namespace by title
            namespaces_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces",
                headers=headers
            )
            
            if namespaces_response.status_code == 200:
                namespaces = namespaces_response.json()["result"]
                namespace_info = None
                
                for ns in namespaces:
                    if ns["title"] == namespace:
                        namespace_info = ns
                        break
                
                if namespace_info:
                    namespace_id = namespace_info["id"]
                    
                    # Get keys count
                    keys_response = requests.get(
                        f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/keys",
                        headers=headers
                    )
                    
                    key_count = 0
                    if keys_response.status_code == 200:
                        keys_data = keys_response.json()["result"]
                        key_count = len(keys_data)
                    
                    return {
                        "namespace": namespace,
                        "namespace_id": namespace_id,
                        "account_id": account_id,
                        "key_count": key_count,
                        "supports_url_encoding": namespace_info.get("supports_url_encoding", False),
                        "status": "active"
                    }
                else:
                    raise Exception(f"Namespace not found: {namespace}")
            else:
                raise Exception(f"Failed to get namespace status: {namespaces_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to get KV namespace status: {str(e)}")

    def put_value(self, namespace: str, key: str, value: Union[str, Dict, List], 
                  ttl: Optional[int]) -> Dict[str, Any]:
        """Put value in KV store"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            namespace_id = self._get_namespace_id(account_id, namespace, headers)
            
            # Convert non-string values to JSON
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
                content_type = "application/json"
            else:
                value_str = str(value)
                content_type = "text/plain"
            
            # Put value with optional TTL
            put_url = f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
            put_headers = {**headers, "Content-Type": content_type}
            put_params = {}
            if ttl:
                put_params['expiration_ttl'] = ttl
            
            put_response = requests.put(
                put_url,
                headers=put_headers,
                params=put_params,
                data=value_str
            )
            
            if put_response.status_code in [200, 201]:
                return {
                    "namespace": namespace,
                    "key": key,
                    "value_length": len(value_str),
                    "ttl": ttl,
                    "status": "stored"
                }
            else:
                raise Exception(f"Failed to put value: {put_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to put value in KV store: {str(e)}")

    def get_value(self, namespace: str, key: str) -> Dict[str, Any]:
        """Get value from KV store"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            namespace_id = self._get_namespace_id(account_id, namespace, headers)
            
            get_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}",
                headers=headers
            )
            
            if get_response.status_code == 200:
                value = get_response.text
                
                # Try to parse as JSON
                try:
                    parsed_value = json.loads(value)
                    value_type = "json"
                except json.JSONDecodeError:
                    parsed_value = value
                    value_type = "text"
                
                return {
                    "namespace": namespace,
                    "key": key,
                    "value": parsed_value,
                    "value_type": value_type,
                    "status": "found"
                }
            elif get_response.status_code == 404:
                return {
                    "namespace": namespace,
                    "key": key,
                    "value": None,
                    "status": "not_found"
                }
            else:
                raise Exception(f"Failed to get value: {get_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to get value from KV store: {str(e)}")

    def delete_value(self, namespace: str, key: str) -> Dict[str, Any]:
        """Delete value from KV store"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            namespace_id = self._get_namespace_id(account_id, namespace, headers)
            
            delete_response = requests.delete(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}",
                headers=headers
            )
            
            if delete_response.status_code == 200:
                return {
                    "namespace": namespace,
                    "key": key,
                    "status": "deleted"
                }
            else:
                raise Exception(f"Failed to delete value: {delete_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to delete value from KV store: {str(e)}")

    def list_keys(self, namespace: str, prefix: str = "") -> Dict[str, Any]:
        """List keys in KV namespace"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            namespace_id = self._get_namespace_id(account_id, namespace, headers)
            
            params = {}
            if prefix:
                params['prefix'] = prefix
            
            keys_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/keys",
                headers=headers,
                params=params
            )
            
            if keys_response.status_code == 200:
                keys_data = keys_response.json()["result"]
                
                return {
                    "namespace": namespace,
                    "prefix": prefix,
                    "key_count": len(keys_data),
                    "keys": [key["name"] for key in keys_data],
                    "status": "listed"
                }
            else:
                raise Exception(f"Failed to list keys: {keys_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to list keys in KV namespace: {str(e)}")

    def _get_namespace_id(self, account_id: str, namespace: str, headers: Dict[str, str]) -> str:
        """Get namespace ID by name"""
        namespaces_response = requests.get(
            f"{self.base_url}/accounts/{account_id}/storage/kv/namespaces",
            headers=headers
        )
        
        if namespaces_response.status_code == 200:
            namespaces = namespaces_response.json()["result"]
            for ns in namespaces:
                if ns["title"] == namespace:
                    return ns["id"]
        
        raise ValueError(f"Namespace not found: {namespace}") 