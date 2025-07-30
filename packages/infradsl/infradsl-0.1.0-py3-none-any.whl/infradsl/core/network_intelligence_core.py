"""
Network Intelligence Core Engine

The core NetworkIntelligence class providing enterprise networking intelligence including:
- Intelligent CIDR planning and conflict prevention
- Cost-optimized network architecture recommendations
- Security-first networking with automatic compliance
- Multi-cloud network topology optimization
"""

import ipaddress
import logging
from typing import Dict, Any, List, Optional

from .network_types import (
    NetworkTier, NetworkTopology, CIDRPlan, NetworkCostAnalysis, 
    NetworkTopologyRecommendation
)
from .cross_cloud_intelligence import ServiceCategory, ProviderCapability
from datetime import datetime

logger = logging.getLogger(__name__)


class NetworkIntelligence:
    """
    Revolutionary Network Intelligence Engine
    
    Extends Nexus Engine with enterprise networking intelligence including:
    - Intelligent CIDR planning and conflict prevention
    - Cost-optimized network architecture recommendations
    - Security-first networking with automatic compliance
    - Multi-cloud network topology optimization
    """
    
    def __init__(self, cross_cloud_intelligence = None):
        self.cross_cloud = cross_cloud_intelligence
        
        # Enterprise IP allocation standards
        self.standard_allocations = {
            "global_supernets": [
                "10.0.0.0/8",    # RFC 1918 - 16M addresses
                "172.16.0.0/12", # RFC 1918 - 1M addresses
                "192.168.0.0/16" # RFC 1918 - 65K addresses
            ],
            "region_sizes": {
                "small": "/20",   # 4,096 addresses
                "medium": "/16",  # 65,536 addresses
                "large": "/12",   # 1,048,576 addresses
                "xlarge": "/8"    # 16,777,216 addresses
            },
            "environment_ratios": {
                "production": 0.50,   # 50% of regional allocation
                "staging": 0.30,      # 30% of regional allocation
                "development": 0.15,  # 15% of regional allocation
                "management": 0.05    # 5% for management/monitoring
            }
        }
        
        # Network cost optimization patterns
        self.cost_optimization_rules = {
            "nat_gateway": {
                "threshold_monthly": 45.0,
                "alternatives": [
                    "nat_instance_with_autoscaling",
                    "vpc_endpoints_for_aws_services",
                    "consolidated_nat_strategy"
                ]
            },
            "load_balancer": {
                "utilization_threshold": 0.3,
                "consolidation_opportunities": True
            },
            "cross_az_traffic": {
                "cost_per_gb": 0.01,
                "optimization_strategies": [
                    "az_locality_optimization",
                    "connection_pooling",
                    "data_locality_improvements"
                ]
            }
        }
        
        # Security compliance frameworks
        self.compliance_frameworks = {
            "SOC2": {
                "required_encryption": True,
                "network_segmentation": True,
                "access_logging": True,
                "monitoring_required": ["vpc_flow_logs", "network_acl_changes"]
            },
            "HIPAA": {
                "required_encryption": True,
                "network_isolation": True,
                "access_logging": True,
                "dedicated_instances": True,
                "monitoring_required": ["all_network_traffic", "access_patterns"]
            },
            "PCI": {
                "network_segmentation": True,
                "firewall_rules": "strict",
                "monitoring_required": ["payment_network_access", "cardholder_data_flows"]
            }
        }
    
    def generate_enterprise_cidr_plan(self, 
                                    organization_name: str,
                                    target_regions: List[str],
                                    expected_scale: str = "medium",
                                    compliance_requirements: List[str] = None) -> CIDRPlan:
        """
        Generate intelligent CIDR allocation plan for enterprise deployment
        
        This prevents CIDR conflicts and creates scalable IP allocation strategy
        """
        
        # Select optimal global supernet based on scale
        if expected_scale == "small":
            global_supernet = "192.168.0.0/16"  # 65K addresses
            regional_prefix = 20  # 4K per region
        elif expected_scale == "medium":
            global_supernet = "172.16.0.0/12"   # 1M addresses
            regional_prefix = 16  # 65K per region
        elif expected_scale == "large":
            global_supernet = "10.0.0.0/8"      # 16M addresses
            regional_prefix = 12  # 1M per region
        else:
            global_supernet = "10.0.0.0/8"
            regional_prefix = 16
        
        # Generate regional allocations
        regional_allocations = {}
        environment_allocations = {}
        base_network = ipaddress.IPv4Network(global_supernet)
        
        # Calculate regional subnets
        regional_networks = list(base_network.subnets(new_prefix=regional_prefix))
        
        for i, region in enumerate(target_regions):
            if i >= len(regional_networks):
                logger.warning(f"Insufficient IP space for region {region}")
                continue
                
            region_network = regional_networks[i]
            regional_allocations[region] = str(region_network)
            
            # Generate environment allocations within region
            env_allocations = self._generate_environment_allocations(region_network)
            environment_allocations[region] = env_allocations
        
        # Generate subnet patterns for different tiers
        subnet_patterns = {
            NetworkTier.PUBLIC: f"{{region_base}}.0.0/24",      # 256 addresses
            NetworkTier.PRIVATE: f"{{region_base}}.16.0/20",    # 4096 addresses
            NetworkTier.DATABASE: f"{{region_base}}.32.0/24",   # 256 addresses
            NetworkTier.MANAGEMENT: f"{{region_base}}.48.0/28", # 16 addresses
            NetworkTier.CACHE: f"{{region_base}}.49.0/28"       # 16 addresses
        }
        
        # Reserve blocks for future expansion
        reserved_blocks = []
        if len(regional_networks) > len(target_regions):
            for i in range(len(target_regions), min(len(target_regions) + 3, len(regional_networks))):
                reserved_blocks.append(str(regional_networks[i]))
        
        # Check for conflicts with existing deployments
        conflict_free = self._verify_no_cidr_conflicts(regional_allocations)
        
        return CIDRPlan(
            organization_name=organization_name,
            global_supernet=global_supernet,
            regional_allocations=regional_allocations,
            environment_allocations=environment_allocations,
            subnet_patterns=subnet_patterns,
            reserved_blocks=reserved_blocks,
            conflict_free=conflict_free,
            created_at=datetime.now()
        )
    
    def _generate_environment_allocations(self, region_network: ipaddress.IPv4Network) -> Dict[str, str]:
        """Generate environment-specific CIDR allocations within a region"""
        
        env_allocations = {}
        
        # Calculate prefix for environment subnets (typically +2 from regional)
        env_prefix = region_network.prefixlen + 2  # 4 environments per region
        env_networks = list(region_network.subnets(new_prefix=env_prefix))
        
        environments = ["production", "staging", "development", "management"]
        
        for i, env in enumerate(environments):
            if i < len(env_networks):
                env_allocations[env] = str(env_networks[i])
        
        return env_allocations
    
    def _verify_no_cidr_conflicts(self, new_allocations: Dict[str, str]) -> bool:
        """
        Verify that new CIDR allocations don't conflict with existing networks
        
        In production, this would check against:
        - Existing VPC configurations
        - On-premises networks
        - Partner network connections
        """
        
        # For now, we'll implement basic overlap detection
        networks = []
        for cidr in new_allocations.values():
            try:
                networks.append(ipaddress.IPv4Network(cidr))
            except ipaddress.AddressValueError:
                logger.error(f"Invalid CIDR: {cidr}")
                return False
        
        # Check for overlaps
        for i, net1 in enumerate(networks):
            for j, net2 in enumerate(networks[i+1:], i+1):
                if net1.overlaps(net2):
                    logger.error(f"CIDR conflict detected: {net1} overlaps with {net2}")
                    return False
        
        return True
    
    def analyze_network_costs(self, 
                            current_architecture: Dict[str, Any],
                            provider: str = "aws") -> List[NetworkCostAnalysis]:
        """
        Analyze network costs and provide optimization recommendations
        """
        
        analyses = []
        
        # Analyze NAT Gateway costs
        nat_analysis = self._analyze_nat_gateway_costs(current_architecture, provider)
        if nat_analysis:
            analyses.append(nat_analysis)
        
        # Analyze Load Balancer costs
        lb_analysis = self._analyze_load_balancer_costs(current_architecture, provider)
        if lb_analysis:
            analyses.append(lb_analysis)
        
        # Analyze Cross-AZ traffic costs
        traffic_analysis = self._analyze_cross_az_traffic_costs(current_architecture, provider)
        if traffic_analysis:
            analyses.append(traffic_analysis)
        
        return analyses
    
    def _analyze_nat_gateway_costs(self, architecture: Dict[str, Any], provider: str) -> Optional[NetworkCostAnalysis]:
        """Analyze NAT Gateway costs and optimization opportunities"""
        
        nat_gateways = architecture.get("nat_gateways", [])
        if not nat_gateways:
            return None
        
        # Calculate current costs
        nat_count = len(nat_gateways)
        monthly_cost_per_nat = 45.0  # AWS NAT Gateway cost
        current_monthly_cost = nat_count * monthly_cost_per_nat
        
        # Optimization: Consolidate to single NAT with route table optimization
        if nat_count > 1:
            optimized_cost = monthly_cost_per_nat  # Single NAT Gateway
            monthly_savings = current_monthly_cost - optimized_cost
            
            optimization_actions = [
                f"Consolidate {nat_count} NAT Gateways to 1 with optimized routing",
                "Implement VPC Endpoints for AWS services to reduce NAT traffic",
                "Consider NAT Instance with auto-scaling for 60% cost reduction"
            ]
        else:
            # Already optimized, but suggest VPC endpoints
            optimized_cost = current_monthly_cost * 0.7  # 30% reduction with VPC endpoints
            monthly_savings = current_monthly_cost - optimized_cost
            
            optimization_actions = [
                "Implement VPC Endpoints for S3, DynamoDB, and other AWS services",
                "Optimize routing to reduce internet-bound traffic"
            ]
        
        return NetworkCostAnalysis(
            resource_type="nat_gateway",
            provider=provider,
            current_monthly_cost=current_monthly_cost,
            optimized_monthly_cost=optimized_cost,
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            optimization_actions=optimization_actions,
            implementation_complexity="medium",
            confidence_score=0.85
        )
    
    def _analyze_load_balancer_costs(self, architecture: Dict[str, Any], provider: str) -> Optional[NetworkCostAnalysis]:
        """Analyze Load Balancer costs and consolidation opportunities"""
        
        load_balancers = architecture.get("load_balancers", [])
        if not load_balancers:
            return None
        
        lb_count = len(load_balancers)
        monthly_cost_per_lb = 22.50  # AWS ALB cost
        current_monthly_cost = lb_count * monthly_cost_per_lb
        
        # Check for consolidation opportunities
        underutilized_lbs = [lb for lb in load_balancers if lb.get("utilization", 0) < 0.3]
        
        if len(underutilized_lbs) > 1:
            # Can consolidate underutilized load balancers
            consolidated_count = lb_count - len(underutilized_lbs) + 1
            optimized_cost = consolidated_count * monthly_cost_per_lb
            monthly_savings = current_monthly_cost - optimized_cost
            
            optimization_actions = [
                f"Consolidate {len(underutilized_lbs)} underutilized load balancers",
                "Use host-based routing to combine multiple services",
                "Implement path-based routing for better resource utilization"
            ]
            
            return NetworkCostAnalysis(
                resource_type="load_balancer",
                provider=provider,
                current_monthly_cost=current_monthly_cost,
                optimized_monthly_cost=optimized_cost,
                monthly_savings=monthly_savings,
                annual_savings=monthly_savings * 12,
                optimization_actions=optimization_actions,
                implementation_complexity="low",
                confidence_score=0.90
            )
        
        return None
    
    def _analyze_cross_az_traffic_costs(self, architecture: Dict[str, Any], provider: str) -> Optional[NetworkCostAnalysis]:
        """Analyze cross-AZ traffic costs and optimization opportunities"""
        
        # Estimate based on typical patterns
        estimated_monthly_gb = architecture.get("estimated_cross_az_traffic_gb", 1000)
        cost_per_gb = 0.01
        current_monthly_cost = estimated_monthly_gb * cost_per_gb
        
        # Optimization: 40% reduction through locality optimization
        optimized_cost = current_monthly_cost * 0.6
        monthly_savings = current_monthly_cost - optimized_cost
        
        optimization_actions = [
            "Implement AZ-aware application deployment",
            "Optimize database read replicas for local AZ access",
            "Use connection pooling to reduce inter-AZ database connections",
            "Implement caching layers to reduce cross-AZ data transfer"
        ]
        
        return NetworkCostAnalysis(
            resource_type="cross_az_traffic",
            provider=provider,
            current_monthly_cost=current_monthly_cost,
            optimized_monthly_cost=optimized_cost,
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            optimization_actions=optimization_actions,
            implementation_complexity="medium",
            confidence_score=0.75
        )
    
    def recommend_network_topology(self,
                                 application_requirements: Dict[str, Any]) -> NetworkTopologyRecommendation:
        """
        Recommend optimal network topology based on application requirements
        """
        
        # Analyze requirements
        service_count = application_requirements.get("service_count", 1)
        compliance_required = bool(application_requirements.get("compliance_requirements"))
        high_availability = application_requirements.get("high_availability", False)
        expected_traffic = application_requirements.get("expected_traffic", "medium")
        security_tier = application_requirements.get("security_tier", "standard")
        
        # Determine optimal topology
        if service_count <= 3 and not compliance_required:
            topology = NetworkTopology.FLAT
            architecture = self._design_flat_topology()
            cost_multiplier = 1.0
            security_score = 0.7
        elif service_count <= 10 and security_tier == "standard":
            topology = NetworkTopology.THREE_TIER
            architecture = self._design_three_tier_topology()
            cost_multiplier = 1.3
            security_score = 0.85
        elif service_count > 10 or compliance_required:
            topology = NetworkTopology.MICROSERVICES
            architecture = self._design_microservices_topology()
            cost_multiplier = 1.5
            security_score = 0.95
        else:
            topology = NetworkTopology.HUB_SPOKE
            architecture = self._design_hub_spoke_topology()
            cost_multiplier = 1.2
            security_score = 0.90
        
        # Calculate scores
        base_cost = 150.0  # Base monthly cost
        cost_estimate = base_cost * cost_multiplier
        
        performance_score = 0.8 if topology in [NetworkTopology.FLAT, NetworkTopology.THREE_TIER] else 0.9
        scalability_score = 0.6 if topology == NetworkTopology.FLAT else 0.9
        
        # Generate reasoning
        reasoning = [
            f"Recommended {topology.value} topology for {service_count} services",
            f"Security score: {security_score:.1%} meets {security_tier} requirements",
            f"Estimated monthly cost: ${cost_estimate:.2f}"
        ]
        
        if compliance_required:
            reasoning.append("Compliance requirements drive network segmentation needs")
        
        if high_availability:
            reasoning.append("High availability requires multi-AZ deployment")
        
        return NetworkTopologyRecommendation(
            recommended_topology=topology,
            architecture_components=architecture,
            cost_estimate=cost_estimate,
            performance_score=performance_score,
            security_score=security_score,
            scalability_score=scalability_score,
            reasoning=reasoning,
            implementation_steps=self._generate_implementation_steps(topology)
        )
    
    def _design_flat_topology(self) -> Dict[str, Any]:
        """Design flat network topology for simple applications"""
        return {
            "vpc_count": 1,
            "subnet_tiers": ["public", "private"],
            "nat_gateways": 1,
            "load_balancers": 1,
            "security_groups": 3,
            "network_acls": "default"
        }
    
    def _design_three_tier_topology(self) -> Dict[str, Any]:
        """Design three-tier network topology (web/app/data)"""
        return {
            "vpc_count": 1,
            "subnet_tiers": ["public", "private", "database"],
            "nat_gateways": 2,  # Multi-AZ
            "load_balancers": 2,  # Public and internal
            "security_groups": 6,
            "network_acls": "custom",
            "database_subnets": True
        }
    
    def _design_microservices_topology(self) -> Dict[str, Any]:
        """Design microservices network topology with service mesh"""
        return {
            "vpc_count": 1,
            "subnet_tiers": ["public", "private", "database", "cache", "management"],
            "nat_gateways": 3,  # Multi-AZ with redundancy
            "load_balancers": 4,  # External, internal, service mesh
            "security_groups": 12,
            "network_acls": "strict",
            "service_mesh": True,
            "istio_gateway": True,
            "database_subnets": True,
            "cache_subnets": True
        }
    
    def _design_hub_spoke_topology(self) -> Dict[str, Any]:
        """Design hub-spoke topology for multi-region deployment"""
        return {
            "vpc_count": 4,  # Hub + 3 spokes
            "transit_gateway": True,
            "subnet_tiers": ["public", "private", "database"],
            "nat_gateways": 6,  # 2 per major VPC
            "load_balancers": 6,
            "security_groups": 15,
            "network_acls": "strict",
            "cross_region_peering": True
        }
    
    def _generate_implementation_steps(self, topology: NetworkTopology) -> List[str]:
        """Generate step-by-step implementation guide"""
        
        base_steps = [
            "1. Generate CIDR plan with conflict checking",
            "2. Create VPC with intelligent subnetting",
            "3. Configure security groups with least-privilege access",
            "4. Deploy NAT Gateways with cost optimization"
        ]
        
        if topology == NetworkTopology.THREE_TIER:
            base_steps.extend([
                "5. Create database subnet group with encryption",
                "6. Configure network ACLs for tier isolation",
                "7. Deploy internal load balancer for app tier"
            ])
        elif topology == NetworkTopology.MICROSERVICES:
            base_steps.extend([
                "5. Deploy service mesh infrastructure",
                "6. Configure ingress gateway with SSL termination",
                "7. Implement network policies for micro-segmentation",
                "8. Deploy monitoring and observability stack"
            ])
        elif topology == NetworkTopology.HUB_SPOKE:
            base_steps.extend([
                "5. Deploy Transit Gateway in hub region",
                "6. Create spoke VPCs with auto-peering",
                "7. Configure routing tables for hub-spoke traffic",
                "8. Implement cross-region connectivity"
            ])
        
        base_steps.append(f"{len(base_steps) + 1}. Apply network intelligence monitoring with infra-daemon")
        
        return base_steps
    
    def detect_cidr_conflicts(self, 
                            proposed_cidr: str, 
                            existing_networks: List[str]) -> Dict[str, Any]:
        """
        Detect CIDR conflicts and suggest alternatives
        
        This is called by the daemon for real-time conflict prevention
        """
        
        conflicts = []
        suggested_alternatives = []
        
        try:
            proposed_network = ipaddress.IPv4Network(proposed_cidr)
            
            for existing_cidr in existing_networks:
                try:
                    existing_network = ipaddress.IPv4Network(existing_cidr)
                    if proposed_network.overlaps(existing_network):
                        overlap = self._calculate_overlap(proposed_network, existing_network)
                        conflicts.append({
                            "existing_cidr": existing_cidr,
                            "proposed_cidr": proposed_cidr,
                            "overlap_range": str(overlap),
                            "affected_ips": overlap.num_addresses
                        })
                except ipaddress.AddressValueError:
                    logger.warning(f"Invalid existing CIDR: {existing_cidr}")
            
            # Generate alternative CIDRs if conflicts exist
            if conflicts:
                suggested_alternatives = self._generate_alternative_cidrs(
                    proposed_network, 
                    [ipaddress.IPv4Network(cidr) for cidr in existing_networks if self._is_valid_cidr(cidr)]
                )
            
        except ipaddress.AddressValueError:
            return {
                "has_conflicts": True,
                "conflicts": [],
                "error": f"Invalid CIDR format: {proposed_cidr}",
                "suggested_alternatives": []
            }
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "suggested_alternatives": suggested_alternatives,
            "proposed_cidr": proposed_cidr
        }
    
    def _calculate_overlap(self, net1: ipaddress.IPv4Network, net2: ipaddress.IPv4Network) -> ipaddress.IPv4Network:
        """Calculate the overlapping range between two networks"""
        if net1.subnet_of(net2):
            return net1
        elif net2.subnet_of(net1):
            return net2
        else:
            # Find intersection
            start_ip = max(net1.network_address, net2.network_address)
            end_ip = min(net1.broadcast_address, net2.broadcast_address)
            
            # Create network from the overlapping range
            # This is a simplified approach - in production you'd want more sophisticated overlap calculation
            return ipaddress.IPv4Network(f"{start_ip}/{max(net1.prefixlen, net2.prefixlen)}")
    
    def _generate_alternative_cidrs(self, 
                                  proposed: ipaddress.IPv4Network, 
                                  existing: List[ipaddress.IPv4Network]) -> List[str]:
        """Generate alternative CIDR blocks that don't conflict"""
        
        alternatives = []
        
        # Try different base networks
        base_networks = [
            ipaddress.IPv4Network("10.0.0.0/8"),
            ipaddress.IPv4Network("172.16.0.0/12"),
            ipaddress.IPv4Network("192.168.0.0/16")
        ]
        
        for base in base_networks:
            # Generate subnets of the same size as proposed
            try:
                candidate_subnets = list(base.subnets(new_prefix=proposed.prefixlen))
                
                for candidate in candidate_subnets[:5]:  # Check first 5 candidates
                    if not any(candidate.overlaps(existing_net) for existing_net in existing):
                        alternatives.append(str(candidate))
                        if len(alternatives) >= 3:  # Provide 3 alternatives
                            break
                
                if len(alternatives) >= 3:
                    break
                    
            except ValueError:
                continue  # Skip if prefix is too large
        
        return alternatives
    
    def _is_valid_cidr(self, cidr: str) -> bool:
        """Check if CIDR is valid"""
        try:
            ipaddress.IPv4Network(cidr)
            return True
        except ipaddress.AddressValueError:
            return False