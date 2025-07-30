"""
GKE Types and Data Classes

Core data structures for GCP GKE Intelligence Engine.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class NodePoolType(Enum):
    """Node pool types"""
    STANDARD = "standard"
    PREEMPTIBLE = "preemptible"
    SPOT = "spot"


class ClusterType(Enum):
    """Cluster deployment types"""
    ZONAL = "zonal"
    REGIONAL = "regional"


class SecurityLevel(Enum):
    """Security configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    HARDENED = "hardened"


@dataclass
class NodeConfig:
    """Node configuration specification"""
    machine_type: str
    disk_size_gb: int
    disk_type: str
    image_type: str
    preemptible: bool = False
    spot: bool = False


@dataclass
class AutoscalingConfig:
    """Autoscaling configuration"""
    enabled: bool
    min_node_count: int = 0
    max_node_count: int = 10


@dataclass
class NodePoolRecommendation:
    """Node pool optimization recommendation"""
    pool_name: str
    recommendations: List[str]
    cost_impact: Optional[float] = None
    priority: str = "medium"


@dataclass
class GKESecurityFinding:
    """Security audit finding"""
    severity: str
    category: str
    finding: str
    recommendation: str
    resource: Optional[str] = None


@dataclass
class GKECostAnalysis:
    """Cost analysis for GKE cluster"""
    current_monthly_cost: float
    optimized_monthly_cost: float
    potential_savings: float
    cost_breakdown: Dict[str, float]
    recommendations: List[str]


@dataclass
class GKEScalingPrediction:
    """Scaling prediction result"""
    action: str
    confidence: str
    recommendation: str
    suggested_actions: List[str]


@dataclass
class GKESecurityAssessment:
    """Comprehensive security assessment"""
    cluster_name: str
    assessment_timestamp: str
    overall_security_score: float
    security_findings: List[GKESecurityFinding]
    compliance_status: Dict[str, Any]
    risk_level: str
    recommendations: List[str]


@dataclass
class GKEOptimizationAnalysis:
    """Complete optimization analysis"""
    cluster_name: str
    current_cost_estimate: float
    optimized_cost_estimate: float
    potential_savings: float
    recommendations: List[str]
    node_pool_recommendations: List[NodePoolRecommendation]
    security_recommendations: List[str]
    scaling_recommendations: List[Dict[str, Any]]
    cost_breakdown: Dict[str, float]