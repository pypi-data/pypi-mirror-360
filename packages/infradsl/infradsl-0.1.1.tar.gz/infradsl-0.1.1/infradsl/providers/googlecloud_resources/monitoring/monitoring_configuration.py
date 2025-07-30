"""
GCP Cloud Monitoring Configuration Mixin

Chainable configuration methods for Google Cloud Monitoring.
Provides Rails-like method chaining for fluent monitoring configuration.
"""

from typing import Dict, Any, List, Optional


class MonitoringConfigurationMixin:
    """
    Mixin for Cloud Monitoring configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Alert policies and notification channels
    - Uptime checks and synthetic monitoring
    - Dashboards and custom metrics
    - Service Level Objectives (SLOs)
    - Monitoring targets and resource groups
    """
    
    def description(self, description: str):
        """Set description for the monitoring workspace"""
        self.monitoring_description = description
        return self
        
    def workspace(self, workspace_id: str):
        """Set workspace ID for monitoring operations"""
        self.workspace_id = workspace_id
        return self
        
    def project(self, project_id: str):
        """Set project ID for monitoring operations - Rails convenience"""
        self.project_id = project_id
        self.workspace_id = f"projects/{project_id}"
        return self
        
    def metrics_scope(self, scope: str):
        """Set metrics scope - Rails convenience"""
        valid_scopes = ["project", "organization", "folder"]
        if scope not in valid_scopes:
            print(f"⚠️  Warning: Invalid metrics scope '{scope}'. Valid: {valid_scopes}")
        self.metrics_scope = scope
        return self
        
    def retention_period(self, days: int):
        """Set metric retention period in days"""
        if days < 1 or days > 2557:  # GCP max retention
            print(f"⚠️  Warning: Invalid retention period {days} days. Valid range: 1-2557")
        self.retention_days = days
        return self
        
    # Alert policy configuration
    def alert_policy(self, name: str, conditions: List[Dict], notification_channels: List[str] = None):
        """Add an alert policy"""
        policy = {
            "display_name": name,
            "conditions": conditions,
            "notification_channels": notification_channels or [],
            "enabled": True,
            "combiner": "OR"
        }
        
        if self._validate_alert_policy_config(policy):
            self.alert_policies.append(policy)
        else:
            print(f"⚠️  Warning: Invalid alert policy configuration for '{name}'")
            
        return self
        
    def threshold_alert(self, name: str, metric_type: str, threshold: float, 
                       comparison: str = "COMPARISON_GT", duration: str = "300s"):
        """Create threshold-based alert - Rails convenience"""
        condition = {
            "display_name": f"{name} Condition",
            "condition_type": "CONDITION_THRESHOLD",
            "condition_threshold": {
                "filter": f'metric.type="{metric_type}"',
                "comparison": comparison,
                "threshold_value": threshold,
                "duration": duration,
                "aggregations": [{
                    "alignment_period": "60s",
                    "per_series_aligner": "ALIGN_RATE"
                }]
            }
        }
        
        return self.alert_policy(name, [condition])
        
    def cpu_alert(self, name: str, threshold: float = 0.8):
        """Create CPU utilization alert - Rails convenience"""
        return self.threshold_alert(
            name,
            "compute.googleapis.com/instance/cpu/utilization",
            threshold,
            "COMPARISON_GT"
        )
        
    def memory_alert(self, name: str, threshold: float = 0.85):
        """Create memory utilization alert - Rails convenience"""
        return self.threshold_alert(
            name,
            "compute.googleapis.com/instance/memory/utilization",
            threshold,
            "COMPARISON_GT"
        )
        
    def disk_alert(self, name: str, threshold: float = 0.9):
        """Create disk utilization alert - Rails convenience"""
        return self.threshold_alert(
            name,
            "compute.googleapis.com/instance/disk/utilization",
            threshold,
            "COMPARISON_GT"
        )
        
    def error_rate_alert(self, name: str, threshold: float = 0.05):
        """Create error rate alert - Rails convenience"""
        return self.threshold_alert(
            name,
            "loadbalancing.googleapis.com/https/request_count",
            threshold,
            "COMPARISON_GT"
        )
        
    # Notification channel configuration
    def notification_channel(self, channel_type: str, config: Dict[str, Any]):
        """Add a notification channel"""
        channel = {
            "type": channel_type,
            "display_name": config.get("display_name", f"{channel_type} Channel"),
            "description": config.get("description", f"Notification channel for {channel_type}"),
            "labels": config.get("labels", {}),
            "enabled": config.get("enabled", True)
        }
        
        if self._validate_notification_channel_config(channel):
            self.notification_channels.append(channel)
        else:
            print(f"⚠️  Warning: Invalid notification channel configuration for '{channel_type}'")
            
        return self
        
    def email_notification(self, email: str, display_name: str = None):
        """Add email notification channel - Rails convenience"""
        return self.notification_channel("email", {
            "display_name": display_name or f"Email: {email}",
            "labels": {"email_address": email}
        })
        
    def slack_notification(self, webhook_url: str, channel: str = None):
        """Add Slack notification channel - Rails convenience"""
        labels = {"url": webhook_url}
        if channel:
            labels["channel"] = channel
            
        return self.notification_channel("slack", {
            "display_name": f"Slack: {channel or 'Default'}",
            "labels": labels
        })
        
    def webhook_notification(self, url: str, display_name: str = None):
        """Add webhook notification channel - Rails convenience"""
        return self.notification_channel("webhook", {
            "display_name": display_name or f"Webhook: {url}",
            "labels": {"url": url}
        })
        
    def sms_notification(self, phone_number: str):
        """Add SMS notification channel - Rails convenience"""
        return self.notification_channel("sms", {
            "display_name": f"SMS: {phone_number}",
            "labels": {"number": phone_number}
        })
        
    # Uptime check configuration
    def uptime_check(self, name: str, target: str, check_type: str = "HTTP", **kwargs):
        """Add an uptime check"""
        check = {
            "display_name": name,
            "monitored_resource": {
                "type": "uptime_url",
                "labels": {"host": target}
            },
            "http_check": {
                "request_method": kwargs.get("method", "GET"),
                "use_ssl": kwargs.get("use_ssl", True),
                "path": kwargs.get("path", "/"),
                "port": kwargs.get("port", 443 if kwargs.get("use_ssl", True) else 80)
            },
            "timeout": kwargs.get("timeout", "10s"),
            "period": kwargs.get("period", "300s"),
            "selected_regions": kwargs.get("regions", ["USA", "EUROPE", "ASIA_PACIFIC"])
        }
        
        if self._validate_uptime_check_config(check):
            self.uptime_checks.append(check)
        else:
            print(f"⚠️  Warning: Invalid uptime check configuration for '{name}'")
            
        return self
        
    def http_check(self, name: str, url: str, path: str = "/", method: str = "GET"):
        """Add HTTP uptime check - Rails convenience"""
        return self.uptime_check(name, url, "HTTP", path=path, method=method, use_ssl=True)
        
    def https_check(self, name: str, url: str, path: str = "/"):
        """Add HTTPS uptime check - Rails convenience"""
        return self.uptime_check(name, url, "HTTPS", path=path, use_ssl=True)
        
    def tcp_check(self, name: str, host: str, port: int):
        """Add TCP uptime check - Rails convenience"""
        return self.uptime_check(name, host, "TCP", port=port, use_ssl=False)
        
    # Dashboard configuration
    def dashboard(self, name: str, **kwargs):
        """Add a dashboard"""
        dashboard = {
            "display_name": name,
            "description": kwargs.get("description", f"Dashboard for {name}"),
            "grid_layout": kwargs.get("grid_layout", {}),
            "mosaic_layout": kwargs.get("mosaic_layout", {}),
            "labels": kwargs.get("labels", {})
        }
        
        if self._validate_dashboard_config(dashboard):
            self.dashboards.append(dashboard)
        else:
            print(f"⚠️  Warning: Invalid dashboard configuration for '{name}'")
            
        return self
        
    def system_dashboard(self, name: str = "System Overview"):
        """Create system monitoring dashboard - Rails convenience"""
        return self.dashboard(name, description="System resource monitoring dashboard")
        
    def application_dashboard(self, app_name: str):
        """Create application monitoring dashboard - Rails convenience"""
        return self.dashboard(
            f"{app_name} Application Dashboard",
            description=f"Monitoring dashboard for {app_name} application"
        )
        
    def performance_dashboard(self, name: str = "Performance Metrics"):
        """Create performance monitoring dashboard - Rails convenience"""
        return self.dashboard(name, description="Performance and latency monitoring")
        
    # Custom metrics configuration
    def custom_metric(self, metric_type: str, **kwargs):
        """Add a custom metric"""
        metric = {
            "metric_type": metric_type,
            "display_name": kwargs.get("display_name", metric_type),
            "description": kwargs.get("description", f"Custom metric {metric_type}"),
            "metric_kind": kwargs.get("metric_kind", "GAUGE"),
            "value_type": kwargs.get("value_type", "DOUBLE"),
            "unit": kwargs.get("unit", "1"),
            "labels": kwargs.get("labels", [])
        }
        
        if self._is_valid_metric_type(metric_type):
            self.custom_metrics.append(metric)
        else:
            print(f"⚠️  Warning: Invalid custom metric type '{metric_type}'")
            
        return self
        
    def gauge_metric(self, name: str, description: str = None):
        """Add gauge metric - Rails convenience"""
        return self.custom_metric(
            f"custom.googleapis.com/{name}",
            display_name=name,
            description=description,
            metric_kind="GAUGE"
        )
        
    def counter_metric(self, name: str, description: str = None):
        """Add counter metric - Rails convenience"""
        return self.custom_metric(
            f"custom.googleapis.com/{name}",
            display_name=name,
            description=description,
            metric_kind="CUMULATIVE"
        )
        
    # Service Level Objectives (SLOs)
    def slo(self, name: str, service_name: str, sli_config: Dict[str, Any], target: float):
        """Add Service Level Objective"""
        slo = {
            "display_name": name,
            "service_name": service_name,
            "sli": sli_config,
            "goal": {
                "performance_goal": {
                    "performance_threshold": target,
                    "basic_sli_performance": sli_config
                }
            },
            "rolling_period": "2592000s"  # 30 days
        }
        
        self.slos.append(slo)
        return self
        
    def availability_slo(self, service_name: str, target: float = 0.999):
        """Add availability SLO - Rails convenience"""
        sli_config = {
            "availability": {
                "enabled": True
            }
        }
        
        return self.slo(
            f"{service_name} Availability SLO",
            service_name,
            sli_config,
            target
        )
        
    def latency_slo(self, service_name: str, threshold_ms: int = 500, target: float = 0.95):
        """Add latency SLO - Rails convenience"""
        sli_config = {
            "request_based": {
                "good_total_ratio": {
                    "good_service_filter": f'metric.type="loadbalancing.googleapis.com/https/total_latencies" AND metric.label.response_code_class="2xx"',
                    "total_service_filter": f'metric.type="loadbalancing.googleapis.com/https/total_latencies"'
                }
            }
        }
        
        return self.slo(
            f"{service_name} Latency SLO",
            service_name,
            sli_config,
            target
        )
        
    # Monitoring targets
    def monitor_resource(self, resource_type: str, resource_labels: Dict[str, str]):
        """Add monitored resource"""
        resource = {
            "type": resource_type,
            "labels": resource_labels
        }
        
        self.monitored_resources.append(resource)
        return self
        
    def monitor_gce_instance(self, instance_id: str, zone: str):
        """Monitor GCE instance - Rails convenience"""
        return self.monitor_resource("gce_instance", {
            "instance_id": instance_id,
            "zone": zone,
            "project_id": self.project_id
        })
        
    def monitor_cloud_function(self, function_name: str, region: str):
        """Monitor Cloud Function - Rails convenience"""
        return self.monitor_resource("cloud_function", {
            "function_name": function_name,
            "region": region,
            "project_id": self.project_id
        })
        
    def monitor_cloud_sql(self, database_id: str, region: str):
        """Monitor Cloud SQL - Rails convenience"""
        return self.monitor_resource("cloudsql_database", {
            "database_id": database_id,
            "region": region,
            "project_id": self.project_id
        })
        
    def monitor_load_balancer(self, lb_name: str, region: str):
        """Monitor Load Balancer - Rails convenience"""
        return self.monitor_resource("http_load_balancer", {
            "backend_target_name": lb_name,
            "region": region,
            "project_id": self.project_id
        })
        
    # Labels and organization
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.monitoring_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.monitoring_labels[key] = value
        return self
        
    # Rails-like environment configurations
    def development_monitoring(self):
        """Configure for development environment - Rails convention"""
        return (self.retention_period(7)
                .metrics_scope("project")
                .label("environment", "development")
                .label("monitoring", "basic"))
                
    def staging_monitoring(self):
        """Configure for staging environment - Rails convention"""
        return (self.retention_period(30)
                .metrics_scope("project")
                .label("environment", "staging")
                .label("monitoring", "standard"))
                
    def production_monitoring(self):
        """Configure for production environment - Rails convention"""
        return (self.retention_period(90)
                .metrics_scope("project")
                .label("environment", "production")
                .label("monitoring", "comprehensive"))
                
    # Common monitoring patterns
    def web_app_monitoring(self, app_name: str, domain: str = None):
        """Set up common monitoring for web applications - Rails convenience"""
        # Basic system alerts
        self.cpu_alert(f"{app_name} High CPU", 0.8)
        self.memory_alert(f"{app_name} High Memory", 0.85)
        self.disk_alert(f"{app_name} High Disk", 0.9)
        
        # Application dashboard
        self.application_dashboard(app_name)
        
        # Uptime monitoring
        if domain:
            self.https_check(f"{app_name} Uptime", domain)
            
        return self
        
    def microservices_monitoring(self, service_name: str, function_name: str = None):
        """Set up monitoring for microservices - Rails convenience"""
        # Function monitoring
        if function_name:
            self.monitor_cloud_function(function_name, "us-central1")
            
        # Error rate monitoring
        self.error_rate_alert(f"{service_name} Error Rate", 0.05)
        
        # Performance dashboard
        self.performance_dashboard(f"{service_name} Performance")
        
        # SLOs
        self.availability_slo(service_name, 0.999)
        self.latency_slo(service_name, 500, 0.95)
        
        return self
        
    def database_monitoring(self, db_name: str, region: str = "us-central1"):
        """Set up database monitoring - Rails convenience"""
        # Monitor database
        self.monitor_cloud_sql(db_name, region)
        
        # Database-specific alerts
        self.threshold_alert(
            f"{db_name} High Connections",
            "cloudsql.googleapis.com/database/network/connections",
            80,
            "COMPARISON_GT"
        )
        
        self.threshold_alert(
            f"{db_name} High CPU",
            "cloudsql.googleapis.com/database/cpu/utilization",
            0.8,
            "COMPARISON_GT"
        )
        
        # Database dashboard
        self.dashboard(f"{db_name} Database Dashboard")
        
        return self
        
    def infrastructure_monitoring(self):
        """Set up comprehensive infrastructure monitoring - Rails convenience"""
        # System dashboards
        self.system_dashboard("Infrastructure Overview")
        self.performance_dashboard("Infrastructure Performance")
        
        # Common infrastructure alerts
        self.cpu_alert("Infrastructure High CPU", 0.85)
        self.memory_alert("Infrastructure High Memory", 0.9)
        self.disk_alert("Infrastructure High Disk", 0.95)
        
        # Network monitoring
        self.threshold_alert(
            "High Network Egress",
            "compute.googleapis.com/instance/network/sent_bytes_count",
            1000000000,  # 1GB
            "COMPARISON_GT"
        )
        
        return self