"""
Cloudflare Pages Manager

Handles Cloudflare Pages static site hosting operations with the Cloudflare API.
Provides methods for creating, managing, and deploying static sites.
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional


class PagesManager:
    """Manager for Cloudflare Pages operations"""

    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for authentication"""
        if not self.api_token:
            raise ValueError("Cloudflare API token required for Pages operations")
        
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

    def create_pages_project(self, project_name: str, deployment_type: str,
                             repo_url: Optional[str], branch: str,
                             build_command: Optional[str], output_dir: Optional[str],
                             root_dir: Optional[str], environment_variables: Dict[str, str],
                             custom_domains: List[str], redirect_rules: List[Dict],
                             header_rules: List[Dict], upload_directory: Optional[str]) -> Dict[str, Any]:
        """Create Pages project"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            if deployment_type == "github" and repo_url:
                # Create project with GitHub integration
                project_data = {
                    "name": project_name,
                    "source": {
                        "type": "github",
                        "config": {
                            "owner": repo_url.split('/')[0],
                            "repo_name": repo_url.split('/')[1],
                            "production_branch": branch,
                            "pr_comments_enabled": True,
                            "deployments_enabled": True
                        }
                    },
                    "build_config": {
                        "build_command": build_command,
                        "destination_dir": output_dir,
                        "root_dir": root_dir,
                        "web_analytics_tag": None,
                        "web_analytics_token": None
                    },
                    "deployment_configs": {
                        "production": {
                            "environment_variables": environment_variables,
                            "kv_namespaces": {},
                            "durable_object_namespaces": {},
                            "d1_databases": {},
                            "r2_buckets": {},
                            "services": {},
                            "compatibility_date": "2023-05-18",
                            "compatibility_flags": []
                        }
                    }
                }
            elif deployment_type == "upload" and upload_directory:
                # Create project for direct upload
                project_data = {
                    "name": project_name,
                    "source": None,
                    "build_config": {
                        "build_command": None,
                        "destination_dir": ".",
                        "root_dir": ".",
                        "web_analytics_tag": None,
                        "web_analytics_token": None
                    },
                    "deployment_configs": {
                        "production": {
                            "environment_variables": environment_variables,
                            "kv_namespaces": {},
                            "durable_object_namespaces": {},
                            "d1_databases": {},
                            "r2_buckets": {},
                            "services": {},
                            "compatibility_date": "2023-05-18",
                            "compatibility_flags": []
                        }
                    }
                }
            else:
                raise ValueError("Invalid deployment configuration")
            
            # Create the project
            create_response = requests.post(
                f"{self.base_url}/accounts/{account_id}/pages/projects",
                headers=headers,
                json=project_data
            )
            
            if create_response.status_code not in [200, 201]:
                raise Exception(f"Failed to create project: {create_response.text}")
            
            project = create_response.json()["result"]
            project_id = project["name"]
            
            # Add custom domains
            domain_results = []
            for domain in custom_domains:
                domain_response = requests.post(
                    f"{self.base_url}/accounts/{account_id}/pages/projects/{project_id}/domains",
                    headers=headers,
                    json={"name": domain}
                )
                
                if domain_response.status_code in [200, 201]:
                    domain_results.append(domain_response.json()["result"])
            
            # Handle direct upload if specified
            upload_result = None
            if deployment_type == "upload" and upload_directory:
                upload_result = self._upload_directory(account_id, project_id, upload_directory, headers)
            
            return {
                "project_name": project_name,
                "project_id": project_id,
                "account_id": account_id,
                "deployment_type": deployment_type,
                "subdomain": f"{project_name}.pages.dev",
                "custom_domains": domain_results,
                "upload_result": upload_result,
                "status": "created"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create Pages project: {str(e)}")

    def _upload_directory(self, account_id: str, project_id: str, upload_directory: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Upload directory for direct deployment"""
        try:
            import zipfile
            import tempfile
            import os
            
            # Create a zip file of the directory
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(upload_directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, upload_directory)
                            zipf.write(file_path, arcname)
                
                # Upload the zip file
                with open(temp_zip.name, 'rb') as zip_file:
                    upload_headers = {
                        "Authorization": headers["Authorization"]
                    }
                    
                    files = {'file': ('deployment.zip', zip_file, 'application/zip')}
                    
                    upload_response = requests.post(
                        f"{self.base_url}/accounts/{account_id}/pages/projects/{project_id}/deployments",
                        headers=upload_headers,
                        files=files
                    )
                
                # Clean up temp file
                os.unlink(temp_zip.name)
                
                if upload_response.status_code in [200, 201]:
                    return upload_response.json()["result"]
                else:
                    raise Exception(f"Upload failed: {upload_response.text}")
                    
        except Exception as e:
            raise Exception(f"Failed to upload directory: {str(e)}")

    def delete_pages_project(self, project_name: str) -> Dict[str, Any]:
        """Delete Pages project"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            response = requests.delete(
                f"{self.base_url}/accounts/{account_id}/pages/projects/{project_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "project_name": project_name,
                    "account_id": account_id,
                    "status": "deleted"
                }
            else:
                raise Exception(f"Failed to delete project: {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to delete Pages project: {str(e)}")

    def get_pages_status(self, project_name: str) -> Dict[str, Any]:
        """Get Pages project status"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            # Get project details
            project_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/pages/projects/{project_name}",
                headers=headers
            )
            
            # Get deployments
            deployments_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/pages/projects/{project_name}/deployments",
                headers=headers
            )
            
            # Get domains
            domains_response = requests.get(
                f"{self.base_url}/accounts/{account_id}/pages/projects/{project_name}/domains",
                headers=headers
            )
            
            if project_response.status_code == 200:
                project = project_response.json()["result"]
                deployments = deployments_response.json()["result"] if deployments_response.status_code == 200 else []
                domains = domains_response.json()["result"] if domains_response.status_code == 200 else []
                
                return {
                    "project_name": project_name,
                    "project_id": project["name"],
                    "account_id": account_id,
                    "subdomain": project["subdomain"],
                    "source": project.get("source"),
                    "build_config": project.get("build_config"),
                    "deployments": deployments,
                    "domains": domains,
                    "created_on": project["created_on"],
                    "status": "active"
                }
            else:
                raise Exception(f"Project not found: {project_response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to get Pages status: {str(e)}")

    def trigger_deployment(self, project_name: str) -> Dict[str, Any]:
        """Trigger new deployment"""
        try:
            account_id = self._get_account_id()
            headers = self._get_headers()
            
            response = requests.post(
                f"{self.base_url}/accounts/{account_id}/pages/projects/{project_name}/deployments",
                headers=headers,
                json={}
            )
            
            if response.status_code in [200, 201]:
                deployment = response.json()["result"]
                return {
                    "project_name": project_name,
                    "deployment_id": deployment["id"],
                    "deployment_stage": deployment["stage"],
                    "status": "triggered"
                }
            else:
                raise Exception(f"Failed to trigger deployment: {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to trigger deployment: {str(e)}") 