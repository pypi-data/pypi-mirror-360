"""
AWS Domain Registration Resource

Automatically register domains through Route53 Domains API.
Integrates with Certificate Manager and Route53 for seamless domain setup.
"""

import time
from typing import Dict, Any, List, Optional
from .base_resource import BaseAwsResource


class DomainRegistration(BaseAwsResource):
    """
    AWS Domain Registration Resource
    
    Automatically registers domains through Route53 Domains API and sets up DNS.
    """

    def __init__(self, name: str):
        """
        Initialize Domain Registration resource.

        Args:
            name: Resource name for identification
        """
        super().__init__(name)

        # Core configuration
        self.domain_name = None
        self.registration_duration_years = 1
        
        # Contact information
        self.admin_contact = {}
        self.registrant_contact = {}
        self.tech_contact = {}
        
        # Auto-configuration
        self.auto_renew = True
        self.privacy_protection = True
        self.transfer_lock = True
        
        # DNS settings
        self.create_hosted_zone = True
        self.use_route53_nameservers = True
        
        # State
        self.domain_registered = False
        self.hosted_zone_created = False
        self.nameservers = []
        
        # Clients
        self.domains_client = None
        self.route53_client = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        # Domain registration doesn't need separate managers
        # All functionality is handled directly by the class
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        from ..aws_managers.aws_client import AwsClient
        
        self.aws_client = AwsClient()
        self.aws_client.authenticate(silent=True)
        self.domains_client = self.get_domains_client()
        self.route53_client = self.get_route53_client()

    def get_domains_client(self):
        """Get Route53 Domains client"""
        try:
            import boto3
            return boto3.client('route53domains', region_name='us-east-1')  # Domains API is only in us-east-1
        except Exception as e:
            print(f"⚠️  Failed to create Route53 Domains client: {e}")
            return None

    def get_route53_client(self):
        """Get Route53 client"""
        try:
            import boto3
            return boto3.client('route53', region_name='us-east-1')
        except Exception as e:
            print(f"⚠️  Failed to create Route53 client: {e}")
            return None

    def check_domain_availability(self, domain_name: str = None) -> Dict[str, Any]:
        """Check if a domain is available for registration"""
        domain = domain_name or self.domain_name
        if not domain:
            return {'available': False, 'error': 'No domain specified'}
        
        try:
            response = self.domains_client.check_domain_availability(DomainName=domain)
            return {
                'domain': domain,
                'available': response['Availability'] == 'AVAILABLE',
                'availability': response['Availability']
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}

    def is_domain_registered(self, domain_name: str = None) -> bool:
        """Check if domain is already registered (by us or others)"""
        domain = domain_name or self.domain_name
        if not domain:
            return False
            
        try:
            # Check if we own this domain
            response = self.domains_client.list_domains()
            for registered_domain in response.get('Domains', []):
                if registered_domain['DomainName'].lower() == domain.lower():
                    return True
            return False
        except Exception:
            # If we can't check, assume it might be registered
            return True

    def preview(self) -> Dict[str, Any]:
        """Preview domain registration actions"""
        self._ensure_authenticated()
        
        if not self.domain_name:
            return {'error': 'Domain name required'}
        
        # Check domain status
        availability = self.check_domain_availability()
        already_registered = self.is_domain_registered()
        
        domain_cost = self.estimate_domain_cost()
        
        actions = []
        
        if already_registered:
            actions.append({
                'action': 'keep',
                'description': f'Domain {self.domain_name} already registered',
                'cost': 0
            })
        elif availability.get('available', False):
            actions.append({
                'action': 'register',
                'description': f'Register domain {self.domain_name}',
                'duration': f'{self.registration_duration_years} year(s)',
                'cost': domain_cost
            })
        else:
            actions.append({
                'action': 'unavailable',
                'description': f'Domain {self.domain_name} not available',
                'availability': availability.get('availability', 'UNKNOWN'),
                'cost': 0
            })
        
        if self.create_hosted_zone:
            actions.append({
                'action': 'create_zone',
                'description': f'Create Route53 hosted zone',
                'cost': 0.50  # $0.50/month per hosted zone
            })
        
        # Generate mock values for preview
        mock_operation_id = f"op-{hash(self.domain_name or 'default') % 1000000:06d}"
        mock_hosted_zone_id = f"Z{hash(self.domain_name or 'default') % 1000000:06d}"
        
        return {
            'domain_name': self.domain_name,
            'operation_id': mock_operation_id,  # Mock operation ID for preview
            'hosted_zone_id': mock_hosted_zone_id,  # Mock hosted zone ID for preview
            'actions': actions,
            'total_cost': sum(action.get('cost', 0) for action in actions),
            'available': availability.get('available', False),
            'already_registered': already_registered
        }

    def create(self) -> Dict[str, Any]:
        """Register domain and set up DNS automatically"""
        self._ensure_authenticated()
        
        if not self.domain_name:
            raise ValueError("Domain name is required")
        
        # Check if domain is already registered by us
        if self.is_domain_registered():
            print(f"🔄 Domain '{self.domain_name}' already registered by us")
            return self._setup_existing_domain()
        
        # Check availability
        availability = self.check_domain_availability()
        if not availability.get('available', False):
            # Domain not available - could be registered by us or someone else
            print(f"🔄 Domain '{self.domain_name}' is not available for new registration")
            print(f"   This usually means it's already registered (possibly by us)")
            print(f"   Continuing with existing domain setup...")
            return self._setup_existing_domain()
        
        print(f"🌐 Registering domain: {self.domain_name}")
        print(f"   ⏱️  Duration: {self.registration_duration_years} year(s)")
        print(f"   🔒 Privacy Protection: {'Enabled' if self.privacy_protection else 'Disabled'}")
        print(f"   🔄 Auto Renewal: {'Enabled' if self.auto_renew else 'Disabled'}")
        
        try:
            # Register the domain
            response = self.domains_client.register_domain(
                DomainName=self.domain_name,
                DurationInYears=self.registration_duration_years,
                AutoRenew=self.auto_renew,
                AdminContact=self._get_contact_info('admin'),
                RegistrantContact=self._get_contact_info('registrant'),
                TechContact=self._get_contact_info('tech'),
                PrivacyProtectAdminContact=self.privacy_protection,
                PrivacyProtectRegistrantContact=self.privacy_protection,
                PrivacyProtectTechContact=self.privacy_protection
            )
            
            operation_id = response['OperationId']
            print(f"✅ Domain registration initiated!")
            print(f"📍 Operation ID: {operation_id}")
            
            # Create hosted zone if requested
            hosted_zone_id = None
            if self.create_hosted_zone:
                hosted_zone_id = self._create_hosted_zone()
            
            return {
                'success': True,
                'domain_name': self.domain_name,
                'operation_id': operation_id,
                'hosted_zone_id': hosted_zone_id,
                'nameservers': self.nameservers,
                'status': 'registering',
                'auto_renew': self.auto_renew,
                'privacy_protection': self.privacy_protection
            }
            
        except Exception as e:
            print(f"❌ Failed to register domain: {str(e)}")
            raise

    def _setup_existing_domain(self) -> Dict[str, Any]:
        """Set up DNS for an existing domain"""
        hosted_zone_id = None
        
        if self.create_hosted_zone:
            hosted_zone_id = self._create_hosted_zone()
        
        return {
            'success': True,
            'domain_name': self.domain_name,
            'hosted_zone_id': hosted_zone_id,
            'nameservers': self.nameservers,
            'status': 'existing',
            'existing': True
        }

    def _create_hosted_zone(self) -> str:
        """Create Route53 hosted zone"""
        try:
            caller_reference = f"infradsl-{self.domain_name}-{int(time.time())}"
            
            response = self.route53_client.create_hosted_zone(
                Name=self.domain_name,
                CallerReference=caller_reference,
                HostedZoneConfig={
                    'Comment': f'Hosted zone for {self.domain_name} - created by InfraDSL',
                    'PrivateZone': False
                }
            )
            
            zone_id = response['HostedZone']['Id'].split('/')[-1]
            self.nameservers = response['DelegationSet']['NameServers']
            
            print(f"✅ Created hosted zone: {zone_id}")
            print(f"🌍 Nameservers: {len(self.nameservers)} assigned")
            
            return zone_id
            
        except Exception as e:
            print(f"⚠️  Failed to create hosted zone: {str(e)}")
            return None

    def _get_contact_info(self, contact_type: str) -> Dict[str, Any]:
        """Get contact information for domain registration"""
        # Use admin contact as default for all contact types if others not specified
        base_contact = self.admin_contact.copy()
        
        if contact_type == 'registrant' and self.registrant_contact:
            base_contact.update(self.registrant_contact)
        elif contact_type == 'tech' and self.tech_contact:
            base_contact.update(self.tech_contact)
        
        # Provide sensible defaults if no contact info specified
        return {
            'FirstName': base_contact.get('first_name', 'Infrastructure'),
            'LastName': base_contact.get('last_name', 'Admin'),
            'ContactType': base_contact.get('contact_type', 'COMPANY'),
            'OrganizationName': base_contact.get('organization', 'InfraDSL'),
            'AddressLine1': base_contact.get('address_line1', '123 Cloud Street'),
            'City': base_contact.get('city', 'San Francisco'),
            'State': base_contact.get('state', 'CA'),
            'CountryCode': base_contact.get('country_code', 'US'),
            'ZipCode': base_contact.get('zip_code', '94102'),
            'PhoneNumber': base_contact.get('phone', '+1.4155551234'),
            'Email': base_contact.get('email', 'admin@example.com')
        }

    def estimate_domain_cost(self) -> float:
        """Estimate domain registration cost"""
        # Common TLD pricing (simplified)
        tld_pricing = {
            '.com': 12.00,
            '.org': 12.00,
            '.net': 12.00,
            '.info': 12.00,
            '.biz': 15.00,
            '.us': 15.00,
            '.co': 30.00,
            '.io': 50.00
        }
        
        if not self.domain_name:
            return 0
        
        # Extract TLD
        parts = self.domain_name.split('.')
        if len(parts) < 2:
            return 15.00  # Default
        
        tld = '.' + parts[-1]
        return tld_pricing.get(tld, 15.00) * self.registration_duration_years

    # Chainable methods
    def domain(self, domain_name: str) -> 'DomainRegistration':
        """Set domain name"""
        self.domain_name = domain_name
        return self

    def duration(self, years: int) -> 'DomainRegistration':
        """Set registration duration"""
        self.registration_duration_years = max(1, min(10, years))
        return self

    def contact(self, email: str, first_name: str = None, last_name: str = None, organization: str = None) -> 'DomainRegistration':
        """Set contact information"""
        self.admin_contact.update({
            'email': email,
            'first_name': first_name or 'Infrastructure',
            'last_name': last_name or 'Admin',
            'organization': organization or 'InfraDSL'
        })
        return self

    def privacy(self, enabled: bool = True) -> 'DomainRegistration':
        """Enable/disable privacy protection"""
        self.privacy_protection = enabled
        return self

    def auto_renewal(self, enabled: bool = True) -> 'DomainRegistration':
        """Enable/disable auto renewal"""
        self.auto_renew = enabled
        return self

    def with_hosted_zone(self, create: bool = True) -> 'DomainRegistration':
        """Create hosted zone automatically"""
        self.create_hosted_zone = create
        return self
    
    def nexus_dns_setup(self) -> 'DomainRegistration':
        """Nexus Engine: Intelligent DNS setup with best practices"""
        self.create_hosted_zone = True
        self.use_route53_nameservers = True
        self.auto_renew = True
        self.privacy_protection = True
        return self

    def destroy(self) -> Dict[str, Any]:
        """Destroy/deregister the domain (WARNING: This is irreversible!)"""
        print(f"⚠️  WARNING: Domain destruction is not typically supported.")
        print(f"⚠️  Domains cannot be easily deleted - they expire or transfer.")
        print(f"⚠️  For domain '{self.domain_name}', consider:")
        print(f"   • Disable auto-renewal to let it expire")
        print(f"   • Transfer to another registrar")
        print(f"   • Delete associated hosted zone if created")
        
        # In a real scenario, you might:
        # 1. Disable auto-renewal
        # 2. Delete hosted zone if it was created
        # 3. Log the action for audit purposes
        
        return {
            'domain_name': self.domain_name,
            'action': 'warned',
            'message': 'Domain destruction requires manual intervention',
            'suggested_actions': [
                'Disable auto-renewal',
                'Transfer domain',
                'Let domain expire naturally'
            ]
        } 