"""
GCP Cloud Storage Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Cloud Storage buckets.
Extends the GCP intelligence base with Cloud Storage-specific capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class CloudStorageIntelligence(GCPIntelligenceBase):
    """Cloud Storage-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(GCPResourceType.CLOUD_STORAGE)
        self.storage_client = None
    
    def _initialize_service_client(self):
        """Initialize Cloud Storage client"""
        try:
            from google.cloud import storage
            self.storage_client = storage.Client()
        except Exception as e:
            print(f"⚠️  Failed to create Cloud Storage client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Cloud Storage buckets"""
        existing_buckets = {}
        
        if not self._get_gcp_client():
            return existing_buckets
        
        try:
            # Mock discovery for demonstration
            # In real implementation would use: self.storage_client.list_buckets()
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Cloud Storage buckets: {str(e)}")
        
        return existing_buckets
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Cloud Storage bucket state"""
        return {
            'name': cloud_state.get('name'),
            'location': cloud_state.get('location'),
            'location_type': cloud_state.get('location_type'),
            'storage_class': cloud_state.get('storage_class'),
            'versioning_enabled': cloud_state.get('versioning', {}).get('enabled', False),
            'uniform_bucket_level_access': cloud_state.get('iam_configuration', {}).get('uniform_bucket_level_access', {}).get('enabled', False),
            'public_access_prevention': cloud_state.get('iam_configuration', {}).get('public_access_prevention', 'inherited'),
            'lifecycle_rules': cloud_state.get('lifecycle', {}).get('rule', []),
            'cors_configuration': cloud_state.get('cors', []),
            'website_configuration': cloud_state.get('website', {}),
            'logging_configuration': cloud_state.get('logging', {}),
            'encryption': cloud_state.get('encryption', {}),
            'retention_policy': cloud_state.get('retention_policy', {}),
            'labels': cloud_state.get('labels', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cloud Storage-specific fingerprint data"""
        fingerprint_data = {}
        
        # Bucket naming pattern
        bucket_name = cloud_state.get('name', '')
        if bucket_name:
            fingerprint_data['naming_pattern'] = {
                'length': len(bucket_name),
                'has_org_prefix': any(bucket_name.startswith(p) for p in ['gs-', 'gcp-', 'google-']),
                'has_env_suffix': any(bucket_name.endswith(s) for s in ['-dev', '-staging', '-prod', '-test']),
                'has_purpose_suffix': any(bucket_name.endswith(s) for s in ['-logs', '-backup', '-data', '-static']),
                'contains_underscore': '_' in bucket_name,
                'is_globally_unique': True  # All GCS bucket names are globally unique
            }
        
        # Location and storage class fingerprint
        location = cloud_state.get('location', '')
        location_type = cloud_state.get('location_type', '')
        storage_class = cloud_state.get('storage_class', 'STANDARD')
        
        fingerprint_data['storage_pattern'] = {
            'location_type': location_type,  # REGION, DUAL_REGION, MULTI_REGION
            'is_multi_regional': location_type == 'MULTI_REGION',
            'is_regional': location_type == 'REGION',
            'is_dual_regional': location_type == 'DUAL_REGION',
            'storage_class': storage_class,
            'is_nearline': storage_class == 'NEARLINE',
            'is_coldline': storage_class == 'COLDLINE',
            'is_archive': storage_class == 'ARCHIVE',
            'location': location
        }
        
        # Security and access control fingerprint
        iam_config = cloud_state.get('iam_configuration', {})
        fingerprint_data['security_pattern'] = {
            'uniform_bucket_level_access': iam_config.get('uniform_bucket_level_access', {}).get('enabled', False),
            'public_access_prevention': iam_config.get('public_access_prevention', 'inherited'),
            'versioning_enabled': cloud_state.get('versioning', {}).get('enabled', False),
            'has_encryption': bool(cloud_state.get('encryption', {}).get('default_kms_key_name')),
            'has_retention_policy': bool(cloud_state.get('retention_policy')),
            'retention_locked': cloud_state.get('retention_policy', {}).get('is_locked', False)
        }
        
        # Feature usage fingerprint
        fingerprint_data['feature_pattern'] = {
            'has_lifecycle_rules': len(cloud_state.get('lifecycle', {}).get('rule', [])) > 0,
            'lifecycle_rule_count': len(cloud_state.get('lifecycle', {}).get('rule', [])),
            'has_cors': len(cloud_state.get('cors', [])) > 0,
            'has_website_config': bool(cloud_state.get('website', {}).get('main_page_suffix')),
            'has_logging': bool(cloud_state.get('logging', {}).get('log_bucket')),
            'has_notification_config': bool(cloud_state.get('notification', {})),
            'has_labels': len(cloud_state.get('labels', {})) > 0,
            'label_count': len(cloud_state.get('labels', {}))
        }
        
        return fingerprint_data
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Cloud Storage-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0  # Cloud Storage changes are generally zero-downtime
        propagation_time = 60  # 1 minute for most changes
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Storage class changes
        current_class = current.get('storage_class', 'STANDARD')
        desired_class = desired.get('storage_class', 'STANDARD')
        
        if current_class != desired_class:
            changes.append("storage_class_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            # Calculate cost impact for different storage classes
            cost_impact += self._estimate_storage_class_cost_impact(current_class, desired_class)
            
            if desired_class in ['NEARLINE', 'COLDLINE', 'ARCHIVE']:
                recommendations.append(f"Changing to {desired_class}: reduced storage cost, higher access cost")
                recommendations.append("Consider lifecycle rules for automatic transitions")
            else:
                recommendations.append("Changing to STANDARD: higher storage cost, lower access cost")
                
            recommendations.append("Storage class changes apply to new objects immediately")
            recommendations.append("Existing objects retain their current storage class")
        
        # 2. Location changes (not possible - would require recreation)
        if current.get('location') != desired.get('location'):
            changes.append("location_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: Location cannot be changed on existing bucket")
            recommendations.append("Requires creating new bucket and migrating data")
            recommendations.append("Consider gsutil or Transfer Service for data migration")
        
        # 3. Versioning changes
        current_versioning = current.get('versioning', {}).get('enabled', False)
        desired_versioning = desired.get('versioning_enabled', False)
        
        if current_versioning != desired_versioning:
            changes.append("versioning_modification")
            
            if desired_versioning and not current_versioning:
                recommendations.append("Enabling versioning will store multiple versions of objects")
                recommendations.append("Monitor storage costs as versions accumulate")
                cost_impact += 25  # Rough estimate for versioning overhead
            else:
                recommendations.append("WARNING: Disabling versioning stops creating new versions")
                recommendations.append("Existing versions will be retained")
        
        # 4. Uniform bucket-level access changes
        current_ubla = current.get('iam_configuration', {}).get('uniform_bucket_level_access', {}).get('enabled', False)
        desired_ubla = desired.get('uniform_bucket_level_access', False)
        
        if current_ubla != desired_ubla:
            changes.append("uniform_bucket_level_access_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            if desired_ubla and not current_ubla:
                recommendations.append("Enabling uniform bucket-level access improves security")
                recommendations.append("WARNING: This will disable ACLs on all objects")
                rollback_complexity = "medium"
            else:
                recommendations.append("Disabling uniform bucket-level access re-enables ACLs")
        
        # 5. Public access prevention changes
        current_pap = current.get('iam_configuration', {}).get('public_access_prevention', 'inherited')
        desired_pap = desired.get('public_access_prevention', 'inherited')
        
        if current_pap != desired_pap:
            changes.append("public_access_prevention_modification")
            
            if desired_pap == 'enforced':
                recommendations.append("Enforcing public access prevention improves security")
                recommendations.append("Prevents making bucket or objects publicly accessible")
            elif desired_pap == 'inherited' and current_pap == 'enforced':
                recommendations.append("WARNING: Allowing public access increases security risk")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
        
        # 6. Lifecycle rule changes
        current_lifecycle = current.get('lifecycle', {}).get('rule', [])
        desired_lifecycle = desired.get('lifecycle_rules', [])
        
        if current_lifecycle != desired_lifecycle:
            changes.append("lifecycle_rules_modification")
            
            if desired_lifecycle and not current_lifecycle:
                recommendations.append("Adding lifecycle rules can significantly reduce storage costs")
                cost_impact -= 30  # Potential cost savings
            elif not desired_lifecycle and current_lifecycle:
                recommendations.append("Removing lifecycle rules may increase storage costs")
                cost_impact += 30
            
            recommendations.append("Lifecycle rules take effect within 24 hours")
        
        # 7. CORS configuration changes
        current_cors = current.get('cors', [])
        desired_cors = desired.get('cors_configuration', [])
        
        if current_cors != desired_cors:
            changes.append("cors_configuration_modification")
            recommendations.append("CORS changes affect web browser access to bucket")
            recommendations.append("Test cross-origin requests after deployment")
        
        # 8. Website configuration changes
        current_website = current.get('website', {})
        desired_website = desired.get('website_configuration', {})
        
        if current_website != desired_website:
            changes.append("website_configuration_modification")
            
            if desired_website and not current_website:
                recommendations.append("Enabling website hosting requires bucket to be publicly readable")
                recommendations.append("Consider Cloud CDN for better performance")
                affected_resources.append("cloud_cdn")
            elif not desired_website and current_website:
                recommendations.append("Disabling website hosting will break web access")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
        
        # 9. Encryption changes
        current_encryption = current.get('encryption', {})
        desired_encryption = desired.get('encryption', {})
        
        if current_encryption != desired_encryption:
            changes.append("encryption_modification")
            
            current_kms = current_encryption.get('default_kms_key_name')
            desired_kms = desired_encryption.get('default_kms_key_name')
            
            if desired_kms and not current_kms:
                recommendations.append("Enabling customer-managed encryption keys")
                recommendations.append("New objects will use specified KMS key")
                cost_impact += 2  # KMS key usage costs
                affected_resources.append("kms_keys")
            elif not desired_kms and current_kms:
                recommendations.append("Switching to Google-managed encryption")
        
        # 10. Retention policy changes
        current_retention = current.get('retention_policy', {})
        desired_retention = desired.get('retention_policy', {})
        
        if current_retention != desired_retention:
            changes.append("retention_policy_modification")
            
            if desired_retention and not current_retention:
                recommendations.append("Setting retention policy prevents object deletion")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            elif not desired_retention and current_retention:
                if current_retention.get('is_locked'):
                    recommendations.append("CRITICAL: Locked retention policy cannot be removed")
                    impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
                    rollback_complexity = "high"
                else:
                    recommendations.append("Removing retention policy allows object deletion")
        
        # Find affected resources
        bucket_name = current.get('name') or desired.get('name')
        if bucket_name:
            affected_resources.extend([
                f"cloud_functions_triggers_{bucket_name}",
                f"pub_sub_notifications_{bucket_name}",
                f"cloud_cdn_backends_{bucket_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "bucket_configuration_update"
        
        return ChangeImpactAnalysis(
            change_type=change_type,
            impact_level=impact_level,
            estimated_downtime=downtime,
            propagation_time=propagation_time,
            cost_impact=cost_impact,
            affected_resources=affected_resources,
            recommendations=recommendations,
            rollback_complexity=rollback_complexity
        )
    
    def _estimate_storage_class_cost_impact(self, current_class: str, desired_class: str) -> float:
        """Estimate cost impact of storage class changes"""
        
        # Relative cost multipliers for GCS storage classes (storage cost)
        storage_costs = {
            'STANDARD': 1.0,
            'NEARLINE': 0.5,   # ~50% cheaper storage
            'COLDLINE': 0.25,  # ~75% cheaper storage
            'ARCHIVE': 0.12    # ~88% cheaper storage
        }
        
        current_cost = storage_costs.get(current_class, 1.0)
        desired_cost = storage_costs.get(desired_class, 1.0)
        
        # Storage cost impact
        storage_impact = ((desired_cost - current_cost) / current_cost) * 100
        
        # Note: Access costs increase for cooler storage classes, but we focus on storage costs here
        return storage_impact
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Cloud Storage bucket health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Security checks
        iam_config = cloud_state.get('iam_configuration', {})
        
        # Public access prevention
        pap = iam_config.get('public_access_prevention', 'inherited')
        if pap != 'enforced':
            health_score -= 0.2
            issues.append("Public access prevention not enforced (security risk)")
        
        # Uniform bucket-level access
        ubla = iam_config.get('uniform_bucket_level_access', {}).get('enabled', False)
        if not ubla:
            health_score -= 0.1
            issues.append("Uniform bucket-level access not enabled (consider for better security)")
        
        # Versioning
        versioning = cloud_state.get('versioning', {}).get('enabled', False)
        if not versioning:
            health_score -= 0.1
            issues.append("Versioning not enabled (recommended for data protection)")
        
        # Encryption
        encryption = cloud_state.get('encryption', {})
        if not encryption.get('default_kms_key_name'):
            issues.append("Using Google-managed encryption (consider customer-managed keys)")
        else:
            metrics['uses_customer_managed_encryption'] = True
        
        # Lifecycle management
        lifecycle_rules = cloud_state.get('lifecycle', {}).get('rule', [])
        if not lifecycle_rules:
            issues.append("No lifecycle rules configured (consider for cost optimization)")
        else:
            metrics['lifecycle_rule_count'] = len(lifecycle_rules)
        
        # Location and storage class optimization
        location_type = cloud_state.get('location_type', '')
        storage_class = cloud_state.get('storage_class', 'STANDARD')
        
        if location_type == 'MULTI_REGION' and storage_class == 'STANDARD':
            issues.append("Multi-regional STANDARD storage is expensive (consider regional or different storage class)")
        
        if storage_class == 'STANDARD':
            issues.append("Using STANDARD storage class (consider NEARLINE/COLDLINE for infrequent access)")
        
        # Retention policy
        retention_policy = cloud_state.get('retention_policy', {})
        if retention_policy:
            if retention_policy.get('is_locked'):
                metrics['retention_policy_locked'] = True
            else:
                issues.append("Retention policy not locked (consider locking for compliance)")
        else:
            issues.append("No retention policy configured")
        
        # Website configuration security
        website_config = cloud_state.get('website', {})
        if website_config:
            if pap != 'enforced':
                health_score -= 0.2
                issues.append("Website hosting without public access prevention (security risk)")
        
        # CORS configuration
        cors_config = cloud_state.get('cors', [])
        if cors_config:
            # Check for overly permissive CORS
            for cors_rule in cors_config:
                if '*' in cors_rule.get('origin', []):
                    health_score -= 0.1
                    issues.append("CORS allows all origins (*) - consider restricting")
                    break
        
        # Calculate feature metrics
        metrics['security_features'] = sum([
            pap == 'enforced',
            ubla,
            versioning,
            bool(encryption.get('default_kms_key_name')),
            bool(retention_policy)
        ])
        
        metrics['cost_optimization_features'] = sum([
            len(lifecycle_rules) > 0,
            storage_class in ['NEARLINE', 'COLDLINE', 'ARCHIVE'],
            location_type == 'REGION'  # Regional is cheaper than multi-regional
        ])
        
        metrics['management_features'] = sum([
            len(cloud_state.get('labels', {})) > 0,
            bool(cloud_state.get('logging', {}).get('log_bucket')),
            bool(retention_policy)
        ])
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Cloud Storage-specific changes"""
        changes = {}
        
        # Storage class changes
        if current.get('storage_class') != desired.get('storage_class'):
            changes['storage_class'] = {
                'from': current.get('storage_class'),
                'to': desired.get('storage_class'),
                'requires': 'update'
            }
        
        # Versioning changes
        current_versioning = current.get('versioning', {}).get('enabled', False)
        desired_versioning = desired.get('versioning_enabled', False)
        
        if current_versioning != desired_versioning:
            changes['versioning'] = {
                'from': current_versioning,
                'to': desired_versioning,
                'requires': 'update'
            }
        
        # Uniform bucket-level access changes
        current_ubla = current.get('iam_configuration', {}).get('uniform_bucket_level_access', {}).get('enabled', False)
        desired_ubla = desired.get('uniform_bucket_level_access', False)
        
        if current_ubla != desired_ubla:
            changes['uniform_bucket_level_access'] = {
                'from': current_ubla,
                'to': desired_ubla,
                'requires': 'update'
            }
        
        # Public access prevention changes
        current_pap = current.get('iam_configuration', {}).get('public_access_prevention', 'inherited')
        desired_pap = desired.get('public_access_prevention', 'inherited')
        
        if current_pap != desired_pap:
            changes['public_access_prevention'] = {
                'from': current_pap,
                'to': desired_pap,
                'requires': 'update'
            }
        
        # Lifecycle rules changes
        current_lifecycle = current.get('lifecycle', {}).get('rule', [])
        desired_lifecycle = desired.get('lifecycle_rules', [])
        
        if current_lifecycle != desired_lifecycle:
            changes['lifecycle_rules'] = {
                'from': current_lifecycle,
                'to': desired_lifecycle,
                'requires': 'update'
            }
        
        # CORS configuration changes
        if current.get('cors') != desired.get('cors_configuration'):
            changes['cors_configuration'] = {
                'from': current.get('cors'),
                'to': desired.get('cors_configuration'),
                'requires': 'update'
            }
        
        return changes