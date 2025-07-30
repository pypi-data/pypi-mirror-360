"""
GCP Cloud DNS Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Cloud DNS zones and records.
Extends the GCP intelligence base with Cloud DNS-specific capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class CloudDNSIntelligence(GCPIntelligenceBase):
    """Cloud DNS-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(GCPResourceType.CLOUD_DNS)
        self.dns_client = None
    
    def _initialize_service_client(self):
        """Initialize Cloud DNS client"""
        try:
            from google.cloud import dns
            self.dns_client = dns.Client()
        except Exception as e:
            print(f"⚠️  Failed to create Cloud DNS client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Cloud DNS zones and records"""
        existing_zones = {}
        
        if not self._get_gcp_client():
            return existing_zones
        
        try:
            # Mock discovery for demonstration
            # In real implementation would use: self.dns_client.list_zones()
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Cloud DNS zones: {str(e)}")
        
        return existing_zones
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Cloud DNS zone/record state"""
        return {
            'name': cloud_state.get('name'),
            'dns_name': cloud_state.get('dns_name'),
            'description': cloud_state.get('description'),
            'visibility': cloud_state.get('visibility', 'public'),
            'name_servers': cloud_state.get('name_servers', []),
            'creation_time': cloud_state.get('creation_time'),
            'dnssec_config': cloud_state.get('dnssec_config', {}),
            'private_visibility_config': cloud_state.get('private_visibility_config', {}),
            'forwarding_config': cloud_state.get('forwarding_config', {}),
            'peering_config': cloud_state.get('peering_config', {}),
            'records': cloud_state.get('records', []),
            'labels': cloud_state.get('labels', {}),
            'reverse_lookup': cloud_state.get('reverse_lookup', False),
            'service_directory_config': cloud_state.get('service_directory_config', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cloud DNS-specific fingerprint data"""
        fingerprint_data = {}
        
        # Zone type and visibility fingerprint
        visibility = cloud_state.get('visibility', 'public')
        dns_name = cloud_state.get('dns_name', '')
        
        fingerprint_data['zone_pattern'] = {
            'visibility': visibility,
            'is_public': visibility == 'public',
            'is_private': visibility == 'private',
            'dns_name': dns_name,
            'is_root_domain': dns_name.count('.') == 1,
            'is_subdomain': dns_name.count('.') > 1,
            'is_reverse_lookup': cloud_state.get('reverse_lookup', False),
            'has_description': bool(cloud_state.get('description'))
        }
        
        # DNSSEC configuration fingerprint
        dnssec_config = cloud_state.get('dnssec_config', {})
        fingerprint_data['security_pattern'] = {
            'dnssec_enabled': dnssec_config.get('state') == 'on',
            'dnssec_state': dnssec_config.get('state', 'off'),
            'key_signing_key_algorithm': dnssec_config.get('default_key_specs', [{}])[0].get('algorithm') if dnssec_config.get('default_key_specs') else None,
            'zone_signing_key_algorithm': dnssec_config.get('default_key_specs', [{}])[1].get('algorithm') if len(dnssec_config.get('default_key_specs', [])) > 1 else None,
            'non_existence': dnssec_config.get('non_existence', 'nsec3')
        }
        
        # Private zone configuration fingerprint
        private_config = cloud_state.get('private_visibility_config', {})
        fingerprint_data['private_pattern'] = {
            'has_private_networks': len(private_config.get('networks', [])) > 0,
            'network_count': len(private_config.get('networks', [])),
            'gke_clusters_count': len(private_config.get('gke_clusters', [])) if private_config.get('gke_clusters') else 0,
            'has_gke_clusters': bool(private_config.get('gke_clusters'))
        }
        
        # Forwarding and peering configuration fingerprint
        forwarding_config = cloud_state.get('forwarding_config', {})
        peering_config = cloud_state.get('peering_config', {})
        
        fingerprint_data['routing_pattern'] = {
            'has_forwarding': bool(forwarding_config.get('target_name_servers')),
            'forwarding_targets_count': len(forwarding_config.get('target_name_servers', [])),
            'has_peering': bool(peering_config.get('target_network')),
            'peering_network': peering_config.get('target_network')
        }
        
        # DNS records fingerprint
        records = cloud_state.get('records', [])
        fingerprint_data['records_pattern'] = {
            'total_records': len(records),
            'record_types': list(set(record.get('type', '') for record in records)),
            'has_a_records': any(record.get('type') == 'A' for record in records),
            'has_aaaa_records': any(record.get('type') == 'AAAA' for record in records),
            'has_cname_records': any(record.get('type') == 'CNAME' for record in records),
            'has_mx_records': any(record.get('type') == 'MX' for record in records),
            'has_txt_records': any(record.get('type') == 'TXT' for record in records),
            'has_srv_records': any(record.get('type') == 'SRV' for record in records),
            'has_ns_records': any(record.get('type') == 'NS' for record in records),
            'has_ptr_records': any(record.get('type') == 'PTR' for record in records),
            'has_soa_record': any(record.get('type') == 'SOA' for record in records),
            'wildcard_records': len([r for r in records if r.get('name', '').startswith('*')])
        }
        
        # Service Directory integration fingerprint
        service_dir_config = cloud_state.get('service_directory_config', {})
        fingerprint_data['service_directory_pattern'] = {
            'has_service_directory': bool(service_dir_config.get('namespace')),
            'namespace': service_dir_config.get('namespace')
        }
        
        return fingerprint_data
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Cloud DNS-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0  # DNS changes are generally zero-downtime
        propagation_time = 300  # 5 minutes for DNS propagation
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Zone visibility changes
        current_visibility = current.get('visibility', 'public')
        desired_visibility = desired.get('visibility', 'public')
        
        if current_visibility != desired_visibility:
            changes.append("visibility_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: Changing zone visibility requires recreation")
            recommendations.append("All DNS records will be temporarily unavailable")
            
            if desired_visibility == 'private' and current_visibility == 'public':
                recommendations.append("Making zone private - configure VPC networks for access")
                affected_resources.append("vpc_networks")
            else:
                recommendations.append("Making zone public - ensure security implications are understood")
        
        # 2. DNSSEC configuration changes
        current_dnssec = current.get('dnssec_config', {}).get('state', 'off')
        desired_dnssec = desired.get('dnssec_config', {}).get('state', 'off')
        
        if current_dnssec != desired_dnssec:
            changes.append("dnssec_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 900)  # 15 minutes for DNSSEC propagation
            
            if desired_dnssec == 'on' and current_dnssec == 'off':
                recommendations.append("Enabling DNSSEC improves DNS security")
                recommendations.append("DNSSEC propagation can take up to 15 minutes")
                recommendations.append("Ensure parent zone supports DNSSEC")
            else:
                recommendations.append("Disabling DNSSEC reduces security")
                recommendations.append("Remove DS records from parent zone first")
        
        # 3. Private network configuration changes
        current_networks = current.get('private_visibility_config', {}).get('networks', [])
        desired_networks = desired.get('private_visibility_config', {}).get('networks', [])
        
        if current_networks != desired_networks:
            changes.append("private_networks_modification")
            
            if len(desired_networks) > len(current_networks):
                recommendations.append("Adding VPC networks to private zone")
                recommendations.append("DNS will become available in new networks")
            else:
                recommendations.append("Removing VPC networks from private zone")
                recommendations.append("DNS will become unavailable in removed networks")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            affected_resources.extend([f"vpc_network:{net.get('network_url', '')}" for net in desired_networks])
        
        # 4. Forwarding configuration changes
        current_forwarding = current.get('forwarding_config', {})
        desired_forwarding = desired.get('forwarding_config', {})
        
        if current_forwarding != desired_forwarding:
            changes.append("forwarding_configuration_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired_forwarding and not current_forwarding:
                recommendations.append("Setting up DNS forwarding to external resolvers")
                recommendations.append("Queries will be forwarded to specified name servers")
            elif not desired_forwarding and current_forwarding:
                recommendations.append("Removing DNS forwarding configuration")
                recommendations.append("Zone will handle queries locally")
        
        # 5. Peering configuration changes
        current_peering = current.get('peering_config', {})
        desired_peering = desired.get('peering_config', {})
        
        if current_peering != desired_peering:
            changes.append("peering_configuration_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired_peering and not current_peering:
                target_network = desired_peering.get('target_network', '')
                recommendations.append(f"Setting up DNS peering with {target_network}")
                affected_resources.append(f"vpc_network:{target_network}")
            elif not desired_peering and current_peering:
                recommendations.append("Removing DNS peering configuration")
        
        # 6. DNS records changes
        current_records = current.get('records', [])
        desired_records = desired.get('records', [])
        
        if current_records != desired_records:
            changes.append("dns_records_modification")
            
            current_record_count = len(current_records)
            desired_record_count = len(desired_records)
            
            if desired_record_count > current_record_count:
                new_records = desired_record_count - current_record_count
                recommendations.append(f"Adding {new_records} DNS records")
                cost_impact += new_records * 0.02  # Rough cost per record
            elif desired_record_count < current_record_count:
                removed_records = current_record_count - desired_record_count
                recommendations.append(f"Removing {removed_records} DNS records")
                cost_impact -= removed_records * 0.02
            
            # Check for critical record changes
            current_a_records = [r for r in current_records if r.get('type') == 'A']
            desired_a_records = [r for r in desired_records if r.get('type') == 'A']
            
            if len(current_a_records) != len(desired_a_records):
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                recommendations.append("A record changes affect application availability")
            
            # Check for wildcard records
            wildcard_records = [r for r in desired_records if r.get('name', '').startswith('*')]
            if wildcard_records:
                recommendations.append("Wildcard records affect subdomain resolution")
        
        # 7. Service Directory configuration changes
        current_service_dir = current.get('service_directory_config', {})
        desired_service_dir = desired.get('service_directory_config', {})
        
        if current_service_dir != desired_service_dir:
            changes.append("service_directory_modification")
            
            if desired_service_dir and not current_service_dir:
                recommendations.append("Integrating with Service Directory")
                affected_resources.append("service_directory_namespaces")
            elif not desired_service_dir and current_service_dir:
                recommendations.append("Removing Service Directory integration")
        
        # 8. Zone name changes (not allowed)
        if current.get('dns_name') != desired.get('dns_name'):
            changes.append("dns_name_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: DNS zone name cannot be changed")
            recommendations.append("Requires creating new zone and migrating records")
            recommendations.append("Update NS records in parent zone")
        
        # Find affected resources
        zone_name = current.get('name') or desired.get('name')
        dns_name = current.get('dns_name') or desired.get('dns_name')
        if zone_name:
            affected_resources.extend([
                f"applications_using_dns:{dns_name}",
                f"certificates_for_domain:{dns_name}",
                f"load_balancers_for_domain:{dns_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "dns_zone_update"
        
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
        """Check Cloud DNS zone health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Zone visibility and accessibility
        visibility = cloud_state.get('visibility', 'public')
        
        # DNSSEC configuration check
        dnssec_config = cloud_state.get('dnssec_config', {})
        dnssec_enabled = dnssec_config.get('state') == 'on'
        
        if not dnssec_enabled and visibility == 'public':
            health_score -= 0.2
            issues.append("DNSSEC not enabled for public zone (security risk)")
        
        # Private zone network configuration
        if visibility == 'private':
            private_config = cloud_state.get('private_visibility_config', {})
            networks = private_config.get('networks', [])
            
            if not networks:
                health_score -= 0.3
                issues.append("Private zone has no associated VPC networks")
            elif len(networks) == 1:
                issues.append("Private zone has only one VPC network (consider redundancy)")
        
        # DNS records analysis
        records = cloud_state.get('records', [])
        
        # Check for essential records
        record_types = [record.get('type') for record in records]
        
        if 'SOA' not in record_types:
            health_score -= 0.3
            issues.append("Missing SOA record (required for DNS zone)")
        
        if 'NS' not in record_types:
            health_score -= 0.2
            issues.append("Missing NS records (affects delegation)")
        
        # Check for A/AAAA records for main domain
        dns_name = cloud_state.get('dns_name', '')
        root_a_records = [r for r in records if r.get('name') == dns_name and r.get('type') == 'A']
        root_aaaa_records = [r for r in records if r.get('name') == dns_name and r.get('type') == 'AAAA']
        
        if not root_a_records and not root_aaaa_records:
            issues.append("No A or AAAA records for root domain")
        
        # Check for common security records
        txt_records = [r for r in records if r.get('type') == 'TXT']
        spf_records = [r for r in txt_records if 'spf' in r.get('rrdatas', [''])[0].lower()]
        dmarc_records = [r for r in records if r.get('name', '').startswith('_dmarc')]
        
        if not spf_records:
            issues.append("No SPF record found (email security)")
        
        if not dmarc_records:
            issues.append("No DMARC record found (email security)")
        
        # Check for wildcard records (potential security risk)
        wildcard_records = [r for r in records if r.get('name', '').startswith('*')]
        if wildcard_records:
            health_score -= 0.1
            issues.append(f"{len(wildcard_records)} wildcard records found (review for security)")
        
        # TTL analysis
        low_ttl_records = [r for r in records if r.get('ttl', 300) < 60]
        high_ttl_records = [r for r in records if r.get('ttl', 300) > 86400]
        
        if low_ttl_records:
            issues.append(f"{len(low_ttl_records)} records with very low TTL (< 60s)")
        
        if high_ttl_records:
            issues.append(f"{len(high_ttl_records)} records with very high TTL (> 24h)")
        
        # Forwarding/Peering configuration health
        forwarding_config = cloud_state.get('forwarding_config', {})
        peering_config = cloud_state.get('peering_config', {})
        
        if forwarding_config and peering_config:
            health_score -= 0.2
            issues.append("Both forwarding and peering configured (potential conflict)")
        
        # Service Directory integration
        service_dir_config = cloud_state.get('service_directory_config', {})
        if service_dir_config:
            metrics['has_service_directory'] = True
        else:
            metrics['has_service_directory'] = False
        
        # Calculate feature metrics
        metrics['security_features'] = sum([
            dnssec_enabled,
            len(spf_records) > 0,
            len(dmarc_records) > 0,
            len(wildcard_records) == 0,
            visibility == 'private'  # Private zones are more secure
        ])
        
        metrics['performance_features'] = sum([
            len([r for r in records if r.get('ttl', 300) >= 300]) > 0,  # Reasonable TTLs
            len(records) > 0,  # Has actual records
            bool(forwarding_config or peering_config),  # Has routing config
            len(networks) > 1 if visibility == 'private' else True  # Multiple networks for private
        ])
        
        metrics['record_count'] = len(records)
        metrics['record_types'] = len(set(record_types))
        metrics['dnssec_enabled'] = dnssec_enabled
        metrics['wildcard_record_count'] = len(wildcard_records)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Cloud DNS-specific changes"""
        changes = {}
        
        # Visibility changes
        if current.get('visibility') != desired.get('visibility'):
            changes['visibility'] = {
                'from': current.get('visibility'),
                'to': desired.get('visibility'),
                'requires': 'recreation'
            }
        
        # DNSSEC changes
        current_dnssec = current.get('dnssec_config', {}).get('state', 'off')
        desired_dnssec = desired.get('dnssec_config', {}).get('state', 'off')
        
        if current_dnssec != desired_dnssec:
            changes['dnssec'] = {
                'from': current_dnssec,
                'to': desired_dnssec,
                'requires': 'update'
            }
        
        # Private network changes
        current_networks = current.get('private_visibility_config', {}).get('networks', [])
        desired_networks = desired.get('private_visibility_config', {}).get('networks', [])
        
        if current_networks != desired_networks:
            changes['private_networks'] = {
                'from': current_networks,
                'to': desired_networks,
                'requires': 'update'
            }
        
        # DNS records changes
        if current.get('records') != desired.get('records'):
            changes['records'] = {
                'from': current.get('records'),
                'to': desired.get('records'),
                'requires': 'update'
            }
        
        # Forwarding configuration changes
        if current.get('forwarding_config') != desired.get('forwarding_config'):
            changes['forwarding_config'] = {
                'from': current.get('forwarding_config'),
                'to': desired.get('forwarding_config'),
                'requires': 'update'
            }
        
        return changes