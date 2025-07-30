class LoadBalancerConfigurationMixin:
    """
    Mixin for LoadBalancer chainable configuration methods.
    """
    def lb_type(self, lb_type: str):
        """Set the load balancer type (application, network, gateway)"""
        self.load_balancer_type = lb_type
        return self

    def application(self):
        """Configure as Application Load Balancer"""
        self.load_balancer_type = "application"
        return self

    def network(self):
        """Configure as Network Load Balancer"""
        self.load_balancer_type = "network"
        return self

    def gateway(self):
        """Configure as Gateway Load Balancer"""
        self.load_balancer_type = "gateway"
        return self

    def scheme(self, scheme: str):
        """Set the load balancer scheme (internet-facing, internal)"""
        self.lb_scheme = scheme
        return self

    def internet_facing(self):
        """Configure as internet-facing load balancer"""
        self.lb_scheme = "internet-facing"
        return self

    def internal(self):
        """Configure as internal load balancer"""
        self.lb_scheme = "internal"
        return self

    def ip_address_type(self, ip_type: str):
        """Set the IP address type (ipv4, dualstack)"""
        self.ip_address_type = ip_type
        return self

    def ipv4(self):
        """Configure for IPv4 only"""
        self.ip_address_type = "ipv4"
        return self

    def dualstack(self):
        """Configure for IPv4 and IPv6"""
        self.ip_address_type = "dualstack"
        return self

    def vpc(self, vpc_id: str):
        """Set the VPC ID"""
        self.vpc_id = vpc_id
        return self

    def in_subnets(self, subnet_ids: list):
        """Set the subnet IDs"""
        self.subnets = subnet_ids
        return self

    def with_security_groups(self, security_group_ids: list):
        """Set the security group IDs"""
        self.security_groups = security_group_ids
        return self

    def target_group(self, name: str, port: int, protocol: str = 'HTTP'):
        """Add a target group"""
        target_group = {
            'name': name,
            'port': port,
            'protocol': protocol
        }
        self.target_groups.append(target_group)
        return self

    def listener(self, port: int, protocol: str = 'HTTP', default_action: str = 'forward'):
        """Add a listener"""
        listener = {
            'port': port,
            'protocol': protocol,
            'default_action': default_action
        }
        self.listeners.append(listener)
        return self

    def health_check(self, path: str = '/', port: int = None, protocol: str = 'HTTP'):
        """Configure health check settings"""
        health_check = {
            'path': path,
            'port': port,
            'protocol': protocol
        }
        self.health_checks.append(health_check)
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the load balancer"""
        self.tags[key] = value
        return self 