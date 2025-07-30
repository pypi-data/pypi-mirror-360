class CertificateManagerLifecycleMixin:
    """
    Mixin for CertificateManager lifecycle operations (create, update, destroy).
    """
    def create(self):
        """Create/update certificate and remove any that are no longer needed"""
        self._ensure_authenticated()
        
        print(f"🔐 Creating/updating certificate for domain: {self.cert_domain_name or self.domain_name or self.name}")
        
        # In a real implementation, this would:
        # 1. Request certificate from ACM
        # 2. Handle validation (DNS or Email)
        # 3. Wait for validation to complete
        # 4. Return certificate ARN
        
        # Mock implementation
        domain = self.cert_domain_name or self.domain_name or self.name
        self.certificate_arn = f"arn:aws:acm:us-east-1:123456789012:certificate/{domain.replace('.', '-')}-12345"
        self.status = "ISSUED"
        self.certificate_exists = True
        
        # Mock validation records for DNS validation
        if self.cert_validation_method == 'DNS':
            self.validation_records = [{
                'name': f'_acme-challenge.{domain}',
                'type': 'CNAME',
                'value': f'{domain}.acm-validations.aws.'
            }]
            print(f"   📝 DNS validation required - Add CNAME record:")
            print(f"      Name: {self.validation_records[0]['name']}")
            print(f"      Value: {self.validation_records[0]['value']}")
        
        print(f"✅ Certificate created successfully!")
        print(f"   ARN: {self.certificate_arn}")
        print(f"   Status: {self.status}")
        
        return {
            'certificate_arn': self.certificate_arn,
            'domain_name': domain,
            'status': self.status,
            'validation_method': self.cert_validation_method or self.validation_method,
            'validation_records': self.validation_records
        }

    def destroy(self):
        """Destroy the certificate"""
        self._ensure_authenticated()
        
        if not self.certificate_exists:
            print("⚠️  No certificate to destroy")
            return {'destroyed': False, 'reason': 'Certificate does not exist'}
        
        print(f"🗑️  Destroying certificate: {self.certificate_arn}")
        
        # Check if certificate is in use
        if hasattr(self, '_in_use_by') and self._in_use_by:
            print(f"⚠️  Warning: Certificate is in use by: {', '.join(self._in_use_by)}")
            print("   Remove certificate from these resources before deletion")
        
        # Mock deletion
        self.certificate_exists = False
        self.status = "DELETED"
        
        print("✅ Certificate destroyed successfully")
        
        return {
            'destroyed': True,
            'certificate_arn': self.certificate_arn,
            'domain_name': self.cert_domain_name or self.domain_name or self.name
        }
    
    def _display_preview(self, to_create, to_keep, to_remove):
        """Display preview of changes"""
        print("\n📋 Certificate Manager Preview:")
        print("=" * 50)
        
        if to_create:
            print("✨ To Create:")
            for cert in to_create:
                print(f"   - {cert['domain']} ({cert['type']})")
        
        if to_keep:
            print("✅ To Keep:")
            for cert in to_keep:
                print(f"   - {cert['domain']} (No changes)")
        
        if to_remove:
            print("🗑️  To Remove:")
            for cert in to_remove:
                print(f"   - {cert['domain']}")
        
        print("=" * 50) 