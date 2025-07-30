"""
Cloudflare Firewall Manager

Handles Cloudflare Web Application Firewall (WAF) operations.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List


class FirewallManager:
    """
    Manager for Cloudflare Web Application Firewall operations.
    """

    def __init__(self):
        """Initialize Firewall manager"""
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.api_email = os.getenv("CLOUDFLARE_EMAIL")
        self.api_key = os.getenv("CLOUDFLARE_API_KEY")
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        if not (self.api_token or (self.api_email and self.api_key)):
            raise ValueError("Cloudflare authentication required. Set CLOUDFLARE_API_TOKEN or CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY")

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.api_token:
            return {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "X-Auth-Email": self.api_email,
                "X-Auth-Key": self.api_key,
                "Content-Type": "application/json"
            }

    def _get_zone_id(self, domain: str) -> str:
        """Get zone ID for domain"""
        response = requests.get(
            f"{self.base_url}/zones",
            headers=self._get_headers(),
            params={"name": domain}
        )
        response.raise_for_status()
        
        data = response.json()
        if not data["result"]:
            raise ValueError(f"Zone not found for domain: {domain}")
        
        return data["result"][0]["id"]

    def set_security_level(self, domain: str, security_level: str) -> Dict[str, Any]:
        """
        Set security level for the zone

        Args:
            domain: Domain name
            security_level: Security level ("off", "essentially_off", "low", "medium", "high", "under_attack")

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.patch(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers(),
            json={"value": security_level}
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Security level set to {security_level}",
            "data": response.json()
        }

    def create_firewall_rule(self, domain: str, expression: str, action: str, description: str = "") -> Dict[str, Any]:
        """
        Create a custom firewall rule

        Args:
            domain: Domain name
            expression: Firewall rule expression
            action: Action to take
            description: Rule description

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        # First create the filter
        filter_response = requests.post(
            f"{self.base_url}/zones/{zone_id}/filters",
            headers=self._get_headers(),
            json={
                "expression": expression,
                "description": description or f"Custom rule: {expression}"
            }
        )
        filter_response.raise_for_status()
        filter_id = filter_response.json()["result"]["id"]
        
        # Then create the firewall rule
        rule_response = requests.post(
            f"{self.base_url}/zones/{zone_id}/firewall/rules",
            headers=self._get_headers(),
            json={
                "filter": {"id": filter_id},
                "action": action,
                "description": description or f"Custom rule: {expression}"
            }
        )
        rule_response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Firewall rule created: {description or expression}",
            "data": {
                "filter": filter_response.json(),
                "rule": rule_response.json()
            }
        }

    def create_rate_limit_rule(self, domain: str, path: str, threshold: int, period: int, action: str) -> Dict[str, Any]:
        """
        Create a rate limiting rule

        Args:
            domain: Domain name
            path: Path pattern
            threshold: Request threshold
            period: Time period in seconds
            action: Action when threshold exceeded

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.post(
            f"{self.base_url}/zones/{zone_id}/rate_limits",
            headers=self._get_headers(),
            json={
                "match": {
                    "request": {
                        "url": f"*{domain}{path}*"
                    }
                },
                "threshold": threshold,
                "period": period,
                "action": {
                    "mode": action,
                    "timeout": 60
                },
                "description": f"Rate limit for {path}"
            }
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Rate limit rule created for {path}",
            "data": response.json()
        }

    def block_countries(self, domain: str, countries: List[str]) -> Dict[str, Any]:
        """
        Block traffic from specific countries

        Args:
            domain: Domain name
            countries: List of country codes

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        # Create expression for country blocking
        country_list = " or ".join([f'ip.geoip.country == "{country}"' for country in countries])
        expression = f"({country_list})"
        
        return self.create_firewall_rule(
            domain,
            expression,
            "block",
            f"Block countries: {', '.join(countries)}"
        )

    def block_ips(self, domain: str, ip_addresses: List[str]) -> Dict[str, Any]:
        """
        Block specific IP addresses

        Args:
            domain: Domain name
            ip_addresses: List of IP addresses

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        # Create expression for IP blocking
        ip_list = " or ".join([f'ip.src == {ip}' for ip in ip_addresses])
        expression = f"({ip_list})"
        
        return self.create_firewall_rule(
            domain,
            expression,
            "block",
            f"Block IPs: {', '.join(ip_addresses)}"
        )

    def allow_ips(self, domain: str, ip_addresses: List[str]) -> Dict[str, Any]:
        """
        Allow specific IP addresses (whitelist)

        Args:
            domain: Domain name
            ip_addresses: List of IP addresses

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        # Create expression for IP allowing
        ip_list = " or ".join([f'ip.src == {ip}' for ip in ip_addresses])
        expression = f"({ip_list})"
        
        return self.create_firewall_rule(
            domain,
            expression,
            "allow",
            f"Allow IPs: {', '.join(ip_addresses)}"
        )

    def get_firewall_rules(self, domain: str) -> Dict[str, Any]:
        """
        Get all firewall rules for a domain

        Args:
            domain: Domain name

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.get(
            f"{self.base_url}/zones/{zone_id}/firewall/rules",
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }

    def delete_firewall_rule(self, domain: str, rule_id: str) -> Dict[str, Any]:
        """
        Delete a firewall rule

        Args:
            domain: Domain name
            rule_id: Rule ID to delete

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.delete(
            f"{self.base_url}/zones/{zone_id}/firewall/rules/{rule_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Firewall rule {rule_id} deleted",
            "data": response.json()
        }

    def get_security_settings(self, domain: str) -> Dict[str, Any]:
        """
        Get security settings for a domain

        Args:
            domain: Domain name

        Returns:
            Dict containing security settings
        """
        zone_id = self._get_zone_id(domain)
        
        # Get security level
        security_response = requests.get(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers()
        )
        security_response.raise_for_status()
        
        # Get challenge passage
        challenge_response = requests.get(
            f"{self.base_url}/zones/{zone_id}/settings/challenge_ttl",
            headers=self._get_headers()
        )
        challenge_response.raise_for_status()
        
        return {
            "success": True,
            "data": {
                "security_level": security_response.json(),
                "challenge_ttl": challenge_response.json()
            }
        }

    def enable_managed_rules(self, domain: str, rule_ids: List[str]) -> Dict[str, Any]:
        """
        Enable managed firewall rules

        Args:
            domain: Domain name
            rule_ids: List of managed rule IDs

        Returns:
            Dict containing the response
        """
        results = []
        for rule_id in rule_ids:
            try:
                result = self.create_firewall_rule(
                    domain,
                    f'cf.waf.rule_id == "{rule_id}"',
                    "block",
                    f"Managed rule: {rule_id}"
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "rule_id": rule_id
                })
        
        return {
            "success": True,
            "message": f"Processed {len(rule_ids)} managed rules",
            "data": results
        }

    def preview_configuration(self, domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview firewall configuration

        Args:
            domain: Domain name
            config: Firewall configuration

        Returns:
            Dict containing preview information
        """
        return {
            "domain": domain,
            "security_level": config.get("security_level", "medium"),
            "managed_rules": config.get("managed_rules", []),
            "custom_rules": config.get("custom_rules", []),
            "rate_limit_rules": config.get("rate_limit_rules", []),
            "blocked_countries": config.get("blocked_countries", []),
            "blocked_ips": config.get("blocked_ips", []),
            "allowed_ips": config.get("allowed_ips", []),
            "estimated_rules": len(config.get("custom_rules", [])) + len(config.get("managed_rules", []))
        } 