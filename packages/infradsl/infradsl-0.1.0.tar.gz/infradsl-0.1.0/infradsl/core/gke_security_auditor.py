"""
GKE Security Auditor

Comprehensive security analysis and recommendations for GCP GKE clusters.
"""

from typing import Dict, Any, List
from datetime import datetime
from .gke_types import GKESecurityFinding, GKESecurityAssessment


class GKESecurityAuditor:
    """
    GKE Security Audit Engine
    
    Provides comprehensive security analysis including:
    - Workload Identity configuration
    - Binary Authorization compliance
    - Network security policies
    - Node security configuration
    - RBAC and access controls
    """
    
    def __init__(self, security_thresholds: Dict[str, Any]):
        self.security_thresholds = security_thresholds
    
    def generate_security_assessment(self, cluster_data: Dict[str, Any]) -> GKESecurityAssessment:
        """Generate comprehensive GKE security assessment"""
        
        findings = []
        
        # Security configuration audit
        security_findings = self._audit_security_config(cluster_data)
        findings.extend(security_findings)
        
        # Node security audit
        node_findings = self._audit_node_security(cluster_data.get("node_pools", []))
        findings.extend(node_findings)
        
        # Network security audit
        network_findings = self._audit_network_security(cluster_data)
        findings.extend(network_findings)
        
        # Calculate overall security score
        security_score = self._calculate_security_score(findings)
        
        # Determine risk level
        risk_level = self._determine_risk_level(security_score)
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(findings)
        
        return GKESecurityAssessment(
            cluster_name=cluster_data.get("cluster_name"),
            assessment_timestamp=datetime.now().isoformat(),
            overall_security_score=security_score,
            security_findings=findings,
            compliance_status={},
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _audit_security_config(self, cluster_data: Dict[str, Any]) -> List[GKESecurityFinding]:
        """Audit GKE security configuration"""
        
        findings = []
        security_config = cluster_data.get("security_config", {})
        private_cluster = cluster_data.get("private_cluster_config", {})
        
        # Workload Identity
        if not security_config.get("workload_identity_enabled", False):
            findings.append(GKESecurityFinding(
                severity="high",
                category="authentication",
                finding="Workload Identity is not enabled",
                recommendation="Enable Workload Identity for secure service account authentication"
            ))
        
        # Binary Authorization
        if not security_config.get("binary_authorization_enabled", False):
            findings.append(GKESecurityFinding(
                severity="medium",
                category="container_security",
                finding="Binary Authorization is not enabled",
                recommendation="Enable Binary Authorization to ensure only trusted container images are deployed"
            ))
        
        # Private nodes
        if not private_cluster.get("enable_private_nodes", False):
            findings.append(GKESecurityFinding(
                severity="high",
                category="network_security",
                finding="Private nodes are not enabled",
                recommendation="Enable private nodes to isolate worker nodes from public internet"
            ))
        
        # Network Policy
        if not security_config.get("network_policy_enabled", False):
            findings.append(GKESecurityFinding(
                severity="medium",
                category="network_security",
                finding="Network Policy is not enabled",
                recommendation="Enable Network Policy for pod-to-pod traffic control"
            ))
        
        # Pod Security Policy/Standards
        if not security_config.get("pod_security_policy_enabled", False):
            findings.append(GKESecurityFinding(
                severity="medium",
                category="runtime_security",
                finding="Pod Security Standards are not implemented",
                recommendation="Implement Pod Security Standards for runtime security controls"
            ))
        
        return findings
    
    def _audit_node_security(self, node_pools: List[Dict[str, Any]]) -> List[GKESecurityFinding]:
        """Audit node pool security configurations"""
        
        findings = []
        
        for pool in node_pools:
            pool_name = pool.get("name")
            node_config = pool.get("node_config", {})
            management = pool.get("management", {})
            
            # Image type check
            image_type = node_config.get("image_type", "")
            if "COS" not in image_type:
                findings.append(GKESecurityFinding(
                    severity="medium",
                    category="node_security",
                    finding=f"Node pool {pool_name} not using Container-Optimized OS",
                    recommendation="Use Container-Optimized OS (COS) for better security",
                    resource=pool_name
                ))
            
            # Automatic upgrades
            if not management.get("auto_upgrade", False):
                findings.append(GKESecurityFinding(
                    severity="medium",
                    category="node_security",
                    finding=f"Auto-upgrade disabled for node pool {pool_name}",
                    recommendation="Enable auto-upgrade for security patches",
                    resource=pool_name
                ))
            
            # Automatic repair
            if not management.get("auto_repair", False):
                findings.append(GKESecurityFinding(
                    severity="low",
                    category="node_security",
                    finding=f"Auto-repair disabled for node pool {pool_name}",
                    recommendation="Enable auto-repair for better reliability",
                    resource=pool_name
                ))
        
        return findings
    
    def _audit_network_security(self, cluster_data: Dict[str, Any]) -> List[GKESecurityFinding]:
        """Audit network security configuration"""
        
        findings = []
        addons = cluster_data.get("addons_config", {})
        private_cluster = cluster_data.get("private_cluster_config", {})
        
        # Kubernetes Dashboard (should be disabled)
        if not addons.get("kubernetes_dashboard", {}).get("disabled", True):
            findings.append(GKESecurityFinding(
                severity="critical",
                category="network_security",
                finding="Kubernetes Dashboard is enabled",
                recommendation="Disable Kubernetes Dashboard and use Cloud Console for cluster management"
            ))
        
        # Private endpoint
        if private_cluster.get("enable_private_nodes", False) and not private_cluster.get("enable_private_endpoint", False):
            findings.append(GKESecurityFinding(
                severity="medium",
                category="network_security",
                finding="Private cluster without private endpoint",
                recommendation="Consider enabling private endpoint for enhanced security"
            ))
        
        # Master authorized networks (if available in data)
        master_auth_networks = private_cluster.get("master_authorized_networks", {})
        if not master_auth_networks.get("enabled", False) and not private_cluster.get("enable_private_endpoint", False):
            findings.append(GKESecurityFinding(
                severity="medium",
                category="network_security",
                finding="Master authorized networks not configured",
                recommendation="Configure master authorized networks to restrict API server access"
            ))
        
        return findings
    
    def _calculate_security_score(self, findings: List[GKESecurityFinding]) -> float:
        """Calculate overall GKE security score"""
        
        base_score = 100.0
        
        for finding in findings:
            severity = finding.severity
            
            if severity == "critical":
                base_score -= 30
            elif severity == "high":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5
        
        return max(0.0, base_score)
    
    def _determine_risk_level(self, security_score: float) -> str:
        """Determine risk level based on security score"""
        
        if security_score < 40:
            return "critical"
        elif security_score < 70:
            return "high"
        elif security_score < 85:
            return "medium"
        else:
            return "low"
    
    def _generate_security_recommendations(self, findings: List[GKESecurityFinding]) -> List[str]:
        """Generate security recommendations based on findings"""
        
        recommendations = []
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.category
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        # Generate category-specific recommendations
        if "authentication" in categories:
            recommendations.append("Implement strong authentication mechanisms")
            recommendations.append("Use Workload Identity for service account management")
        
        if "network_security" in categories:
            recommendations.append("Implement network segmentation and policies")
            recommendations.append("Use private clusters for sensitive workloads")
        
        if "container_security" in categories:
            recommendations.append("Implement container image scanning and validation")
            recommendations.append("Use admission controllers for policy enforcement")
        
        if "node_security" in categories:
            recommendations.append("Keep nodes updated with latest security patches")
            recommendations.append("Use Container-Optimized OS for all node pools")
        
        if "runtime_security" in categories:
            recommendations.append("Implement Pod Security Standards")
            recommendations.append("Use resource quotas and limits")
        
        # General recommendations
        recommendations.append("Regular security audits and compliance checks")
        recommendations.append("Implement least privilege access controls")
        recommendations.append("Monitor cluster activity with Cloud Audit Logs")
        recommendations.append("Use encrypted communication between components")
        
        return list(set(recommendations))  # Remove duplicates
    
    def audit_rbac_configuration(self, cluster_data: Dict[str, Any]) -> List[GKESecurityFinding]:
        """Audit RBAC configuration (if RBAC data is available)"""
        
        findings = []
        
        # This would require actual RBAC data from the cluster
        # For now, we provide general RBAC recommendations
        findings.append(GKESecurityFinding(
            severity="medium",
            category="access_control",
            finding="RBAC configuration not audited",
            recommendation="Regularly audit RBAC configurations for least privilege access"
        ))
        
        return findings
    
    def check_compliance_frameworks(self, cluster_data: Dict[str, Any], 
                                  frameworks: List[str]) -> Dict[str, Any]:
        """Check compliance against security frameworks"""
        
        compliance_status = {}
        
        for framework in frameworks:
            if framework.upper() == "CIS":
                compliance_status["CIS"] = self._check_cis_compliance(cluster_data)
            elif framework.upper() == "NIST":
                compliance_status["NIST"] = self._check_nist_compliance(cluster_data)
            elif framework.upper() == "SOC2":
                compliance_status["SOC2"] = self._check_soc2_compliance(cluster_data)
        
        return compliance_status
    
    def _check_cis_compliance(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check CIS Kubernetes Benchmark compliance"""
        
        security_config = cluster_data.get("security_config", {})
        private_cluster = cluster_data.get("private_cluster_config", {})
        
        checks = {
            "workload_identity": security_config.get("workload_identity_enabled", False),
            "private_nodes": private_cluster.get("enable_private_nodes", False),
            "network_policy": security_config.get("network_policy_enabled", False),
            "binary_authorization": security_config.get("binary_authorization_enabled", False)
        }
        
        passed_checks = sum(1 for check in checks.values() if check)
        total_checks = len(checks)
        
        return {
            "compliance_percentage": (passed_checks / total_checks) * 100,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "details": checks
        }
    
    def _check_nist_compliance(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check NIST compliance"""
        
        # Simplified NIST checks
        security_score = self._calculate_security_score(self._audit_security_config(cluster_data))
        
        return {
            "compliance_percentage": security_score,
            "assessment": "partial" if security_score > 70 else "non_compliant"
        }
    
    def _check_soc2_compliance(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check SOC 2 compliance"""
        
        # SOC 2 focuses on security, availability, processing integrity, confidentiality, and privacy
        private_cluster = cluster_data.get("private_cluster_config", {})
        security_config = cluster_data.get("security_config", {})
        
        soc2_controls = {
            "access_control": security_config.get("workload_identity_enabled", False),
            "network_security": private_cluster.get("enable_private_nodes", False),
            "monitoring": cluster_data.get("logging_service") is not None,
            "encryption": True  # Assume encryption at rest is enabled by default in GKE
        }
        
        passed_controls = sum(1 for control in soc2_controls.values() if control)
        total_controls = len(soc2_controls)
        
        return {
            "compliance_percentage": (passed_controls / total_controls) * 100,
            "passed_controls": passed_controls,
            "total_controls": total_controls,
            "details": soc2_controls
        }