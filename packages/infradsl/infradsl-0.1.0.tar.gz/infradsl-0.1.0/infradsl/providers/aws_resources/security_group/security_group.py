"""
AWS Security Group Complete Implementation

Combines all Security Group functionality through multiple inheritance:
- SecurityGroupCore: Core attributes and authentication
- SecurityGroupConfigurationMixin: Chainable configuration methods
- SecurityGroupLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .security_group_core import SecurityGroupCore
from .security_group_configuration import SecurityGroupConfigurationMixin
from .security_group_lifecycle import SecurityGroupLifecycleMixin


class SecurityGroup(SecurityGroupLifecycleMixin, SecurityGroupConfigurationMixin, SecurityGroupCore):
    """
    Complete AWS Security Group implementation for network firewall management.
    
    This class combines:
    - Firewall rule configuration methods (ingress/egress rules)
    - Security group lifecycle management (create, destroy, preview)
    - Common port shortcuts and security presets
    - VPC and networking integration
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize Security Group instance for firewall management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.security_validated = False
    
    def validate_security_rules(self):
        """Validate the current security group rules for best practices"""
        warnings = []
        errors = []
        
        # Check for overly permissive rules
        for rule in self.ingress_rules:
            if rule['source'] == '0.0.0.0/0':
                if rule['port'] == 22:
                    warnings.append("SSH (port 22) is open to the internet (0.0.0.0/0)")
                elif rule['port'] == 3389:
                    warnings.append("RDP (port 3389) is open to the internet (0.0.0.0/0)")
                elif rule['port'] in [3306, 5432, 6379]:
                    errors.append(f"Database port {rule['port']} should not be open to the internet")
        
        # Check for missing descriptions
        for rule in self.ingress_rules + self.egress_rules:
            if not rule.get('description'):
                warnings.append(f"Rule for port {rule['port']} lacks description")
        
        # Check for unnecessary rules
        if len(self.ingress_rules) == 0:
            warnings.append("No ingress rules defined - this security group will block all incoming traffic")
        
        if errors:
            raise ValueError(f"Security validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Security warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.security_validated = True
        return True
    
    def get_security_summary(self):
        """Get a security summary of the security group"""
        return {
            'group_id': self.group_id,
            'group_name': self.group_name or self.name,
            'description': self.group_description,
            'vpc_id': self.vpc_id or 'Default VPC',
            'ingress_rules_count': len(self.ingress_rules),
            'egress_rules_count': len(self.egress_rules),
            'tags_count': len(self.tags),
            'security_group_exists': self.security_group_exists,
            'deployment_ready': self.deployment_ready,
            'security_validated': self.security_validated,
            'open_ports': [rule['port'] for rule in self.ingress_rules if rule['source'] == '0.0.0.0/0'],
            'restricted_ports': [rule['port'] for rule in self.ingress_rules if rule['source'] != '0.0.0.0/0']
        }
    
    def clone(self, new_name: str):
        """Create a copy of this security group with a new name"""
        cloned_sg = SecurityGroup(new_name)
        cloned_sg.group_description = f"Clone of {self.group_description}"
        cloned_sg.vpc_id = self.vpc_id
        cloned_sg.ingress_rules = self.ingress_rules.copy()
        cloned_sg.egress_rules = self.egress_rules.copy()
        cloned_sg.tags = self.tags.copy()
        return cloned_sg
    
    def export_rules(self):
        """Export security group rules for backup or migration"""
        return {
            'metadata': {
                'group_name': self.group_name or self.name,
                'description': self.group_description,
                'vpc_id': self.vpc_id,
                'exported_at': 'Mock timestamp'
            },
            'ingress_rules': self.ingress_rules,
            'egress_rules': self.egress_rules,
            'tags': self.tags
        }
    
    def import_rules(self, rules_data: dict):
        """Import security group rules from exported data"""
        if 'ingress_rules' in rules_data:
            self.ingress_rules = rules_data['ingress_rules']
        if 'egress_rules' in rules_data:
            self.egress_rules = rules_data['egress_rules']
        if 'tags' in rules_data:
            self.tags = rules_data['tags']
        return self


# Convenience function for creating SecurityGroup instances
def create_security_group(name: str, description: str = None) -> SecurityGroup:
    """Create a new Security Group with optional description"""
    sg = SecurityGroup(name)
    if description:
        sg.description(description)
    return sg