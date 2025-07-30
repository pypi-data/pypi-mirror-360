"""
Resource Creation Methods for IntelligentApplication

Methods for creating provider-specific resources based on Cross-Cloud Magic
optimization results.
"""

from typing import TYPE_CHECKING, Dict, Any

from .data_classes import ServiceConfiguration

if TYPE_CHECKING:
    from .core import IntelligentApplication

try:
    from ...providers.aws import AWS
    from ...providers.googlecloud import GoogleCloud
    from ...providers.digitalocean import DigitalOcean
    from ...providers.cloudflare import Cloudflare
except ImportError:
    # Fallback for cases where providers aren't available
    AWS = None
    GoogleCloud = None
    DigitalOcean = None
    Cloudflare = None


class ResourceCreationMixin:
    """Mixin providing resource creation methods"""
    
    def _create_resource_with_provider(self: 'IntelligentApplication', 
                                     provider: str, 
                                     service_config: ServiceConfiguration,
                                     recommendation) -> Any:
        """Create resource with the optimal provider"""
        
        service_type = service_config.service_type
        config = service_config.configuration
        service_name = service_config.service_name
        
        # Map service types to provider-specific resources
        if provider == "aws":
            return self._create_aws_resource(service_type, service_name, config)
        elif provider == "gcp":
            return self._create_gcp_resource(service_type, service_name, config)
        elif provider == "digitalocean":
            return self._create_digitalocean_resource(service_type, service_name, config)
        elif provider == "cloudflare":
            return self._create_cloudflare_resource(service_type, service_name, config)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _create_aws_resource(self: 'IntelligentApplication', service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create AWS resource based on service type"""
        
        if AWS is None:
            return f"AWS {service_type} resource: {service_name} (mock - AWS provider not available)"
        
        if service_type == "postgresql":
            return (AWS.RDS(service_name)
                   .postgres()
                   .instance_class(config.get('instance_class', 'db.t3.micro'))
                   .storage(config.get('storage', 20))
                   .backup_retention(config.get('backup_retention', 7))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "web-servers":
            return (AWS.EC2(service_name)
                   .t3_medium()
                   .auto_scale(
                       min_size=config.get('min_size', 2),
                       max_size=config.get('max_size', 10)
                   )
                   .load_balancer()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "user-uploads":
            return (AWS.S3(service_name)
                   .private()
                   .versioning()
                   .backup()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "static-assets":
            return (AWS.CloudFront(service_name)
                   .price_class("PriceClass_100")
                   .cache_behavior("optimized")
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (AWS.Lambda(service_name)
                   .python()
                   .memory(config.get('memory', 512))
                   .timeout(config.get('timeout', 30))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (AWS.ECS(service_name)
                   .fargate()
                   .cpu(config.get('cpu', 512))
                   .memory(config.get('memory', 1024))
                   .auto_scale(
                       min_size=config.get('min_size', 1),
                       max_size=config.get('max_size', 10)
                   )
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # AWS CloudWatch + X-Ray monitoring
            return f"AWS CloudWatch monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return f"AWS EKS cluster for {service_name}"
        
        elif service_type == "load-balancer":
            return (AWS.LoadBalancer(service_name)
                   .application()
                   .health_checks()
                   .ssl_termination()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported AWS service type: {service_type}")
    
    def _create_gcp_resource(self: 'IntelligentApplication', service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create GCP resource based on service type"""
        
        if GoogleCloud is None:
            return f"GCP {service_type} resource: {service_name} (mock - GCP provider not available)"
        
        if service_type == "postgresql":
            return (GoogleCloud.CloudSQL(service_name)
                   .postgres()
                   .tier(config.get('tier', 'db-f1-micro'))
                   .storage_size(config.get('storage', 20))
                   .backup_enabled()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "web-servers":
            return (GoogleCloud.Vm(service_name)
                   .machine_type(config.get('machine_type', 'e2-medium'))
                   .disk_size(config.get('disk_size', 20))
                   .auto_scaling(
                       min_replicas=config.get('min_size', 2),
                       max_replicas=config.get('max_size', 10)
                   )
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "user-uploads":
            return (GoogleCloud.Storage(service_name)
                   .private()
                   .versioning()
                   .backup()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "static-assets":
            return (GoogleCloud.CloudCDN(service_name)
                   .cache_mode("CACHE_ALL_STATIC")
                   .compression()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (GoogleCloud.CloudFunctions(service_name)
                   .python()
                   .memory(config.get('memory', '512MB'))
                   .timeout(config.get('timeout', 60))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (GoogleCloud.CloudRun(service_name)
                   .cpu(config.get('cpu', 1))
                   .memory(config.get('memory', '1Gi'))
                   .min_instances(config.get('min_size', 0))
                   .max_instances(config.get('max_size', 10))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # GCP Cloud Monitoring + Logging
            return f"GCP Cloud Monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return (GoogleCloud.GKE(service_name)
                   .autopilot()
                   .region(config.get('region', 'us-central1'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "load-balancer":
            return (GoogleCloud.LoadBalancer(service_name)
                   .global_load_balancer()
                   .health_checks()
                   .ssl_certificates()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported GCP service type: {service_type}")
    
    def _create_digitalocean_resource(self: 'IntelligentApplication', service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create DigitalOcean resource based on service type"""
        
        if DigitalOcean is None:
            return f"DigitalOcean {service_type} resource: {service_name} (mock - DigitalOcean provider not available)"
        
        if service_type == "web-servers":
            return (DigitalOcean.Droplet(service_name)
                   .size(config.get('size', 's-2vcpu-2gb'))
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "user-uploads":
            return (DigitalOcean.Space(service_name)
                   .region(config.get('region', 'nyc3'))
                   .cdn_enabled(config.get('cdn', True))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "postgresql":
            return (DigitalOcean.Database(service_name)
                   .postgres()
                   .size(config.get('size', 'db-s-1vcpu-1gb'))
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (DigitalOcean.Function(service_name)
                   .python()
                   .memory(config.get('memory', 512))
                   .timeout(config.get('timeout', 30))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (DigitalOcean.AppPlatform(service_name)
                   .container()
                   .size(config.get('size', 'basic'))
                   .auto_deploy()
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # DigitalOcean basic monitoring
            return f"DigitalOcean monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return (DigitalOcean.Kubernetes(service_name)
                   .node_pool(
                       size=config.get('node_size', 's-2vcpu-2gb'),
                       count=config.get('node_count', 3)
                   )
                   .region(config.get('region', 'nyc1'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "load-balancer":
            return (DigitalOcean.LoadBalancer(service_name)
                   .health_checks()
                   .sticky_sessions()
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported DigitalOcean service type: {service_type}")
    
    def _create_cloudflare_resource(self: 'IntelligentApplication', service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create Cloudflare resource based on service type"""
        
        if Cloudflare is None:
            return f"Cloudflare {service_type} resource: {service_name} (mock - Cloudflare provider not available)"
        
        if service_type == "static-assets":
            domain = config.get('domain', f"{self.name}.example.com")
            return (Cloudflare.DNS(domain)
                   .cdn_enabled()
                   .ssl_full()
                   .firewall("strict")
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "dns":
            domain = config.get('domain', f"{self.name}.example.com")
            return (Cloudflare.DNS(domain)
                   .proxy_enabled()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (Cloudflare.Worker(service_name)
                   .script(config.get('script', 'worker.js'))
                   .route(config.get('route', f"api.{self.name}.com/*"))
                   .kv_namespace(config.get('kv_namespace'))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "load-balancer":
            return (Cloudflare.LoadBalancer(service_name)
                   .geo_routing()
                   .health_checks()
                   .failover_pools()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported Cloudflare service type: {service_type}")