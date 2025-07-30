"""
InfraDSL Daemon Configuration Management

Handles loading and validation of daemon configuration from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from ..core.drift_management import DriftCheckInterval, AutoRemediationPolicy


@dataclass
class AlertConfig:
    """Configuration for alert destinations"""
    name: str
    type: str  # discord, slack, email, pagerduty
    webhook: Optional[str] = None
    api_key: Optional[str] = None
    events: List[str] = field(default_factory=lambda: ["drift_detected", "auto_healed"])
    enabled: bool = True


@dataclass
class MonitoringPolicy:
    """Monitoring policy for resources"""
    name: str
    check_interval: str = "15m"  # 15 minutes default
    auto_remediation: str = "conservative"
    learning_mode: bool = False
    alerts: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, critical


@dataclass
class ResourceConfig:
    """Per-resource monitoring configuration"""
    name: str
    policy: str = "default"
    auto_remediation: Optional[str] = None
    priority: Optional[str] = None
    enabled: bool = True


@dataclass
class DaemonConfig:
    """Complete daemon configuration"""
    # Daemon settings
    check_interval: str = "15m"
    log_level: str = "info"
    pid_file: str = "/tmp/infradsl-daemon.pid"
    cache_dir: str = ".infradsl_cache"
    
    # Monitoring settings
    auto_discovery: bool = True
    resource_paths: List[str] = field(default_factory=lambda: ["**/*.infra.py"])
    
    # Policies
    policies: Dict[str, MonitoringPolicy] = field(default_factory=dict)
    
    # Alerts
    alerts: Dict[str, AlertConfig] = field(default_factory=dict)
    
    # Per-resource overrides
    resources: Dict[str, ResourceConfig] = field(default_factory=dict)
    
    @classmethod
    def load(cls, config_path: str = ".infradsl_daemon.yml") -> 'DaemonConfig':
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"📋 No config file found at {config_path}, using defaults")
            return cls.create_default()
        
        try:
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            return cls.from_dict(data)
            
        except Exception as e:
            print(f"❌ Failed to load config from {config_path}: {e}")
            print("📋 Using default configuration")
            return cls.create_default()
    
    @classmethod
    def create_default(cls) -> 'DaemonConfig':
        """Create default configuration"""
        config = cls()
        
        # Add default policy
        config.policies["default"] = MonitoringPolicy(
            name="default",
            check_interval="15m",
            auto_remediation="conservative",
            learning_mode=False,
            alerts=["console"],
            priority="normal"
        )
        
        # Add console alert (always available)
        config.alerts["console"] = AlertConfig(
            name="console",
            type="console",
            events=["drift_detected", "auto_healed", "failed_remediation"]
        )
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DaemonConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Daemon settings
        daemon_config = data.get("daemon", {})
        config.check_interval = daemon_config.get("check_interval", config.check_interval)
        config.log_level = daemon_config.get("log_level", config.log_level)
        config.pid_file = daemon_config.get("pid_file", config.pid_file)
        
        # Monitoring settings
        monitoring_config = data.get("monitoring", {})
        config.auto_discovery = monitoring_config.get("auto_discovery", config.auto_discovery)
        config.resource_paths = monitoring_config.get("resource_paths", config.resource_paths)
        config.cache_dir = monitoring_config.get("cache_dir", config.cache_dir)
        
        # Policies
        policies_config = data.get("policies", {})
        for policy_name, policy_data in policies_config.items():
            config.policies[policy_name] = MonitoringPolicy(
                name=policy_name,
                check_interval=policy_data.get("check_interval", "15m"),
                auto_remediation=policy_data.get("auto_remediation", "conservative"),
                learning_mode=policy_data.get("learning_mode", False),
                alerts=policy_data.get("alerts", []),
                priority=policy_data.get("priority", "normal")
            )
        
        # Alerts
        alerts_config = data.get("alerts", {})
        for alert_name, alert_data in alerts_config.items():
            config.alerts[alert_name] = AlertConfig(
                name=alert_name,
                type=alert_data.get("type", "console"),
                webhook=alert_data.get("webhook"),
                api_key=alert_data.get("api_key"),
                events=alert_data.get("events", ["drift_detected", "auto_healed"]),
                enabled=alert_data.get("enabled", True)
            )
        
        # Resources
        resources_config = data.get("resources", {})
        for resource_name, resource_data in resources_config.items():
            config.resources[resource_name] = ResourceConfig(
                name=resource_name,
                policy=resource_data.get("policy", "default"),
                auto_remediation=resource_data.get("auto_remediation"),
                priority=resource_data.get("priority"),
                enabled=resource_data.get("enabled", True)
            )
        
        # Add default console alert if no alerts configured
        if not config.alerts:
            config.alerts["console"] = AlertConfig(
                name="console",
                type="console",
                events=["drift_detected", "auto_healed", "failed_remediation"]
            )
        
        # Add default policy if no policies configured
        if not config.policies:
            config.policies["default"] = MonitoringPolicy(
                name="default",
                check_interval="15m",
                auto_remediation="conservative",
                learning_mode=False,
                alerts=["console"],
                priority="normal"
            )
        
        return config
    
    def get_policy(self, policy_name: str) -> MonitoringPolicy:
        """Get monitoring policy by name"""
        return self.policies.get(policy_name, self.policies.get("default"))
    
    def get_resource_config(self, resource_name: str) -> ResourceConfig:
        """Get resource configuration"""
        return self.resources.get(resource_name, ResourceConfig(name=resource_name))
    
    def parse_interval(self, interval_str: str) -> int:
        """Parse interval string to seconds"""
        if interval_str.endswith('s'):
            return int(interval_str[:-1])
        elif interval_str.endswith('m'):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith('h'):
            return int(interval_str[:-1]) * 3600
        elif interval_str.endswith('d'):
            return int(interval_str[:-1]) * 86400
        else:
            # Default to minutes if no suffix
            return int(interval_str) * 60
    
    def to_drift_check_interval(self, interval_str: str) -> DriftCheckInterval:
        """Convert interval string to DriftCheckInterval enum"""
        seconds = self.parse_interval(interval_str)
        
        if seconds <= 30 * 60:  # 30 minutes
            return DriftCheckInterval.THIRTY_MINUTES
        elif seconds <= 60 * 60:  # 1 hour
            return DriftCheckInterval.ONE_HOUR
        elif seconds <= 2 * 60 * 60:  # 2 hours
            return DriftCheckInterval.TWO_HOURS
        elif seconds <= 3 * 60 * 60:  # 3 hours
            return DriftCheckInterval.THREE_HOURS
        elif seconds <= 6 * 60 * 60:  # 6 hours
            return DriftCheckInterval.SIX_HOURS
        elif seconds <= 12 * 60 * 60:  # 12 hours
            return DriftCheckInterval.TWELVE_HOURS
        else:  # Daily or longer
            return DriftCheckInterval.DAILY
    
    def to_auto_remediation_policy(self, policy_str: str) -> AutoRemediationPolicy:
        """Convert policy string to AutoRemediationPolicy enum"""
        policy_map = {
            "conservative": AutoRemediationPolicy.CONSERVATIVE,
            "aggressive": AutoRemediationPolicy.AGGRESSIVE,
            "disabled": AutoRemediationPolicy.DISABLED
        }
        return policy_map.get(policy_str.lower(), AutoRemediationPolicy.CONSERVATIVE)
    
    def save(self, config_path: str = ".infradsl_daemon.yml"):
        """Save configuration to YAML file"""
        # Convert to dictionary
        data = {
            "daemon": {
                "check_interval": self.check_interval,
                "log_level": self.log_level,
                "pid_file": self.pid_file
            },
            "monitoring": {
                "auto_discovery": self.auto_discovery,
                "resource_paths": self.resource_paths,
                "cache_dir": self.cache_dir
            },
            "policies": {},
            "alerts": {},
            "resources": {}
        }
        
        # Add policies
        for policy_name, policy in self.policies.items():
            data["policies"][policy_name] = {
                "check_interval": policy.check_interval,
                "auto_remediation": policy.auto_remediation,
                "learning_mode": policy.learning_mode,
                "alerts": policy.alerts,
                "priority": policy.priority
            }
        
        # Add alerts
        for alert_name, alert in self.alerts.items():
            alert_data = {
                "type": alert.type,
                "events": alert.events,
                "enabled": alert.enabled
            }
            if alert.webhook:
                alert_data["webhook"] = alert.webhook
            if alert.api_key:
                alert_data["api_key"] = alert.api_key
            data["alerts"][alert_name] = alert_data
        
        # Add resources
        for resource_name, resource in self.resources.items():
            resource_data = {
                "policy": resource.policy,
                "enabled": resource.enabled
            }
            if resource.auto_remediation:
                resource_data["auto_remediation"] = resource.auto_remediation
            if resource.priority:
                resource_data["priority"] = resource.priority
            data["resources"][resource_name] = resource_data
        
        # Write to file
        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
        
        print(f"📁 Configuration saved to {config_path}")


def create_example_config() -> str:
    """Create an example configuration file"""
    example_config = """# InfraDSL Daemon Configuration
