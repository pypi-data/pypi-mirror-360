import os
from typing import Dict, Any, Optional, List, Union
from ..base_resource import BaseGcpResource
from ..auth_service import GcpAuthenticationService
from ...googlecloud_managers.gcp_client import GcpClient
from ...googlecloud_managers.status_reporter import GcpStatusReporter


class DnsRecord:
    """Represents a DNS record for Cloud DNS"""
    
    def __init__(self, name: str, record_type: str, ttl: int = 300):
        self.name = name
        self.record_type = record_type.upper()
        self.ttl = ttl
        self.values = []
        
    def add_value(self, value: str):
        """Add a value to this DNS record"""
        self.values.append(value)
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        return {
            'name': self.name,
            'type': self.record_type,
            'ttl': self.ttl,
            'rrdatas': self.values
        }


class CloudDNS(BaseGcpResource):
    """Rails-like Google Cloud DNS orchestrator - domain management made simple"""

    def __init__(self, zone_name: str):
        self.config = {
            'zone_name': zone_name,
            'dns_name': None,
            'description': f"DNS zone for {zone_name}",
            'visibility': 'public',
            'dnssec_enabled': False,
            'vpc_networks': [],
            'forwarding_targets': []
        }
        self.records = []
        self.status_reporter = GcpStatusReporter()
        super().__init__(zone_name)

    def _initialize_managers(self):
        """Initialize DNS specific managers"""
        self.dns_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Initialize GCP client for DNS operations  
        from ...googlecloud_managers.gcp_client import GcpClient
        if not hasattr(self, 'gcp_client') or not self.gcp_client:
            self.gcp_client = GcpClient()
            self.gcp_client.authenticate(silent=True)
        
        # We'll implement DNS manager later, for now use direct API calls
        pass

    def _discover_existing_zones(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DNS zones and their records"""
        existing_zones = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            service = discovery.build('dns', 'v1', credentials=self.gcp_client.credentials)
            
            # List all managed zones
            request = service.managedZones().list(project=self.gcp_client.project_id)
            response = request.execute()
            
            for zone in response.get('managedZones', []):
                zone_name = zone['name']
                
                # Get records for this zone
                records_request = service.resourceRecordSets().list(
                    project=self.gcp_client.project_id,
                    managedZone=zone_name
                )
                records_response = records_request.execute()
                
                existing_zones[zone_name] = {
                    'zone_name': zone_name,
                    'dns_name': zone.get('dnsName'),
                    'description': zone.get('description', ''),
                    'visibility': zone.get('visibility', 'public'),
                    'dnssec_enabled': zone.get('dnssecConfig', {}).get('state') == 'on',
                    'creation_time': zone.get('creationTime'),
                    'name_servers': zone.get('nameServers', []),
                    'records_count': len(records_response.get('rrsets', [])),
                    'records': records_response.get('rrsets', [])
                }
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing DNS zones: {str(e)}")
        
        return existing_zones

    def domain(self, domain_name: str) -> 'CloudDNS':
        """Set the domain name for this DNS zone"""
        # Ensure domain ends with a dot for DNS
        if not domain_name.endswith('.'):
            domain_name += '.'
        self.config['dns_name'] = domain_name
        return self

    def description(self, description: str) -> 'CloudDNS':
        """Set description for the DNS zone"""
        self.config['description'] = description
        return self

    def private(self, vpc_networks: List[str] = None) -> 'CloudDNS':
        """Configure as private DNS zone for VPC networks"""
        self.config['visibility'] = 'private'
        if vpc_networks:
            self.config['vpc_networks'] = vpc_networks
        return self

    def public(self) -> 'CloudDNS':
        """Configure as public DNS zone (default)"""
        self.config['visibility'] = 'public'
        self.config['vpc_networks'] = []
        return self

    def dnssec(self, enabled: bool = True) -> 'CloudDNS':
        """Enable/disable DNSSEC for enhanced security"""
        self.config['dnssec_enabled'] = enabled
        return self

    def a_record(self, name: str, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Add an A record (IPv4 address)"""
        record = DnsRecord(self._format_record_name(name), 'A', ttl)
        record.add_value(ip_address)
        self.records.append(record)
        return self

    def aaaa_record(self, name: str, ipv6_address: str, ttl: int = 300) -> 'CloudDNS':
        """Add an AAAA record (IPv6 address)"""
        record = DnsRecord(self._format_record_name(name), 'AAAA', ttl)
        record.add_value(ipv6_address)
        self.records.append(record)
        return self

    def cname_record(self, name: str, target: str, ttl: int = 300) -> 'CloudDNS':
        """Add a CNAME record (canonical name)"""
        record = DnsRecord(self._format_record_name(name), 'CNAME', ttl)
        # For CNAME targets, don't format if it's already a FQDN or external domain
        if '.' in target and not target.endswith('.'):
            # Add trailing dot for FQDN
            target = target + '.'
        elif not target.endswith('.') and target != '@':
            # Internal reference within the zone
            target = self._format_record_name(target)
        record.add_value(target)
        self.records.append(record)
        return self

    def mx_record(self, name: str, priority: int, mail_server: str, ttl: int = 300) -> 'CloudDNS':
        """Add an MX record (mail exchange)"""
        record = DnsRecord(self._format_record_name(name), 'MX', ttl)
        record.add_value(f"{priority} {self._format_record_name(mail_server)}")
        self.records.append(record)
        return self

    def txt_record(self, name: str, text: str, ttl: int = 300) -> 'CloudDNS':
        """Add a TXT record (text record)"""
        record = DnsRecord(self._format_record_name(name), 'TXT', ttl)
        # TXT records need to be quoted
        if not text.startswith('"'):
            text = f'"{text}"'
        record.add_value(text)
        self.records.append(record)
        return self

    def ns_record(self, name: str, nameserver: str, ttl: int = 300) -> 'CloudDNS':
        """Add an NS record (name server)"""
        record = DnsRecord(self._format_record_name(name), 'NS', ttl)
        record.add_value(self._format_record_name(nameserver))
        self.records.append(record)
        return self

    def srv_record(self, name: str, priority: int, weight: int, port: int, target: str, ttl: int = 300) -> 'CloudDNS':
        """Add an SRV record (service record)"""
        record = DnsRecord(self._format_record_name(name), 'SRV', ttl)
        record.add_value(f"{priority} {weight} {port} {self._format_record_name(target)}")
        self.records.append(record)
        return self

    def www(self, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Convenience method for www A record"""
        return self.a_record('www', ip_address, ttl)

    def root(self, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Convenience method for root domain A record"""
        return self.a_record('@', ip_address, ttl)

    def subdomain(self, subdomain: str, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Convenience method for subdomain A record"""
        return self.a_record(subdomain, ip_address, ttl)

    def docs(self, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Convenience method for docs subdomain A record"""
        return self.a_record('docs', ip_address, ttl)

    def api(self, ip_address: str, ttl: int = 300) -> 'CloudDNS':
        """Convenience method for api subdomain A record"""
        return self.a_record('api', ip_address, ttl)

    def mail_setup(self, mail_server: str, priority: int = 10) -> 'CloudDNS':
        """Convenience method for basic mail setup"""
        return self.mx_record('@', priority, mail_server)

    def _format_record_name(self, name: str) -> str:
        """Format record name with proper domain suffix"""
        if name == '@':
            # Root domain
            return self.config['dns_name'] or f"{self.config['zone_name']}."
        elif name.endswith('.'):
            # Already fully qualified
            return name
        else:
            # Add domain suffix
            domain = self.config['dns_name'] or f"{self.config['zone_name']}."
            return f"{name}.{domain}"

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing zones
        existing_zones = self._discover_existing_zones()
        
        # Categorize zones
        zones_to_create = []
        zones_to_keep = []
        zones_to_remove = []
        
        records_to_create = []
        records_to_keep = []
        records_to_remove = []
        
        # Check if our desired zone exists
        desired_zone_name = self.config['zone_name']
        zone_exists = desired_zone_name in existing_zones
        
        if not zone_exists:
            zones_to_create.append({
                'zone_name': desired_zone_name,
                'dns_name': self.config['dns_name'],
                'description': self.config['description'],
                'visibility': self.config['visibility'],
                'dnssec_enabled': self.config['dnssec_enabled'],
                'vpc_networks': self.config['vpc_networks'],
                'records_count': len(self.records)
            })
            
            # All records would be created
            records_to_create = [{
                'name': record.name,
                'type': record.record_type,
                'values': record.values,
                'ttl': record.ttl
            } for record in self.records]
        else:
            zone_info = existing_zones[desired_zone_name]
            zones_to_keep.append(zone_info)
            
            # Check which records need to be created
            existing_record_names = {record['name'] for record in zone_info['records']}
            for record in self.records:
                if record.name not in existing_record_names:
                    records_to_create.append({
                        'name': record.name,
                        'type': record.record_type,
                        'values': record.values,
                        'ttl': record.ttl
                    })

        print(f"\n🌐 Google Cloud DNS Configuration Preview")
        
        # Show zones to create
        if zones_to_create:
            print(f"╭─ 🌐 DNS Zones to CREATE: {len(zones_to_create)}")
            for zone in zones_to_create:
                print(f"├─ 🆕 {zone['zone_name']}")
                print(f"│  ├─ 🌍 Domain: {zone['dns_name'] or 'Not set'}")
                print(f"│  ├─ 📝 Description: {zone['description']}")
                print(f"│  ├─ 👁️  Visibility: {zone['visibility'].title()}")
                print(f"│  ├─ 🔒 DNSSEC: {'Enabled' if zone['dnssec_enabled'] else 'Disabled'}")
                if zone['visibility'] == 'private' and zone['vpc_networks']:
                    print(f"│  ├─ 🔗 VPC Networks: {len(zone['vpc_networks'])} configured")
                print(f"│  ├─ 📋 Records: {zone['records_count']} to create")
                print(f"│  └─ 🌐 Global DNS: 100% uptime SLA")
            print(f"╰─")
        
        # Show records to create
        if records_to_create:
            print(f"╭─ 📋 DNS Records to CREATE: {len(records_to_create)}")
            for i, record in enumerate(records_to_create):
                connector = "├─" if i < len(records_to_create) - 1 else "└─"
                values_str = ', '.join(record['values'])
                print(f"{connector} {record['type']:>6} {record['name']:<35} → {values_str}")
                if i < len(records_to_create) - 1:
                    print(f"│  └─ TTL: {record['ttl']}s")
                else:
                    print(f"   └─ TTL: {record['ttl']}s")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        zone_count = len(zones_to_create) + len(zones_to_keep)
        print(f"   ├─ 🌐 Hosted Zones: ${zone_count * 0.50:.2f} (${0.50:.2f} per zone)")
        print(f"   ├─ 🔍 DNS Queries: $0.40 per million queries")
        if any(zone.get('dnssec_enabled') for zone in zones_to_create):
            print(f"   ├─ 🔒 DNSSEC: No additional cost")
        if any(zone.get('visibility') == 'private' for zone in zones_to_create):
            print(f"   ├─ 🔗 Private Zones: Same as public zones")
        print(f"   └─ 🎯 Free Tier: First 25 zones free for first year")

        return {
            'resource_type': 'gcp_cloud_dns',
            'name': self.config['zone_name'],
            'zones_to_create': zones_to_create,
            'zones_to_keep': zones_to_keep,
            'zones_to_remove': zones_to_remove,
            'records_to_create': records_to_create,
            'records_to_keep': records_to_keep,
            'records_to_remove': records_to_remove,
            'existing_zones': existing_zones,
            'zone_name': self.config['zone_name'],
            'dns_name': self.config['dns_name'],
            'visibility': self.config['visibility'],
            'dnssec_enabled': self.config['dnssec_enabled'],
            'records_count': len(self.records),
            'estimated_zones': zone_count
        }

    def create(self) -> Dict[str, Any]:
        """Create the DNS zone and records with smart state management"""
        self._ensure_authenticated()

        if not self.config['dns_name']:
            raise ValueError("Domain name is required. Use .domain('example.com') to set it.")

        # Discover existing zones first
        existing_zones = self._discover_existing_zones()
        
        # Determine what changes need to be made
        desired_zone_name = self.config['zone_name']
        
        # Check for zones to remove (not in current configuration)
        zones_to_remove = []
        for zone_name, zone_info in existing_zones.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which zones should be removed based on configuration
            # For now, we'll focus on creating the desired zone
            pass
        
        # Remove zones no longer in configuration
        if zones_to_remove:
            print(f"\n🗑️  Removing DNS zones no longer in configuration:")
            for zone_info in zones_to_remove:
                print(f"╭─ 🔄 Removing zone: {zone_info['zone_name']}")
                print(f"├─ 🌍 Domain: {zone_info['dns_name']}")
                print(f"├─ 📋 Records: {zone_info['records_count']}")
                print(f"├─ 👁️  Visibility: {zone_info['visibility'].title()}")
                print(f"└─ ⚠️  Zone and all records will be permanently deleted")
                
                # In real implementation:
                # self._delete_dns_zone_by_name(zone_info['zone_name'])

        print(f"\n🌐 Creating Google Cloud DNS zone: {self.config['zone_name']}")

        try:
            # Create DNS zone (or use existing)
            zone_result = self._create_dns_zone()
            
            # Create DNS records
            records_result = []
            if self.records:
                records_result = self._create_dns_records()

            result = {
                'status': 'success',
                'zone': zone_result,
                'records': records_result,
                'name_servers': zone_result.get('nameServers', []),
                'resource_type': 'gcp_cloud_dns'
            }

            print(f"\n✅ DNS zone '{self.config['zone_name']}' ready!")
            print(f"   🌍 Domain: {self.config['dns_name']}")
            print(f"   👁️  Visibility: {self.config['visibility'].title()}")
            if self.config['dnssec_enabled']:
                print(f"   🔒 DNSSEC: Enabled")
            print(f"   📋 Records: {len(records_result)} created/updated")
            
            if result['name_servers']:
                print(f"\n🔗 Name Servers (configure with domain registrar):")
                for ns in result['name_servers']:
                    print(f"   • {ns}")
            
            if len(zones_to_remove) > 0:
                result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")

            return result

        except Exception as e:
            print(f"❌ Failed to create DNS zone: {str(e)}")
            raise

    def add_records(self) -> Dict[str, Any]:
        """Add DNS records to existing zone without trying to create the zone"""
        self._ensure_authenticated()

        if not self.config['dns_name']:
            raise ValueError("Domain name is required. Use .domain('example.com') to set it.")

        self._print_resource_header("Google Cloud DNS Records", "Adding")

        try:
            # Only create DNS records, don't try to create the zone
            records_result = []
            if self.records:
                records_result = self._create_dns_records()

            result = {
                'status': 'success',
                'records': records_result,
                'resource_type': 'cloud_dns_records'
            }

            print(f"✅ DNS records added to zone '{self.config['zone_name']}' successfully!")
            print(f"📋 Records created: {len(records_result)}")

            return result

        except Exception as e:
            print(f"❌ Failed to add DNS records: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the DNS zone and all records"""
        self._ensure_authenticated()

        self._print_resource_header("Google Cloud DNS Zone", "Destroying")

        try:
            result = self._delete_dns_zone()
            print(f"✅ DNS zone '{self.config['zone_name']}' deleted successfully!")
            return result

        except Exception as e:
            print(f"❌ Failed to delete DNS zone: {str(e)}")
            raise

    def _create_dns_zone(self) -> Dict[str, Any]:
        """Create the DNS zone using Google Cloud DNS API, or return existing zone"""
        from googleapiclient import discovery
        from googleapiclient.errors import HttpError

        service = discovery.build('dns', 'v1', credentials=self.gcp_client.credentials)
        
        # First, check if the zone already exists
        try:
            request = service.managedZones().get(
                project=self.gcp_client.project_id,
                managedZone=self.config['zone_name']
            )
            existing_zone = request.execute()
            print(f"🔍 DNS zone '{self.config['zone_name']}' already exists, using existing zone")
            return existing_zone
        except HttpError as e:
            if e.resp.status != 404:
                # Re-raise if it's not a "not found" error
                raise e
            # Zone doesn't exist, continue with creation
            pass
        
        # Zone doesn't exist, create it
        zone_body = {
            'name': self.config['zone_name'],
            'dnsName': self.config['dns_name'],
            'description': self.config['description'],
            'visibility': self.config['visibility']
        }

        if self.config['dnssec_enabled']:
            zone_body['dnssecConfig'] = {'state': 'on'}

        if self.config['visibility'] == 'private' and self.config['vpc_networks']:
            zone_body['privateVisibilityConfig'] = {
                'networks': [{'networkUrl': net} for net in self.config['vpc_networks']]
            }

        request = service.managedZones().create(
            project=self.gcp_client.project_id,
            body=zone_body
        )
        
        return request.execute()

    def _create_dns_records(self) -> List[Dict[str, Any]]:
        """Create DNS records in the zone"""
        from googleapiclient import discovery
        from googleapiclient.errors import HttpError

        service = discovery.build('dns', 'v1', credentials=self.gcp_client.credentials)
        
        # Prepare record sets
        additions = []
        for record in self.records:
            additions.append(record.to_dict())

        if not additions:
            return []

        try:
            # Create change request
            change_body = {
                'additions': additions
            }

            request = service.changes().create(
                project=self.gcp_client.project_id,
                managedZone=self.config['zone_name'],
                body=change_body
            )
            
            result = request.execute()
            
            # Wait for change to complete
            self._wait_for_change(service, result['id'])
            
            print(f"✅ Successfully created {len(additions)} DNS records")
            return additions
            
        except HttpError as e:
            if 'already exists' in str(e):
                print(f"⚠️  Some DNS records already exist, skipping duplicates")
                return additions
            else:
                print(f"❌ Failed to create DNS records: {str(e)}")
                raise

    def _delete_dns_zone(self) -> Dict[str, Any]:
        """Delete the DNS zone"""
        from googleapiclient import discovery

        service = discovery.build('dns', 'v1', credentials=self.gcp_client.credentials)
        
        request = service.managedZones().delete(
            project=self.gcp_client.project_id,
            managedZone=self.config['zone_name']
        )
        
        return request.execute()

    def _wait_for_change(self, service, change_id: str, timeout: int = 300):
        """Wait for DNS change to propagate"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            request = service.changes().get(
                project=self.gcp_client.project_id,
                managedZone=self.config['zone_name'],
                changeId=change_id
            )
            change = request.execute()
            
            if change['status'] == 'done':
                return
                
            time.sleep(5)
        
        print("⚠️  DNS change is still propagating...")

    def get_info(self) -> Dict[str, Any]:
        """Get information about the DNS zone"""
        self._ensure_authenticated()
        
        try:
            from googleapiclient import discovery
            service = discovery.build('dns', 'v1', credentials=self.gcp_client.credentials)
            
            request = service.managedZones().get(
                project=self.gcp_client.project_id,
                managedZone=self.config['zone_name']
            )
            
            return request.execute()
            
        except Exception as e:
            print(f"❌ Failed to get DNS zone info: {str(e)}")
            raise


# Convenience alias
DNS = CloudDNS 