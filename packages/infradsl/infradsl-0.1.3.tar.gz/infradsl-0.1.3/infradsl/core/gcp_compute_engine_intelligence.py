"""
GCP Compute Engine Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Compute Engine instances.
Extends the GCP intelligence base with Compute Engine-specific capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class ComputeEngineIntelligence(GCPIntelligenceBase):
    """Compute Engine-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(GCPResourceType.COMPUTE_ENGINE)
        self.compute_client = None
    
    def _initialize_service_client(self):
        """Initialize Compute Engine client"""
        try:
            from google.cloud import compute_v1
            self.compute_client = compute_v1.InstancesClient()
        except Exception as e:
            print(f"⚠️  Failed to create Compute Engine client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Compute Engine instances"""
        existing_instances = {}
        
        if not self._get_gcp_client():
            return existing_instances
        
        try:
            # Mock discovery for demonstration (in real implementation would use GCP APIs)
            # This would iterate through projects and zones to discover instances
            
            # For now, return empty dict - actual implementation would use:
            # request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
            # instances = self.compute_client.list(request=request)
            
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Compute Engine instances: {str(e)}")
        
        return existing_instances
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Compute Engine instance state"""
        return {
            'name': cloud_state.get('name'),
            'machine_type': cloud_state.get('machine_type'),
            'zone': cloud_state.get('zone'),
            'image': cloud_state.get('source_image'),
            'network_interfaces': cloud_state.get('network_interfaces', []),
            'service_accounts': cloud_state.get('service_accounts', []),
            'metadata': cloud_state.get('metadata', {}),
            'labels': cloud_state.get('labels', {}),
            'tags': cloud_state.get('tags', {}),
            'startup_script': cloud_state.get('metadata', {}).get('startup-script', ''),
            'preemptible': cloud_state.get('preemptible', False),
            'deletion_protection': cloud_state.get('deletion_protection', False)
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Compute Engine-specific fingerprint data"""
        fingerprint_data = {}
        
        # Machine type fingerprint
        machine_type = cloud_state.get('machine_type', '')
        if machine_type:
            fingerprint_data['machine_pattern'] = {
                'series': self._get_machine_series(machine_type),
                'is_custom': 'custom' in machine_type,
                'is_shared_cpu': machine_type.startswith(('f1', 'g1')),
                'is_standard': machine_type.startswith('n1-standard'),
                'is_high_memory': 'highmem' in machine_type,
                'is_high_cpu': 'highcpu' in machine_type,
                'generation': self._get_machine_generation(machine_type)
            }
        
        # Network configuration fingerprint
        network_interfaces = cloud_state.get('network_interfaces', [])
        fingerprint_data['network_pattern'] = {
            'interface_count': len(network_interfaces),
            'has_external_ip': any(
                'access_configs' in ni and ni['access_configs'] 
                for ni in network_interfaces
            ),
            'network_count': len(set(
                ni.get('network', '') for ni in network_interfaces
            )),
            'has_custom_network': any(
                not ni.get('network', '').endswith('/default') 
                for ni in network_interfaces
            )
        }
        
        # Compute features fingerprint
        fingerprint_data['compute_features'] = {
            'preemptible': cloud_state.get('preemptible', False),
            'deletion_protection': cloud_state.get('deletion_protection', False),
            'has_startup_script': bool(cloud_state.get('metadata', {}).get('startup-script')),
            'service_account_count': len(cloud_state.get('service_accounts', [])),
            'has_custom_service_account': any(
                not sa.get('email', '').endswith('-compute@developer.gserviceaccount.com')
                for sa in cloud_state.get('service_accounts', [])
            )
        }
        
        # Storage fingerprint
        disks = cloud_state.get('disks', [])
        fingerprint_data['storage_pattern'] = {
            'disk_count': len(disks),
            'has_additional_disks': len(disks) > 1,
            'disk_types': list(set(
                disk.get('type', 'pd-standard') for disk in disks
            )),
            'total_size_gb': sum(disk.get('size_gb', 0) for disk in disks)
        }
        
        return fingerprint_data
    
    def _get_machine_series(self, machine_type: str) -> str:
        """Get machine type series (n1, n2, e2, etc.)"""
        if '-' in machine_type:
            return machine_type.split('-')[0]
        return 'unknown'
    
    def _get_machine_generation(self, machine_type: str) -> str:
        """Get machine type generation"""
        series = self._get_machine_series(machine_type)
        generation_map = {
            'n1': 'first',
            'n2': 'second', 
            'n2d': 'second',
            'e2': 'second',
            'c2': 'second',
            'm1': 'first',
            'm2': 'second',
            'f1': 'first',
            'g1': 'first'
        }
        return generation_map.get(series, 'unknown')
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Compute Engine-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 120  # 2 minutes default for GCP
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Machine type changes
        current_machine = current.get('machine_type')
        desired_machine = desired.get('machine_type')
        
        if current_machine != desired_machine:
            changes.append("machine_type_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            downtime = 300  # 5 minutes for stop/start
            propagation_time = max(propagation_time, 600)
            rollback_complexity = "medium"
            
            # Calculate cost impact for GCP machine types
            cost_impact = self._estimate_machine_type_cost_impact(current_machine, desired_machine)
            
            recommendations.append("Machine type change requires instance stop/start")
            recommendations.append("Backup critical data before changing machine type")
            
            if cost_impact > 50:
                recommendations.append(f"WARNING: Cost increase of ~{cost_impact:.0f}%")
            elif cost_impact < -20:
                recommendations.append(f"Cost savings of ~{abs(cost_impact):.0f}% detected")
        
        # 2. Zone changes
        if current.get('zone') != desired.get('zone'):
            changes.append("zone_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            downtime = 900  # 15 minutes for recreation
            
            recommendations.append("CRITICAL: Zone change requires instance recreation")
            recommendations.append("All ephemeral data will be lost")
            recommendations.append("External IP address will change")
            
            affected_resources.append("persistent_disks")
            affected_resources.append("load_balancer_backends")
        
        # 3. Network interface changes
        current_networks = current.get('network_interfaces', [])
        desired_networks = desired.get('network_interfaces', [])
        
        if current_networks != desired_networks:
            changes.append("network_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            propagation_time = max(propagation_time, 300)
            
            # Check for external IP changes
            current_external = any('access_configs' in ni for ni in current_networks)
            desired_external = any('access_configs' in ni for ni in desired_networks)
            
            if current_external != desired_external:
                if desired_external:
                    recommendations.append("Adding external IP address")
                    cost_impact += 5  # External IP costs
                else:
                    recommendations.append("Removing external IP address")
                    recommendations.append("Ensure connectivity through other means")
            
            affected_resources.append("firewall_rules")
            affected_resources.append("load_balancers")
        
        # 4. Image changes
        if current.get('source_image') != desired.get('source_image'):
            changes.append("image_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            downtime = 600  # 10 minutes for recreation
            
            recommendations.append("CRITICAL: Image change requires instance recreation")
            recommendations.append("All local data will be lost")
            recommendations.append("Ensure data is stored on persistent disks")
        
        # 5. Preemptible changes
        if current.get('preemptible') != desired.get('preemptible'):
            changes.append("preemptible_modification")
            
            if desired.get('preemptible') and not current.get('preemptible'):
                # Changing to preemptible
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                cost_impact -= 80  # Up to 80% savings
                recommendations.append("Changing to preemptible: up to 80% cost savings")
                recommendations.append("WARNING: Instance can be terminated at any time")
                rollback_complexity = "high"  # Cannot change back without recreation
            else:
                # Changing from preemptible
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                cost_impact += 400  # Significant cost increase
                recommendations.append("Changing from preemptible: significant cost increase")
                recommendations.append("Improved reliability and availability")
        
        # 6. Service account changes
        current_sa = current.get('service_accounts', [])
        desired_sa = desired.get('service_accounts', [])
        
        if current_sa != desired_sa:
            changes.append("service_account_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            recommendations.append("Service account changes affect API access")
            recommendations.append("Test application permissions after change")
            
            affected_resources.append("iam_policies")
        
        # 7. Startup script changes
        current_script = current.get('metadata', {}).get('startup-script', '')
        desired_script = desired.get('startup_script', '')
        
        if current_script != desired_script:
            changes.append("startup_script_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            recommendations.append("Startup script changes take effect on next restart")
            recommendations.append("Consider testing script changes on staging instance")
        
        # 8. Deletion protection changes
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
                f"stackdriver_monitoring:{instance_name}",
                f"persistent_disks:{instance_name}",
                f"instance_groups:{instance_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "instance_update"
        
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
    
    def _estimate_machine_type_cost_impact(self, current_type: str, desired_type: str) -> float:
        """Estimate cost impact of machine type changes"""
        
        # Simplified cost estimation for GCP machine types
        cost_multipliers = {
            'f1-micro': 1, 'g1-small': 2,
            'n1-standard-1': 5, 'n1-standard-2': 10, 'n1-standard-4': 20, 'n1-standard-8': 40,
            'n2-standard-2': 12, 'n2-standard-4': 24, 'n2-standard-8': 48,
            'e2-micro': 1, 'e2-small': 2, 'e2-medium': 4, 'e2-standard-2': 8, 'e2-standard-4': 16,
            'c2-standard-4': 30, 'c2-standard-8': 60, 'c2-standard-16': 120,
            'n1-highmem-2': 15, 'n1-highmem-4': 30, 'n1-highmem-8': 60,
            'n1-highcpu-16': 35, 'n1-highcpu-32': 70
        }
        
        current_cost = cost_multipliers.get(current_type, 10)
        desired_cost = cost_multipliers.get(desired_type, 10)
        
        if current_cost == 0:
            return 0
        
        return ((desired_cost - current_cost) / current_cost) * 100
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Compute Engine instance health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Instance status check
        status = cloud_state.get('status', 'UNKNOWN')
        if status != 'RUNNING':
            health_score -= 0.3
            issues.append(f"Instance status: {status}")
        
        # Machine type appropriateness
        machine_type = cloud_state.get('machine_type', '')
        if machine_type.startswith('f1-micro'):
            issues.append("Very small instance (f1-micro) - consider upgrading for production")
        elif machine_type.startswith('n1-'):
            issues.append("Consider upgrading to newer generation (N2, E2) for better performance")
        
        # Network security checks
        network_interfaces = cloud_state.get('network_interfaces', [])
        has_external_ip = any('access_configs' in ni and ni['access_configs'] for ni in network_interfaces)
        
        if has_external_ip:
            health_score -= 0.1
            issues.append("Instance has external IP (consider using Cloud NAT for better security)")
        
        # Service account checks
        service_accounts = cloud_state.get('service_accounts', [])
        if not service_accounts:
            health_score -= 0.2
            issues.append("No service account configured (limited API access)")
        else:
            # Check for default service account
            default_sa = any(
                sa.get('email', '').endswith('-compute@developer.gserviceaccount.com')
                for sa in service_accounts
            )
            if default_sa:
                health_score -= 0.1
                issues.append("Using default service account (consider custom service account)")
        
        # Preemptible instance check
        if cloud_state.get('preemptible'):
            issues.append("Preemptible instance (can be terminated anytime)")
            metrics['is_preemptible'] = True
        else:
            metrics['is_preemptible'] = False
        
        # Deletion protection check
        if not cloud_state.get('deletion_protection'):
            health_score -= 0.1
            issues.append("Deletion protection not enabled")
        
        # Disk configuration check
        disks = cloud_state.get('disks', [])
        if not disks:
            health_score -= 0.2
            issues.append("No disks configured")
        else:
            ssd_disks = [d for d in disks if d.get('type', '').endswith('ssd')]
            if not ssd_disks:
                issues.append("Consider SSD persistent disks for better performance")
        
        # Startup script check
        startup_script = cloud_state.get('metadata', {}).get('startup-script', '')
        if startup_script:
            metrics['has_startup_script'] = True
        else:
            metrics['has_startup_script'] = False
            issues.append("No startup script configured")
        
        # Calculate feature metrics
        metrics['security_features'] = sum([
            not has_external_ip,
            bool(service_accounts),
            cloud_state.get('deletion_protection', False),
            len(network_interfaces) > 0
        ])
        
        metrics['performance_features'] = sum([
            not machine_type.startswith(('f1', 'g1')),  # Not shared CPU
            len([d for d in disks if 'ssd' in d.get('type', '')]) > 0,  # Has SSD
            not cloud_state.get('preemptible', False)  # Not preemptible
        ])
        
        metrics['network_interfaces'] = len(network_interfaces)
        metrics['disk_count'] = len(disks)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Compute Engine-specific changes"""
        changes = {}
        
        # Machine type changes
        if current.get('machine_type') != desired.get('machine_type'):
            changes['machine_type'] = {
                'from': current.get('machine_type'),
                'to': desired.get('machine_type'),
                'requires': 'restart'
            }
        
        # Zone changes
        if current.get('zone') != desired.get('zone'):
            changes['zone'] = {
                'from': current.get('zone'),
                'to': desired.get('zone'),
                'requires': 'recreation'
            }
        
        # Network interface changes
        if current.get('network_interfaces') != desired.get('network_interfaces'):
            changes['network_interfaces'] = {
                'from': current.get('network_interfaces'),
                'to': desired.get('network_interfaces'),
                'requires': 'restart'
            }
        
        # Image changes
        if current.get('source_image') != desired.get('source_image'):
            changes['source_image'] = {
                'from': current.get('source_image'),
                'to': desired.get('source_image'),
                'requires': 'recreation'
            }
        
        # Preemptible changes
        if current.get('preemptible') != desired.get('preemptible'):
            changes['preemptible'] = {
                'from': current.get('preemptible'),
                'to': desired.get('preemptible'),
                'requires': 'recreation'
            }
        
        # Service account changes
        if current.get('service_accounts') != desired.get('service_accounts'):
            changes['service_accounts'] = {
                'from': current.get('service_accounts'),
                'to': desired.get('service_accounts'),
                'requires': 'restart'
            }
        
        return changes