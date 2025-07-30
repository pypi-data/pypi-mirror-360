class RDSConfigurationMixin:
    """
    Mixin for RDS chainable configuration methods.
    """
    def postgresql(self):
        """Set the database engine to PostgreSQL"""
        self.engine = "postgres"
        return self

    def private_subnet(self):
        """Configure the RDS instance to be in a private subnet (not publicly accessible)"""
        self.publicly_accessible = False
        return self

    def encrypted_storage(self):
        """Enable encrypted storage for the RDS instance"""
        self.storage_encrypted = True
        return self

    def credentials(self, secrets_manager_resource):
        """Set master credentials using a SecretsManager resource"""
        self.master_username = secrets_manager_resource.secret_name  # Assuming secret_name is the username
        self.master_password = secrets_manager_resource.secret_value  # Assuming secret_value is the password
        return self

    def engine(self, engine: str):
        """Set the database engine"""
        self.engine = engine
        return self

    def instance_class(self, instance_class: str):
        """Set the instance class"""
        self.db_instance_class = instance_class
        return self

    def storage(self, allocated_storage: int, storage_type: str = 'gp2'):
        """Set storage configuration"""
        self.allocated_storage = allocated_storage
        self.storage_type = storage_type
        return self

    def database(self, database_name: str):
        """Set the database name"""
        self.database_name = database_name
        return self

    def vpc_security_groups(self, security_group_ids: list):
        """Set VPC security groups"""
        self.vpc_security_groups = security_group_ids
        return self

    def subnet_group(self, subnet_group_name: str):
        """Set the subnet group"""
        self.subnet_group = subnet_group_name
        return self

    def backup(self, retention_period: int = 7, window: str = None):
        """Configure backup settings"""
        self.backup_retention_period = retention_period
        if window:
            self.backup_window = window
        return self

    def maintenance(self, window: str):
        """Set maintenance window"""
        self.maintenance_window = window
        return self

    def multi_az(self, enabled: bool = True):
        """Enable or disable Multi-AZ deployment"""
        self.is_multi_az = enabled
        return self

    def publicly_accessible(self, enabled: bool = False):
        """Enable or disable public accessibility"""
        self.publicly_accessible = enabled
        return self

    def encryption(self, enabled: bool = True, kms_key_id: str = None):
        """Enable or disable storage encryption"""
        self.storage_encrypted = enabled
        if kms_key_id:
            self.kms_key_id = kms_key_id
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the RDS instance"""
        self.tags[key] = value
        return self
    
    def mysql(self):
        """Set the database engine to MySQL"""
        self.engine = "mysql"
        return self
    
    def aurora_mysql(self):
        """Set the database engine to Aurora MySQL"""
        self.engine = "aurora-mysql"
        return self
    
    def aurora_postgresql(self):
        """Set the database engine to Aurora PostgreSQL"""
        self.engine = "aurora-postgresql"
        return self
    
    def mariadb(self):
        """Set the database engine to MariaDB"""
        self.engine = "mariadb"
        return self
    
    def oracle(self):
        """Set the database engine to Oracle"""
        self.engine = "oracle-ee"
        return self
    
    def sql_server(self):
        """Set the database engine to SQL Server"""
        self.engine = "sqlserver-ex"
        return self
    
    def instance_id(self, instance_identifier: str):
        """Set the database instance identifier"""
        self.db_instance_id = instance_identifier
        return self
    
    def master_credentials(self, username: str, password: str):
        """Set master username and password"""
        self.master_username = username
        self.master_password = password
        return self
    
    def port(self, port: int):
        """Set the database port"""
        self.db_port = port
        return self
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing RDS for {priority}")
        
        # Apply AWS RDS-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective database")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance database")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable database")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant database")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS RDS-specific cost optimizations"""
        # Use smaller instance class for cost savings
        if not self.db_instance_class or self.db_instance_class.startswith('db.m5'):
            print("   💰 Using cost-effective db.t3.small instance class")
            self.db_instance_class = "db.t3.small"
        
        # Use gp2 storage for cost savings
        if not self.storage_type:
            print("   💰 Using gp2 storage for cost efficiency")
            self.storage_type = "gp2"
        
        # Disable Multi-AZ for cost savings (warning)
        if self.multi_az:
            print("   💰 Consider disabling Multi-AZ for cost savings (impacts availability)")
        
        # Add cost optimization tags
        self.tags.update({
            "cost-optimized": "true",
            "instance-right-sized": "true"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS RDS-specific performance optimizations"""
        # Use larger instance class for performance
        if not self.db_instance_class or self.db_instance_class.startswith('db.t3'):
            print("   ⚡ Using high-performance db.m5.large instance class")
            self.db_instance_class = "db.m5.large"
        
        # Use io1 storage for better IOPS
        if not self.storage_type:
            print("   ⚡ Using io1 storage for high IOPS performance")
            self.storage_type = "io1"
        
        # Enable Multi-AZ for performance and availability
        print("   ⚡ Enabling Multi-AZ for high availability")
        self.multi_az = True
        
        # Add performance tags
        self.tags.update({
            "performance-optimized": "true",
            "high-iops": "enabled"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS RDS-specific reliability optimizations"""
        # Enable Multi-AZ for reliability
        print("   🛡️ Enabling Multi-AZ for high availability")
        self.multi_az = True
        
        # Configure backups
        print("   🛡️ Configuring 30-day backup retention")
        self.backup_retention_period = 30
        
        # Enable encryption
        print("   🛡️ Enabling storage encryption")
        self.storage_encrypted = True
        
        # Make database private
        print("   🛡️ Making database private (not publicly accessible)")
        self.publicly_accessible = False
        
        # Add reliability tags
        self.tags.update({
            "reliability-optimized": "true",
            "multi-az": "enabled",
            "encrypted": "true",
            "backup-enabled": "true"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS RDS-specific compliance optimizations"""
        # Enable encryption for compliance
        print("   📋 Enabling storage encryption for compliance")
        self.storage_encrypted = True
        
        # Make database private
        print("   📋 Making database private for security compliance")
        self.publicly_accessible = False
        
        # Enable automated backups
        print("   📋 Enabling automated backups for compliance")
        self.backup_retention_period = 7
        
        # Enable minor version upgrades for security
        print("   📋 Enabling automatic minor version upgrades for security")
        self.auto_minor_version_upgrade = True
        
        # Add compliance tags
        self.tags.update({
            "compliance-optimized": "true",
            "encrypted": "true",
            "private": "true",
            "audit-enabled": "true"
        }) 