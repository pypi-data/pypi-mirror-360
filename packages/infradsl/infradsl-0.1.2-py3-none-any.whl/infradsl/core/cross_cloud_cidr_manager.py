"""
Cross-Cloud CIDR Manager

Unified IP address planning and management across AWS, GCP, Azure, and other providers
"""

import ipaddress
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .network_types import NetworkTier
from .network_intelligence_core import NetworkIntelligence

logger = logging.getLogger(__name__)


class CrossCloudCIDRManager:
    """
    Cross-Cloud CIDR Management System
    
    Unified IP address planning and management across AWS, GCP, Azure, and other providers
    """
    
    def __init__(self, network_intelligence: NetworkIntelligence):
        self.network_intelligence = network_intelligence
        self.provider_allocations: Dict[str, Dict[str, Any]] = {}
        self.global_allocation_map: Dict[str, str] = {}  # region -> CIDR
        self.cross_cloud_peering: Dict[str, List[str]] = {}  # provider -> list of peer providers
        
        # Provider-specific CIDR preferences
        self.provider_preferences = {
            "aws": {
                "preferred_supernets": ["10.0.0.0/8", "172.16.0.0/12"],
                "default_vpc_size": "/16",
                "region_allocation_strategy": "geographic_proximity"
            },
            "gcp": {
                "preferred_supernets": ["10.0.0.0/8", "192.168.0.0/16"], 
                "default_vpc_size": "/16",
                "region_allocation_strategy": "performance_optimized"
            },
            "azure": {
                "preferred_supernets": ["10.0.0.0/8", "172.16.0.0/12"],
                "default_vnet_size": "/16", 
                "region_allocation_strategy": "cost_optimized"
            },
            "digitalocean": {
                "preferred_supernets": ["10.0.0.0/8"],
                "default_vpc_size": "/20",
                "region_allocation_strategy": "simple_sequential"
            }
        }
    
    def generate_global_cidr_plan(self, 
                                organization_name: str,
                                target_providers: List[str],
                                target_regions: Dict[str, List[str]],  # provider -> regions
                                connectivity_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate unified CIDR plan across multiple cloud providers
        """
        
        if connectivity_requirements is None:
            connectivity_requirements = {}
        
        # Calculate total regional requirements
        total_regions = sum(len(regions) for regions in target_regions.values())
        
        # Select global supernet based on scale
        if total_regions <= 8:
            global_supernet = "10.0.0.0/8"
            provider_prefix = 12  # /12 per provider (1M addresses each)
        elif total_regions <= 16:
            global_supernet = "10.0.0.0/8" 
            provider_prefix = 13  # /13 per provider (512K addresses each)
        else:
            global_supernet = "10.0.0.0/8"
            provider_prefix = 14  # /14 per provider (256K addresses each)
        
        base_network = ipaddress.IPv4Network(global_supernet)
        provider_networks = list(base_network.subnets(new_prefix=provider_prefix))
        
        global_plan = {
            "organization_name": organization_name,
            "global_supernet": global_supernet,
            "total_providers": len(target_providers),
            "total_regions": total_regions,
            "provider_allocations": {},
            "cross_cloud_connectivity": {},
            "conflict_analysis": {"conflicts_detected": False, "conflicts": []},
            "created_at": datetime.now().isoformat()
        }
        
        # Allocate CIDRs per provider
        for i, provider in enumerate(target_providers):
            if i >= len(provider_networks):
                raise ValueError(f"Insufficient IP space for provider {provider}")
            
            provider_network = provider_networks[i]
            provider_regions = target_regions.get(provider, [])
            
            # Generate provider-specific allocations
            provider_allocation = self._generate_provider_allocation(
                provider,
                str(provider_network),
                provider_regions,
                connectivity_requirements.get(provider, {})
            )
            
            global_plan["provider_allocations"][provider] = provider_allocation
            
            # Track for conflict analysis
            self.provider_allocations[provider] = provider_allocation
        
        # Analyze cross-provider connectivity requirements
        if connectivity_requirements.get("cross_cloud_peering"):
            global_plan["cross_cloud_connectivity"] = self._plan_cross_cloud_connectivity(
                target_providers,
                connectivity_requirements["cross_cloud_peering"]
            )
        
        # Perform global conflict analysis
        conflict_analysis = self._analyze_global_conflicts(global_plan["provider_allocations"])
        global_plan["conflict_analysis"] = conflict_analysis
        
        return global_plan
    
    def _generate_provider_allocation(self, 
                                    provider: str, 
                                    provider_cidr: str, 
                                    regions: List[str],
                                    connectivity_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CIDR allocation for a specific provider"""
        
        provider_network = ipaddress.IPv4Network(provider_cidr)
        preferences = self.provider_preferences.get(provider, self.provider_preferences["aws"])
        
        # Determine regional prefix based on number of regions
        if len(regions) <= 4:
            regional_prefix = provider_network.prefixlen + 2  # 4 regions max
        elif len(regions) <= 8:
            regional_prefix = provider_network.prefixlen + 3  # 8 regions max
        elif len(regions) <= 16:
            regional_prefix = provider_network.prefixlen + 4  # 16 regions max
        else:
            raise ValueError(f"Too many regions ({len(regions)}) for provider {provider}")
        
        regional_networks = list(provider_network.subnets(new_prefix=regional_prefix))
        
        allocation = {
            "provider": provider,
            "provider_cidr": provider_cidr,
            "strategy": preferences["region_allocation_strategy"],
            "regional_allocations": {},
            "reserved_blocks": [],
            "connectivity_config": connectivity_requirements
        }
        
        # Allocate regions based on strategy
        if preferences["region_allocation_strategy"] == "geographic_proximity":
            sorted_regions = self._sort_regions_geographically(regions, provider)
        elif preferences["region_allocation_strategy"] == "performance_optimized":
            sorted_regions = self._sort_regions_by_performance(regions, provider)
        elif preferences["region_allocation_strategy"] == "cost_optimized":
            sorted_regions = self._sort_regions_by_cost(regions, provider)
        else:
            sorted_regions = regions  # simple_sequential
        
        for i, region in enumerate(sorted_regions):
            if i >= len(regional_networks):
                logger.warning(f"Insufficient IP space for region {region} in provider {provider}")
                continue
            
            regional_network = regional_networks[i]
            
            # Generate environment allocations within region
            env_allocations = self._generate_regional_environment_allocations(
                regional_network, 
                provider, 
                region
            )
            
            allocation["regional_allocations"][region] = {
                "region_cidr": str(regional_network),
                "available_ips": regional_network.num_addresses - 1000,  # Reserve for overhead
                "environment_allocations": env_allocations,
                "can_expand": i < len(regional_networks) - 1
            }
        
        # Reserve remaining blocks for future expansion
        if len(regions) < len(regional_networks):
            for i in range(len(regions), min(len(regions) + 2, len(regional_networks))):
                allocation["reserved_blocks"].append(str(regional_networks[i]))
        
        return allocation
    
    def _generate_regional_environment_allocations(self, 
                                                 regional_network: ipaddress.IPv4Network,
                                                 provider: str,
                                                 region: str) -> Dict[str, Any]:
        """Generate environment allocations within a region"""
        
        # Standard environments: prod (50%), staging (25%), dev (15%), mgmt (10%)
        env_ratios = {
            "production": 0.50,
            "staging": 0.25, 
            "development": 0.15,
            "management": 0.10
        }
        
        # Calculate environment prefix (typically +2 from regional)
        env_prefix = regional_network.prefixlen + 2
        env_networks = list(regional_network.subnets(new_prefix=env_prefix))
        
        allocations = {}
        
        for i, (env_name, ratio) in enumerate(env_ratios.items()):
            if i >= len(env_networks):
                break
                
            env_network = env_networks[i]
            
            # Generate subnet tier allocations within environment
            tier_allocations = self._generate_tier_allocations(env_network, provider)
            
            allocations[env_name] = {
                "environment_cidr": str(env_network),
                "allocated_ratio": ratio,
                "available_ips": env_network.num_addresses - 100,
                "tier_allocations": tier_allocations
            }
        
        return allocations
    
    def _generate_tier_allocations(self, env_network: ipaddress.IPv4Network, provider: str) -> Dict[str, str]:
        """Generate network tier allocations within an environment"""
        
        # Standard tiers with typical sizing
        tier_configs = {
            NetworkTier.PUBLIC: {"ratio": 0.10, "min_prefix": 24},
            NetworkTier.PRIVATE: {"ratio": 0.60, "min_prefix": 20}, 
            NetworkTier.DATABASE: {"ratio": 0.20, "min_prefix": 24},
            NetworkTier.CACHE: {"ratio": 0.05, "min_prefix": 26},
            NetworkTier.MANAGEMENT: {"ratio": 0.05, "min_prefix": 26}
        }
        
        tier_prefix = env_network.prefixlen + 3  # 8 tier subnets max
        tier_networks = list(env_network.subnets(new_prefix=tier_prefix))
        
        allocations = {}
        
        for i, (tier, config) in enumerate(tier_configs.items()):
            if i >= len(tier_networks):
                break
            
            tier_network = tier_networks[i]
            
            # Adjust prefix based on minimum requirements
            final_prefix = max(tier_network.prefixlen, config["min_prefix"])
            if final_prefix > tier_network.prefixlen:
                # Need to create smaller subnet
                adjusted_subnets = list(tier_network.subnets(new_prefix=final_prefix))
                if adjusted_subnets:
                    allocations[tier.value] = str(adjusted_subnets[0])
            else:
                allocations[tier.value] = str(tier_network)
        
        return allocations
    
    def _sort_regions_geographically(self, regions: List[str], provider: str) -> List[str]:
        """Sort regions by geographic proximity"""
        
        # Simplified geographic grouping - in production would use actual coordinates
        geographic_groups = {
            "aws": {
                "us": ["us-east-1", "us-east-2", "us-west-1", "us-west-2"],
                "eu": ["eu-west-1", "eu-west-2", "eu-central-1"],
                "ap": ["ap-southeast-1", "ap-southeast-2", "ap-northeast-1"]
            },
            "gcp": {
                "us": ["us-central1", "us-east1", "us-west1"],
                "eu": ["europe-west1", "europe-west2", "europe-west3"],
                "asia": ["asia-southeast1", "asia-northeast1"]
            }
        }
        
        provider_groups = geographic_groups.get(provider, {})
        sorted_regions = []
        
        # Group regions geographically
        for group_regions in provider_groups.values():
            for region in regions:
                if region in group_regions and region not in sorted_regions:
                    sorted_regions.append(region)
        
        # Add any remaining regions
        for region in regions:
            if region not in sorted_regions:
                sorted_regions.append(region)
        
        return sorted_regions
    
    def _sort_regions_by_performance(self, regions: List[str], provider: str) -> List[str]:
        """Sort regions by performance characteristics"""
        
        # Simplified performance scoring - in production would use real metrics
        performance_scores = {
            "aws": {
                "us-east-1": 10, "us-west-2": 9, "eu-west-1": 8,
                "ap-southeast-1": 7, "us-east-2": 6
            },
            "gcp": {
                "us-central1": 10, "us-east1": 9, "europe-west1": 8,
                "asia-southeast1": 7
            }
        }
        
        scores = performance_scores.get(provider, {})
        return sorted(regions, key=lambda r: scores.get(r, 5), reverse=True)
    
    def _sort_regions_by_cost(self, regions: List[str], provider: str) -> List[str]:
        """Sort regions by cost optimization"""
        
        # Simplified cost scoring - in production would use real pricing data
        cost_scores = {
            "aws": {
                "us-east-1": 10, "us-east-2": 9, "us-west-1": 6,
                "eu-west-1": 7, "ap-southeast-1": 5
            },
            "gcp": {
                "us-central1": 10, "us-east1": 8, "europe-west1": 6,
                "asia-southeast1": 5
            }
        }
        
        scores = cost_scores.get(provider, {})
        return sorted(regions, key=lambda r: scores.get(r, 5), reverse=True)
    
    def _plan_cross_cloud_connectivity(self, 
                                     providers: List[str], 
                                     peering_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan cross-cloud connectivity and peering"""
        
        connectivity_plan = {
            "peering_connections": [],
            "transit_gateways": {},
            "vpn_connections": [],
            "estimated_costs": {},
            "bandwidth_requirements": {}
        }
        
        # Analyze required peering connections
        for provider1 in providers:
            for provider2 in providers:
                if provider1 != provider2:
                    peering_key = f"{provider1}-{provider2}"
                    reverse_key = f"{provider2}-{provider1}"
                    
                    # Check if peering is required and not already planned
                    if (peering_requirements.get(peering_key) and 
                        not any(conn["connection_id"] == peering_key for conn in connectivity_plan["peering_connections"])):
                        
                        connection = {
                            "connection_id": peering_key,
                            "provider_1": provider1,
                            "provider_2": provider2,
                            "connection_type": self._determine_connection_type(provider1, provider2),
                            "bandwidth_requirement": peering_requirements[peering_key].get("bandwidth", "1Gbps"),
                            "estimated_monthly_cost": self._estimate_connection_cost(provider1, provider2),
                            "latency_requirement": peering_requirements[peering_key].get("latency", "< 100ms")
                        }
                        
                        connectivity_plan["peering_connections"].append(connection)
        
        return connectivity_plan
    
    def _determine_connection_type(self, provider1: str, provider2: str) -> str:
        """Determine optimal connection type between providers"""
        
        # Connection type mapping based on provider compatibility
        connection_types = {
            ("aws", "gcp"): "vpn_gateway",
            ("aws", "azure"): "express_route_gateway", 
            ("gcp", "azure"): "interconnect_vpn",
            ("aws", "digitalocean"): "vpn_tunnel",
            ("gcp", "digitalocean"): "vpn_tunnel",
            ("azure", "digitalocean"): "vpn_tunnel"
        }
        
        key = tuple(sorted([provider1, provider2]))
        return connection_types.get(key, "vpn_tunnel")
    
    def _estimate_connection_cost(self, provider1: str, provider2: str) -> float:
        """Estimate monthly cost for cross-cloud connection"""
        
        # Simplified cost estimation - in production would use real pricing
        base_costs = {
            "vpn_gateway": 45.0,
            "express_route_gateway": 200.0,
            "interconnect_vpn": 100.0,
            "vpn_tunnel": 25.0
        }
        
        connection_type = self._determine_connection_type(provider1, provider2)
        return base_costs.get(connection_type, 50.0)
    
    def _analyze_global_conflicts(self, provider_allocations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conflicts across all provider allocations"""
        
        conflicts = []
        all_cidrs = []
        
        # Collect all CIDRs across providers
        for provider, allocation in provider_allocations.items():
            provider_cidr = allocation["provider_cidr"]
            all_cidrs.append({"provider": provider, "cidr": provider_cidr, "type": "provider"})
            
            for region, region_data in allocation["regional_allocations"].items():
                region_cidr = region_data["region_cidr"]
                all_cidrs.append({"provider": provider, "region": region, "cidr": region_cidr, "type": "region"})
        
        # Check for conflicts
        for i, cidr1 in enumerate(all_cidrs):
            for cidr2 in all_cidrs[i+1:]:
                conflict_result = self.network_intelligence.detect_cidr_conflicts(
                    cidr1["cidr"], 
                    [cidr2["cidr"]]
                )
                
                if conflict_result["has_conflicts"]:
                    conflicts.append({
                        "conflict_type": "cross_provider_overlap",
                        "cidr_1": cidr1,
                        "cidr_2": cidr2,
                        "overlap_details": conflict_result["conflicts"][0] if conflict_result["conflicts"] else {}
                    })
        
        return {
            "conflicts_detected": len(conflicts) > 0,
            "total_conflicts": len(conflicts),
            "conflicts": conflicts,
            "resolution_recommendations": self._generate_conflict_resolutions(conflicts)
        }
    
    def _generate_conflict_resolutions(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for resolving conflicts"""
        
        if not conflicts:
            return ["No conflicts detected - CIDR allocation is clean"]
        
        recommendations = []
        
        for conflict in conflicts:
            cidr1 = conflict["cidr_1"] 
            cidr2 = conflict["cidr_2"]
            
            if cidr1["type"] == "provider" and cidr2["type"] == "provider":
                recommendations.append(
                    f"Critical: Provider-level CIDR conflict between {cidr1['provider']} and {cidr2['provider']} - "
                    f"redesign global supernet allocation"
                )
            elif cidr1["type"] == "region" and cidr2["type"] == "region":
                recommendations.append(
                    f"Regional CIDR conflict between {cidr1['provider']}:{cidr1['region']} and "
                    f"{cidr2['provider']}:{cidr2['region']} - adjust regional allocations"
                )
        
        recommendations.append("Consider using larger global supernet (e.g., 10.0.0.0/8 -> dedicated /12 per provider)")
        
        return recommendations
    
    def validate_cross_cloud_plan(self, global_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate cross-cloud CIDR plan for deployment readiness"""
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for conflicts
        if global_plan["conflict_analysis"]["conflicts_detected"]:
            validation["valid"] = False
            validation["errors"].append("CIDR conflicts detected - plan cannot be deployed")
            validation["errors"].extend(global_plan["conflict_analysis"]["resolution_recommendations"])
        
        # Validate provider allocations
        for provider, allocation in global_plan["provider_allocations"].items():
            provider_validation = self._validate_provider_allocation(provider, allocation)
            
            if not provider_validation["valid"]:
                validation["valid"] = False
                validation["errors"].extend(provider_validation["errors"])
            
            validation["warnings"].extend(provider_validation["warnings"])
            validation["recommendations"].extend(provider_validation["recommendations"])
        
        return validation
    
    def _validate_provider_allocation(self, provider: str, allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual provider allocation"""
        
        validation = {"valid": True, "warnings": [], "errors": [], "recommendations": []}
        
        # Check if provider CIDR is large enough
        provider_network = ipaddress.IPv4Network(allocation["provider_cidr"])
        regions_count = len(allocation["regional_allocations"])
        
        if provider_network.prefixlen > 12 and regions_count > 4:
            validation["warnings"].append(
                f"{provider}: Small provider CIDR /{provider_network.prefixlen} for {regions_count} regions"
            )
        
        # Check regional allocations
        for region, region_data in allocation["regional_allocations"].items():
            region_network = ipaddress.IPv4Network(region_data["region_cidr"])
            
            if region_network.prefixlen > 20:
                validation["warnings"].append(
                    f"{provider}:{region}: Small regional CIDR /{region_network.prefixlen} may limit scaling"
                )
            
            # Check environment allocations
            env_count = len(region_data["environment_allocations"])
            if env_count < 3:
                validation["recommendations"].append(
                    f"{provider}:{region}: Consider adding more environments (currently {env_count})"
                )
        
        return validation