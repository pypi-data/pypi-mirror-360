from typing import Dict, Any, List
import uuid

class SecurityGroupLifecycleMixin:
    """
    Mixin for SecurityGroup lifecycle operations (create, update, destroy).
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Mock discovery for now - in real implementation this would use AWS SDK
        existing_security_groups = {}
        
        # Determine desired state
        desired_group_name = self.group_name or self.name
        
        # Categorize security groups
        to_create = []
        to_keep = []
        to_remove = []
        
        # Check if our desired security group exists
        group_exists = desired_group_name in existing_security_groups
        
        if not group_exists:
            to_create.append({
                'name': desired_group_name,
                'description': self.group_description,
                'vpc_id': self.vpc_id or 'Default VPC',
                'ingress_rules': self.ingress_rules,
                'egress_rules': self.egress_rules,
                'tags': self.tags
            })
        else:
            to_keep.append(existing_security_groups[desired_group_name])
        
        self._display_preview(to_create, to_keep, to_remove)
        
        return {
            'resource_type': 'AWS Security Group',
            'name': desired_group_name,
            'group_id': f"sg-{str(uuid.uuid4()).replace('-', '')[:17]}",  # Mock security group ID
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_security_groups': existing_security_groups,
            'description': self.group_description,
            'vpc_id': self.vpc_id or 'Default VPC',
            'ingress_rules_count': len(self.ingress_rules),
            'egress_rules_count': len(self.egress_rules),
            'estimated_cost': '$0.00/month'
        }
    
    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n🔒 Security Group Preview")
        
        # Show security groups to create
        if to_create:
            print(f"╭─ 🛡️  Security Groups to CREATE: {len(to_create)}")
            for sg in to_create:
                print(f"├─ 🆕 {sg['name']}")
                print(f"│  ├─ 📝 Description: {sg['description']}")
                print(f"│  ├─ 🌐 VPC: {sg['vpc_id']}")
                
                if sg['ingress_rules']:
                    print(f"│  ├─ 📥 Ingress Rules: {len(sg['ingress_rules'])}")
                    for i, rule in enumerate(sg['ingress_rules'][:5]):  # Show first 5 rules
                        connector = "│  │  ├─" if i < min(len(sg['ingress_rules']), 5) - 1 else "│  │  └─"
                        port_info = f"Port {rule['port']}" if rule['port'] != 'icmp' else "ICMP"
                        print(f"{connector} {port_info}: {rule['source']} ({rule['protocol'].upper()})")
                        if rule.get('description'):
                            print(f"│  │     └─ {rule['description']}")
                    if len(sg['ingress_rules']) > 5:
                        print(f"│  │     └─ ... and {len(sg['ingress_rules']) - 5} more rules")
                
                if sg['egress_rules']:
                    print(f"│  ├─ 📤 Egress Rules: {len(sg['egress_rules'])}")
                    for i, rule in enumerate(sg['egress_rules'][:3]):  # Show first 3 rules
                        connector = "│  │  ├─" if i < min(len(sg['egress_rules']), 3) - 1 else "│  │  └─"
                        port_info = f"Port {rule['port']}" if rule['port'] != 'icmp' else "ICMP"
                        print(f"{connector} {port_info}: {rule['destination']} ({rule['protocol'].upper()})")
                        if rule.get('description'):
                            print(f"│  │     └─ {rule['description']}")
                    if len(sg['egress_rules']) > 3:
                        print(f"│  │     └─ ... and {len(sg['egress_rules']) - 3} more rules")
                
                if sg['tags']:
                    print(f"│  ├─ 🏷️  Tags: {len(sg['tags'])}")
                    for key, value in list(sg['tags'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if len(sg['tags']) > 3:
                        print(f"│  │  └─ ... and {len(sg['tags']) - 3} more tags")
                
                print(f"│  └─ 💰 Cost: $0.00/month (no charge for security groups)")
            print(f"╰─")
        
        # Show security groups to keep
        if to_keep:
            print(f"╭─ 🔄 Security Groups to KEEP: {len(to_keep)}")
            for sg in to_keep:
                print(f"├─ ✅ {sg.get('name', 'Unknown')}")
                print(f"│  ├─ 🆔 Group ID: {sg.get('id', 'Unknown')}")
                print(f"│  ├─ 🌐 VPC: {sg.get('vpc_id', 'Unknown')}")
                print(f"│  └─ 📊 Rules: {sg.get('rules_count', 'Unknown')}")
            print(f"╰─")
        
        # Show security best practices
        print(f"\n🛡️  Security Best Practices:")
        print(f"   ├─ 🔒 Principle of Least Privilege: Only allow necessary traffic")
        print(f"   ├─ 🌐 Source Restrictions: Avoid 0.0.0.0/0 for sensitive ports")
        print(f"   ├─ 📝 Rule Documentation: Add descriptions to all rules")
        print(f"   └─ 🔄 Regular Audits: Review and remove unused rules")
    
    def create(self) -> Dict[str, Any]:
        """Create/update security group"""
        self._ensure_authenticated()
        
        desired_group_name = self.group_name or self.name
        group_id = f"sg-{str(uuid.uuid4()).replace('-', '')[:17]}"
        
        print(f"\n🔒 Creating Security Group: {desired_group_name}")
        print(f"   📝 Description: {self.group_description}")
        print(f"   🌐 VPC: {self.vpc_id or 'Default VPC'}")
        
        try:
            # Mock creation for now - in real implementation this would use AWS SDK
            result = {
                'group_id': group_id,
                'group_name': desired_group_name,
                'description': self.group_description,
                'vpc_id': self.vpc_id or 'Default VPC',
                'ingress_rules': self.ingress_rules,
                'egress_rules': self.egress_rules,
                'tags': self.tags,
                'status': 'Available'
            }
            
            # Update instance attributes
            self.group_id = result['group_id']
            self.security_group_exists = True
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create Security Group: {str(e)}")
            raise
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ Security Group created successfully")
        print(f"   📋 Group ID: {result['group_id']}")
        print(f"   🏷️  Group Name: {result['group_name']}")
        print(f"   🌐 VPC: {result['vpc_id']}")
        print(f"   📥 Ingress Rules: {len(result['ingress_rules'])}")
        print(f"   📤 Egress Rules: {len(result['egress_rules'])}")
        if result['tags']:
            print(f"   🏷️  Tags: {len(result['tags'])}")
        print(f"   📊 Status: {result['status']}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the security group"""
        self._ensure_authenticated()
        
        print(f"🗑️ Destroying Security Group: {self.group_name or self.name}")
        
        try:
            # Mock destruction for now - in real implementation this would use AWS SDK
            result = {
                'group_id': self.group_id,
                'group_name': self.group_name or self.name,
                'status': 'Deleted',
                'deleted': True
            }
            
            # Reset instance attributes
            self.group_id = None
            self.security_group_exists = False
            
            print(f"✅ Security Group destruction completed")
            print(f"   📋 Group ID: {result['group_id']}")
            print(f"   📊 Status: {result['status']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy Security Group: {str(e)}")
            raise