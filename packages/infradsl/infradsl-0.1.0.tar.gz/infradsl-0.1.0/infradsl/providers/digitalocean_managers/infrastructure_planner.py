from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class FirewallRule(BaseModel):
    name: str
    port: int
    protocol: str = "tcp"
    source_addresses: List[str] = ["0.0.0.0/0", "::/0"]


class LoadBalancerConfig(BaseModel):
    name: str
    algorithm: str = "round_robin"
    size: Optional[str] = None
    forwarding_rules: List[Dict[str, Any]] = []
    health_check: Dict[str, Any] = {}
    droplet_ids: List[int] = []


class KubernetesNodePool(BaseModel):
    size: str
    count: int
    name: str
    min_nodes: Optional[int] = None
    max_nodes: Optional[int] = None


class KubernetesClusterConfig(BaseModel):
    name: str
    region: str
    version: str
    node_pools: List[KubernetesNodePool] = []
    high_availability: bool = False
    addons: List[str] = []


class InfrastructurePlanner:
    """Plans what infrastructure changes need to be made"""
    
    def __init__(self):
        pass
    
    def plan_infrastructure_changes(
        self, 
        existing_resources: Dict[str, Any], 
        firewall_rules: Optional[List[FirewallRule]] = None,
        load_balancer_config: Optional[LoadBalancerConfig] = None
    ) -> Dict[str, Any]:
        """Plan what infrastructure changes need to be made"""
        actions = {
            'droplet': {'action': 'create'},
            'firewall': {'action': 'skip'},
            'load_balancer': {'action': 'skip'}
        }
        
        # Plan droplet action
        if existing_resources['droplet']:
            actions['droplet'] = {
                'action': 'use',
                'id': existing_resources['droplet']['id'],
                'name': existing_resources['droplet']['name']
            }
        
        # Plan firewall action
        if firewall_rules:
            # User wants a firewall
            if existing_resources['firewall']:
                actions['firewall'] = {
                    'action': 'use',
                    'id': existing_resources['firewall']['id'],
                    'name': existing_resources['firewall']['name']
                }
            else:
                actions['firewall'] = {'action': 'create'}
        else:
            # User doesn't want a firewall
            if existing_resources['firewall']:
                actions['firewall'] = {
                    'action': 'remove',
                    'id': existing_resources['firewall']['id'],
                    'name': existing_resources['firewall']['name']
                }
        
        # Plan load balancer action
        if load_balancer_config:
            # User wants a load balancer
            if existing_resources['load_balancer']:
                actions['load_balancer'] = {
                    'action': 'use',
                    'id': existing_resources['load_balancer']['id'],
                    'name': existing_resources['load_balancer']['name'],
                    'ip': existing_resources['load_balancer']['ip']
                }
            else:
                actions['load_balancer'] = {'action': 'create'}
        else:
            # User doesn't want a load balancer
            if existing_resources['load_balancer']:
                actions['load_balancer'] = {
                    'action': 'remove',
                    'id': existing_resources['load_balancer']['id'],
                    'name': existing_resources['load_balancer']['name'],
                    'ip': existing_resources['load_balancer']['ip']
                }
        
        return actions
    
    def print_planned_actions(self, actions: Dict[str, Any], droplet_name: str, firewall_rules: Optional[List[FirewallRule]] = None, load_balancer_config: Optional[LoadBalancerConfig] = None):
        """Print the planned infrastructure actions"""
        print(f"\n🔍 Infrastructure Plan:")
        
        # Print droplet actions
        if actions['droplet']['action'] == 'create':
            print(f"➕ Will create new droplet: {droplet_name}")
        elif actions['droplet']['action'] == 'use':
            print(f"✅ Will use existing droplet: {actions['droplet']['name']} ({actions['droplet']['id']})")
            
        # Print firewall actions
        if actions['firewall']['action'] == 'create':
            print(f"➕ Will create new firewall with {len(firewall_rules)} rules")
        elif actions['firewall']['action'] == 'use':
            print(f"✅ Will use existing firewall: {actions['firewall']['name']} ({actions['firewall']['id']})")
        elif actions['firewall']['action'] == 'remove':
            print(f"🔄 Will remove droplet from firewall: {actions['firewall']['name']} ({actions['firewall']['id']})")
            
        # Print load balancer actions
        if actions['load_balancer']['action'] == 'create':
            print(f"➕ Will create new load balancer: {load_balancer_config.name}")
        elif actions['load_balancer']['action'] == 'use':
            print(f"✅ Will use existing load balancer: {actions['load_balancer']['name']} ({actions['load_balancer']['ip']})")
        elif actions['load_balancer']['action'] == 'remove':
            print(f"🔄 Will remove droplet from load balancer: {actions['load_balancer']['name']} ({actions['load_balancer']['ip']})") 