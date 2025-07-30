"""
InfraDSL Marketplace - Registry Client

This module provides the client API for interacting with the InfraDSL marketplace
hosted on Firestore. It handles authentication, template management, workspace
operations, and access control.

Usage:
    from infradsl.marketplace import RegistryClient
    
    # Individual user
    client = RegistryClient()
    client.login()
    
    # Workspace user  
    client = RegistryClient(workspace="nolimitcity")
    client.login()
"""

import os
import json
import hashlib
import importlib
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import auth, firestore, credentials
import requests
from dataclasses import dataclass, asdict

from .firestore_schema import (
    FirestoreCollections, TemplateVisibility, UserRole, TemplateType,
    USERS_SCHEMA, WORKSPACES_SCHEMA, TEMPLATES_SCHEMA
)


@dataclass
class TemplateInfo:
    """Template information"""
    id: str
    name: str
    display_name: str
    description: str
    workspace_id: Optional[str]
    creator_id: str
    visibility: str
    category: str
    providers: List[str]
    tags: List[str]
    latest_version: str
    downloads: int
    rating: float
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkspaceInfo:
    """Workspace information"""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    owner_id: str
    member_count: int
    template_count: int
    subscription_tier: str
    created_at: datetime


class RegistryError(Exception):
    """Base exception for registry operations"""
    pass


class AuthenticationError(RegistryError):
    """Authentication related errors"""
    pass


class PermissionError(RegistryError):
    """Permission related errors"""
    pass


class TemplateNotFoundError(RegistryError):
    """Template not found errors"""
    pass


