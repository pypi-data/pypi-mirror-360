"""
InfraDSL Marketplace - Company Template System

This module implements the company template inheritance system that allows
organizations to create reusable infrastructure patterns that inherit
company policies, standards, and best practices.

Example Usage:
    # Company creates base patterns
    class NolimitCityBase(CompanyTemplateBase):
        company_name = "nolimitcity"
        
        def __init__(self, name):
            super().__init__(name)
            self.apply_company_policies()
    
    class ProdVM(NolimitCityBase, GoogleCloud.VM):
        def __init__(self, name):
            super().__init__(name)
            self.apply_production_standards()
    
    # Teams use the patterns
    from infradsl.marketplace.nolimitcity import ProdVM
    vm = ProdVM("web-server-1")
    vm.create()
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
from dataclasses import dataclass

from .registry_client import RegistryClient


@dataclass
class CompanyPolicy:
    """Company infrastructure policy"""
    name: str
    description: str
    required: bool
    category: str  # "security", "compliance", "cost", "monitoring"
    implementation: callable
    validation: Optional[callable] = None


@dataclass 
class CompanyStandard:
    """Company infrastructure standard"""
    name: str
    description: str
    default_value: Any
    allowed_values: Optional[List[Any]] = None
    validation_rule: Optional[str] = None


class CompanyTemplateBase(ABC):
    """
    Base class for company-specific templates
    
    This class provides the foundation for creating company-specific
    infrastructure patterns that automatically inherit organizational
    policies, standards, and best practices.
    """
    
    # Company configuration (to be overridden by subclasses)
    company_name: str = ""
    company_display_name: str = ""
    company_policies: List[CompanyPolicy] = []
    company_standards: Dict[str, CompanyStandard] = {}
    
    def __init__(self, name: str):
        """
        Initialize company template base
        
        Args:
            name: Resource name
        """
        self.name = name
        self.company_config = {}
        self.applied_policies = []
        self.compliance_status = {}
        self._registry_client = None
        
        # Load company configuration
        self._load_company_config()
        
        # Initialize base resource
        self._init_base_resource()
    
    def _load_company_config(self):
        """Load company-specific configuration"""
        if not self.company_name:
            return
        
        # Try to load from registry first
        try:
            self._registry_client = RegistryClient(workspace=self.company_name)
            # Load company configuration from registry
            # This would fetch workspace settings, policies, standards, etc.
        except Exception:
            # Fall back to local configuration
            pass
        
        # Load local company configuration if available
        config_file = os.path.expanduser(f"~/.infradsl/companies/{self.company_name}.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.company_config = json.load(f)
    
    @abstractmethod
    def _init_base_resource(self):
        """Initialize the base resource (implemented by specific resource types)"""
        pass
    
    def apply_company_policies(self):
        """Apply all company policies to the resource"""
        for policy in self.company_policies:
            try:
                policy.implementation(self)
                self.applied_policies.append(policy.name)
                self.compliance_status[policy.name] = "compliant"
            except Exception as e:
                self.compliance_status[policy.name] = f"failed: {str(e)}"
                if policy.required:
                    raise RuntimeError(f"Required policy '{policy.name}' failed: {e}")
    
    def apply_company_standards(self):
        """Apply company standards with default values"""
        for standard_name, standard in self.company_standards.items():
            if not hasattr(self, standard_name):
                setattr(self, standard_name, standard.default_value)
    
    def validate_compliance(self) -> Dict[str, str]:
        """Validate compliance with company policies"""
        results = {}
        
        for policy in self.company_policies:
            if policy.validation:
                try:
                    is_compliant = policy.validation(self)
                    results[policy.name] = "compliant" if is_compliant else "non-compliant"
                except Exception as e:
                    results[policy.name] = f"validation_error: {str(e)}"
            else:
                results[policy.name] = self.compliance_status.get(policy.name, "unknown")
        
        return results
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get company template information"""
        return {
            "company_name": self.company_name,
            "company_display_name": self.company_display_name,
            "applied_policies": self.applied_policies,
            "compliance_status": self.compliance_status,
            "template_class": self.__class__.__name__,
            "resource_name": self.name
        }


