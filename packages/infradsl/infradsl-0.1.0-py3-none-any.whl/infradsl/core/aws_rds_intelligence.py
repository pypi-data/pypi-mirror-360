"""
RDS Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for RDS databases.
Extends the AWS intelligence base with RDS-specific capabilities.
"""

import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType,
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class RDSIntelligence(AWSIntelligenceBase):
    """RDS-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(ResourceType.RDS_INSTANCE)
        self.rds_client = None
    
    def _get_rds_client(self):
        """Get RDS client with error handling"""
        if not self.rds_client:
            try:
                self.rds_client = boto3.client('rds')
            except (NoCredentialsError, Exception) as e:
                print(f"⚠️  Failed to create RDS client: {e}")
                return None
        return self.rds_client
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing RDS instances and clusters"""
        existing_resources = {}
        
        client = self._get_rds_client()
        if not client:
            return existing_resources
        
        try:
            # Get DB instances
            paginator = client.get_paginator('describe_db_instances')
            
            for page in paginator.paginate():
                for db_instance in page.get('DBInstances', []):
                    instance_id = db_instance['DBInstanceIdentifier']
                    
                    try:
                        instance_data = self._extract_db_instance_data(db_instance)
                        existing_resources[instance_id] = instance_data
                        
                    except Exception as e:
                        print(f"⚠️  Failed to extract data for RDS instance {instance_id}: {str(e)}")
                        existing_resources[instance_id] = {
                            'db_instance_identifier': instance_id,
                            'db_instance_status': db_instance.get('DBInstanceStatus', 'unknown'),
                            'error': str(e)
                        }
            
            # Get DB clusters (Aurora)
            try:
                cluster_paginator = client.get_paginator('describe_db_clusters')
                
                for page in cluster_paginator.paginate():
                    for db_cluster in page.get('DBClusters', []):
                        cluster_id = db_cluster['DBClusterIdentifier']
                        
                        try:
                            cluster_data = self._extract_db_cluster_data(db_cluster)
                            existing_resources[cluster_id] = cluster_data
                            
                        except Exception as e:
                            print(f"⚠️  Failed to extract data for RDS cluster {cluster_id}: {str(e)}")
                            existing_resources[cluster_id] = {
                                'db_cluster_identifier': cluster_id,
                                'status': db_cluster.get('Status', 'unknown'),
                                'resource_type': 'db_cluster',
                                'error': str(e)
                            }
                            
            except ClientError as e:
                # Aurora might not be available in all regions
                if 'InvalidAction' not in str(e):
                    print(f"⚠️  Failed to discover RDS clusters: {str(e)}")
        
        except Exception as e:
            print(f"⚠️  Failed to discover RDS resources: {str(e)}")
        
        return existing_resources
    
    def _extract_db_instance_data(self, db_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive DB instance data"""
        
        # Extract tags
        tags = {}
        for tag in db_instance.get('TagList', []):
            tags[tag['Key']] = tag['Value']
        
        return {
            'db_instance_identifier': db_instance['DBInstanceIdentifier'],
            'resource_type': 'db_instance',
            'db_instance_class': db_instance.get('DBInstanceClass'),
            'engine': db_instance.get('Engine'),
            'engine_version': db_instance.get('EngineVersion'),
            'db_instance_status': db_instance.get('DBInstanceStatus'),
            'master_username': db_instance.get('MasterUsername'),
            'db_name': db_instance.get('DBName'),
            'endpoint': db_instance.get('Endpoint', {}),
            'allocated_storage': db_instance.get('AllocatedStorage'),
            'storage_type': db_instance.get('StorageType'),
            'storage_encrypted': db_instance.get('StorageEncrypted', False),
            'kms_key_id': db_instance.get('KmsKeyId'),
            'iops': db_instance.get('Iops'),
            'vpc_security_groups': [sg['VpcSecurityGroupId'] for sg in db_instance.get('VpcSecurityGroups', [])],
            'db_subnet_group': db_instance.get('DBSubnetGroup', {}),
            'multi_az': db_instance.get('MultiAZ', False),
            'backup_retention_period': db_instance.get('BackupRetentionPeriod', 0),
            'preferred_backup_window': db_instance.get('PreferredBackupWindow'),
            'preferred_maintenance_window': db_instance.get('PreferredMaintenanceWindow'),
            'auto_minor_version_upgrade': db_instance.get('AutoMinorVersionUpgrade', False),
            'publicly_accessible': db_instance.get('PubliclyAccessible', False),
            'deletion_protection': db_instance.get('DeletionProtection', False),
            'performance_insights_enabled': db_instance.get('PerformanceInsightsEnabled', False),
            'monitoring_interval': db_instance.get('MonitoringInterval', 0),
            'enhanced_monitoring_resource_arn': db_instance.get('EnhancedMonitoringResourceArn'),
            'availability_zone': db_instance.get('AvailabilityZone'),
            'instance_create_time': db_instance.get('InstanceCreateTime'),
            'latest_restorable_time': db_instance.get('LatestRestorableTime'),
            'db_parameter_groups': db_instance.get('DBParameterGroups', []),
            'option_group_memberships': db_instance.get('OptionGroupMemberships', []),
            'tags': tags
        }
    
    def _extract_db_cluster_data(self, db_cluster: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive DB cluster data"""
        
        # Extract tags
        tags = {}
        for tag in db_cluster.get('TagList', []):
            tags[tag['Key']] = tag['Value']
        
        return {
            'db_cluster_identifier': db_cluster['DBClusterIdentifier'],
            'resource_type': 'db_cluster',
            'engine': db_cluster.get('Engine'),
            'engine_version': db_cluster.get('EngineVersion'),
            'status': db_cluster.get('Status'),
            'master_username': db_cluster.get('MasterUsername'),
            'database_name': db_cluster.get('DatabaseName'),
            'endpoint': db_cluster.get('Endpoint'),
            'reader_endpoint': db_cluster.get('ReaderEndpoint'),
            'port': db_cluster.get('Port'),
            'storage_encrypted': db_cluster.get('StorageEncrypted', False),
            'kms_key_id': db_cluster.get('KmsKeyId'),
            'vpc_security_groups': [sg['VpcSecurityGroupId'] for sg in db_cluster.get('VpcSecurityGroups', [])],
            'db_subnet_group': db_cluster.get('DBSubnetGroup'),
            'db_cluster_members': db_cluster.get('DBClusterMembers', []),
            'backup_retention_period': db_cluster.get('BackupRetentionPeriod', 0),
            'preferred_backup_window': db_cluster.get('PreferredBackupWindow'),
            'preferred_maintenance_window': db_cluster.get('PreferredMaintenanceWindow'),
            'deletion_protection': db_cluster.get('DeletionProtection', False),
            'cluster_create_time': db_cluster.get('ClusterCreateTime'),
            'availability_zones': db_cluster.get('AvailabilityZones', []),
            'db_cluster_parameter_group': db_cluster.get('DBClusterParameterGroup'),
            'tags': tags
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from RDS resource state"""
        if cloud_state.get('resource_type') == 'db_cluster':
            return {
                'db_cluster_identifier': cloud_state.get('db_cluster_identifier'),
                'engine': cloud_state.get('engine'),
                'engine_version': cloud_state.get('engine_version'),
                'master_username': cloud_state.get('master_username'),
                'storage_encrypted': cloud_state.get('storage_encrypted', False),
                'backup_retention_period': cloud_state.get('backup_retention_period', 0),
                'deletion_protection': cloud_state.get('deletion_protection', False),
                'vpc_security_groups': cloud_state.get('vpc_security_groups', []),
                'db_subnet_group': cloud_state.get('db_subnet_group'),
                'availability_zones': cloud_state.get('availability_zones', []),
                'tags': cloud_state.get('tags', {})
            }
        else:
            return {
                'db_instance_identifier': cloud_state.get('db_instance_identifier'),
                'db_instance_class': cloud_state.get('db_instance_class'),
                'engine': cloud_state.get('engine'),
                'engine_version': cloud_state.get('engine_version'),
                'master_username': cloud_state.get('master_username'),
                'allocated_storage': cloud_state.get('allocated_storage'),
                'storage_type': cloud_state.get('storage_type'),
                'storage_encrypted': cloud_state.get('storage_encrypted', False),
                'multi_az': cloud_state.get('multi_az', False),
                'backup_retention_period': cloud_state.get('backup_retention_period', 0),
                'deletion_protection': cloud_state.get('deletion_protection', False),
                'publicly_accessible': cloud_state.get('publicly_accessible', False),
                'vpc_security_groups': cloud_state.get('vpc_security_groups', []),
                'db_subnet_group': cloud_state.get('db_subnet_group', {}),
                'tags': cloud_state.get('tags', {})
            }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RDS-specific fingerprint data"""
        fingerprint_data = {}
        
        # Database engine fingerprint
        engine = cloud_state.get('engine', '')
        fingerprint_data['engine_pattern'] = {
            'engine_family': self._get_engine_family(engine),
            'is_mysql_compatible': engine in ['mysql', 'aurora-mysql'],
            'is_postgres_compatible': engine in ['postgres', 'aurora-postgresql'],
            'is_oracle': engine.startswith('oracle'),
            'is_sqlserver': engine.startswith('sqlserver'),
            'is_aurora': engine.startswith('aurora')
        }
        
        # Configuration fingerprint
        resource_type = cloud_state.get('resource_type', 'db_instance')
        
        if resource_type == 'db_cluster':
            fingerprint_data['configuration_pattern'] = {
                'is_cluster': True,
                'member_count': len(cloud_state.get('db_cluster_members', [])),
                'has_reader_endpoint': bool(cloud_state.get('reader_endpoint')),
                'multi_az_deployment': len(cloud_state.get('availability_zones', [])) > 1
            }
        else:
            fingerprint_data['configuration_pattern'] = {
                'is_cluster': False,
                'instance_family': self._get_instance_family(cloud_state.get('db_instance_class', '')),
                'multi_az': cloud_state.get('multi_az', False),
                'has_read_replicas': False  # Would need additional API call
            }
        
        # Security fingerprint
        fingerprint_data['security_pattern'] = {
            'storage_encrypted': cloud_state.get('storage_encrypted', False),
            'publicly_accessible': cloud_state.get('publicly_accessible', False),
            'deletion_protection': cloud_state.get('deletion_protection', False),
            'security_group_count': len(cloud_state.get('vpc_security_groups', [])),
            'in_vpc': bool(cloud_state.get('db_subnet_group'))
        }
        
        # Backup and maintenance fingerprint
        fingerprint_data['maintenance_pattern'] = {
            'backup_enabled': cloud_state.get('backup_retention_period', 0) > 0,
            'backup_retention_days': cloud_state.get('backup_retention_period', 0),
            'auto_minor_version_upgrade': cloud_state.get('auto_minor_version_upgrade', False),
            'has_maintenance_window': bool(cloud_state.get('preferred_maintenance_window')),
            'performance_insights': cloud_state.get('performance_insights_enabled', False),
            'enhanced_monitoring': cloud_state.get('monitoring_interval', 0) > 0
        }
        
        return fingerprint_data
    
    def _get_engine_family(self, engine: str) -> str:
        """Get database engine family"""
        if engine.startswith('mysql') or engine == 'aurora-mysql':
            return 'mysql'
        elif engine.startswith('postgres') or engine == 'aurora-postgresql':
            return 'postgresql'
        elif engine.startswith('oracle'):
            return 'oracle'
        elif engine.startswith('sqlserver'):
            return 'sqlserver'
        elif engine.startswith('aurora'):
            return 'aurora'
        else:
            return 'other'
    
    def _get_instance_family(self, instance_class: str) -> str:
        """Get RDS instance family"""
        if not instance_class or '.' not in instance_class:
            return 'unknown'
        
        family = instance_class.split('.')[1]
        
        if family.startswith('t'):
            return 'burstable'
        elif family.startswith('m'):
            return 'general_purpose'
        elif family.startswith('r'):
            return 'memory_optimized'
        elif family.startswith('x'):
            return 'memory_optimized_extreme'
        else:
            return 'other'
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict RDS-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 300  # 5 minutes default
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        resource_type = current.get('resource_type') or desired.get('resource_type', 'db_instance')
        
        # 1. Instance class changes
        if resource_type == 'db_instance':
            current_class = current.get('db_instance_class')
            desired_class = desired.get('db_instance_class')
            
            if current_class != desired_class:
                changes.append("instance_class_modification")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                downtime = 300  # 5 minutes typical
                propagation_time = max(propagation_time, 900)  # 15 minutes total
                rollback_complexity = "medium"
                
                # Calculate cost impact
                cost_impact = self._estimate_instance_class_cost_impact(current_class, desired_class)
                
                recommendations.append("Instance class change causes brief downtime")
                recommendations.append("Schedule during maintenance window")
                
                if cost_impact > 50:
                    recommendations.append(f"WARNING: Cost increase of ~{cost_impact:.0f}%")
                elif cost_impact < -20:
                    recommendations.append(f"Cost savings of ~{abs(cost_impact):.0f}% detected")
        
        # 2. Storage changes
        current_storage = current.get('allocated_storage', 0)
        desired_storage = desired.get('allocated_storage', 0)
        
        if current_storage != desired_storage:
            changes.append("storage_modification")
            
            if desired_storage > current_storage:
                # Storage increase - online operation for most engines
                impact_level = ChangeImpact.LOW if impact_level.value < ChangeImpact.LOW.value else impact_level
                recommendations.append("Storage increase is typically online (no downtime)")
                cost_impact += ((desired_storage - current_storage) / current_storage) * 20 if current_storage > 0 else 20
            else:
                # Storage decrease - not supported in most cases
                impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
                recommendations.append("CRITICAL: Storage cannot be decreased")
                recommendations.append("Consider creating new instance with smaller storage")
                rollback_complexity = "high"
        
        # 3. Engine version changes
        if current.get('engine_version') != desired.get('engine_version'):
            changes.append("engine_version_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            downtime = max(downtime, 600)  # 10 minutes for major version upgrades
            propagation_time = max(propagation_time, 1200)  # 20 minutes total
            rollback_complexity = "high"
            
            recommendations.append("Engine version upgrade may cause extended downtime")
            recommendations.append("Test application compatibility before upgrade")
            recommendations.append("Take snapshot before proceeding")
        
        # 4. Multi-AZ changes
        if current.get('multi_az') != desired.get('multi_az'):
            changes.append("multi_az_modification")
            
            if desired.get('multi_az') and not current.get('multi_az'):
                # Enabling Multi-AZ
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                downtime = max(downtime, 180)  # 3 minutes
                cost_impact += 100  # Roughly double the cost
                recommendations.append("Enabling Multi-AZ significantly improves availability")
                recommendations.append("WARNING: Cost will approximately double")
            else:
                # Disabling Multi-AZ
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                downtime = max(downtime, 120)  # 2 minutes
                cost_impact -= 50  # Roughly half the cost
                recommendations.append("Disabling Multi-AZ reduces availability")
                recommendations.append("Cost savings of ~50%")
        
        # 5. Security group changes
        current_sgs = set(current.get('vpc_security_groups', []))
        desired_sgs = set(desired.get('vpc_security_groups', []))
        
        if current_sgs != desired_sgs:
            changes.append("security_group_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            removed_sgs = current_sgs - desired_sgs
            if removed_sgs:
                recommendations.append("WARNING: Removing security groups may break connectivity")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            recommendations.append("Test database connectivity after security group changes")
            affected_resources.extend([f"security_group:{sg}" for sg in current_sgs.union(desired_sgs)])
        
        # 6. Backup retention changes
        current_backup = current.get('backup_retention_period', 0)
        desired_backup = desired.get('backup_retention_period', 0)
        
        if current_backup != desired_backup:
            changes.append("backup_retention_modification")
            
            if desired_backup > current_backup:
                recommendations.append("Increasing backup retention improves disaster recovery")
                cost_impact += (desired_backup - current_backup) * 0.5  # Rough estimate
            elif desired_backup == 0 and current_backup > 0:
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                recommendations.append("WARNING: Disabling backups removes disaster recovery")
            else:
                recommendations.append("Reducing backup retention period")
        
        # 7. Encryption changes
        if current.get('storage_encrypted') != desired.get('storage_encrypted'):
            changes.append("encryption_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            recommendations.append("CRITICAL: Encryption cannot be changed on existing instance")
            recommendations.append("Requires snapshot restore to encrypted instance")
            rollback_complexity = "high"
            downtime = 1800  # 30 minutes for snapshot restore
        
        # 8. Public accessibility changes
        if current.get('publicly_accessible') != desired.get('publicly_accessible'):
            changes.append("public_access_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired.get('publicly_accessible') and not current.get('publicly_accessible'):
                recommendations.append("WARNING: Making database publicly accessible increases security risk")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            else:
                recommendations.append("Improving security by making database private")
        
        # Find affected resources
        db_identifier = current.get('db_instance_identifier') or current.get('db_cluster_identifier')
        if db_identifier:
            affected_resources.extend([
                f"applications_using_{db_identifier}",
                f"read_replicas_{db_identifier}",
                f"cloudwatch_alarms_{db_identifier}"
            ])
        
        change_type = ", ".join(changes) if changes else "database_update"
        
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
    
    def _estimate_instance_class_cost_impact(self, current_class: str, desired_class: str) -> float:
        """Estimate cost impact of instance class changes"""
        
        # Simplified cost estimation based on instance classes
        cost_multipliers = {
            'db.t3.micro': 1, 'db.t3.small': 2, 'db.t3.medium': 4, 'db.t3.large': 8,
            'db.t3.xlarge': 16, 'db.t3.2xlarge': 32,
            'db.m5.large': 10, 'db.m5.xlarge': 20, 'db.m5.2xlarge': 40, 'db.m5.4xlarge': 80,
            'db.r5.large': 15, 'db.r5.xlarge': 30, 'db.r5.2xlarge': 60, 'db.r5.4xlarge': 120,
            'db.x1e.xlarge': 50, 'db.x1e.2xlarge': 100, 'db.x1e.4xlarge': 200
        }
        
        current_cost = cost_multipliers.get(current_class, 10)
        desired_cost = cost_multipliers.get(desired_class, 10)
        
        if current_cost == 0:
            return 0
        
        return ((desired_cost - current_cost) / current_cost) * 100
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check RDS resource health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        resource_type = cloud_state.get('resource_type', 'db_instance')
        status = cloud_state.get('db_instance_status') or cloud_state.get('status', 'unknown')
        
        # Status check
        if status != 'available':
            health_score -= 0.3
            issues.append(f"Database status: {status}")
        
        # Security checks
        if cloud_state.get('publicly_accessible', False):
            health_score -= 0.2
            issues.append("Database is publicly accessible (security risk)")
        
        if not cloud_state.get('storage_encrypted', False):
            health_score -= 0.2
            issues.append("Storage encryption not enabled")
        
        if not cloud_state.get('deletion_protection', False):
            health_score -= 0.1
            issues.append("Deletion protection not enabled")
        
        # Backup checks
        backup_retention = cloud_state.get('backup_retention_period', 0)
        if backup_retention == 0:
            health_score -= 0.2
            issues.append("Automated backups not enabled")
        elif backup_retention < 7:
            health_score -= 0.1
            issues.append("Short backup retention period (consider 7+ days)")
        
        # Multi-AZ check for production workloads
        if resource_type == 'db_instance' and not cloud_state.get('multi_az', False):
            health_score -= 0.1
            issues.append("Multi-AZ not enabled (consider for production)")
        
        # VPC security groups check
        security_groups = cloud_state.get('vpc_security_groups', [])
        if not security_groups:
            health_score -= 0.2
            issues.append("No VPC security groups attached")
        
        # Monitoring checks
        if not cloud_state.get('performance_insights_enabled', False):
            issues.append("Performance Insights not enabled (recommended for troubleshooting)")
        
        if cloud_state.get('monitoring_interval', 0) == 0:
            issues.append("Enhanced monitoring not enabled")
        
        # Engine version check
        engine = cloud_state.get('engine', '')
        engine_version = cloud_state.get('engine_version', '')
        if engine and engine_version:
            # This is simplified - in reality you'd check against latest versions
            if '5.6' in engine_version or '9.6' in engine_version:
                health_score -= 0.1
                issues.append("Consider upgrading to newer engine version")
        
        # Calculate metrics
        metrics['security_features'] = sum([
            not cloud_state.get('publicly_accessible', False),
            cloud_state.get('storage_encrypted', False),
            cloud_state.get('deletion_protection', False),
            len(security_groups) > 0
        ])
        
        metrics['availability_features'] = sum([
            cloud_state.get('multi_az', False),
            backup_retention > 0,
            len(cloud_state.get('availability_zones', [])) > 1 if resource_type == 'db_cluster' else 0
        ])
        
        metrics['monitoring_features'] = sum([
            cloud_state.get('performance_insights_enabled', False),
            cloud_state.get('monitoring_interval', 0) > 0,
            bool(cloud_state.get('enhanced_monitoring_resource_arn'))
        ])
        
        if resource_type == 'db_cluster':
            metrics['cluster_members'] = len(cloud_state.get('db_cluster_members', []))
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate RDS-specific changes"""
        changes = {}
        
        # Instance class changes
        if current.get('db_instance_class') != desired.get('db_instance_class'):
            changes['db_instance_class'] = {
                'from': current.get('db_instance_class'),
                'to': desired.get('db_instance_class'),
                'requires': 'restart'
            }
        
        # Storage changes
        if current.get('allocated_storage') != desired.get('allocated_storage'):
            changes['allocated_storage'] = {
                'from': current.get('allocated_storage'),
                'to': desired.get('allocated_storage'),
                'requires': 'online_resize' if desired.get('allocated_storage', 0) > current.get('allocated_storage', 0) else 'not_supported'
            }
        
        # Multi-AZ changes
        if current.get('multi_az') != desired.get('multi_az'):
            changes['multi_az'] = {
                'from': current.get('multi_az'),
                'to': desired.get('multi_az'),
                'requires': 'restart'
            }
        
        # Security groups changes
        current_sgs = set(current.get('vpc_security_groups', []))
        desired_sgs = set(desired.get('vpc_security_groups', []))
        
        if current_sgs != desired_sgs:
            changes['vpc_security_groups'] = {
                'from': list(current_sgs),
                'to': list(desired_sgs),
                'requires': 'update'
            }
        
        # Backup retention changes
        if current.get('backup_retention_period') != desired.get('backup_retention_period'):
            changes['backup_retention_period'] = {
                'from': current.get('backup_retention_period'),
                'to': desired.get('backup_retention_period'),
                'requires': 'update'
            }
        
        # Engine version changes
        if current.get('engine_version') != desired.get('engine_version'):
            changes['engine_version'] = {
                'from': current.get('engine_version'),
                'to': desired.get('engine_version'),
                'requires': 'restart'
            }
        
        return changes