"""
Cloudflare SSL Manager

Handles SSL/TLS certificate operations with the Cloudflare API.
Provides methods for creating, managing, and monitoring SSL certificates.
"""

import os
import requests
from typing import Dict, Any, List, Optional


class SSLManager:
    """Manager for Cloudflare SSL/TLS operations"""

    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.api_key = os.getenv('CLOUDFLARE_API_KEY')
        self.email = os.getenv('CLOUDFLARE_EMAIL')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for authentication"""
        if self.api_token:
            return {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        elif self.api_key and self.email:
            return {
                "X-Auth-Key": self.api_key,
                "X-Auth-Email": self.email,
                "Content-Type": "application/json"
            }
        else:
            raise ValueError("Cloudflare authentication credentials not found")

    def _get_zone_id(self, domain: str) -> str:
        """Get zone ID for a domain"""
        if self.zone_id:
            return self.zone_id
        
        headers = self._get_headers()
        response = requests.get(
            f"{self.base_url}/zones",
            headers=headers,
            params={"name": domain}
        )
        
        if response.status_code == 200:
            zones = response.json()["result"]
            if zones:
                return zones[0]["id"]
        
        raise ValueError(f"Zone not found for domain: {domain}")

    def create_ssl_configuration(self, domain: str, certificate_type: str, 
                                 min_tls_version: str, cipher_suites: List[str],
                                 hostnames: List[str], ssl_mode: str,
                                 always_use_https: bool, hsts_enabled: bool,
                                 hsts_max_age: int, hsts_include_subdomains: bool) -> Dict[str, Any]:
        """Create SSL configuration"""
        try:
            zone_id = self._get_zone_id(domain)
            headers = self._get_headers()
            
            # Configure SSL mode
            ssl_response = requests.patch(
                f"{self.base_url}/zones/{zone_id}/settings/ssl",
                headers=headers,
                json={"value": ssl_mode}
            )
            
            # Configure minimum TLS version
            tls_response = requests.patch(
                f"{self.base_url}/zones/{zone_id}/settings/min_tls_version",
                headers=headers,
                json={"value": min_tls_version}
            )
            
            # Configure Always Use HTTPS
            if always_use_https:
                https_response = requests.patch(
                    f"{self.base_url}/zones/{zone_id}/settings/always_use_https",
                    headers=headers,
                    json={"value": "on"}
                )
            
            # Configure HSTS
            if hsts_enabled:
                hsts_response = requests.patch(
                    f"{self.base_url}/zones/{zone_id}/settings/security_header",
                    headers=headers,
                    json={
                        "value": {
                            "strict_transport_security": {
                                "enabled": True,
                                "max_age": hsts_max_age,
                                "include_subdomains": hsts_include_subdomains
                            }
                        }
                    }
                )
            
            # Create certificate based on type
            cert_response = None
            if certificate_type == "advanced":
                cert_response = self._create_advanced_certificate(zone_id, hostnames, headers)
            elif certificate_type == "origin":
                cert_response = self._create_origin_certificate(hostnames, headers)
            elif certificate_type == "dedicated":
                cert_response = self._create_dedicated_certificate(zone_id, headers)
            
            return {
                "domain": domain,
                "zone_id": zone_id,
                "certificate_type": certificate_type,
                "ssl_mode": ssl_mode,
                "min_tls_version": min_tls_version,
                "always_use_https": always_use_https,
                "hsts_enabled": hsts_enabled,
                "certificate_info": cert_response.json() if cert_response else None,
                "status": "configured"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create SSL configuration: {str(e)}")

    def _create_advanced_certificate(self, zone_id: str, hostnames: List[str], headers: Dict[str, str]) -> requests.Response:
        """Create advanced certificate"""
        return requests.post(
            f"{self.base_url}/zones/{zone_id}/ssl/certificate_packs",
            headers=headers,
            json={
                "type": "advanced",
                "hosts": hostnames if hostnames else None
            }
        )

    def _create_origin_certificate(self, hostnames: List[str], headers: Dict[str, str]) -> requests.Response:
        """Create origin certificate"""
        return requests.post(
            f"{self.base_url}/certificates",
            headers=headers,
            json={
                "hostnames": hostnames,
                "requested_validity": 365,
                "request_type": "origin-rsa"
            }
        )

    def _create_dedicated_certificate(self, zone_id: str, headers: Dict[str, str]) -> requests.Response:
        """Create dedicated certificate"""
        return requests.post(
            f"{self.base_url}/zones/{zone_id}/ssl/certificate_packs",
            headers=headers,
            json={"type": "dedicated"}
        )

    def delete_ssl_configuration(self, domain: str) -> Dict[str, Any]:
        """Delete SSL configuration"""
        try:
            zone_id = self._get_zone_id(domain)
            headers = self._get_headers()
            
            # Reset SSL mode to off
            requests.patch(
                f"{self.base_url}/zones/{zone_id}/settings/ssl",
                headers=headers,
                json={"value": "off"}
            )
            
            # Disable Always Use HTTPS
            requests.patch(
                f"{self.base_url}/zones/{zone_id}/settings/always_use_https",
                headers=headers,
                json={"value": "off"}
            )
            
            return {
                "domain": domain,
                "zone_id": zone_id,
                "status": "ssl_disabled"
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete SSL configuration: {str(e)}")

    def get_ssl_status(self, domain: str) -> Dict[str, Any]:
        """Get SSL status"""
        try:
            zone_id = self._get_zone_id(domain)
            headers = self._get_headers()
            
            # Get SSL settings
            ssl_response = requests.get(
                f"{self.base_url}/zones/{zone_id}/settings/ssl",
                headers=headers
            )
            
            # Get TLS settings
            tls_response = requests.get(
                f"{self.base_url}/zones/{zone_id}/settings/min_tls_version",
                headers=headers
            )
            
            # Get HTTPS settings
            https_response = requests.get(
                f"{self.base_url}/zones/{zone_id}/settings/always_use_https",
                headers=headers
            )
            
            # Get certificates
            certs_response = requests.get(
                f"{self.base_url}/zones/{zone_id}/ssl/certificate_packs",
                headers=headers
            )
            
            return {
                "domain": domain,
                "zone_id": zone_id,
                "ssl_mode": ssl_response.json()["result"]["value"] if ssl_response.status_code == 200 else "unknown",
                "min_tls_version": tls_response.json()["result"]["value"] if tls_response.status_code == 200 else "unknown",
                "always_use_https": https_response.json()["result"]["value"] if https_response.status_code == 200 else "unknown",
                "certificates": certs_response.json()["result"] if certs_response.status_code == 200 else [],
                "status": "active"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get SSL status: {str(e)}")

    def renew_certificate(self, domain: str) -> Dict[str, Any]:
        """Renew SSL certificate"""
        try:
            zone_id = self._get_zone_id(domain)
            headers = self._get_headers()
            
            # Get current certificates
            certs_response = requests.get(
                f"{self.base_url}/zones/{zone_id}/ssl/certificate_packs",
                headers=headers
            )
            
            if certs_response.status_code == 200:
                certificates = certs_response.json()["result"]
                renewed_certs = []
                
                for cert in certificates:
                    if cert["type"] != "universal":  # Can't renew universal certificates
                        renew_response = requests.patch(
                            f"{self.base_url}/zones/{zone_id}/ssl/certificate_packs/{cert['id']}",
                            headers=headers,
                            json={"request_type": "renewal"}
                        )
                        
                        if renew_response.status_code == 200:
                            renewed_certs.append(cert["id"])
                
                return {
                    "domain": domain,
                    "zone_id": zone_id,
                    "renewed_certificates": renewed_certs,
                    "status": "renewed"
                }
            else:
                raise Exception("Failed to get current certificates")
                
        except Exception as e:
            raise Exception(f"Failed to renew certificate: {str(e)}") 