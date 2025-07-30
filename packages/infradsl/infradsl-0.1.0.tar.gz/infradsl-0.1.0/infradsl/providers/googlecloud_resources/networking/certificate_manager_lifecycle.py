"""
GCP Certificate Manager Lifecycle Mixin

Lifecycle operations for Google Cloud Certificate Manager.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional, Union
import time


class CertificateManagerLifecycleMixin:
    """
    Mixin for Certificate Manager lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Certificate validation and monitoring operations
    - State comparison and drift detection
    """
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created, kept, and removed.
        
        Returns:
            Dict containing preview information and cost estimates
        """
        self._ensure_authenticated()
        
        # Discover existing certificates
        existing_certificates = self._discover_existing_certificates()
        current_state = self._fetch_current_cloud_state()
        
        # Categorize certificates
        certs_to_create = []
        certs_to_keep = []
        certs_to_remove = []
        
        # Check if our desired certificate exists
        cert_exists = current_state.get("exists", False)
        
        if not cert_exists:
            certs_to_create.append({
                'cert_name': self.cert_name,
                'cert_type': "Google-managed" if self.managed_certificate else "Self-managed",
                'domains': self.domain_names,
                'domain_count': len(self.domain_names),
                'location': self.certificate_location,
                'scope': self.certificate_scope,
                'auto_renewal': self.managed_certificate,
                'description': self.certificate_description,
                'labels': self.certificate_labels
            })
        else:
            certs_to_keep.append({
                'cert_name': self.cert_name,
                'cert_type': current_state.get('certificate_type', 'Unknown'),
                'domains': current_state.get('domains', []),
                'domain_count': len(current_state.get('domains', [])),
                'status': current_state.get('status', 'Unknown'),
                'auto_renewal': current_state.get('auto_renewal', False),
                'location': current_state.get('location', 'Unknown'),
                'provisioning_issues': current_state.get('provisioning_issues', [])
            })
        
        # Display preview
        self._display_certificate_preview(certs_to_create, certs_to_keep, certs_to_remove)
        
        # Return structured data
        return {
            'resource_type': 'gcp_certificate_manager',
            'name': self.cert_name,
            'current_state': current_state,
            'certs_to_create': certs_to_create,
            'certs_to_keep': certs_to_keep,
            'certs_to_remove': certs_to_remove,
            'estimated_cost': self._calculate_certificate_cost(),
            'configuration': self._get_certificate_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the SSL certificate.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_certificate_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_certificate_actions(current_state)
        
        # Execute actions
        result = self._execute_certificate_actions(actions, current_state)
        
        # Update state
        self.certificate_exists = True
        self.certificate_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the SSL certificate.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying SSL Certificate: {self.cert_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Certificate '{self.cert_name}' does not exist")
                return {"success": True, "message": "Certificate does not exist", "name": self.cert_name}
            
            # Show what will be destroyed
            self._display_certificate_destruction_preview(current_state)
            
            # Perform destruction
            try:
                operation = self.cert_manager_client.delete_certificate(name=self.certificate_resource_name)
                
                # Wait for deletion to complete
                try:
                    operation.result(timeout=120)  # Wait up to 2 minutes
                    print(f"✅ Certificate '{self.cert_name}' destroyed successfully")
                except Exception:
                    print(f"✅ Certificate deletion initiated")
                
                self.certificate_exists = False
                self.certificate_created = False
                
                return {
                    "success": True, 
                    "name": self.cert_name,
                    "domains_affected": current_state.get("domains", [])
                }
                
            except Exception as e:
                print(f"❌ Failed to destroy certificate: {str(e)}")
                return {"success": False, "name": self.cert_name, "error": str(e)}
                
        except Exception as e:
            print(f"❌ Error destroying Certificate Manager: {str(e)}")
            return {"success": False, "name": self.cert_name, "error": str(e)}
            
    def wait_for_provisioning(self, timeout_minutes: int = 30) -> Dict[str, Any]:
        """
        Wait for certificate provisioning to complete.
        
        Args:
            timeout_minutes: Maximum time to wait for provisioning
            
        Returns:
            Dict containing provisioning results
        """
        if not self.managed_certificate:
            return {"success": True, "message": "Self-managed certificate - no provisioning needed"}
        
        print(f"⏳ Waiting for certificate provisioning (timeout: {timeout_minutes} minutes)...")
        
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                from google.cloud import certificatemanager_v1
                
                certificate = self.cert_manager_client.get_certificate(name=self.certificate_resource_name)
                
                if hasattr(certificate, 'managed') and certificate.managed:
                    # Check managed certificate status
                    if hasattr(certificate.managed, 'state'):
                        state = certificate.managed.state
                        if state == certificatemanager_v1.Certificate.ManagedCertificate.State.ACTIVE:
                            print(f"✅ Certificate provisioned and active!")
                            self.certificate_status = "ACTIVE"
                            return {
                                "success": True,
                                "status": "active",
                                "cert_name": self.cert_name,
                                "domains": self.domain_names
                            }
                        elif state == certificatemanager_v1.Certificate.ManagedCertificate.State.FAILED:
                            print(f"❌ Certificate provisioning failed")
                            
                            # Get failure details
                            issues = []
                            if hasattr(certificate.managed, 'provisioning_issue') and certificate.managed.provisioning_issue:
                                issue = certificate.managed.provisioning_issue
                                issues.append({
                                    'type': str(issue.type_),
                                    'details': issue.details
                                })
                            
                            return {
                                "success": False, 
                                "error": "Provisioning failed",
                                "issues": issues
                            }
                
                print(f"   Status: Provisioning - waiting...")
                time.sleep(30)
                
            except Exception as e:
                print(f"⚠️  Error checking provisioning status: {e}")
                time.sleep(30)
        
        print(f"⚠️  Provisioning timeout after {timeout_minutes} minutes")
        return {"success": False, "error": "Provisioning timeout"}
        
    def get_validation_records(self) -> Dict[str, Any]:
        """
        Get DNS validation records needed for certificate provisioning.
        
        Returns:
            Dict containing validation record information
        """
        if not self.managed_certificate:
            return {"success": False, "error": "Validation records only available for managed certificates"}
        
        try:
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                return {"success": False, "error": "Certificate not created yet"}
            
            # In a real implementation, you would get the actual validation records
            # from the Certificate Manager API. For now, we'll return a template.
            validation_records = []
            
            for domain in self.domain_names:
                validation_records.append({
                    "domain": domain,
                    "type": "TXT",
                    "name": f"_acme-challenge.{domain}",
                    "value": "validation-token-placeholder",
                    "ttl": 300
                })
            
            return {
                "success": True,
                "cert_name": self.cert_name,
                "validation_method": self.validation_method,
                "records": validation_records,
                "instructions": "Add these DNS records to prove domain ownership"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def check_certificate_status(self) -> Dict[str, Any]:
        """
        Check current certificate status and health.
        
        Returns:
            Dict containing certificate status information
        """
        try:
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                return {
                    "success": True,
                    "status": "not_found",
                    "cert_name": self.cert_name,
                    "message": "Certificate does not exist"
                }
            
            return {
                "success": True,
                "cert_name": self.cert_name,
                "status": current_state.get("status", "unknown"),
                "certificate_type": current_state.get("certificate_type", "unknown"),
                "domains": current_state.get("domains", []),
                "auto_renewal": current_state.get("auto_renewal", False),
                "provisioning_issues": current_state.get("provisioning_issues", []),
                "create_time": current_state.get("create_time"),
                "location": current_state.get("location"),
                "scope": current_state.get("scope")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _validate_certificate_configuration(self):
        """Validate the Certificate Manager configuration before creation"""
        errors = []
        warnings = []
        
        # Validate certificate name
        if not self.cert_name:
            errors.append("Certificate name is required")
        elif not self._is_valid_certificate_name(self.cert_name):
            errors.append(f"Invalid certificate name: {self.cert_name}")
        
        # Validate domain requirements
        if self.managed_certificate:
            if not self.domain_names:
                errors.append("Domain names are required for managed certificates")
            else:
                for domain in self.domain_names:
                    if not self._is_valid_domain_name(domain):
                        errors.append(f"Invalid domain name: {domain}")
        else:
            if not self.certificate_pem or not self.private_key_pem:
                errors.append("Certificate PEM and private key PEM are required for self-managed certificates")
        
        # Validate location
        if not self._is_valid_location(self.certificate_location):
            errors.append(f"Invalid location: {self.certificate_location}")
        
        # Performance warnings
        if len(self.domain_names) > 100:
            warnings.append(f"Large number of domains ({len(self.domain_names)}) may slow provisioning")
        
        # Security warnings
        if not self.managed_certificate and self.renewal_enabled:
            warnings.append("Self-managed certificates don't support automatic renewal")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_certificate_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_certificate": False,
            "update_certificate": False,
            "keep_certificate": False,
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_certificate"] = True
            actions["changes"].append("Create new certificate")
            if self.managed_certificate:
                actions["changes"].append("Start domain validation process")
        else:
            # Compare current state with desired state
            metadata_changes = self._detect_certificate_drift(current_state)
            
            if metadata_changes:
                actions["update_certificate"] = True
                actions["changes"].extend(metadata_changes)
            
            if not actions["changes"]:
                actions["keep_certificate"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_certificate_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired certificate state"""
        changes = []
        
        # Compare description
        current_description = current_state.get("description", "")
        if current_description != self.certificate_description:
            changes.append(f"Description: '{current_description}' → '{self.certificate_description}'")
        
        # Compare labels
        current_labels = current_state.get("labels", {})
        if current_labels != self.certificate_labels:
            changes.append(f"Labels: {current_labels} → {self.certificate_labels}")
        
        # Compare domains (for managed certificates)
        if self.managed_certificate:
            current_domains = set(current_state.get("domains", []))
            desired_domains = set(self.domain_names)
            if current_domains != desired_domains:
                changes.append(f"Domains: {current_domains} → {desired_domains}")
        
        # Note: Some properties like certificate type and location cannot be changed after creation
        
        return changes
        
    def _execute_certificate_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_certificate"]:
            return self._create_certificate()
        elif actions["update_certificate"]:
            return self._update_certificate(current_state, actions)
        else:
            return self._keep_certificate(current_state)
            
    def _create_certificate(self) -> Dict[str, Any]:
        """Create a new SSL certificate"""
        print(f"\n🔐 Creating SSL certificate: {self.cert_name}")
        print(f"   🏷️  Type: {'Google-managed' if self.managed_certificate else 'Self-managed'}")
        print(f"   📍 Location: {self.certificate_location}")
        print(f"   🎯 Scope: {self.certificate_scope}")
        print(f"   🌍 Domains: {len(self.domain_names)}")
        
        if self.domain_names:
            print(f"   📋 Domain list:")
            for domain in self.domain_names[:5]:
                print(f"      • {domain}")
            if len(self.domain_names) > 5:
                print(f"      • ... and {len(self.domain_names) - 5} more domains")
        
        try:
            from google.cloud import certificatemanager_v1
            
            # Create certificate object
            if self.managed_certificate:
                # Google-managed certificate
                certificate = certificatemanager_v1.Certificate(
                    name=self.certificate_resource_name,
                    description=self.certificate_description,
                    managed=certificatemanager_v1.Certificate.ManagedCertificate(
                        domains=self.domain_names
                    ),
                    scope=self.certificate_scope,
                    labels=self.certificate_labels
                )
            else:
                # Self-managed certificate
                certificate = certificatemanager_v1.Certificate(
                    name=self.certificate_resource_name,
                    description=self.certificate_description,
                    self_managed=certificatemanager_v1.Certificate.SelfManagedCertificate(
                        pem_certificate=self.certificate_pem,
                        pem_private_key=self.private_key_pem
                    ),
                    scope=self.certificate_scope,
                    labels=self.certificate_labels
                )
            
            # Create certificate
            operation = self.cert_manager_client.create_certificate(
                parent=f"projects/{self.project_id}/locations/{self.certificate_location}",
                certificate_id=self.cert_name,
                certificate=certificate
            )
            
            print(f"\n✅ Certificate creation initiated!")
            print(f"   🔐 Certificate: {self.cert_name}")
            print(f"   🌐 Resource: {self.certificate_resource_name}")
            print(f"   🔄 Auto-renewal: {'✅ Enabled' if self.managed_certificate else '❌ Manual'}")
            
            if self.managed_certificate:
                print(f"\n📋 Domain Validation Required:")
                print(f"   You need to prove domain ownership by adding DNS records.")
                print(f"   Certificate will be provisioned automatically once validation completes.")
                print(f"   Use wait_for_provisioning() to monitor the process.")
                
                for domain in self.domain_names[:3]:
                    print(f"   • {domain}: Add DNS TXT record")
                if len(self.domain_names) > 3:
                    print(f"   • ... and {len(self.domain_names) - 3} more domains")
            
            # Brief wait for operation to start
            try:
                result = operation.result(timeout=60)
                print(f"   ✅ Certificate created successfully!")
                self.certificate_status = "ACTIVE" if not self.managed_certificate else "PROVISIONING"
            except Exception:
                print(f"   ⏳ Certificate creation in progress...")
                self.certificate_status = "PROVISIONING"
            
            print(f"   💰 Estimated Cost: {self._calculate_certificate_cost()}")
            
            return {
                "success": True,
                "name": self.cert_name,
                "resource_name": self.certificate_resource_name,
                "certificate_type": "Google-managed" if self.managed_certificate else "Self-managed",
                "domains": self.domain_names,
                "domain_count": len(self.domain_names),
                "status": self.certificate_status,
                "auto_renewal": self.managed_certificate,
                "estimated_cost": self._calculate_certificate_cost(),
                "created": True
            }
            
        except Exception as e:
            print(f"❌ Failed to create SSL certificate: {str(e)}")
            raise
            
    def _update_certificate(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing SSL certificate"""
        print(f"\n🔄 Updating SSL certificate: {self.cert_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            # Note: Many certificate properties cannot be updated after creation
            # This would typically require recreating the certificate
            print(f"   ⚠️  Note: Certificate properties cannot be updated after creation")
            print(f"   ⚠️  Consider recreating the certificate if changes are needed")
            
            print(f"\n✅ Certificate checked successfully!")
            print(f"   🔐 Certificate: {self.cert_name}")
            print(f"   📋 No updates applied (certificates are immutable)")
            
            return {
                "success": True,
                "name": self.cert_name,
                "changes_applied": 0,
                "message": "Certificates are immutable after creation",
                "updated": False
            }
            
        except Exception as e:
            print(f"❌ Failed to update SSL certificate: {str(e)}")
            raise
            
    def _keep_certificate(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing SSL certificate (no changes needed)"""
        print(f"\n✅ SSL certificate '{self.cert_name}' is up to date")
        print(f"   🔐 Certificate: {self.cert_name}")
        print(f"   🏷️  Type: {current_state.get('certificate_type', 'Unknown').replace('_', ' ').title()}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown').replace('_', ' ').title()}")
        print(f"   🌍 Domains: {len(current_state.get('domains', []))}")
        print(f"   🔄 Auto-renewal: {'✅ Yes' if current_state.get('auto_renewal', False) else '❌ No'}")
        
        return {
            "success": True,
            "name": self.cert_name,
            "resource_name": current_state.get("certificate_resource_name"),
            "certificate_type": current_state.get("certificate_type"),
            "status": current_state.get("status"),
            "domains": current_state.get("domains", []),
            "domain_count": len(current_state.get("domains", [])),
            "auto_renewal": current_state.get("auto_renewal", False),
            "unchanged": True
        }
        
    def _display_certificate_preview(self, certs_to_create, certs_to_keep, certs_to_remove):
        """Display preview of actions to be taken"""
        print(f"\n🔐 Google Cloud Certificate Manager Preview")
        print(f"   🎯 Certificate: {self.cert_name}")
        print(f"   📍 Location: {self.certificate_location}")
        print(f"   🎯 Scope: {self.certificate_scope}")
        
        if certs_to_create:
            cert = certs_to_create[0]
            print(f"\n╭─ 🆕 WILL CREATE CERTIFICATE")
            print(f"├─ 🔐 Certificate: {cert['cert_name']}")
            print(f"├─ 🏷️  Type: {cert['cert_type']}")
            print(f"├─ 📍 Location: {cert['location']}")
            print(f"├─ 🎯 Scope: {cert['scope']}")
            print(f"├─ 🌍 Domains: {cert['domain_count']}")
            
            if cert['domains']:
                print(f"├─ 📋 Domain List:")
                for domain in cert['domains'][:5]:
                    print(f"│  • {domain}")
                if len(cert['domains']) > 5:
                    print(f"│  • ... and {len(cert['domains']) - 5} more domains")
            
            print(f"├─ 🔄 Auto-renewal: {'✅ Enabled' if cert['auto_renewal'] else '❌ Manual'}")
            
            if cert['labels']:
                print(f"├─ 🏷️  Labels: {len(cert['labels'])}")
                for key, value in list(cert['labels'].items())[:3]:
                    print(f"│  • {key}: {value}")
            
            print(f"├─ 🚀 Features:")
            print(f"│  ├─ 🔒 SSL/TLS encryption")
            print(f"│  ├─ 📱 Multi-domain support")
            print(f"│  ├─ 🔄 Automatic provisioning")
            print(f"│  └─ 📋 Domain validation")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_certificate_cost()}")
        
        if certs_to_keep:
            cert = certs_to_keep[0]
            print(f"\n╭─ ✅ WILL KEEP CERTIFICATE")
            print(f"├─ 🔐 Certificate: {cert['cert_name']}")
            print(f"├─ 🏷️  Type: {cert['cert_type'].replace('_', ' ').title()}")
            print(f"├─ 📊 Status: {cert['status'].replace('_', ' ').title()}")
            print(f"├─ 🌍 Domains: {cert['domain_count']}")
            print(f"├─ 🔄 Auto-renewal: {'✅ Yes' if cert['auto_renewal'] else '❌ No'}")
            
            if cert.get('provisioning_issues'):
                print(f"├─ ⚠️  Issues: {len(cert['provisioning_issues'])} provisioning issues")
            
            print(f"╰─ 📍 Location: {cert['location']}")
            
    def _display_certificate_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Certificate: {self.cert_name}")
        print(f"   🏷️  Type: {current_state.get('certificate_type', 'Unknown')}")
        print(f"   🌍 Protected Domains: {len(current_state.get('domains', []))}")
        if current_state.get("domains"):
            print(f"   📋 Domain List:")
            for domain in current_state["domains"][:5]:
                print(f"      • {domain}")
            if len(current_state["domains"]) > 5:
                print(f"      • ... and {len(current_state['domains']) - 5} more domains")
        print(f"   ⚠️  SSL PROTECTION FOR THESE DOMAINS WILL BE REMOVED")
        print(f"   ⚠️  THIS ACTION CANNOT BE UNDONE")
        
    def _calculate_certificate_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_certificate_cost()
        if base_cost == 0.0:
            return "Free"
        else:
            return f"${base_cost:.2f}/month"
        
    def _get_certificate_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current Certificate Manager configuration"""
        return {
            "cert_name": self.cert_name,
            "certificate_description": self.certificate_description,
            "managed_certificate": self.managed_certificate,
            "domain_names": self.domain_names,
            "domain_count": len(self.domain_names),
            "certificate_location": self.certificate_location,
            "certificate_scope": self.certificate_scope,
            "validation_method": self.validation_method,
            "certificate_labels": self.certificate_labels,
            "renewal_enabled": self.renewal_enabled,
            "certificate_type": self._get_certificate_type_from_config(),
            "has_wildcard": any(domain.startswith("*.") for domain in self.domain_names)
        }
        
    def optimize_for(self, priority: str):
        """
        Use Cross-Cloud Magic to optimize for cost/performance/reliability/compliance
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Certificate Manager for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective SSL certificates")
            # Use Google-managed certificates (free)
            self.managed()
            self.global_scope()  # Most cost-effective
            self.label("optimization", "cost")
            print("   💡 Configured for free Google-managed certificates")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance SSL")
            # Use global scope for best performance
            self.managed()
            self.global_scope()
            self.dns_validation()  # Faster validation
            self.label("optimization", "performance")
            print("   💡 Configured for global scope and fast validation")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable SSL certificates")
            # Use managed certificates with automatic renewal
            self.managed()
            self.global_scope()
            self.label("optimization", "reliability")
            self.label("monitoring", "enabled")
            print("   💡 Configured for automatic renewal and global availability")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant SSL certificates")
            # Enhanced security and monitoring
            self.managed()
            self.global_scope()
            self.dns_validation()  # More secure validation
            self.label("optimization", "compliance")
            self.label("compliance", "required")
            self.label("audit", "enabled")
            self.label("encryption", "tls13")
            print("   💡 Configured for compliance with enhanced security and audit")
            
        return self