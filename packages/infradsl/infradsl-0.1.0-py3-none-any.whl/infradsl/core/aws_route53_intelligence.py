"""
Route53 Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Route53 DNS records.
Extends the AWS intelligence base with Route53-specific capabilities.
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


class Route53Intelligence(AWSIntelligenceBase):
    """Route53-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(ResourceType.ROUTE53_RECORD)
        self.route53_client = None
    
    def _get_route53_client(self):
        """Get Route53 client with error handling"""
        if not self.route53_client:
            try:
                self.route53_client = boto3.client('route53')
            except (NoCredentialsError, Exception) as e:
                print(f"⚠️  Failed to create Route53 client: {e}")
                return None
        return self.route53_client
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Route53 hosted zones and records"""
        existing_resources = {}
        
        client = self._get_route53_client()
        if not client:
            return existing_resources
        
        try:
            # Get all hosted zones
            paginator = client.get_paginator('list_hosted_zones')
            
            for page in paginator.paginate():
                for zone in page.get('HostedZones', []):
                    zone_id = zone['Id'].replace('/hostedzone/', '')
                    
                    try:
                        # Get records for this zone
                        zone_records = self._get_zone_records(zone_id)
                        
                        zone_data = {
                            'zone_id': zone_id,
                            'name': zone['Name'].rstrip('.'),
                            'type': 'hosted_zone',
                            'config': zone.get('Config', {}),
                            'resource_record_count': zone.get('ResourceRecordSetCount', 0),
                            'caller_reference': zone.get('CallerReference', ''),
                            'records': zone_records,
                            'tags': self._get_zone_tags(zone_id)
                        }
                        
                        existing_resources[zone_id] = zone_data
                        
                        # Also add individual records as separate resources
                        for record in zone_records:
                            record_key = f"{record['name']}_{record['type']}_{zone_id}"
                            existing_resources[record_key] = {
                                **record,
                                'zone_id': zone_id,
                                'zone_name': zone['Name'].rstrip('.'),
                                'type': 'dns_record'
                            }
                            
                    except Exception as e:
                        print(f"⚠️  Failed to get records for zone {zone_id}: {str(e)}")
                        existing_resources[zone_id] = {
                            'zone_id': zone_id,
                            'name': zone['Name'].rstrip('.'),
                            'type': 'hosted_zone',
                            'error': str(e)
                        }
        
        except Exception as e:
            print(f"⚠️  Failed to discover Route53 resources: {str(e)}")
        
        return existing_resources
    
    def _get_zone_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """Get all records for a hosted zone"""
        client = self._get_route53_client()
        records = []
        
        try:
            paginator = client.get_paginator('list_resource_record_sets')
            
            for page in paginator.paginate(HostedZoneId=zone_id):
                for record_set in page.get('ResourceRecordSets', []):
                    record_data = {
                        'name': record_set['Name'].rstrip('.'),
                        'type': record_set['Type'],
                        'ttl': record_set.get('TTL'),
                        'resource_records': record_set.get('ResourceRecords', []),
                        'alias_target': record_set.get('AliasTarget'),
                        'weight': record_set.get('Weight'),
                        'set_identifier': record_set.get('SetIdentifier'),
                        'failover': record_set.get('Failover'),
                        'geo_location': record_set.get('GeoLocation'),
                        'health_check_id': record_set.get('HealthCheckId'),
                        'traffic_policy_instance_id': record_set.get('TrafficPolicyInstanceId')
                    }
                    records.append(record_data)
                    
        except Exception as e:
            print(f"⚠️  Error getting records for zone {zone_id}: {str(e)}")
        
        return records
    
    def _get_zone_tags(self, zone_id: str) -> Dict[str, str]:
        """Get tags for a hosted zone"""
        client = self._get_route53_client()
        tags = {}
        
        try:
            response = client.list_tags_for_resource(
                ResourceType='hostedzone',
                ResourceId=zone_id
            )
            
            tag_set = response.get('ResourceTagSet', {}).get('Tags', [])
            tags = {tag['Key']: tag['Value'] for tag in tag_set}
            
        except Exception as e:
            print(f"⚠️  Error getting tags for zone {zone_id}: {str(e)}")
        
        return tags
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Route53 resource state"""
        if cloud_state.get('type') == 'hosted_zone':
            return {
                'zone_id': cloud_state.get('zone_id'),
                'name': cloud_state.get('name'),
                'private_zone': cloud_state.get('config', {}).get('PrivateZone', False),
                'record_count': cloud_state.get('resource_record_count', 0),
                'caller_reference': cloud_state.get('caller_reference'),
                'tags': cloud_state.get('tags', {})
            }
        else:  # DNS record
            return {
                'name': cloud_state.get('name'),
                'type': cloud_state.get('type'),
                'ttl': cloud_state.get('ttl'),
                'is_alias': bool(cloud_state.get('alias_target')),
                'has_health_check': bool(cloud_state.get('health_check_id')),
                'routing_policy': self._determine_routing_policy(cloud_state),
                'zone_id': cloud_state.get('zone_id')
            }
    
    def _determine_routing_policy(self, record_data: Dict[str, Any]) -> str:
        """Determine the routing policy for a record"""
        if record_data.get('weight') is not None:
            return 'weighted'
        elif record_data.get('failover'):
            return 'failover'
        elif record_data.get('geo_location'):
            return 'geolocation'
        elif record_data.get('set_identifier'):
            return 'latency'
        else:
            return 'simple'
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Route53-specific fingerprint data"""
        fingerprint_data = {}
        
        if cloud_state.get('type') == 'hosted_zone':
            # Hosted zone fingerprinting
            zone_name = cloud_state.get('name', '')
            
            fingerprint_data['zone_pattern'] = {
                'is_subdomain': '.' in zone_name and not zone_name.endswith('.com'),
                'tld': zone_name.split('.')[-1] if '.' in zone_name else '',
                'is_private': cloud_state.get('config', {}).get('PrivateZone', False),
                'record_count_range': self._categorize_record_count(
                    cloud_state.get('resource_record_count', 0)
                )
            }
            
            # Record type distribution
            records = cloud_state.get('records', [])
            record_types = [r.get('type') for r in records]
            fingerprint_data['record_distribution'] = {
                'has_mx': 'MX' in record_types,
                'has_txt': 'TXT' in record_types,
                'has_cname': 'CNAME' in record_types,
                'has_alias': any(r.get('alias_target') for r in records),
                'total_types': len(set(record_types))
            }
            
        else:
            # DNS record fingerprinting
            fingerprint_data['record_pattern'] = {
                'record_type': cloud_state.get('type'),
                'is_apex': cloud_state.get('name', '') == cloud_state.get('zone_name', ''),
                'is_wildcard': cloud_state.get('name', '').startswith('*'),
                'is_alias': bool(cloud_state.get('alias_target')),
                'routing_policy': self._determine_routing_policy(cloud_state),
                'has_health_check': bool(cloud_state.get('health_check_id'))
            }
            
            # TTL patterns
            ttl = cloud_state.get('ttl', 300)
            fingerprint_data['ttl_pattern'] = {
                'ttl_category': self._categorize_ttl(ttl),
                'is_custom_ttl': ttl not in [300, 600, 3600, 86400],
                'is_low_ttl': ttl < 300,
                'is_high_ttl': ttl > 86400
            }
        
        return fingerprint_data
    
    def _categorize_record_count(self, count: int) -> str:
        """Categorize record count for fingerprinting"""
        if count <= 5:
            return 'minimal'
        elif count <= 20:
            return 'small'
        elif count <= 50:
            return 'medium'
        else:
            return 'large'
    
    def _categorize_ttl(self, ttl: Optional[int]) -> str:
        """Categorize TTL for fingerprinting"""
        if ttl is None:
            return 'alias'
        elif ttl <= 300:
            return 'short'
        elif ttl <= 3600:
            return 'standard'
        elif ttl <= 86400:
            return 'long'
        else:
            return 'very_long'
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Route53-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 300  # 5 minutes for DNS propagation
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        resource_type = current.get('type') or desired.get('type')
        
        if resource_type == 'hosted_zone':
            # Hosted zone changes
            if not current.get('exists', True) and desired.get('exists', True):
                changes.append("zone_creation")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                propagation_time = max(propagation_time, 172800)  # 48 hours for NS propagation
                recommendations.append("Update domain registrar NS records to point to new zone")
                recommendations.append("DNS propagation may take up to 48 hours")
                cost_impact = 0.50  # $0.50 per month per zone
                
        else:
            # DNS record changes
            
            # 1. Record type changes
            if current.get('type') != desired.get('type'):
                changes.append("record_type_modification")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                propagation_time = max(propagation_time, 3600)  # 1 hour
                recommendations.append("Record type changes may cause temporary resolution failures")
                recommendations.append("Consider creating new record before deleting old one")
                rollback_complexity = "medium"
            
            # 2. TTL changes
            current_ttl = current.get('ttl', 300)
            desired_ttl = desired.get('ttl', 300)
            
            if current_ttl != desired_ttl:
                changes.append("ttl_modification")
                
                if desired_ttl > current_ttl:
                    # Increasing TTL
                    impact_level = ChangeImpact.LOW if impact_level.value < ChangeImpact.LOW.value else impact_level
                    propagation_time = max(propagation_time, current_ttl)
                    recommendations.append("TTL increase will take effect gradually")
                else:
                    # Decreasing TTL
                    impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                    propagation_time = max(propagation_time, current_ttl)
                    recommendations.append("TTL decrease requires waiting for current TTL to expire")
            
            # 3. Alias target changes
            current_alias = current.get('alias_target')
            desired_alias = desired.get('alias_target')
            
            if current_alias != desired_alias:
                changes.append("alias_target_modification")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                propagation_time = max(propagation_time, 900)  # 15 minutes
                recommendations.append("Verify target resource is healthy before switching")
                
                if current_alias and not desired_alias:
                    recommendations.append("Converting from alias to regular record")
                elif not current_alias and desired_alias:
                    recommendations.append("Converting from regular record to alias")
            
            # 4. Resource record changes
            current_records = current.get('resource_records', [])
            desired_records = desired.get('resource_records', [])
            
            if current_records != desired_records:
                changes.append("resource_records_modification")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                
                # Check if it's an IP address change
                record_type = current.get('type') or desired.get('type')
                if record_type in ['A', 'AAAA']:
                    recommendations.append("IP address changes will affect all clients")
                    affected_resources.append("load_balancers")
                    affected_resources.append("cloudfront_distributions")
                elif record_type == 'CNAME':
                    recommendations.append("CNAME changes redirect traffic to different targets")
                elif record_type == 'MX':
                    recommendations.append("MX record changes affect email delivery")
                    impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            # 5. Routing policy changes
            current_policy = self._determine_routing_policy(current)
            desired_policy = self._determine_routing_policy(desired)
            
            if current_policy != desired_policy:
                changes.append("routing_policy_modification")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                recommendations.append("Routing policy changes affect traffic distribution")
                recommendations.append("Monitor traffic patterns after deployment")
                rollback_complexity = "medium"
            
            # 6. Health check changes
            if current.get('health_check_id') != desired.get('health_check_id'):
                changes.append("health_check_modification")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                
                if desired.get('health_check_id') and not current.get('health_check_id'):
                    recommendations.append("Adding health check improves reliability")
                    cost_impact += 0.50  # Health check costs
                elif not desired.get('health_check_id') and current.get('health_check_id'):
                    recommendations.append("Removing health check reduces failover capabilities")
        
        # Calculate DNS query cost impact
        if 'record_creation' in changes or 'zone_creation' in changes:
            cost_impact += 0.01  # Minimal query costs
        
        # Find affected resources
        record_name = current.get('name') or desired.get('name')
        if record_name:
            affected_resources.extend([
                f"applications_using_{record_name}",
                f"ssl_certificates_{record_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "dns_update"
        
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
        """Check Route53 resource health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        resource_type = cloud_state.get('type')
        
        if resource_type == 'hosted_zone':
            # Hosted zone health checks
            record_count = cloud_state.get('resource_record_count', 0)
            
            if record_count == 0:
                health_score -= 0.5
                issues.append("Hosted zone has no records")
            elif record_count < 2:
                health_score -= 0.2
                issues.append("Very few DNS records (consider adding MX, TXT records)")
            
            # Check for common record types
            records = cloud_state.get('records', [])
            record_types = [r.get('type') for r in records]
            
            if 'MX' not in record_types:
                issues.append("No MX records (email delivery not configured)")
            
            if 'TXT' not in record_types:
                issues.append("No TXT records (consider SPF, DKIM for email security)")
            
            # Check for alias records
            alias_count = sum(1 for r in records if r.get('alias_target'))
            metrics['alias_records'] = alias_count
            metrics['total_records'] = len(records)
            
            if alias_count == 0 and len(records) > 5:
                issues.append("Consider using alias records for AWS resources")
            
        else:
            # DNS record health checks
            record_type = cloud_state.get('type')
            ttl = cloud_state.get('ttl')
            
            # TTL checks
            if ttl and ttl < 60:
                health_score -= 0.2
                issues.append("Very low TTL may cause high query costs")
            elif ttl and ttl > 604800:  # 1 week
                health_score -= 0.1
                issues.append("Very high TTL reduces flexibility")
            
            # Record type specific checks
            if record_type == 'A':
                records = cloud_state.get('resource_records', [])
                if len(records) > 1:
                    metrics['ip_count'] = len(records)
                    issues.append("Multiple A records provide basic load balancing")
                    
            elif record_type == 'CNAME':
                record_name = cloud_state.get('name', '')
                zone_name = cloud_state.get('zone_name', '')
                
                if record_name == zone_name:
                    health_score -= 0.4
                    issues.append("CNAME at apex not allowed (use alias record instead)")
            
            # Health check verification
            if cloud_state.get('health_check_id'):
                metrics['has_health_check'] = True
                health_score += 0.1  # Bonus for health checking
            else:
                metrics['has_health_check'] = False
                if record_type in ['A', 'AAAA'] and cloud_state.get('routing_policy') != 'simple':
                    issues.append("Complex routing without health checks reduces reliability")
            
            # Alias record benefits
            if cloud_state.get('alias_target'):
                metrics['is_alias'] = True
                health_score += 0.05  # Small bonus for using alias
            else:
                metrics['is_alias'] = False
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Route53-specific changes"""
        changes = {}
        
        # Record type changes
        if current.get('type') != desired.get('type'):
            changes['record_type'] = {
                'from': current.get('type'),
                'to': desired.get('type'),
                'requires': 'recreation'
            }
        
        # TTL changes
        if current.get('ttl') != desired.get('ttl'):
            changes['ttl'] = {
                'from': current.get('ttl'),
                'to': desired.get('ttl'),
                'requires': 'update'
            }
        
        # Resource records changes
        if current.get('resource_records') != desired.get('resource_records'):
            changes['resource_records'] = {
                'from': current.get('resource_records'),
                'to': desired.get('resource_records'),
                'requires': 'update'
            }
        
        # Alias target changes
        if current.get('alias_target') != desired.get('alias_target'):
            changes['alias_target'] = {
                'from': current.get('alias_target'),
                'to': desired.get('alias_target'),
                'requires': 'update'
            }
        
        # Health check changes
        if current.get('health_check_id') != desired.get('health_check_id'):
            changes['health_check'] = {
                'from': current.get('health_check_id'),
                'to': desired.get('health_check_id'),
                'requires': 'update'
            }
        
        return changes