class NolimitCityBase(CompanyTemplateBase):
    """
    Base class for Nolimit City infrastructure templates
    
    Automatically applies Nolimit City's infrastructure policies:
    - Monitoring with Discord webhooks
    - Conservative auto-remediation
    - European regions (GDPR compliance)
    - Cost tracking and alerts
    - Security scanning
    """
    
    company_name = "nolimitcity"
    company_display_name = "Nolimit City"
    
    # Company-specific configuration
    DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1389316853591048303/HA94V793l2ut0mhs0ln8hsqpby9lzlky_hnpomqljjzp6vtdpp"
    COMPANY_REGION = "europe-north1"
    COMPANY_VPC = "nolimitcity-vpc"
    BACKUP_RETENTION = "30d"
    
    company_policies = [
        CompanyPolicy(
            name="gdpr_compliance",
            description="Ensure GDPR compliance by using European regions",
            required=True,
            category="compliance",
            implementation=lambda self: self._apply_gdpr_compliance()
        ),
        CompanyPolicy(
            name="monitoring_policy", 
            description="Apply company monitoring standards",
            required=True,
            category="monitoring",
            implementation=lambda self: self._apply_monitoring_policy()
        ),
        CompanyPolicy(
            name="backup_policy",
            description="Apply company backup retention policies",
            required=True,
            category="data",
            implementation=lambda self: self._apply_backup_policy()
        ),
        CompanyPolicy(
            name="cost_policy",
            description="Apply cost tracking and alerts",
            required=False,
            category="cost",
            implementation=lambda self: self._apply_cost_policy()
        ),
        CompanyPolicy(
            name="security_policy",
            description="Apply security scanning and hardening",
            required=True,
            category="security",
            implementation=lambda self: self._apply_security_policy()
        ),
        CompanyPolicy(
            name="tagging_policy",
            description="Apply company resource tagging standards",
            required=True,
            category="governance",
            implementation=lambda self: self._apply_tagging_policy()
        )
    ]
    
    company_standards = {
        "region": CompanyStandard(
            name="region",
            description="Default region for resources",
            default_value="europe-north1",
            allowed_values=["europe-north1", "europe-west1", "europe-west2"]
        ),
        "backup_retention": CompanyStandard(
            name="backup_retention", 
            description="Backup retention period",
            default_value="30d",
            allowed_values=["7d", "30d", "90d", "1y"]
        ),
        "environment": CompanyStandard(
            name="environment",
            description="Environment type",
            default_value="production",
            allowed_values=["development", "staging", "production"]
        )
    }
    
    def _init_base_resource(self):
        """Initialize base resource configuration"""
        # This will be called by the specific resource type
        pass
    
    def _apply_gdpr_compliance(self):
        """Apply GDPR compliance policies"""
        # Ensure European region
        if hasattr(self, 'zone') and callable(getattr(self, 'zone')):
            if not any(region in str(getattr(self, '_zone', '')) 
                      for region in ["europe-north1", "europe-west1", "europe-west2"]):
                self.zone(f"{self.COMPANY_REGION}-a")
        
        # Apply data protection settings
        if hasattr(self, 'tags') and callable(getattr(self, 'tags')):
            gdpr_tags = {
                "data_classification": "eu_personal_data",
                "gdpr_compliant": "true",
                "data_region": "eu"
            }
            existing_tags = getattr(self, '_tags', {})
            existing_tags.update(gdpr_tags)
            self.tags(existing_tags)
    
    def _apply_monitoring_policy(self):
        """Apply company monitoring policy"""
        if hasattr(self, 'check_state') and callable(getattr(self, 'check_state')):
            self.check_state(
                check_interval="30m",
                auto_remediate="conservative",
                webhook=self.DISCORD_WEBHOOK,
                enable_auto_fix=True
            )
    
    def _apply_backup_policy(self):
        """Apply company backup policy"""
        if hasattr(self, 'backup') and callable(getattr(self, 'backup')):
            self.backup(
                enabled=True,
                retention=self.BACKUP_RETENTION,
                schedule="daily",
                encryption=True
            )
    
    def _apply_cost_policy(self):
        """Apply cost tracking and alerts"""
        if hasattr(self, 'cost_alerts') and callable(getattr(self, 'cost_alerts')):
            self.cost_alerts(
                monthly_limit=500,  # $500/month
                alert_thresholds=[50, 80, 95],  # Alert at 50%, 80%, 95%
                webhook=self.DISCORD_WEBHOOK
            )
    
    def _apply_security_policy(self):
        """Apply security hardening"""
        if hasattr(self, 'security') and callable(getattr(self, 'security')):
            self.security(
                vulnerability_scanning=True,
                compliance_checks=["CIS", "NIST"],
                automatic_patching=True,
                firewall_logging=True
            )
    
    def _apply_tagging_policy(self):
        """Apply company tagging standards"""
        if hasattr(self, 'tags') and callable(getattr(self, 'tags')):
            company_tags = {
                "ManagedBy": "InfraDSL",
                "Company": "NolimitCity",
                "CostCenter": "engineering",
                "Environment": getattr(self, 'environment', 'production'),
                "Owner": os.getenv('USER', 'unknown'),
                "CreatedAt": datetime.utcnow().isoformat(),
                "Project": "infradsl"
            }
            
            existing_tags = getattr(self, '_tags', {})
            existing_tags.update(company_tags)
            self.tags(existing_tags)


