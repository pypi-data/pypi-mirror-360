"""
Core IntelligentApplication Class

The main class that combines all mixins to provide the revolutionary 
Cross-Cloud Magic developer experience.
"""

import logging
from typing import Dict, Optional

from ..cross_cloud_intelligence import cross_cloud_intelligence
from ..provider_constraints import ProviderConstraints

from .data_classes import OptimizationPreferences, ServiceConfiguration
from .constraint_methods import ConstraintMethodsMixin
from .service_methods import ServiceMethodsMixin
from .lifecycle_methods import LifecycleMethodsMixin
from .resource_creation import ResourceCreationMixin
from .preview_methods import PreviewMethodsMixin

logger = logging.getLogger(__name__)


class IntelligentApplication(
    ConstraintMethodsMixin,
    ServiceMethodsMixin, 
    LifecycleMethodsMixin,
    ResourceCreationMixin,
    PreviewMethodsMixin
):
    """
    Revolutionary IntelligentApplication class
    
    Provides the magical developer experience where infrastructure
    automatically selects optimal providers per service.
    
    This is the feature that makes traditional IaC tools obsolete.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.services: Dict[str, ServiceConfiguration] = {}
        self.optimization_preferences = OptimizationPreferences()
        self.cross_cloud_intelligence = cross_cloud_intelligence
        self.auto_optimization_enabled = False
        self.created_resources = {}
        self.provider_constraints = ProviderConstraints()  # User-defined constraints
        
        logger.info(f"🚀 Initializing IntelligentApplication: {name}")
    
    def auto_optimize(self, priorities: Optional[Dict[str, float]] = None) -> 'IntelligentApplication':
        """
        Enable Cross-Cloud Magic auto-optimization
        
        This is the revolutionary feature that automatically selects
        optimal providers for each service.
        
        Args:
            priorities: Optional optimization priorities
                       {'cost': 0.4, 'performance': 0.3, 'reliability': 0.2, 'compliance': 0.1}
        
        Returns:
            Self for method chaining
        """
        
        self.auto_optimization_enabled = True
        
        if priorities:
            self.optimization_preferences.cost_weight = priorities.get('cost', 0.4)
            self.optimization_preferences.performance_weight = priorities.get('performance', 0.3)
            self.optimization_preferences.reliability_weight = priorities.get('reliability', 0.2)
            self.optimization_preferences.compliance_weight = priorities.get('compliance', 0.1)
            
            # Normalize weights
            self.optimization_preferences.normalize()
        
        logger.info(f"🧠 Auto-optimization enabled for {self.name}")
        logger.info(f"   Priorities: Cost={self.optimization_preferences.cost_weight:.1%}, "
                   f"Performance={self.optimization_preferences.performance_weight:.1%}, "
                   f"Reliability={self.optimization_preferences.reliability_weight:.1%}, "
                   f"Compliance={self.optimization_preferences.compliance_weight:.1%}")
        
        return self