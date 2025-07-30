from typing import List, Dict, Any, Optional
from .do_client import DoClient
from .infrastructure_planner import FirewallRule


class StandaloneFirewall:
    """Standalone firewall configuration and management"""
    
    def __init__(self, name: str, port: int, protocol: str = "tcp"):
        self.name = name
        # Default to private networks for better security
        self.rules = [FirewallRule(
            name=f"{name}-rule",
            port=port,
            protocol=protocol,
            source_addresses=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        )]
        self.do_client = DoClient()
        self._droplet_ids = []
        self._tags = []
    
    def protocol(self, protocol: str) -> 'StandaloneFirewall':
        """Set the protocol (tcp/udp)"""
        self.rules[0].protocol = protocol
        return self
    
    def source_addresses(self, addresses: List[str]) -> 'StandaloneFirewall':
        """Set source addresses for the firewall rule"""
        self.rules[0].source_addresses = addresses
        return self
    
    def allow_from(self, sources: List[str]) -> 'StandaloneFirewall':
        """Allow traffic from specific sources (alias for source_addresses)"""
        return self.source_addresses(sources)
    
    def allow_from_anywhere(self) -> 'StandaloneFirewall':
        """Allow traffic from anywhere (0.0.0.0/0, ::/0)"""
        return self.source_addresses(["0.0.0.0/0", "::/0"])
    
    def allow_from_private_networks(self) -> 'StandaloneFirewall':
        """Allow traffic only from private network ranges"""
        private_ranges = [
            "10.0.0.0/8",        # Private Class A
            "172.16.0.0/12",     # Private Class B  
            "192.168.0.0/16",    # Private Class C
            "fc00::/7"           # IPv6 private range
        ]
        return self.source_addresses(private_ranges)
    
    def allow_from_ip(self, ip: str) -> 'StandaloneFirewall':
        """Allow traffic from a specific IP address"""
        # Add /32 for IPv4 or /128 for IPv6 if not specified
        if '/' not in ip:
            if ':' in ip:  # IPv6
                ip = f"{ip}/128"
            else:  # IPv4
                ip = f"{ip}/32"
        return self.source_addresses([ip])
    
    def allow_from_subnet(self, subnet: str) -> 'StandaloneFirewall':
        """Allow traffic from a specific subnet (CIDR notation)"""
        return self.source_addresses([subnet])
    
    def add_rule(self, name: str, port: int, protocol: str = "tcp", source_addresses: List[str] = None, allow_from: str = None) -> 'StandaloneFirewall':
        """Add an additional firewall rule with flexible source specification"""
        if source_addresses is None and allow_from is None:
            # Default to private networks for better security
            source_addresses = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        elif allow_from is not None:
            # Handle convenient allow_from parameter
            if allow_from == "anywhere":
                source_addresses = ["0.0.0.0/0", "::/0"]
            elif allow_from == "private":
                source_addresses = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7"]
            elif "/" in allow_from:  # CIDR notation
                source_addresses = [allow_from]
            else:  # Single IP
                if ':' in allow_from:  # IPv6
                    source_addresses = [f"{allow_from}/128"]
                else:  # IPv4
                    source_addresses = [f"{allow_from}/32"]
        
        rule = FirewallRule(
            name=name,
            port=port,
            protocol=protocol,
            source_addresses=source_addresses
        )
        self.rules.append(rule)
        return self
    
    def add_rule_from_ip(self, name: str, port: int, ip: str, protocol: str = "tcp") -> 'StandaloneFirewall':
        """Add a rule allowing traffic from a specific IP"""
        return self.add_rule(name, port, protocol, allow_from=ip)
    
    def add_rule_from_subnet(self, name: str, port: int, subnet: str, protocol: str = "tcp") -> 'StandaloneFirewall':
        """Add a rule allowing traffic from a specific subnet"""
        return self.add_rule(name, port, protocol, allow_from=subnet)
    
    def add_rule_from_anywhere(self, name: str, port: int, protocol: str = "tcp") -> 'StandaloneFirewall':
        """Add a rule allowing traffic from anywhere (use with caution!)"""
        return self.add_rule(name, port, protocol, allow_from="anywhere")
    
    def droplet_ids(self, droplet_ids: List[int]) -> 'StandaloneFirewall':
        """Attach firewall to specific droplets by ID"""
        self._droplet_ids = droplet_ids
        return self
    
    def tags(self, tags: List[str]) -> 'StandaloneFirewall':
        """Add tags to apply firewall to droplets with these tags"""
        self._tags = tags
        return self
    
    def authenticate(self, token: str) -> 'StandaloneFirewall':
        """Set the DigitalOcean API token"""
        self.do_client.authenticate(token)
        return self

    def _discover_existing_firewalls(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DigitalOcean Firewalls"""
        existing_firewalls = {}
        
        try:
            manager = self.do_client.client
            resp = manager.firewalls.list()
            
            for firewall in resp.get("firewalls", []):
                if firewall.get("name") == self.name:
                    existing_firewalls[self.name] = {
                        "name": firewall.get("name"),
                        "id": firewall.get("id"),
                        "status": firewall.get("status", "unknown"),
                        "inbound_rules": firewall.get("inbound_rules", []),
                        "outbound_rules": firewall.get("outbound_rules", []),
                        "droplet_ids": firewall.get("droplet_ids", []),
                        "tags": firewall.get("tags", []),
                        "created_at": firewall.get("created_at")
                    }
                    break
                    
        except Exception as e:
            # Silently handle discovery errors
            pass
            
        return existing_firewalls

    def preview(self) -> Dict[str, Any]:
        """Preview DigitalOcean Firewall with smart state management"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        print(f"╭─ 🔥 DigitalOcean Firewall Preview: {self.name}")
        print(f"├─ 📋 Rules: {len(self.rules)}")
        
        # Discover existing firewalls
        existing_firewalls = self._discover_existing_firewalls()
        
        # Determine changes needed
        to_create = []
        to_update = []
        to_keep = []
        
        if self.name not in existing_firewalls:
            to_create.append(self.name)
        else:
            existing_fw = existing_firewalls[self.name]
            # Check if rules need updating
            needs_update = len(existing_fw.get("inbound_rules", [])) != len(self.rules)
            
            if needs_update:
                to_update.append(self.name)
            else:
                to_keep.append(self.name)
        
        print(f"├─ 🌍 Cost: $0/month (free)")
        
        # Show only actionable changes
        if to_create:
            print(f"├─ 🔧 Firewalls to CREATE:")
            print(f"│  ├─ 🔥 {self.name}")
            for rule in self.rules:
                sources = ', '.join(rule.source_addresses[:2]) + ('...' if len(rule.source_addresses) > 2 else '')
                print(f"│  │  ├─ {rule.protocol.upper()}/{rule.port} from {sources}")
                
        if to_update:
            print(f"├─ 🔄 Firewalls to UPDATE:")
            existing_fw = existing_firewalls[self.name]
            print(f"│  ├─ 🔥 {self.name}")
            print(f"│  │  ├─ Rules: {len(existing_fw.get('inbound_rules', []))} → {len(self.rules)}")
            
        if existing_firewalls and self.name in existing_firewalls:
            existing_fw = existing_firewalls[self.name]
            print(f"├─ ✅ Current status: {existing_fw.get('status', 'unknown')}")
            if existing_fw.get('droplet_ids'):
                print(f"├─ 🔷 Applied to {len(existing_fw.get('droplet_ids', []))} droplets")
        
        print(f"╰─ 💡 Run .create() to deploy firewall")
        
        return {
            "name": self.name,
            "to_create": to_create,
            "to_update": to_update,
            "existing_firewalls": existing_firewalls,
            "rules": [rule.dict() for rule in self.rules],
            "droplet_ids": self._droplet_ids,
            "tags": self._tags,
            "changes": len(to_create) + len(to_update) > 0
        }
    
    def create(self) -> Dict[str, Any]:
        """Create or update the standalone firewall with smart state management"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        # Discover existing firewalls first
        existing_firewalls = self._discover_existing_firewalls()
        
        # Determine changes needed
        action = "CREATE"
        existing_fw = None
        if self.name in existing_firewalls:
            existing_fw = existing_firewalls[self.name]
            # Check if update is needed
            needs_update = len(existing_fw.get("inbound_rules", [])) != len(self.rules)
            action = "UPDATE" if needs_update else "KEEP"
        
        print(f"🔥 {action}ING DigitalOcean Firewall: {self.name}")
        
        if action == "KEEP":
            print(f"✅ Firewall already exists with desired configuration")
            return {
                "id": existing_fw.get("id"),
                "name": self.name,
                "status": existing_fw.get("status"),
                "action": "kept",
                "changes": False
            }
        
        try:
            from digitalocean import Firewall as DoFirewall, InboundRule, OutboundRule, Destinations, Sources
            
            # Build inbound rules
            inbound_rules = []
            for rule in self.rules:
                inbound_rule = InboundRule(
                    protocol=rule.protocol,
                    ports=str(rule.port),
                    sources=Sources(addresses=rule.source_addresses)
                )
                inbound_rules.append(inbound_rule)
            
            # Create standard outbound rules (allow all outbound traffic)
            outbound_rules = [
                OutboundRule(
                    protocol="tcp",
                    ports="all",
                    destinations=Destinations(addresses=["0.0.0.0/0", "::/0"])
                ),
                OutboundRule(
                    protocol="udp", 
                    ports="all",
                    destinations=Destinations(addresses=["0.0.0.0/0", "::/0"])
                ),
                OutboundRule(
                    protocol="icmp",
                    destinations=Destinations(addresses=["0.0.0.0/0", "::/0"])
                )
            ]
            
            if action == "CREATE":
                # Create firewall
                firewall = DoFirewall(
                    token=self.do_client.token,
                    name=self.name,
                    inbound_rules=inbound_rules,
                    outbound_rules=outbound_rules,
                    droplet_ids=self._droplet_ids,
                    tags=self._tags
                )
                firewall.create()
                
                print(f"╭─ ✅ Firewall created successfully!")
            else:
                # Update existing firewall
                firewall = DoFirewall(token=self.do_client.token)
                firewall.id = existing_fw["id"]
                firewall.name = self.name
                firewall.inbound_rules = inbound_rules
                firewall.outbound_rules = outbound_rules
                firewall.droplet_ids = self._droplet_ids
                firewall.tags = self._tags
                firewall.save()
                
                print(f"╭─ ✅ Firewall updated successfully!")
            
            print(f"├─ 🔥 Name: {self.name}")
            print(f"├─ 📋 Rules: {len(self.rules)} configured")
            if self._droplet_ids:
                print(f"├─ 🔷 Applied to {len(self._droplet_ids)} droplets")
            if self._tags:
                print(f"├─ 🏷️  Applied to droplets with tags: {', '.join(self._tags)}")
            print(f"╰─ 🆔 ID: {firewall.id}")
            
            return {
                "id": firewall.id,
                "name": self.name,
                "rules": [rule.dict() for rule in self.rules],
                "droplet_ids": self._droplet_ids,
                "tags": self._tags,
                "action": action.lower(),
                "changes": True
            }
            
        except Exception as e:
            raise Exception(f"Failed to {action.lower()} firewall: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Destroy the standalone firewall"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        print(f"\n🗑️  Destroying firewall: {self.name}")
        
        try:
            import digitalocean
            
            # Find the firewall
            firewalls = digitalocean.Firewall(token=self.do_client.token)
            all_firewalls = firewalls.get_all()
            
            firewall_to_destroy = None
            for firewall in all_firewalls:
                if firewall.name == self.name:
                    firewall_to_destroy = firewall
                    break
            
            if not firewall_to_destroy:
                print(f"✅ No firewall found with name: {self.name}")
                return {"firewall": False}
            
            # Destroy the firewall
            print(f"🗑️  Destroying firewall: {firewall_to_destroy.name} (ID: {firewall_to_destroy.id})")
            firewall_to_destroy.destroy()
            print(f"✅ Firewall destroyed successfully")
            return {"firewall": True}
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to destroy firewall: {e}")
            return {"firewall": False} 