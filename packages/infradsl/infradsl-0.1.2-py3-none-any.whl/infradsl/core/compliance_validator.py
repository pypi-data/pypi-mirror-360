"""
Compliance Network Validator

Validates network configurations against regulatory requirements (SOC2, HIPAA, PCI-DSS, GDPR)
"""

import ipaddress
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

from .network_intelligence_core import NetworkIntelligence

logger = logging.getLogger(__name__)


class ComplianceNetworkValidator:
    """
    Advanced Compliance Network Validator
    
    Validates network configurations against regulatory requirements (SOC2, HIPAA, PCI-DSS)
    """
    
    def __init__(self, network_intelligence: NetworkIntelligence):
        self.network_intelligence = network_intelligence
        self.compliance_rules = {
            "SOC2": {
                "network_segmentation": True,
                "encryption_in_transit": True,
                "access_logging": True,
                "minimum_subnet_size": 26,  # /26 or larger
                "required_monitoring": ["vpc_flow_logs", "network_access_logs"],
                "forbidden_protocols": ["telnet", "ftp", "http"],
                "required_security_groups": ["database_isolation", "web_tier_isolation"]
            },
            "HIPAA": {
                "network_isolation": True,
                "encryption_in_transit": True,
                "encryption_at_rest": True,
                "dedicated_tenancy": True,
                "minimum_subnet_size": 24,  # /24 or larger
                "required_monitoring": ["all_network_traffic", "phi_access_logs"],
                "forbidden_protocols": ["telnet", "ftp", "http", "snmp_v1", "snmp_v2"],
                "required_security_groups": ["phi_isolation", "application_isolation", "database_isolation"],
                "audit_trail_retention": 2555  # 7 years in days
            },
            "PCI": {
                "network_segmentation": True,
                "cardholder_data_isolation": True,
                "encryption_in_transit": True,
                "minimum_subnet_size": 24,  # /24 or larger
                "required_monitoring": ["cardholder_data_access", "network_changes"],
                "forbidden_protocols": ["telnet", "ftp", "http"],
                "required_security_groups": ["cardholder_data_isolation", "payment_processing_isolation"],
                "regular_penetration_testing": True
            },
            "GDPR": {
                "data_locality": True,
                "encryption_in_transit": True,
                "encryption_at_rest": True,
                "minimum_subnet_size": 26,
                "required_monitoring": ["personal_data_access", "data_transfers"],
                "data_retention_controls": True,
                "right_to_be_forgotten": True
            }
        }
    
    def validate_network_compliance(self, 
                                  network_config: Dict[str, Any], 
                                  required_frameworks: List[str]) -> Dict[str, Any]:
        """
        Validate network configuration against compliance frameworks
        """
        
        validation_results = {
            "compliant": True,
            "framework_results": {},
            "violations": [],
            "recommendations": [],
            "risk_score": 0.0
        }
        
        for framework in required_frameworks:
            if framework not in self.compliance_rules:
                validation_results["violations"].append(f"Unknown compliance framework: {framework}")
                continue
            
            framework_result = self._validate_framework(network_config, framework)
            validation_results["framework_results"][framework] = framework_result
            
            if not framework_result["compliant"]:
                validation_results["compliant"] = False
                validation_results["violations"].extend(framework_result["violations"])
                validation_results["recommendations"].extend(framework_result["recommendations"])
                validation_results["risk_score"] = max(validation_results["risk_score"], framework_result["risk_score"])
        
        return validation_results
    
    def _validate_framework(self, network_config: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Validate against specific compliance framework"""
        
        rules = self.compliance_rules[framework]
        result = {
            "compliant": True,
            "violations": [],
            "recommendations": [],
            "risk_score": 0.0
        }
        
        # Validate network segmentation
        if rules.get("network_segmentation"):
            segmentation_result = self._validate_network_segmentation(network_config, framework)
            if not segmentation_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(segmentation_result["violations"])
                result["recommendations"].extend(segmentation_result["recommendations"])
                result["risk_score"] = max(result["risk_score"], segmentation_result["risk_score"])
        
        # Validate subnet sizes
        if "minimum_subnet_size" in rules:
            subnet_result = self._validate_subnet_sizes(network_config, rules["minimum_subnet_size"], framework)
            if not subnet_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(subnet_result["violations"])
                result["recommendations"].extend(subnet_result["recommendations"])
                result["risk_score"] = max(result["risk_score"], subnet_result["risk_score"])
        
        # Validate encryption requirements
        if rules.get("encryption_in_transit"):
            encryption_result = self._validate_encryption_in_transit(network_config, framework)
            if not encryption_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(encryption_result["violations"])
                result["recommendations"].extend(encryption_result["recommendations"])
                result["risk_score"] = max(result["risk_score"], encryption_result["risk_score"])
        
        # Validate monitoring requirements
        if "required_monitoring" in rules:
            monitoring_result = self._validate_monitoring_requirements(network_config, rules["required_monitoring"], framework)
            if not monitoring_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(monitoring_result["violations"])
                result["recommendations"].extend(monitoring_result["recommendations"])
                result["risk_score"] = max(result["risk_score"], monitoring_result["risk_score"])
        
        # Validate forbidden protocols
        if "forbidden_protocols" in rules:
            protocol_result = self._validate_protocol_restrictions(network_config, rules["forbidden_protocols"], framework)
            if not protocol_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(protocol_result["violations"])
                result["recommendations"].extend(protocol_result["recommendations"])
                result["risk_score"] = max(result["risk_score"], protocol_result["risk_score"])
        
        return result
    
    def _validate_network_segmentation(self, network_config: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Validate network segmentation requirements"""
        
        result = {"compliant": True, "violations": [], "recommendations": [], "risk_score": 0.0}
        
        # Check for proper tier separation
        subnets = network_config.get("subnets", [])
        tiers = set()
        
        for subnet in subnets:
            tier = subnet.get("tier", "unknown")
            tiers.add(tier)
        
        required_tiers = {"public", "private", "database"}
        if framework == "HIPAA":
            required_tiers.add("phi_isolation")
        elif framework == "PCI":
            required_tiers.add("cardholder_data")
        
        missing_tiers = required_tiers - tiers
        if missing_tiers:
            result["compliant"] = False
            result["violations"].append(f"Missing required network tiers: {missing_tiers}")
            result["recommendations"].append(f"Create isolated subnets for: {missing_tiers}")
            result["risk_score"] = 8.0  # High risk
        
        # Check for proper CIDR separation
        subnet_cidrs = [subnet.get("cidr") for subnet in subnets if subnet.get("cidr")]
        for i, cidr1 in enumerate(subnet_cidrs):
            for cidr2 in subnet_cidrs[i+1:]:
                if cidr1 and cidr2:
                    conflict_result = self.network_intelligence.detect_cidr_conflicts(cidr1, [cidr2])
                    if conflict_result["has_conflicts"]:
                        result["compliant"] = False
                        result["violations"].append(f"CIDR overlap detected: {cidr1} and {cidr2}")
                        result["recommendations"].append("Redesign CIDR allocation to eliminate overlaps")
                        result["risk_score"] = max(result["risk_score"], 6.0)
        
        return result
    
    def _validate_subnet_sizes(self, network_config: Dict[str, Any], min_size: int, framework: str) -> Dict[str, Any]:
        """Validate subnet sizes meet compliance requirements"""
        
        result = {"compliant": True, "violations": [], "recommendations": [], "risk_score": 0.0}
        
        subnets = network_config.get("subnets", [])
        
        for subnet in subnets:
            cidr = subnet.get("cidr")
            if not cidr:
                continue
            
            try:
                network = ipaddress.IPv4Network(cidr)
                if network.prefixlen > min_size:
                    result["compliant"] = False
                    result["violations"].append(
                        f"Subnet {cidr} (/{network.prefixlen}) smaller than required /{min_size} for {framework}"
                    )
                    result["recommendations"].append(
                        f"Resize subnet {cidr} to at least /{min_size} for {framework} compliance"
                    )
                    result["risk_score"] = max(result["risk_score"], 5.0)
            except ipaddress.AddressValueError:
                result["violations"].append(f"Invalid CIDR format: {cidr}")
                result["risk_score"] = max(result["risk_score"], 3.0)
        
        return result
    
    def _validate_encryption_in_transit(self, network_config: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Validate encryption in transit requirements"""
        
        result = {"compliant": True, "violations": [], "recommendations": [], "risk_score": 0.0}
        
        # Check load balancer SSL/TLS configuration
        load_balancers = network_config.get("load_balancers", [])
        for lb in load_balancers:
            if not lb.get("ssl_enabled", False):
                result["compliant"] = False
                result["violations"].append(f"Load balancer {lb.get('name', 'unknown')} missing SSL/TLS encryption")
                result["recommendations"].append("Enable SSL/TLS encryption on all load balancers")
                result["risk_score"] = max(result["risk_score"], 7.0)
        
        # Check for HTTP listeners (should be HTTPS)
        for lb in load_balancers:
            listeners = lb.get("listeners", [])
            for listener in listeners:
                if listener.get("protocol") == "HTTP":
                    result["compliant"] = False
                    result["violations"].append(f"HTTP listener detected on load balancer {lb.get('name', 'unknown')}")
                    result["recommendations"].append("Replace HTTP listeners with HTTPS")
                    result["risk_score"] = max(result["risk_score"], 8.0)
        
        return result
    
    def _validate_monitoring_requirements(self, network_config: Dict[str, Any], required_monitoring: List[str], framework: str) -> Dict[str, Any]:
        """Validate monitoring requirements"""
        
        result = {"compliant": True, "violations": [], "recommendations": [], "risk_score": 0.0}
        
        enabled_monitoring = network_config.get("monitoring", {}).get("enabled_features", [])
        
        missing_monitoring = set(required_monitoring) - set(enabled_monitoring)
        if missing_monitoring:
            result["compliant"] = False
            result["violations"].append(f"Missing required monitoring for {framework}: {missing_monitoring}")
            result["recommendations"].append(f"Enable monitoring features: {missing_monitoring}")
            result["risk_score"] = 6.0
        
        return result
    
    def _validate_protocol_restrictions(self, network_config: Dict[str, Any], forbidden_protocols: List[str], framework: str) -> Dict[str, Any]:
        """Validate protocol restrictions"""
        
        result = {"compliant": True, "violations": [], "recommendations": [], "risk_score": 0.0}
        
        # Check security group rules
        security_groups = network_config.get("security_groups", [])
        for sg in security_groups:
            rules = sg.get("rules", [])
            for rule in rules:
                protocol = rule.get("protocol", "").lower()
                if protocol in forbidden_protocols:
                    result["compliant"] = False
                    result["violations"].append(
                        f"Forbidden protocol {protocol} found in security group {sg.get('name', 'unknown')}"
                    )
                    result["recommendations"].append(f"Remove {protocol} protocol from security group rules")
                    result["risk_score"] = max(result["risk_score"], 7.0)
        
        return result
    
    def generate_compliance_report(self, network_config: Dict[str, Any], frameworks: List[str]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        validation_results = self.validate_network_compliance(network_config, frameworks)
        
        report = {
            "report_id": f"compliance-{int(time.time())}",
            "generated_at": datetime.now().isoformat(),
            "network_config_summary": {
                "total_vpcs": len(network_config.get("vpcs", [])),
                "total_subnets": len(network_config.get("subnets", [])),
                "total_security_groups": len(network_config.get("security_groups", [])),
                "frameworks_evaluated": frameworks
            },
            "compliance_status": {
                "overall_compliant": validation_results["compliant"],
                "risk_score": validation_results["risk_score"],
                "total_violations": len(validation_results["violations"]),
                "framework_breakdown": validation_results["framework_results"]
            },
            "violations": validation_results["violations"],
            "recommendations": validation_results["recommendations"],
            "remediation_priority": self._prioritize_remediation(validation_results["violations"]),
            "estimated_remediation_time": self._estimate_remediation_time(validation_results["violations"])
        }
        
        return report
    
    def _prioritize_remediation(self, violations: List[str]) -> List[Dict[str, Any]]:
        """Prioritize remediation actions"""
        
        priority_mapping = {
            "encryption": {"priority": "critical", "effort": "medium"},
            "protocol": {"priority": "high", "effort": "low"},
            "segmentation": {"priority": "high", "effort": "high"},
            "monitoring": {"priority": "medium", "effort": "low"},
            "subnet": {"priority": "medium", "effort": "medium"}
        }
        
        prioritized = []
        for violation in violations:
            priority_info = {"violation": violation, "priority": "low", "effort": "unknown"}
            
            for key, mapping in priority_mapping.items():
                if key in violation.lower():
                    priority_info.update(mapping)
                    break
            
            prioritized.append(priority_info)
        
        # Sort by priority: critical -> high -> medium -> low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        prioritized.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return prioritized
    
    def _estimate_remediation_time(self, violations: List[str]) -> Dict[str, Any]:
        """Estimate time required for remediation"""
        
        time_estimates = {
            "encryption": 2,  # days
            "protocol": 0.5,  # days
            "segmentation": 5,  # days
            "monitoring": 1,  # days
            "subnet": 3  # days
        }
        
        total_days = 0
        breakdown = {}
        
        for violation in violations:
            for key, days in time_estimates.items():
                if key in violation.lower():
                    total_days += days
                    breakdown[key] = breakdown.get(key, 0) + days
                    break
        
        return {
            "total_days": total_days,
            "total_weeks": round(total_days / 7, 1),
            "breakdown_by_category": breakdown,
            "parallel_execution_days": max(breakdown.values()) if breakdown else 0
        }