"""
Firebase Client for InfraDSL Registry

This module provides Firebase/Firestore integration for the InfraDSL CLI,
allowing direct interaction with the production registry at registry.infradsl.dev
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .output_formatters import print_error, print_success, print_info, print_warning


class FirebaseClient:
    """Client for Firebase/Firestore operations"""
    
    def __init__(self, project_id: str = "infradsl"):
        self.project_id = project_id
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"
        self.auth_token = None
        self.user_info = None
        
    def authenticate_with_api_key(self, api_key: str, email: str, password: str) -> bool:
        """Authenticate with Firebase Auth using REST API"""
        try:
            # Firebase Auth REST API endpoint
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            
            auth_data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(auth_url, json=auth_data)
            
            if response.status_code == 200:
                auth_result = response.json()
                self.auth_token = auth_result.get('idToken')
                self.user_info = {
                    'uid': auth_result.get('localId'),
                    'email': auth_result.get('email'),
                    'displayName': auth_result.get('displayName', ''),
                    'refreshToken': auth_result.get('refreshToken')
                }
                return True
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print_error(f"Authentication failed: {error_message}")
                return False
                
        except Exception as e:
            print_error(f"Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        if not self.auth_token:
            raise Exception("Not authenticated. Please login first.")
        
        return {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
    
    def create_workspace(self, workspace_data: Dict[str, Any]) -> Optional[str]:
        """Create a workspace in Firestore"""
        try:
            workspace_id = workspace_data['name']
            
            # Convert data to Firestore format
            firestore_data = self._to_firestore_format({
                'id': workspace_id,
                'name': workspace_data['name'],
                'displayName': workspace_data.get('displayName', workspace_data['name']),
                'description': workspace_data.get('description', ''),
                'isPublic': workspace_data.get('isPublic', False),
                'ownerId': self.user_info['uid'],
                'members': [{
                    'uid': self.user_info['uid'],
                    'role': 'owner',
                    'joinedAt': datetime.now().isoformat()
                }],
                'memberIds': [self.user_info['uid']],
                'templateCount': 0,
                'settings': {
                    'allowPublicTemplates': workspace_data.get('isPublic', False),
                    'requireApprovalForMembers': not workspace_data.get('isPublic', False)
                },
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            })
            
            # Create workspace document
            workspace_url = f"{self.base_url}/workspaces/{workspace_id}"
            response = requests.patch(
                workspace_url,
                json={'fields': firestore_data},
                headers=self.get_auth_headers()
            )
            
            if response.status_code in [200, 201]:
                # Update user's workspaces array
                self._add_workspace_to_user(workspace_id)
                return workspace_id
            else:
                print_error(f"Failed to create workspace: {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Error creating workspace: {str(e)}")
            return None
    
    def publish_template(self, template_data: Dict[str, Any]) -> Optional[str]:
        """Publish a template to Firestore"""
        try:
            template_id = f"{template_data['workspace']}_{template_data['name']}_{template_data['version']}"
            
            # Convert to Firestore format
            firestore_data = self._to_firestore_format({
                'id': template_id,
                'name': template_data['name'],
                'displayName': template_data.get('display_name', template_data['name']),
                'description': template_data['description'],
                'version': template_data['version'],
                'category': template_data['category'],
                'providers': template_data['providers'],
                'tags': template_data['tags'],
                'visibility': template_data.get('visibility', 'workspace'),
                'workspaceId': template_data.get('workspace'),
                'authorId': self.user_info['uid'],
                'authorName': self.user_info.get('displayName', self.user_info['email']),
                'sourceCode': template_data['source_code'],
                'className': template_data.get('class_name', ''),
                'templateType': template_data.get('template_type', 'class'),
                'requirements': template_data.get('requirements', {}),
                'usageStats': {
                    'totalDownloads': 0,
                    'weeklyDownloads': 0,
                    'uniqueUsers': 0,
                    'averageRating': 0,
                    'totalRatings': 0
                },
                'versionInfo': {
                    'latestVersion': template_data['version'],
                    'totalVersions': 1
                },
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            })
            
            # Create template document in workspace subcollection
            workspace_id = template_data.get('workspace')
            template_url = f"{self.base_url}/workspaces/{workspace_id}/templates/{template_id}"
            response = requests.patch(
                template_url,
                json={'fields': firestore_data},
                headers=self.get_auth_headers()
            )
            
            if response.status_code in [200, 201]:
                return template_id
            else:
                print_error(f"Failed to publish template: {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Error publishing template: {str(e)}")
            return None
    
    def get_templates(self, workspace: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get templates from Firestore workspace subcollection"""
        try:
            # Use the provided workspace or default to the current user's workspace
            target_workspace = workspace or 'infradsl'  # Default workspace
            
            # Build query URL for workspace subcollection
            url = f"{self.base_url}/workspaces/{target_workspace}/templates"
            
            response = requests.get(url, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                templates = []
                
                for doc in data.get('documents', []):
                    template = self._from_firestore_format(doc.get('fields', {}))
                    
                    # Apply filters
                    if category and template.get('category') != category:
                        continue
                    
                    templates.append(template)
                
                return templates
            else:
                error_text = response.text
                print_error(f"Failed to get templates: {error_text}")
                # Raise exception to trigger fallback mechanism
                raise Exception(f"Firestore error: {error_text}")
                
        except Exception as e:
            print_error(f"Error getting templates: {str(e)}")
            raise e  # Re-raise to trigger fallback mechanism
    
    def get_template(self, template_name: str, workspace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific template from Firestore workspace subcollection"""
        try:
            # Try to find template by name and workspace
            templates = self.get_templates(workspace=workspace)
            
            for template in templates:
                if template.get('name') == template_name:
                    return template
            
            return None
            
        except Exception as e:
            print_error(f"Error getting template: {str(e)}")
            raise e  # Re-raise to trigger fallback mechanism
    
    def delete_template(self, template_name: str, workspace: Optional[str] = None, version: Optional[str] = None) -> bool:
        """Delete a template from the registry"""
        try:
            workspace = workspace or self.user_info.get('workspace', 'default')
            
            # Template document path
            template_path = f"workspaces/{workspace}/templates/{template_name}"
            template_url = f"{self.base_url}/{template_path}"
            
            print_info(f"🗑️  Deleting template from: {template_path}")
            
            # Delete the template document
            response = requests.delete(template_url, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                print_success(f"✅ Template '{workspace}/{template_name}' deleted from Firestore")
                return True
            elif response.status_code == 404:
                print_warning(f"⚠️  Template '{workspace}/{template_name}' not found in Firestore")
                return False
            else:
                print_error(f"❌ Failed to delete template: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error deleting template: {str(e)}")
            return False
    
    def _add_workspace_to_user(self, workspace_id: str):
        """Add workspace to user's workspaces array"""
        try:
            # Get current user document
            user_url = f"{self.base_url}/users/{self.user_info['uid']}"
            response = requests.get(user_url, headers=self.get_auth_headers())
            
            workspaces = []
            if response.status_code == 200:
                user_data = response.json()
                current_workspaces = user_data.get('fields', {}).get('workspaces', {}).get('arrayValue', {}).get('values', [])
                workspaces = [w.get('stringValue', '') for w in current_workspaces]
            
            # Add new workspace if not already present
            if workspace_id not in workspaces:
                workspaces.append(workspace_id)
            
            # Update user document
            user_data = self._to_firestore_format({
                'uid': self.user_info['uid'],
                'email': self.user_info['email'],
                'displayName': self.user_info.get('displayName', ''),
                'workspaces': workspaces,
                'updatedAt': datetime.now().isoformat()
            })
            
            response = requests.patch(
                user_url,
                json={'fields': user_data},
                headers=self.get_auth_headers()
            )
            
        except Exception as e:
            print_warning(f"Warning: Could not update user workspaces: {str(e)}")
    
    def _to_firestore_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python dict to Firestore format"""
        def convert_value(value):
            if isinstance(value, str):
                return {'stringValue': value}
            elif isinstance(value, bool):
                return {'booleanValue': value}
            elif isinstance(value, int):
                return {'integerValue': str(value)}
            elif isinstance(value, float):
                return {'doubleValue': value}
            elif isinstance(value, list):
                return {
                    'arrayValue': {
                        'values': [convert_value(item) for item in value]
                    }
                }
            elif isinstance(value, dict):
                return {
                    'mapValue': {
                        'fields': {k: convert_value(v) for k, v in value.items()}
                    }
                }
            else:
                return {'stringValue': str(value)}
        
        return {key: convert_value(value) for key, value in data.items()}
    
    def _from_firestore_format(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Firestore format to Python dict"""
        def convert_value(field_value):
            if 'stringValue' in field_value:
                return field_value['stringValue']
            elif 'booleanValue' in field_value:
                return field_value['booleanValue']
            elif 'integerValue' in field_value:
                return int(field_value['integerValue'])
            elif 'doubleValue' in field_value:
                return field_value['doubleValue']
            elif 'arrayValue' in field_value:
                values = field_value['arrayValue'].get('values', [])
                return [convert_value(item) for item in values]
            elif 'mapValue' in field_value:
                map_fields = field_value['mapValue'].get('fields', {})
                return {k: convert_value(v) for k, v in map_fields.items()}
            else:
                return None
        
        return {key: convert_value(value) for key, value in fields.items()}