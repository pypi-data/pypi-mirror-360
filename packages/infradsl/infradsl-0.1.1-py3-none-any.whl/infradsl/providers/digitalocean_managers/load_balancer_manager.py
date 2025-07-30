import digitalocean
from typing import Tuple, Optional
from digitalocean import LoadBalancer, ForwardingRule, HealthCheck
from .do_client import DoClient
from .infrastructure_planner import LoadBalancerConfig


class LoadBalancerManager:
    """Manages load balancer operations including creation, updates, and cleanup"""
    
    def __init__(self, do_client: DoClient):
        self.do_client = do_client
    
    def create_load_balancer(self, load_balancer_config: LoadBalancerConfig, region: str, droplet_id: int) -> Tuple[Optional[str], Optional[str]]:
        """Create a load balancer for the droplet"""
        try:
            # Create forwarding rules
            forwarding_rules = []
            for rule_config in load_balancer_config.forwarding_rules:
                rule = ForwardingRule(
                    entry_protocol=rule_config["entry_protocol"],
                    entry_port=rule_config["entry_port"],
                    target_protocol=rule_config["target_protocol"],
                    target_port=rule_config["target_port"],
                    tls_passthrough=rule_config.get("tls_passthrough", False)
                )
                forwarding_rules.append(rule)
            
            # Create health check
            health_check = HealthCheck(
                protocol=load_balancer_config.health_check["protocol"],
                port=load_balancer_config.health_check["port"],
                path=load_balancer_config.health_check["path"],
                check_interval_seconds=load_balancer_config.health_check["check_interval_seconds"],
                response_timeout_seconds=load_balancer_config.health_check["response_timeout_seconds"],
                healthy_threshold=load_balancer_config.health_check["healthy_threshold"],
                unhealthy_threshold=load_balancer_config.health_check["unhealthy_threshold"]
            )
            
            # Create load balancer
            load_balancer = LoadBalancer(
                token=self.do_client.token,
                name=load_balancer_config.name,
                algorithm=load_balancer_config.algorithm,
                region=region,
                forwarding_rules=forwarding_rules,
                health_check=health_check,
                droplet_ids=[droplet_id]
            )
            load_balancer.create()
            
            return load_balancer.id, load_balancer.ip
            
        except Exception as e:
            print(f"Warning: Failed to create load balancer: {str(e)}")
            return None, None
    
    def ensure_droplet_in_load_balancer(self, load_balancer_id: str, droplet_id: int):
        """Ensure droplet is attached to the load balancer"""
        try:
            lb = digitalocean.LoadBalancer()
            lb.token = self.do_client.token
            lb.id = load_balancer_id
            lb.load()
            
            # Check if droplet is already in load balancer
            # droplet_ids is a list of integers, not dictionaries
            droplet_ids = lb.droplet_ids if lb.droplet_ids else []
            if droplet_id not in droplet_ids:
                print(f"🔄 Adding droplet to existing load balancer...")
                lb.add_droplets([droplet_id])
            else:
                print(f"✅ Droplet already in load balancer")
                
        except Exception as e:
            print(f"Warning: Failed to update load balancer: {str(e)}")
    
    def remove_droplet_from_load_balancer(self, load_balancer_id: str, droplet_id: int):
        """Remove droplet from load balancer, and delete load balancer if empty"""
        try:
            load_balancer = digitalocean.LoadBalancer()
            load_balancer.token = self.do_client.token
            load_balancer.id = load_balancer_id
            load_balancer.load()
            
            # Remove droplet from load balancer
            current_droplets = load_balancer.droplet_ids if load_balancer.droplet_ids else []
            if droplet_id in current_droplets:
                load_balancer.remove_droplets([droplet_id])
                print(f"✅ Droplet removed from load balancer")
                
                # Check if load balancer is now empty
                load_balancer.load()  # Reload to get updated droplet list
                remaining_droplets = load_balancer.droplet_ids if load_balancer.droplet_ids else []
                if not remaining_droplets:
                    print(f"🗑️  Load balancer is now empty, deleting it...")
                    load_balancer.destroy()
                    print(f"✅ Empty load balancer deleted")
                else:
                    print(f"✅ Load balancer kept (still has {len(remaining_droplets)} other droplets)")
            else:
                print(f"✅ Droplet was not in load balancer")
                
        except Exception as e:
            print(f"Warning: Failed to remove droplet from load balancer: {str(e)}") 