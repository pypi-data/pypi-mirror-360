"""
Network Intelligence Engine - Refactored Modular Version

Enterprise Networking Intelligence for Nexus with modular architecture.

The world's first intelligent networking system that provides:
- Automatic CIDR planning and conflict prevention
- Cost-optimized network architecture
- Security-first networking with compliance automation
- Multi-cloud network topology optimization
- Predictive network failure prevention

This extends the Nexus Engine with enterprise-grade networking intelligence.
"""

# Import all network intelligence components
from .network_types import (
    NetworkTier, NetworkTopology, CIDRPlan, NetworkSecurityProfile,
    NetworkCostAnalysis, NetworkTopologyRecommendation, SubnetAllocationRequest,
    SubnetAllocationResult, NetworkConflictAlert
)

from .network_intelligence_core import NetworkIntelligence
from .subnet_allocator import DynamicSubnetAllocator
from .compliance_validator import ComplianceNetworkValidator
from .conflict_monitor import NetworkConflictMonitor
from .cross_cloud_cidr_manager import CrossCloudCIDRManager

# Global Network Intelligence instance for backward compatibility
network_intelligence = NetworkIntelligence()

# Export all components for easy importing
__all__ = [
    # Types and Enums
    'NetworkTier',
    'NetworkTopology', 
    'CIDRPlan',
    'NetworkSecurityProfile',
    'NetworkCostAnalysis',
    'NetworkTopologyRecommendation',
    'SubnetAllocationRequest',
    'SubnetAllocationResult',
    'NetworkConflictAlert',
    
    # Core Classes
    'NetworkIntelligence',
    'DynamicSubnetAllocator',
    'ComplianceNetworkValidator', 
    'NetworkConflictMonitor',
    'CrossCloudCIDRManager',
    
    # Global instance
    'network_intelligence'
]