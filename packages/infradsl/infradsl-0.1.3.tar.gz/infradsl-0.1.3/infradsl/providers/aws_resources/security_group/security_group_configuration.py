from typing import Dict, Any, List, Union

class SecurityGroupConfigurationMixin:
    """
    Mixin for SecurityGroup chainable configuration methods.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize configuration-specific attributes if not already set
        if not hasattr(self, 'ingress_rules'):
            self.ingress_rules = []
        if not hasattr(self, 'egress_rules'):
            self.egress_rules = []
        if not hasattr(self, 'tags'):
            self.tags = {}
    
    def description(self, description: str):
        """Set the security group description"""
        self.group_description = description
        return self

    def vpc(self, vpc_id: str):
        """Set the VPC ID for the security group"""
        self.vpc_id = vpc_id
        return self

    def ingress(self, port: Union[int, str], source: str = "0.0.0.0/0", protocol: str = "tcp", description: str = None):
        """Add an ingress rule to the security group"""
        rule = {
            "port": port,
            "source": source,
            "protocol": protocol.lower(),
            "description": description or f"Allow {protocol.upper()} on port {port}"
        }
        self.ingress_rules.append(rule)
        return self

    def egress(self, port: Union[int, str], destination: str = "0.0.0.0/0", protocol: str = "tcp", description: str = None):
        """Add an egress rule to the security group"""
        rule = {
            "port": port,
            "destination": destination,
            "protocol": protocol.lower(),
            "description": description or f"Allow {protocol.upper()} to port {port}"
        }
        self.egress_rules.append(rule)
        return self
    
    # Common port shortcuts for ingress
    def allow_ssh(self, source: str = "0.0.0.0/0"):
        """Allow SSH access (port 22)"""
        return self.ingress(22, source, "tcp", "SSH access")
    
    def allow_http(self, source: str = "0.0.0.0/0"):
        """Allow HTTP access (port 80)"""
        return self.ingress(80, source, "tcp", "HTTP access")
    
    def allow_https(self, source: str = "0.0.0.0/0"):
        """Allow HTTPS access (port 443)"""
        return self.ingress(443, source, "tcp", "HTTPS access")
    
    def allow_web(self, source: str = "0.0.0.0/0"):
        """Allow both HTTP and HTTPS access"""
        return self.allow_http(source).allow_https(source)
    
    def allow_mysql(self, source: str = "0.0.0.0/0"):
        """Allow MySQL access (port 3306)"""
        return self.ingress(3306, source, "tcp", "MySQL database access")
    
    def allow_postgres(self, source: str = "0.0.0.0/0"):
        """Allow PostgreSQL access (port 5432)"""
        return self.ingress(5432, source, "tcp", "PostgreSQL database access")
    
    def allow_redis(self, source: str = "0.0.0.0/0"):
        """Allow Redis access (port 6379)"""
        return self.ingress(6379, source, "tcp", "Redis cache access")
    
    def allow_smtp(self, source: str = "0.0.0.0/0"):
        """Allow SMTP access (port 25)"""
        return self.ingress(25, source, "tcp", "SMTP mail access")
    
    def allow_smtp_secure(self, source: str = "0.0.0.0/0"):
        """Allow secure SMTP access (port 587)"""
        return self.ingress(587, source, "tcp", "Secure SMTP access")
    
    def allow_ftp(self, source: str = "0.0.0.0/0"):
        """Allow FTP access (port 21)"""
        return self.ingress(21, source, "tcp", "FTP access")
    
    def allow_rdp(self, source: str = "0.0.0.0/0"):
        """Allow RDP access (port 3389)"""
        return self.ingress(3389, source, "tcp", "RDP access")
    
    def allow_dns(self, source: str = "0.0.0.0/0"):
        """Allow DNS access (port 53)"""
        return self.ingress(53, source, "udp", "DNS queries")
    
    def allow_ntp(self, source: str = "0.0.0.0/0"):
        """Allow NTP access (port 123)"""
        return self.ingress(123, source, "udp", "NTP time sync")
    
    def allow_ping(self, source: str = "0.0.0.0/0"):
        """Allow ICMP ping"""
        return self.ingress("icmp", source, "icmp", "ICMP ping")
    
    def allow_port_range(self, from_port: int, to_port: int, source: str = "0.0.0.0/0", protocol: str = "tcp"):
        """Allow a range of ports"""
        port_range = f"{from_port}-{to_port}"
        return self.ingress(port_range, source, protocol, f"Port range {port_range}")
    
    def allow_all_tcp(self, source: str = "0.0.0.0/0"):
        """Allow all TCP traffic"""
        return self.ingress("0-65535", source, "tcp", "All TCP traffic")
    
    def allow_all_udp(self, source: str = "0.0.0.0/0"):
        """Allow all UDP traffic"""
        return self.ingress("0-65535", source, "udp", "All UDP traffic")
    
    def allow_security_group(self, security_group_id: str, port: Union[int, str] = "all", protocol: str = "tcp"):
        """Allow traffic from another security group"""
        return self.ingress(port, security_group_id, protocol, f"Access from security group {security_group_id}")
    
    def allow_load_balancer(self, load_balancer_sg: str):
        """Allow traffic from load balancer security group"""
        return self.allow_security_group(load_balancer_sg, 80, "tcp").allow_security_group(load_balancer_sg, 443, "tcp")
    
    # Egress shortcuts
    def allow_outbound_web(self):
        """Allow outbound HTTP and HTTPS"""
        return self.egress(80, "0.0.0.0/0", "tcp", "Outbound HTTP").egress(443, "0.0.0.0/0", "tcp", "Outbound HTTPS")
    
    def allow_outbound_dns(self):
        """Allow outbound DNS"""
        return self.egress(53, "0.0.0.0/0", "udp", "Outbound DNS").egress(53, "0.0.0.0/0", "tcp", "Outbound DNS TCP")
    
    def allow_all_outbound(self):
        """Allow all outbound traffic (default AWS behavior)"""
        return self.egress("0-65535", "0.0.0.0/0", "tcp", "All outbound TCP").egress("0-65535", "0.0.0.0/0", "udp", "All outbound UDP")
    
    def deny_all_outbound(self):
        """Remove all outbound rules (deny all)"""
        self.egress_rules = []
        return self
    
    # Preset configurations
    def web_server(self, admin_source: str = "0.0.0.0/0"):
        """Standard web server configuration"""
        return self.allow_web().allow_ssh(admin_source).allow_outbound_web().allow_outbound_dns()
    
    def database_server(self, app_security_group: str, admin_source: str = "10.0.0.0/8"):
        """Standard database server configuration"""
        return self.allow_security_group(app_security_group, 3306).allow_ssh(admin_source).allow_outbound_dns()
    
    def load_balancer(self):
        """Standard load balancer configuration"""
        return self.allow_web().allow_outbound_web()
    
    def app_server(self, lb_security_group: str, admin_source: str = "10.0.0.0/8"):
        """Standard application server configuration"""
        return self.allow_security_group(lb_security_group, 8080).allow_ssh(admin_source).allow_outbound_web().allow_outbound_dns()
    
    def tag(self, key: str, value: str):
        """Add a tag to the security group"""
        self.tags[key] = value
        return self
    
    def tags_dict(self, tags_dict: Dict[str, str]):
        """Add multiple tags to the security group"""
        self.tags.update(tags_dict)
        return self