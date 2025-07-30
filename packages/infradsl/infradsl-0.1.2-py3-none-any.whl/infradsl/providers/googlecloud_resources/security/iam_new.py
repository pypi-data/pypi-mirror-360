"""
GCP Cloud IAM Complete Implementation

Combines all Cloud IAM functionality through multiple inheritance:
- IAMCore: Core attributes and authentication
- IAMConfigurationMixin: Chainable configuration methods  
- IAMLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .iam_core import IAMCore
from .iam_configuration import IAMConfigurationMixin
from .iam_lifecycle import IAMLifecycleMixin


class CloudIAM(IAMLifecycleMixin, IAMConfigurationMixin, IAMCore):
    """
    Complete GCP Cloud IAM implementation for identity and access management.
    
    This class combines:
    - IAM policy configuration methods (roles, members, conditions)
    - IAM lifecycle management (create, destroy, preview)
    - Service account and custom role management
    - Advanced security features (conditional access, audit logging)
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudIAM instance for identity and access management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$2.00/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._iam_type = None
        self._monitoring_enabled = True
        self._auto_scaling_enabled = False
    
    def validate_configuration(self):
        """Validate the current Cloud IAM configuration"""
        errors = []
        warnings = []
        
        # Validate resource name
        if not self.resource_name:
            errors.append("Resource name is required (project, organization, or folder)")
        
        # Validate policy bindings
        for i, binding in enumerate(self.policy_bindings):
            if not self._validate_policy_binding(binding):
                errors.append(f"Invalid policy binding at index {i}: {binding.get('role', 'Unknown')}")
        
        # Validate service accounts
        for sa in self.service_accounts:
            if not self._validate_service_account_config(sa):
                errors.append(f"Invalid service account configuration: {sa.get('account_id', 'Unknown')}")
        
        # Validate custom roles
        for role in self.custom_roles:
            if not self._validate_custom_role_config(role):
                errors.append(f"Invalid custom role configuration: {role.get('role_id', 'Unknown')}")
        
        # Security warnings
        public_bindings = [b for b in self.policy_bindings 
                          if "allUsers" in b.get("members", []) or "allAuthenticatedUsers" in b.get("members", [])]
        if public_bindings:
            warnings.append(f"{len(public_bindings)} binding(s) grant public access - review for security")
        
        # Owner role warnings
        owner_bindings = [b for b in self.policy_bindings if b.get("role") == "roles/owner"]
        if len(owner_bindings) > 2:
            warnings.append(f"{len(owner_bindings)} owner role bindings - consider limiting owner access")
        
        # Service account warnings
        sa_with_owner = [b for b in self.policy_bindings 
                        if b.get("role") == "roles/owner" and 
                        any("serviceAccount:" in member for member in b.get("members", []))]
        if sa_with_owner:
            warnings.append("Service accounts with owner role found - consider using more specific roles")
        
        # Policy version warnings
        if self.policy_version < 3 and any(b.get("condition") for b in self.policy_bindings):
            warnings.append("Conditional bindings require policy version 3")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_iam_info(self):
        """Get complete information about the Cloud IAM configuration"""
        return {
            'iam_name': self.iam_name,
            'description': self.iam_description,
            'resource_name': self.resource_name,
            'policy_version': self.policy_version,
            'policy_bindings_count': len(self.policy_bindings),
            'policy_bindings': self.policy_bindings,
            'service_accounts_count': len(self.service_accounts),
            'service_accounts': self.service_accounts,
            'custom_roles_count': len(self.custom_roles),
            'custom_roles': self.custom_roles,
            'audit_logging_enabled': self.audit_logging_enabled,
            'labels_count': len(self.iam_labels),
            'iam_exists': self.iam_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'iam_type': self._iam_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this IAM configuration with a new name"""
        cloned_iam = CloudIAM(new_name)
        cloned_iam.iam_name = new_name
        cloned_iam.iam_description = self.iam_description
        cloned_iam.resource_name = self.resource_name
        cloned_iam.policy_version = self.policy_version
        cloned_iam.policy_bindings = [binding.copy() for binding in self.policy_bindings]
        cloned_iam.service_accounts = [sa.copy() for sa in self.service_accounts]
        cloned_iam.custom_roles = [role.copy() for role in self.custom_roles]
        cloned_iam.audit_logging_enabled = self.audit_logging_enabled
        cloned_iam.iam_labels = self.iam_labels.copy()
        return cloned_iam
    
    def export_configuration(self):
        """Export IAM configuration for backup or migration"""
        return {
            'metadata': {
                'iam_name': self.iam_name,
                'resource_name': self.resource_name,
                'policy_version': self.policy_version,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'iam_name': self.iam_name,
                'description': self.iam_description,
                'resource_name': self.resource_name,
                'policy_version': self.policy_version,
                'policy_bindings': self.policy_bindings,
                'service_accounts': self.service_accounts,
                'custom_roles': self.custom_roles,
                'audit_logging_enabled': self.audit_logging_enabled,
                'labels': self.iam_labels,
                'optimization_priority': self._optimization_priority,
                'iam_type': self._iam_type,
                'monitoring_enabled': self._monitoring_enabled,
                'auto_scaling_enabled': self._auto_scaling_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import IAM configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.iam_name = config.get('iam_name', self.iam_name)
            self.iam_description = config.get('description', f"IAM configuration for {self.iam_name}")
            self.resource_name = config.get('resource_name')
            self.policy_version = config.get('policy_version', 3)
            self.policy_bindings = config.get('policy_bindings', [])
            self.service_accounts = config.get('service_accounts', [])
            self.custom_roles = config.get('custom_roles', [])
            self.audit_logging_enabled = config.get('audit_logging_enabled', True)
            self.iam_labels = config.get('labels', {})
            self._optimization_priority = config.get('optimization_priority')
            self._iam_type = config.get('iam_type')
            self._monitoring_enabled = config.get('monitoring_enabled', True)
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable comprehensive monitoring and alerting"""
        self._monitoring_enabled = enabled
        if enabled:
            self.audit_logging_enabled = True
            print("📊 Comprehensive monitoring enabled")
            print("   💡 IAM audit logging activated")
            print("   💡 Access monitoring configured")
            print("   💡 Security alerts enabled")
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling for IAM resources"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for IAM")
            print("   💡 Dynamic role assignment configured")
            print("   💡 Auto-provisioning enabled")
        return self
    
    def get_binding_by_role(self, role: str):
        """Get policy binding by role"""
        for binding in self.policy_bindings:
            if binding.get("role") == role:
                return binding
        return None
    
    def get_bindings_by_member(self, member: str):
        """Get all policy bindings for a specific member"""
        matching_bindings = []
        for binding in self.policy_bindings:
            if member in binding.get("members", []):
                matching_bindings.append(binding)
        return matching_bindings
    
    def get_service_account_by_id(self, account_id: str):
        """Get service account configuration by account ID"""
        for sa in self.service_accounts:
            if sa.get("account_id") == account_id:
                return sa
        return None
    
    def get_custom_role_by_id(self, role_id: str):
        """Get custom role configuration by role ID"""
        for role in self.custom_roles:
            if role.get("role_id") == role_id:
                return role
        return None
    
    def remove_binding(self, role: str):
        """Remove a policy binding by role"""
        self.policy_bindings = [b for b in self.policy_bindings if b.get("role") != role]
        print(f"🗑️  Removed policy binding for role '{role}'")
        return self
    
    def remove_member_from_role(self, role: str, member: str):
        """Remove a specific member from a role"""
        for binding in self.policy_bindings:
            if binding.get("role") == role:
                members = binding.get("members", [])
                if member in members:
                    members.remove(member)
                    print(f"🗑️  Removed '{member}' from role '{role}'")
                    break
        return self
    
    def remove_service_account(self, account_id: str):
        """Remove a service account from configuration"""
        self.service_accounts = [sa for sa in self.service_accounts if sa.get("account_id") != account_id]
        print(f"🗑️  Removed service account '{account_id}'")
        return self
    
    def remove_custom_role(self, role_id: str):
        """Remove a custom role from configuration"""
        self.custom_roles = [role for role in self.custom_roles if role.get("role_id") != role_id]
        print(f"🗑️  Removed custom role '{role_id}'")
        return self
    
    def get_security_analysis(self):
        """Analyze IAM security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": [],
            "high_risk_bindings": 0,
            "medium_risk_bindings": 0,
            "low_risk_bindings": 0
        }
        
        # Analyze policy bindings for security risks
        for binding in self.policy_bindings:
            role = binding.get("role", "")
            members = binding.get("members", [])
            
            # Check for public access
            if "allUsers" in members:
                analysis["issues"].append(f"Public access granted for role '{role}'")
                analysis["security_score"] -= 30
                analysis["high_risk_bindings"] += 1
            elif "allAuthenticatedUsers" in members:
                analysis["issues"].append(f"All authenticated users have access to role '{role}'")
                analysis["security_score"] -= 20
                analysis["medium_risk_bindings"] += 1
            
            # Check for overprivileged roles
            if role == "roles/owner":
                if len(members) > 2:
                    analysis["recommendations"].append(f"Consider limiting owner role - currently {len(members)} members")
                    analysis["security_score"] -= 10
                analysis["medium_risk_bindings"] += 1
            elif role == "roles/editor":
                if len(members) > 5:
                    analysis["recommendations"].append(f"Consider using more specific roles instead of editor - currently {len(members)} members")
                    analysis["security_score"] -= 5
                analysis["low_risk_bindings"] += 1
            else:
                analysis["low_risk_bindings"] += 1
        
        # Check service accounts
        sa_with_high_privileges = []
        for binding in self.policy_bindings:
            if binding.get("role") in ["roles/owner", "roles/editor"]:
                for member in binding.get("members", []):
                    if member.startswith("serviceAccount:"):
                        sa_with_high_privileges.append(member)
        
        if sa_with_high_privileges:
            analysis["recommendations"].append(f"{len(sa_with_high_privileges)} service account(s) have high privileges")
            analysis["security_score"] -= 10
        
        # Check audit logging
        if not self.audit_logging_enabled:
            analysis["recommendations"].append("Enable audit logging for better security monitoring")
            analysis["security_score"] -= 15
        
        # Check policy version
        if self.policy_version < 3:
            analysis["recommendations"].append("Upgrade to policy version 3 for conditional access features")
            analysis["security_score"] -= 5
        
        return analysis
    
    def apply_security_best_practices(self):
        """Apply security best practices to the IAM configuration"""
        print("🔒 Applying security best practices to IAM")
        
        # Enable audit logging
        if not self.audit_logging_enabled:
            print("   💡 Enabling audit logging")
            self.audit_logging_enabled = True
        
        # Upgrade policy version
        if self.policy_version < 3:
            print("   💡 Upgrading to policy version 3")
            self.policy_version = 3
        
        # Add security labels
        self.iam_labels.update({
            "security": "enhanced",
            "compliance": "best-practices",
            "audit": "enabled"
        })
        print("   💡 Added security labels")
        
        # Analyze current security posture
        analysis = self.get_security_analysis()
        if analysis["issues"]:
            print(f"   ⚠️  Security issues found: {len(analysis['issues'])}")
            for issue in analysis["issues"][:3]:  # Show first 3
                print(f"      - {issue}")
        
        if analysis["recommendations"]:
            print(f"   💡 Security recommendations: {len(analysis['recommendations'])}")
            for rec in analysis["recommendations"][:3]:  # Show first 3
                print(f"      - {rec}")
        
        return self
    
    def get_effective_permissions(self, member: str):
        """Get all effective permissions for a member"""
        permissions = set()
        roles = []
        
        # Find all roles assigned to the member
        for binding in self.policy_bindings:
            if member in binding.get("members", []):
                role = binding.get("role")
                roles.append(role)
                
                # For custom roles, get specific permissions
                if role.startswith("projects/") or role.startswith("organizations/"):
                    custom_role = self.get_custom_role_by_id(role.split("/")[-1])
                    if custom_role:
                        permissions.update(custom_role.get("permissions", []))
        
        return {
            "member": member,
            "roles": roles,
            "custom_permissions": list(permissions),
            "total_roles": len(roles),
            "total_permissions": len(permissions)
        }
    
    def get_members_with_role(self, role: str):
        """Get all members that have a specific role"""
        binding = self.get_binding_by_role(role)
        if binding:
            return binding.get("members", [])
        return []
    
    def audit_report(self):
        """Generate an audit report of the IAM configuration"""
        return {
            "configuration_name": self.iam_name,
            "resource": self.resource_name,
            "policy_version": self.policy_version,
            "total_bindings": len(self.policy_bindings),
            "total_members": len(set(
                member for binding in self.policy_bindings 
                for member in binding.get("members", [])
            )),
            "service_accounts": len(self.service_accounts),
            "custom_roles": len(self.custom_roles),
            "security_analysis": self.get_security_analysis(),
            "audit_logging": self.audit_logging_enabled,
            "conditional_bindings": len([b for b in self.policy_bindings if b.get("condition")]),
            "public_access_bindings": len([
                b for b in self.policy_bindings 
                if "allUsers" in b.get("members", []) or "allAuthenticatedUsers" in b.get("members", [])
            ]),
            "generated_at": "Mock timestamp"
        }


# Convenience functions for creating CloudIAM instances
def create_project_iam(project_id: str) -> CloudIAM:
    """Create IAM configuration for a project"""
    iam = CloudIAM(f"{project_id}-iam")
    iam.project(project_id).production_iam()
    return iam

def create_web_app_iam(project_id: str, app_name: str, dev_email: str = None) -> CloudIAM:
    """Create IAM configuration for a web application"""
    iam = CloudIAM(f"{app_name}-iam")
    iam.project(project_id).production_iam().web_app_roles(app_name, dev_email)
    return iam

def create_microservices_iam(project_id: str, service_name: str, team_group: str = None) -> CloudIAM:
    """Create IAM configuration for microservices"""
    iam = CloudIAM(f"{service_name}-iam")
    iam.project(project_id).production_iam().microservices_roles(service_name, team_group)
    return iam

def create_development_iam(project_id: str, dev_team_group: str) -> CloudIAM:
    """Create IAM configuration for development environment"""
    iam = CloudIAM(f"{project_id}-dev-iam")
    iam.project(project_id).development_iam().group("roles/editor", dev_team_group)
    return iam

def create_admin_iam(project_id: str, admin_email: str, backup_admin: str = None) -> CloudIAM:
    """Create IAM configuration for administrative access"""
    iam = CloudIAM(f"{project_id}-admin-iam")
    iam.project(project_id).production_iam().admin_setup(admin_email, backup_admin)
    return iam

# Aliases for backward compatibility
IAM = CloudIAM
GCPIam = CloudIAM