"""
Google Cloud Certificate Manager Resource

Rails-like SSL/TLS certificate management with automatic provisioning and renewal.
Supports Google-managed certificates and self-managed certificates.
"""

import json
import time
from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class CertificateManager(BaseGcpResource):
    """Google Cloud Certificate Manager Resource with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        
        # Core configuration
        self.cert_name = name
        self.domain_names = []
        self.managed_certificate = True  # True for Google-managed, False for self-managed
        self.description = f"Certificate: {name}"
        
        # Self-managed certificate data
        self.certificate_pem = None
        self.private_key_pem = None
        
        # Scope and location
        self.location = "global"  # global or regional
        self.scope = "DEFAULT"    # DEFAULT or EDGE_CACHE
        
        # Labels
        self.cert_labels = {}
        
        # State
        self.certificate_resource_name = None
        self.certificate_status = None
        self.certificate_id = None

        # Client
        self.cert_manager_client = None

    def _initialize_managers(self):
        self.cert_manager_client = None

    def _post_authentication_setup(self):
        self.cert_manager_client = self.get_cert_manager_client()
        
        # Set resource name
        project_id = self.gcp_client.project
        self.certificate_resource_name = f"projects/{project_id}/locations/{self.location}/certificates/{self.cert_name}"

    def _discover_existing_certificates(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing SSL/TLS certificates"""
        existing_certificates = {}
        
        try:
            from google.cloud import certificatemanager_v1
            from google.api_core.exceptions import GoogleAPIError
            
            parent = f"projects/{self.gcp_client.project}/locations/{self.location}"
            
            # List all certificates in the location
            request = certificatemanager_v1.ListCertificatesRequest(parent=parent)
            page_result = self.cert_manager_client.list_certificates(request=request)
            
            for certificate in page_result:
                cert_name = certificate.name.split('/')[-1]
                
                # Extract certificate details
                cert_type = "unknown"
                domains = []
                status = "unknown"
                expiry_time = None
                
                # Check if managed or self-managed
                if hasattr(certificate, 'managed') and certificate.managed:
                    cert_type = "google_managed"
                    domains = list(certificate.managed.domains) if certificate.managed.domains else []
                    
                    # Get provisioning status
                    if hasattr(certificate.managed, 'state'):
                        status = str(certificate.managed.state).replace('State.', '').lower()
                    
                    # Check for provisioning issues
                    provisioning_issues = []
                    if hasattr(certificate.managed, 'provisioning_issue') and certificate.managed.provisioning_issue:
                        issue = certificate.managed.provisioning_issue
                        provisioning_issues.append({
                            'type': str(issue.type_),
                            'details': issue.details
                        })
                
                elif hasattr(certificate, 'self_managed') and certificate.self_managed:
                    cert_type = "self_managed"
                    status = "active"
                    
                    # Try to extract domain from certificate if available
                    if hasattr(certificate.self_managed, 'pem_certificate'):
                        # In a real implementation, you'd parse the certificate
                        # to extract the subject alternative names (domains)
                        pass
                
                # Get certificate metadata
                create_time = None
                update_time = None
                if hasattr(certificate, 'create_time'):
                    create_time = certificate.create_time.strftime('%Y-%m-%d %H:%M:%S UTC') if certificate.create_time else None
                if hasattr(certificate, 'update_time'):
                    update_time = certificate.update_time.strftime('%Y-%m-%d %H:%M:%S UTC') if certificate.update_time else None
                
                # Get labels
                labels = dict(certificate.labels) if certificate.labels else {}
                
                existing_certificates[cert_name] = {
                    'cert_name': cert_name,
                    'full_name': certificate.name,
                    'cert_type': cert_type,
                    'domains': domains,
                    'domain_count': len(domains),
                    'status': status,
                    'description': certificate.description or '',
                    'location': self.location,
                    'scope': str(certificate.scope).replace('Scope.', '') if certificate.scope else 'DEFAULT',
                    'labels': labels,
                    'label_count': len(labels),
                    'create_time': create_time,
                    'update_time': update_time,
                    'expiry_time': expiry_time,
                    'auto_renewal': cert_type == "google_managed",
                    'provisioning_issues': provisioning_issues if 'provisioning_issues' in locals() else []
                }
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing certificates: {str(e)}")
        
        return existing_certificates

    def get_cert_manager_client(self):
        try:
            from google.cloud import certificatemanager_v1
            return certificatemanager_v1.CertificateManagerClient(credentials=self.gcp_client.credentials)
        except Exception as e:
            print(f"⚠️  Failed to create Certificate Manager client: {e}")
            return None

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing certificates
        existing_certificates = self._discover_existing_certificates()
        
        # Categorize certificates
        certs_to_create = []
        certs_to_keep = []
        certs_to_remove = []
        
        # Check if our desired certificate exists
        desired_cert_name = self.cert_name
        cert_exists = desired_cert_name in existing_certificates
        
        if not cert_exists:
            certs_to_create.append({
                'cert_name': desired_cert_name,
                'cert_type': "Google-managed" if self.managed_certificate else "Self-managed",
                'domains': self.domain_names,
                'domain_count': len(self.domain_names),
                'location': self.location,
                'scope': self.scope,
                'auto_renewal': self.managed_certificate,
                'description': self.description
            })
        else:
            certs_to_keep.append(existing_certificates[desired_cert_name])

        print(f"\n🔐 Google Cloud Certificate Manager Preview")
        
        # Show certificates to create
        if certs_to_create:
            print(f"╭─ 🔐 SSL Certificates to CREATE: {len(certs_to_create)}")
            for cert in certs_to_create:
                print(f"├─ 🆕 {cert['cert_name']}")
                print(f"│  ├─ 🏷️  Type: {cert['cert_type']}")
                print(f"│  ├─ 📍 Location: {cert['location']}")
                print(f"│  ├─ 🎯 Scope: {cert['scope']}")
                print(f"│  ├─ 🌍 Domains: {cert['domain_count']}")
                
                if cert['domains']:
                    print(f"│  ├─ 📋 Domain List:")
                    for i, domain in enumerate(cert['domains'][:5]):  # Show first 5 domains
                        connector = "│  │  ├─" if i < min(len(cert['domains']), 5) - 1 else "│  │  └─"
                        print(f"{connector} {domain}")
                        if i == 0 and '.' in domain:
                            print(f"│  │     └─ Include: www.{domain}")
                    if len(cert['domains']) > 5:
                        print(f"│  │     └─ ... and {len(cert['domains']) - 5} more domains")
                
                print(f"│  ├─ 🔄 Auto-renewal: {'✅ Enabled' if cert['auto_renewal'] else '❌ Manual'}")
                
                if cert['cert_type'] == "Google-managed":
                    print(f"│  ├─ ⚡ Provisioning: Automatic via DNS/HTTP validation")
                    print(f"│  ├─ 🔒 Encryption: RSA 2048-bit or ECDSA P-256")
                else:
                    print(f"│  ├─ 📜 Source: Self-managed certificate")
                    print(f"│  ├─ ⚠️  Renewal: Manual renewal required")
                
                print(f"│  └─ 💰 Cost: Free (Google-managed certificates)")
            print(f"╰─")

        # Show existing certificates being kept
        if certs_to_keep:
            print(f"\n╭─ 🔐 Existing SSL Certificates to KEEP: {len(certs_to_keep)}")
            for cert in certs_to_keep:
                status_icon = "✅" if cert['status'] == 'active' else "⏳" if cert['status'] == 'provisioning' else "⚠️"
                print(f"├─ {status_icon} {cert['cert_name']}")
                print(f"│  ├─ 🏷️  Type: {cert['cert_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 📊 Status: {cert['status'].replace('_', ' ').title()}")
                print(f"│  ├─ 🌍 Domains: {cert['domain_count']}")
                
                if cert['domains']:
                    print(f"│  ├─ 📋 Protected Domains:")
                    for i, domain in enumerate(cert['domains'][:3]):  # Show first 3 domains
                        connector = "│  │  ├─" if i < min(len(cert['domains']), 3) - 1 else "│  │  └─"
                        print(f"{connector} {domain}")
                    if len(cert['domains']) > 3:
                        print(f"│  │     └─ ... and {len(cert['domains']) - 3} more domains")
                
                print(f"│  ├─ 📍 Location: {cert['location']}")
                print(f"│  ├─ 🎯 Scope: {cert['scope']}")
                print(f"│  ├─ 🔄 Auto-renewal: {'✅ Yes' if cert['auto_renewal'] else '❌ No'}")
                
                if cert['provisioning_issues']:
                    print(f"│  ├─ ⚠️  Issues: {len(cert['provisioning_issues'])} provisioning issues")
                    for issue in cert['provisioning_issues'][:2]:
                        print(f"│  │     └─ {issue['type']}: {issue['details'][:50]}...")
                
                if cert['create_time']:
                    print(f"│  └─ 📅 Created: {cert['create_time']}")
                else:
                    print(f"│  └─ 📅 Created: Unknown")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 SSL Certificate Costs:")
        print(f"   ├─ 🔐 Google-managed certificates: Free")
        print(f"   ├─ 🔄 Automatic renewal: Free")
        print(f"   ├─ 📡 Certificate Manager API: Free")
        print(f"   ├─ 🌍 Domain validation: Free")
        print(f"   └─ 📊 Total: $0.00/month")

        # Show validation requirements for new managed certificates
        if certs_to_create and any(cert['cert_type'] == "Google-managed" for cert in certs_to_create):
            print(f"\n🔍 Domain Validation Required:")
            print(f"   ├─ 📋 DNS validation: Add TXT records")
            print(f"   ├─ 🌐 HTTP validation: Upload verification files") 
            print(f"   ├─ ⏱️  Validation time: 5-15 minutes")
            print(f"   └─ ⚡ Auto-provisioning: Once validation completes")

        return {
            'resource_type': 'gcp_certificate_manager',
            'name': desired_cert_name,
            'certs_to_create': certs_to_create,
            'certs_to_keep': certs_to_keep,
            'certs_to_remove': certs_to_remove,
            'existing_certificates': existing_certificates,
            'cert_name': desired_cert_name,
            'cert_type': "Google-managed" if self.managed_certificate else "Self-managed",
            'domain_count': len(self.domain_names),
            'estimated_cost': "Free"
        }

    def create(self) -> Dict[str, Any]:
        """Create SSL certificate with smart state management"""
        self._ensure_authenticated()
        
        if not self.domain_names and self.managed_certificate:
            raise ValueError("Domain names are required for managed certificates")
        
        if not self.certificate_pem and not self.managed_certificate:
            raise ValueError("Certificate PEM data is required for self-managed certificates")
        
        # Discover existing certificates first
        existing_certificates = self._discover_existing_certificates()
        
        # Determine what changes need to be made
        desired_cert_name = self.cert_name
        
        # Check for certificates to remove (not in current configuration)
        certs_to_remove = []
        for cert_name, cert_info in existing_certificates.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which certificates should be removed based on configuration
            # For now, we'll focus on creating the desired certificate
            pass
        
        # Remove certificates no longer in configuration
        if certs_to_remove:
            print(f"\n🗑️  Removing certificates no longer in configuration:")
            for cert_info in certs_to_remove:
                print(f"╭─ 🔄 Removing certificate: {cert_info['cert_name']}")
                print(f"├─ 🏷️  Type: {cert_info['cert_type'].replace('_', ' ').title()}")
                print(f"├─ 🌍 Domains: {cert_info['domain_count']}")
                print(f"├─ 📍 Location: {cert_info['location']}")
                if cert_info['domains']:
                    print(f"├─ 📋 Protected domains:")
                    for domain in cert_info['domains'][:3]:
                        print(f"│  └─ {domain}")
                print(f"└─ ⚠️  SSL protection for these domains will be removed")
                
                # In real implementation:
                # self._delete_certificate(cert_info['cert_name'])

        # Check if our desired certificate already exists
        cert_exists = desired_cert_name in existing_certificates
        if cert_exists:
            existing_cert = existing_certificates[desired_cert_name]
            print(f"\n🔄 Certificate '{desired_cert_name}' already exists")
            print(f"   🏷️  Type: {existing_cert['cert_type'].replace('_', ' ').title()}")
            print(f"   📊 Status: {existing_cert['status'].replace('_', ' ').title()}")
            print(f"   🌍 Domains: {existing_cert['domain_count']}")
            
            if existing_cert['provisioning_issues']:
                print(f"   ⚠️  Issues: {len(existing_cert['provisioning_issues'])} provisioning issues")
                for issue in existing_cert['provisioning_issues'][:2]:
                    print(f"      └─ {issue['type']}: {issue['details'][:60]}...")
            
            result = {
                'cert_name': existing_cert['cert_name'],
                'cert_type': existing_cert['cert_type'],
                'status': existing_cert['status'],
                'domains': existing_cert['domains'],
                'domain_count': existing_cert['domain_count'],
                'existing': True
            }
            if len(certs_to_remove) > 0:
                result['changes'] = True
            return result

        print(f"\n🔐 Creating SSL certificate: {desired_cert_name}")
        print(f"   🏷️  Type: {'Google-managed' if self.managed_certificate else 'Self-managed'}")
        print(f"   📍 Location: {self.location}")
        print(f"   🎯 Scope: {self.scope}")
        print(f"   🌍 Domains: {len(self.domain_names)}")
        
        if self.domain_names:
            print(f"   📋 Domain list:")
            for domain in self.domain_names[:5]:
                print(f"      └─ {domain}")
            if len(self.domain_names) > 5:
                print(f"      └─ ... and {len(self.domain_names) - 5} more domains")

        try:
            result = self._create_new_certificate()
            
            print(f"\n✅ SSL certificate created successfully!")
            print(f"   🔐 Name: {result.get('cert_name', desired_cert_name)}")
            print(f"   🏷️  Type: {'Google-managed' if self.managed_certificate else 'Self-managed'}")
            print(f"   📊 Status: {result.get('status', 'Provisioning')}")
            print(f"   🌍 Protected domains: {len(self.domain_names)}")
            print(f"   🔄 Auto-renewal: {'✅ Enabled' if self.managed_certificate else '❌ Manual'}")
            
            if self.managed_certificate:
                print(f"   ⏳ Domain validation required - check DNS/HTTP validation")
                print(f"   ⚡ Certificate will be active once validation completes")
            
            if len(certs_to_remove) > 0:
                result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")

            return result
        except Exception as e:
            print(f"❌ Failed to create SSL certificate: {e}")
            raise

    def _find_existing_certificate(self) -> Optional[Dict[str, Any]]:
        try:
            certificate = self.cert_manager_client.get_certificate(name=self.certificate_resource_name)
            return certificate
        except Exception:
            return None

    def _create_new_certificate(self) -> Dict[str, Any]:
        try:
            from google.cloud import certificatemanager_v1

            # Create certificate object
            if self.managed_certificate:
                # Google-managed certificate
                certificate = certificatemanager_v1.Certificate(
                    name=self.certificate_resource_name,
                    description=self.description,
                    managed=certificatemanager_v1.Certificate.ManagedCertificate(
                        domains=self.domain_names
                    ),
                    scope=self.scope,
                    labels=self.cert_labels
                )
            else:
                # Self-managed certificate
                certificate = certificatemanager_v1.Certificate(
                    name=self.certificate_resource_name,
                    description=self.description,
                    self_managed=certificatemanager_v1.Certificate.SelfManagedCertificate(
                        pem_certificate=self.certificate_pem,
                        pem_private_key=self.private_key_pem
                    ),
                    scope=self.scope,
                    labels=self.cert_labels
                )

            # Create certificate
            operation = self.cert_manager_client.create_certificate(
                parent=f"projects/{self.gcp_client.project}/locations/{self.location}",
                certificate_id=self.cert_name,
                certificate=certificate
            )

            print(f"✅ Certificate creation initiated!")
            print(f"📍 Certificate: {self.certificate_resource_name}")

            if self.managed_certificate:
                print("\n📋 Domain Validation Required:")
                print("You need to prove domain ownership by adding DNS records or files.")
                print("Certificate will be provisioned automatically once validation is complete.")
                print("\nValidation methods:")
                for domain in self.domain_names:
                    print(f"  • {domain}: Add DNS TXT record or HTTP file")

            # Wait for operation to complete (briefly)
            try:
                result = operation.result(timeout=60)  # Wait up to 1 minute
                self._extract_certificate_info(result)
                print("✅ Certificate created successfully!")
            except Exception:
                print("⏳ Certificate creation in progress...")
                self.certificate_status = "PROVISIONING"

            return self._get_certificate_info()

        except Exception as e:
            print(f"❌ Failed to create certificate: {str(e)}")
            raise

    def _extract_certificate_info(self, certificate):
        """Extract information from certificate resource"""
        try:
            self.certificate_id = certificate.name.split('/')[-1]
            
            # Extract domain validation information for managed certificates
            if hasattr(certificate, 'managed') and certificate.managed:
                self.certificate_status = "MANAGED_PROVISIONING"
                if hasattr(certificate.managed, 'provisioning_issue'):
                    issue = certificate.managed.provisioning_issue
                    if issue:
                        print(f"⚠️  Provisioning issue: {issue.details}")
            else:
                self.certificate_status = "ACTIVE"

        except Exception as e:
            print(f"⚠️  Failed to extract certificate info: {e}")

    def wait_for_provisioning(self, timeout_minutes: int = 30) -> Dict[str, Any]:
        """Wait for certificate provisioning to complete"""
        print(f"⏳ Waiting for certificate provisioning (timeout: {timeout_minutes} minutes)...")
        
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                certificate = self.cert_manager_client.get_certificate(name=self.certificate_resource_name)
                
                if hasattr(certificate, 'managed') and certificate.managed:
                    # Check managed certificate status
                    if hasattr(certificate.managed, 'state'):
                        state = certificate.managed.state
                        if state == certificatemanager_v1.Certificate.ManagedCertificate.State.ACTIVE:
                            print(f"✅ Certificate provisioned and active!")
                            self.certificate_status = "ACTIVE"
                            return self._get_certificate_info()
                        elif state == certificatemanager_v1.Certificate.ManagedCertificate.State.FAILED:
                            print(f"❌ Certificate provisioning failed")
                            return {'success': False, 'error': 'Provisioning failed'}
                
                print(f"   Status: Provisioning - waiting...")
                time.sleep(30)
                
            except Exception as e:
                print(f"⚠️  Error checking provisioning status: {e}")
                time.sleep(30)
        
        print(f"⚠️  Provisioning timeout after {timeout_minutes} minutes")
        return {'success': False, 'error': 'Provisioning timeout'}

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        print(f"🗑️  Destroying Certificate: {self.cert_name}")

        try:
            if not self.certificate_resource_name:
                return {'success': False, 'error': 'Certificate resource name not set'}

            # Delete certificate
            operation = self.cert_manager_client.delete_certificate(name=self.certificate_resource_name)
            
            # Wait for deletion to complete
            try:
                operation.result(timeout=120)  # Wait up to 2 minutes
                print(f"✅ Certificate destroyed!")
            except Exception:
                print(f"✅ Certificate deletion initiated!")

            return {'success': True, 'certificate_name': self.cert_name, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy certificate: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_certificate_info(self) -> Dict[str, Any]:
        try:
            return {
                'success': True,
                'certificate_name': self.cert_name,
                'certificate_resource_name': self.certificate_resource_name,
                'domain_names': self.domain_names,
                'certificate_type': "Google-managed" if self.managed_certificate else "Self-managed",
                'status': self.certificate_status,
                'location': self.location
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _estimate_monthly_cost(self) -> str:
        # Google-managed SSL certificates are free
        # Self-managed certificates may have minimal costs for management
        if self.managed_certificate:
            return "Free"
        else:
            return "~$0.10/month"

    # Rails-like chainable methods
    def domains(self, domain_list: List[str]) -> 'CertificateManager':
        """Set domain names for the certificate"""
        self.domain_names = domain_list
        return self

    def domain(self, domain_name: str) -> 'CertificateManager':
        """Add a single domain name"""
        if domain_name not in self.domain_names:
            self.domain_names.append(domain_name)
        return self

    def managed(self) -> 'CertificateManager':
        """Use Google-managed certificate (automatic provisioning)"""
        self.managed_certificate = True
        return self

    def self_managed(self, certificate_pem: str, private_key_pem: str) -> 'CertificateManager':
        """Use self-managed certificate with provided PEM data"""
        self.managed_certificate = False
        self.certificate_pem = certificate_pem
        self.private_key_pem = private_key_pem
        return self

    def global_scope(self) -> 'CertificateManager':
        """Set global scope (for global load balancers)"""
        self.location = "global"
        self.scope = "DEFAULT"
        return self

    def regional(self, region: str) -> 'CertificateManager':
        """Set regional scope"""
        self.location = region
        self.scope = "DEFAULT"
        return self

    def edge_cache(self) -> 'CertificateManager':
        """Set edge cache scope"""
        self.scope = "EDGE_CACHE"
        return self

    def labels(self, labels: Dict[str, str]) -> 'CertificateManager':
        """Set labels"""
        self.cert_labels.update(labels)
        return self

    def label(self, key: str, value: str) -> 'CertificateManager':
        """Add single label"""
        self.cert_labels[key] = value
        return self

    def description_text(self, desc: str) -> 'CertificateManager':
        """Set description"""
        self.description = desc
        return self

    # Rails convenience methods
    def single_domain_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: Single domain certificate"""
        return (self.domain(domain_name)
                .managed()
                .global_scope())

    def wildcard_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: Wildcard certificate"""
        return (self.domain(f"*.{domain_name}")
                .domain(domain_name)  # Include apex domain
                .managed()
                .global_scope())

    def webapp_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: Web app certificate (www + apex)"""
        return (self.domains([domain_name, f"www.{domain_name}"])
                .managed()
                .global_scope()
                .label("purpose", "webapp"))

    def api_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: API certificate"""
        return (self.domain(f"api.{domain_name}")
                .managed()
                .global_scope()
                .label("purpose", "api"))

    def multi_domain_cert(self, domain_list: List[str]) -> 'CertificateManager':
        """Rails convenience: Multi-domain certificate"""
        return (self.domains(domain_list)
                .managed()
                .global_scope())

    def load_balancer_cert(self, domain_list: List[str]) -> 'CertificateManager':
        """Rails convenience: Load balancer certificate"""
        return (self.domains(domain_list)
                .managed()
                .global_scope()
                .label("purpose", "load-balancer"))

    def cdn_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: CDN certificate"""
        return (self.domain(domain_name)
                .managed()
                .edge_cache()
                .label("purpose", "cdn"))

    def complete_website_cert(self, domain_name: str) -> 'CertificateManager':
        """Rails convenience: Complete website certificate"""
        return (self.domains([
                    domain_name,
                    f"www.{domain_name}",
                    f"api.{domain_name}",
                    f"cdn.{domain_name}"
                ])
                .managed()
                .global_scope()
                .label("purpose", "complete-website")) 