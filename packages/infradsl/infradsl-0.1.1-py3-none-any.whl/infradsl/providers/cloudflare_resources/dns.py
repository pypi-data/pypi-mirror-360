"""
Cloudflare DNS Resource

Rails-like interface for managing Cloudflare DNS records.
Provides chainable methods for easy configuration and deployment.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.dns_manager import DNSManager


class DNS(BaseCloudflareResource):
    """
    Cloudflare DNS resource with Rails-like simplicity.

    Examples:
        # Simple A record
        dns = (Cloudflare.DNS("myapp.com")
               .a_record("www", "192.168.1.1")
               .create())

        # Complete domain setup
        domain = (Cloudflare.DNS("myapp.com")
                  .a_record("@", "192.168.1.1")
                  .a_record("www", "192.168.1.1")
                  .cname_record("api", "api.herokuapp.com")
                  .mx_record("@", "mail.google.com", priority=10)
                  .txt_record("@", "v=spf1 include:_spf.google.com ~all")
                  .create())
    """

    def __init__(self, domain: str):
        """
        Initialize DNS resource for a domain

        Args:
            domain: The domain name to manage DNS for
        """
        super().__init__(domain)
        self.domain = domain
        self.records = []
        self._ttl = 3600  # Default TTL
        self._proxied = False  # Default proxy setting

    def _initialize_managers(self):
        """Initialize DNS-specific managers"""
        self.dns_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.dns_manager = DNSManager()

    def ttl(self, seconds: int) -> 'DNS':
        """
        Set the default TTL for DNS records

        Args:
            seconds: TTL in seconds (minimum 120, maximum 86400)

        Returns:
            DNS: Self for method chaining
        """
        if seconds < 120 or seconds > 86400:
            raise ValueError("TTL must be between 120 and 86400 seconds")
        self._ttl = seconds
        return self

    def proxied(self, enabled: bool = True) -> 'DNS':
        """
        Enable/disable Cloudflare proxy for applicable records

        Args:
            enabled: Whether to proxy traffic through Cloudflare

        Returns:
            DNS: Self for method chaining
        """
        self._proxied = enabled
        return self

    def a_record(self, name: str, ip: str, ttl: Optional[int] = None, proxied: Optional[bool] = None) -> 'DNS':
        """
        Add an A record

        Args:
            name: Record name (use "@" for root domain)
            ip: IPv4 address
            ttl: TTL in seconds (uses default if not specified)
            proxied: Whether to proxy through Cloudflare (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'A',
            'name': name,
            'content': ip,
            'ttl': ttl or self._ttl,
            'proxied': proxied if proxied is not None else self._proxied
        })
        return self

    def aaaa_record(self, name: str, ipv6: str, ttl: Optional[int] = None, proxied: Optional[bool] = None) -> 'DNS':
        """
        Add an AAAA record (IPv6)

        Args:
            name: Record name (use "@" for root domain)
            ipv6: IPv6 address
            ttl: TTL in seconds (uses default if not specified)
            proxied: Whether to proxy through Cloudflare (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'AAAA',
            'name': name,
            'content': ipv6,
            'ttl': ttl or self._ttl,
            'proxied': proxied if proxied is not None else self._proxied
        })
        return self

    def cname_record(self, name: str, target: str, ttl: Optional[int] = None, proxied: Optional[bool] = None) -> 'DNS':
        """
        Add a CNAME record

        Args:
            name: Record name
            target: Target domain
            ttl: TTL in seconds (uses default if not specified)
            proxied: Whether to proxy through Cloudflare (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'CNAME',
            'name': name,
            'content': target,
            'ttl': ttl or self._ttl,
            'proxied': proxied if proxied is not None else self._proxied
        })
        return self

    def mx_record(self, name: str, mail_server: str, priority: int = 10, ttl: Optional[int] = None) -> 'DNS':
        """
        Add an MX record

        Args:
            name: Record name (usually "@" for root domain)
            mail_server: Mail server hostname
            priority: Priority (lower numbers have higher priority)
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'MX',
            'name': name,
            'content': mail_server,
            'priority': priority,
            'ttl': ttl or self._ttl,
            'proxied': False  # MX records cannot be proxied
        })
        return self

    def txt_record(self, name: str, content: str, ttl: Optional[int] = None) -> 'DNS':
        """
        Add a TXT record

        Args:
            name: Record name (use "@" for root domain)
            content: Text content
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'TXT',
            'name': name,
            'content': content,
            'ttl': ttl or self._ttl,
            'proxied': False  # TXT records cannot be proxied
        })
        return self

    def ns_record(self, name: str, nameserver: str, ttl: Optional[int] = None) -> 'DNS':
        """
        Add an NS record

        Args:
            name: Record name
            nameserver: Nameserver hostname
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'NS',
            'name': name,
            'content': nameserver,
            'ttl': ttl or self._ttl,
            'proxied': False  # NS records cannot be proxied
        })
        return self

    def srv_record(self, name: str, target: str, port: int, priority: int = 0, weight: int = 5, ttl: Optional[int] = None) -> 'DNS':
        """
        Add an SRV record

        Args:
            name: Service name (e.g., "_sip._tcp")
            target: Target hostname
            port: Port number
            priority: Priority (lower numbers have higher priority)
            weight: Weight for same priority records
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'SRV',
            'name': name,
            'content': target,
            'port': port,
            'priority': priority,
            'weight': weight,
            'ttl': ttl or self._ttl,
            'proxied': False  # SRV records cannot be proxied
        })
        return self

    def caa_record(self, name: str, flags: int, tag: str, value: str, ttl: Optional[int] = None) -> 'DNS':
        """
        Add a CAA record

        Args:
            name: Record name (usually "@" for root domain)
            flags: Flags (0 or 128)
            tag: Tag (issue, issuewild, or iodef)
            value: Certificate authority or email
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            DNS: Self for method chaining
        """
        self.records.append({
            'type': 'CAA',
            'name': name,
            'flags': flags,
            'tag': tag,
            'value': value,
            'ttl': ttl or self._ttl,
            'proxied': False  # CAA records cannot be proxied
        })
        return self

    # Convenience methods for common setups
    def web_app(self, ip: str) -> 'DNS':
        """
        Quick setup for a web application (@ and www records)

        Args:
            ip: IP address for the web server

        Returns:
            DNS: Self for method chaining
        """
        return self.a_record("@", ip, proxied=True).a_record("www", ip, proxied=True)

    def mail_setup(self, mail_server: str, priority: int = 10) -> 'DNS':
        """
        Quick setup for email (MX and common TXT records)

        Args:
            mail_server: Mail server hostname
            priority: MX record priority

        Returns:
            DNS: Self for method chaining
        """
        return self.mx_record("@", mail_server, priority)

    def google_workspace(self) -> 'DNS':
        """
        Quick setup for Google Workspace

        Returns:
            DNS: Self for method chaining
        """
        return (self
                .mx_record("@", "smtp.gmail.com", 1)
                .txt_record("@", "v=spf1 include:_spf.google.com ~all")
                .cname_record("mail", "ghs.googlehosted.com"))

    def preview(self) -> Dict[str, Any]:
        """Preview the DNS records that will be created"""
        self._ensure_authenticated()

        return self._format_response("preview", {
            "domain": self.domain,
            "records_count": len(self.records),
            "records": self.records,
            "default_ttl": self._ttl,
            "default_proxied": self._proxied
        })

    def create(self) -> Dict[str, Any]:
        """Create the DNS records"""
        self._ensure_authenticated()

        try:
            results = []
            for record in self.records:
                result = self.dns_manager.create_record(self.domain, record)
                results.append(result)

            return self._format_response("create", {
                "domain": self.domain,
                "records_created": len(results),
                "results": results
            })
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete DNS records for this domain"""
        self._ensure_authenticated()

        try:
            result = self.dns_manager.delete_domain_records(self.domain)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get current DNS status for the domain"""
        self._ensure_authenticated()

        try:
            status = self.dns_manager.get_domain_status(self.domain)
            return self._format_response("status", status)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def list_records(self) -> Dict[str, Any]:
        """List all existing DNS records for the domain"""
        self._ensure_authenticated()

        try:
            records = self.dns_manager.list_records(self.domain)
            return self._format_response("list", {
                "domain": self.domain,
                "records": records
            })
        except Exception as e:
            return self._format_error_response("list", str(e))
