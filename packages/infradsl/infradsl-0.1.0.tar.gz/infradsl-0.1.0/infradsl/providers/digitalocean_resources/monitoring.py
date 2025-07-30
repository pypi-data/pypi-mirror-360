"""
DigitalOcean Monitoring Resource

Provides Rails-like interface for creating and managing DigitalOcean monitoring,
alerts, and uptime checks.
"""

from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseDigitalOceanResource


class Monitoring(BaseDigitalOceanResource):
    """DigitalOcean Monitoring with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        self.config = {
            "name": name,
            "type": "uptime",  # uptime, alert_policy
            "target": None,
            "regions": ["us_east"],  # Default regions for uptime checks
            "enabled": True,
            "tags": [],
            # Uptime check specific
            "check_regions": ["us_east", "us_west", "eu_west"],
            "target_url": None,
            "target_resource_id": None,
            "target_resource_type": None,
            # Alert policy specific
            "policy_type": "v1/insights/droplet/cpu",
            "comparison": "GreaterThan",
            "threshold": 80,
            "window": "5m",
            "entities": [],
            "alerts": {
                "email": [],
                "slack": []
            }
        }

    def _initialize_managers(self):
        """Initialize monitoring-specific managers"""
        from ..digitalocean_managers.monitoring_manager import MonitoringManager
        self.monitoring_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        from ..digitalocean_managers.monitoring_manager import MonitoringManager
        self.monitoring_manager = MonitoringManager(self.do_client)

    # Type configuration
    def uptime_check(self, url: str) -> 'Monitoring':
        """Configure as uptime check for URL"""
        self.config["type"] = "uptime"
        self.config["target_url"] = url
        self.config["target"] = url
        return self

    def resource_check(self, resource_id: str, resource_type: str = "droplet") -> 'Monitoring':
        """Configure as uptime check for resource (droplet, load_balancer)"""
        self.config["type"] = "uptime"
        self.config["target_resource_id"] = resource_id
        self.config["target_resource_type"] = resource_type
        self.config["target"] = f"{resource_type}:{resource_id}"
        return self

    def alert_policy(self, policy_type: str = "v1/insights/droplet/cpu") -> 'Monitoring':
        """Configure as alert policy"""
        self.config["type"] = "alert_policy"
        self.config["policy_type"] = policy_type
        return self

    # Regions and targeting
    def regions(self, regions: List[str]) -> 'Monitoring':
        """Set check regions (us_east, us_west, eu_west, eu_central, se_asia)"""
        self.config["check_regions"] = regions
        return self

    def global_check(self) -> 'Monitoring':
        """Enable checking from all available regions"""
        return self.regions(["us_east", "us_west", "eu_west", "eu_central", "se_asia"])

    def us_only(self) -> 'Monitoring':
        """Check from US regions only"""
        return self.regions(["us_east", "us_west"])

    def eu_only(self) -> 'Monitoring':
        """Check from EU regions only"""
        return self.regions(["eu_west", "eu_central"])

    # Alert policy configuration
    def cpu_alert(self, threshold: float = 80, window: str = "5m") -> 'Monitoring':
        """Configure CPU utilization alert"""
        return self.alert_policy("v1/insights/droplet/cpu").threshold(threshold, "GreaterThan").window(window)

    def memory_alert(self, threshold: float = 80, window: str = "5m") -> 'Monitoring':
        """Configure memory utilization alert"""
        return self.alert_policy("v1/insights/droplet/memory_utilization_percent").threshold(threshold, "GreaterThan").window(window)

    def disk_alert(self, threshold: float = 85, window: str = "5m") -> 'Monitoring':
        """Configure disk utilization alert"""
        return self.alert_policy("v1/insights/droplet/disk_utilization_percent").threshold(threshold, "GreaterThan").window(window)

    def load_alert(self, threshold: float = 1.0, window: str = "5m") -> 'Monitoring':
        """Configure load average alert"""
        return self.alert_policy("v1/insights/droplet/load_1").threshold(threshold, "GreaterThan").window(window)

    def bandwidth_alert(self, threshold: float = 1000000000, window: str = "5m") -> 'Monitoring':
        """Configure bandwidth alert (bytes per second)"""
        return self.alert_policy("v1/insights/droplet/public_outbound_bandwidth").threshold(threshold, "GreaterThan").window(window)

    def threshold(self, value: float, comparison: str = "GreaterThan") -> 'Monitoring':
        """Set alert threshold and comparison"""
        self.config["threshold"] = value
        self.config["comparison"] = comparison  # GreaterThan, LessThan
        return self

    def window(self, window: str) -> 'Monitoring':
        """Set alert window (5m, 10m, 30m, 1h)"""
        self.config["window"] = window
        return self

    def entities(self, entity_ids: List[str]) -> 'Monitoring':
        """Set entities (droplet IDs) to monitor"""
        self.config["entities"] = entity_ids
        return self

    def all_droplets(self) -> 'Monitoring':
        """Monitor all droplets with specific tags"""
        self.config["entities"] = ["*"]  # Special marker for all droplets
        return self

    # Alert destinations
    def email_alert(self, emails: Union[str, List[str]]) -> 'Monitoring':
        """Add email alerts"""
        if isinstance(emails, str):
            emails = [emails]
        self.config["alerts"]["email"].extend(emails)
        return self

    def slack_alert(self, webhook_url: str, channel: str = None) -> 'Monitoring':
        """Add Slack webhook alert"""
        slack_config = {"url": webhook_url}
        if channel:
            slack_config["channel"] = channel
        self.config["alerts"]["slack"].append(slack_config)
        return self

    def tags(self, tags: List[str]) -> 'Monitoring':
        """Add tags"""
        self.config["tags"] = tags
        return self

    def enabled(self, enabled: bool = True) -> 'Monitoring':
        """Enable or disable monitoring"""
        self.config["enabled"] = enabled
        return self

    # Rails-like convenience methods
    def website_monitoring(self, url: str, emails: List[str] = None) -> 'Monitoring':
        """Configure basic website monitoring"""
        monitor = self.uptime_check(url).global_check()
        if emails:
            monitor = monitor.email_alert(emails)
        return monitor

    def server_monitoring(self, droplet_id: str, emails: List[str] = None) -> 'Monitoring':
        """Configure basic server monitoring"""
        monitor = self.resource_check(droplet_id, "droplet").global_check()
        if emails:
            monitor = monitor.email_alert(emails)
        return monitor

    def performance_alerts(self, droplet_ids: List[str], emails: List[str] = None) -> 'Monitoring':
        """Configure comprehensive performance alerts"""
        monitor = self.cpu_alert(80).entities(droplet_ids)
        if emails:
            monitor = monitor.email_alert(emails)
        return monitor

    def development(self) -> 'Monitoring':
        """Configure for development environment (relaxed thresholds)"""
        if self.config["type"] == "alert_policy":
            return self.threshold(90).window("10m")
        return self.regions(["us_east"])

    def production(self) -> 'Monitoring':
        """Configure for production environment (strict thresholds)"""
        if self.config["type"] == "alert_policy":
            return self.threshold(75).window("5m")
        return self.global_check()

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        self._ensure_authenticated()
        return self.monitoring_manager.preview_monitoring(self.config)

    def create(self) -> Dict[str, Any]:
        """Create the monitoring check or alert policy"""
        self._ensure_authenticated()
        
        resource_type = "Uptime Check" if self.config["type"] == "uptime" else "Alert Policy"
        self._print_resource_header(resource_type, "Creating")
        
        # Print configuration summary
        print(f"📊 Monitor Name: {self.config['name']}")
        print(f"🔍 Type: {resource_type}")
        
        if self.config["type"] == "uptime":
            if self.config.get("target_url"):
                print(f"🌐 Target URL: {self.config['target_url']}")
            elif self.config.get("target_resource_id"):
                print(f"🖥️  Target Resource: {self.config['target_resource_type']}:{self.config['target_resource_id']}")
            print(f"🌍 Check Regions: {', '.join(self.config['check_regions'])}")
        else:
            print(f"📈 Policy Type: {self.config['policy_type']}")
            print(f"⚠️  Threshold: {self.config['comparison']} {self.config['threshold']}")
            print(f"⏱️  Window: {self.config['window']}")
            if self.config["entities"]:
                if "*" in self.config["entities"]:
                    print(f"🎯 Entities: All droplets")
                else:
                    print(f"🎯 Entities: {len(self.config['entities'])} resources")
        
        # Alert destinations
        alert_count = len(self.config["alerts"]["email"]) + len(self.config["alerts"]["slack"])
        if alert_count > 0:
            print(f"📧 Alert Destinations: {alert_count} configured")
        
        result = self.monitoring_manager.create_monitoring(self.config)
        
        self._print_resource_footer(f"create {resource_type.lower()}")
        return result

    def destroy(self) -> Dict[str, Any]:
        """Destroy the monitoring check or alert policy"""
        self._ensure_authenticated()
        
        print(f"\n🗑️  Destroying monitoring: {self.name}")
        result = self.monitoring_manager.destroy_monitoring(self.name, self.config["type"])
        
        if result.get("success"):
            print(f"✅ Monitoring '{self.name}' destroyed successfully")
        else:
            print(f"❌ Failed to destroy monitoring: {result.get('error', 'Unknown error')}")
        
        return result