"""
Dynamic Subnet Allocator

Automatically allocates and expands subnets based on real-time usage patterns
"""

import ipaddress
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .network_types import NetworkTier, SubnetAllocationRequest, SubnetAllocationResult
from .network_intelligence_core import NetworkIntelligence

logger = logging.getLogger(__name__)


class DynamicSubnetAllocator:
    """
    Dynamic Subnet Allocation Engine
    
    Automatically allocates and expands subnets based on real-time usage patterns
    """
    
    def __init__(self, network_intelligence: NetworkIntelligence):
        self.network_intelligence = network_intelligence
        self.allocated_subnets: Dict[str, SubnetAllocationResult] = {}
        self.usage_patterns: Dict[str, List[float]] = {}  # Track usage over time
        
    def allocate_subnet(self, request: SubnetAllocationRequest) -> SubnetAllocationResult:
        """
        Intelligently allocate subnet with dynamic expansion capability
        """
        
        # Calculate optimal subnet size with growth factor
        base_capacity = request.required_capacity
        growth_capacity = int(base_capacity * request.growth_factor)
        total_capacity = base_capacity + growth_capacity
        
        # Determine optimal CIDR prefix for capacity
        prefix = self._calculate_optimal_prefix(total_capacity)
        
        # Find available CIDR block
        available_cidr = self._find_available_cidr_block(
            request.region, 
            request.environment, 
            prefix,
            request.network_tier
        )
        
        if not available_cidr:
            raise ValueError(f"No available CIDR block for {total_capacity} IPs in {request.region}")
        
        # Generate subnet ID
        subnet_id = f"{request.service_name}-{request.environment}-{request.network_tier.value}-{int(time.time())}"
        
        # Check for compliance requirements
        if request.compliance_requirements:
            self._validate_compliance_requirements(available_cidr, request.compliance_requirements)
        
        # Calculate next expansion possibility
        next_expansion = self._calculate_next_expansion(available_cidr, request.region)
        
        allocation_result = SubnetAllocationResult(
            allocated_cidr=available_cidr,
            available_ips=total_capacity - 5,  # Reserve 5 for AWS/GCP system use
            reserved_for_growth=growth_capacity,
            subnet_id=subnet_id,
            allocation_timestamp=datetime.now(),
            expires_at=None,  # Dynamic subnets don't expire
            can_expand=bool(next_expansion),
            next_available_expansion=next_expansion
        )
        
        # Store allocation
        self.allocated_subnets[subnet_id] = allocation_result
        
        return allocation_result
    
    def _calculate_optimal_prefix(self, required_capacity: int) -> int:
        """Calculate optimal CIDR prefix for required capacity"""
        
        # Add overhead for system addresses
        total_needed = required_capacity + 10
        
        # Find smallest prefix that can accommodate capacity
        for prefix in range(16, 29):  # /16 to /28
            available_addresses = 2 ** (32 - prefix) - 2  # Subtract network and broadcast
            if available_addresses >= total_needed:
                return prefix
        
        raise ValueError(f"Cannot allocate subnet for {required_capacity} addresses")
    
    def _find_available_cidr_block(self, region: str, environment: str, prefix: int, tier: NetworkTier) -> Optional[str]:
        """Find available CIDR block that doesn't conflict"""
        
        # Get existing allocations for the region/environment
        existing_cidrs = self._get_existing_cidrs(region, environment)
        
        # Base networks for different tiers
        tier_bases = {
            NetworkTier.PUBLIC: "10.0.0.0/16",
            NetworkTier.PRIVATE: "10.1.0.0/16", 
            NetworkTier.DATABASE: "10.2.0.0/16",
            NetworkTier.MANAGEMENT: "10.3.0.0/16",
            NetworkTier.CACHE: "10.4.0.0/16"
        }
        
        base_network = ipaddress.IPv4Network(tier_bases.get(tier, "10.1.0.0/16"))
        
        # Generate candidate subnets
        try:
            candidate_subnets = list(base_network.subnets(new_prefix=prefix))
            
            for candidate in candidate_subnets:
                # Check for conflicts
                conflicts = self.network_intelligence.detect_cidr_conflicts(
                    str(candidate), 
                    existing_cidrs
                )
                
                if not conflicts["has_conflicts"]:
                    return str(candidate)
                    
        except ValueError:
            logger.error(f"Invalid prefix {prefix} for base network {base_network}")
        
        return None
    
    def _get_existing_cidrs(self, region: str, environment: str) -> List[str]:
        """Get existing CIDR allocations for conflict checking"""
        
        existing = []
        
        # Get from stored allocations
        for allocation in self.allocated_subnets.values():
            existing.append(allocation.allocated_cidr)
        
        # In production, would also query cloud providers for existing VPCs/subnets
        # For now, return stored allocations
        return existing
    
    def _validate_compliance_requirements(self, cidr: str, requirements: List[str]):
        """Validate subnet allocation meets compliance requirements"""
        
        network = ipaddress.IPv4Network(cidr)
        
        for requirement in requirements:
            if requirement == "HIPAA":
                # HIPAA requires dedicated tenancy - check if CIDR is large enough for isolation
                if network.prefixlen > 24:
                    raise ValueError(f"HIPAA compliance requires subnet size >= /24, got /{network.prefixlen}")
            
            elif requirement == "SOC2":
                # SOC2 requires network segmentation - ensure proper tier isolation
                if network.prefixlen > 26:
                    logger.warning(f"SOC2 compliance recommends subnet size >= /26 for proper segmentation")
            
            elif requirement == "PCI":
                # PCI requires network isolation for cardholder data
                if network.prefixlen > 24:
                    raise ValueError(f"PCI compliance requires subnet size >= /24, got /{network.prefixlen}")
    
    def _calculate_next_expansion(self, current_cidr: str, region: str) -> Optional[str]:
        """Calculate next available expansion CIDR"""
        
        current_network = ipaddress.IPv4Network(current_cidr)
        
        # Find next adjacent network of same size
        next_network_int = int(current_network.broadcast_address) + 1
        
        try:
            next_network = ipaddress.IPv4Network(f"{ipaddress.IPv4Address(next_network_int)}/{current_network.prefixlen}")
            
            # Check if next network is available
            existing_cidrs = self._get_existing_cidrs(region, "all")
            conflicts = self.network_intelligence.detect_cidr_conflicts(
                str(next_network), 
                existing_cidrs
            )
            
            if not conflicts["has_conflicts"]:
                return str(next_network)
                
        except (ipaddress.AddressValueError, ValueError):
            pass
        
        return None
    
    def expand_subnet(self, subnet_id: str) -> SubnetAllocationResult:
        """Expand existing subnet allocation"""
        
        if subnet_id not in self.allocated_subnets:
            raise ValueError(f"Subnet {subnet_id} not found")
        
        current_allocation = self.allocated_subnets[subnet_id]
        
        if not current_allocation.can_expand or not current_allocation.next_available_expansion:
            raise ValueError(f"Subnet {subnet_id} cannot be expanded")
        
        # Merge current and expansion CIDRs
        current_network = ipaddress.IPv4Network(current_allocation.allocated_cidr)
        expansion_network = ipaddress.IPv4Network(current_allocation.next_available_expansion)
        
        # Create supernet that encompasses both
        merged_cidr = list(ipaddress.collapse_addresses([current_network, expansion_network]))[0]
        
        # Update allocation
        current_allocation.allocated_cidr = str(merged_cidr)
        current_allocation.available_ips = merged_cidr.num_addresses - 5
        current_allocation.allocation_timestamp = datetime.now()
        current_allocation.next_available_expansion = self._calculate_next_expansion(
            str(merged_cidr), 
            "region"  # Would extract from subnet_id in production
        )
        
        return current_allocation
    
    def monitor_subnet_usage(self, subnet_id: str, current_usage_percent: float):
        """Monitor subnet usage for automatic expansion triggers"""
        
        if subnet_id not in self.usage_patterns:
            self.usage_patterns[subnet_id] = []
        
        self.usage_patterns[subnet_id].append(current_usage_percent)
        
        # Keep only last 24 hours of data (assuming hourly updates)
        if len(self.usage_patterns[subnet_id]) > 24:
            self.usage_patterns[subnet_id] = self.usage_patterns[subnet_id][-24:]
        
        # Check for automatic expansion trigger
        if current_usage_percent > 85.0:  # 85% utilization threshold
            recent_usage = self.usage_patterns[subnet_id][-3:]  # Last 3 hours
            if len(recent_usage) >= 3 and all(usage > 80.0 for usage in recent_usage):
                logger.warning(f"Subnet {subnet_id} approaching capacity: {current_usage_percent:.1f}%")
                
                # Trigger automatic expansion if possible
                if subnet_id in self.allocated_subnets:
                    allocation = self.allocated_subnets[subnet_id]
                    if allocation.can_expand:
                        logger.info(f"Auto-expanding subnet {subnet_id}")
                        try:
                            self.expand_subnet(subnet_id)
                        except Exception as e:
                            logger.error(f"Failed to auto-expand subnet {subnet_id}: {e}")