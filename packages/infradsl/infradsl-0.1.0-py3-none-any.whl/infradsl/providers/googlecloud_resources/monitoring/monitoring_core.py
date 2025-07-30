"""
GCP Cloud Monitoring Core Implementation

Core attributes and authentication for Google Cloud Monitoring.
Provides the foundation for the modular monitoring and observability system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class MonitoringCore(BaseGcpResource):
    """
    Core class for Google Cloud Monitoring functionality.
    
    This class provides:
    - Basic monitoring attributes and configuration
    - Authentication setup
    - Common utilities for monitoring operations
    - Alerting and dashboard management foundations
    """
    
    def __init__(self, name: str):
        """Initialize monitoring core with workspace name"""
        super().__init__(name)
        
        # Core monitoring attributes
        self.monitoring_name = name
        self.monitoring_description = f"Monitoring workspace for {name}"
        self.workspace_id = None
        self.project_id = None
        
        # Monitoring configuration
        self.metrics_scope = "project"  # project, organization, folder
        self.retention_days = 30  # Metric retention period
        self.monitoring_enabled = True
        
        # Alert policies
        self.alert_policies = []
        self.notification_channels = []
        self.alert_conditions = []
        
        # Uptime checks
        self.uptime_checks = []
        self.synthetic_monitors = []
        
        # Dashboards and charts
        self.dashboards = []
        self.custom_charts = []
        self.dashboard_layouts = []
        
        # Metrics and filters
        self.custom_metrics = []
        self.metric_filters = []
        self.log_based_metrics = []
        
        # Service Level Objectives (SLOs)
        self.slos = []
        self.sli_configs = []
        self.error_budgets = []
        
        # Monitoring targets
        self.monitored_resources = []
        self.resource_groups = []
        
        # Notification configuration
        self.email_notifications = []
        self.slack_notifications = []
        self.webhook_notifications = []
        self.sms_notifications = []
        
        # Logging integration
        self.log_sinks = []
        self.log_metrics = []
        self.audit_logs_enabled = True
        
        # Labels and organization
        self.monitoring_labels = {}
        
        # State tracking
        self.monitoring_exists = False
        self.monitoring_created = False
        self.workspace_created = False
        
    def _initialize_managers(self):
        """Initialize monitoring-specific managers"""
        # Will be set up after authentication
        self.monitoring_manager = None
        self.alerting_manager = None
        self.dashboard_manager = None
        self.uptime_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.monitoring.monitoring_manager import MonitoringManager
        from ...googlecloud_managers.monitoring.alerting_manager import AlertingManager
        from ...googlecloud_managers.monitoring.dashboard_manager import DashboardManager
        from ...googlecloud_managers.monitoring.uptime_manager import UptimeManager
        
        self.monitoring_manager = MonitoringManager(self.gcp_client)
        self.alerting_manager = AlertingManager(self.gcp_client)
        self.dashboard_manager = DashboardManager(self.gcp_client)
        self.uptime_manager = UptimeManager(self.gcp_client)
        
        # Set up project context
        self.project_id = self.project_id or self.gcp_client.project_id
        self.workspace_id = f"projects/{self.project_id}"
        
    def _is_valid_metric_type(self, metric_type: str) -> bool:
        """Check if metric type is valid"""
        # GCP metric types follow format: compute.googleapis.com/instance/cpu/utilization
        parts = metric_type.split("/")
        return len(parts) >= 2 and "." in parts[0]
        
    def _is_valid_notification_channel_type(self, channel_type: str) -> bool:
        """Check if notification channel type is valid"""
        valid_types = [
            "email", "sms", "slack", "webhook", "pagerduty", 
            "campfire", "pubsub", "mobile_push"
        ]
        return channel_type.lower() in valid_types
        
    def _is_valid_alert_condition_type(self, condition_type: str) -> bool:
        """Check if alert condition type is valid"""
        valid_types = [
            "CONDITION_THRESHOLD", "CONDITION_ABSENT", 
            "CONDITION_MATCHED_LOG", "CONDITION_MONITORING_QUERY_LANGUAGE"
        ]
        return condition_type in valid_types
        
    def _is_valid_comparison_type(self, comparison: str) -> bool:
        """Check if comparison operator is valid"""
        valid_comparisons = [
            "COMPARISON_GT", "COMPARISON_GE", "COMPARISON_LT", 
            "COMPARISON_LE", "COMPARISON_EQ", "COMPARISON_NE"
        ]
        return comparison in valid_comparisons
        
    def _is_valid_aggregation_type(self, aggregation: str) -> bool:
        """Check if aggregation type is valid"""
        valid_aggregations = [
            "ALIGN_NONE", "ALIGN_DELTA", "ALIGN_RATE", "ALIGN_INTERPOLATE",
            "ALIGN_NEXT_OLDER", "ALIGN_MIN", "ALIGN_MAX", "ALIGN_MEAN",
            "ALIGN_COUNT", "ALIGN_SUM", "ALIGN_STDDEV", "ALIGN_COUNT_TRUE",
            "ALIGN_COUNT_FALSE", "ALIGN_FRACTION_TRUE", "ALIGN_PERCENTILE_99",
            "ALIGN_PERCENTILE_95", "ALIGN_PERCENTILE_50", "ALIGN_PERCENTILE_05"
        ]
        return aggregation in valid_aggregations
        
    def _validate_alert_policy_config(self, policy_config: Dict[str, Any]) -> bool:
        """Validate alert policy configuration"""
        required_fields = ["display_name", "conditions"]
        
        for field in required_fields:
            if field not in policy_config:
                return False
                
        # Validate conditions
        conditions = policy_config.get("conditions", [])
        if not isinstance(conditions, list) or not conditions:
            return False
            
        for condition in conditions:
            if not self._validate_alert_condition(condition):
                return False
                
        return True
        
    def _validate_alert_condition(self, condition: Dict[str, Any]) -> bool:
        """Validate alert condition configuration"""
        required_fields = ["display_name", "condition_type"]
        
        for field in required_fields:
            if field not in condition:
                return False
                
        # Validate condition type
        if not self._is_valid_alert_condition_type(condition["condition_type"]):
            return False
            
        return True
        
    def _validate_notification_channel_config(self, channel_config: Dict[str, Any]) -> bool:
        """Validate notification channel configuration"""
        required_fields = ["type", "display_name"]
        
        for field in required_fields:
            if field not in channel_config:
                return False
                
        # Validate channel type
        if not self._is_valid_notification_channel_type(channel_config["type"]):
            return False
            
        return True
        
    def _validate_uptime_check_config(self, check_config: Dict[str, Any]) -> bool:
        """Validate uptime check configuration"""
        required_fields = ["display_name", "monitored_resource"]
        
        for field in required_fields:
            if field not in check_config:
                return False
                
        # Validate monitored resource
        resource = check_config.get("monitored_resource", {})
        if not isinstance(resource, dict) or "type" not in resource:
            return False
            
        return True
        
    def _validate_dashboard_config(self, dashboard_config: Dict[str, Any]) -> bool:
        """Validate dashboard configuration"""
        required_fields = ["display_name"]
        
        for field in required_fields:
            if field not in dashboard_config:
                return False
                
        return True
        
    def _get_common_metrics(self) -> List[str]:
        """Get list of common GCP metrics"""
        return [
            # Compute Engine metrics
            "compute.googleapis.com/instance/cpu/utilization",
            "compute.googleapis.com/instance/disk/read_bytes_count",
            "compute.googleapis.com/instance/disk/write_bytes_count",
            "compute.googleapis.com/instance/network/received_bytes_count",
            "compute.googleapis.com/instance/network/sent_bytes_count",
            "compute.googleapis.com/instance/up",
            
            # Cloud SQL metrics
            "cloudsql.googleapis.com/database/cpu/utilization",
            "cloudsql.googleapis.com/database/memory/utilization",
            "cloudsql.googleapis.com/database/disk/utilization",
            "cloudsql.googleapis.com/database/network/connections",
            
            # Cloud Storage metrics
            "storage.googleapis.com/api/request_count",
            "storage.googleapis.com/network/sent_bytes_count",
            "storage.googleapis.com/network/received_bytes_count",
            "storage.googleapis.com/storage/total_bytes",
            
            # Load Balancer metrics
            "loadbalancing.googleapis.com/https/request_count",
            "loadbalancing.googleapis.com/https/total_latencies",
            "loadbalancing.googleapis.com/https/backend_latencies",
            "loadbalancing.googleapis.com/https/frontend_tcp_rtt",
            
            # Cloud Functions metrics
            "cloudfunctions.googleapis.com/function/execution_count",
            "cloudfunctions.googleapis.com/function/execution_times",
            "cloudfunctions.googleapis.com/function/memory_usage",
            "cloudfunctions.googleapis.com/function/network_egress",
            
            # VPC metrics
            "compute.googleapis.com/firewall/dropped_packets_count",
            "networking.googleapis.com/vm_flow/rtt",
            "networking.googleapis.com/vpc_flow/egress_bytes_count",
            "networking.googleapis.com/vpc_flow/ingress_bytes_count"
        ]
        
    def _get_metric_description(self, metric_type: str) -> str:
        """Get description for a metric type"""
        descriptions = {
            "compute.googleapis.com/instance/cpu/utilization": "CPU utilization (0-1)",
            "compute.googleapis.com/instance/disk/read_bytes_count": "Disk read bytes",
            "compute.googleapis.com/instance/disk/write_bytes_count": "Disk write bytes",
            "compute.googleapis.com/instance/network/received_bytes_count": "Network received bytes",
            "compute.googleapis.com/instance/network/sent_bytes_count": "Network sent bytes",
            "cloudsql.googleapis.com/database/cpu/utilization": "Database CPU utilization",
            "cloudsql.googleapis.com/database/memory/utilization": "Database memory utilization",
            "storage.googleapis.com/api/request_count": "Storage API requests",
            "loadbalancing.googleapis.com/https/request_count": "Load balancer requests",
            "cloudfunctions.googleapis.com/function/execution_count": "Function executions"
        }
        return descriptions.get(metric_type, metric_type)
        
    def _estimate_monitoring_cost(self) -> float:
        """Estimate monthly cost for monitoring"""
        # Google Cloud Monitoring pricing (simplified)
        base_cost = 0.0  # First 150 MB of logs per month are free
        
        # Alert policies cost
        alert_policies_cost = max(0, len(self.alert_policies) - 5) * 0.0  # First 5 free
        
        # Uptime checks cost
        uptime_checks_cost = max(0, len(self.uptime_checks) - 3) * 1.0  # First 3 free, $1 each after
        
        # Custom metrics cost (estimated)
        custom_metrics_cost = len(self.custom_metrics) * 0.30  # $0.30 per custom metric per month
        
        # API calls cost (estimated)
        api_calls_cost = 5.0  # $5 estimated for API calls
        
        # Log-based metrics cost
        log_metrics_cost = len(self.log_based_metrics) * 0.50  # $0.50 per log metric
        
        return (base_cost + alert_policies_cost + uptime_checks_cost + 
                custom_metrics_cost + api_calls_cost + log_metrics_cost)
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of monitoring from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get monitoring workspace info
            if self.monitoring_manager:
                monitoring_info = self.monitoring_manager.get_workspace_info(self.workspace_id)
                
                if monitoring_info.get("exists", False):
                    # Get alert policies
                    alert_policies = []
                    if self.alerting_manager:
                        alert_policies = self.alerting_manager.list_alert_policies(self.workspace_id)
                    
                    # Get notification channels
                    notification_channels = []
                    if self.alerting_manager:
                        notification_channels = self.alerting_manager.list_notification_channels(self.workspace_id)
                    
                    # Get uptime checks
                    uptime_checks = []
                    if self.uptime_manager:
                        uptime_checks = self.uptime_manager.list_uptime_checks(self.workspace_id)
                    
                    # Get dashboards
                    dashboards = []
                    if self.dashboard_manager:
                        dashboards = self.dashboard_manager.list_dashboards(self.workspace_id)
                    
                    return {
                        "exists": True,
                        "workspace_id": self.workspace_id,
                        "monitoring_name": self.monitoring_name,
                        "project_id": self.project_id,
                        "alert_policies": alert_policies,
                        "alert_policies_count": len(alert_policies),
                        "notification_channels": notification_channels,
                        "notification_channels_count": len(notification_channels),
                        "uptime_checks": uptime_checks,
                        "uptime_checks_count": len(uptime_checks),
                        "dashboards": dashboards,
                        "dashboards_count": len(dashboards),
                        "metrics_scope": monitoring_info.get("metrics_scope", "project"),
                        "creation_time": monitoring_info.get("creation_time"),
                        "labels": monitoring_info.get("labels", {}),
                        "status": monitoring_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "workspace_id": self.workspace_id
                    }
            else:
                return {
                    "exists": False,
                    "workspace_id": self.workspace_id,
                    "error": "Monitoring manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch monitoring state: {str(e)}")
            return {
                "exists": False,
                "workspace_id": self.workspace_id,
                "error": str(e)
            }