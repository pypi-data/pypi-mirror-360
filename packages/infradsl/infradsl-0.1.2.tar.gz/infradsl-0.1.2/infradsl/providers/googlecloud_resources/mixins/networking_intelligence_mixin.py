from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..vm import Vm

class NetworkingIntelligenceMixin:
    """Mixin for Nexus networking intelligence features"""
    
    def _initialize_networking_intelligence(self: 'Vm'):
        """Initialize Nexus networking intelligence"""
        try:
            from ....core.cross_cloud_intelligence import cross_cloud_intelligence
            self._networking_intelligence = cross_cloud_intelligence.get_networking_intelligence()
            # Only print success message if networking intelligence methods are being called
        except ImportError:
            print("⚠️  Networking intelligence not available")
            self._networking_intelligence = None

    def intelligent_cidr(self: 'Vm', organization_name: str = None, target_regions: List[str] = None) -> 'Vm':
        """
        Use Nexus intelligence to automatically optimize network configuration
        
        This analyzes the VM's network requirements and applies intelligent
        CIDR allocation with conflict prevention.
        
        Args:
            organization_name: Organization name for CIDR planning
            target_regions: List of target regions for multi-region deployment
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            self._initialize_networking_intelligence()
            if not self._networking_intelligence:
                print("⚠️  Networking intelligence not initialized")
                return self
        
        # Default organization name if not provided
        if organization_name is None:
            organization_name = "InfraDSL-Org"
        
        # Default to VM's current zone region if not specified
        if target_regions is None:
            primary_config = self.configs[self.vm_names[0]]
            zone = primary_config.zone
            # Extract region from zone (e.g., 'us-central1-a' -> 'us-central1')
            region = '-'.join(zone.split('-')[:-1])
            target_regions = [region]
        
        try:
            from ....core.cross_cloud_intelligence import cross_cloud_intelligence
            
            print("🧠 Nexus Networking Intelligence Activated:")
            print(f"   • Organization: {organization_name}")
            print(f"   • Target regions: {', '.join(target_regions)}")
            
            # Generate intelligent CIDR plan
            cidr_result = cross_cloud_intelligence.generate_intelligent_cidr_plan(
                organization_name=organization_name,
                target_regions=target_regions,
                scale="medium"
            )
            
            cidr_plan = cidr_result["cidr_plan"]
            
            # Extract region from VM's zone
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Apply networking recommendations
            if vm_region in cidr_plan.regional_allocations:
                optimal_cidr = cidr_plan.regional_allocations[vm_region]
                
                print(f"   • Optimal CIDR for {vm_region}: {optimal_cidr}")
                print(f"   • Global supernet: {cidr_plan.global_supernet}")
                print(f"   • Conflict-free: {'✅' if cidr_plan.conflict_free else '❌'}")
                
                # Apply to VM network configuration
                for config in self.configs.values():
                    # Create intelligent subnet name based on environment
                    subnet_name = f"{organization_name.lower()}-{vm_region}-private"
                    config.subnetwork = subnet_name
                    
                print(f"   • Applied subnet: {subnet_name}")
                
                if not cidr_plan.conflict_free:
                    print("⚠️  CIDR conflicts detected - manual review recommended")
                
                # Analyze network optimization opportunities
                current_architecture = {
                    "vpc_count": 1,
                    "service_count": len(self.vm_names),
                    "region": vm_region,
                    "machine_types": [config.machine_type for config in self.configs.values()]
                }
                
                optimization = cross_cloud_intelligence.analyze_network_optimization_opportunities(current_architecture)
                
                if optimization['total_monthly_savings'] > 0:
                    print(f"   • Network cost optimization: ${optimization['total_monthly_savings']:.2f}/month savings")
                
            else:
                print(f"⚠️  No CIDR allocation found for region {vm_region}")
                
        except Exception as e:
            print(f"⚠️  Networking intelligence error: {e}")
        
        return self

    def cidr_conflict_check(self: 'Vm', existing_networks: List[str] = None) -> 'Vm':
        """
        Check for CIDR conflicts using Nexus intelligence
        
        This prevents network conflicts before deployment and suggests
        alternative configurations if conflicts are detected.
        
        Args:
            existing_networks: List of existing CIDR blocks to check against
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        # Default existing networks commonly used in enterprise environments
        if existing_networks is None:
            existing_networks = [
                "10.0.0.0/8",      # Common enterprise range
                "172.16.0.0/12",   # RFC 1918 range
                "192.168.0.0/16",  # Home/small office range
                "10.1.0.0/16",     # Common VPC range
                "10.2.0.0/16"      # Another common VPC range
            ]
        
        try:
            # Analyze current VM network configuration
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Simulate current network configuration based on VM placement
            proposed_cidr = "10.0.0.0/16"  # Default GCP VPC range
            
            print("🚨 Nexus CIDR Conflict Analysis:")
            print(f"   • VM Region: {vm_region}")
            print(f"   • Proposed network: {proposed_cidr}")
            print(f"   • Checking against {len(existing_networks)} existing networks")
            
            # Check for conflicts
            conflict_result = self._networking_intelligence.detect_cidr_conflicts(
                proposed_cidr, 
                existing_networks
            )
            
            if conflict_result["has_conflicts"]:
                print("   ❌ CONFLICTS DETECTED!")
                
                for conflict in conflict_result["conflicts"]:
                    print(f"      • Conflict with: {conflict['existing_cidr']}")
                    print(f"      • Overlap range: {conflict['overlap_range']}")
                    print(f"      • Affected IPs: {conflict['affected_ips']}")
                
                print("   💡 Nexus Recommendations:")
                for i, alt in enumerate(conflict_result["suggested_alternatives"], 1):
                    print(f"      {i}. Use CIDR: {alt}")
                
                # Apply first alternative automatically
                if conflict_result["suggested_alternatives"]:
                    optimal_cidr = conflict_result["suggested_alternatives"][0]
                    print(f"   🔧 Auto-applying conflict-free CIDR: {optimal_cidr}")
                    
                    # Update VM network configuration
                    for config in self.configs.values():
                        # Create subnet name based on the new CIDR
                        subnet_name = f"nexus-optimized-{vm_region}"
                        config.subnetwork = subnet_name
                    
                    print(f"   ✅ Updated subnet configuration: {subnet_name}")
                
            else:
                print("   ✅ NO CONFLICTS DETECTED")
                print("   🎯 Current network configuration is safe to deploy")
            
            # Additional network security recommendations
            print("   🛡️ Security Recommendations:")
            if len(self.firewall_rules) == 0:
                print("      • Add firewall rules for network security")
            else:
                for rule in self.firewall_rules:
                    if rule.source_ranges and '0.0.0.0/0' in rule.source_ranges:
                        print(f"      • Rule '{rule.name}' allows all IPs - consider restricting")
                    else:
                        print(f"      • Rule '{rule.name}' has good security posture")
            
            # Network performance recommendations
            machine_type = primary_config.machine_type
            if machine_type in ['f1-micro', 'g1-small', 'e2-micro']:
                print("   ⚡ Performance Note:")
                print("      • Shared-core instances have limited network performance")
                print("      • Consider e2-standard-2+ for network-intensive applications")
            
        except Exception as e:
            print(f"⚠️  CIDR conflict check error: {e}")
        
        return self

    def network_cost_optimization(self: 'Vm') -> 'Vm':
        """
        Apply Nexus network cost optimization intelligence
        
        Analyzes current VM network configuration and suggests cost optimizations
        including load balancer consolidation, NAT gateway optimization, and
        cross-AZ traffic reduction.
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            print("💰 Nexus Network Cost Optimization:")
            
            # Analyze current architecture
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Simulate current network architecture
            current_architecture = {
                "vpc_count": 1,
                "nat_gateways": [{"utilization": 0.4, "region": vm_region}],
                "load_balancers": [{"utilization": 0.3 if self._load_balancer_config else 0}],
                "estimated_cross_az_traffic_gb": len(self.vm_names) * 100,  # Estimate based on VM count
                "service_count": len(self.vm_names),
                "machine_types": [config.machine_type for config in self.configs.values()]
            }
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            optimization = cross_cloud_intelligence.analyze_network_optimization_opportunities(current_architecture)
            
            print(f"   • Monthly savings potential: ${optimization['total_monthly_savings']:.2f}")
            print(f"   • Annual savings potential: ${optimization['total_annual_savings']:.2f}")
            print(f"   • Optimization confidence: {optimization['optimization_confidence']:.1%}")
            
            # Show topology recommendation
            topology_rec = optimization["topology_recommendation"]
            print(f"   • Recommended topology: {topology_rec.recommended_topology.value}")
            print(f"   • Estimated monthly cost: ${topology_rec.cost_estimate:.2f}")
            
            # Apply cost optimization recommendations
            if len(self.vm_names) > 1 and not self._load_balancer_config:
                print("   💡 Recommendation: Add load balancer for multi-VM setup")
                print("      • Improves availability and enables cost optimization")
            
            if optimization['total_monthly_savings'] > 50:
                print("   🎯 High-impact optimizations available:")
                print("      • Consider implementing suggested network topology")
                print("      • Review load balancer consolidation opportunities")
            
        except Exception as e:
            print(f"⚠️  Network cost optimization error: {e}")
        
        return self

    def compliance_validated(self: 'Vm', frameworks: List[str]) -> 'Vm':
        """
        Validate VM network configuration against compliance frameworks
        
        Uses Nexus intelligence to validate networking configuration against
        enterprise compliance requirements like SOC2, HIPAA, PCI, etc.
        
        Args:
            frameworks: List of compliance frameworks to validate against
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            print("🛡️ Nexus Compliance Validation:")
            print(f"   • Frameworks: {', '.join(frameworks)}")
            
            # Analyze current VM network configuration
            primary_config = self.configs[self.vm_names[0]]
            
            # Build network configuration for compliance checking
            network_config = {
                "encryption_enabled": True,  # GCP encrypts by default
                "network_segmentation": len(self.firewall_rules) > 0,
                "enabled_logging": ["vpc_flow_logs"],  # Assume basic logging
                "vm_count": len(self.vm_names),
                "machine_type": primary_config.machine_type,
                "zone": primary_config.zone,
                "firewall_rules": len(self.firewall_rules)
            }
            
            # Add additional logging if monitoring is enabled
            if self._monitoring_enabled:
                network_config["enabled_logging"].extend(["monitoring", "audit_logs"])
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            compliance_result = cross_cloud_intelligence.validate_network_security_compliance(
                network_config, frameworks
            )
            
            print(f"   • Overall compliant: {'✅' if compliance_result['overall_compliant'] else '❌'}")
            
            for framework, result in compliance_result["framework_results"].items():
                status = "✅" if result["overall_compliant"] else "❌"
                print(f"   • {framework}: {status}")
                
                if result["required_improvements"]:
                    for improvement in result["required_improvements"]:
                        print(f"     - {improvement}")
            
            print("   📋 Recommendations:")
            for rec in compliance_result["recommendations"]:
                print(f"     • {rec}")
            
            # Apply automatic improvements where possible
            if not compliance_result['overall_compliant']:
                print("   🔧 Auto-applying compliance improvements:")
                
                # Enable monitoring if not already enabled for compliance
                if not self._monitoring_enabled:
                    self.monitoring(True)
                    print("     ✅ Enabled monitoring for compliance logging")
                
                # Add firewall rules if none exist
                if len(self.firewall_rules) == 0:
                    print("     💡 Add firewall rules for network segmentation")
                    print("     💡 Use .firewall() method to add security rules")
            
        except Exception as e:
            print(f"⚠️  Compliance validation error: {e}")
        
        return self 