def create_company_template_loader(workspace_name: str):
    """
    Create a dynamic template loader for a company workspace
    
    This function creates a module-like object that can be used to import
    templates from a company workspace.
    
    Usage:
        nolimitcity = create_company_template_loader("nolimitcity")
        ProdVM = nolimitcity.ProdVM
        
        vm = ProdVM("web-server")
        vm.create()
    
    Args:
        workspace_name: Name of the workspace
        
    Returns:
        Template loader object
    """
    
    class CompanyTemplateLoader:
        def __init__(self, workspace: str):
            self.workspace = workspace
            self._registry_client = RegistryClient(workspace=workspace)
            self._cache = {}
        
        def __getattr__(self, template_name: str) -> Type:
            """Dynamically load template from registry"""
            if template_name in self._cache:
                return self._cache[template_name]
            
            try:
                # Convert PascalCase to kebab-case for registry lookup
                template_slug = self._pascal_to_kebab(template_name)
                template_ref = f"{self.workspace}/{template_slug}"
                
                # Import template from registry
                template_class = self._registry_client.import_template(template_ref)
                
                # Cache the loaded template
                self._cache[template_name] = template_class
                
                return template_class
                
            except Exception as e:
                raise AttributeError(f"Template '{template_name}' not found in workspace '{self.workspace}': {e}")
        
        def list_templates(self) -> List[str]:
            """List all available templates in the workspace"""
            templates = self._registry_client.search_templates()
            return [self._kebab_to_pascal(t.name) for t in templates if t.workspace_id]
        
        def search(self, query: str = "", category: str = "", providers: List[str] = []) -> List[str]:
            """Search for templates in the workspace"""
            templates = self._registry_client.search_templates(
                query=query, 
                category=category, 
                providers=providers
            )
            return [self._kebab_to_pascal(t.name) for t in templates if t.workspace_id]
        
        def _pascal_to_kebab(self, name: str) -> str:
            """Convert PascalCase to kebab-case"""
            import re
            return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
        
        def _kebab_to_pascal(self, name: str) -> str:
            """Convert kebab-case to PascalCase"""
            return ''.join(word.capitalize() for word in name.split('-'))
    
    return CompanyTemplateLoader(workspace_name)


