"""
AWS VPC Intelligence

Advanced intelligence for AWS Virtual Private Cloud (VPC) networking
providing intelligent network design, security optimization, and cost analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)


class AWSVPCIntelligence(AWSIntelligenceBase):
    """
    AWS VPC Intelligence Engine
    
    Provides intelligent VPC networking including:
    - Smart CIDR planning and subnet optimization
    - Security group and NACL recommendations
    - VPC peering and transit gateway optimization
    - Internet gateway and NAT gateway cost optimization
    - Flow logs analysis and recommendations
    - Multi-AZ networking best practices
    """
    
    def __init__(self):
        super().__init__(ResourceType.NETWORK)
        self.optimization_rules = {
            "cidr_planning": {
                "minimum_subnets_per_tier": 2,  # Minimum subnets per tier
                "minimum_az_coverage": 2,       # Minimum availability zones
                "reserved_ip_percentage": 0.25,  # Reserve 25% for growth
                "subnet_size_guidelines": {
                    "public": "/24",     # 254 IPs
                    "private": "/23",    # 510 IPs
                    "database": "/24"    # 254 IPs
                }
            },
            "cost_optimization": {
                "nat_gateway_monthly_cost": 45.00,      # Per NAT gateway
                "internet_gateway_cost": 0.00,          # Free
                "vpc_endpoint_monthly_cost": 7.20,      # Per endpoint
                "transit_gateway_attachment_cost": 36.00, # Per attachment
                "data_processing_cost_per_gb": 0.02     # Data processing
            },
            "security_thresholds": {
                "max_ingress_rules_per_sg": 60,
                "max_egress_rules_per_sg": 60,
                "max_security_groups_per_instance": 5,
                "recommended_nacl_rules": 20
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing VPC resources"""
        
        # Mock implementation - in production would use boto3
        return {
            "vpc-production": {
                "vpc_id": "vpc-12345678",
                "cidr_block": "10.0.0.0/16",
                "state": "available",
                "enable_dns_hostnames": True,
                "enable_dns_support": True,
                "instance_tenancy": "default",
                "subnets": [
                    {
                        "subnet_id": "subnet-web-1a",
                        "cidr_block": "10.0.1.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "available",
                        "subnet_type": "public",
                        "auto_assign_public_ip": True,
                        "available_ip_count": 251
                    },
                    {
                        "subnet_id": "subnet-web-1b",
                        "cidr_block": "10.0.2.0/24",
                        "availability_zone": "us-east-1b",
                        "state": "available",
                        "subnet_type": "public",
                        "auto_assign_public_ip": True,
                        "available_ip_count": 248
                    },
                    {
                        "subnet_id": "subnet-app-1a",
                        "cidr_block": "10.0.10.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "available",
                        "subnet_type": "private",
                        "auto_assign_public_ip": False,
                        "available_ip_count": 240
                    },
                    {
                        "subnet_id": "subnet-app-1b",
                        "cidr_block": "10.0.11.0/24",
                        "availability_zone": "us-east-1b",
                        "state": "available",
                        "subnet_type": "private",
                        "auto_assign_public_ip": False,
                        "available_ip_count": 235
                    },
                    {
                        "subnet_id": "subnet-db-1a",
                        "cidr_block": "10.0.20.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "available",
                        "subnet_type": "database",
                        "auto_assign_public_ip": False,
                        "available_ip_count": 250
                    }
                ],
                "internet_gateway": {
                    "igw_id": "igw-12345678",
                    "state": "attached"
                },
                "nat_gateways": [
                    {
                        "nat_gateway_id": "nat-12345678",
                        "subnet_id": "subnet-web-1a",
                        "state": "available",
                        "connectivity_type": "public",
                        "elastic_ip": "203.0.113.1"
                    },
                    {
                        "nat_gateway_id": "nat-87654321",
                        "subnet_id": "subnet-web-1b",
                        "state": "available",
                        "connectivity_type": "public",
                        "elastic_ip": "203.0.113.2"
                    }
                ],
                "route_tables": [
                    {
                        "route_table_id": "rtb-public",
                        "routes": [
                            {"destination": "10.0.0.0/16", "target": "local"},
                            {"destination": "0.0.0.0/0", "target": "igw-12345678"}
                        ],
                        "associated_subnets": ["subnet-web-1a", "subnet-web-1b"]
                    },
                    {
                        "route_table_id": "rtb-private-1a",
                        "routes": [
                            {"destination": "10.0.0.0/16", "target": "local"},
                            {"destination": "0.0.0.0/0", "target": "nat-12345678"}
                        ],
                        "associated_subnets": ["subnet-app-1a", "subnet-db-1a"]
                    }
                ],
                "security_groups": [
                    {
                        "group_id": "sg-web-tier",
                        "group_name": "web-tier-sg",
                        "description": "Security group for web tier",
                        "ingress_rules": [
                            {"protocol": "tcp", "port_range": "80-80", "source": "0.0.0.0/0"},
                            {"protocol": "tcp", "port_range": "443-443", "source": "0.0.0.0/0"},
                            {"protocol": "tcp", "port_range": "22-22", "source": "10.0.0.0/16"}
                        ],
                        "egress_rules": [
                            {"protocol": "all", "port_range": "all", "destination": "0.0.0.0/0"}
                        ]
                    },
                    {
                        "group_id": "sg-app-tier",
                        "group_name": "app-tier-sg",
                        "description": "Security group for application tier",
                        "ingress_rules": [
                            {"protocol": "tcp", "port_range": "8080-8080", "source": "sg-web-tier"},
                            {"protocol": "tcp", "port_range": "22-22", "source": "10.0.0.0/16"}
                        ],
                        "egress_rules": [
                            {"protocol": "all", "port_range": "all", "destination": "0.0.0.0/0"}
                        ]
                    }
                ],
                "vpc_endpoints": [
                    {
                        "vpc_endpoint_id": "vpce-s3-12345678",
                        "service_name": "com.amazonaws.us-east-1.s3",
                        "vpc_endpoint_type": "Gateway",
                        "state": "available"
                    }
                ],
                "flow_logs": {
                    "enabled": True,
                    "destination": "cloudwatch",
                    "traffic_type": "ALL",
                    "log_group": "vpc-flow-logs"
                },
                "metrics": {
                    "monthly_data_transfer_gb": 2500,
                    "nat_gateway_hourly_rate": 0.045,
                    "vpc_endpoint_hourly_rate": 0.01,
                    "average_bandwidth_utilization": 0.35
                }
            },
            "vpc-development": {
                "vpc_id": "vpc-dev-87654321",
                "cidr_block": "172.16.0.0/16",
                "state": "available",
                "enable_dns_hostnames": True,
                "enable_dns_support": True,
                "instance_tenancy": "default",
                "subnets": [
                    {
                        "subnet_id": "subnet-dev-1a",
                        "cidr_block": "172.16.1.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "available",
                        "subnet_type": "public",
                        "auto_assign_public_ip": True,
                        "available_ip_count": 220
                    }
                ],
                "internet_gateway": {
                    "igw_id": "igw-dev-87654321",
                    "state": "attached"
                },
                "nat_gateways": [],
                "route_tables": [
                    {
                        "route_table_id": "rtb-dev-public",
                        "routes": [
                            {"destination": "172.16.0.0/16", "target": "local"},
                            {"destination": "0.0.0.0/0", "target": "igw-dev-87654321"}
                        ],
                        "associated_subnets": ["subnet-dev-1a"]
                    }
                ],
                "security_groups": [
                    {
                        "group_id": "sg-dev-default",
                        "group_name": "dev-default-sg",
                        "description": "Default development security group",
                        "ingress_rules": [
                            {"protocol": "all", "port_range": "all", "source": "0.0.0.0/0"}
                        ],
                        "egress_rules": [
                            {"protocol": "all", "port_range": "all", "destination": "0.0.0.0/0"}
                        ]
                    }
                ],
                "vpc_endpoints": [],
                "flow_logs": {"enabled": False},
                "metrics": {
                    "monthly_data_transfer_gb": 150,
                    "average_bandwidth_utilization": 0.15
                }
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract VPC configuration from cloud state"""
        
        return {
            "vpc_id": cloud_state.get("vpc_id"),
            "cidr_block": cloud_state.get("cidr_block"),
            "enable_dns_hostnames": cloud_state.get("enable_dns_hostnames"),
            "enable_dns_support": cloud_state.get("enable_dns_support"),
            "subnets": cloud_state.get("subnets", []),
            "internet_gateway": cloud_state.get("internet_gateway"),
            "nat_gateways": cloud_state.get("nat_gateways", []),
            "route_tables": cloud_state.get("route_tables", []),
            "security_groups": cloud_state.get("security_groups", []),
            "vpc_endpoints": cloud_state.get("vpc_endpoints", []),
            "flow_logs": cloud_state.get("flow_logs", {}),
            "metrics": cloud_state.get("metrics", {})
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for VPC configuration"""
        
        # Focus on key networking configuration elements
        key_config = {
            "vpc_id": config.get("vpc_id"),
            "cidr_block": config.get("cidr_block"),
            "subnets": [
                {
                    "cidr_block": s.get("cidr_block"),
                    "availability_zone": s.get("availability_zone"),
                    "subnet_type": s.get("subnet_type")
                }
                for s in config.get("subnets", [])
            ],
            "nat_gateways": len(config.get("nat_gateways", [])),
            "vpc_endpoints": len(config.get("vpc_endpoints", [])),
            "security_groups": [
                {
                    "group_name": sg.get("group_name"),
                    "ingress_rules": len(sg.get("ingress_rules", [])),
                    "egress_rules": len(sg.get("egress_rules", []))
                }
                for sg in config.get("security_groups", [])
            ]
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    def analyze_vpc_optimization(self, vpc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze VPC for optimization opportunities
        """
        
        optimization_analysis = {
            "vpc_id": vpc_data.get("vpc_id"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "security_recommendations": [],
            "subnet_optimization": {},
            "cost_breakdown": {},
            "compliance_score": 0.0
        }
        
        # Cost analysis
        cost_analysis = self._analyze_vpc_costs(vpc_data)
        optimization_analysis.update(cost_analysis)
        
        # Security analysis
        security_analysis = self._analyze_vpc_security(vpc_data)
        optimization_analysis["security_recommendations"] = security_analysis
        
        # Subnet optimization
        subnet_analysis = self._analyze_subnet_optimization(vpc_data)
        optimization_analysis["subnet_optimization"] = subnet_analysis
        
        # Architecture recommendations
        architecture_recommendations = self._analyze_vpc_architecture(vpc_data)
        optimization_analysis["recommendations"].extend(architecture_recommendations)
        
        # Compliance scoring
        compliance_score = self._calculate_compliance_score(vpc_data)
        optimization_analysis["compliance_score"] = compliance_score
        
        return optimization_analysis
    
    def _analyze_vpc_costs(self, vpc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze VPC cost optimization opportunities"""
        
        metrics = vpc_data.get("metrics", {})
        nat_gateways = vpc_data.get("nat_gateways", [])
        vpc_endpoints = vpc_data.get("vpc_endpoints", [])
        
        # Calculate current costs
        nat_gateway_cost = len(nat_gateways) * self.optimization_rules["cost_optimization"]["nat_gateway_monthly_cost"]
        vpc_endpoint_cost = len(vpc_endpoints) * self.optimization_rules["cost_optimization"]["vpc_endpoint_monthly_cost"]
        
        data_transfer = metrics.get("monthly_data_transfer_gb", 0)
        data_cost = data_transfer * self.optimization_rules["cost_optimization"]["data_processing_cost_per_gb"]
        
        current_monthly_cost = nat_gateway_cost + vpc_endpoint_cost + data_cost
        optimized_cost = current_monthly_cost
        recommendations = []
        
        # NAT Gateway optimization
        bandwidth_utilization = metrics.get("average_bandwidth_utilization", 0.5)
        if len(nat_gateways) > 1 and bandwidth_utilization < 0.3:
            recommendations.append("Consider consolidating NAT gateways - low bandwidth utilization detected")
            potential_savings = self.optimization_rules["cost_optimization"]["nat_gateway_monthly_cost"]
            optimized_cost -= potential_savings
        
        # VPC Endpoints optimization
        if len(vpc_endpoints) == 0 and data_transfer > 1000:
            recommendations.append("Add VPC endpoints for S3 and DynamoDB to reduce data transfer costs")
            # Potential savings from reduced data transfer
            estimated_savings = data_transfer * 0.3 * self.optimization_rules["cost_optimization"]["data_processing_cost_per_gb"]
            optimized_cost -= estimated_savings
        
        # Data transfer optimization
        if data_transfer > 5000:
            recommendations.append("High data transfer detected - review architecture for data locality optimization")
        
        return {
            "current_cost_estimate": current_monthly_cost,
            "optimized_cost_estimate": optimized_cost,
            "potential_savings": current_monthly_cost - optimized_cost,
            "cost_breakdown": {
                "nat_gateways": nat_gateway_cost,
                "vpc_endpoints": vpc_endpoint_cost,
                "data_transfer": data_cost
            },
            "recommendations": recommendations
        }
    
    def _analyze_vpc_security(self, vpc_data: Dict[str, Any]) -> List[str]:
        """Analyze VPC security configuration"""
        
        recommendations = []
        security_groups = vpc_data.get("security_groups", [])
        flow_logs = vpc_data.get("flow_logs", {})
        subnets = vpc_data.get("subnets", [])
        
        # Flow logs analysis
        if not flow_logs.get("enabled", False):
            recommendations.append("Enable VPC Flow Logs for network monitoring and security analysis")
        
        # Security group analysis
        for sg in security_groups:
            ingress_rules = sg.get("ingress_rules", [])
            
            # Check for overly permissive rules
            for rule in ingress_rules:
                if rule.get("source") == "0.0.0.0/0":
                    if rule.get("protocol") == "all" or rule.get("port_range") == "all":
                        recommendations.append(f"Security group {sg.get('group_name')} has overly permissive ingress rules")
                    elif rule.get("port_range") not in ["80-80", "443-443"]:
                        recommendations.append(f"Review public access for non-standard ports in {sg.get('group_name')}")
            
            # Check rule count
            if len(ingress_rules) > self.optimization_rules["security_thresholds"]["max_ingress_rules_per_sg"]:
                recommendations.append(f"Security group {sg.get('group_name')} has too many rules - consider consolidation")
        
        # Subnet security analysis
        public_subnets = [s for s in subnets if s.get("subnet_type") == "public"]
        private_subnets = [s for s in subnets if s.get("subnet_type") == "private"]
        database_subnets = [s for s in subnets if s.get("subnet_type") == "database"]
        
        if len(database_subnets) == 0 and len(private_subnets) > 0:
            recommendations.append("Consider dedicated database subnets for better security isolation")
        
        # Multi-AZ recommendations
        availability_zones = set(s.get("availability_zone") for s in subnets)
        if len(availability_zones) < self.optimization_rules["cidr_planning"]["minimum_az_coverage"]:
            recommendations.append("Deploy across multiple availability zones for high availability")
        
        return recommendations
    
    def _analyze_subnet_optimization(self, vpc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze subnet configuration and utilization"""
        
        subnets = vpc_data.get("subnets", [])
        cidr_block = vpc_data.get("cidr_block", "")
        
        subnet_analysis = {
            "total_subnets": len(subnets),
            "subnet_utilization": {},
            "recommendations": [],
            "ip_allocation_efficiency": 0.0
        }
        
        total_available_ips = 0
        total_allocated_ips = 0
        
        # Analyze each subnet
        for subnet in subnets:
            subnet_id = subnet.get("subnet_id")
            available_ips = subnet.get("available_ip_count", 0)
            cidr = subnet.get("cidr_block", "")
            
            # Calculate subnet size (rough estimation)
            if "/24" in cidr:
                total_ips = 254  # /24 subnet
            elif "/23" in cidr:
                total_ips = 510  # /23 subnet
            elif "/25" in cidr:
                total_ips = 126  # /25 subnet
            else:
                total_ips = 254  # Default assumption
            
            allocated_ips = total_ips - available_ips
            utilization = allocated_ips / total_ips if total_ips > 0 else 0
            
            subnet_analysis["subnet_utilization"][subnet_id] = {
                "total_ips": total_ips,
                "allocated_ips": allocated_ips,
                "available_ips": available_ips,
                "utilization_percentage": utilization * 100
            }
            
            total_available_ips += available_ips
            total_allocated_ips += allocated_ips
            
            # Utilization recommendations
            if utilization > 0.85:
                subnet_analysis["recommendations"].append(
                    f"Subnet {subnet_id} is highly utilized ({utilization:.1%}) - consider expanding"
                )
            elif utilization < 0.10:
                subnet_analysis["recommendations"].append(
                    f"Subnet {subnet_id} is underutilized ({utilization:.1%}) - consider consolidation"
                )
        
        # Overall IP allocation efficiency
        total_ips = total_available_ips + total_allocated_ips
        if total_ips > 0:
            subnet_analysis["ip_allocation_efficiency"] = total_allocated_ips / total_ips
        
        return subnet_analysis
    
    def _analyze_vpc_architecture(self, vpc_data: Dict[str, Any]) -> List[str]:
        """Analyze VPC architecture for best practices"""
        
        recommendations = []
        subnets = vpc_data.get("subnets", [])
        nat_gateways = vpc_data.get("nat_gateways", [])
        internet_gateway = vpc_data.get("internet_gateway")
        vpc_endpoints = vpc_data.get("vpc_endpoints", [])
        
        # Subnet tier analysis
        subnet_types = set(s.get("subnet_type") for s in subnets)
        if "private" in subnet_types and len(nat_gateways) == 0:
            recommendations.append("Private subnets require NAT gateways or NAT instances for internet access")
        
        # High availability recommendations
        if len(nat_gateways) == 1:
            recommendations.append("Deploy NAT gateways in multiple AZs for high availability")
        
        # Internet Gateway recommendations
        if not internet_gateway or internet_gateway.get("state") != "attached":
            recommendations.append("Ensure Internet Gateway is properly attached for public subnet connectivity")
        
        # VPC Endpoints recommendations
        if len(vpc_endpoints) == 0:
            recommendations.append("Consider VPC endpoints for AWS services to reduce costs and improve security")
        
        # DNS recommendations
        if not vpc_data.get("enable_dns_hostnames") or not vpc_data.get("enable_dns_support"):
            recommendations.append("Enable DNS hostnames and DNS support for proper service discovery")
        
        return recommendations
    
    def _calculate_compliance_score(self, vpc_data: Dict[str, Any]) -> float:
        """Calculate VPC compliance score"""
        
        score = 0.0
        max_score = 100.0
        
        # Flow logs (20 points)
        if vpc_data.get("flow_logs", {}).get("enabled", False):
            score += 20.0
        
        # Multi-AZ deployment (20 points)
        subnets = vpc_data.get("subnets", [])
        availability_zones = set(s.get("availability_zone") for s in subnets)
        if len(availability_zones) >= 2:
            score += 20.0
        
        # Proper subnet tiers (20 points)
        subnet_types = set(s.get("subnet_type") for s in subnets)
        if len(subnet_types) >= 2:  # At least public and private
            score += 20.0
        
        # Security groups (20 points)
        security_groups = vpc_data.get("security_groups", [])
        overly_permissive = False
        for sg in security_groups:
            for rule in sg.get("ingress_rules", []):
                if rule.get("source") == "0.0.0.0/0" and rule.get("protocol") == "all":
                    overly_permissive = True
                    break
        
        if not overly_permissive and len(security_groups) > 0:
            score += 20.0
        
        # DNS configuration (10 points)
        if vpc_data.get("enable_dns_hostnames") and vpc_data.get("enable_dns_support"):
            score += 10.0
        
        # VPC endpoints (10 points)
        if len(vpc_data.get("vpc_endpoints", [])) > 0:
            score += 10.0
        
        return min(score, max_score)
    
    def predict_network_scaling(self, vpc_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict network scaling needs based on historical metrics
        """
        
        if not metrics_history:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze bandwidth and connection patterns
        bandwidth_values = [m.get("bandwidth_utilization", 0) for m in metrics_history]
        data_transfer_values = [m.get("data_transfer_gb", 0) for m in metrics_history]
        connection_counts = [m.get("active_connections", 0) for m in metrics_history]
        
        avg_bandwidth = sum(bandwidth_values) / len(bandwidth_values)
        avg_data_transfer = sum(data_transfer_values) / len(data_transfer_values)
        peak_bandwidth = max(bandwidth_values) if bandwidth_values else 0
        
        # Trend analysis
        if len(bandwidth_values) >= 7:
            recent_avg = sum(bandwidth_values[-7:]) / 7
            earlier_avg = sum(bandwidth_values[:7]) / 7
            bandwidth_trend = "increasing" if recent_avg > earlier_avg * 1.1 else "stable"
        else:
            bandwidth_trend = "stable"
        
        prediction = {
            "vpc_name": vpc_name,
            "network_analysis": {
                "average_bandwidth_utilization": avg_bandwidth,
                "peak_bandwidth_utilization": peak_bandwidth,
                "average_monthly_data_transfer": avg_data_transfer,
                "bandwidth_trend": bandwidth_trend
            },
            "scaling_prediction": self._generate_network_scaling_prediction(avg_bandwidth, peak_bandwidth, bandwidth_trend),
            "capacity_recommendations": self._generate_network_capacity_recommendations(avg_bandwidth, avg_data_transfer),
            "confidence_score": min(len(metrics_history) / 30.0, 1.0)  # 30 days of data = 100%
        }
        
        return prediction
    
    def _generate_network_scaling_prediction(self, avg_bandwidth: float, peak_bandwidth: float, trend: str) -> Dict[str, Any]:
        """Generate network scaling predictions"""
        
        if trend == "increasing" and peak_bandwidth > 0.8:
            return {
                "action": "scale_network_capacity",
                "confidence": "high",
                "recommendation": "Network utilization trending upward - prepare for capacity expansion",
                "suggested_actions": ["Add additional NAT gateways", "Consider Transit Gateway for complex routing"]
            }
        elif peak_bandwidth > 0.9:
            return {
                "action": "immediate_scaling_required",
                "confidence": "high",
                "recommendation": "High network utilization detected - immediate scaling recommended",
                "suggested_actions": ["Scale NAT gateway capacity", "Review bandwidth-intensive applications"]
            }
        elif avg_bandwidth < 0.2:
            return {
                "action": "optimize_for_cost",
                "confidence": "medium",
                "recommendation": "Low network utilization - optimize for cost efficiency",
                "suggested_actions": ["Consolidate NAT gateways", "Review over-provisioned resources"]
            }
        else:
            return {
                "action": "maintain",
                "confidence": "medium",
                "recommendation": "Network utilization appears optimal",
                "suggested_actions": ["Continue monitoring", "Maintain current configuration"]
            }
    
    def _generate_network_capacity_recommendations(self, avg_bandwidth: float, avg_data_transfer: float) -> List[str]:
        """Generate network capacity planning recommendations"""
        
        recommendations = []
        
        if avg_data_transfer > 10000:  # 10TB per month
            recommendations.append("High data transfer volume - consider VPC endpoints to reduce costs")
            recommendations.append("Implement data compression and caching strategies")
        
        if avg_bandwidth > 0.7:
            recommendations.append("High bandwidth utilization - monitor for potential bottlenecks")
            recommendations.append("Consider upgrading instance types for network-intensive workloads")
        
        if avg_data_transfer > 1000:
            recommendations.append("Implement CloudWatch monitoring for network performance metrics")
            recommendations.append("Consider AWS Transit Gateway for complex inter-VPC communication")
        
        recommendations.append("Regularly review and optimize security group rules")
        recommendations.append("Implement VPC Flow Logs for traffic analysis and optimization")
        
        return recommendations
    
    def generate_vpc_security_audit(self, vpc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive VPC security audit
        """
        
        audit_result = {
            "vpc_id": vpc_data.get("vpc_id"),
            "audit_timestamp": datetime.now().isoformat(),
            "overall_security_score": 0.0,
            "security_findings": [],
            "compliance_status": {},
            "remediation_priority": "medium",
            "recommendations": []
        }
        
        # Security group audit
        sg_findings = self._audit_security_groups(vpc_data.get("security_groups", []))
        audit_result["security_findings"].extend(sg_findings)
        
        # Network ACL audit (if available)
        # Subnet security audit
        subnet_findings = self._audit_subnet_security(vpc_data.get("subnets", []))
        audit_result["security_findings"].extend(subnet_findings)
        
        # Flow logs audit
        flow_logs_findings = self._audit_flow_logs(vpc_data.get("flow_logs", {}))
        audit_result["security_findings"].extend(flow_logs_findings)
        
        # Calculate overall security score
        audit_result["overall_security_score"] = self._calculate_security_score(audit_result["security_findings"])
        
        # Determine remediation priority
        if audit_result["overall_security_score"] < 50:
            audit_result["remediation_priority"] = "critical"
        elif audit_result["overall_security_score"] < 75:
            audit_result["remediation_priority"] = "high"
        
        # Generate recommendations
        audit_result["recommendations"] = self._generate_security_recommendations(audit_result["security_findings"])
        
        return audit_result
    
    def _audit_security_groups(self, security_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audit security group configurations"""
        
        findings = []
        
        for sg in security_groups:
            sg_name = sg.get("group_name", "Unknown")
            
            # Check for overly permissive inbound rules
            for rule in sg.get("ingress_rules", []):
                if rule.get("source") == "0.0.0.0/0":
                    if rule.get("protocol") == "all":
                        findings.append({
                            "severity": "critical",
                            "category": "security_group",
                            "resource": sg_name,
                            "finding": "Security group allows all inbound traffic from anywhere",
                            "recommendation": "Restrict inbound rules to specific protocols and sources"
                        })
                    elif rule.get("port_range") not in ["80-80", "443-443"]:
                        findings.append({
                            "severity": "high",
                            "category": "security_group",
                            "resource": sg_name,
                            "finding": f"Non-standard port {rule.get('port_range')} open to public",
                            "recommendation": "Restrict public access to standard web ports only"
                        })
            
            # Check rule count
            total_rules = len(sg.get("ingress_rules", [])) + len(sg.get("egress_rules", []))
            if total_rules > 50:
                findings.append({
                    "severity": "medium",
                    "category": "security_group",
                    "resource": sg_name,
                    "finding": "Security group has excessive number of rules",
                    "recommendation": "Consider consolidating rules or splitting into multiple security groups"
                })
        
        return findings
    
    def _audit_subnet_security(self, subnets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audit subnet security configurations"""
        
        findings = []
        
        public_subnets = [s for s in subnets if s.get("subnet_type") == "public"]
        private_subnets = [s for s in subnets if s.get("subnet_type") == "private"]
        
        # Check for auto-assign public IP on private subnets
        for subnet in private_subnets:
            if subnet.get("auto_assign_public_ip", False):
                findings.append({
                    "severity": "high",
                    "category": "subnet",
                    "resource": subnet.get("subnet_id"),
                    "finding": "Private subnet has auto-assign public IP enabled",
                    "recommendation": "Disable auto-assign public IP for private subnets"
                })
        
        # Check for lack of private subnets
        if len(public_subnets) > 0 and len(private_subnets) == 0:
            findings.append({
                "severity": "medium",
                "category": "architecture",
                "resource": "VPC",
                "finding": "VPC lacks private subnets for internal resources",
                "recommendation": "Implement private subnets for better security isolation"
            })
        
        return findings
    
    def _audit_flow_logs(self, flow_logs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit VPC Flow Logs configuration"""
        
        findings = []
        
        if not flow_logs.get("enabled", False):
            findings.append({
                "severity": "high",
                "category": "monitoring",
                "resource": "VPC",
                "finding": "VPC Flow Logs are not enabled",
                "recommendation": "Enable VPC Flow Logs for network monitoring and security analysis"
            })
        
        return findings
    
    def _calculate_security_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall security score based on findings"""
        
        base_score = 100.0
        
        for finding in findings:
            severity = finding.get("severity", "low")
            
            if severity == "critical":
                base_score -= 25
            elif severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5
        
        return max(0.0, base_score)
    
    def _generate_security_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings"""
        
        recommendations = []
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        # Generate category-specific recommendations
        if "security_group" in categories:
            recommendations.append("Review and tighten security group rules")
            recommendations.append("Implement least privilege access principles")
        
        if "subnet" in categories:
            recommendations.append("Review subnet security configurations")
            recommendations.append("Ensure proper tier isolation")
        
        if "monitoring" in categories:
            recommendations.append("Enable comprehensive network monitoring")
            recommendations.append("Implement automated security alerting")
        
        # General recommendations
        recommendations.append("Conduct regular security audits")
        recommendations.append("Implement Infrastructure as Code for consistent security")
        
        return recommendations