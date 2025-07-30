"""
GCP Cloud Monitoring Complete Implementation

Combines all Cloud Monitoring functionality through multiple inheritance:
- MonitoringCore: Core attributes and authentication
- MonitoringConfigurationMixin: Chainable configuration methods  
- MonitoringLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .monitoring_core import MonitoringCore
from .monitoring_configuration import MonitoringConfigurationMixin
from .monitoring_lifecycle import MonitoringLifecycleMixin


class CloudMonitoring(MonitoringLifecycleMixin, MonitoringConfigurationMixin, MonitoringCore):
    """
    Complete GCP Cloud Monitoring implementation for infrastructure monitoring and observability.
    
    This class combines:
    - Monitoring configuration methods (alerts, dashboards, uptime checks)
    - Monitoring lifecycle management (create, destroy, preview)
    - Custom metrics and notification management
    - Service Level Objectives (SLOs) and error budgets
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudMonitoring instance for infrastructure monitoring"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$15.00/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._monitoring_type = None
        self._auto_scaling_enabled = False
        self._high_availability_enabled = True
    
    def validate_configuration(self):
        """Validate the current Cloud Monitoring configuration"""
        errors = []
        warnings = []
        
        # Validate workspace ID
        if not self.workspace_id:
            errors.append("Workspace ID is required")
        
        # Validate alert policies
        for i, policy in enumerate(self.alert_policies):
            if not self._validate_alert_policy_config(policy):
                errors.append(f"Invalid alert policy at index {i}: {policy.get('display_name', 'Unknown')}")
        
        # Validate notification channels
        for i, channel in enumerate(self.notification_channels):
            if not self._validate_notification_channel_config(channel):
                errors.append(f"Invalid notification channel at index {i}: {channel.get('display_name', 'Unknown')}")
        
        # Validate uptime checks
        for check in self.uptime_checks:
            if not self._validate_uptime_check_config(check):
                errors.append(f"Invalid uptime check configuration: {check.get('display_name', 'Unknown')}")
        
        # Validate dashboards
        for dashboard in self.dashboards:
            if not self._validate_dashboard_config(dashboard):
                errors.append(f"Invalid dashboard configuration: {dashboard.get('display_name', 'Unknown')}")
        
        # Resource warnings
        if len(self.alert_policies) > 500:
            warnings.append(f"{len(self.alert_policies)} alert policies may impact performance")
        
        if len(self.uptime_checks) > 100:
            warnings.append(f"{len(self.uptime_checks)} uptime checks may exceed quotas")
        
        # Cost warnings
        estimated_cost = self._estimate_monitoring_cost()
        if estimated_cost > 100:
            warnings.append(f"High estimated cost: ${estimated_cost:.2f}/month")
        
        # Notification coverage
        if self.alert_policies and not self.notification_channels:
            warnings.append("Alert policies defined but no notification channels configured")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_monitoring_info(self):
        """Get complete information about the Cloud Monitoring configuration"""
        return {
            'monitoring_name': self.monitoring_name,
            'description': self.monitoring_description,
            'workspace_id': self.workspace_id,
            'project_id': self.project_id,
            'metrics_scope': self.metrics_scope,
            'retention_days': self.retention_days,
            'alert_policies_count': len(self.alert_policies),
            'alert_policies': self.alert_policies,
            'notification_channels_count': len(self.notification_channels),
            'notification_channels': self.notification_channels,
            'uptime_checks_count': len(self.uptime_checks),
            'uptime_checks': self.uptime_checks,
            'dashboards_count': len(self.dashboards),
            'dashboards': self.dashboards,
            'custom_metrics_count': len(self.custom_metrics),
            'custom_metrics': self.custom_metrics,
            'slos_count': len(self.slos),
            'slos': self.slos,
            'monitored_resources_count': len(self.monitored_resources),
            'monitored_resources': self.monitored_resources,
            'labels_count': len(self.monitoring_labels),
            'monitoring_exists': self.monitoring_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'monitoring_type': self._monitoring_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this monitoring configuration with a new name"""
        cloned_monitoring = CloudMonitoring(new_name)
        cloned_monitoring.monitoring_name = new_name
        cloned_monitoring.monitoring_description = self.monitoring_description
        cloned_monitoring.workspace_id = f"projects/{new_name}" if new_name else self.workspace_id
        cloned_monitoring.project_id = self.project_id
        cloned_monitoring.metrics_scope = self.metrics_scope
        cloned_monitoring.retention_days = self.retention_days
        cloned_monitoring.alert_policies = [policy.copy() for policy in self.alert_policies]
        cloned_monitoring.notification_channels = [channel.copy() for channel in self.notification_channels]
        cloned_monitoring.uptime_checks = [check.copy() for check in self.uptime_checks]
        cloned_monitoring.dashboards = [dashboard.copy() for dashboard in self.dashboards]
        cloned_monitoring.custom_metrics = [metric.copy() for metric in self.custom_metrics]
        cloned_monitoring.monitoring_labels = self.monitoring_labels.copy()
        return cloned_monitoring
    
    def export_configuration(self):
        """Export monitoring configuration for backup or migration"""
        return {
            'metadata': {
                'monitoring_name': self.monitoring_name,
                'workspace_id': self.workspace_id,
                'project_id': self.project_id,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'monitoring_name': self.monitoring_name,
                'description': self.monitoring_description,
                'workspace_id': self.workspace_id,
                'project_id': self.project_id,
                'metrics_scope': self.metrics_scope,
                'retention_days': self.retention_days,
                'alert_policies': self.alert_policies,
                'notification_channels': self.notification_channels,
                'uptime_checks': self.uptime_checks,
                'dashboards': self.dashboards,
                'custom_metrics': self.custom_metrics,
                'slos': self.slos,
                'monitored_resources': self.monitored_resources,
                'labels': self.monitoring_labels,
                'optimization_priority': self._optimization_priority,
                'monitoring_type': self._monitoring_type,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'high_availability_enabled': self._high_availability_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import monitoring configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.monitoring_name = config.get('monitoring_name', self.monitoring_name)
            self.monitoring_description = config.get('description', f"Monitoring workspace for {self.monitoring_name}")
            self.workspace_id = config.get('workspace_id')
            self.project_id = config.get('project_id')
            self.metrics_scope = config.get('metrics_scope', 'project')
            self.retention_days = config.get('retention_days', 30)
            self.alert_policies = config.get('alert_policies', [])
            self.notification_channels = config.get('notification_channels', [])
            self.uptime_checks = config.get('uptime_checks', [])
            self.dashboards = config.get('dashboards', [])
            self.custom_metrics = config.get('custom_metrics', [])
            self.slos = config.get('slos', [])
            self.monitored_resources = config.get('monitored_resources', [])
            self.monitoring_labels = config.get('labels', {})
            self._optimization_priority = config.get('optimization_priority')
            self._monitoring_type = config.get('monitoring_type')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
            self._high_availability_enabled = config.get('high_availability_enabled', True)
        
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling for monitoring resources"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for monitoring")
            print("   💡 Dynamic alert threshold adjustment configured")
            print("   💡 Auto-provisioning for high-volume metrics enabled")
        return self
    
    def enable_high_availability(self, enabled: bool = True):
        """Enable high availability for monitoring"""
        self._high_availability_enabled = enabled
        if enabled:
            print("🛡️ High availability enabled for monitoring")
            print("   💡 Multi-region monitoring configured")
            print("   💡 Redundant notification channels enabled")
        return self
    
    def get_alert_policy_by_name(self, name: str):
        """Get alert policy by display name"""
        for policy in self.alert_policies:
            if policy.get("display_name") == name:
                return policy
        return None
    
    def get_notification_channel_by_name(self, name: str):
        """Get notification channel by display name"""
        for channel in self.notification_channels:
            if channel.get("display_name") == name:
                return channel
        return None
    
    def get_uptime_check_by_name(self, name: str):
        """Get uptime check by display name"""
        for check in self.uptime_checks:
            if check.get("display_name") == name:
                return check
        return None
    
    def get_dashboard_by_name(self, name: str):
        """Get dashboard by display name"""
        for dashboard in self.dashboards:
            if dashboard.get("display_name") == name:
                return dashboard
        return None
    
    def remove_alert_policy(self, name: str):
        """Remove an alert policy by name"""
        self.alert_policies = [p for p in self.alert_policies if p.get("display_name") != name]
        print(f"🗑️  Removed alert policy '{name}'")
        return self
    
    def remove_notification_channel(self, name: str):
        """Remove a notification channel by name"""
        self.notification_channels = [c for c in self.notification_channels if c.get("display_name") != name]
        print(f"🗑️  Removed notification channel '{name}'")
        return self
    
    def remove_uptime_check(self, name: str):
        """Remove an uptime check by name"""
        self.uptime_checks = [c for c in self.uptime_checks if c.get("display_name") != name]
        print(f"🗑️  Removed uptime check '{name}'")
        return self
    
    def remove_dashboard(self, name: str):
        """Remove a dashboard by name"""
        self.dashboards = [d for d in self.dashboards if d.get("display_name") != name]
        print(f"🗑️  Removed dashboard '{name}'")
        return self
    
    def get_monitoring_summary(self):
        """Get a summary of the monitoring configuration"""
        return {
            "monitoring_name": self.monitoring_name,
            "workspace_id": self.workspace_id,
            "total_alert_policies": len(self.alert_policies),
            "total_notification_channels": len(self.notification_channels),
            "total_uptime_checks": len(self.uptime_checks),
            "total_dashboards": len(self.dashboards),
            "total_custom_metrics": len(self.custom_metrics),
            "total_slos": len(self.slos),
            "total_monitored_resources": len(self.monitored_resources),
            "retention_days": self.retention_days,
            "metrics_scope": self.metrics_scope,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "deployment_ready": self.deployment_ready
        }
    
    def get_health_status(self):
        """Get health status of the monitoring configuration"""
        status = {
            "overall_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check for common issues
        if not self.notification_channels and self.alert_policies:
            status["issues"].append("Alert policies exist but no notification channels configured")
            status["overall_status"] = "warning"
        
        if len(self.uptime_checks) == 0:
            status["recommendations"].append("Consider adding uptime checks for critical services")
        
        if len(self.dashboards) == 0:
            status["recommendations"].append("Consider creating dashboards for better visibility")
        
        if self.retention_days < 30:
            status["recommendations"].append("Consider increasing retention period for better historical analysis")
        
        # Check notification channel diversity
        channel_types = set(c.get("type") for c in self.notification_channels)
        if len(channel_types) == 1:
            status["recommendations"].append("Consider adding multiple notification channel types for redundancy")
        
        return status
    
    def apply_monitoring_best_practices(self):
        """Apply monitoring best practices to the configuration"""
        print("📊 Applying monitoring best practices")
        
        # Ensure basic notification channels
        if not any(c.get("type") == "email" for c in self.notification_channels):
            print("   💡 Adding email notification channel")
            self.email_notification("admin@example.com", "Admin Email")
        
        # Ensure basic uptime checks
        if len(self.uptime_checks) == 0:
            print("   💡 Adding basic uptime check")
            self.https_check("Basic Health Check", "https://example.com")
        
        # Ensure system monitoring
        has_cpu_alert = any("cpu" in p.get("display_name", "").lower() for p in self.alert_policies)
        if not has_cpu_alert:
            print("   💡 Adding CPU monitoring alert")
            self.cpu_alert("High CPU Usage", 0.8)
        
        has_memory_alert = any("memory" in p.get("display_name", "").lower() for p in self.alert_policies)
        if not has_memory_alert:
            print("   💡 Adding memory monitoring alert")
            self.memory_alert("High Memory Usage", 0.85)
        
        # Ensure minimum retention
        if self.retention_days < 30:
            print("   💡 Increasing retention to 30 days")
            self.retention_days = 30
        
        # Add monitoring labels
        self.monitoring_labels.update({
            "monitoring": "enabled",
            "best-practices": "applied",
            "managed-by": "infradsl"
        })
        print("   💡 Added monitoring best practice labels")
        
        return self
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown for monitoring"""
        breakdown = {
            "base_cost": 0.0,
            "alert_policies_cost": max(0, len(self.alert_policies) - 5) * 0.0,  # First 5 free
            "uptime_checks_cost": max(0, len(self.uptime_checks) - 3) * 1.0,   # First 3 free, $1 each after
            "custom_metrics_cost": len(self.custom_metrics) * 0.30,            # $0.30 per custom metric
            "api_calls_cost": 5.0,                                             # Estimated API calls
            "log_metrics_cost": len(self.log_based_metrics) * 0.50,           # $0.50 per log metric
            "total_cost": 0.0
        }
        
        breakdown["total_cost"] = sum([
            breakdown["base_cost"],
            breakdown["alert_policies_cost"],
            breakdown["uptime_checks_cost"],
            breakdown["custom_metrics_cost"],
            breakdown["api_calls_cost"],
            breakdown["log_metrics_cost"]
        ])
        
        return breakdown


# Convenience functions for creating CloudMonitoring instances
def create_web_app_monitoring(project_id: str, app_name: str, domain: str = None) -> CloudMonitoring:
    """Create monitoring configuration for a web application"""
    monitoring = CloudMonitoring(f"{app_name}-monitoring")
    monitoring.project(project_id).production_monitoring().web_app_monitoring(app_name, domain)
    return monitoring

def create_microservices_monitoring(project_id: str, service_name: str, function_name: str = None) -> CloudMonitoring:
    """Create monitoring configuration for microservices"""
    monitoring = CloudMonitoring(f"{service_name}-monitoring")
    monitoring.project(project_id).production_monitoring().microservices_monitoring(service_name, function_name)
    return monitoring

def create_infrastructure_monitoring(project_id: str) -> CloudMonitoring:
    """Create comprehensive infrastructure monitoring"""
    monitoring = CloudMonitoring(f"{project_id}-infrastructure-monitoring")
    monitoring.project(project_id).production_monitoring().infrastructure_monitoring()
    return monitoring

def create_database_monitoring(project_id: str, db_name: str, region: str = "us-central1") -> CloudMonitoring:
    """Create monitoring configuration for databases"""
    monitoring = CloudMonitoring(f"{db_name}-monitoring")
    monitoring.project(project_id).production_monitoring().database_monitoring(db_name, region)
    return monitoring

def create_development_monitoring(project_id: str) -> CloudMonitoring:
    """Create monitoring configuration for development environment"""
    monitoring = CloudMonitoring(f"{project_id}-dev-monitoring")
    monitoring.project(project_id).development_monitoring()
    return monitoring

# Aliases for backward compatibility
Monitoring = CloudMonitoring
GCPMonitoring = CloudMonitoring