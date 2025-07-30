"""
GCP Cloud DNS Configuration Mixin

Chainable configuration methods for Google Cloud DNS zones.
Provides Rails-like method chaining for fluent DNS configuration.
"""

from typing import Dict, Any, List, Optional
from .dns_core import DNSRecord


class DNSConfigurationMixin:
    """
    Mixin for DNS zone configuration methods.
    
    This mixin provides chainable configuration methods for:
    - DNS zone configuration (domain, visibility, DNSSEC)
    - DNS record creation (A, AAAA, CNAME, MX, TXT, etc.)
    - VPC network configuration for private zones
    - Security and performance settings
    """
    
    def domain(self, domain_name: str):
        """Set the domain name for this DNS zone (Rails convention)"""
        # Ensure domain ends with a dot for DNS
        if not domain_name.endswith('.'):
            domain_name += '.'
        
        if not self._is_valid_dns_name(domain_name):
            print(f"⚠️  Warning: Invalid domain name format '{domain_name}'")
        
        self.dns_name = domain_name
        return self
        
    def description(self, description: str):
        """Set description for the DNS zone"""
        self.dns_description = description
        return self
        
    def zone_name(self, name: str):
        """Set the zone name (Rails convention)"""
        if not self._is_valid_zone_name(name):
            print(f"⚠️  Warning: Invalid zone name format '{name}'")
        self.zone_name = name
        return self
        
    # Visibility configuration
    def public(self):
        """Configure as public DNS zone (default) - Rails convention"""
        self.dns_visibility = "public"
        self.vpc_networks = []
        return self
        
    def private(self, vpc_networks: List[str] = None):
        """Configure as private DNS zone for VPC networks - Rails convention"""
        self.dns_visibility = "private"
        if vpc_networks:
            self.vpc_networks = vpc_networks
        else:
            self.vpc_networks = []
        return self
        
    def add_vpc_network(self, network_url: str):
        """Add VPC network to private DNS zone"""
        if network_url not in self.vpc_networks:
            self.vpc_networks.append(network_url)
        return self
        
    # DNSSEC configuration
    def dnssec(self, enabled: bool = True):
        """Enable/disable DNSSEC for enhanced security"""
        self.dnssec_enabled = enabled
        self.dnssec_state = "on" if enabled else "off"
        return self
        
    def enable_dnssec(self):
        """Enable DNSSEC - Rails convenience"""
        return self.dnssec(True)
        
    def disable_dnssec(self):
        """Disable DNSSEC - Rails convenience"""
        return self.dnssec(False)
        
    def dnssec_algorithm(self, ksk_algorithm: str = "rsasha256", zsk_algorithm: str = "rsasha256"):
        """Set DNSSEC signing algorithms"""
        self.key_signing_key_algorithm = ksk_algorithm
        self.zone_signing_key_algorithm = zsk_algorithm
        return self
        
    # DNS record creation methods
    def a_record(self, name: str, ip_address: str, ttl: int = None):
        """Add an A record (IPv4 address) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        if not self._validate_record_value("A", ip_address):
            print(f"⚠️  Warning: Invalid IPv4 address '{ip_address}'")
        
        record = DNSRecord(self._format_record_name(name), 'A', ttl)
        record.add_value(ip_address)
        self.dns_records.append(record)
        return self
        
    def aaaa_record(self, name: str, ipv6_address: str, ttl: int = None):
        """Add an AAAA record (IPv6 address) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        if not self._validate_record_value("AAAA", ipv6_address):
            print(f"⚠️  Warning: Invalid IPv6 address '{ipv6_address}'")
        
        record = DNSRecord(self._format_record_name(name), 'AAAA', ttl)
        record.add_value(ipv6_address)
        self.dns_records.append(record)
        return self
        
    def cname_record(self, name: str, target: str, ttl: int = None):
        """Add a CNAME record (canonical name) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        # For CNAME targets, format properly
        if '.' in target and not target.endswith('.'):
            target = target + '.'
        elif not target.endswith('.') and target != '@':
            target = self._format_record_name(target)
            
        if not self._validate_record_value("CNAME", target):
            print(f"⚠️  Warning: Invalid CNAME target '{target}'")
        
        record = DNSRecord(self._format_record_name(name), 'CNAME', ttl)
        record.add_value(target)
        self.dns_records.append(record)
        return self
        
    def mx_record(self, name: str, priority: int, mail_server: str, ttl: int = None):
        """Add an MX record (mail exchange) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        # Format mail server
        if not mail_server.endswith('.'):
            mail_server = self._format_record_name(mail_server)
        
        value = f"{priority} {mail_server}"
        if not self._validate_record_value("MX", value):
            print(f"⚠️  Warning: Invalid MX record '{value}'")
        
        record = DNSRecord(self._format_record_name(name), 'MX', ttl)
        record.add_value(value)
        self.dns_records.append(record)
        return self
        
    def txt_record(self, name: str, text: str, ttl: int = None):
        """Add a TXT record (text record) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        # TXT records need to be quoted
        if not text.startswith('"'):
            text = f'"{text}"'
            
        if not self._validate_record_value("TXT", text):
            print(f"⚠️  Warning: Invalid TXT record value")
        
        record = DNSRecord(self._format_record_name(name), 'TXT', ttl)
        record.add_value(text)
        self.dns_records.append(record)
        return self
        
    def ns_record(self, name: str, nameserver: str, ttl: int = None):
        """Add an NS record (name server) - Rails convention"""
        ttl = ttl or self.ns_ttl
        
        if not nameserver.endswith('.'):
            nameserver = self._format_record_name(nameserver)
        
        record = DNSRecord(self._format_record_name(name), 'NS', ttl)
        record.add_value(nameserver)
        self.dns_records.append(record)
        return self
        
    def srv_record(self, name: str, priority: int, weight: int, port: int, target: str, ttl: int = None):
        """Add an SRV record (service record) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        if not target.endswith('.'):
            target = self._format_record_name(target)
        
        value = f"{priority} {weight} {port} {target}"
        if not self._validate_record_value("SRV", value):
            print(f"⚠️  Warning: Invalid SRV record '{value}'")
        
        record = DNSRecord(self._format_record_name(name), 'SRV', ttl)
        record.add_value(value)
        self.dns_records.append(record)
        return self
        
    def caa_record(self, name: str, flags: int, tag: str, value: str, ttl: int = None):
        """Add a CAA record (Certificate Authority Authorization) - Rails convention"""
        ttl = ttl or self.default_ttl
        
        caa_value = f"{flags} {tag} {value}"
        record = DNSRecord(self._format_record_name(name), 'CAA', ttl)
        record.add_value(caa_value)
        self.dns_records.append(record)
        return self
        
    # Convenience methods for common DNS patterns
    def www(self, ip_address: str, ttl: int = None):
        """Convenience method for www A record - Rails convention"""
        return self.a_record('www', ip_address, ttl)
        
    def root(self, ip_address: str, ttl: int = None):
        """Convenience method for root domain A record - Rails convention"""
        return self.a_record('@', ip_address, ttl)
        
    def subdomain(self, subdomain: str, ip_address: str, ttl: int = None):
        """Convenience method for subdomain A record - Rails convention"""
        return self.a_record(subdomain, ip_address, ttl)
        
    def api(self, ip_address: str, ttl: int = None):
        """Convenience method for api subdomain A record - Rails convention"""
        return self.a_record('api', ip_address, ttl)
        
    def docs(self, ip_address: str, ttl: int = None):
        """Convenience method for docs subdomain A record - Rails convention"""
        return self.a_record('docs', ip_address, ttl)
        
    def blog(self, ip_address: str, ttl: int = None):
        """Convenience method for blog subdomain A record - Rails convention"""
        return self.a_record('blog', ip_address, ttl)
        
    def cdn(self, target: str, ttl: int = None):
        """Convenience method for CDN CNAME record - Rails convention"""
        return self.cname_record('cdn', target, ttl)
        
    def www_redirect(self, ttl: int = None):
        """Convenience method to redirect www to root domain - Rails convention"""
        return self.cname_record('www', '@', ttl)
        
    # Mail configuration convenience methods
    def mail_setup(self, mail_server: str, priority: int = 10, ttl: int = None):
        """Convenience method for basic mail setup - Rails convention"""
        return self.mx_record('@', priority, mail_server, ttl)
        
    def google_mail(self, ttl: int = None):
        """Configure Google Workspace mail - Rails convenience"""
        mail_servers = [
            ('aspmx.l.google.com.', 1),
            ('alt1.aspmx.l.google.com.', 5),
            ('alt2.aspmx.l.google.com.', 5),
            ('alt3.aspmx.l.google.com.', 10),
            ('alt4.aspmx.l.google.com.', 10)
        ]
        for server, priority in mail_servers:
            self.mx_record('@', priority, server, ttl)
        return self
        
    def office365_mail(self, ttl: int = None):
        """Configure Office 365 mail - Rails convenience"""
        return self.mx_record('@', 0, 'outlook.com.', ttl)
        
    # Verification and validation records
    def google_verification(self, verification_code: str, ttl: int = None):
        """Add Google domain verification TXT record - Rails convenience"""
        return self.txt_record('@', f'google-site-verification={verification_code}', ttl)
        
    def spf_record(self, include_domains: List[str] = None, ttl: int = None):
        """Add SPF record for email authentication - Rails convenience"""
        includes = ' '.join(f'include:{domain}' for domain in (include_domains or []))
        spf_value = f"v=spf1 {includes} ~all".strip()
        return self.txt_record('@', spf_value, ttl)
        
    def dmarc_record(self, policy: str = "quarantine", rua: str = None, ttl: int = None):
        """Add DMARC record for email authentication - Rails convenience"""
        dmarc_value = f"v=DMARC1; p={policy};"
        if rua:
            dmarc_value += f" rua=mailto:{rua};"
        return self.txt_record('_dmarc', dmarc_value, ttl)
        
    def dkim_record(self, selector: str, public_key: str, ttl: int = None):
        """Add DKIM record for email authentication - Rails convenience"""
        dkim_value = f"v=DKIM1; k=rsa; p={public_key}"
        return self.txt_record(f'{selector}._domainkey', dkim_value, ttl)
        
    # SSL/TLS certificate validation
    def acme_challenge(self, token: str, ttl: int = None):
        """Add ACME challenge record for SSL certificate validation - Rails convenience"""
        return self.txt_record('_acme-challenge', token, ttl or 60)
        
    def ssl_certificate_validation(self, domain: str, validation_record: str, ttl: int = None):
        """Add SSL certificate validation record - Rails convenience"""
        return self.txt_record(f'_ssl-validation.{domain}', validation_record, ttl or 300)
        
    # Advanced configuration
    def ttl(self, default_ttl: int):
        """Set default TTL for new records"""
        self.default_ttl = default_ttl
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.dns_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.dns_labels[key] = value
        return self
        
    def logging(self, enabled: bool = True, log_config: Dict[str, Any] = None):
        """Enable/disable DNS query logging"""
        self.logging_enabled = enabled
        if log_config:
            self.logging_config.update(log_config)
        return self
        
    def enable_logging(self):
        """Enable DNS query logging - Rails convenience"""
        return self.logging(True)
        
    def disable_logging(self):
        """Disable DNS query logging - Rails convenience"""
        return self.logging(False)
        
    # Rails-like environment configurations
    def development_dns(self):
        """Configure for development environment - Rails convention"""
        return (self.public()
                .ttl(60)  # Short TTL for quick changes
                .disable_dnssec()
                .disable_logging()
                .label("environment", "development"))
                
    def staging_dns(self):
        """Configure for staging environment - Rails convention"""
        return (self.public()
                .ttl(300)  # Medium TTL
                .enable_dnssec()
                .enable_logging()
                .label("environment", "staging"))
                
    def production_dns(self):
        """Configure for production environment - Rails convention"""
        return (self.public()
                .ttl(3600)  # Longer TTL for stability
                .enable_dnssec()
                .enable_logging()
                .label("environment", "production"))
                
    def internal_dns(self, vpc_networks: List[str] = None):
        """Configure for internal services - Rails convention"""
        return (self.private(vpc_networks)
                .ttl(300)
                .disable_dnssec()  # DNSSEC not needed for private zones
                .enable_logging()
                .label("type", "internal"))
                
    # Bulk record operations
    def add_multiple_a_records(self, records: Dict[str, str], ttl: int = None):
        """Add multiple A records at once - Rails convenience"""
        for name, ip in records.items():
            self.a_record(name, ip, ttl)
        return self
        
    def add_load_balancer_records(self, lb_ip: str, subdomains: List[str] = None, ttl: int = None):
        """Add records for load balancer - Rails convenience"""
        subdomains = subdomains or ['www', 'api', 'app']
        
        # Root domain
        self.root(lb_ip, ttl)
        
        # Subdomains
        for subdomain in subdomains:
            self.a_record(subdomain, lb_ip, ttl)
            
        return self
        
    def clear_records(self):
        """Clear all DNS records - Rails convenience"""
        self.dns_records = []
        return self