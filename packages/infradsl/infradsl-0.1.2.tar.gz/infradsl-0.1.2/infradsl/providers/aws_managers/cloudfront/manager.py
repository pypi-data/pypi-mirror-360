"""
AWS CloudFront Manager

Main coordinator for CloudFront operations. This manager orchestrates
different CloudFront components like distributions, origins, and behaviors.
"""

from typing import Dict, Any, List, Optional
from ..aws_client import AwsClient
from .distributions import CloudFrontDistributions
from .origins import CloudFrontOrigins
from .behaviors import CloudFrontBehaviors
from .configuration import CloudFrontConfiguration


class CloudFrontManager:
    """Main CloudFront manager that coordinates distribution operations"""

    def __init__(self, aws_client: Optional[AwsClient] = None):
        self.aws_client = aws_client or AwsClient()

        # Initialize component managers
        self.distributions = CloudFrontDistributions(self.aws_client)
        self.origins = CloudFrontOrigins(self.aws_client)
        self.behaviors = CloudFrontBehaviors(self.aws_client)
        self.configuration = CloudFrontConfiguration(self.aws_client)

    def _ensure_authenticated(self):
        """Ensure AWS authentication"""
        if not self.aws_client.is_authenticated:
            self.aws_client.authenticate(silent=True)

    # Distribution operations - delegate to distributions component
    def create_distribution(self, distribution_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a CloudFront distribution"""
        self._ensure_authenticated()
        return self.distributions.create(distribution_config)

    def update_distribution(self, distribution_id: str, distribution_config: Dict[str, Any], etag: str) -> Dict[str, Any]:
        """Update a CloudFront distribution"""
        self._ensure_authenticated()
        return self.distributions.update(distribution_id, distribution_config, etag)

    def delete_distribution(self, distribution_id: str) -> Dict[str, Any]:
        """Delete a CloudFront distribution"""
        self._ensure_authenticated()
        return self.distributions.delete(distribution_id)

    def list_distributions(self) -> List[Dict[str, Any]]:
        """List all CloudFront distributions"""
        self._ensure_authenticated()
        return self.distributions.list()

    def get_distribution(self, distribution_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific distribution"""
        self._ensure_authenticated()
        return self.distributions.get(distribution_id)

    def discover_existing_distributions(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing CloudFront distributions"""
        self._ensure_authenticated()
        return self.distributions.discover_existing()

    # Origin operations - delegate to origins component
    def build_origins(self, origins_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build origins configuration"""
        return self.origins.build_origins_config(origins_config)

    def build_origin_config(self, origin: Dict[str, Any]) -> Dict[str, Any]:
        """Build individual origin configuration"""
        return self.origins.build_single_origin_config(origin)

    # Behavior operations - delegate to behaviors component
    def build_default_cache_behavior(self, behavior_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build default cache behavior"""
        return self.behaviors.build_default_behavior(behavior_config)

    def build_cache_behaviors(self, behaviors_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build cache behaviors"""
        return self.behaviors.build_behaviors_list(behaviors_config)

    # Configuration operations - delegate to configuration component
    def build_distribution_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete CloudFront distribution configuration"""
        return self.configuration.build_complete_config(config)

    def build_viewer_certificate(self, ssl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build viewer certificate configuration"""
        return self.configuration.build_ssl_config(ssl_config)

    def build_logging_config(self, logging_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build logging configuration"""
        return self.configuration.build_logging_config(logging_config)

    def build_restrictions(self, geo_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build geo restrictions"""
        return self.configuration.build_geo_restrictions(geo_config)

    # Convenience methods for common workflows
    def create_static_site_distribution(
        self,
        name: str,
        origin_domain: str,
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """
        Create a CloudFront distribution optimized for static sites.

        Args:
            name: Distribution name
            origin_domain: S3 bucket or custom origin domain
            custom_domains: List of custom domain names
            ssl_certificate_arn: SSL certificate ARN for custom domains

        Returns:
            Distribution information
        """
        self._ensure_authenticated()

        print(f"🌐 Creating static site distribution: {name}")

        # Build optimized config for static sites
        config = self.configuration.build_static_site_config(
            name=name,
            origin_domain=origin_domain,
            custom_domains=custom_domains or [],
            ssl_certificate_arn=ssl_certificate_arn
        )

        return self.create_distribution(config)

    def create_api_distribution(
        self,
        name: str,
        api_domain: str,
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """
        Create a CloudFront distribution optimized for API acceleration.

        Args:
            name: Distribution name
            api_domain: API gateway or load balancer domain
            custom_domains: List of custom domain names
            ssl_certificate_arn: SSL certificate ARN for custom domains

        Returns:
            Distribution information
        """
        self._ensure_authenticated()

        print(f"🚀 Creating API acceleration distribution: {name}")

        # Build optimized config for APIs
        config = self.configuration.build_api_config(
            name=name,
            api_domain=api_domain,
            custom_domains=custom_domains or [],
            ssl_certificate_arn=ssl_certificate_arn
        )

        return self.create_distribution(config)

    def get_region(self) -> str:
        """Get current AWS region"""
        return self.aws_client.get_region()

    def get_account_id(self) -> str:
        """Get current AWS account ID"""
        return self.aws_client.get_account_id() 