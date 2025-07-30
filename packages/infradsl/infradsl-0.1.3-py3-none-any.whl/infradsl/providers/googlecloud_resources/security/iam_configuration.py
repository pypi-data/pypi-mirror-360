"""
GCP Cloud IAM Configuration Mixin

Chainable configuration methods for Google Cloud Identity & Access Management.
Provides Rails-like method chaining for fluent IAM configuration.
"""

from typing import Dict, Any, List, Optional


class IAMConfigurationMixin:
    """
    Mixin for IAM configuration methods.
    
    This mixin provides chainable configuration methods for:
    - IAM policy bindings (roles and members)
    - Service account creation and management
    - Custom role definitions
    - Conditional access policies
    - Security and audit configurations
    """
    
    def description(self, description: str):
        """Set description for the IAM configuration"""
        self.iam_description = description
        return self
        
    def resource(self, resource_name: str):
        """Set the resource name for IAM policy (project, folder, organization)"""
        self.resource_name = resource_name
        return self
        
    def project(self, project_id: str):
        """Set project ID for IAM operations - Rails convenience"""
        self.project_id = project_id
        self.resource_name = f"projects/{project_id}"
        return self
        
    def organization(self, org_id: str):
        """Set organization ID for IAM operations - Rails convenience"""
        self.organization_id = org_id
        self.resource_name = f"organizations/{org_id}"
        return self
        
    def folder(self, folder_id: str):
        """Set folder ID for IAM operations - Rails convenience"""
        self.folder_id = folder_id
        self.resource_name = f"folders/{folder_id}"
        return self
        
    # Policy binding methods
    def bind_role(self, role: str, members: List[str], condition: Dict[str, str] = None):
        """Add a role binding to the IAM policy"""
        if not self._is_valid_role(role):
            print(f"⚠️  Warning: Invalid role format '{role}'")
            
        for member in members:
            if not self._is_valid_member(member):
                print(f"⚠️  Warning: Invalid member format '{member}'")
        
        binding = {
            "role": role,
            "members": members
        }
        
        if condition:
            binding["condition"] = condition
            
        if self._validate_policy_binding(binding):
            self.policy_bindings.append(binding)
        else:
            print(f"⚠️  Warning: Invalid policy binding for role '{role}'")
            
        return self
        
    def add_member(self, role: str, member: str, condition: Dict[str, str] = None):
        """Add a single member to a role - Rails convenience"""
        return self.bind_role(role, [member], condition)
        
    def user(self, role: str, email: str, condition: Dict[str, str] = None):
        """Grant role to a user - Rails convenience"""
        return self.add_member(role, f"user:{email}", condition)
        
    def service_account(self, role: str, email: str, condition: Dict[str, str] = None):
        """Grant role to a service account - Rails convenience"""
        return self.add_member(role, f"serviceAccount:{email}", condition)
        
    def group(self, role: str, email: str, condition: Dict[str, str] = None):
        """Grant role to a group - Rails convenience"""
        return self.add_member(role, f"group:{email}", condition)
        
    def domain(self, role: str, domain_name: str, condition: Dict[str, str] = None):
        """Grant role to all users in a domain - Rails convenience"""
        return self.add_member(role, f"domain:{domain_name}", condition)
        
    def all_users(self, role: str, condition: Dict[str, str] = None):
        """Grant role to all users (public access) - Rails convenience"""
        print("⚠️  WARNING: Granting role to 'allUsers' makes the resource publicly accessible")
        return self.add_member(role, "allUsers", condition)
        
    def all_authenticated_users(self, role: str, condition: Dict[str, str] = None):
        """Grant role to all authenticated users - Rails convenience"""
        return self.add_member(role, "allAuthenticatedUsers", condition)
        
    # Predefined role convenience methods
    def viewer(self, member: str, condition: Dict[str, str] = None):
        """Grant viewer role - Rails convenience"""
        return self.add_member("roles/viewer", member, condition)
        
    def editor(self, member: str, condition: Dict[str, str] = None):
        """Grant editor role - Rails convenience"""
        return self.add_member("roles/editor", member, condition)
        
    def owner(self, member: str, condition: Dict[str, str] = None):
        """Grant owner role - Rails convenience"""
        return self.add_member("roles/owner", member, condition)
        
    def compute_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant Compute Engine admin role - Rails convenience"""
        return self.add_member("roles/compute.admin", member, condition)
        
    def storage_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant Cloud Storage admin role - Rails convenience"""
        return self.add_member("roles/storage.admin", member, condition)
        
    def iam_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant IAM admin role - Rails convenience"""
        return self.add_member("roles/iam.serviceAccountAdmin", member, condition)
        
    def sql_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant Cloud SQL admin role - Rails convenience"""
        return self.add_member("roles/cloudsql.admin", member, condition)
        
    def functions_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant Cloud Functions admin role - Rails convenience"""
        return self.add_member("roles/cloudfunctions.admin", member, condition)
        
    def monitoring_admin(self, member: str, condition: Dict[str, str] = None):
        """Grant Monitoring admin role - Rails convenience"""
        return self.add_member("roles/monitoring.admin", member, condition)
        
    # Service account configuration
    def create_service_account(self, account_id: str, display_name: str = None, description: str = None):
        """Create a service account"""
        if not self._validate_service_account_config({"account_id": account_id}):
            print(f"⚠️  Warning: Invalid service account ID '{account_id}'")
            return self
            
        sa_config = {
            "account_id": account_id,
            "display_name": display_name or account_id.replace("-", " ").title(),
            "description": description or f"Service account for {account_id}",
            "email": f"{account_id}@{self.project_id}.iam.gserviceaccount.com"
        }
        
        self.service_accounts.append(sa_config)
        return self
        
    def sa(self, account_id: str, display_name: str = None):
        """Create service account - Rails convenience"""
        return self.create_service_account(account_id, display_name)
        
    def app_service_account(self, app_name: str):
        """Create service account for an application - Rails convenience"""
        account_id = f"{app_name}-sa"
        return self.create_service_account(
            account_id,
            f"{app_name.title()} Service Account",
            f"Service account for {app_name} application"
        )
        
    def compute_service_account(self, instance_name: str):
        """Create service account for Compute Engine - Rails convenience"""
        account_id = f"{instance_name}-compute-sa"
        return self.create_service_account(
            account_id,
            f"{instance_name.title()} Compute SA",
            f"Service account for {instance_name} compute instance"
        )
        
    def function_service_account(self, function_name: str):
        """Create service account for Cloud Function - Rails convenience"""
        account_id = f"{function_name}-func-sa"
        return self.create_service_account(
            account_id,
            f"{function_name.title()} Function SA",
            f"Service account for {function_name} cloud function"
        )
        
    # Custom role configuration
    def create_custom_role(self, role_id: str, permissions: List[str], **kwargs):
        """Create a custom role"""
        role_config = {
            "role_id": role_id,
            "title": kwargs.get("title", role_id.replace("_", " ").title()),
            "description": kwargs.get("description", f"Custom role {role_id}"),
            "permissions": permissions,
            "stage": kwargs.get("stage", "GA"),
            "included_permissions": permissions,
            "excluded_permissions": kwargs.get("excluded_permissions", [])
        }
        
        if self._validate_custom_role_config(role_config):
            self.custom_roles.append(role_config)
        else:
            print(f"⚠️  Warning: Invalid custom role configuration for '{role_id}'")
            
        return self
        
    def custom_role(self, role_id: str, permissions: List[str], title: str = None):
        """Create custom role - Rails convenience"""
        return self.create_custom_role(role_id, permissions, title=title)
        
    def app_role(self, app_name: str, permissions: List[str]):
        """Create application-specific role - Rails convenience"""
        role_id = f"{app_name}_app_role"
        return self.create_custom_role(
            role_id,
            permissions,
            title=f"{app_name.title()} Application Role",
            description=f"Custom role for {app_name} application"
        )
        
    def developer_role(self, permissions: List[str]):
        """Create developer role - Rails convenience"""
        return self.create_custom_role(
            "developer_role",
            permissions,
            title="Developer Role",
            description="Custom role for developers"
        )
        
    # Conditional access methods
    def time_condition(self, title: str, start_time: str, end_time: str):
        """Create time-based access condition"""
        expression = f'request.time.getHours() >= {start_time} && request.time.getHours() <= {end_time}'
        return {
            "title": title,
            "description": f"Access allowed between {start_time}:00 and {end_time}:00",
            "expression": expression
        }
        
    def ip_condition(self, title: str, allowed_ips: List[str]):
        """Create IP-based access condition"""
        ip_list = "', '".join(allowed_ips)
        expression = f"request.auth.access_levels.contains('accessPolicies/ACCESS_POLICY_NAME/accessLevels/IP_RESTRICTION')"
        return {
            "title": title,
            "description": f"Access allowed from specific IP addresses",
            "expression": expression
        }
        
    def resource_condition(self, title: str, resource_pattern: str):
        """Create resource-based access condition"""
        expression = f"resource.name.startsWith('{resource_pattern}')"
        return {
            "title": title,
            "description": f"Access limited to resources matching pattern",
            "expression": expression
        }
        
    def date_condition(self, title: str, expiry_date: str):
        """Create date-based expiration condition"""
        expression = f"request.time < timestamp('{expiry_date}')"
        return {
            "title": title,
            "description": f"Access expires on {expiry_date}",
            "expression": expression
        }
        
    # Audit and security configuration
    def enable_audit_logging(self, enabled: bool = True):
        """Enable IAM audit logging"""
        self.audit_logging_enabled = enabled
        return self
        
    def audit_logging(self):
        """Enable audit logging - Rails convenience"""
        return self.enable_audit_logging(True)
        
    def no_audit_logging(self):
        """Disable audit logging - Rails convenience"""
        return self.enable_audit_logging(False)
        
    def policy_version(self, version: int):
        """Set IAM policy version (1, 2, or 3)"""
        if version not in [1, 2, 3]:
            print(f"⚠️  Warning: Invalid policy version {version}. Valid versions: 1, 2, 3")
        self.policy_version = version
        return self
        
    # Labels and organization
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.iam_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.iam_labels[key] = value
        return self
        
    # Rails-like environment configurations
    def development_iam(self):
        """Configure for development environment - Rails convention"""
        return (self.policy_version(3)
                .enable_audit_logging(False)
                .label("environment", "development")
                .label("security", "relaxed"))
                
    def staging_iam(self):
        """Configure for staging environment - Rails convention"""
        return (self.policy_version(3)
                .enable_audit_logging(True)
                .label("environment", "staging")
                .label("security", "standard"))
                
    def production_iam(self):
        """Configure for production environment - Rails convention"""
        return (self.policy_version(3)
                .enable_audit_logging(True)
                .label("environment", "production")
                .label("security", "enhanced"))
                
    # Common role patterns
    def web_app_roles(self, app_name: str, dev_email: str = None):
        """Set up common roles for a web application - Rails convenience"""
        # Create app service account
        self.app_service_account(app_name)
        
        # Grant necessary roles to service account
        sa_email = f"{app_name}-sa@{self.project_id}.iam.gserviceaccount.com"
        self.service_account("roles/cloudsql.client", sa_email)
        self.service_account("roles/storage.objectViewer", sa_email)
        self.service_account("roles/secretmanager.secretAccessor", sa_email)
        
        # Grant developer access if provided
        if dev_email:
            self.user("roles/editor", dev_email)
            
        return self
        
    def microservices_roles(self, service_name: str, team_group: str = None):
        """Set up roles for microservices architecture - Rails convenience"""
        # Create service account for the microservice
        self.function_service_account(service_name)
        
        # Grant minimal required permissions
        sa_email = f"{service_name}-func-sa@{self.project_id}.iam.gserviceaccount.com"
        self.service_account("roles/cloudsql.client", sa_email)
        self.service_account("roles/pubsub.publisher", sa_email)
        self.service_account("roles/storage.objectViewer", sa_email)
        
        # Grant team access if provided
        if team_group:
            self.group("roles/viewer", team_group)
            
        return self
        
    def admin_setup(self, admin_email: str, backup_admin_email: str = None):
        """Set up administrative access - Rails convenience"""
        # Primary admin
        self.user("roles/owner", admin_email)
        self.user("roles/iam.serviceAccountAdmin", admin_email)
        
        # Backup admin with limited access
        if backup_admin_email:
            self.user("roles/editor", backup_admin_email)
            self.user("roles/iam.serviceAccountUser", backup_admin_email)
            
        return self
        
    def readonly_access(self, member: str, condition: Dict[str, str] = None):
        """Grant read-only access across all services - Rails convenience"""
        readonly_roles = [
            "roles/viewer",
            "roles/compute.viewer", 
            "roles/storage.objectViewer",
            "roles/cloudsql.viewer",
            "roles/monitoring.viewer",
            "roles/logging.viewer"
        ]
        
        for role in readonly_roles:
            self.add_member(role, member, condition)
            
        return self
        
    def security_admin_access(self, member: str):
        """Grant security administration access - Rails convenience"""
        security_roles = [
            "roles/iam.securityAdmin",
            "roles/iam.serviceAccountAdmin",
            "roles/cloudkms.admin",
            "roles/secretmanager.admin",
            "roles/networksecurity.admin"
        ]
        
        for role in security_roles:
            self.add_member(role, member)
            
        return self
        
    def monitoring_access(self, member: str):
        """Grant monitoring and logging access - Rails convenience"""
        monitoring_roles = [
            "roles/monitoring.admin",
            "roles/logging.admin",
            "roles/cloudtrace.admin",
            "roles/errorreporting.admin"
        ]
        
        for role in monitoring_roles:
            self.add_member(role, member)
            
        return self