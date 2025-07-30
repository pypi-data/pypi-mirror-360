"""
GCP Cloud IAM Core Implementation

Core attributes and authentication for Google Cloud Identity & Access Management.
Provides the foundation for the modular IAM security system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class IAMCore(BaseGcpResource):
    """
    Core class for Google Cloud IAM functionality.
    
    This class provides:
    - Basic IAM attributes and configuration
    - Authentication setup
    - Common utilities for IAM operations
    - Policy and binding management foundations
    """
    
    def __init__(self, name: str):
        """Initialize IAM core with policy/resource name"""
        super().__init__(name)
        
        # Core IAM attributes
        self.iam_name = name
        self.iam_description = f"IAM configuration for {name}"
        self.iam_type = "policy"  # policy, service_account, custom_role
        
        # IAM Policy configuration
        self.policy_bindings = []
        self.policy_version = 3  # IAM Policy version (supports conditions)
        self.policy_etag = None
        
        # Service Account configuration
        self.service_accounts = []
        self.sa_display_name = None
        self.sa_email = None
        self.sa_unique_id = None
        self.sa_keys = []
        
        # Custom Roles configuration
        self.custom_roles = []
        self.role_permissions = []
        self.role_stage = "GA"  # GA, BETA, ALPHA, DEPRECATED, DISABLED
        
        # Organization and Project IAM
        self.organization_id = None
        self.folder_id = None
        self.project_id = None
        self.resource_name = None
        
        # Built-in roles and permissions
        self.predefined_roles = []
        self.conditional_bindings = []
        
        # Security configuration
        self.audit_logging_enabled = True
        self.condition_expressions = []
        self.iam_conditions = []
        
        # Labels and organization
        self.iam_labels = {}
        
        # State tracking
        self.iam_exists = False
        self.iam_created = False
        self.policy_created = False
        
    def _initialize_managers(self):
        """Initialize IAM-specific managers"""
        # Will be set up after authentication
        self.iam_manager = None
        self.service_account_manager = None
        self.role_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.security.iam_manager import IAMManager
        from ...googlecloud_managers.security.service_account_manager import ServiceAccountManager
        from ...googlecloud_managers.security.role_manager import RoleManager
        
        self.iam_manager = IAMManager(self.gcp_client)
        self.service_account_manager = ServiceAccountManager(self.gcp_client)
        self.role_manager = RoleManager(self.gcp_client)
        
        # Set up project context
        self.project_id = self.project_id or self.gcp_client.project_id
        
    def _is_valid_role(self, role: str) -> bool:
        """Check if role format is valid"""
        # Roles can be:
        # - Predefined: roles/viewer, roles/editor, roles/owner
        # - Custom: projects/PROJECT_ID/roles/ROLE_NAME
        # - Organization: organizations/ORG_ID/roles/ROLE_NAME
        
        if role.startswith("roles/"):
            return True  # Predefined role
        elif role.startswith("projects/") and "/roles/" in role:
            return True  # Project custom role
        elif role.startswith("organizations/") and "/roles/" in role:
            return True  # Organization custom role
        else:
            return False
            
    def _is_valid_member(self, member: str) -> bool:
        """Check if member format is valid"""
        # Members can be:
        # - user:email@domain.com
        # - serviceAccount:email@project.iam.gserviceaccount.com
        # - group:group@domain.com
        # - domain:domain.com
        # - allUsers
        # - allAuthenticatedUsers
        
        valid_prefixes = ["user:", "serviceAccount:", "group:", "domain:"]
        special_members = ["allUsers", "allAuthenticatedUsers"]
        
        if member in special_members:
            return True
            
        return any(member.startswith(prefix) for prefix in valid_prefixes)
        
    def _is_valid_permission(self, permission: str) -> bool:
        """Check if permission format is valid"""
        # Permissions format: service.resource.verb
        # Examples: compute.instances.create, storage.buckets.list
        
        parts = permission.split(".")
        return len(parts) >= 3 and all(part.isalnum() or "_" in part for part in parts)
        
    def _is_valid_condition_expression(self, expression: str) -> bool:
        """Check if CEL condition expression is valid"""
        # Basic validation for Common Expression Language (CEL)
        # Real implementation would use CEL parser
        
        if not expression:
            return False
            
        # Check for common CEL patterns
        cel_patterns = [
            "request.time",
            "resource.name",
            "resource.type",
            "has(",
            "size(",
            "duration(",
            "timestamp("
        ]
        
        return any(pattern in expression for pattern in cel_patterns)
        
    def _validate_policy_binding(self, binding: Dict[str, Any]) -> bool:
        """Validate IAM policy binding"""
        required_fields = ["role", "members"]
        
        for field in required_fields:
            if field not in binding:
                return False
                
        # Validate role
        if not self._is_valid_role(binding["role"]):
            return False
            
        # Validate members
        members = binding.get("members", [])
        if not isinstance(members, list) or not members:
            return False
            
        for member in members:
            if not self._is_valid_member(member):
                return False
                
        # Validate condition if present
        condition = binding.get("condition")
        if condition:
            required_condition_fields = ["title", "expression"]
            for field in required_condition_fields:
                if field not in condition:
                    return False
                    
            if not self._is_valid_condition_expression(condition["expression"]):
                return False
                
        return True
        
    def _validate_service_account_config(self, sa_config: Dict[str, Any]) -> bool:
        """Validate service account configuration"""
        required_fields = ["account_id"]
        
        for field in required_fields:
            if field not in sa_config:
                return False
                
        # Validate account ID format
        account_id = sa_config["account_id"]
        if not (6 <= len(account_id) <= 30):
            return False
            
        # Must start with lowercase letter, contain only lowercase letters, digits, hyphens
        import re
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, account_id))
        
    def _validate_custom_role_config(self, role_config: Dict[str, Any]) -> bool:
        """Validate custom role configuration"""
        required_fields = ["role_id", "permissions"]
        
        for field in required_fields:
            if field not in role_config:
                return False
                
        # Validate role ID
        role_id = role_config["role_id"]
        if not (3 <= len(role_id) <= 64):
            return False
            
        # Validate permissions
        permissions = role_config.get("permissions", [])
        if not isinstance(permissions, list) or not permissions:
            return False
            
        for permission in permissions:
            if not self._is_valid_permission(permission):
                return False
                
        # Validate stage
        valid_stages = ["GA", "BETA", "ALPHA", "DEPRECATED", "DISABLED"]
        stage = role_config.get("stage", "GA")
        if stage not in valid_stages:
            return False
            
        return True
        
    def _get_predefined_roles(self) -> List[str]:
        """Get list of common predefined GCP roles"""
        return [
            # Basic roles
            "roles/viewer",
            "roles/editor", 
            "roles/owner",
            
            # Compute roles
            "roles/compute.admin",
            "roles/compute.instanceAdmin",
            "roles/compute.viewer",
            "roles/compute.networkAdmin",
            "roles/compute.securityAdmin",
            
            # Storage roles
            "roles/storage.admin",
            "roles/storage.objectAdmin",
            "roles/storage.objectViewer",
            "roles/storage.objectCreator",
            
            # IAM roles
            "roles/iam.serviceAccountAdmin",
            "roles/iam.serviceAccountUser",
            "roles/iam.serviceAccountKeyAdmin",
            "roles/iam.roleAdmin",
            "roles/iam.securityAdmin",
            
            # Networking roles
            "roles/networksecurity.admin",
            "roles/dns.admin",
            "roles/loadbalancing.admin",
            
            # Database roles
            "roles/cloudsql.admin",
            "roles/cloudsql.client",
            "roles/cloudsql.editor",
            "roles/cloudsql.viewer",
            
            # Functions roles
            "roles/cloudfunctions.admin",
            "roles/cloudfunctions.developer",
            "roles/cloudfunctions.viewer",
            
            # Monitoring roles
            "roles/monitoring.admin",
            "roles/monitoring.editor",
            "roles/monitoring.viewer",
            "roles/logging.admin",
            "roles/logging.viewer",
            
            # Security roles
            "roles/secretmanager.admin",
            "roles/secretmanager.secretAccessor",
            "roles/cloudkms.admin",
            "roles/cloudkms.cryptoKeyEncrypterDecrypter"
        ]
        
    def _get_role_description(self, role: str) -> str:
        """Get description for a role"""
        descriptions = {
            "roles/viewer": "View access to all resources",
            "roles/editor": "Edit access to all resources", 
            "roles/owner": "Full control of all resources",
            "roles/compute.admin": "Full control of Compute Engine resources",
            "roles/storage.admin": "Full control of Cloud Storage resources",
            "roles/iam.serviceAccountAdmin": "Create and manage service accounts",
            "roles/cloudsql.admin": "Full control of Cloud SQL resources",
            "roles/cloudfunctions.admin": "Full control of Cloud Functions"
        }
        return descriptions.get(role, role)
        
    def _estimate_iam_cost(self) -> float:
        """Estimate monthly cost for IAM"""
        # Google Cloud IAM is free for most operations
        # Only some advanced features have costs
        
        base_cost = 0.0  # IAM is free
        
        # Service account keys cost (if using key-based auth)
        sa_keys_cost = len(self.sa_keys) * 0.0  # Currently free
        
        # Custom roles cost (currently free)
        custom_roles_cost = len(self.custom_roles) * 0.0
        
        # Advanced audit logging might have costs
        audit_cost = 0.0
        if self.audit_logging_enabled:
            audit_cost = 2.0  # Estimated $2/month for audit logs
            
        return base_cost + sa_keys_cost + custom_roles_cost + audit_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of IAM from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get IAM policy info
            if self.iam_manager:
                iam_info = self.iam_manager.get_iam_policy_info(
                    resource_name=self.resource_name or f"projects/{self.project_id}"
                )
                
                if iam_info.get("exists", False):
                    # Get service accounts
                    service_accounts = []
                    if self.service_account_manager:
                        service_accounts = self.service_account_manager.list_service_accounts(self.project_id)
                    
                    # Get custom roles
                    custom_roles = []
                    if self.role_manager:
                        custom_roles = self.role_manager.list_custom_roles(self.project_id)
                    
                    return {
                        "exists": True,
                        "resource_name": self.resource_name or f"projects/{self.project_id}",
                        "policy_version": iam_info.get("version", 1),
                        "policy_etag": iam_info.get("etag"),
                        "bindings": iam_info.get("bindings", []),
                        "bindings_count": len(iam_info.get("bindings", [])),
                        "service_accounts": service_accounts,
                        "service_accounts_count": len(service_accounts),
                        "custom_roles": custom_roles,
                        "custom_roles_count": len(custom_roles),
                        "audit_configs": iam_info.get("auditConfigs", []),
                        "last_modified": iam_info.get("last_modified"),
                        "status": iam_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "resource_name": self.resource_name or f"projects/{self.project_id}"
                    }
            else:
                return {
                    "exists": False,
                    "resource_name": self.resource_name or f"projects/{self.project_id}",
                    "error": "IAM manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch IAM state: {str(e)}")
            return {
                "exists": False,
                "resource_name": self.resource_name or f"projects/{self.project_id}",
                "error": str(e)
            }