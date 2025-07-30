"""
AWS Certificate Manager Complete Implementation

Combines all Certificate Manager functionality through multiple inheritance:
- CertificateManagerCore: Core attributes and authentication
- CertificateManagerConfigurationMixin: Chainable configuration methods  
- CertificateManagerLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .certificate_manager_core import CertificateManagerCore
from .certificate_manager_configuration import CertificateManagerConfigurationMixin
from .certificate_manager_lifecycle import CertificateManagerLifecycleMixin


class CertificateManager(CertificateManagerLifecycleMixin, CertificateManagerConfigurationMixin, CertificateManagerCore):
    """
    Complete AWS Certificate Manager implementation for SSL/TLS certificate management.
    
    This class combines:
    - SSL/TLS certificate provisioning and management
    - Domain validation (DNS or Email)
    - Certificate renewal automation
    - Integration with Load Balancers and CloudFront
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize Certificate Manager instance"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.00/month"  # ACM certificates are free
        
        # Initialize configuration attributes to avoid conflicts
        self.cert_domain_name = None
        self.cert_validation_method = 'DNS'  # Default to DNS validation
        self.cert_type = 'AMAZON_ISSUED'  # Default to Amazon-issued
        self.cert_key_algorithm = 'RSA_2048'  # Default algorithm
        self.cert_alternative_names = []
        self.cert_validation_domain = None
        self.cert_tags = {}
        
        # Certificate status tracking
        self._renewal_eligible = False
        self._in_use_by = []  # Resources using this certificate
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
    
    def validate_configuration(self):
        """Validate the current Certificate Manager configuration"""
        errors = []
        warnings = []
        
        # Validate domain name
        if not self.cert_domain_name and not self.name:
            errors.append("Domain name is required")
        
        domain = self.cert_domain_name or self.name
        if domain and not self._is_valid_domain(domain):
            errors.append("Invalid domain name format")
        
        # Validate certificate type
        valid_types = ['AMAZON_ISSUED', 'IMPORTED', 'PRIVATE']
        if self.cert_type not in valid_types:
            errors.append(f"Invalid certificate type: {self.cert_type}")
        
        # Validate validation method
        if self.cert_type == 'AMAZON_ISSUED':
            valid_methods = ['DNS', 'EMAIL']
            if self.cert_validation_method not in valid_methods:
                errors.append(f"Invalid validation method: {self.cert_validation_method}")
        
        # Validate key algorithm
        valid_algorithms = ['RSA_2048', 'RSA_1024', 'RSA_4096', 'EC_prime256v1', 'EC_secp384r1', 'EC_secp521r1']
        if self.cert_key_algorithm not in valid_algorithms:
            errors.append(f"Invalid key algorithm: {self.cert_key_algorithm}")
        
        # Validate alternative names
        for alt_name in self.cert_alternative_names:
            if not self._is_valid_domain(alt_name):
                errors.append(f"Invalid alternative name: {alt_name}")
        
        # Private certificate validation
        if self.cert_type == 'PRIVATE' and not self.certificate_authority:
            errors.append("Private certificates require a certificate authority ARN")
        
        # Warnings
        if self.cert_validation_method == 'EMAIL':
            warnings.append("Email validation requires manual approval steps")
        
        if len(self.cert_alternative_names) > 10:
            warnings.append("Large number of alternative names may slow certificate issuance")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_certificate_info(self):
        """Get complete information about the certificate"""
        return {
            'certificate_arn': self.certificate_arn,
            'domain_name': self.cert_domain_name or self.name,
            'alternative_names': self.cert_alternative_names,
            'validation_method': self.cert_validation_method,
            'certificate_type': self.cert_type,
            'key_algorithm': self.cert_key_algorithm,
            'status': self.status,
            'issued_date': self.issued_date,
            'expiration_date': self.expiration_date,
            'renewal_eligible': self._renewal_eligible,
            'in_use_by': self._in_use_by,
            'tags_count': len(self.tags),
            'certificate_exists': self.certificate_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority
        }
    
    def clone(self, new_domain: str):
        """Create a copy of this certificate with a new domain"""
        cloned_cert = CertificateManager(new_domain)
        cloned_cert.cert_domain_name = new_domain
        cloned_cert.cert_validation_method = self.cert_validation_method
        cloned_cert.cert_type = self.cert_type
        cloned_cert.cert_key_algorithm = self.cert_key_algorithm
        cloned_cert.cert_alternative_names = self.cert_alternative_names.copy()
        cloned_cert.cert_validation_domain = self.cert_validation_domain
        cloned_cert.certificate_authority = self.certificate_authority
        cloned_cert.tags = self.tags.copy()
        return cloned_cert
    
    def export_configuration(self):
        """Export certificate configuration for backup or migration"""
        return {
            'metadata': {
                'domain_name': self.cert_domain_name or self.name,
                'certificate_type': self.cert_type,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'validation_method': self.cert_validation_method,
                'key_algorithm': self.cert_key_algorithm,
                'alternative_names': self.cert_alternative_names,
                'certificate_authority': self.certificate_authority,
                'validation_domain': self.cert_validation_domain,
                'optimization_priority': self._optimization_priority
            },
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import certificate configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.cert_validation_method = config.get('validation_method', 'DNS')
            self.cert_key_algorithm = config.get('key_algorithm', 'RSA_2048')
            self.cert_alternative_names = config.get('alternative_names', [])
            self.certificate_authority = config.get('certificate_authority')
            self.cert_validation_domain = config.get('validation_domain')
            self._optimization_priority = config.get('optimization_priority')
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain name format"""
        import re
        
        # Basic domain validation regex
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9]'  # First character must be alphanumeric
            r'(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)'  # Subdomain
            r'*[a-zA-Z0-9]'  # Last character must be alphanumeric
            r'(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'  # Domain
        )
        
        # Allow wildcards for certificate domains
        if domain.startswith('*.'):
            domain = domain[2:]
        
        return bool(domain_regex.match(domain))
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing Certificate Manager for {priority}")
        
        # Apply AWS Certificate Manager-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Using AWS-issued certificates (free)")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring for fast validation")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring for high availability")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring for security compliance")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS Certificate Manager-specific cost optimizations"""
        # Use Amazon-issued certificates (free)
        if self.cert_type != 'AMAZON_ISSUED':
            print("   💰 Switching to Amazon-issued certificates for zero cost")
            self.cert_type = 'AMAZON_ISSUED'
        
        # Use DNS validation for automation
        if self.cert_validation_method != 'DNS':
            print("   💰 Using DNS validation for automated renewal")
            self.cert_validation_method = 'DNS'
        
        # Add cost optimization tags
        self.tags.update({
            "cost-optimized": "true",
            "certificate-type": "amazon-issued"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS Certificate Manager-specific performance optimizations"""
        # Use DNS validation for faster issuance
        if self.cert_validation_method != 'DNS':
            print("   ⚡ Using DNS validation for faster certificate issuance")
            self.cert_validation_method = 'DNS'
        
        # Use modern key algorithms
        if self.cert_key_algorithm == 'RSA_1024':
            print("   ⚡ Upgrading to RSA_2048 for better performance/security balance")
            self.cert_key_algorithm = 'RSA_2048'
        
        # Add performance tags
        self.tags.update({
            "performance-optimized": "true",
            "validation-method": "dns"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS Certificate Manager-specific reliability optimizations"""
        # Use stronger key algorithms
        if self.cert_key_algorithm in ['RSA_1024', 'RSA_2048']:
            print("   🛡️ Upgrading to RSA_4096 for enhanced security")
            self.cert_key_algorithm = 'RSA_4096'
        
        # Enable monitoring
        print("   🛡️ Enable CloudWatch monitoring for certificate expiration")
        
        # Add reliability tags
        self.tags.update({
            "reliability-optimized": "true",
            "key-strength": "high",
            "monitoring-enabled": "true"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS Certificate Manager-specific compliance optimizations"""
        # Use strongest key algorithms for compliance
        if self.cert_key_algorithm not in ['RSA_4096', 'EC_secp384r1', 'EC_secp521r1']:
            print("   📋 Upgrading to RSA_4096 for compliance requirements")
            self.cert_key_algorithm = 'RSA_4096'
        
        # Add compliance tags
        self.tags.update({
            "compliance-optimized": "true",
            "encryption-strength": "high",
            "audit-enabled": "true"
        })
    
    # Convenience methods with non-conflicting names
    def domain(self, domain_name: str):
        """Set the primary domain name"""
        self.cert_domain_name = domain_name
        return self
    
    def add_alternative_names(self, *names: str):
        """Add subject alternative names"""
        self.cert_alternative_names.extend(names)
        return self
    
    def validation(self, method: str):
        """Set the validation method (DNS, EMAIL)"""
        self.cert_validation_method = method.upper()
        return self
    
    def dns_validation(self):
        """Use DNS validation (recommended)"""
        self.cert_validation_method = 'DNS'
        return self
    
    def email_validation(self):
        """Use email validation"""
        self.cert_validation_method = 'EMAIL'
        return self
    
    def certificate_type(self, cert_type: str):
        """Set the certificate type"""
        self.cert_type = cert_type
        return self
    
    def amazon_issued(self):
        """Use Amazon-issued certificate (default)"""
        self.cert_type = 'AMAZON_ISSUED'
        return self
    
    def imported(self):
        """Import existing certificate"""
        self.cert_type = 'IMPORTED'
        return self
    
    def private_ca(self, ca_arn: str):
        """Use private certificate authority"""
        self.cert_type = 'PRIVATE'
        self.certificate_authority = ca_arn
        return self
    
    def key_algorithm(self, algorithm: str):
        """Set the key algorithm"""
        self.cert_key_algorithm = algorithm
        return self
    
    def wildcard(self):
        """Make this a wildcard certificate"""
        if self.cert_domain_name and not self.cert_domain_name.startswith('*.'):
            self.cert_domain_name = f'*.{self.cert_domain_name}'
        return self
    
    def for_load_balancer(self, lb_name: str):
        """Mark certificate as being used by a load balancer"""
        self._in_use_by.append(f'LoadBalancer:{lb_name}')
        return self
    
    def for_cloudfront(self, distribution_id: str):
        """Mark certificate as being used by CloudFront"""
        self._in_use_by.append(f'CloudFront:{distribution_id}')
        return self
    
    def tag(self, key: str, value: str):
        """Add a tag to the certificate"""
        self.tags[key] = value
        return self


# Convenience functions for creating Certificate Manager instances
def create_certificate(domain: str, validation: str = 'DNS') -> CertificateManager:
    """Create a new certificate with basic configuration"""
    cert = CertificateManager(domain)
    cert.domain(domain).validation(validation)
    return cert

def create_wildcard_certificate(domain: str) -> CertificateManager:
    """Create a wildcard certificate for a domain"""
    cert = CertificateManager(domain)
    cert.domain(f'*.{domain}').dns_validation()
    cert.add_alternative_names(domain)  # Include base domain
    return cert

def create_multi_domain_certificate(primary_domain: str, alternative_domains: list) -> CertificateManager:
    """Create a certificate with multiple domains"""
    cert = CertificateManager(primary_domain)
    cert.domain(primary_domain).dns_validation()
    cert.add_alternative_names(*alternative_domains)
    return cert

def create_private_certificate(domain: str, ca_arn: str) -> CertificateManager:
    """Create a private certificate using AWS Private CA"""
    cert = CertificateManager(domain)
    cert.domain(domain).private_ca(ca_arn)
    return cert