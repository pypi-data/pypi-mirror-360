"""
Network Intelligence Types and Enums

Common types, enums, and data classes used across the network intelligence system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NetworkTier(Enum):
    """Network tier classifications"""
    PUBLIC = "public"
    PRIVATE = "private" 
    DATABASE = "database"
    MANAGEMENT = "management"
    CACHE = "cache"


class NetworkTopology(Enum):
    """Network topology patterns"""
    FLAT = "flat"
    THREE_TIER = "three_tier"
    HUB_SPOKE = "hub_spoke"
    MESH = "mesh"
    MICROSERVICES = "microservices"


@dataclass
class CIDRPlan:
    """CIDR allocation plan for an organization"""
    organization_name: str
    global_supernet: str  # e.g., "10.0.0.0/8"
    regional_allocations: Dict[str, str]  # region -> CIDR
    environment_allocations: Dict[str, Dict[str, str]]  # region -> env -> CIDR
    subnet_patterns: Dict[NetworkTier, str]  # tier -> pattern
    reserved_blocks: List[str]  # Reserved for future expansion
    conflict_free: bool
    created_at: datetime


@dataclass
class NetworkSecurityProfile:
    """Network security configuration profile"""
    profile_name: str
    compliance_frameworks: List[str]  # SOC2, HIPAA, PCI, etc.
    default_deny: bool
    required_protocols: List[str]
    forbidden_protocols: List[str]
    mandatory_encryption: bool
    logging_required: bool
    monitoring_endpoints: List[str]


@dataclass
class NetworkCostAnalysis:
    """Network cost analysis and optimization recommendations"""
    resource_type: str
    provider: str
    current_monthly_cost: float
    optimized_monthly_cost: float
    monthly_savings: float
    annual_savings: float
    optimization_actions: List[str]
    implementation_complexity: str  # low, medium, high
    confidence_score: float


@dataclass
class NetworkTopologyRecommendation:
    """Intelligent network topology recommendation"""
    recommended_topology: NetworkTopology
    architecture_components: Dict[str, Any]
    cost_estimate: float
    performance_score: float
    security_score: float
    scalability_score: float
    reasoning: List[str]
    implementation_steps: List[str]


@dataclass
class SubnetAllocationRequest:
    """Request for dynamic subnet allocation"""
    service_name: str
    region: str
    environment: str
    network_tier: NetworkTier
    required_capacity: int  # Number of IP addresses needed
    growth_factor: float = 2.0  # Multiplier for future growth
    compliance_requirements: List[str] = None
    priority: str = "medium"  # low, medium, high, critical


@dataclass
class SubnetAllocationResult:
    """Result of dynamic subnet allocation"""
    allocated_cidr: str
    available_ips: int
    reserved_for_growth: int
    subnet_id: str
    allocation_timestamp: datetime
    expires_at: Optional[datetime]
    can_expand: bool
    next_available_expansion: Optional[str]


@dataclass
class NetworkConflictAlert:
    """Alert for network conflicts"""
    conflict_type: str
    severity: str  # low, medium, high, critical
    affected_resources: List[str]
    conflicting_cidrs: List[str]
    impact_assessment: str
    recommended_actions: List[str]
    auto_remediation_available: bool
    detected_at: datetime