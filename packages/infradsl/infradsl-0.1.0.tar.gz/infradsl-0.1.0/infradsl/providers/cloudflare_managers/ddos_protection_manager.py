"""
Cloudflare DDoS Protection Manager

Handles Cloudflare DDoS Protection operations.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List


class DDOSProtectionManager:
    """
    Manager for Cloudflare DDoS Protection operations.
    """

    def __init__(self):
        """Initialize DDoS Protection manager"""
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

    def set_ddos_sensitivity(self, domain: str, sensitivity: str) -> Dict[str, Any]:
        """
        Set DDoS protection sensitivity

        Args:
            domain: Domain name
            sensitivity: Sensitivity level ("low", "medium", "high", "off")

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        # Map sensitivity to Cloudflare's security level setting
        sensitivity_mapping = {
            "off": "off",
            "low": "low", 
            "medium": "medium",
            "high": "high"
        }
        
        cf_level = sensitivity_mapping.get(sensitivity, "medium")
        
        response = requests.patch(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers(),
            json={"value": cf_level}
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"DDoS sensitivity set to {sensitivity}",
            "data": response.json()
        }

    def enable_under_attack_mode(self, domain: str) -> Dict[str, Any]:
        """
        Enable "Under Attack" mode for maximum DDoS protection

        Args:
            domain: Domain name

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.patch(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers(),
            json={"value": "under_attack"}
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Under Attack mode enabled - maximum DDoS protection active",
            "data": response.json()
        }

    def disable_under_attack_mode(self, domain: str) -> Dict[str, Any]:
        """
        Disable "Under Attack" mode

        Args:
            domain: Domain name

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.patch(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers(),
            json={"value": "medium"}
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Under Attack mode disabled - normal protection resumed",
            "data": response.json()
        }

    def set_browser_integrity_check(self, domain: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable/disable browser integrity check

        Args:
            domain: Domain name
            enabled: Whether to enable browser integrity check

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.patch(
            f"{self.base_url}/zones/{zone_id}/settings/browser_check",
            headers=self._get_headers(),
            json={"value": "on" if enabled else "off"}
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Browser integrity check {'enabled' if enabled else 'disabled'}",
            "data": response.json()
        }

    def create_rate_limiting_rule(self, domain: str, threshold: int, period: int, action: str = "simulate") -> Dict[str, Any]:
        """
        Create a rate limiting rule for DDoS protection

        Args:
            domain: Domain name
            threshold: Request threshold
            period: Time period in seconds
            action: Action to take ("simulate", "ban", "challenge")

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
                        "url": f"*{domain}/*"
                    }
                },
                "threshold": threshold,
                "period": period,
                "action": {
                    "mode": action,
                    "timeout": 600  # 10 minutes
                },
                "description": f"DDoS protection rate limit: {threshold} requests per {period}s"
            }
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"DDoS rate limiting rule created: {threshold} requests per {period}s",
            "data": response.json()
        }

    def create_custom_ddos_rule(self, domain: str, expression: str, action: str, description: str = "") -> Dict[str, Any]:
        """
        Create a custom DDoS protection rule

        Args:
            domain: Domain name
            expression: Rule expression
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
                "description": description or f"DDoS protection rule: {expression}"
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
                "description": description or f"DDoS protection rule: {expression}"
            }
        )
        rule_response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Custom DDoS rule created: {description or expression}",
            "data": {
                "filter": filter_response.json(),
                "rule": rule_response.json()
            }
        }

    def get_ddos_analytics(self, domain: str, since: str = "-1440", until: str = "0") -> Dict[str, Any]:
        """
        Get DDoS analytics for a domain

        Args:
            domain: Domain name
            since: Start time (minutes ago, negative number)
            until: End time (minutes ago, 0 for now)

        Returns:
            Dict containing analytics data
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.get(
            f"{self.base_url}/zones/{zone_id}/analytics/dashboard",
            headers=self._get_headers(),
            params={
                "since": since,
                "until": until
            }
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "DDoS analytics retrieved",
            "data": response.json()
        }

    def get_security_events(self, domain: str, since: str = "-1440", until: str = "0") -> Dict[str, Any]:
        """
        Get security events related to DDoS protection

        Args:
            domain: Domain name
            since: Start time (minutes ago, negative number)
            until: End time (minutes ago, 0 for now)

        Returns:
            Dict containing security events
        """
        zone_id = self._get_zone_id(domain)
        
        response = requests.get(
            f"{self.base_url}/zones/{zone_id}/security/events",
            headers=self._get_headers(),
            params={
                "since": since,
                "until": until
            }
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Security events retrieved",
            "data": response.json()
        }

    def configure_ip_access_rules(self, domain: str, ip_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Configure IP access rules for DDoS protection

        Args:
            domain: Domain name
            ip_rules: List of IP rules with IP and action

        Returns:
            Dict containing the response
        """
        zone_id = self._get_zone_id(domain)
        results = []
        
        for rule in ip_rules:
            ip = rule.get("ip")
            action = rule.get("action", "block")  # block, whitelist, challenge
            
            response = requests.post(
                f"{self.base_url}/zones/{zone_id}/firewall/access_rules/rules",
                headers=self._get_headers(),
                json={
                    "mode": action,
                    "configuration": {
                        "target": "ip",
                        "value": ip
                    },
                    "notes": f"DDoS protection rule for {ip}"
                }
            )
            
            try:
                response.raise_for_status()
                results.append({
                    "success": True,
                    "ip": ip,
                    "action": action,
                    "data": response.json()
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "ip": ip,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Configured {len(ip_rules)} IP access rules",
            "data": results
        }

    def get_ddos_protection_status(self, domain: str) -> Dict[str, Any]:
        """
        Get DDoS protection status for a domain

        Args:
            domain: Domain name

        Returns:
            Dict containing protection status
        """
        zone_id = self._get_zone_id(domain)
        
        # Get security level
        security_response = requests.get(
            f"{self.base_url}/zones/{zone_id}/settings/security_level",
            headers=self._get_headers()
        )
        security_response.raise_for_status()
        
        # Get browser check
        browser_response = requests.get(
            f"{self.base_url}/zones/{zone_id}/settings/browser_check",
            headers=self._get_headers()
        )
        browser_response.raise_for_status()
        
        # Get rate limits
        rate_limit_response = requests.get(
            f"{self.base_url}/zones/{zone_id}/rate_limits",
            headers=self._get_headers()
        )
        rate_limit_response.raise_for_status()
        
        return {
            "success": True,
            "data": {
                "security_level": security_response.json(),
                "browser_integrity_check": browser_response.json(),
                "rate_limits": rate_limit_response.json(),
                "protection_active": security_response.json()["result"]["value"] != "off"
            }
        }

    def delete_ddos_rule(self, domain: str, rule_id: str) -> Dict[str, Any]:
        """
        Delete a DDoS protection rule

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
            "message": f"DDoS protection rule {rule_id} deleted",
            "data": response.json()
        }

    def preview_configuration(self, domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview DDoS protection configuration

        Args:
            domain: Domain name
            config: DDoS protection configuration

        Returns:
            Dict containing preview information
        """
        sensitivity = config.get("sensitivity", "medium")
        threshold = config.get("threshold", 1000)
        custom_rules = config.get("custom_rules", [])
        ip_rules = config.get("ip_rules", [])
        
        return {
            "domain": domain,
            "sensitivity": sensitivity,
            "threshold": threshold,
            "under_attack_mode": sensitivity == "under_attack",
            "custom_rules_count": len(custom_rules),
            "ip_rules_count": len(ip_rules),
            "browser_integrity_check": config.get("browser_integrity_check", True),
            "estimated_protection_level": "High" if sensitivity in ["high", "under_attack"] else "Standard"
        } 