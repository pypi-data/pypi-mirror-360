"""
Data Classes for IntelligentApplication

Core data structures used throughout the Cross-Cloud Magic system.
"""

from typing import Dict, Any
from dataclasses import dataclass

from ..cross_cloud_intelligence import ServiceRequirements, ServiceCategory


@dataclass
class OptimizationPreferences:
    """User-defined optimization preferences"""
    cost_weight: float = 0.4           # How much to prioritize cost (0.0-1.0)
    performance_weight: float = 0.3    # How much to prioritize performance
    reliability_weight: float = 0.2    # How much to prioritize reliability  
    compliance_weight: float = 0.1     # How much to prioritize compliance
    
    def normalize(self):
        """Normalize weights to sum to 1.0"""
        total = self.cost_weight + self.performance_weight + self.reliability_weight + self.compliance_weight
        if total > 0:
            self.cost_weight /= total
            self.performance_weight /= total
            self.reliability_weight /= total
            self.compliance_weight /= total


@dataclass
class ServiceConfiguration:
    """Configuration for a specific service"""
    service_name: str
    service_type: str
    service_category: ServiceCategory
    configuration: Dict[str, Any]
    requirements: ServiceRequirements