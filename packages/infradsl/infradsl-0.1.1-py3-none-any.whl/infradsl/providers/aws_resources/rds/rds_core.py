from typing import Dict, Any
from ..base_resource import BaseAwsResource

class RDSCore(BaseAwsResource):
    """
    Core RDS class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.db_instance_id = None
        self.engine = None
        self.db_instance_class = None
        self.allocated_storage = None
        self.storage_type = None
        self.master_username = None
        self.master_password = None
        self.database_name = None
        self.vpc_security_groups = []
        self.subnet_group = None
        self.parameter_group = None
        self.option_group = None
        self.backup_retention_period = None
        self.backup_window = None
        self.maintenance_window = None
        self.is_multi_az = False
        self.publicly_accessible = False
        self.auto_minor_version_upgrade = True
        self.storage_encrypted = True
        self.kms_key_id = None
        self.tags = {}
        self.instance_exists = False
        self.endpoint = None
        self.db_port = None
        self.status = None
        self.rds_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        return None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        return None
    
    def create(self):
        """Create/update RDS instance - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .rds_lifecycle import RDSLifecycleMixin
        # Call the lifecycle mixin's create method
        return RDSLifecycleMixin.create(self)

    def destroy(self):
        """Destroy RDS instance - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .rds_lifecycle import RDSLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return RDSLifecycleMixin.destroy(self)

    def preview(self):
        """Preview RDS instance configuration"""
        return {
            "resource_type": "AWS RDS Database Instance",
            "instance_id": self.db_instance_id or self.name,
            "engine": self.engine,
            "instance_class": self.db_instance_class,
            "allocated_storage": self.allocated_storage,
            "storage_type": self.storage_type,
            "master_username": self.master_username,
            "database_name": self.database_name,
            "multi_az": self.is_multi_az,
            "publicly_accessible": self.publicly_accessible,
            "storage_encrypted": self.storage_encrypted,
            "backup_retention_period": self.backup_retention_period,
            "auto_minor_version_upgrade": self.auto_minor_version_upgrade,
            "vpc_security_groups_count": len(self.vpc_security_groups),
            "tags_count": len(self.tags),
            "estimated_monthly_cost": self._estimate_monthly_cost()
        }
    
    def get_rds_client(self, region: str = None):
        """Get RDS client for this resource"""
        return self.get_client('rds', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region)
    
    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for RDS instance"""
        if not self.db_instance_class:
            return "$0.00"
        
        # Basic cost estimation based on instance class
        cost_map = {
            "db.t3.micro": 15.33,
            "db.t3.small": 30.66,
            "db.t3.medium": 61.32,
            "db.t3.large": 122.64,
            "db.t3.xlarge": 245.28,
            "db.m5.large": 158.40,
            "db.m5.xlarge": 316.80,
            "db.m5.2xlarge": 633.60,
            "db.r5.large": 204.48,
            "db.r5.xlarge": 408.96
        }
        
        base_cost = cost_map.get(self.db_instance_class, 100.00)
        
        # Add storage cost
        storage_cost = 0
        if self.allocated_storage:
            if self.storage_type == 'gp2':
                storage_cost = self.allocated_storage * 0.115  # $0.115 per GB per month
            elif self.storage_type == 'io1':
                storage_cost = self.allocated_storage * 0.125  # $0.125 per GB per month
        
        total_cost = base_cost + storage_cost
        
        if self.is_multi_az:
            total_cost *= 2  # Multi-AZ doubles the cost
        
        return f"${total_cost:.2f}" 