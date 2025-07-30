"""
Service Definition Methods for IntelligentApplication

Methods for defining various types of cloud services that will be 
automatically optimized by Cross-Cloud Magic.
"""

import logging
from typing import TYPE_CHECKING, List

from ..cross_cloud_intelligence import ServiceRequirements, ServiceCategory
from .data_classes import ServiceConfiguration

if TYPE_CHECKING:
    from .core import IntelligentApplication

logger = logging.getLogger(__name__)


class ServiceMethodsMixin:
    """Mixin providing service definition methods"""
    
    def database(self: 'IntelligentApplication', 
                db_type: str, 
                **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent database service
        
        Args:
            db_type: Database type (postgresql, mysql, mongodb, etc.)
            **kwargs: Additional configuration options
                     performance: basic, standard, high, ultra
                     reliability: basic, high, mission_critical
                     compliance: List of compliance requirements
                     regions: List of geographic regions
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-database"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.DATABASE,
            service_type=db_type,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=db_type,
            service_category=ServiceCategory.DATABASE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"📊 Added database service: {db_type}")
        
        return self
    
    def compute(self: 'IntelligentApplication', 
               compute_type: str,
               **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent compute service
        
        Args:
            compute_type: Compute type (web-servers, api-servers, workers, etc.)
            **kwargs: Additional configuration options
                     scaling: minimal, moderate, aggressive
                     performance: basic, standard, high, ultra
                     global_distribution: bool
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-compute"
        
        # Determine performance tier based on scaling requirements
        scaling = kwargs.get('scaling', 'moderate')
        if scaling == 'aggressive':
            performance_tier = 'high'
        elif scaling == 'minimal':
            performance_tier = 'basic'
        else:
            performance_tier = kwargs.get('performance', 'standard')
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.COMPUTE,
            service_type=compute_type,
            performance_tier=performance_tier,
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1', 'eu-west-1'] if kwargs.get('global_distribution') else ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=compute_type,
            service_category=ServiceCategory.COMPUTE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🖥️ Added compute service: {compute_type}")
        
        return self
    
    def cdn(self: 'IntelligentApplication', 
           content_type: str,
           **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent CDN service
        
        Args:
            content_type: Content type (static-assets, api-cache, media, etc.)
            **kwargs: Additional configuration options
                     performance: basic, standard, high, ultra
                     edge_optimization: bool
                     global_distribution: bool
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-cdn"
        
        # CDN services typically need global distribution
        regions = ['global'] if kwargs.get('global_distribution', True) else ['us-east-1']
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.CDN,
            service_type=content_type,
            performance_tier=kwargs.get('performance', 'high'),  # CDN typically needs high performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=regions,
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.2,  # CDN is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=content_type,
            service_category=ServiceCategory.CDN,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🌐 Added CDN service: {content_type}")
        
        return self
    
    def storage(self: 'IntelligentApplication', 
               storage_type: str,
               **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent storage service
        
        Args:
            storage_type: Storage type (user-uploads, backups, data-lake, etc.)
            **kwargs: Additional configuration options
                     access_pattern: frequent, infrequent, archive
                     backup_requirements: none, basic, automated
                     compliance: List of compliance requirements
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-storage"
        
        # Adjust performance requirements based on access pattern
        access_pattern = kwargs.get('access_pattern', 'frequent')
        if access_pattern == 'archive':
            performance_tier = 'basic'
        elif access_pattern == 'infrequent':
            performance_tier = 'standard'
        else:
            performance_tier = kwargs.get('performance', 'standard')
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.STORAGE,
            service_type=storage_type,
            performance_tier=performance_tier,
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight * 1.2,  # Storage is often cost-sensitive
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=storage_type,
            service_category=ServiceCategory.STORAGE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"💾 Added storage service: {storage_type}")
        
        return self
    
    def monitoring(self: 'IntelligentApplication', 
                  monitoring_type: str,
                  **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent monitoring service
        
        Args:
            monitoring_type: Monitoring type (full-stack, metrics-only, logs-only, etc.)
            **kwargs: Additional configuration options
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-monitoring"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.MONITORING,
            service_type=monitoring_type,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=monitoring_type,
            service_category=ServiceCategory.MONITORING,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"📈 Added monitoring service: {monitoring_type}")
        
        return self
    
    def function(self: 'IntelligentApplication', 
                function_name: str,
                **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent serverless function
        
        Args:
            function_name: Function identifier
            **kwargs: Additional configuration options
                     runtime: python, nodejs, go, etc.
                     memory: Memory allocation in MB
                     timeout: Function timeout in seconds
                     triggers: List of trigger types
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-function"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.FUNCTIONS,
            service_type=function_name,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight * 1.1,  # Functions are cost-sensitive
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=function_name,
            service_category=ServiceCategory.FUNCTIONS,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"⚡ Added serverless function: {function_name}")
        
        return self
    
    def container(self: 'IntelligentApplication', 
                 container_name: str,
                 **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent containerized service
        
        Args:
            container_name: Container service identifier
            **kwargs: Additional configuration options
                     image: Container image
                     cpu: CPU allocation
                     memory: Memory allocation
                     scaling: Scaling configuration
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-container"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.CONTAINERS,
            service_type=container_name,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=container_name,
            service_category=ServiceCategory.CONTAINERS,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🐳 Added container service: {container_name}")
        
        return self
    
    def kubernetes(self: 'IntelligentApplication',
                  cluster_name: str,
                  **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent Kubernetes cluster
        
        Args:
            cluster_name: Kubernetes cluster identifier
            **kwargs: Additional configuration options
                     node_count: Number of nodes
                     node_type: Node instance type
                     auto_scaling: Enable auto-scaling
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-kubernetes"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.KUBERNETES,
            service_type="kubernetes",
            performance_tier=kwargs.get('performance', 'high'),  # K8s typically needs good performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.1,  # K8s is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type="kubernetes",
            service_category=ServiceCategory.KUBERNETES,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"☸️ Added Kubernetes cluster: {cluster_name}")
        
        return self
    
    def load_balancer(self: 'IntelligentApplication',
                     lb_name: str,
                     **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent load balancer
        
        Args:
            lb_name: Load balancer identifier
            **kwargs: Additional configuration options
                     type: application, network, classic
                     ssl_termination: Enable SSL termination
                     health_checks: Health check configuration
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-load-balancer"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.LOAD_BALANCER,
            service_type="load-balancer",
            performance_tier=kwargs.get('performance', 'high'),  # LB needs good performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.2,  # LB is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight * 1.1,  # LB is reliability-critical
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type="load-balancer",
            service_category=ServiceCategory.LOAD_BALANCER,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"⚖️ Added load balancer: {lb_name}")
        
        return self
    
    def compliance(self: 'IntelligentApplication', standards: List[str]) -> 'IntelligentApplication':
        """
        Add compliance requirements to the application
        
        Args:
            standards: List of compliance standards (e.g., ["SOC2", "HIPAA", "PCI-DSS"])
            
        Returns:
            Self for method chaining
        """
        
        # Store compliance requirements globally for the application
        self.compliance_requirements = standards
        
        # Apply compliance requirements to all existing services
        for service_name, service_config in self.services.items():
            service_config.requirements.compliance_requirements = standards
            
            # Update compliance sensitivity based on standards
            if standards:
                service_config.requirements.compliance_sensitivity = 1.0
            
        logger.info(f"📋 Added compliance requirements: {', '.join(standards)}")
        
        return self