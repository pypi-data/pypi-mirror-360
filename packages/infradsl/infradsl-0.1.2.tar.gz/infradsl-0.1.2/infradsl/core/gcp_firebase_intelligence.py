"""
GCP Firebase Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Firebase services.
Extends the GCP intelligence base with Firebase-specific capabilities including:
- Firebase Hosting
- Firebase Authentication
- Firestore Database
- Firebase Functions
- Firebase Storage
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class FirebaseIntelligence(GCPIntelligenceBase):
    """Firebase-specific stateless intelligence implementation"""
    
    def __init__(self, firebase_service: str = "hosting"):
        # Map Firebase service to resource type
        service_type_map = {
            "hosting": GCPResourceType.FIREBASE_HOSTING,
            "auth": GCPResourceType.FIREBASE_AUTH,
            "firestore": GCPResourceType.FIRESTORE,
            "functions": GCPResourceType.FIREBASE_FUNCTIONS,
            "storage": GCPResourceType.FIREBASE_STORAGE
        }
        
        resource_type = service_type_map.get(firebase_service, GCPResourceType.FIREBASE_HOSTING)
        super().__init__(resource_type)
        self.firebase_service = firebase_service
        self.firebase_client = None
    
    def _initialize_service_client(self):
        """Initialize Firebase client"""
        try:
            if self.firebase_service == "hosting":
                # Firebase Hosting uses Firebase Admin SDK
                import firebase_admin
                from firebase_admin import credentials, initialize_app
                # In real implementation, would initialize with service account
                self.firebase_client = "hosting_client"
            elif self.firebase_service == "auth":
                from firebase_admin import auth
                self.firebase_client = "auth_client"
            elif self.firebase_service == "firestore":
                from firebase_admin import firestore
                self.firebase_client = "firestore_client"
            elif self.firebase_service == "functions":
                # Firebase Functions use Cloud Functions API
                from google.cloud import functions_v1
                self.firebase_client = functions_v1.CloudFunctionsServiceClient()
            elif self.firebase_service == "storage":
                # Firebase Storage uses Cloud Storage API
                from google.cloud import storage
                self.firebase_client = storage.Client()
        except Exception as e:
            print(f"⚠️  Failed to create Firebase {self.firebase_service} client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firebase resources"""
        existing_resources = {}
        
        if not self._get_gcp_client():
            return existing_resources
        
        try:
            # Mock discovery for demonstration
            # In real implementation would use Firebase Admin SDK or appropriate APIs
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Firebase {self.firebase_service} resources: {str(e)}")
        
        return existing_resources
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Firebase resource state"""
        if self.firebase_service == "hosting":
            return self._extract_hosting_config(cloud_state)
        elif self.firebase_service == "auth":
            return self._extract_auth_config(cloud_state)
        elif self.firebase_service == "firestore":
            return self._extract_firestore_config(cloud_state)
        elif self.firebase_service == "functions":
            return self._extract_functions_config(cloud_state)
        elif self.firebase_service == "storage":
            return self._extract_storage_config(cloud_state)
        else:
            return {}
    
    def _extract_hosting_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Firebase Hosting configuration"""
        return {
            'site_name': cloud_state.get('name'),
            'default_url': cloud_state.get('default_url'),
            'app_id': cloud_state.get('app_id'),
            'type': cloud_state.get('type', 'DEFAULT_SITE'),
            'labels': cloud_state.get('labels', {}),
            'custom_domains': cloud_state.get('custom_domains', []),
            'ssl_config': cloud_state.get('ssl_config', {}),
            'releases': cloud_state.get('releases', []),
            'versions': cloud_state.get('versions', []),
            'channels': cloud_state.get('channels', [])
        }
    
    def _extract_auth_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Firebase Authentication configuration"""
        return {
            'project_id': cloud_state.get('project_id'),
            'sign_in_options': cloud_state.get('sign_in_options', []),
            'authorized_domains': cloud_state.get('authorized_domains', []),
            'quota_config': cloud_state.get('quota_config', {}),
            'monitoring_config': cloud_state.get('monitoring_config', {}),
            'multi_factor_config': cloud_state.get('multi_factor_config', {}),
            'blocking_functions': cloud_state.get('blocking_functions', {}),
            'client_permissions': cloud_state.get('client_permissions', {}),
            'password_policy_config': cloud_state.get('password_policy_config', {}),
            'email_privacy_config': cloud_state.get('email_privacy_config', {}),
            'recaptcha_config': cloud_state.get('recaptcha_config', {})
        }
    
    def _extract_firestore_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Firestore configuration"""
        return {
            'name': cloud_state.get('name'),
            'location_id': cloud_state.get('location_id'),
            'type': cloud_state.get('type', 'FIRESTORE_NATIVE'),
            'concurrency_mode': cloud_state.get('concurrency_mode', 'OPTIMISTIC'),
            'app_engine_integration_mode': cloud_state.get('app_engine_integration_mode', 'ENABLED'),
            'key_prefix': cloud_state.get('key_prefix'),
            'point_in_time_recovery_enablement': cloud_state.get('point_in_time_recovery_enablement'),
            'delete_protection_state': cloud_state.get('delete_protection_state'),
            'version_retention_period': cloud_state.get('version_retention_period'),
            'earliest_version_time': cloud_state.get('earliest_version_time'),
            'etag': cloud_state.get('etag')
        }
    
    def _extract_functions_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Firebase Functions configuration"""
        # Firebase Functions are Cloud Functions with Firebase triggers
        return {
            'name': cloud_state.get('name'),
            'runtime': cloud_state.get('runtime'),
            'entry_point': cloud_state.get('entry_point'),
            'memory': cloud_state.get('available_memory_mb'),
            'timeout': cloud_state.get('timeout'),
            'environment_variables': cloud_state.get('environment_variables', {}),
            'firebase_triggers': cloud_state.get('firebase_triggers', {}),
            'https_trigger': cloud_state.get('https_trigger', {}),
            'labels': cloud_state.get('labels', {})
        }
    
    def _extract_storage_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Firebase Storage configuration"""
        # Firebase Storage is backed by Cloud Storage
        return {
            'bucket_name': cloud_state.get('bucket_name'),
            'location': cloud_state.get('location'),
            'storage_class': cloud_state.get('storage_class'),
            'firebase_config': cloud_state.get('firebase_config', {}),
            'cors_configuration': cloud_state.get('cors_configuration', []),
            'security_rules': cloud_state.get('security_rules', ''),
            'labels': cloud_state.get('labels', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firebase-specific fingerprint data"""
        if self.firebase_service == "hosting":
            return self._generate_hosting_fingerprint(cloud_state)
        elif self.firebase_service == "auth":
            return self._generate_auth_fingerprint(cloud_state)
        elif self.firebase_service == "firestore":
            return self._generate_firestore_fingerprint(cloud_state)
        elif self.firebase_service == "functions":
            return self._generate_functions_fingerprint(cloud_state)
        elif self.firebase_service == "storage":
            return self._generate_storage_fingerprint(cloud_state)
        else:
            return {}
    
    def _generate_hosting_fingerprint(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firebase Hosting fingerprint"""
        fingerprint_data = {}
        
        # Site configuration fingerprint
        site_type = cloud_state.get('type', 'DEFAULT_SITE')
        custom_domains = cloud_state.get('custom_domains', [])
        
        fingerprint_data['hosting_pattern'] = {
            'site_type': site_type,
            'is_default_site': site_type == 'DEFAULT_SITE',
            'has_custom_domains': len(custom_domains) > 0,
            'custom_domain_count': len(custom_domains),
            'has_ssl_config': bool(cloud_state.get('ssl_config')),
            'release_count': len(cloud_state.get('releases', [])),
            'version_count': len(cloud_state.get('versions', [])),
            'channel_count': len(cloud_state.get('channels', []))
        }
        
        # SSL and security fingerprint
        ssl_config = cloud_state.get('ssl_config', {})
        fingerprint_data['security_pattern'] = {
            'ssl_state': ssl_config.get('certificate_state', 'NONE'),
            'has_valid_ssl': ssl_config.get('certificate_state') == 'ACTIVE',
            'certificate_type': ssl_config.get('certificate_type', 'NONE'),
            'uses_managed_ssl': ssl_config.get('certificate_type') == 'MANAGED'
        }
        
        return fingerprint_data
    
    def _generate_auth_fingerprint(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firebase Authentication fingerprint"""
        fingerprint_data = {}
        
        # Authentication providers fingerprint
        sign_in_options = cloud_state.get('sign_in_options', [])
        fingerprint_data['auth_pattern'] = {
            'provider_count': len(sign_in_options),
            'has_email_password': any(opt.get('provider') == 'EMAIL_PASSWORD' for opt in sign_in_options),
            'has_google_oauth': any(opt.get('provider') == 'GOOGLE' for opt in sign_in_options),
            'has_facebook_oauth': any(opt.get('provider') == 'FACEBOOK' for opt in sign_in_options),
            'has_twitter_oauth': any(opt.get('provider') == 'TWITTER' for opt in sign_in_options),
            'has_github_oauth': any(opt.get('provider') == 'GITHUB' for opt in sign_in_options),
            'has_phone_auth': any(opt.get('provider') == 'PHONE' for opt in sign_in_options),
            'has_anonymous_auth': any(opt.get('provider') == 'ANONYMOUS' for opt in sign_in_options)
        }
        
        # Security features fingerprint
        mfa_config = cloud_state.get('multi_factor_config', {})
        password_policy = cloud_state.get('password_policy_config', {})
        
        fingerprint_data['security_pattern'] = {
            'mfa_enabled': mfa_config.get('state') == 'ENABLED',
            'mfa_enforcement': mfa_config.get('enforcement_state', 'OFF'),
            'has_password_policy': bool(password_policy.get('enforcement_state')),
            'password_policy_enforcement': password_policy.get('enforcement_state', 'OFF'),
            'has_recaptcha': bool(cloud_state.get('recaptcha_config', {}).get('site_key')),
            'authorized_domain_count': len(cloud_state.get('authorized_domains', []))
        }
        
        return fingerprint_data
    
    def _generate_firestore_fingerprint(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firestore fingerprint"""
        fingerprint_data = {}
        
        # Database configuration fingerprint
        fingerprint_data['database_pattern'] = {
            'type': cloud_state.get('type', 'FIRESTORE_NATIVE'),
            'is_native_mode': cloud_state.get('type') == 'FIRESTORE_NATIVE',
            'is_datastore_mode': cloud_state.get('type') == 'DATASTORE_MODE',
            'location_id': cloud_state.get('location_id'),
            'concurrency_mode': cloud_state.get('concurrency_mode', 'OPTIMISTIC'),
            'is_optimistic_concurrency': cloud_state.get('concurrency_mode') == 'OPTIMISTIC',
            'app_engine_integration': cloud_state.get('app_engine_integration_mode', 'ENABLED') == 'ENABLED'
        }
        
        # Backup and recovery fingerprint
        fingerprint_data['backup_pattern'] = {
            'pitr_enabled': cloud_state.get('point_in_time_recovery_enablement') == 'POINT_IN_TIME_RECOVERY_ENABLED',
            'delete_protection': cloud_state.get('delete_protection_state') == 'DELETE_PROTECTION_ENABLED',
            'has_version_retention': bool(cloud_state.get('version_retention_period'))
        }
        
        return fingerprint_data
    
    def _generate_functions_fingerprint(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firebase Functions fingerprint"""
        fingerprint_data = {}
        
        # Firebase-specific trigger fingerprint
        firebase_triggers = cloud_state.get('firebase_triggers', {})
        fingerprint_data['trigger_pattern'] = {
            'has_auth_triggers': bool(firebase_triggers.get('auth')),
            'has_firestore_triggers': bool(firebase_triggers.get('firestore')),
            'has_realtime_db_triggers': bool(firebase_triggers.get('database')),
            'has_analytics_triggers': bool(firebase_triggers.get('analytics')),
            'has_crashlytics_triggers': bool(firebase_triggers.get('crashlytics')),
            'has_remote_config_triggers': bool(firebase_triggers.get('remote_config')),
            'has_test_lab_triggers': bool(firebase_triggers.get('test_lab'))
        }
        
        return fingerprint_data
    
    def _generate_storage_fingerprint(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Firebase Storage fingerprint"""
        fingerprint_data = {}
        
        # Firebase Storage specific configuration
        firebase_config = cloud_state.get('firebase_config', {})
        fingerprint_data['firebase_storage_pattern'] = {
            'has_security_rules': bool(cloud_state.get('security_rules')),
            'cors_rule_count': len(cloud_state.get('cors_configuration', [])),
            'has_firebase_integration': bool(firebase_config),
            'storage_class': cloud_state.get('storage_class', 'STANDARD')
        }
        
        return fingerprint_data
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firebase-specific change impacts"""
        if self.firebase_service == "hosting":
            return self._predict_hosting_impact(current, desired)
        elif self.firebase_service == "auth":
            return self._predict_auth_impact(current, desired)
        elif self.firebase_service == "firestore":
            return self._predict_firestore_impact(current, desired)
        elif self.firebase_service == "functions":
            return self._predict_functions_impact(current, desired)
        elif self.firebase_service == "storage":
            return self._predict_storage_impact(current, desired)
        else:
            return ChangeImpactAnalysis(
                change_type="unknown_firebase_service",
                impact_level=ChangeImpact.LOW,
                estimated_downtime=0,
                propagation_time=60,
                cost_impact=0.0,
                affected_resources=[],
                recommendations=["Unknown Firebase service type"],
                rollback_complexity="unknown"
            )
    
    def _predict_hosting_impact(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firebase Hosting impact"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0  # Hosting deployments are zero-downtime
        propagation_time = 300  # 5 minutes for global CDN propagation
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Custom domain changes
        current_domains = current.get('custom_domains', [])
        desired_domains = desired.get('custom_domains', [])
        
        if current_domains != desired_domains:
            changes.append("custom_domains_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 1800)  # 30 minutes for DNS propagation
            
            new_domains = set(desired_domains) - set(current_domains)
            removed_domains = set(current_domains) - set(desired_domains)
            
            if new_domains:
                recommendations.append(f"Adding custom domains: {', '.join(new_domains)}")
                recommendations.append("Verify DNS records and SSL certificate provisioning")
                affected_resources.extend([f"dns_record:{domain}" for domain in new_domains])
            
            if removed_domains:
                recommendations.append(f"Removing custom domains: {', '.join(removed_domains)}")
                recommendations.append("Ensure traffic is redirected before removal")
        
        # SSL configuration changes
        current_ssl = current.get('ssl_config', {})
        desired_ssl = desired.get('ssl_config', {})
        
        if current_ssl != desired_ssl:
            changes.append("ssl_configuration_modification")
            
            recommendations.append("SSL configuration changes may affect site accessibility")
            recommendations.append("Monitor certificate provisioning status")
        
        change_type = ", ".join(changes) if changes else "hosting_update"
        
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
    
    def _predict_auth_impact(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firebase Authentication impact"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 60
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Sign-in provider changes
        current_providers = [opt.get('provider') for opt in current.get('sign_in_options', [])]
        desired_providers = [opt.get('provider') for opt in desired.get('sign_in_options', [])]
        
        if current_providers != desired_providers:
            changes.append("sign_in_providers_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            new_providers = set(desired_providers) - set(current_providers)
            removed_providers = set(current_providers) - set(desired_providers)
            
            if removed_providers:
                recommendations.append(f"WARNING: Removing auth providers: {', '.join(removed_providers)}")
                recommendations.append("Users with these providers will lose access")
                impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            
            if new_providers:
                recommendations.append(f"Adding auth providers: {', '.join(new_providers)}")
        
        # MFA configuration changes
        current_mfa = current.get('multi_factor_config', {}).get('state', 'DISABLED')
        desired_mfa = desired.get('multi_factor_config', {}).get('state', 'DISABLED')
        
        if current_mfa != desired_mfa:
            changes.append("mfa_configuration_modification")
            
            if desired_mfa == 'ENABLED' and current_mfa == 'DISABLED':
                recommendations.append("Enabling MFA improves security")
                recommendations.append("Users will need to set up additional factors")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
        
        change_type = ", ".join(changes) if changes else "auth_configuration_update"
        
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
    
    def _predict_firestore_impact(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firestore impact"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 300
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Database type changes (not supported)
        if current.get('type') != desired.get('type'):
            changes.append("database_type_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: Database type cannot be changed")
            recommendations.append("Requires creating new database and migrating data")
        
        # Point-in-time recovery changes
        current_pitr = current.get('point_in_time_recovery_enablement')
        desired_pitr = desired.get('point_in_time_recovery_enablement')
        
        if current_pitr != desired_pitr:
            changes.append("pitr_modification")
            
            if desired_pitr == 'POINT_IN_TIME_RECOVERY_ENABLED':
                recommendations.append("Enabling point-in-time recovery improves data protection")
                cost_impact += 25  # PITR has storage costs
            else:
                recommendations.append("Disabling point-in-time recovery reduces costs but removes data protection")
        
        change_type = ", ".join(changes) if changes else "firestore_configuration_update"
        
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
    
    def _predict_functions_impact(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firebase Functions impact"""
        # Firebase Functions follow similar patterns to Cloud Functions
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 120
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Firebase trigger changes
        current_triggers = current.get('firebase_triggers', {})
        desired_triggers = desired.get('firebase_triggers', {})
        
        if current_triggers != desired_triggers:
            changes.append("firebase_triggers_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            recommendations.append("Firebase trigger changes affect function invocation")
            affected_resources.extend(["firebase_auth", "firestore", "realtime_database"])
        
        change_type = ", ".join(changes) if changes else "firebase_function_update"
        
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
    
    def _predict_storage_impact(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Firebase Storage impact"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 60
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Security rules changes
        current_rules = current.get('security_rules', '')
        desired_rules = desired.get('security_rules', '')
        
        if current_rules != desired_rules:
            changes.append("security_rules_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            recommendations.append("Security rules changes affect file access permissions")
            recommendations.append("Test rules thoroughly before deployment")
        
        change_type = ", ".join(changes) if changes else "firebase_storage_update"
        
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
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firebase service health"""
        if self.firebase_service == "hosting":
            return self._check_hosting_health(resource_id, cloud_state)
        elif self.firebase_service == "auth":
            return self._check_auth_health(resource_id, cloud_state)
        elif self.firebase_service == "firestore":
            return self._check_firestore_health(resource_id, cloud_state)
        elif self.firebase_service == "functions":
            return self._check_functions_health(resource_id, cloud_state)
        elif self.firebase_service == "storage":
            return self._check_storage_health(resource_id, cloud_state)
        else:
            return ResourceHealth(
                resource_id=resource_id,
                health_score=0.5,
                issues=["Unknown Firebase service type"],
                performance_metrics={},
                last_check=datetime.now()
            )
    
    def _check_hosting_health(self, resource_id: str, cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firebase Hosting health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # SSL certificate check
        ssl_config = cloud_state.get('ssl_config', {})
        ssl_state = ssl_config.get('certificate_state', 'NONE')
        
        if ssl_state != 'ACTIVE':
            health_score -= 0.3
            issues.append(f"SSL certificate state: {ssl_state}")
        
        # Custom domains check
        custom_domains = cloud_state.get('custom_domains', [])
        if not custom_domains:
            issues.append("No custom domains configured (using default Firebase domain)")
        
        # Release and version management
        releases = cloud_state.get('releases', [])
        versions = cloud_state.get('versions', [])
        
        if len(versions) > 10:
            issues.append(f"Many versions deployed ({len(versions)}) - consider cleanup")
        
        metrics['ssl_active'] = ssl_state == 'ACTIVE'
        metrics['custom_domain_count'] = len(custom_domains)
        metrics['release_count'] = len(releases)
        metrics['version_count'] = len(versions)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _check_auth_health(self, resource_id: str, cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firebase Authentication health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Provider configuration
        sign_in_options = cloud_state.get('sign_in_options', [])
        if not sign_in_options:
            health_score -= 0.5
            issues.append("No authentication providers enabled")
        
        # MFA configuration
        mfa_config = cloud_state.get('multi_factor_config', {})
        if mfa_config.get('state') != 'ENABLED':
            health_score -= 0.2
            issues.append("Multi-factor authentication not enabled")
        
        # Password policy
        password_policy = cloud_state.get('password_policy_config', {})
        if not password_policy.get('enforcement_state') or password_policy.get('enforcement_state') == 'OFF':
            health_score -= 0.1
            issues.append("Password policy not enforced")
        
        metrics['provider_count'] = len(sign_in_options)
        metrics['mfa_enabled'] = mfa_config.get('state') == 'ENABLED'
        metrics['password_policy_active'] = password_policy.get('enforcement_state') == 'ENFORCE'
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _check_firestore_health(self, resource_id: str, cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firestore health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Point-in-time recovery
        pitr_enabled = cloud_state.get('point_in_time_recovery_enablement') == 'POINT_IN_TIME_RECOVERY_ENABLED'
        if not pitr_enabled:
            health_score -= 0.2
            issues.append("Point-in-time recovery not enabled")
        
        # Delete protection
        delete_protection = cloud_state.get('delete_protection_state') == 'DELETE_PROTECTION_ENABLED'
        if not delete_protection:
            health_score -= 0.1
            issues.append("Delete protection not enabled")
        
        metrics['pitr_enabled'] = pitr_enabled
        metrics['delete_protection_enabled'] = delete_protection
        metrics['database_type'] = cloud_state.get('type', 'FIRESTORE_NATIVE')
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _check_functions_health(self, resource_id: str, cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firebase Functions health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Firebase triggers check
        firebase_triggers = cloud_state.get('firebase_triggers', {})
        if not firebase_triggers:
            issues.append("No Firebase-specific triggers configured")
        
        metrics['firebase_trigger_count'] = len(firebase_triggers)
        metrics['has_auth_triggers'] = bool(firebase_triggers.get('auth'))
        metrics['has_firestore_triggers'] = bool(firebase_triggers.get('firestore'))
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _check_storage_health(self, resource_id: str, cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Firebase Storage health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Security rules check
        security_rules = cloud_state.get('security_rules', '')
        if not security_rules:
            health_score -= 0.3
            issues.append("No security rules configured (open access)")
        
        # CORS configuration
        cors_config = cloud_state.get('cors_configuration', [])
        if not cors_config:
            issues.append("No CORS configuration (may affect web access)")
        
        metrics['has_security_rules'] = bool(security_rules)
        metrics['cors_rule_count'] = len(cors_config)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Firebase-specific changes"""
        changes = {}
        
        if self.firebase_service == "hosting":
            # Custom domain changes
            if current.get('custom_domains') != desired.get('custom_domains'):
                changes['custom_domains'] = {
                    'from': current.get('custom_domains'),
                    'to': desired.get('custom_domains'),
                    'requires': 'update'
                }
        
        elif self.firebase_service == "auth":
            # Sign-in provider changes
            if current.get('sign_in_options') != desired.get('sign_in_options'):
                changes['sign_in_options'] = {
                    'from': current.get('sign_in_options'),
                    'to': desired.get('sign_in_options'),
                    'requires': 'update'
                }
        
        elif self.firebase_service == "firestore":
            # PITR changes
            if current.get('point_in_time_recovery_enablement') != desired.get('point_in_time_recovery_enablement'):
                changes['point_in_time_recovery'] = {
                    'from': current.get('point_in_time_recovery_enablement'),
                    'to': desired.get('point_in_time_recovery_enablement'),
                    'requires': 'update'
                }
        
        return changes