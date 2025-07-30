import digitalocean
from typing import Dict, Any, Optional
from .do_client import DoClient


class ResourceDiscovery:
    """Discovers existing DigitalOcean resources that match our configuration"""
    
    def __init__(self, do_client: DoClient):
        self.do_client = do_client
    
    def discover_existing_resources(self, droplet_name: str, load_balancer_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover existing resources that match our configuration"""
        existing = {
            'droplet': None,
            'firewall': None,
            'load_balancer': None
        }
        
        try:
            # Find existing droplet by name
            existing['droplet'] = self._find_droplet(droplet_name)
            
            # Find existing firewall by name
            existing['firewall'] = self._find_firewall(f"{droplet_name}-firewall")
            
            # Find existing load balancer
            existing['load_balancer'] = self._find_load_balancer(droplet_name, load_balancer_name)
                        
        except Exception as e:
            print(f"Warning: Error discovering existing resources: {str(e)}")
            
        return existing
    
    def _find_droplet(self, droplet_name: str) -> Optional[Dict[str, Any]]:
        """Find existing droplet by name"""
        try:
            droplets = self.do_client.client.get_all_droplets()
            for droplet in droplets:
                if droplet.name == droplet_name:
                    return {
                        'id': droplet.id,
                        'name': droplet.name,
                        'ip': droplet.ip_address,
                        'status': droplet.status
                    }
        except Exception as e:
            print(f"Warning: Error finding droplet: {str(e)}")
        return None
    
    def _find_firewall(self, firewall_name: str) -> Optional[Dict[str, Any]]:
        """Find existing firewall by name"""
        try:
            firewalls = self.do_client.client.get_all_firewalls()
            for firewall in firewalls:
                if firewall.name == firewall_name:
                    return {
                        'id': firewall.id,
                        'name': firewall.name
                    }
        except Exception as e:
            print(f"Warning: Error finding firewall: {str(e)}")
        return None
    
    def _find_load_balancer(self, droplet_name: str, load_balancer_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find existing load balancer"""
        try:
            load_balancers = self.do_client.client.get_all_load_balancers()
            droplet_id = None
            
            # First get the droplet ID if we need to search by droplet association
            if not load_balancer_name:
                droplet = self._find_droplet(droplet_name)
                if droplet:
                    droplet_id = droplet['id']
            
            for lb in load_balancers:
                # First, check if this is the load balancer we want (if we have one defined)
                if load_balancer_name and lb.name == load_balancer_name:
                    return {
                        'id': lb.id,
                        'name': lb.name,
                        'ip': lb.ip,
                        'obj': lb
                    }
                # If no specific load balancer is wanted, check if this droplet is in any load balancer
                elif not load_balancer_name and droplet_id:
                    # Load the full load balancer details to check droplet associations
                    lb_full = digitalocean.LoadBalancer()
                    lb_full.token = self.do_client.token
                    lb_full.id = lb.id
                    try:
                        lb_full.load()
                        # Check if our droplet is in this load balancer
                        if lb_full.droplet_ids and droplet_id in lb_full.droplet_ids:
                            return {
                                'id': lb.id,
                                'name': lb.name,
                                'ip': lb.ip,
                                'obj': lb_full
                            }
                    except Exception:
                        # Skip this load balancer if we can't load it
                        continue
        except Exception as e:
            print(f"Warning: Error finding load balancer: {str(e)}")
        
        return None 