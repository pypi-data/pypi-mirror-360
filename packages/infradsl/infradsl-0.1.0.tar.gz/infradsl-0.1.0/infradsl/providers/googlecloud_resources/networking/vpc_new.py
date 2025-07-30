"""
GCP VPC Complete Implementation

Combines all VPC functionality through multiple inheritance:
- VPCCore: Core attributes and authentication
- VPCConfigurationMixin: Chainable configuration methods  
- VPCLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .vpc_core import VPCCore
from .vpc_configuration import VPCConfigurationMixin
from .vpc_lifecycle import VPCLifecycleMixin


class VPC(VPCLifecycleMixin, VPCConfigurationMixin, VPCCore):
    """
    Complete GCP VPC implementation for cloud networking.
    
    This class combines:
    - VPC network configuration methods (routing, subnets, firewall rules)
    - VPC lifecycle management (create, destroy, preview)
    - Subnet and firewall rule management
    - VPC peering and advanced networking features
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize VPC instance for cloud networking"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$5.00/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._vpc_type = None
        self._monitoring_enabled = True
        self._auto_scaling_enabled = False
    
    def validate_configuration(self):
        """Validate the current VPC configuration"""
        errors = []
        warnings = []
        
        # Validate VPC name
        if not self.vpc_name:
            errors.append("VPC name is required")
        
        # Validate routing mode
        if not self._is_valid_routing_mode(self.routing_mode):
            errors.append(f"Invalid routing mode: {self.routing_mode}")
        
        # Validate MTU
        if not (1460 <= self.mtu <= 1500):
            warnings.append(f"MTU {self.mtu} is outside recommended range (1460-1500)")
        
        # Validate subnets
        if not self.auto_create_subnetworks and not self.subnets:
            warnings.append("Custom subnet mode enabled but no subnets defined")
        
        for subnet in self.subnets:
            if not self._validate_subnet_config(subnet):
                errors.append(f"Invalid subnet configuration: {subnet.get('name', 'Unknown')}")
        
        # Check for subnet CIDR overlaps
        overlaps = self._check_subnet_overlaps()
        if overlaps:
            errors.extend(overlaps)
        
        # Validate firewall rules
        for rule in self.firewall_rules:
            if not self._validate_firewall_rule(rule):
                errors.append(f"Invalid firewall rule: {rule.get('name', 'Unknown')}")
        
        # Security warnings
        allow_all_rules = [rule for rule in self.firewall_rules 
                          if "0.0.0.0/0" in rule.get("source_ranges", [])]
        if allow_all_rules:
            warnings.append(f"{len(allow_all_rules)} firewall rule(s) allow traffic from anywhere (0.0.0.0/0)")
        
        # Performance warnings
        if self.routing_mode == "REGIONAL" and len(self.subnets) > 1:
            regions = set(subnet.get("region") for subnet in self.subnets)
            if len(regions) > 1:
                warnings.append("Regional routing with multi-region subnets may impact performance")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_vpc_info(self):
        """Get complete information about the VPC"""
        return {
            'vpc_name': self.vpc_name,
            'description': self.vpc_description,
            'routing_mode': self.routing_mode,
            'auto_create_subnetworks': self.auto_create_subnetworks,
            'mtu': self.mtu,
            'vpc_type_display': self._get_vpc_type_display(),
            'subnets_count': len(self.subnets),
            'subnets': self.subnets,
            'firewall_rules_count': len(self.firewall_rules),
            'firewall_rules': self.firewall_rules,
            'static_routes_count': len(self.static_routes),
            'vpc_peerings_count': len(self.vpc_peerings),
            'enable_flow_logs': self.enable_flow_logs,
            'flow_logs_config': self.flow_logs_config,
            'dns_config': self.dns_config,
            'labels_count': len(self.vpc_labels),
            'vpc_url': self.vpc_url,
            'vpc_exists': self.vpc_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'vpc_type': self._vpc_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this VPC with a new name"""
        cloned_vpc = VPC(new_name)
        cloned_vpc.vpc_name = new_name
        cloned_vpc.vpc_description = self.vpc_description
        cloned_vpc.routing_mode = self.routing_mode
        cloned_vpc.auto_create_subnetworks = self.auto_create_subnetworks
        cloned_vpc.mtu = self.mtu
        cloned_vpc.subnets = [subnet.copy() for subnet in self.subnets]
        cloned_vpc.firewall_rules = [rule.copy() for rule in self.firewall_rules]
        cloned_vpc.static_routes = [route.copy() for route in self.static_routes]
        cloned_vpc.vpc_peerings = [peering.copy() for peering in self.vpc_peerings]
        cloned_vpc.enable_flow_logs = self.enable_flow_logs
        cloned_vpc.flow_logs_config = self.flow_logs_config.copy()
        cloned_vpc.dns_config = self.dns_config.copy()
        cloned_vpc.vpc_labels = self.vpc_labels.copy()
        return cloned_vpc
    
    def export_configuration(self):
        """Export VPC configuration for backup or migration"""
        return {
            'metadata': {
                'vpc_name': self.vpc_name,
                'routing_mode': self.routing_mode,
                'region': self.vpc_region,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'vpc_name': self.vpc_name,
                'description': self.vpc_description,
                'routing_mode': self.routing_mode,
                'auto_create_subnetworks': self.auto_create_subnetworks,
                'mtu': self.mtu,
                'subnets': self.subnets,
                'firewall_rules': self.firewall_rules,
                'static_routes': self.static_routes,
                'vpc_peerings': self.vpc_peerings,
                'enable_flow_logs': self.enable_flow_logs,
                'flow_logs_config': self.flow_logs_config,
                'dns_config': self.dns_config,
                'labels': self.vpc_labels,
                'optimization_priority': self._optimization_priority,
                'vpc_type': self._vpc_type,
                'monitoring_enabled': self._monitoring_enabled,
                'auto_scaling_enabled': self._auto_scaling_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import VPC configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.vpc_name = config.get('vpc_name', self.vpc_name)
            self.vpc_description = config.get('description', f"VPC network for {self.vpc_name}")
            self.routing_mode = config.get('routing_mode', 'REGIONAL')
            self.auto_create_subnetworks = config.get('auto_create_subnetworks', False)
            self.mtu = config.get('mtu', 1460)
            self.subnets = config.get('subnets', [])
            self.firewall_rules = config.get('firewall_rules', [])
            self.static_routes = config.get('static_routes', [])
            self.vpc_peerings = config.get('vpc_peerings', [])
            self.enable_flow_logs = config.get('enable_flow_logs', False)
            self.flow_logs_config = config.get('flow_logs_config', {})
            self.dns_config = config.get('dns_config', {})
            self.vpc_labels = config.get('labels', {})
            self._optimization_priority = config.get('optimization_priority')
            self._vpc_type = config.get('vpc_type')
            self._monitoring_enabled = config.get('monitoring_enabled', True)
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable comprehensive monitoring and alerting"""
        self._monitoring_enabled = enabled
        if enabled:
            self.enable_flow_logs = True
            self.dns_config["enable_logging"] = True
            print("📊 Comprehensive monitoring enabled")
            print("   💡 VPC flow logs activated")
            print("   💡 DNS query logging enabled")
            print("   💡 Network monitoring configured")
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling for VPC resources"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for VPC")
            print("   💡 Subnet auto-expansion configured")
            print("   💡 Firewall rule auto-adjustment enabled")
        return self
    
    def get_subnet_by_name(self, name: str):
        """Get subnet configuration by name"""
        for subnet in self.subnets:
            if subnet.get("name") == name:
                return subnet
        return None
    
    def get_subnets_by_region(self, region: str):
        """Get all subnets in a specific region"""
        return [subnet for subnet in self.subnets if subnet.get("region") == region]
    
    def get_firewall_rule_by_name(self, name: str):
        """Get firewall rule configuration by name"""
        for rule in self.firewall_rules:
            if rule.get("name") == name:
                return rule
        return None
    
    def remove_subnet(self, name: str):
        """Remove a subnet from the VPC"""
        self.subnets = [subnet for subnet in self.subnets if subnet.get("name") != name]
        print(f"🗑️  Removed subnet '{name}' from VPC")
        return self
    
    def remove_firewall_rule(self, name: str):
        """Remove a firewall rule from the VPC"""
        self.firewall_rules = [rule for rule in self.firewall_rules if rule.get("name") != name]
        print(f"🗑️  Removed firewall rule '{name}' from VPC")
        return self
    
    def get_network_statistics(self):
        """Get statistics about the VPC network"""
        if not self.vpc_manager:
            return {"error": "VPC manager not available"}
        
        try:
            stats = self.vpc_manager.get_network_statistics(self.vpc_name)
            return {
                "vpc_name": self.vpc_name,
                "subnets_count": len(self.subnets),
                "firewall_rules_count": len(self.firewall_rules),
                "total_ip_addresses": sum(self._count_ip_addresses(subnet.get("cidr", "")) for subnet in self.subnets),
                "regions_spanned": len(set(subnet.get("region") for subnet in self.subnets)),
                "flow_logs_enabled": self.enable_flow_logs,
                "traffic_stats": stats.get("traffic_stats", {}),
                "security_events": stats.get("security_events", {}),
                "period": stats.get("period", "24h")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _count_ip_addresses(self, cidr: str) -> int:
        """Count the number of IP addresses in a CIDR block"""
        if not cidr:
            return 0
        try:
            import ipaddress
            network = ipaddress.ip_network(cidr, strict=False)
            return network.num_addresses
        except ValueError:
            return 0
    
    def get_security_analysis(self):
        """Analyze VPC security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": [],
            "compliant_rules": 0,
            "risky_rules": 0
        }
        
        # Analyze firewall rules
        for rule in self.firewall_rules:
            if "0.0.0.0/0" in rule.get("source_ranges", []):
                analysis["issues"].append(f"Rule '{rule.get('name')}' allows traffic from anywhere")
                analysis["security_score"] -= 10
                analysis["risky_rules"] += 1
            else:
                analysis["compliant_rules"] += 1
        
        # Check for SSH access
        ssh_rules = [rule for rule in self.firewall_rules 
                    if any("22" in str(allowed.get("ports", [])) for allowed in rule.get("allowed", []))]
        if ssh_rules:
            for rule in ssh_rules:
                if "0.0.0.0/0" in rule.get("source_ranges", []):
                    analysis["issues"].append(f"SSH access allowed from anywhere in rule '{rule.get('name')}'")
                    analysis["security_score"] -= 20
        
        # Check flow logs
        if not self.enable_flow_logs:
            analysis["recommendations"].append("Enable VPC Flow Logs for better security monitoring")
            analysis["security_score"] -= 5
        
        # Check DNS logging
        if not self.dns_config.get("enable_logging", False):
            analysis["recommendations"].append("Enable DNS query logging for security analysis")
            analysis["security_score"] -= 5
        
        return analysis
    
    def apply_security_best_practices(self):
        """Apply security best practices to the VPC"""
        print("🔒 Applying security best practices to VPC")
        
        # Enable monitoring
        if not self.enable_flow_logs:
            print("   💡 Enabling VPC Flow Logs")
            self.enable_flow_logs = True
        
        # Enable DNS logging
        if not self.dns_config.get("enable_logging", False):
            print("   💡 Enabling DNS query logging")
            self.dns_config["enable_logging"] = True
        
        # Add security labels
        self.vpc_labels.update({
            "security": "enhanced",
            "monitoring": "enabled",
            "compliance": "best-practices"
        })
        print("   💡 Added security labels")
        
        # Suggest firewall improvements
        open_rules = [rule for rule in self.firewall_rules 
                     if "0.0.0.0/0" in rule.get("source_ranges", [])]
        if open_rules:
            print(f"   ⚠️  Consider restricting {len(open_rules)} rule(s) that allow traffic from anywhere")
        
        return self


# Convenience functions for creating VPC instances
def create_simple_vpc(name: str, cidr_base: str = "10.0") -> VPC:
    """Create a simple VPC with basic configuration"""
    vpc = VPC(name)
    vpc.development_vpc().three_tier_architecture(cidr_base)
    return vpc

def create_production_vpc(name: str, regions: List[str] = None) -> VPC:
    """Create a production-ready VPC"""
    regions = regions or ["us-central1", "us-east1"]
    vpc = VPC(name)
    vpc.production_vpc().multi_region_setup(regions).optimize_for("reliability")
    return vpc

def create_microservices_vpc(name: str, region: str = "us-central1") -> VPC:
    """Create a VPC optimized for microservices"""
    vpc = VPC(name)
    vpc.production_vpc().microservices_architecture(region=region).optimize_for("performance")
    return vpc

def create_development_vpc(name: str, cidr_base: str = "172.16") -> VPC:
    """Create a VPC for development environments"""
    vpc = VPC(name)
    vpc.development_vpc().three_tier_architecture(cidr_base).optimize_for("cost")
    return vpc

def create_staging_vpc(name: str, cidr_base: str = "192.168") -> VPC:
    """Create a VPC for staging environments"""
    vpc = VPC(name)
    vpc.staging_vpc().three_tier_architecture(cidr_base).optimize_for("performance")
    return vpc

# Alias for backward compatibility
GCPVpc = VPC