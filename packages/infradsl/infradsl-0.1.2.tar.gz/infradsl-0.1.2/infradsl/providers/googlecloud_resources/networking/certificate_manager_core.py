"""
GCP Certificate Manager Core Implementation

Core attributes and authentication for Google Cloud Certificate Manager.
Provides the foundation for the modular SSL/TLS certificate management system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class CertificateManagerCore(BaseGcpResource):
    """
    Core class for Google Cloud Certificate Manager functionality.
    
    This class provides:
    - Basic certificate attributes and configuration
    - Authentication setup
    - Common utilities for certificate operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Certificate Manager core with certificate name"""
        super().__init__(name)
        
        # Core certificate attributes
        self.cert_name = name
        self.certificate_description = f"SSL certificate for {name}"
        self.certificate_resource_name = None
        self.certificate_id = None
        
        # Certificate type and data
        self.managed_certificate = True  # True for Google-managed, False for self-managed
        self.domain_names = []
        self.certificate_pem = None
        self.private_key_pem = None
        
        # Scope and location
        self.certificate_location = "global"  # global or regional
        self.certificate_scope = "DEFAULT"    # DEFAULT or EDGE_CACHE
        
        # Labels and metadata
        self.certificate_labels = {}
        self.certificate_annotations = {}
        
        # State tracking
        self.certificate_exists = False
        self.certificate_created = False
        self.certificate_status = None
        self.provisioning_issues = []
        
        # Validation and expiry
        self.validation_method = "DNS"  # DNS or HTTP
        self.certificate_expiry = None
        self.renewal_enabled = True
        
        # Client reference
        self.cert_manager_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "Free"
        
    def _initialize_managers(self):
        """Initialize Certificate Manager-specific managers"""
        self.cert_manager_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import certificatemanager_v1
            
            # Initialize client
            self.cert_manager_client = certificatemanager_v1.CertificateManagerClient(
                credentials=self.gcp_client.credentials
            )
            
            # Set project context
            self.project_id = self.project_id or self.gcp_client.project_id
            
            # Generate resource names
            if self.project_id:
                self.certificate_resource_name = f"projects/{self.project_id}/locations/{self.certificate_location}/certificates/{self.cert_name}"
                
        except Exception as e:
            print(f"⚠️  Failed to initialize Certificate Manager client: {str(e)}")
            
    def _is_valid_certificate_name(self, name: str) -> bool:
        """Check if certificate name is valid"""
        import re
        # Certificate names must contain only letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 63
        
    def _is_valid_domain_name(self, domain: str) -> bool:
        """Check if domain name is valid"""
        import re
        # Basic domain validation
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        return bool(re.match(pattern, domain)) and len(domain) <= 253
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if certificate location is valid"""
        valid_locations = [
            "global",  # Global scope
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-north1", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        ]
        return location in valid_locations
        
    def _validate_certificate_config(self, config: Dict[str, Any]) -> bool:
        """Validate certificate configuration"""
        required_fields = ["cert_name"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate certificate name format
        if not self._is_valid_certificate_name(config["cert_name"]):
            return False
            
        # Validate domain names if provided
        domain_names = config.get("domain_names", [])
        if domain_names:
            for domain in domain_names:
                if not self._is_valid_domain_name(domain):
                    return False
                    
        # Validate location if specified
        if config.get("location") and not self._is_valid_location(config["location"]):
            return False
            
        # Validate certificate type requirements
        if config.get("managed_certificate", True):
            # Managed certificates require domain names
            if not domain_names:
                return False
        else:
            # Self-managed certificates require PEM data
            if not config.get("certificate_pem") or not config.get("private_key_pem"):
                return False
                
        return True
        
    def _get_certificate_type_from_config(self) -> str:
        """Determine certificate type from configuration"""
        if self.managed_certificate:
            if len(self.domain_names) == 1:
                domain = self.domain_names[0]
                if domain.startswith("*."):
                    return "wildcard"
                elif domain.startswith("api."):
                    return "api"
                elif domain.startswith("www.") or any(d.startswith("www.") for d in self.domain_names):
                    return "webapp"
                else:
                    return "single_domain"
            elif len(self.domain_names) > 1:
                return "multi_domain"
            else:
                return "managed"
        else:
            return "self_managed"
            
    def _estimate_certificate_cost(self) -> float:
        """Estimate monthly cost for Certificate Manager usage"""
        # Google-managed certificates are free
        if self.managed_certificate:
            return 0.0
        else:
            # Self-managed certificates have minimal management costs
            return 0.10
            
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Certificate Manager from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if certificate exists
            try:
                certificate = self.cert_manager_client.get_certificate(name=self.certificate_resource_name)
                certificate_exists = True
            except Exception:
                certificate_exists = False
                
            if not certificate_exists:
                return {
                    "exists": False,
                    "cert_name": self.cert_name,
                    "certificate_resource_name": self.certificate_resource_name
                }
                
            # Get certificate details
            current_state = {
                "exists": True,
                "cert_name": self.cert_name,
                "certificate_resource_name": certificate.name,
                "description": certificate.description or "",
                "labels": dict(certificate.labels) if certificate.labels else {},
                "location": self.certificate_location,
                "scope": str(certificate.scope).replace('Scope.', '') if certificate.scope else 'DEFAULT',
                "create_time": certificate.create_time.isoformat() if hasattr(certificate, 'create_time') else None,
                "update_time": certificate.update_time.isoformat() if hasattr(certificate, 'update_time') else None,
                "certificate_type": "unknown",
                "domains": [],
                "status": "unknown",
                "provisioning_issues": [],
                "expiry_time": None,
                "auto_renewal": False
            }
            
            # Determine certificate type and extract details
            if hasattr(certificate, 'managed') and certificate.managed:
                current_state["certificate_type"] = "google_managed"
                current_state["auto_renewal"] = True
                current_state["domains"] = list(certificate.managed.domains) if certificate.managed.domains else []
                
                # Get provisioning status
                if hasattr(certificate.managed, 'state'):
                    state_map = {
                        'PROVISIONING': 'provisioning',
                        'FAILED': 'failed', 
                        'ACTIVE': 'active'
                    }
                    state_str = str(certificate.managed.state).replace('State.', '')
                    current_state["status"] = state_map.get(state_str, state_str.lower())
                
                # Check for provisioning issues
                if hasattr(certificate.managed, 'provisioning_issue') and certificate.managed.provisioning_issue:
                    issue = certificate.managed.provisioning_issue
                    current_state["provisioning_issues"].append({
                        'type': str(issue.type_),
                        'details': issue.details
                    })
                    
            elif hasattr(certificate, 'self_managed') and certificate.self_managed:
                current_state["certificate_type"] = "self_managed"
                current_state["auto_renewal"] = False
                current_state["status"] = "active"
                
                # Try to extract domains from certificate (would require parsing PEM)
                # For now, we'll leave domains empty for self-managed certs
                
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Certificate Manager state: {str(e)}")
            return {
                "exists": False,
                "cert_name": self.cert_name,
                "certificate_resource_name": self.certificate_resource_name,
                "error": str(e)
            }
            
    def _discover_existing_certificates(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing certificates in the project"""
        existing_certificates = {}
        
        try:
            from google.cloud import certificatemanager_v1
            
            parent = f"projects/{self.project_id}/locations/{self.certificate_location}"
            
            # List all certificates in the location
            request = certificatemanager_v1.ListCertificatesRequest(parent=parent)
            page_result = self.cert_manager_client.list_certificates(request=request)
            
            for certificate in page_result:
                cert_name = certificate.name.split('/')[-1]
                
                try:
                    # Get basic certificate information
                    cert_info = {
                        "cert_name": cert_name,
                        "full_name": certificate.name,
                        "description": certificate.description or "",
                        "labels": dict(certificate.labels) if certificate.labels else {},
                        "location": self.certificate_location,
                        "scope": str(certificate.scope).replace('Scope.', '') if certificate.scope else 'DEFAULT',
                        "create_time": certificate.create_time.isoformat() if hasattr(certificate, 'create_time') else None,
                        "certificate_type": "unknown",
                        "domains": [],
                        "domain_count": 0,
                        "status": "unknown",
                        "auto_renewal": False,
                        "provisioning_issues": []
                    }
                    
                    # Extract type-specific details
                    if hasattr(certificate, 'managed') and certificate.managed:
                        cert_info["certificate_type"] = "google_managed"
                        cert_info["auto_renewal"] = True
                        cert_info["domains"] = list(certificate.managed.domains) if certificate.managed.domains else []
                        cert_info["domain_count"] = len(cert_info["domains"])
                        
                        # Get status
                        if hasattr(certificate.managed, 'state'):
                            state_str = str(certificate.managed.state).replace('State.', '')
                            cert_info["status"] = state_str.lower()
                        
                        # Get provisioning issues
                        if hasattr(certificate.managed, 'provisioning_issue') and certificate.managed.provisioning_issue:
                            issue = certificate.managed.provisioning_issue
                            cert_info["provisioning_issues"].append({
                                'type': str(issue.type_),
                                'details': issue.details
                            })
                            
                    elif hasattr(certificate, 'self_managed') and certificate.self_managed:
                        cert_info["certificate_type"] = "self_managed"
                        cert_info["auto_renewal"] = False
                        cert_info["status"] = "active"
                        
                    existing_certificates[cert_name] = cert_info
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for certificate {cert_name}: {str(e)}")
                    existing_certificates[cert_name] = {
                        "cert_name": cert_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing certificates: {str(e)}")
            
        return existing_certificates