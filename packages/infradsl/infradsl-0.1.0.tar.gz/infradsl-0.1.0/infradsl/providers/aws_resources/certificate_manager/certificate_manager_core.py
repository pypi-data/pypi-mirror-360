from ..base_resource import BaseAwsResource

class CertificateManagerCore(BaseAwsResource):
    """
    Core CertificateManager class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.certificate_arn = None
        self.domain_name = None
        self.subject_alternative_names = []
        self.validation_method = None
        self.certificate_type = None
        self.key_algorithm = None
        self.certificate_authority = None
        self.validation_domain = None
        self.validation_records = []
        self.status = None
        self.issued_date = None
        self.expiration_date = None
        self.tags = {}
        self.certificate_exists = False
        self.certificate_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        # Certificate manager will be initialized after authentication
        self.certificate_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize ACM client
        self.acm_client = self.get_acm_client()
    
    def get_acm_client(self, region: str = None):
        """Get ACM client for this resource"""
        return self.get_client('acm', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region)
    
    def create(self):
        """Create/update certificate - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .certificate_manager_lifecycle import CertificateManagerLifecycleMixin
        # Call the lifecycle mixin's create method
        return CertificateManagerLifecycleMixin.create(self)

    def destroy(self):
        """Destroy certificate - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .certificate_manager_lifecycle import CertificateManagerLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return CertificateManagerLifecycleMixin.destroy(self)

    def preview(self):
        """Preview certificate configuration"""
        return {
            "resource_type": "AWS Certificate Manager",
            "domain_name": self.domain_name or self.name,
            "subject_alternative_names": self.subject_alternative_names,
            "validation_method": self.validation_method or "DNS",
            "certificate_type": self.certificate_type or "AMAZON_ISSUED",
            "key_algorithm": self.key_algorithm or "RSA_2048",
            "tags_count": len(self.tags),
            "estimated_monthly_cost": self._estimate_monthly_cost()
        }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for certificate"""
        # ACM certificates are free for use with AWS services
        # Only private certificates have costs
        if self.certificate_type == 'PRIVATE':
            # Private CA costs ~$400/month + $0.75 per certificate
            return "$0.75"
        else:
            return "$0.00" 