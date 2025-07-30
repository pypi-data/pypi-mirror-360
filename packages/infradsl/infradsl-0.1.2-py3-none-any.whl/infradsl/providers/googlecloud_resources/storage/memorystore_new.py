"""
GCP Memorystore Complete Implementation

Complete Memorystore implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .memorystore_core import MemorystoreCore
from .memorystore_configuration import MemorystoreConfigurationMixin
from .memorystore_lifecycle import MemorystoreLifecycleMixin


class Memorystore(MemorystoreCore, MemorystoreConfigurationMixin, MemorystoreLifecycleMixin):
    """
    Complete Google Cloud Memorystore implementation.
    
    This class combines:
    - MemorystoreCore: Basic instance attributes and authentication
    - MemorystoreConfigurationMixin: Chainable configuration methods
    - MemorystoreLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent Redis configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Redis versions 5.0, 6.x, and 7.0 support
    - High availability with automatic failover
    - Read replicas for improved read performance
    - Persistence and backup configuration
    - Security features (authentication, encryption)
    - Common caching patterns (session store, app cache, high-performance)
    - Industry-specific configurations (gaming, financial, IoT, e-commerce)
    - Environment-specific settings (development, staging, production)
    - Performance optimization and Redis parameter tuning
    
    Example:
        # Simple session store
        cache = Memorystore("session-cache")
        cache.session_store()
        cache.create()
        
        # High-performance application cache
        cache = Memorystore("app-cache")
        cache.high_performance_cache()
        cache.create()
        
        # Development cache
        cache = Memorystore("dev-cache")
        cache.development()
        cache.create()
        
        # Custom configuration
        cache = Memorystore("custom-cache")
        cache.memory_size(8).standard_ha().auth_enabled().encrypted()
        cache.read_replicas(2).persistence(True)
        cache.redis_config("maxmemory-policy", "allkeys-lru")
        cache.create()
        
        # Industry-specific cache
        cache = Memorystore("gaming-cache")
        cache.gaming_cache()
        cache.create()
        
        # Cross-Cloud Magic optimization
        cache = Memorystore("optimized-cache")
        cache.application_cache()
        cache.optimize_for("performance")
        cache.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Memorystore with instance name.
        
        Args:
            name: Instance name (must be valid GCP instance name)
        """
        # Initialize all parent classes
        MemorystoreCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Memorystore instance"""
        instance_type = self._get_instance_type_from_config()
        persistence = "persistent" if self.has_persistence() else "in-memory"
        replicas = f"{self.replica_count} replicas" if self.has_read_replicas() else "no replicas"
        status = "configured" if self.memory_size_gb > 0 else "unconfigured"
        
        return (f"Memorystore(name='{self.instance_id}', "
                f"type='{instance_type}', "
                f"memory={self.memory_size_gb}GB, "
                f"tier='{self.tier}', "
                f"version='{self.redis_version}', "
                f"persistence='{persistence}', "
                f"replicas='{replicas}', "
                f"region='{self.region}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Memorystore configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze instance configuration
        instance_patterns = []
        
        # Detect patterns from labels and configuration
        purpose = self.instance_labels.get("purpose", "").lower()
        if purpose:
            if "session" in purpose:
                instance_patterns.append("session_store")
            elif "cache" in purpose:
                instance_patterns.append("application_cache")
            elif "high-performance" in purpose:
                instance_patterns.append("high_performance")
            elif "analytics" in purpose:
                instance_patterns.append("analytics")
        
        # Check industry
        industry = self.instance_labels.get("industry", "").lower()
        if industry:
            instance_patterns.append(f"{industry}_optimized")
        
        # Check environment
        environment = self.instance_labels.get("environment", "").lower()
        if environment:
            instance_patterns.append(f"{environment}_environment")
        
        # Check optimization
        optimization = self.instance_labels.get("optimization", "").lower()
        if optimization:
            instance_patterns.append(f"{optimization}_optimized")
        
        # Performance characteristics
        performance_features = []
        if self.tier == 'STANDARD_HA':
            performance_features.append("high_availability")
            performance_features.append("automatic_failover")
        if self.has_read_replicas():
            performance_features.append("read_scaling")
        if self.has_encryption():
            performance_features.append("encryption_enabled")
        if self.has_persistence():
            performance_features.append("data_persistence")
        
        summary = {
            "instance_id": self.instance_id,
            "instance_name": self.instance_name,
            "instance_description": self.instance_description,
            "instance_type": self._get_instance_type_from_config(),
            "instance_patterns": instance_patterns,
            
            # Configuration
            "memory_size_gb": self.memory_size_gb,
            "tier": self.tier,
            "redis_version": self.redis_version,
            "region": self.region,
            "zone": self.zone,
            
            # Security
            "auth_enabled": self.auth_enabled,
            "transit_encryption_mode": self.transit_encryption_mode,
            "has_encryption": self.has_encryption(),
            "customer_managed_key": self.customer_managed_key,
            
            # Network
            "authorized_network": self.authorized_network,
            "reserved_ip_range": self.reserved_ip_range,
            "connect_mode": self.connect_mode,
            
            # Persistence
            "persistence_config": self.persistence_config,
            "has_persistence": self.has_persistence(),
            "persistence_mode": self.persistence_config.get('persistence_mode', 'DISABLED'),
            
            # Read replicas
            "read_replicas_mode": self.read_replicas_mode,
            "replica_count": self.replica_count,
            "has_read_replicas": self.has_read_replicas(),
            
            # Maintenance
            "maintenance_policy": self.maintenance_policy,
            
            # Redis configuration
            "redis_configs": self.redis_configs,
            "redis_config_count": len(self.redis_configs),
            
            # Labels and metadata
            "labels": self.instance_labels,
            "label_count": len(self.instance_labels),
            "annotations": self.instance_annotations,
            
            # Connection details
            "host": self.host,
            "port": self.port,
            "redis_endpoint": self.redis_endpoint,
            "read_endpoint": self.read_endpoint,
            "connection_string": self.connection_string(),
            
            # State
            "state": {
                "exists": self.instance_exists,
                "created": self.instance_created,
                "instance_state": self.instance_state,
                "deployment_status": self.deployment_status
            },
            
            # Performance
            "performance_features": performance_features,
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_memorystore_cost():.2f}"
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n⚡ Memorystore Redis Configuration: {self.instance_id}")
        print(f"   🆔 Instance ID: {self.instance_id}")
        print(f"   📝 Description: {self.instance_description}")
        print(f"   🏗️  Instance Type: {self._get_instance_type_from_config().replace('_', ' ').title()}")
        
        # Memory and tier
        print(f"\n📊 Memory & Performance:")
        print(f"   💾 Memory Size: {self.memory_size_gb}GB")
        print(f"   🏗️  Tier: {self.tier}")
        print(f"   ⚡ Redis Version: {self.redis_version}")
        print(f"   📍 Region: {self.region}")
        if self.zone:
            print(f"   🌐 Zone: {self.zone}")
        
        # Security
        print(f"\n🔒 Security Configuration:")
        print(f"   🔑 Authentication: {'✅ Enabled' if self.auth_enabled else '❌ Disabled'}")
        print(f"   🔐 Transit Encryption: {self.transit_encryption_mode}")
        if self.customer_managed_key:
            print(f"   🔐 Customer Managed Key: {self.customer_managed_key}")
        
        # Network
        print(f"\n🌐 Network Configuration:")
        if self.authorized_network:
            network_name = self.authorized_network.split('/')[-1]
            print(f"   🔗 VPC Network: {network_name}")
        else:
            print(f"   🔗 VPC Network: default")
        
        if self.reserved_ip_range:
            print(f"   📍 IP Range: {self.reserved_ip_range}")
        else:
            print(f"   📍 IP Range: Auto-assigned")
        
        # Persistence
        persistence_mode = self.persistence_config.get('persistence_mode', 'DISABLED')
        print(f"\n💾 Persistence Configuration:")
        print(f"   📊 Mode: {persistence_mode}")
        
        if persistence_mode != 'DISABLED':
            period = self.persistence_config.get('rdb_snapshot_period', 'Unknown')
            backup_time = self.persistence_config.get('rdb_snapshot_start_time', 'Unknown')
            print(f"   📅 Backup Period: {period}")
            print(f"   ⏰ Backup Schedule: {backup_time}")
        
        # Read replicas
        print(f"\n📚 Read Replicas:")
        if self.read_replicas_mode == 'READ_REPLICAS_ENABLED':
            print(f"   ✅ Enabled: {self.replica_count} replicas")
        else:
            print(f"   ❌ Disabled")
        
        # Redis configuration
        if self.redis_configs:
            print(f"\n⚙️  Redis Configuration ({len(self.redis_configs)} parameters):")
            for key, value in list(self.redis_configs.items())[:10]:
                print(f"   • {key}: {value}")
            if len(self.redis_configs) > 10:
                print(f"   • ... and {len(self.redis_configs) - 10} more parameters")
        
        # Maintenance
        if self.maintenance_policy:
            print(f"\n🔧 Maintenance Configuration:")
            if 'weekly_maintenance_window' in self.maintenance_policy:
                window = self.maintenance_policy['weekly_maintenance_window'][0]
                day = window.get('day', 'UNKNOWN')
                hour = window.get('start_time', {}).get('hours', 0)
                print(f"   📅 Window: {day} at {hour:02d}:00")
        
        # Labels
        if self.instance_labels:
            print(f"\n🏷️  Labels ({len(self.instance_labels)}):")
            for key, value in list(self.instance_labels.items())[:10]:
                print(f"   • {key}: {value}")
            if len(self.instance_labels) > 10:
                print(f"   • ... and {len(self.instance_labels) - 10} more")
        
        # Connection details
        if self.redis_endpoint:
            print(f"\n🔗 Connection Details:")
            print(f"   🌐 Primary Endpoint: {self.redis_endpoint}")
            if self.read_endpoint:
                print(f"   📖 Read Endpoint: {self.read_endpoint}")
            print(f"   🔌 Connection String: {self.connection_string()}")
        
        # Performance characteristics
        print(f"\n🚀 Performance Characteristics:")
        print(f"   ⚡ Latency: Sub-millisecond")
        print(f"   📊 Throughput: 100K+ ops/sec")
        if self.tier == 'STANDARD_HA':
            print(f"   🔄 Automatic failover: ✅ Enabled")
            print(f"   📈 Availability SLA: 99.9%")
        else:
            print(f"   📈 Availability SLA: 99.5%")
        
        if self.has_read_replicas():
            print(f"   📚 Read scaling: ✅ {self.replica_count} replicas")
        
        # Cost
        print(f"\n💰 Estimated Cost: ${self._estimate_memorystore_cost():.2f}/month")
        
        # State
        if self.instance_exists:
            print(f"\n📊 State:")
            print(f"   ✅ Exists: {self.instance_exists}")
            print(f"   🆔 Resource: {self.instance_name}")
            if self.instance_state:
                print(f"   📊 Status: {self.instance_state}")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze Memorystore security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "risk_factors": []
        }
        
        # Authentication analysis
        if self.auth_enabled:
            analysis["security_score"] += 25
            analysis["security_features"].append("Redis AUTH enabled")
        else:
            analysis["risk_factors"].append("No authentication enabled")
            analysis["recommendations"].append("Enable Redis AUTH for access control")
        
        # Encryption analysis
        if self.transit_encryption_mode == 'SERVER_AUTHENTICATION':
            analysis["security_score"] += 25
            analysis["security_features"].append("Transit encryption enabled")
        elif self.transit_encryption_mode == 'DISABLED':
            analysis["risk_factors"].append("No transit encryption")
            analysis["recommendations"].append("Enable transit encryption for data in transit")
        
        # Network analysis
        if self.authorized_network and 'default' not in self.authorized_network:
            analysis["security_score"] += 15
            analysis["security_features"].append("Custom VPC network")
        else:
            analysis["recommendations"].append("Use custom VPC network for better isolation")
        
        if self.reserved_ip_range:
            analysis["security_score"] += 10
            analysis["security_features"].append("Reserved IP range configured")
        
        # Tier analysis
        if self.tier == 'STANDARD_HA':
            analysis["security_score"] += 10
            analysis["security_features"].append("High availability for better resilience")
        
        # Persistence analysis (for audit trails)
        if self.has_persistence():
            analysis["security_score"] += 10
            analysis["security_features"].append("Persistence enabled for data durability")
        
        # Labels analysis
        security_labels = ["security", "compliance", "audit", "encryption"]
        for label in security_labels:
            if label in self.instance_labels:
                analysis["security_score"] += 2
                analysis["security_features"].append(f"Security label: {label}")
        
        # Environment analysis
        env_label = self.instance_labels.get("environment", "").lower()
        if env_label == "production":
            if self.auth_enabled and self.has_encryption():
                analysis["security_score"] += 5
                analysis["security_features"].append("Production environment with security")
            else:
                analysis["risk_factors"].append("Production environment without full security")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Memorystore performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_factors": [],
            "latency_factors": []
        }
        
        # Tier analysis
        if self.tier == 'STANDARD_HA':
            analysis["performance_score"] += 25
            analysis["performance_factors"].append("Standard HA tier for high availability")
        else:
            analysis["performance_score"] += 15
            analysis["recommendations"].append("Consider Standard HA tier for better availability")
        
        # Memory size analysis
        if self.memory_size_gb >= 16:
            analysis["performance_score"] += 20
            analysis["performance_factors"].append("Large memory size for high throughput")
        elif self.memory_size_gb >= 4:
            analysis["performance_score"] += 15
            analysis["performance_factors"].append("Adequate memory size")
        else:
            analysis["performance_score"] += 10
            analysis["recommendations"].append("Consider larger memory size for better performance")
        
        # Read replicas analysis
        if self.has_read_replicas():
            analysis["performance_score"] += 20
            analysis["performance_factors"].append(f"Read replicas ({self.replica_count}) for read scaling")
        else:
            analysis["recommendations"].append("Consider read replicas for read-heavy workloads")
        
        # Redis configuration analysis
        memory_policy = self.redis_configs.get('maxmemory-policy', '')
        if memory_policy in ['allkeys-lru', 'allkeys-lfu']:
            analysis["performance_score"] += 10
            analysis["performance_factors"].append(f"Optimized eviction policy: {memory_policy}")
        
        timeout = self.redis_configs.get('timeout', '')
        if timeout == '0':
            analysis["performance_score"] += 5
            analysis["performance_factors"].append("No client timeout for persistent connections")
        
        # Version analysis
        if self.redis_version == 'REDIS_7_0':
            analysis["performance_score"] += 10
            analysis["performance_factors"].append("Latest Redis version with performance improvements")
        elif self.redis_version == 'REDIS_6_X':
            analysis["performance_score"] += 8
            analysis["performance_factors"].append("Modern Redis version")
        else:
            analysis["recommendations"].append("Consider upgrading to Redis 7.0 for latest features")
        
        # Authentication impact
        if self.auth_enabled:
            analysis["latency_factors"].append("Authentication adds minimal latency overhead")
        
        # Encryption impact
        if self.has_encryption():
            analysis["latency_factors"].append("Encryption adds small latency overhead")
        
        return analysis
    
    def analyze_cost(self) -> Dict[str, Any]:
        """
        Analyze Memorystore cost configuration and provide recommendations.
        
        Returns:
            Dict containing cost analysis and recommendations
        """
        analysis = {
            "cost_score": 0,
            "max_score": 100,
            "recommendations": [],
            "cost_factors": [],
            "savings_opportunities": []
        }
        
        base_cost = self._estimate_memorystore_cost()
        
        # Tier analysis
        if self.tier == 'BASIC':
            analysis["cost_score"] += 30
            analysis["cost_factors"].append("Basic tier for cost efficiency")
        else:
            analysis["cost_score"] += 15
            if self.memory_size_gb <= 4:
                analysis["savings_opportunities"].append("Consider Basic tier for smaller workloads")
        
        # Memory size analysis
        if self.memory_size_gb <= 2:
            analysis["cost_score"] += 25
            analysis["cost_factors"].append("Small memory size for cost efficiency")
        elif self.memory_size_gb <= 8:
            analysis["cost_score"] += 20
            analysis["cost_factors"].append("Moderate memory size")
        else:
            analysis["cost_score"] += 10
            analysis["savings_opportunities"].append("Evaluate if all memory is needed")
        
        # Read replicas cost impact
        if self.has_read_replicas():
            replica_cost = base_cost * self.replica_count
            analysis["cost_factors"].append(f"Read replicas add ~${replica_cost:.2f}/month")
            if self.replica_count > 2:
                analysis["savings_opportunities"].append("Evaluate if all read replicas are necessary")
        else:
            analysis["cost_score"] += 15
            analysis["cost_factors"].append("No read replicas to minimize cost")
        
        # Persistence cost impact
        if self.has_persistence():
            analysis["cost_factors"].append("Persistence backups included in base cost")
        else:
            analysis["cost_score"] += 10
            analysis["cost_factors"].append("No persistence backups to save on storage")
        
        # Labels for cost management
        if "cost_management" in self.instance_labels:
            analysis["cost_score"] += 10
            analysis["cost_factors"].append("Cost management labels for tracking")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def _estimate_monthly_cost(self) -> str:
        """Get estimated monthly cost for backwards compatibility"""
        return f"${self._estimate_memorystore_cost():.2f}/month"
    
    def get_status(self) -> Dict[str, Any]:
        """Get instance status for backwards compatibility"""
        return {
            "instance_id": self.instance_id,
            "state": self.instance_state,
            "tier": self.tier,
            "memory_size_gb": self.memory_size_gb,
            "redis_version": self.redis_version,
            "primary_endpoint": self.redis_endpoint,
            "read_endpoint": self.read_endpoint,
            "connection_string": self.connection_string(),
            "auth_enabled": self.auth_enabled,
            "has_persistence": self.has_persistence(),
            "has_read_replicas": self.has_read_replicas(),
            "has_encryption": self.has_encryption()
        }


# Convenience function for creating Memorystore instances
def create_memorystore(name: str) -> Memorystore:
    """
    Create a new Memorystore instance.
    
    Args:
        name: Instance name
        
    Returns:
        Memorystore instance
    """
    return Memorystore(name)


# Export the class for easy importing
__all__ = ['Memorystore', 'create_memorystore']