class RegistryClient:
    """
    Client for InfraDSL marketplace registry operations
    
    Supports both individual users and workspace members with proper
    access control and authentication via Firebase.
    """
    
    def __init__(self, workspace: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize registry client
        
        Args:
            workspace: Workspace name to operate in (optional for individual users)
            config_file: Path to Firebase service account key (optional)
        """
        self.workspace = workspace
        self.current_user = None
        self.workspace_info = None
        self.db = None
        self.auth_token = None
        
        # Initialize Firebase
        self._init_firebase(config_file)
        
        # Load cached authentication if available
        self._load_cached_auth()
    
    def _init_firebase(self, config_file: Optional[str]):
        """Initialize Firebase connection"""
        try:
            # Try to use existing Firebase app
            app = firebase_admin.get_app()
        except ValueError:
            # Initialize new Firebase app
            if config_file and os.path.exists(config_file):
                cred = credentials.Certificate(config_file)
            else:
                # Try environment variable
                service_account = os.getenv('FIREBASE_SERVICE_ACCOUNT')
                if service_account:
                    cred = credentials.Certificate(json.loads(service_account))
                else:
                    # Use Application Default Credentials
                    cred = credentials.ApplicationDefault()
            
            app = firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    def _load_cached_auth(self):
        """Load cached authentication from local storage"""
        auth_file = Path.home() / '.infradsl' / 'auth.json'
        if auth_file.exists():
            try:
                with open(auth_file, 'r') as f:
                    auth_data = json.load(f)
                
                # Verify token is still valid
                if self._verify_token(auth_data.get('token')):
                    self.auth_token = auth_data['token']
                    self.current_user = auth_data.get('user')
                    
                    # Load workspace info if specified
                    if self.workspace:
                        self._load_workspace_info()
                        
            except Exception as e:
                # Invalid cached auth, will need to re-authenticate
                pass
    
    def _save_cached_auth(self):
        """Save authentication to local cache"""
        auth_dir = Path.home() / '.infradsl'
        auth_dir.mkdir(exist_ok=True)
        
        auth_file = auth_dir / 'auth.json'
        auth_data = {
            'token': self.auth_token,
            'user': self.current_user,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        with open(auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
    
    def _verify_token(self, token: str) -> bool:
        """Verify Firebase authentication token"""
        if not token:
            return False
            
        try:
            decoded_token = auth.verify_id_token(token)
            return True
        except Exception:
            return False
    
    def _load_workspace_info(self):
        """Load workspace information"""
        if not self.workspace:
            return
            
        # Find workspace by name/slug
        workspaces_ref = self.db.collection(FirestoreCollections.WORKSPACES)
        query = workspaces_ref.where('slug', '==', self.workspace).limit(1)
        
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            self.workspace_info = WorkspaceInfo(
                id=doc.id,
                name=data['name'],
                display_name=data['display_name'],
                description=data.get('description'),
                owner_id=data['owner_id'],
                member_count=data['stats']['total_members'],
                template_count=data['stats']['total_templates'],
                subscription_tier=data['subscription']['tier'],
                created_at=data['created_at']
            )
            break
        else:
            raise RegistryError(f"Workspace '{self.workspace}' not found")
    
    def login(self, email: Optional[str] = None, interactive: bool = True) -> bool:
        """
        Authenticate with the registry
        
        Args:
            email: Email address (optional, will prompt if not provided)
            interactive: Whether to use interactive authentication
            
        Returns:
            True if authentication successful
        """
        if self.auth_token and self._verify_token(self.auth_token):
            print("✅ Already authenticated")
            return True
        
        if interactive:
            # Interactive authentication flow
            print("🔐 InfraDSL Marketplace Authentication")
            print("Opening browser for authentication...")
            
            # Use Firebase Auth REST API for authentication
            auth_url = self._get_auth_url()
            print(f"Please visit: {auth_url}")
            
            # Wait for authentication callback
            token = self._wait_for_auth_callback()
            
            if token:
                self.auth_token = token
                decoded_token = auth.verify_id_token(token)
                self.current_user = {
                    'uid': decoded_token['uid'],
                    'email': decoded_token.get('email'),
                    'name': decoded_token.get('name')
                }
                
                # Create or update user profile
                self._create_or_update_user()
                
                # Load workspace info if specified
                if self.workspace:
                    self._load_workspace_info()
                    self._verify_workspace_access()
                
                # Save authentication
                self._save_cached_auth()
                
                print(f"✅ Authenticated as {self.current_user['email']}")
                if self.workspace_info:
                    print(f"📁 Workspace: {self.workspace_info.display_name}")
                
                return True
        
        return False
    
    def logout(self):
        """Logout and clear cached authentication"""
        self.auth_token = None
        self.current_user = None
        self.workspace_info = None
        
        # Clear cached auth
        auth_file = Path.home() / '.infradsl' / 'auth.json'
        if auth_file.exists():
            auth_file.unlink()
        
        print("✅ Logged out successfully")
    
    def _get_auth_url(self) -> str:
        """Generate authentication URL"""
        # This would integrate with Firebase Auth UI or custom auth flow
        return "https://docs.infradsl.dev/auth"
    
    def _wait_for_auth_callback(self) -> Optional[str]:
        """Wait for authentication callback (simplified)"""
        # In real implementation, this would:
        # 1. Start local callback server
        # 2. Wait for Firebase auth redirect
        # 3. Extract ID token from callback
        # For now, return mock token for testing
        return "mock_firebase_token"
    
    def _create_or_update_user(self):
        """Create or update user profile in Firestore"""
        if not self.current_user:
            return
        
        user_ref = self.db.collection(FirestoreCollections.USERS).document(self.current_user['uid'])
        
        # Check if user exists
        user_doc = user_ref.get()
        now = datetime.utcnow()
        
        if user_doc.exists():
            # Update last active
            user_ref.update({
                'last_active': now
            })
        else:
            # Create new user
            user_data = {
                'email': self.current_user['email'],
                'display_name': self.current_user.get('name', ''),
                'created_at': now,
                'last_active': now,
                'subscription_tier': 'free',
                'workspaces': [],
                'personal_templates': [],
                'preferences': {
                    'default_providers': [],
                    'notification_settings': {
                        'email_updates': True,
                        'template_notifications': True
                    },
                    'theme': 'dark',
                    'timezone': 'UTC'
                },
                'stats': {
                    'templates_created': 0,
                    'templates_used': 0,
                    'public_templates': 0,
                    'total_downloads': 0
                }
            }
            user_ref.set(user_data)
    
    def _verify_workspace_access(self):
        """Verify user has access to the specified workspace"""
        if not self.workspace_info or not self.current_user:
            return
        
        member_id = f"{self.workspace_info.id}_{self.current_user['uid']}"
        member_ref = self.db.collection(FirestoreCollections.WORKSPACE_MEMBERS).document(member_id)
        member_doc = member_ref.get()
        
        if not member_doc.exists():
            raise PermissionError(f"You don't have access to workspace '{self.workspace}'")
        
        member_data = member_doc.to_dict()
        if member_data['status'] != 'active':
            raise PermissionError(f"Your access to workspace '{self.workspace}' is {member_data['status']}")
    
    def create_workspace(self, name: str, display_name: str, description: str = "") -> str:
        """
        Create a new workspace
        
        Args:
            name: Workspace slug (URL-safe identifier)
            display_name: Human-readable name
            description: Workspace description
            
        Returns:
            Workspace ID
        """
        if not self.current_user:
            raise AuthenticationError("Must be authenticated to create workspace")
        
        # Check if workspace name is available
        existing = self.db.collection(FirestoreCollections.WORKSPACES)\
                         .where('slug', '==', name)\
                         .limit(1)\
                         .stream()
        
        if any(existing):
            raise RegistryError(f"Workspace name '{name}' is already taken")
        
        # Create workspace
        workspace_id = self._generate_id()
        now = datetime.utcnow()
        
        workspace_data = {
            'name': name,
            'display_name': display_name,
            'slug': name,
            'description': description,
            'created_at': now,
            'updated_at': now,
            'owner_id': self.current_user['uid'],
            'subscription': {
                'tier': 'startup',
                'status': 'active',
                'max_members': 10,
                'max_templates': 100,
                'max_private_templates': 50
            },
            'settings': {
                'allow_public_templates': True,
                'require_approval': False,
                'default_visibility': 'workspace',
                'compliance_mode': False,
                'cost_tracking': True,
                'audit_logging': False
            },
            'stats': {
                'total_members': 1,
                'total_templates': 0,
                'public_templates': 0,
                'monthly_downloads': 0
            },
            'integrations': {}
        }
        
        workspace_ref = self.db.collection(FirestoreCollections.WORKSPACES).document(workspace_id)
        workspace_ref.set(workspace_data)
        
        # Add creator as owner
        member_data = {
            'workspace_id': workspace_id,
            'user_id': self.current_user['uid'],
            'role': UserRole.OWNER.value,
            'invited_by': self.current_user['uid'],
            'joined_at': now,
            'last_active': now,
            'permissions': {
                'create_templates': True,
                'edit_templates': True,
                'delete_templates': True,
                'manage_members': True,
                'manage_billing': True,
                'publish_public': True
            },
            'teams': [],
            'status': 'active'
        }
        
        member_id = f"{workspace_id}_{self.current_user['uid']}"
        member_ref = self.db.collection(FirestoreCollections.WORKSPACE_MEMBERS).document(member_id)
        member_ref.set(member_data)
        
        print(f"✅ Created workspace '{display_name}' ({name})")
        return workspace_id
    
    def search_templates(self, query: str = "", category: str = "", 
                        providers: List[str] = [], tags: List[str] = [],
                        limit: int = 20) -> List[TemplateInfo]:
        """
        Search for templates
        
        Args:
            query: Search query string
            category: Filter by category
            providers: Filter by providers
            tags: Filter by tags
            limit: Maximum results to return
            
        Returns:
            List of matching templates
        """
        templates_ref = self.db.collection(FirestoreCollections.TEMPLATES)
        
        # Build query
        if self.workspace_info:
            # Search within workspace and public templates
            query_ref = templates_ref.where('visibility', 'in', ['public', 'workspace'])
        else:
            # Search only public templates for individual users
            query_ref = templates_ref.where('visibility', '==', 'public')
        
        if category:
            query_ref = query_ref.where('category', '==', category)
        
        # Execute query
        docs = query_ref.limit(limit).stream()
        
        templates = []
        for doc in docs:
            data = doc.to_dict()
            
            # Filter by providers if specified
            if providers and not any(p in data['providers'] for p in providers):
                continue
            
            # Filter by tags if specified
            if tags and not any(t in data['tags'] for t in tags):
                continue
            
            # Text search in name and description (simplified)
            if query:
                text = f"{data['name']} {data['description']}".lower()
                if query.lower() not in text:
                    continue
            
            template = TemplateInfo(
                id=doc.id,
                name=data['name'],
                display_name=data['display_name'],
                description=data['description'],
                workspace_id=data.get('workspace_id'),
                creator_id=data['creator_id'],
                visibility=data['visibility'],
                category=data['category'],
                providers=data['providers'],
                tags=data['tags'],
                latest_version=data['version_info']['latest_version'],
                downloads=data['usage_stats']['total_downloads'],
                rating=data['usage_stats']['average_rating'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            templates.append(template)
        
        return templates
    
    def get_template(self, template_id: str, version: str = "latest") -> Dict[str, Any]:
        """
        Get template details and source code
        
        Args:
            template_id: Template ID or workspace/name format
            version: Template version (default: latest)
            
        Returns:
            Template data including source code
        """
        # Handle workspace/name format
        if '/' in template_id:
            workspace_name, template_name = template_id.split('/', 1)
            template_id = self._resolve_template_id(workspace_name, template_name)
        
        # Get template metadata
        template_ref = self.db.collection(FirestoreCollections.TEMPLATES).document(template_id)
        template_doc = template_ref.get()
        
        if not template_doc.exists():
            raise TemplateNotFoundError(f"Template '{template_id}' not found")
        
        template_data = template_doc.to_dict()
        
        # Check access permissions
        if not self._can_access_template(template_data):
            raise PermissionError(f"You don't have access to template '{template_id}'")
        
        # Get version info
        if version == "latest":
            version = template_data['version_info']['latest_version']
        
        version_id = f"{template_id}_{version}"
        version_ref = self.db.collection(FirestoreCollections.TEMPLATE_VERSIONS).document(version_id)
        version_doc = version_ref.get()
        
        if not version_doc.exists():
            raise TemplateNotFoundError(f"Template version '{version}' not found")
        
        version_data = version_doc.to_dict()
        
        # Record usage analytics
        self._record_usage(template_id, version, "download")
        
        return {
            'template': template_data,
            'version': version_data,
            'source_code': version_data['source_code']
        }
    
    def publish_template(self, template_class: Type, name: str, description: str,
                        version: str = "1.0.0", visibility: str = "workspace",
                        category: str = "resource", providers: List[str] = [],
                        tags: List[str] = []) -> str:
        """
        Publish a template to the registry
        
        Args:
            template_class: Python class to publish
            name: Template name
            description: Template description
            version: Semantic version
            visibility: Template visibility level
            category: Template category
            providers: Supported providers
            tags: Template tags
            
        Returns:
            Template ID
        """
        if not self.current_user:
            raise AuthenticationError("Must be authenticated to publish templates")
        
        # Validate permissions
        if visibility == "public" and self.workspace_info:
            if not self._can_publish_public():
                raise PermissionError("You don't have permission to publish public templates")
        
        # Generate template ID
        template_id = self._generate_id()
        now = datetime.utcnow()
        
        # Extract source code
        source_code = self._extract_source_code(template_class)
        
        # Create template document
        template_data = {
            'name': name,
            'display_name': name.replace('-', ' ').title(),
            'slug': name,
            'description': description,
            'workspace_id': self.workspace_info.id if self.workspace_info else None,
            'creator_id': self.current_user['uid'],
            'created_at': now,
            'updated_at': now,
            'template_type': TemplateType.RESOURCE.value,
            'visibility': visibility,
            'category': category,
            'providers': providers,
            'tags': tags,
            'version_info': {
                'latest_version': version,
                'total_versions': 1,
                'stable_version': version,
                'beta_version': None
            },
            'usage_stats': {
                'total_downloads': 0,
                'weekly_downloads': 0,
                'monthly_downloads': 0,
                'unique_users': 0,
                'average_rating': 0.0,
                'total_ratings': 0
            },
            'requirements': {
                'min_infradsl_version': "1.0.0",
                'python_version': "3.8+",
                'dependencies': []
            },
            'pricing': {
                'type': 'free',
                'price': None,
                'currency': None,
                'billing_period': None
            },
            'compliance': {
                'security_scan': False,
                'license': 'MIT',
                'certifications': [],
                'last_scanned': None
            },
            'metadata': {}
        }
        
        template_ref = self.db.collection(FirestoreCollections.TEMPLATES).document(template_id)
        template_ref.set(template_data)
        
        # Create version document
        version_data = {
            'template_id': template_id,
            'version': version,
            'created_at': now,
            'created_by': self.current_user['uid'],
            'changelog': "Initial version",
            'is_stable': True,
            'is_beta': False,
            'is_deprecated': False,
            'source_code': source_code,
            'compatibility': {
                'infradsl_versions': ["1.0.0+"],
                'python_versions': ["3.8+"],
                'provider_versions': {}
            },
            'security': {
                'scan_results': None,
                'vulnerabilities': [],
                'security_score': None
            },
            'performance': {}
        }
        
        version_id = f"{template_id}_{version}"
        version_ref = self.db.collection(FirestoreCollections.TEMPLATE_VERSIONS).document(version_id)
        version_ref.set(version_data)
        
        workspace_prefix = f"{self.workspace}/" if self.workspace else ""
        print(f"✅ Published template '{workspace_prefix}{name}' version {version}")
        
        return template_id
    
    def import_template(self, template_ref: str, version: str = "latest") -> Type:
        """
        Import and dynamically load a template class
        
        Args:
            template_ref: Template reference (id or workspace/name)
            version: Template version
            
        Returns:
            Dynamically loaded template class
        """
        # Get template source code
        template_data = self.get_template(template_ref, version)
        source_code = template_data['source_code']
        
        # Create temporary module
        module_name = f"infradsl_template_{template_ref.replace('/', '_').replace('-', '_')}"
        
        # Compile and execute the source code
        compiled_code = compile(source_code['python_class'], f"<template:{template_ref}>", "exec")
        
        # Create module namespace
        module_namespace = {
            '__name__': module_name,
            '__file__': f"<template:{template_ref}>",
        }
        
        # Import required dependencies
        for dep in source_code.get('dependencies', []):
            module_namespace[dep.split('.')[-1]] = importlib.import_module(dep)
        
        # Execute the template code
        exec(compiled_code, module_namespace)
        
        # Find the template class (assume it's the main class in the module)
        template_class = None
        for name, obj in module_namespace.items():
            if isinstance(obj, type) and hasattr(obj, '__bases__'):
                # Look for classes that inherit from InfraDSL base classes
                for base in obj.__mro__:
                    if hasattr(base, '__module__') and 'infradsl' in getattr(base, '__module__', ''):
                        template_class = obj
                        break
                if template_class:
                    break
        
        if not template_class:
            raise RegistryError(f"Could not find template class in '{template_ref}'")
        
        return template_class
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _resolve_template_id(self, workspace_name: str, template_name: str) -> str:
        """Resolve workspace/name to template ID"""
        # Find workspace
        workspaces_ref = self.db.collection(FirestoreCollections.WORKSPACES)
        workspace_query = workspaces_ref.where('slug', '==', workspace_name).limit(1)
        
        workspace_id = None
        for doc in workspace_query.stream():
            workspace_id = doc.id
            break
        
        if not workspace_id:
            raise RegistryError(f"Workspace '{workspace_name}' not found")
        
        # Find template
        templates_ref = self.db.collection(FirestoreCollections.TEMPLATES)
        template_query = templates_ref\
            .where('workspace_id', '==', workspace_id)\
            .where('slug', '==', template_name)\
            .limit(1)
        
        for doc in template_query.stream():
            return doc.id
        
        raise TemplateNotFoundError(f"Template '{workspace_name}/{template_name}' not found")
    
    def _can_access_template(self, template_data: Dict[str, Any]) -> bool:
        """Check if user can access template"""
        visibility = template_data['visibility']
        
        # Public templates are accessible to everyone
        if visibility == 'public':
            return True
        
        # Private templates only accessible to creator
        if visibility == 'private':
            return self.current_user and template_data['creator_id'] == self.current_user['uid']
        
        # Workspace templates accessible to workspace members
        if visibility == 'workspace':
            if not self.current_user or not template_data.get('workspace_id'):
                return False
            
            # Check workspace membership
            member_id = f"{template_data['workspace_id']}_{self.current_user['uid']}"
            member_ref = self.db.collection(FirestoreCollections.WORKSPACE_MEMBERS).document(member_id)
            member_doc = member_ref.get()
            
            return member_doc.exists() and member_doc.to_dict().get('status') == 'active'
        
        return False
    
    def _can_publish_public(self) -> bool:
        """Check if user can publish public templates"""
        if not self.workspace_info or not self.current_user:
            return True  # Individual users can always publish public templates
        
        # Check workspace member permissions
        member_id = f"{self.workspace_info.id}_{self.current_user['uid']}"
        member_ref = self.db.collection(FirestoreCollections.WORKSPACE_MEMBERS).document(member_id)
        member_doc = member_ref.get()
        
        if member_doc.exists():
            permissions = member_doc.to_dict().get('permissions', {})
            return permissions.get('publish_public', False)
        
        return False
    
    def _extract_source_code(self, template_class: Type) -> Dict[str, Any]:
        """Extract source code from template class"""
        import inspect
        
        # Get source code
        source = inspect.getsource(template_class)
        
        # Get dependencies (imports)
        dependencies = []
        lines = source.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                dependencies.append(line)
        
        return {
            'python_class': source,
            'dependencies': dependencies,
            'examples': [],
            'tests': None,
            'validation_schema': None
        }
    
    def _record_usage(self, template_id: str, version: str, action: str):
        """Record usage analytics"""
        if not self.current_user:
            return
        
        analytics_id = self._generate_id()
        analytics_data = {
            'template_id': template_id,
            'version': version,
            'user_id': self.current_user['uid'],
            'workspace_id': self.workspace_info.id if self.workspace_info else None,
            'action': action,
            'timestamp': datetime.utcnow(),
            'metadata': {},
            'performance': {}
        }
        
        analytics_ref = self.db.collection(FirestoreCollections.USAGE_ANALYTICS).document(analytics_id)
        analytics_ref.set(analytics_data)