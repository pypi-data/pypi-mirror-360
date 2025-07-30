"""
GCP Cloud SQL Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Cloud SQL databases.
Extends the GCP intelligence base with Cloud SQL-specific capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class CloudSQLIntelligence(GCPIntelligenceBase):
    """Cloud SQL-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(GCPResourceType.CLOUD_SQL)
        self.sql_client = None
    
    def _initialize_service_client(self):
        """Initialize Cloud SQL client"""
        try:
            from google.cloud import sql_v1
            self.sql_client = sql_v1.SqlInstancesServiceClient()
        except Exception as e:
            print(f"⚠️  Failed to create Cloud SQL client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Cloud SQL instances"""
        existing_instances = {}
        
        if not self._get_gcp_client():
            return existing_instances
        
        try:
            # Mock discovery for demonstration
            # In real implementation would use: self.sql_client.list(project=project_id)
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Cloud SQL instances: {str(e)}")
        
        return existing_instances
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Cloud SQL instance state"""
        return {
            'name': cloud_state.get('name'),
            'instance_type': cloud_state.get('instance_type'),
            'database_version': cloud_state.get('database_version'),
            'tier': cloud_state.get('settings', {}).get('tier'),
            'region': cloud_state.get('region'),
            'backup_enabled': cloud_state.get('settings', {}).get('backup_configuration', {}).get('enabled', False),
            'binary_log_enabled': cloud_state.get('settings', {}).get('backup_configuration', {}).get('binary_log_enabled', False),
            'high_availability': cloud_state.get('settings', {}).get('availability_type') == 'REGIONAL',
            'disk_size': cloud_state.get('settings', {}).get('data_disk_size_gb'),
            'disk_type': cloud_state.get('settings', {}).get('data_disk_type'),
            'disk_autoresize': cloud_state.get('settings', {}).get('storage_auto_resize', False),
            'deletion_protection': cloud_state.get('settings', {}).get('deletion_protection_enabled', False),
            'authorized_networks': cloud_state.get('settings', {}).get('ip_configuration', {}).get('authorized_networks', []),
            'ssl_mode': cloud_state.get('settings', {}).get('ip_configuration', {}).get('ssl_mode'),
            'require_ssl': cloud_state.get('settings', {}).get('ip_configuration', {}).get('require_ssl', False),
            'private_network': cloud_state.get('settings', {}).get('ip_configuration', {}).get('private_network'),
            'database_flags': cloud_state.get('settings', {}).get('database_flags', []),
            'maintenance_window': cloud_state.get('settings', {}).get('maintenance_window', {}),
            'user_labels': cloud_state.get('settings', {}).get('user_labels', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cloud SQL-specific fingerprint data"""
        fingerprint_data = {}
        
        # Database engine and version fingerprint
        database_version = cloud_state.get('database_version', '')
        instance_type = cloud_state.get('instance_type', '')
        
        fingerprint_data['database_pattern'] = {
            'engine': self._get_database_engine(database_version),
            'version': database_version,
            'is_mysql': database_version.startswith('MYSQL'),
            'is_postgres': database_version.startswith('POSTGRES'),
            'is_sql_server': database_version.startswith('SQLSERVER'),
            'instance_type': instance_type,
            'is_second_generation': instance_type != 'FIRST_GEN'
        }
        
        # Performance and scaling fingerprint
        settings = cloud_state.get('settings', {})
        tier = settings.get('tier', '')
        
        fingerprint_data['performance_pattern'] = {
            'tier': tier,
            'is_shared_core': tier.startswith('db-f1') or tier.startswith('db-g1'),
            'is_standard': tier.startswith('db-n1-standard'),
            'is_high_memory': 'highmem' in tier,
            'is_custom': 'custom' in tier,
            'disk_size_gb': settings.get('data_disk_size_gb', 0),
            'disk_type': settings.get('data_disk_type', 'PD_SSD'),
            'is_ssd': settings.get('data_disk_type') == 'PD_SSD',
            'autoresize_enabled': settings.get('storage_auto_resize', False)
        }
        
        # High availability and backup fingerprint
        backup_config = settings.get('backup_configuration', {})
        fingerprint_data['reliability_pattern'] = {
            'high_availability': settings.get('availability_type') == 'REGIONAL',
            'backup_enabled': backup_config.get('enabled', False),
            'binary_log_enabled': backup_config.get('binary_log_enabled', False),
            'point_in_time_recovery': backup_config.get('point_in_time_recovery_enabled', False),
            'deletion_protection': settings.get('deletion_protection_enabled', False),
            'maintenance_window_configured': bool(settings.get('maintenance_window', {}).get('day'))
        }
        
        # Network security fingerprint
        ip_config = settings.get('ip_configuration', {})
        fingerprint_data['security_pattern'] = {
            'has_private_ip': bool(ip_config.get('private_network')),
            'has_public_ip': ip_config.get('ipv4_enabled', True),
            'require_ssl': ip_config.get('require_ssl', False),
            'ssl_mode': ip_config.get('ssl_mode', 'ALLOW_UNENCRYPTED_AND_ENCRYPTED'),
            'authorized_networks_count': len(ip_config.get('authorized_networks', [])),
            'allows_all_ips': any(
                net.get('value') == '0.0.0.0/0' 
                for net in ip_config.get('authorized_networks', [])
            ),
            'database_flags_count': len(settings.get('database_flags', []))
        }
        
        return fingerprint_data
    
    def _get_database_engine(self, database_version: str) -> str:
        """Extract database engine from version string"""
        if database_version.startswith('MYSQL'):
            return 'mysql'
        elif database_version.startswith('POSTGRES'):
            return 'postgresql'
        elif database_version.startswith('SQLSERVER'):
            return 'sqlserver'
        else:
            return 'unknown'
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Cloud SQL-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 180  # 3 minutes default for Cloud SQL
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Tier/machine type changes
        current_tier = current.get('tier', '')
        desired_tier = desired.get('tier', '')
        
        if current_tier != desired_tier:
            changes.append("tier_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            downtime = 300  # 5 minutes for tier change
            propagation_time = max(propagation_time, 600)
            rollback_complexity = "medium"
            
            # Calculate cost impact for tier changes
            cost_impact = self._estimate_tier_cost_impact(current_tier, desired_tier)
            
            recommendations.append("Tier changes require instance restart")
            recommendations.append("Backup database before tier change")
            
            if cost_impact > 50:
                recommendations.append(f"WARNING: Cost increase of ~{cost_impact:.0f}%")
            elif cost_impact < -20:
                recommendations.append(f"Cost savings of ~{abs(cost_impact):.0f}% detected")
        
        # 2. Database version changes
        if current.get('database_version') != desired.get('database_version'):
            changes.append("database_version_upgrade")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            downtime = 1800  # 30 minutes for major version upgrade
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: Database version upgrades are irreversible")
            recommendations.append("Perform full backup before version upgrade")
            recommendations.append("Test application compatibility with new version")
            recommendations.append("Consider blue-green deployment strategy")
        
        # 3. High availability changes
        current_ha = current.get('high_availability', False)
        desired_ha = desired.get('high_availability', False)
        
        if current_ha != desired_ha:
            changes.append("high_availability_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            downtime = 600  # 10 minutes for HA configuration
            
            if desired_ha and not current_ha:
                cost_impact += 100  # HA roughly doubles the cost
                recommendations.append("Enabling HA: ~100% cost increase for improved reliability")
                recommendations.append("HA provides automatic failover and 99.95% uptime SLA")
            else:
                cost_impact -= 50  # Disabling HA saves ~50% of instance cost
                recommendations.append("Disabling HA: ~50% cost savings but reduced reliability")
                recommendations.append("WARNING: Single point of failure without HA")
        
        # 4. Disk size changes
        current_disk_size = current.get('disk_size', 0)
        desired_disk_size = desired.get('disk_size', 0)
        
        if desired_disk_size and current_disk_size != desired_disk_size:
            changes.append("disk_size_modification")
            
            if desired_disk_size < current_disk_size:
                impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
                recommendations.append("CRITICAL: Cannot reduce disk size on Cloud SQL")
                recommendations.append("Consider creating new instance with smaller disk")
                rollback_complexity = "high"
            else:
                size_increase = desired_disk_size - current_disk_size
                cost_impact += (size_increase / current_disk_size) * 20 if current_disk_size > 0 else 0
                recommendations.append(f"Increasing disk size by {size_increase}GB")
                recommendations.append("Disk size increase is immediate and zero-downtime")
        
        # 5. Backup configuration changes
        current_backup = current.get('backup_enabled', False)
        desired_backup = desired.get('backup_enabled', False)
        
        if current_backup != desired_backup:
            changes.append("backup_configuration_modification")
            
            if desired_backup and not current_backup:
                cost_impact += 5  # Backup storage costs
                recommendations.append("Enabling automated backups improves data protection")
                recommendations.append("Backups are stored for 7 days by default")
            else:
                recommendations.append("WARNING: Disabling backups removes data protection")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
        
        # 6. Binary logging changes
        current_binlog = current.get('binary_log_enabled', False)
        desired_binlog = desired.get('binary_log_enabled', False)
        
        if current_binlog != desired_binlog:
            changes.append("binary_log_modification")
            
            if desired_binlog and not current_binlog:
                recommendations.append("Enabling binary logging enables point-in-time recovery")
                cost_impact += 2  # Small storage overhead
            else:
                recommendations.append("Disabling binary logging removes point-in-time recovery")
        
        # 7. SSL/TLS configuration changes
        current_ssl = current.get('require_ssl', False)
        desired_ssl = desired.get('require_ssl', False)
        
        if current_ssl != desired_ssl:
            changes.append("ssl_configuration_modification")
            
            if desired_ssl and not current_ssl:
                recommendations.append("Requiring SSL improves security")
                recommendations.append("Ensure all clients support SSL connections")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            else:
                recommendations.append("WARNING: Allowing unencrypted connections")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
        
        # 8. Private network changes
        current_private = current.get('private_network')
        desired_private = desired.get('private_network')
        
        if current_private != desired_private:
            changes.append("network_configuration_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            if desired_private and not current_private:
                recommendations.append("Enabling private IP improves security")
                recommendations.append("Requires VPC peering for application access")
                affected_resources.append("vpc_networks")
            else:
                recommendations.append("Switching to public IP")
                recommendations.append("Configure authorized networks for security")
        
        # 9. Deletion protection changes
        if current.get('deletion_protection') != desired.get('deletion_protection'):
            changes.append("deletion_protection_modification")
            
            if not desired.get('deletion_protection') and current.get('deletion_protection'):
                recommendations.append("WARNING: Disabling deletion protection")
            else:
                recommendations.append("Enabling deletion protection improves safety")
        
        # Find affected resources
        instance_name = current.get('name') or desired.get('name')
        if instance_name:
            affected_resources.extend([
                f"applications_using_database:{instance_name}",
                f"database_users:{instance_name}",
                f"read_replicas:{instance_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "database_configuration_update"
        
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
    
    def _estimate_tier_cost_impact(self, current_tier: str, desired_tier: str) -> float:
        """Estimate cost impact of tier changes"""
        
        # Simplified cost estimation for Cloud SQL tiers
        tier_costs = {
            'db-f1-micro': 1,
            'db-g1-small': 2,
            'db-n1-standard-1': 5,
            'db-n1-standard-2': 10,
            'db-n1-standard-4': 20,
            'db-n1-standard-8': 40,
            'db-n1-standard-16': 80,
            'db-n1-highmem-2': 15,
            'db-n1-highmem-4': 30,
            'db-n1-highmem-8': 60,
            'db-custom-1-3840': 8,
            'db-custom-2-7680': 16,
            'db-custom-4-15360': 32
        }
        
        current_cost = tier_costs.get(current_tier, 10)
        desired_cost = tier_costs.get(desired_tier, 10)
        
        if current_cost == 0:
            return 0
        
        return ((desired_cost - current_cost) / current_cost) * 100
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Cloud SQL instance health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Instance state check
        state = cloud_state.get('state', 'UNKNOWN')
        if state != 'RUNNABLE':
            health_score -= 0.3
            issues.append(f"Instance state: {state}")
        
        # High availability check
        settings = cloud_state.get('settings', {})
        ha_enabled = settings.get('availability_type') == 'REGIONAL'
        if not ha_enabled:
            health_score -= 0.2
            issues.append("High availability not enabled (consider for production)")
        
        # Backup configuration check
        backup_config = settings.get('backup_configuration', {})
        backup_enabled = backup_config.get('enabled', False)
        if not backup_enabled:
            health_score -= 0.2
            issues.append("Automated backups not enabled")
        
        binary_log_enabled = backup_config.get('binary_log_enabled', False)
        if backup_enabled and not binary_log_enabled:
            health_score -= 0.1
            issues.append("Binary logging not enabled (limits point-in-time recovery)")
        
        # Security checks
        ip_config = settings.get('ip_configuration', {})
        require_ssl = ip_config.get('require_ssl', False)
        if not require_ssl:
            health_score -= 0.1
            issues.append("SSL not required (consider for better security)")
        
        # Check for public access with open networks
        authorized_networks = ip_config.get('authorized_networks', [])
        has_open_access = any(net.get('value') == '0.0.0.0/0' for net in authorized_networks)
        if has_open_access:
            health_score -= 0.3
            issues.append("CRITICAL: Database allows access from all IPs (0.0.0.0/0)")
        
        # Private network check
        private_network = ip_config.get('private_network')
        if not private_network:
            health_score -= 0.1
            issues.append("Using public IP (consider private network for better security)")
        
        # Deletion protection check
        deletion_protection = settings.get('deletion_protection_enabled', False)
        if not deletion_protection:
            health_score -= 0.1
            issues.append("Deletion protection not enabled")
        
        # Performance checks
        tier = settings.get('tier', '')
        if tier.startswith('db-f1') or tier.startswith('db-g1'):
            issues.append("Shared-core instance (consider dedicated CPU for production)")
        
        # Disk type check
        disk_type = settings.get('data_disk_type', 'PD_HDD')
        if disk_type != 'PD_SSD':
            health_score -= 0.1
            issues.append("Using HDD storage (consider SSD for better performance)")
        
        # Autoresize check
        autoresize = settings.get('storage_auto_resize', False)
        if not autoresize:
            issues.append("Storage autoresize not enabled (may cause outages if disk fills)")
        
        # Maintenance window check
        maintenance_window = settings.get('maintenance_window', {})
        if not maintenance_window.get('day'):
            issues.append("No maintenance window configured (updates may happen anytime)")
        
        # Calculate feature metrics
        metrics['security_features'] = sum([
            require_ssl,
            bool(private_network),
            deletion_protection,
            not has_open_access,
            len(authorized_networks) < 5  # Limited network access
        ])
        
        metrics['reliability_features'] = sum([
            ha_enabled,
            backup_enabled,
            binary_log_enabled,
            autoresize,
            bool(maintenance_window.get('day'))
        ])
        
        metrics['performance_features'] = sum([
            disk_type == 'PD_SSD',
            not tier.startswith(('db-f1', 'db-g1')),  # Dedicated CPU
            settings.get('data_disk_size_gb', 0) >= 100  # Reasonable disk size
        ])
        
        metrics['backup_retention_days'] = backup_config.get('backup_retention_settings', {}).get('retained_backups')
        metrics['authorized_network_count'] = len(authorized_networks)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Cloud SQL-specific changes"""
        changes = {}
        
        # Tier changes
        if current.get('tier') != desired.get('tier'):
            changes['tier'] = {
                'from': current.get('tier'),
                'to': desired.get('tier'),
                'requires': 'restart'
            }
        
        # Database version changes
        if current.get('database_version') != desired.get('database_version'):
            changes['database_version'] = {
                'from': current.get('database_version'),
                'to': desired.get('database_version'),
                'requires': 'upgrade'
            }
        
        # High availability changes
        if current.get('high_availability') != desired.get('high_availability'):
            changes['high_availability'] = {
                'from': current.get('high_availability'),
                'to': desired.get('high_availability'),
                'requires': 'restart'
            }
        
        # Disk size changes
        if current.get('disk_size') != desired.get('disk_size'):
            changes['disk_size'] = {
                'from': current.get('disk_size'),
                'to': desired.get('disk_size'),
                'requires': 'resize'
            }
        
        # Backup configuration changes
        if current.get('backup_enabled') != desired.get('backup_enabled'):
            changes['backup_enabled'] = {
                'from': current.get('backup_enabled'),
                'to': desired.get('backup_enabled'),
                'requires': 'update'
            }
        
        # Network configuration changes
        if current.get('private_network') != desired.get('private_network'):
            changes['private_network'] = {
                'from': current.get('private_network'),
                'to': desired.get('private_network'),
                'requires': 'restart'
            }
        
        return changes