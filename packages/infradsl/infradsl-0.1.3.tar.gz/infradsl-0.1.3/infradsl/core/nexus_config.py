"""
Global Nexus Engine Configuration
Automatically enables intelligent optimizations across all resources
"""

from dataclasses import dataclass
from typing import List, Optional
import os
from pathlib import Path


@dataclass
class GlobalNexusConfig:
    """Global configuration for automatic Nexus Engine intelligence"""
    
    # Core Intelligence Features (enabled by default)
    auto_cost_optimization: bool = True
    auto_failure_prediction: bool = True
    auto_security_scanning: bool = True
    auto_performance_insights: bool = True
    auto_drift_management: bool = True
    auto_cross_cloud_optimization: bool = True
    auto_nexus_networking: bool = True
    
    # Output Control
    verbose_intelligence_output: bool = False  # Concise by default
    show_only_critical_issues: bool = True     # Focus on what matters
    
    # Default Compliance Standards
    default_compliance_standards: List[str] = None
    
    # Optimization Policies
    cost_optimization_aggressiveness: str = "MODERATE"  # CONSERVATIVE, MODERATE, AGGRESSIVE
    security_scan_frequency: str = "DAILY"  # HOURLY, DAILY, WEEKLY
    drift_check_interval: str = "6_HOURS"  # 1_HOUR, 6_HOURS, 24_HOURS
    auto_remediation_policy: str = "CONSERVATIVE"  # CONSERVATIVE, AGGRESSIVE, DISABLED
    
    def __post_init__(self):
        if self.default_compliance_standards is None:
            self.default_compliance_standards = ["CIS", "SOC2"]


# Global instance
_global_config = None


def get_global_nexus_config() -> GlobalNexusConfig:
    """Get the global Nexus configuration"""
    global _global_config
    if _global_config is None:
        _global_config = load_global_nexus_config()
    return _global_config


def load_global_nexus_config() -> GlobalNexusConfig:
    """Load Nexus configuration from environment variables and config files"""
    config = GlobalNexusConfig()
    
    # Load from environment variables
    config.auto_cost_optimization = _get_env_bool("INFRADSL_AUTO_COST_OPTIMIZATION", config.auto_cost_optimization)
    config.auto_failure_prediction = _get_env_bool("INFRADSL_AUTO_FAILURE_PREDICTION", config.auto_failure_prediction)
    config.auto_security_scanning = _get_env_bool("INFRADSL_AUTO_SECURITY_SCANNING", config.auto_security_scanning)
    config.auto_performance_insights = _get_env_bool("INFRADSL_AUTO_PERFORMANCE_INSIGHTS", config.auto_performance_insights)
    config.auto_drift_management = _get_env_bool("INFRADSL_AUTO_DRIFT_MANAGEMENT", config.auto_drift_management)
    config.auto_cross_cloud_optimization = _get_env_bool("INFRADSL_AUTO_CROSS_CLOUD_OPTIMIZATION", config.auto_cross_cloud_optimization)
    config.auto_nexus_networking = _get_env_bool("INFRADSL_AUTO_NEXUS_NETWORKING", config.auto_nexus_networking)
    
    # Load policies
    config.cost_optimization_aggressiveness = os.getenv("INFRADSL_COST_OPTIMIZATION_AGGRESSIVENESS", config.cost_optimization_aggressiveness)
    config.security_scan_frequency = os.getenv("INFRADSL_SECURITY_SCAN_FREQUENCY", config.security_scan_frequency)
    config.drift_check_interval = os.getenv("INFRADSL_DRIFT_CHECK_INTERVAL", config.drift_check_interval)
    config.auto_remediation_policy = os.getenv("INFRADSL_AUTO_REMEDIATION_POLICY", config.auto_remediation_policy)
    
    # Load compliance standards
    compliance_env = os.getenv("INFRADSL_DEFAULT_COMPLIANCE_STANDARDS")
    if compliance_env:
        config.default_compliance_standards = [std.strip() for std in compliance_env.split(",")]
    
    return config


def _get_env_bool(env_var: str, default: bool) -> bool:
    """Get boolean value from environment variable"""
    value = os.getenv(env_var)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def disable_auto_optimization():
    """Disable automatic optimization globally (for testing or specific use cases)"""
    global _global_config
    if _global_config is None:
        _global_config = load_global_nexus_config()
    
    _global_config.auto_cost_optimization = False
    _global_config.auto_failure_prediction = False
    _global_config.auto_security_scanning = False
    _global_config.auto_performance_insights = False
    _global_config.auto_drift_management = False
    _global_config.auto_cross_cloud_optimization = False
    _global_config.auto_nexus_networking = False


def enable_auto_optimization():
    """Re-enable automatic optimization globally"""
    global _global_config
    if _global_config is None:
        _global_config = load_global_nexus_config()
    
    _global_config.auto_cost_optimization = True
    _global_config.auto_failure_prediction = True
    _global_config.auto_security_scanning = True
    _global_config.auto_performance_insights = True
    _global_config.auto_drift_management = True
    _global_config.auto_cross_cloud_optimization = True
    _global_config.auto_nexus_networking = True