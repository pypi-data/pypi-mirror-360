class CertificateManagerConfigurationMixin:
    """
    Mixin for CertificateManager chainable configuration methods.
    """
    def domain(self, domain_name: str):
        """Set the primary domain name"""
        self.domain_name = domain_name
        return self

    def alternative_names(self, names: list):
        """Add subject alternative names"""
        if not hasattr(self, 'subject_alternative_names'):
            self.subject_alternative_names = []
        self.subject_alternative_names.extend(names)
        return self

    def validation_method(self, method: str):
        """Set the validation method (DNS, EMAIL)"""
        self.validation_method = method.upper()
        return self

    def certificate_type(self, cert_type: str):
        """Set the certificate type (AMAZON_ISSUED, IMPORTED, PRIVATE)"""
        self.certificate_type = cert_type
        return self

    def key_algorithm(self, algorithm: str):
        """Set the key algorithm (RSA_2048, RSA_1024, RSA_4096, EC_prime256v1, EC_secp384r1)"""
        self.key_algorithm = algorithm
        return self

    def certificate_authority(self, ca_arn: str):
        """Set the certificate authority ARN for private certificates"""
        self.certificate_authority = ca_arn
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the certificate"""
        if not hasattr(self, 'tags'):
            self.tags = {}
        self.tags[key] = value
        return self
    
    def dns_validation(self):
        """Use DNS validation for domain ownership"""
        self.validation_method = "DNS"
        return self
    
    def email_validation(self):
        """Use email validation for domain ownership"""
        self.validation_method = "EMAIL"
        return self
    
    def auto_renew(self):
        """Enable automatic renewal"""
        # ACM automatically renews by default, this is for explicit intent
        self.auto_renewal_enabled = True
        return self
    
    def cloudfront_compatible(self):
        """Ensure certificate is valid for CloudFront (must be in us-east-1)"""
        self.cloudfront_region = "us-east-1"
        self.cloudfront_compatible_cert = True
        return self 