# Example usage: Create company-specific template classes
class NolimitCityProdVM(NolimitCityBase):
    """
    Nolimit City Production VM Template
    
    Pre-configured with:
    - European region (GDPR compliance)
    - Company monitoring and alerting
    - Security hardening
    - Backup policies
    - Cost tracking
    """
    
    def _init_base_resource(self):
        """Initialize as Google Cloud VM with production standards"""
        # This would typically inherit from GoogleCloud.VM
        # For now, we'll simulate the configuration
        
        # Apply production VM standards
        self.machine_type = "e2-standard-4"
        self.disk_size = 50
        self.image = "debian-11"
        self.zone_value = f"{self.COMPANY_REGION}-a"
        
        # Apply company policies
        self.apply_company_policies()
        self.apply_company_standards()
    
    def machine_type(self, machine_type: str):
        """Set machine type with validation"""
        allowed_types = [
            "e2-micro", "e2-small", "e2-medium", "e2-standard-2", 
            "e2-standard-4", "e2-standard-8", "c2-standard-4", "c2-standard-8"
        ]
        
        if machine_type not in allowed_types:
            raise ValueError(f"Machine type '{machine_type}' not allowed. Use: {allowed_types}")
        
        self.machine_type = machine_type
        return self
    
    def zone(self, zone: str):
        """Set zone with GDPR compliance validation"""
        if not zone.startswith(("europe-north1", "europe-west1", "europe-west2")):
            raise ValueError(f"Zone '{zone}' not GDPR compliant. Must use European regions.")
        
        self.zone_value = zone
        return self
    
    def disk_size(self, size: int):
        """Set disk size with minimum requirements"""
        if size < 20:
            raise ValueError("Minimum disk size is 20GB for production VMs")
        
        self.disk_size = size
        return self
    
    def create(self):
        """Create the VM with final compliance validation"""
        # Validate compliance before creation
        compliance = self.validate_compliance()
        
        non_compliant = [k for k, v in compliance.items() if v != "compliant"]
        if non_compliant:
            raise RuntimeError(f"Cannot create VM - non-compliant policies: {non_compliant}")
        
        print(f"✅ Creating Nolimit City Production VM: {self.name}")
        print(f"   Machine Type: {self.machine_type}")
        print(f"   Zone: {self.zone_value}")
        print(f"   Disk Size: {self.disk_size}GB")
        print(f"   Compliance Status: {len(compliance)} policies applied")
        
        # In real implementation, this would call the actual resource creation
        return {"instance_id": f"nolimitcity-{self.name}", "status": "running"}


class NolimitCityDevVM(NolimitCityBase):
    """
    Nolimit City Development VM Template
    
    Lighter configuration for development:
    - Smaller instances
    - Reduced monitoring
    - Shorter backup retention
    - Cost optimized
    """
    
    def _init_base_resource(self):
        """Initialize as development VM"""
        self.machine_type = "e2-micro"
        self.disk_size = 20
        self.image = "debian-11"
        self.zone_value = f"{self.COMPANY_REGION}-a"
        self.environment = "development"
        
        # Apply reduced policies for development
        self._apply_dev_policies()
    
    def _apply_dev_policies(self):
        """Apply development-specific policies"""
        # Override some base policies for development
        self.BACKUP_RETENTION = "7d"
        
        # Apply base policies
        self.apply_company_policies()
        self.apply_company_standards()
    
    def machine_type(self, machine_type: str):
        """Set machine type (development constraints)"""
        allowed_types = ["e2-micro", "e2-small", "e2-medium", "e2-standard-2"]
        
        if machine_type not in allowed_types:
            raise ValueError(f"Development VMs limited to: {allowed_types}")
        
        self.machine_type = machine_type
        return self
    
    def create(self):
        """Create development VM"""
        print(f"✅ Creating Nolimit City Development VM: {self.name}")
        print(f"   Machine Type: {self.machine_type}")
        print(f"   Environment: development")
        
        return {"instance_id": f"nolimitcity-dev-{self.name}", "status": "running"}