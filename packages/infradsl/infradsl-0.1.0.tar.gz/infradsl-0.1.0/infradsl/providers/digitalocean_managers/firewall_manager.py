import digitalocean
from typing import List, Optional
from digitalocean import Firewall, InboundRule, OutboundRule, Destinations, Sources
from .do_client import DoClient
from .infrastructure_planner import FirewallRule


class FirewallManager:
    """Manages firewall operations including creation, updates, and cleanup"""
    
    def __init__(self, do_client: DoClient):
        self.do_client = do_client
    
    def create_firewall(self, droplet_name: str, firewall_rules: List[FirewallRule], droplet_id: int) -> Optional[str]:
        """Create a firewall with the configured rules"""
        try:
            # Build inbound rules from firewall config
            inbound_rules = []
            for rule in firewall_rules:
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
            
            # Create firewall
            firewall = Firewall(
                token=self.do_client.token,
                name=f"{droplet_name}-firewall",
                inbound_rules=inbound_rules,
                outbound_rules=outbound_rules,
                droplet_ids=[droplet_id]
            )
            firewall.create()
            
            return firewall.id
            
        except Exception as e:
            print(f"Warning: Failed to create firewall: {str(e)}")
            return None
    
    def update_firewall_if_needed(self, firewall_id: str, droplet_id: int):
        """Update firewall to ensure droplet is included and rules are current"""
        try:
            firewall = digitalocean.Firewall()
            firewall.token = self.do_client.token
            firewall.id = firewall_id
            firewall.load()
            
            # Check if droplet is already in firewall
            # droplet_ids is a list of integers, not dictionaries
            droplet_ids = firewall.droplet_ids if firewall.droplet_ids else []
            if droplet_id not in droplet_ids:
                print(f"🔄 Adding droplet to existing firewall...")
                firewall.assign_droplet(droplet_id)
            else:
                print(f"✅ Droplet already in firewall")
                
        except Exception as e:
            print(f"Warning: Failed to update firewall: {str(e)}")
    
    def remove_droplet_from_firewall(self, firewall_id: str, droplet_id: int):
        """Remove droplet from firewall, and delete firewall if empty"""
        try:
            firewall = digitalocean.Firewall()
            firewall.token = self.do_client.token
            firewall.id = firewall_id
            firewall.load()
            
            # Remove droplet from firewall
            current_droplets = firewall.droplet_ids if firewall.droplet_ids else []
            if droplet_id in current_droplets:
                firewall.remove_droplets([droplet_id])
                print(f"✅ Droplet removed from firewall")
                
                # Check if firewall is now empty
                firewall.load()  # Reload to get updated droplet list
                remaining_droplets = firewall.droplet_ids if firewall.droplet_ids else []
                if not remaining_droplets:
                    print(f"🗑️  Firewall is now empty, deleting it...")
                    firewall.destroy()
                    print(f"✅ Empty firewall deleted")
                else:
                    print(f"✅ Firewall kept (still has {len(remaining_droplets)} other droplets)")
            else:
                print(f"✅ Droplet was not in firewall")
                
        except Exception as e:
            print(f"Warning: Failed to remove droplet from firewall: {str(e)}") 