# Complete example with all available options

daemon:
  check_interval: 15m          # How often to check all resources
  log_level: info              # debug, info, warn, error
  pid_file: /tmp/infradsl-daemon.pid

monitoring:
  auto_discovery: true         # Auto-find .infra.py files
  cache_dir: .infradsl_cache   # Where cached resource states are stored
  resource_paths:
    - "./googlecloud/**/*.infra.py"
    - "./aws/production/*.infra.py"
    - "./digitalocean/**/*.infra.py"

policies:
  default:
    check_interval: 15m
    auto_remediation: conservative
    learning_mode: false
    alerts: [console]
    priority: normal
    
  production:
    check_interval: 5m         # More frequent for prod
    auto_remediation: aggressive
    learning_mode: false
    alerts: [discord, pagerduty]
    priority: critical
    
  development:
    check_interval: 1h         # Less frequent for dev
    auto_remediation: disabled
    learning_mode: true
    alerts: [discord]
    priority: low

alerts:
  console:
    type: console
    events: [drift_detected, auto_healed, failed_remediation]
    enabled: true
    
  discord:
    type: discord
    webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
    events: [drift_detected, auto_healed, failed_remediation]
    enabled: true
    
  slack:
    type: slack
    webhook: "https://hooks.slack.com/services/YOUR_WEBHOOK_HERE"
    events: [drift_detected, auto_healed]
    enabled: false
    
  pagerduty:
    type: pagerduty
    api_key: "YOUR_PAGERDUTY_API_KEY"
    events: [critical_drift, failed_remediation]
    enabled: false

resources:
  # Per-resource overrides
  "web-1":
    policy: production
    priority: critical
    enabled: true
    
  "test-vm":
    policy: development
    auto_remediation: disabled
    enabled: true
    
  "staging-db":
    policy: production
    auto_remediation: conservative
    enabled: true
"""
    return example_config