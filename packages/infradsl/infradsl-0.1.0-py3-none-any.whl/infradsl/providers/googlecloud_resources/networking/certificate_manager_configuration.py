"""
GCP Certificate Manager Configuration Mixin

Chainable configuration methods for Google Cloud Certificate Manager.
Provides Rails-like method chaining for fluent SSL/TLS certificate configuration.
"""

from typing import Dict, Any, List, Optional, Union


class CertificateManagerConfigurationMixin:
    """
    Mixin for Certificate Manager configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Certificate type configuration (managed vs self-managed)
    - Domain configuration and validation
    - Scope and location settings
    - Common certificate patterns and use cases
    """
    
    def description(self, description: str):
        """Set certificate description"""
        self.certificate_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for Certificate Manager operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id:
            self.certificate_resource_name = f"projects/{self.project_id}/locations/{self.certificate_location}/certificates/{self.cert_name}"
        return self
        
    # Certificate type configuration
    def managed(self):
        """Use Google-managed certificate (automatic provisioning and renewal)"""
        self.managed_certificate = True
        self.renewal_enabled = True
        return self
        
    def self_managed(self, certificate_pem: str, private_key_pem: str):
        """Use self-managed certificate with provided PEM data"""
        self.managed_certificate = False
        self.certificate_pem = certificate_pem
        self.private_key_pem = private_key_pem
        self.renewal_enabled = False
        return self
        
    def from_file(self, cert_file_path: str, key_file_path: str):
        """Load self-managed certificate from files"""
        try:
            with open(cert_file_path, 'r') as cert_file:
                certificate_pem = cert_file.read()
            with open(key_file_path, 'r') as key_file:
                private_key_pem = key_file.read()
            return self.self_managed(certificate_pem, private_key_pem)
        except Exception as e:
            raise ValueError(f"Failed to read certificate files: {str(e)}")
            
    # Domain configuration
    def domains(self, domain_list: List[str]):
        """Set domain names for the certificate"""
        # Validate domains
        for domain in domain_list:
            if not self._is_valid_domain_name(domain):
                print(f"⚠️  Warning: Invalid domain name '{domain}'")
        self.domain_names = domain_list
        return self
        
    def domain(self, domain_name: str):
        """Add a single domain name"""
        if not self._is_valid_domain_name(domain_name):
            print(f"⚠️  Warning: Invalid domain name '{domain_name}'")
        if domain_name not in self.domain_names:
            self.domain_names.append(domain_name)
        return self
        
    def add_domain(self, domain_name: str):
        """Add a single domain name - alias for domain()"""
        return self.domain(domain_name)
        
    def wildcard_domain(self, base_domain: str):
        """Add wildcard domain (*.example.com)"""
        wildcard = f"*.{base_domain}"
        return self.domain(wildcard).domain(base_domain)  # Include apex domain too
        
    # Location and scope configuration
    def location(self, location: str):
        """Set certificate location"""
        if not self._is_valid_location(location):
            print(f"⚠️  Warning: Invalid location '{location}'. Use 'global' or valid GCP regions.")
        self.certificate_location = location
        # Update resource name if project is set
        if hasattr(self, 'project_id') and self.project_id:
            self.certificate_resource_name = f"projects/{self.project_id}/locations/{self.certificate_location}/certificates/{self.cert_name}"
        return self
        
    def global_scope(self):
        """Set global scope (for global load balancers)"""
        self.certificate_location = "global"
        self.certificate_scope = "DEFAULT"
        return self
        
    def regional(self, region: str):
        """Set regional scope"""
        return self.location(region)
        
    def edge_cache(self):
        """Set edge cache scope (for Cloud CDN)"""
        self.certificate_scope = "EDGE_CACHE"
        return self
        
    def default_scope(self):
        """Set default scope"""
        self.certificate_scope = "DEFAULT"
        return self
        
    # Validation configuration
    def dns_validation(self):
        """Use DNS validation method"""
        self.validation_method = "DNS"
        return self
        
    def http_validation(self):
        """Use HTTP validation method"""
        self.validation_method = "HTTP"
        return self
        
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to the certificate"""
        self.certificate_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.certificate_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add annotations to the certificate"""
        self.certificate_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.certificate_annotations[key] = value
        return self
        
    # Common certificate patterns
    def single_domain_cert(self, domain_name: str):
        """Rails convenience: Single domain certificate"""
        return (self.domain(domain_name)
                .managed()
                .global_scope()
                .label("type", "single_domain"))
        
    def wildcard_cert(self, domain_name: str):
        """Rails convenience: Wildcard certificate (*.domain.com + domain.com)"""
        return (self.wildcard_domain(domain_name)
                .managed()
                .global_scope()
                .label("type", "wildcard"))
        
    def webapp_cert(self, domain_name: str):
        """Rails convenience: Web app certificate (www + apex)"""
        domains = [domain_name]
        if not domain_name.startswith("www."):
            domains.append(f"www.{domain_name}")
        return (self.domains(domains)
                .managed()
                .global_scope()
                .label("type", "webapp")
                .label("purpose", "website"))
        
    def api_cert(self, domain_name: str):
        """Rails convenience: API certificate"""
        api_domain = domain_name if domain_name.startswith("api.") else f"api.{domain_name}"
        return (self.domain(api_domain)
                .managed()
                .global_scope()
                .label("type", "api")
                .label("purpose", "api"))
        
    def multi_domain_cert(self, domain_list: List[str]):
        """Rails convenience: Multi-domain certificate"""
        return (self.domains(domain_list)
                .managed()
                .global_scope()
                .label("type", "multi_domain"))
        
    def complete_website_cert(self, domain_name: str):
        """Rails convenience: Complete website certificate (all subdomains)"""
        domains = [
            domain_name,
            f"www.{domain_name}",
            f"api.{domain_name}",
            f"cdn.{domain_name}",
            f"admin.{domain_name}"
        ]
        return (self.domains(domains)
                .managed()
                .global_scope()
                .label("type", "complete_website")
                .label("purpose", "full_stack"))
        
    def microservices_cert(self, base_domain: str, services: List[str]):
        """Rails convenience: Microservices certificate"""
        domains = [base_domain]
        for service in services:
            domains.append(f"{service}.{base_domain}")
        return (self.domains(domains)
                .managed()
                .global_scope()
                .label("type", "microservices")
                .label("purpose", "api_gateway"))
        
    def saas_cert(self, base_domain: str):
        """Rails convenience: SaaS application certificate"""
        domains = [
            base_domain,
            f"www.{base_domain}",
            f"app.{base_domain}",
            f"api.{base_domain}",
            f"admin.{base_domain}",
            f"docs.{base_domain}"
        ]
        return (self.domains(domains)
                .managed()
                .global_scope()
                .label("type", "saas")
                .label("purpose", "saas_platform"))
        
    # Load balancer specific patterns
    def load_balancer_cert(self, domain_list: List[str]):
        """Rails convenience: Load balancer certificate"""
        return (self.domains(domain_list)
                .managed()
                .global_scope()
                .label("type", "load_balancer")
                .label("purpose", "load_balancing"))
        
    def cdn_cert(self, domain_name: str):
        """Rails convenience: CDN certificate"""
        cdn_domain = domain_name if domain_name.startswith("cdn.") else f"cdn.{domain_name}"
        return (self.domain(cdn_domain)
                .managed()
                .edge_cache()
                .label("type", "cdn")
                .label("purpose", "content_delivery"))
        
    def global_lb_cert(self, domain_list: List[str]):
        """Rails convenience: Global Load Balancer certificate"""
        return (self.domains(domain_list)
                .managed()
                .global_scope()
                .label("type", "global_lb")
                .label("purpose", "global_load_balancing"))
        
    def regional_lb_cert(self, region: str, domain_list: List[str]):
        """Rails convenience: Regional Load Balancer certificate"""
        return (self.domains(domain_list)
                .managed()
                .location(region)
                .label("type", "regional_lb")
                .label("purpose", "regional_load_balancing")
                .label("region", region))
        
    # Environment-specific configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.label("environment", "development")
                .label("auto_cleanup", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.label("environment", "production")
                .label("monitoring", "enabled")
                .label("backup", "enabled"))
        
    # Security and compliance patterns
    def high_security(self):
        """Configure for high security requirements"""
        return (self.label("security", "high")
                .label("compliance", "required")
                .label("monitoring", "enhanced"))
        
    def compliance_ready(self):
        """Configure for compliance requirements"""
        return (self.label("compliance", "sox_pci")
                .label("audit", "required")
                .label("encryption", "required"))
        
    def enterprise_grade(self):
        """Configure for enterprise requirements"""
        return (self.production()
                .high_security()
                .compliance_ready()
                .label("tier", "enterprise"))
        
    # Industry-specific patterns
    def ecommerce_cert(self, domain_name: str):
        """Rails convenience: E-commerce certificate"""
        domains = [
            domain_name,
            f"www.{domain_name}",
            f"shop.{domain_name}",
            f"checkout.{domain_name}",
            f"api.{domain_name}"
        ]
        return (self.domains(domains)
                .managed()
                .global_scope()
                .compliance_ready()
                .label("type", "ecommerce")
                .label("industry", "retail"))
        
    def fintech_cert(self, domain_name: str):
        """Rails convenience: Fintech application certificate"""
        domains = [
            domain_name,
            f"app.{domain_name}",
            f"api.{domain_name}",
            f"secure.{domain_name}"
        ]
        return (self.domains(domains)
                .managed()
                .global_scope()
                .enterprise_grade()
                .label("type", "fintech")
                .label("industry", "financial"))
        
    def healthcare_cert(self, domain_name: str):
        """Rails convenience: Healthcare application certificate"""
        domains = [
            domain_name,
            f"portal.{domain_name}",
            f"api.{domain_name}",
            f"secure.{domain_name}"
        ]
        return (self.domains(domains)
                .managed()
                .global_scope()
                .enterprise_grade()
                .label("type", "healthcare")
                .label("industry", "healthcare")
                .label("hipaa", "compliant"))
        
    # Custom validation patterns
    def quick_validation(self):
        """Configure for quick validation (development)"""
        return (self.dns_validation()
                .label("validation", "quick")
                .development())
        
    def secure_validation(self):
        """Configure for secure validation (production)"""
        return (self.dns_validation()
                .label("validation", "secure")
                .production())
        
    # Utility methods
    def clear_domains(self):
        """Clear all domain names"""
        self.domain_names = []
        return self
        
    def get_domain_count(self) -> int:
        """Get the number of configured domains"""
        return len(self.domain_names)
        
    def has_wildcard(self) -> bool:
        """Check if any domain is a wildcard"""
        return any(domain.startswith("*.") for domain in self.domain_names)
        
    def get_certificate_type(self) -> str:
        """Get the certificate type based on configuration"""
        return self._get_certificate_type_from_config()