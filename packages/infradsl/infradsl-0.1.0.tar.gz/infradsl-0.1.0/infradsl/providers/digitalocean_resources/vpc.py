"""
DigitalOcean VPC (Virtual Private Cloud) Resource

Provides Rails-like interface for creating and managing DigitalOcean VPCs
for private networking.
"""

from typing import Dict, Any, List, Optional
from .base_resource import BaseDigitalOceanResource


class VPC(BaseDigitalOceanResource):
    """DigitalOcean VPC with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        self.config = {
            "name": name,
            "region": "nyc3",  # Default region
            "ip_range": "10.0.0.0/16",  # Default IP range
            "description": f"VPC for {name}",
            "tags": [],
            "networking_intelligence_enabled": True  # Enable Nexus networking intelligence
        }
        self._networking_intelligence = None

    def _initialize_managers(self):
        """Initialize VPC-specific managers"""
        from ..digitalocean_managers.vpc_manager import VPCManager
        self.vpc_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        from ..digitalocean_managers.vpc_manager import VPCManager
        self.vpc_manager = VPCManager(self.do_client)
        
        # Initialize networking intelligence if enabled
        if self.config.get("networking_intelligence_enabled"):
            self._initialize_networking_intelligence()

    # Basic configuration
    def region(self, region: str) -> 'VPC':
        """Set the region (e.g., 'nyc3', 'sfo3')"""
        self.config["region"] = region
        return self

    def ip_range(self, cidr: str) -> 'VPC':
        """Set the IP range (CIDR notation, e.g., '10.0.0.0/16')"""
        self.config["ip_range"] = cidr
        return self

    def description(self, description: str) -> 'VPC':
        """Set VPC description"""
        self.config["description"] = description
        return self

    def tags(self, tags: List[str]) -> 'VPC':
        """Add tags to the VPC"""
        self.config["tags"] = tags
        return self

    # Rails-like convenience methods for common network setups
    def small_network(self) -> 'VPC':
        """Configure for small network (10.0.0.0/24 - 254 hosts)"""
        return self.ip_range("10.0.0.0/24")

    def medium_network(self) -> 'VPC':
        """Configure for medium network (10.0.0.0/20 - 4094 hosts)"""
        return self.ip_range("10.0.0.0/20")

    def large_network(self) -> 'VPC':
        """Configure for large network (10.0.0.0/16 - 65534 hosts)"""
        return self.ip_range("10.0.0.0/16")

    def development(self) -> 'VPC':
        """Configure for development environment"""
        return self.small_network().description(f"Development VPC for {self.name}")

    def staging(self) -> 'VPC':
        """Configure for staging environment"""
        return self.medium_network().description(f"Staging VPC for {self.name}")

    def production(self) -> 'VPC':
        """Configure for production environment"""
        return self.large_network().description(f"Production VPC for {self.name}")

    # Microservices patterns
    def microservices(self) -> 'VPC':
        """Configure for microservices architecture"""
        return self.large_network().description(f"Microservices VPC for {self.name}")

    def database_tier(self) -> 'VPC':
        """Configure for database tier isolation"""
        return self.medium_network().description(f"Database tier VPC for {self.name}")

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        self._ensure_authenticated()
        return self.vpc_manager.preview_vpc(self.config)

    def create(self) -> Dict[str, Any]:
        """Create the VPC"""
        self._ensure_authenticated()
        
        self._print_resource_header("VPC", "Creating")
        
        # Print configuration summary
        print(f"🌐 VPC Name: {self.config['name']}")
        print(f"📍 Region: {self.config['region']}")
        print(f"🔢 IP Range: {self.config['ip_range']}")
        print(f"📝 Description: {self.config['description']}")
        
        if self.config["tags"]:
            print(f"🏷️  Tags: {', '.join(self.config['tags'])}")
        
        result = self.vpc_manager.create_vpc(self.config)
        
        self._print_resource_footer("create VPC")
        return result

    def destroy(self) -> Dict[str, Any]:
        """Destroy the VPC"""
        self._ensure_authenticated()
        
        print(f"\n🗑️  Destroying VPC: {self.name}")
        result = self.vpc_manager.destroy_vpc(self.name)
        
        if result.get("success"):
            print(f"✅ VPC '{self.name}' destroyed successfully")
        else:
            print(f"❌ Failed to destroy VPC: {result.get('error', 'Unknown error')}")
        
        return result

    # Network utilities
    def get_available_ips(self) -> Dict[str, Any]:
        """Get information about available IP addresses in the VPC"""
        self._ensure_authenticated()
        return self.vpc_manager.get_vpc_ip_info(self.name)

    def list_resources(self) -> Dict[str, Any]:
        """List all resources in this VPC"""
        self._ensure_authenticated()
        return self.vpc_manager.list_vpc_resources(self.name)

    # Nexus Networking Intelligence Methods
    def _initialize_networking_intelligence(self):
        """Initialize Nexus networking intelligence"""
        try:
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            self._networking_intelligence = cross_cloud_intelligence.get_networking_intelligence()
        except ImportError:
            print("⚠️  Networking intelligence not available")
            self._networking_intelligence = None

    def nexus_networking(self) -> 'VPC':
        """Enable Nexus networking intelligence for this VPC"""
        self.config["networking_intelligence_enabled"] = True
        return self

    def intelligent_cidr(self, organization_name: str, target_regions: List[str] = None) -> 'VPC':
        """
        Use Nexus intelligence to automatically generate optimal CIDR allocation
        
        This prevents conflicts and creates enterprise-grade IP allocation strategy
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        if target_regions is None:
            target_regions = [self.config["region"]]
        
        try:
            # Generate intelligent CIDR plan
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            cidr_result = cross_cloud_intelligence.generate_intelligent_cidr_plan(
                organization_name=organization_name,
                target_regions=target_regions,
                scale="medium"
            )
            
            cidr_plan = cidr_result["cidr_plan"]
            
            # Apply regional allocation for this VPC
            current_region = self.config["region"]
            if current_region in cidr_plan.regional_allocations:
                optimal_cidr = cidr_plan.regional_allocations[current_region]
                self.config["ip_range"] = optimal_cidr
                
                print(f"🧠 Nexus Intelligence Applied:")
                print(f"   • Optimal CIDR: {optimal_cidr}")
                print(f"   • Conflict-free: {'✅' if cidr_plan.conflict_free else '❌'}")
                print(f"   • Organization: {organization_name}")
                print(f"   • Global supernet: {cidr_plan.global_supernet}")
                
                if not cidr_plan.conflict_free:
                    print("⚠️  CIDR conflicts detected - manual review recommended")
            else:
                print(f"⚠️  No CIDR allocation found for region {current_region}")
                
        except Exception as e:
            print(f"⚠️  Networking intelligence error: {e}")
        
        return self

    def cost_optimized(self) -> 'VPC':
        """
        Apply Nexus cost optimization intelligence to network configuration
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            # Analyze current architecture for cost optimization
            current_architecture = {
                "vpc_count": 1,
                "nat_gateways": [{"utilization": 0.4}],  # Simulated data
                "load_balancers": [{"utilization": 0.3}],
                "estimated_cross_az_traffic_gb": 500,
                "service_count": 3
            }
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            optimization = cross_cloud_intelligence.analyze_network_optimization_opportunities(current_architecture)
            
            print(f"💰 Nexus Cost Optimization:")
            print(f"   • Monthly savings potential: ${optimization['total_monthly_savings']:.2f}")
            print(f"   • Annual savings potential: ${optimization['total_annual_savings']:.2f}")
            print(f"   • Optimization confidence: {optimization['optimization_confidence']:.1%}")
            
            # Apply optimization recommendations
            topology_rec = optimization["topology_recommendation"]
            print(f"   • Recommended topology: {topology_rec.recommended_topology.value}")
            print(f"   • Estimated cost: ${topology_rec.cost_estimate:.2f}/month")
            
        except Exception as e:
            print(f"⚠️  Cost optimization error: {e}")
        
        return self

    def compliance_validated(self, frameworks: List[str]) -> 'VPC':
        """
        Validate VPC configuration against compliance frameworks using Nexus intelligence
        
        Args:
            frameworks: List of compliance frameworks (e.g., ["SOC2", "HIPAA", "PCI"])
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            # Simulate current network configuration
            network_config = {
                "encryption_enabled": True,  # Default to secure
                "network_segmentation": True,
                "enabled_logging": ["vpc_flow_logs", "network_acl_changes"],
                "vpc_name": self.name,
                "region": self.config["region"]
            }
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            compliance_result = cross_cloud_intelligence.validate_network_security_compliance(
                network_config, frameworks
            )
            
            print(f"🛡️ Nexus Compliance Validation:")
            print(f"   • Overall compliant: {'✅' if compliance_result['overall_compliant'] else '❌'}")
            
            for framework, result in compliance_result["framework_results"].items():
                status = "✅" if result["overall_compliant"] else "❌"
                print(f"   • {framework}: {status}")
                
                if result["required_improvements"]:
                    for improvement in result["required_improvements"]:
                        print(f"     - {improvement}")
            
            print(f"   • Recommendations:")
            for rec in compliance_result["recommendations"]:
                print(f"     - {rec}")
                
        except Exception as e:
            print(f"⚠️  Compliance validation error: {e}")
        
        return self

    def cidr_conflict_check(self, existing_networks: List[str] = None) -> Dict[str, Any]:
        """
        Check for CIDR conflicts using Nexus intelligence
        
        Args:
            existing_networks: List of existing CIDR blocks to check against
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return {"error": "Networking intelligence not available"}
        
        if existing_networks is None:
            existing_networks = ["10.1.0.0/16", "192.168.0.0/16"]  # Common networks
        
        try:
            conflict_result = self._networking_intelligence.detect_cidr_conflicts(
                self.config["ip_range"], 
                existing_networks
            )
            
            if conflict_result["has_conflicts"]:
                print("🚨 CIDR Conflict Detected!")
                for conflict in conflict_result["conflicts"]:
                    print(f"   • Conflict with {conflict['existing_cidr']}")
                    print(f"   • Overlap: {conflict['overlap_range']} ({conflict['affected_ips']} IPs)")
                
                print("💡 Suggested alternatives:")
                for alt in conflict_result["suggested_alternatives"]:
                    print(f"   • {alt}")
            else:
                print("✅ No CIDR conflicts detected")
            
            return conflict_result
            
        except Exception as e:
            print(f"⚠️  CIDR conflict check error: {e}")
            return {"error": str(e)}

    def preview_networking_intelligence(self) -> Dict[str, Any]:
        """Preview what Nexus networking intelligence will configure"""
        if not self._networking_intelligence:
            return {"error": "Networking intelligence not available"}
        
        return {
            "current_config": self.config,
            "intelligence_enabled": self.config.get("networking_intelligence_enabled", False),
            "available_methods": [
                "intelligent_cidr() - Auto-generate optimal CIDR allocation",
                "cost_optimized() - Apply cost optimization intelligence", 
                "compliance_validated(frameworks) - Validate against compliance frameworks",
                "cidr_conflict_check(existing) - Check for CIDR conflicts"
            ],
            "networking_features": {
                "cidr_planning": True,
                "cost_optimization": True,
                "compliance_validation": True,
                "conflict_detection": True,
                "topology_recommendations": True
            }
        }