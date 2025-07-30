"""
EC2 Configuration Module

This module contains all the chainable configuration methods for EC2 instances.
It provides Rails-like fluent interface for configuring instance types, AMIs,
security, networking, and other EC2 settings.
"""

from typing import Dict, Any, List, Optional
import os


class EC2ConfigurationMixin:
    """
    Mixin class providing EC2 configuration capabilities.
    
    This class contains chainable methods for:
    - Instance type configuration
    - AMI selection and auto-detection
    - Security group and firewall rules
    - Network and storage configuration
    - Tags and metadata
    """

    # Instance Type Configuration
    def instance(self, instance_type: str):
        """Set the instance type (e.g., 't3.micro', 't3.small', 't3.medium')"""
        self.instance_type = instance_type
        return self

    def t3_micro(self):
        """Set instance type to t3.micro (1 vCPU, 1 GB RAM) - Free tier eligible"""
        return self.instance('t3.micro')

    def t3_small(self):
        """Set instance type to t3.small (2 vCPU, 2 GB RAM)"""
        return self.instance('t3.small')

    def t3_medium(self):
        """Set instance type to t3.medium (2 vCPU, 4 GB RAM)"""
        return self.instance('t3.medium')

    def t3_large(self):
        """Set instance type to t3.large (2 vCPU, 8 GB RAM)"""
        return self.instance('t3.large')

    def c5_large(self):
        """Set instance type to c5.large (2 vCPU, 4 GB RAM) - Compute optimized"""
        return self.instance('c5.large')

    def r5_large(self):
        """Set instance type to r5.large (2 vCPU, 16 GB RAM) - Memory optimized"""
        return self.instance('r5.large')

    def cpu(self, cores: int):
        """Set CPU cores - maps to appropriate AWS instance type
        
        Args:
            cores: Number of CPU cores (1, 2, 4, 8, 16, 32, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps CPU cores to AWS instance types automatically:
            - 1 core -> t3.micro (1 vCPU, 1GB RAM)
            - 2 cores -> t3.small (2 vCPUs, 2GB RAM)
            - 4 cores -> t3.medium (2 vCPUs, 4GB RAM) or t3.large (2 vCPUs, 8GB RAM)
            - 8+ cores -> t3.xlarge or larger instances
        """
        if cores < 1:
            raise ValueError("CPU cores must be at least 1")
            
        # AWS instance type mapping based on CPU cores
        instance_type_map = {
            1: "t3.micro",        # 1 vCPU, 1GB RAM
            2: "t3.small",        # 2 vCPUs, 2GB RAM
            4: "t3.medium",       # 2 vCPUs, 4GB RAM (AWS t3.medium has 2 vCPUs but good for 4-core workloads)
            8: "t3.large",        # 2 vCPUs, 8GB RAM
            16: "t3.xlarge",      # 4 vCPUs, 16GB RAM
            32: "t3.2xlarge",     # 8 vCPUs, 32GB RAM
            64: "m5.4xlarge",     # 16 vCPUs, 64GB RAM
        }
        
        if cores in instance_type_map:
            instance_type = instance_type_map[cores]
            print(f"🔧 Setting CPU cores: {cores} → instance type: {instance_type}")
        else:
            # For non-standard core counts, use closest match
            if cores <= 1:
                instance_type = "t3.micro"
            elif cores <= 2:
                instance_type = "t3.small"
            elif cores <= 4:
                instance_type = "t3.medium"
            elif cores <= 8:
                instance_type = "t3.large"
            elif cores <= 16:
                instance_type = "t3.xlarge"
            elif cores <= 32:
                instance_type = "t3.2xlarge"
            else:
                # For very high core counts, use compute optimized
                instance_type = "c5.4xlarge"  # 16 vCPUs, 32GB RAM
            print(f"🔧 Setting CPU cores: {cores} → closest instance type: {instance_type}")
        
        self.instance_type = instance_type
        return self

    def ram(self, gb: int):
        """Set RAM in GB - maps to appropriate AWS instance type
        
        Args:
            gb: RAM in gigabytes (1, 2, 4, 8, 16, 32, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps RAM to AWS instance types automatically:
            - 1GB -> t3.micro
            - 2GB -> t3.small
            - 4GB -> t3.medium
            - 8GB+ -> t3.large or larger
        """
        if gb < 1:
            raise ValueError("RAM must be at least 1 GB")
            
        # AWS instance type mapping based on RAM
        if gb <= 1:
            instance_type = "t3.micro"        # 1 vCPU, 1GB RAM
        elif gb <= 2:
            instance_type = "t3.small"        # 2 vCPUs, 2GB RAM
        elif gb <= 4:
            instance_type = "t3.medium"       # 2 vCPUs, 4GB RAM
        elif gb <= 8:
            instance_type = "t3.large"        # 2 vCPUs, 8GB RAM
        elif gb <= 16:
            instance_type = "t3.xlarge"       # 4 vCPUs, 16GB RAM
        elif gb <= 32:
            instance_type = "t3.2xlarge"      # 8 vCPUs, 32GB RAM
        elif gb <= 64:
            instance_type = "r5.xlarge"       # 4 vCPUs, 32GB RAM (memory optimized)
        elif gb <= 128:
            instance_type = "r5.2xlarge"      # 8 vCPUs, 64GB RAM
        else:
            # For large RAM requirements, use memory-optimized instances
            instance_type = "r5.4xlarge"      # 16 vCPUs, 128GB RAM
            print(f"🔧 Setting RAM: {gb}GB → memory-optimized instance: {instance_type}")
        
        if not instance_type.startswith("r5.4"):
            print(f"🔧 Setting RAM: {gb}GB → instance type: {instance_type}")
        
        self.instance_type = instance_type
        return self

    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
            
        Note:
            This integrates with InfraDSL's revolutionary Cross-Cloud Magic system
            to automatically select the optimal cloud provider and configuration.
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        # Store optimization preference for later use
        self._optimization_priority = priority
        
        print(f"🎯 Cross-Cloud Magic: Optimizing for {priority}")
        
        # Integrate with Cross-Cloud Intelligence
        try:
            from ....core.cross_cloud_intelligence import cross_cloud_intelligence, ServiceRequirements, ServiceCategory
            
            # Extract CPU/RAM from current instance type
            cpu_count = self._extract_cpu_from_instance_type(self.instance_type)
            ram_gb = self._extract_ram_from_instance_type(self.instance_type)
            
            # Create service requirements
            requirements = ServiceRequirements(
                service_category=ServiceCategory.COMPUTE,
                service_type="web-servers",  # Default to web servers
                performance_tier="standard",
                reliability_requirement="high",
                cost_sensitivity=1.0 if priority == "cost" else 0.3,
                performance_sensitivity=1.0 if priority == "performance" else 0.3,
                reliability_sensitivity=1.0 if priority == "reliability" else 0.3,
                compliance_sensitivity=1.0 if priority == "compliance" else 0.3
            )
            
            # Get Cross-Cloud recommendation
            recommendation = cross_cloud_intelligence.select_optimal_provider(requirements)
            
            # Show recommendation to user
            if recommendation.recommended_provider != "aws":
                print(f"💡 Cross-Cloud Magic suggests {recommendation.recommended_provider.upper()} for {priority} optimization")
                print(f"   💰 Potential monthly savings: ${recommendation.estimated_monthly_cost:.2f}")
                print(f"   📊 Confidence: {recommendation.confidence_score:.1%}")
                print(f"   📝 Consider switching providers for optimal {priority}")
            else:
                print(f"✅ AWS is optimal for {priority} optimization")
                
        except ImportError:
            print("⚠️  Cross-Cloud Magic not available - using provider-specific optimizations")
        except Exception as e:
            print(f"⚠️  Cross-Cloud Magic error: {e} - using provider-specific optimizations")
        
        # Apply AWS-specific optimizations based on priority
        if priority == "cost":
            print("💰 Cost optimization: Selecting cost-effective instance types")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Selecting high-performance instance types")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Selecting reliable instance configurations")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Selecting compliant configurations")
            self._apply_compliance_optimizations()
        
        return self
    
    def _extract_cpu_from_instance_type(self, instance_type: str) -> int:
        """Extract CPU count from AWS instance type"""
        # AWS instance type mapping (approximate vCPUs)
        cpu_map = {
            "t3.micro": 2,     # Burstable, but 2 vCPUs
            "t3.small": 2,     # 2 vCPUs
            "t3.medium": 2,    # 2 vCPUs
            "t3.large": 2,     # 2 vCPUs
            "t3.xlarge": 4,    # 4 vCPUs
            "t3.2xlarge": 8,   # 8 vCPUs
            "c5.large": 2,     # 2 vCPUs
            "c5.xlarge": 4,    # 4 vCPUs
            "c5.2xlarge": 8,   # 8 vCPUs
            "r5.large": 2,     # 2 vCPUs
            "r5.xlarge": 4,    # 4 vCPUs
            "r5.2xlarge": 8,   # 8 vCPUs
            "m5.large": 2,     # 2 vCPUs
            "m5.xlarge": 4,    # 4 vCPUs
        }
        return cpu_map.get(instance_type, 2)  # Default to 2 vCPUs
    
    def _extract_ram_from_instance_type(self, instance_type: str) -> int:
        """Extract RAM in GB from AWS instance type"""
        # AWS instance type RAM mapping
        ram_map = {
            "t3.micro": 1,      # 1 GB
            "t3.small": 2,      # 2 GB
            "t3.medium": 4,     # 4 GB
            "t3.large": 8,      # 8 GB
            "t3.xlarge": 16,    # 16 GB
            "t3.2xlarge": 32,   # 32 GB
            "c5.large": 4,      # 4 GB
            "c5.xlarge": 8,     # 8 GB
            "c5.2xlarge": 16,   # 16 GB
            "r5.large": 16,     # 16 GB
            "r5.xlarge": 32,    # 32 GB
            "r5.2xlarge": 64,   # 64 GB
            "m5.large": 8,      # 8 GB
            "m5.xlarge": 16,    # 16 GB
        }
        return ram_map.get(instance_type, 4)  # Default to 4 GB
    
    def _apply_cost_optimizations(self):
        """Apply AWS-specific cost optimizations"""
        # Use burstable instances for cost savings
        if "c5." in self.instance_type or "r5." in self.instance_type:
            # Switch to t3 equivalent for cost savings
            if "large" in self.instance_type:
                self.instance_type = "t3.large"
                print(f"   💰 Switched to cost-effective: {self.instance_type}")
        
        # Suggest spot instances for cost savings (metadata)
        if not hasattr(self, 'instance_tags'):
            self.instance_tags = {}
        self.instance_tags["cost-optimized"] = "true"
        self.instance_tags["spot-suggested"] = "true"
    
    def _apply_performance_optimizations(self):
        """Apply AWS-specific performance optimizations"""
        # Switch to compute-optimized if using general purpose
        if "t3." in self.instance_type:
            # Suggest c5 for better CPU performance
            if "large" in self.instance_type:
                suggested_type = self.instance_type.replace("t3.", "c5.")
                print(f"   🚀 Performance suggestion: upgrade to {suggested_type}")
                # Could actually switch here
                
        # Enable EBS optimization for better I/O
        self.ebs_optimized = True
        print(f"   💿 Enabled EBS optimization for better I/O performance")
        
        # Add performance optimization metadata
        if not hasattr(self, 'instance_tags'):
            self.instance_tags = {}
        self.instance_tags["performance-optimized"] = "true"
        self.instance_tags["ebs-optimized"] = "true"
    
    def _apply_reliability_optimizations(self):
        """Apply AWS-specific reliability optimizations"""
        # Enable detailed monitoring for reliability
        self.monitoring_enabled = True
        print(f"   🛡️ Enabled detailed CloudWatch monitoring")
        
        # Increase root volume size for reliability
        if self.root_volume_size < 20:
            self.root_volume_size = 20
            print(f"   💿 Increased root volume to {self.root_volume_size}GB for reliability")
        
        # Add reliability optimization metadata
        if not hasattr(self, 'instance_tags'):
            self.instance_tags = {}
        self.instance_tags["reliability-optimized"] = "true"
        self.instance_tags["monitoring-enabled"] = "true"
    
    def _apply_compliance_optimizations(self):
        """Apply AWS-specific compliance optimizations"""
        # Enable termination protection
        self.termination_protection = True
        print(f"   📋 Enabled termination protection for compliance")
        
        # Add compliance optimization metadata
        if not hasattr(self, 'instance_tags'):
            self.instance_tags = {}
        self.instance_tags["compliance-optimized"] = "true"
        self.instance_tags["termination-protected"] = "true"
        self.instance_tags["encryption-recommended"] = "true"

    # AMI Configuration
    def ami(self, ami_id: str):
        """Set the AMI ID manually"""
        self.ami_id = ami_id
        return self

    def ubuntu(self, version: str = '22.04'):
        """Use Ubuntu AMI (auto-detects latest)"""
        # AMI will be auto-detected in _auto_detect_ami
        return self

    def amazon_linux(self, version: str = '2'):
        """Use Amazon Linux AMI (auto-detects latest)"""
        # AMI will be auto-detected in _auto_detect_ami
        return self

    # Key Pair and Security
    def key_pair(self, key_name: str):
        """Set SSH key pair for instance access"""
        self.key_name = key_name
        return self

    def security_group(self, group_id: str):
        """Add a security group"""
        if group_id not in self.security_groups:
            self.security_groups.append(group_id)
        return self

    def security_groups(self, group_ids: List[str]):
        """Set multiple security groups"""
        self.security_groups = group_ids
        return self

    # Firewall and Port Configuration
    def allow_ssh(self, from_cidr: str = "0.0.0.0/0"):
        """Allow SSH access (port 22) - automatically configures security group"""
        self._ensure_security_rule("ssh", 22, "tcp", from_cidr)
        return self

    def allow_http(self, from_cidr: str = "0.0.0.0/0"):
        """Allow HTTP access (port 80) - automatically configures security group"""
        self._ensure_security_rule("http", 80, "tcp", from_cidr)
        return self

    def allow_https(self, from_cidr: str = "0.0.0.0/0"):
        """Allow HTTPS access (port 443) - automatically configures security group"""
        self._ensure_security_rule("https", 443, "tcp", from_cidr)
        return self

    def allow_port(self, port: int, protocol: str = "tcp", from_cidr: str = "0.0.0.0/0", name: str = None):
        """Allow access to a specific port - automatically configures security group"""
        rule_name = name or f"port-{port}"
        self._ensure_security_rule(rule_name, port, protocol, from_cidr)
        return self

    def ssh(self, enabled: bool = True, from_cidr: str = "0.0.0.0/0"):
        """Enable or disable SSH access (port 22) - Rails-like method matching GCP/DO"""
        if enabled:
            self._ensure_security_rule("ssh", 22, "tcp", from_cidr)
            print(f"🔑 SSH access enabled from {from_cidr}")
        else:
            self._remove_security_rule("ssh", 22, "tcp")
            print("🔒 SSH access disabled (rule will be removed)")
        return self

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_ranges: Optional[List[str]] = None):
        """Add firewall rule - Rails-like method matching GCP/DO pattern"""
        if source_ranges is None:
            source_ranges = ["0.0.0.0/0"]

        for source_range in source_ranges:
            self._ensure_security_rule(name, port, protocol, source_range)

        print(f"🛡️  Firewall rule '{name}' configured: {protocol.upper()} port {port}")
        return self

    # Network Configuration
    def subnet(self, subnet_id: str):
        """Set subnet for the instance"""
        self.subnet_id = subnet_id
        return self

    def public_ip_address(self, enabled: bool = True):
        """Enable or disable public IP association"""
        self.associate_public_ip = enabled
        return self

    def public_ip(self):
        """Enable public IP association (convenience method)"""
        return self.public_ip_address(True)

    def private_ip(self):
        """Disable public IP association (convenience method)"""
        return self.public_ip_address(False)

    # Storage Configuration
    def disk_size(self, size_gb: int):
        """Set root volume size in GB"""
        if size_gb < 8:
            print("⚠️  Warning: Minimum disk size is 8 GB for most AMIs")
            size_gb = 8
        self.root_volume_size = size_gb
        return self

    def disk_type(self, volume_type: str):
        """Set root volume type (gp3, gp2, io1, io2)"""
        valid_types = ['gp3', 'gp2', 'io1', 'io2', 'st1', 'sc1']
        if volume_type not in valid_types:
            raise ValueError(f"Invalid volume type. Must be one of: {valid_types}")
        self.root_volume_type = volume_type
        return self

    # Instance Configuration
    def monitoring(self, enabled: bool = True):
        """Enable or disable detailed monitoring"""
        self.monitoring_enabled = enabled
        return self

    def cloudwatch_monitoring(self, enabled: bool = True):
        """Enable or disable CloudWatch monitoring"""
        self.cloudwatch_monitoring_enabled = enabled
        return self

    def log_group(self, log_group_name: str):
        """Set the CloudWatch log group for the instance"""
        self.log_group_name = log_group_name
        return self

    def enable_security_scanning(self, vulnerability_scanning: bool = False, compliance_checks: Optional[List[str]] = None, scan_frequency: str = "daily"):
        """Enable security scanning for the instance"""
        self.security_scanning_enabled = True
        self.vulnerability_scanning = vulnerability_scanning
        self.compliance_checks = compliance_checks if compliance_checks is not None else []
        self.scan_frequency = scan_frequency
        return self

    def ebs_optimized(self, enabled: bool = True):
        """Enable or disable EBS optimization"""
        self.ebs_optimized = enabled
        return self

    def termination_protection(self, enabled: bool = True):
        """Enable or disable termination protection"""
        self.termination_protection = enabled
        return self

    # User Data and Scripts
    def user_data(self, script: str):
        """Set user data script for instance initialization"""
        self.user_data = script
        return self

    def user_data_file(self, file_path: str):
        """Load user data script from file"""
        try:
            with open(file_path, 'r') as f:
                self.user_data = f.read()
            print(f"📄 Loaded user data from: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to load user data file {file_path}: {str(e)}")
        return self

    # Tagging and Metadata
    def tags(self, tags: Dict[str, str]):
        """Set multiple tags"""
        self.instance_tags.update(tags)
        return self

    def tag(self, key: str, value: str):
        """Set a single tag"""
        self.instance_tags[key] = value
        return self

    def region(self, region: str):
        """Set AWS region (for multi-region deployments)"""
        # This would typically require reinitializing clients
        print(f"🌍 Note: Region set to {region}. You may need to reinitialize for this to take effect.")
        return self

    # Service Integration
    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None):
        """Install and configure a service using the service manager"""
        if not hasattr(self, 'service_manager') or not self.service_manager:
            print("⚠️  Service manager not available. Ensure instance is authenticated.")
            return self

        if variables is None:
            variables = {}

        try:
            # Generate service installation script
            service_script = self.service_manager.generate_service_script(service_name, variables)
            
            if service_script:
                # Append to existing user data or create new
                if self.user_data:
                    self.user_data += f"\n\n# Service: {service_name}\n{service_script}"
                else:
                    self.user_data = f"#!/bin/bash\n\n# Service: {service_name}\n{service_script}"
                
                print(f"🔧 Service '{service_name}' configured for installation")
            else:
                print(f"⚠️  Unknown service: {service_name}")
        except Exception as e:
            print(f"⚠️  Failed to configure service {service_name}: {str(e)}")
        
        return self

    # Utility Methods
    def add_security_group(self, security_group_id: str):
        """Add security group to the instance"""
        if security_group_id not in self.security_groups:
            self.security_groups.append(security_group_id)
        return self

    def set_user_data_file(self, file_path: str):
        """Set user data from file (alias for user_data_file)"""
        return self.user_data_file(file_path)

    def generate_ssh_command(self) -> str:
        """Generate SSH command for connecting to the instance"""
        if not self.public_ip and not self.private_ip:
            return "Instance has no IP address assigned"
        
        if not self.key_name:
            return "No key pair configured for SSH access"
        
        ip_address = self.public_ip or self.private_ip
        return f"ssh -i {self.key_name}.pem ubuntu@{ip_address}"

    # Security Rule Management (Private Methods)
    def _ensure_security_rule(self, name: str, port: int, protocol: str, from_cidr: str):
        """Ensure security group rule exists for the specified port"""
        if not hasattr(self, '_pending_security_rules'):
            self._pending_security_rules = []

        rule = {
            'name': name,
            'port': port,
            'protocol': protocol,
            'from_cidr': from_cidr,
            'action': 'add'
        }

        # Avoid duplicates
        if rule not in self._pending_security_rules:
            self._pending_security_rules.append(rule)
            print(f"📋 Queued security rule: {protocol.upper()} port {port} from {from_cidr}")

    def _remove_security_rule(self, name: str, port: int, protocol: str):
        """Remove security group rule for the specified port"""
        if not hasattr(self, '_pending_security_rules'):
            self._pending_security_rules = []

        rule = {
            'name': name,
            'port': port,
            'protocol': protocol,
            'from_cidr': '0.0.0.0/0',  # Default CIDR for removal
            'action': 'remove'
        }

        self._pending_security_rules.append(rule)
        print(f"🗑️  Queued security rule removal: {protocol.upper()} port {port}")

    def _apply_security_rules(self):
        """Apply pending security rules to the security group"""
        if not hasattr(self, '_pending_security_rules') or not self._pending_security_rules:
            return

        if not self.security_groups:
            print("⚠️  No security group specified. Security rules will not be applied.")
            return

        try:
            # Get the first security group (primary)
            sg_id = self.security_groups[0]

            for rule in self._pending_security_rules:
                try:
                    # Get current security group state
                    response = self.ec2_client.describe_security_groups(GroupIds=[sg_id])
                    sg = response['SecurityGroups'][0]

                    if rule['action'] == 'add':
                        # Check if rule already exists
                        rule_exists = any(
                            perm.get('FromPort') == rule['port'] and
                            perm.get('ToPort') == rule['port'] and
                            perm.get('IpProtocol') == rule['protocol'] and
                            any(ip_range['CidrIp'] == rule['from_cidr'] for ip_range in perm.get('IpRanges', []))
                            for perm in sg['IpPermissions']
                        )

                        if rule_exists:
                            print(f"✅ Security rule already exists: {rule['protocol'].upper()} port {rule['port']}")
                            continue

                        # Add the rule
                        self.ec2_client.authorize_security_group_ingress(
                            GroupId=sg_id,
                            IpPermissions=[{
                                'IpProtocol': rule['protocol'],
                                'FromPort': rule['port'],
                                'ToPort': rule['port'],
                                'IpRanges': [{'CidrIp': rule['from_cidr']}]
                            }]
                        )
                        print(f"✅ Added security rule: {rule['protocol'].upper()} port {rule['port']} from {rule['from_cidr']}")

                    elif rule['action'] == 'remove':
                        # Find and remove all rules for this port/protocol
                        rules_to_remove = []
                        for perm in sg['IpPermissions']:
                            if (perm.get('FromPort') == rule['port'] and
                                perm.get('ToPort') == rule['port'] and
                                perm.get('IpProtocol') == rule['protocol']):
                                rules_to_remove.append(perm)

                        if rules_to_remove:
                            for rule_to_remove in rules_to_remove:
                                self.ec2_client.revoke_security_group_ingress(
                                    GroupId=sg_id,
                                    IpPermissions=[rule_to_remove]
                                )
                                print(f"🗑️  Removed security rule: {rule['protocol'].upper()} port {rule['port']}")
                        else:
                            print(f"ℹ️  Security rule not found (already removed): {rule['protocol'].upper()} port {rule['port']}")

                except Exception as e:
                    action_word = "add" if rule['action'] == 'add' else "remove"
                    print(f"⚠️  Failed to {action_word} security rule for port {rule['port']}: {str(e)}")

        except Exception as e:
            print(f"⚠️  Failed to apply security rules: {str(e)}")

        # Clear pending rules after processing
        self._pending_security_rules = []

    # Nexus Intelligence Methods (for Universal Intelligence Mixin)
    def compliance_checks(self, standards: List[str]):
        """Enable compliance checking for specified standards (CIS, SOC2, HIPAA, PCI)"""
        self._compliance_standards = standards
        if standards:
            print(f"📋 Compliance checks enabled: {', '.join(standards)}")
        return self

    def nexus_networking(self):
        """Enable Nexus intelligent networking optimization"""
        self._nexus_networking_enabled = True
        print("🌐 Nexus networking enabled: Intelligent network optimization and routing")
        return self