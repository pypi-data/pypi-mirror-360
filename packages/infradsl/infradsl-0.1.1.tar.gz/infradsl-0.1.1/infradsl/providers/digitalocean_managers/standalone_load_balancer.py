from typing import List, Dict, Any, Optional
from .do_client import DoClient
from .infrastructure_planner import LoadBalancerConfig
import time

class StandaloneLoadBalancer:
    """Standalone load balancer configuration and management"""
    
    def __init__(self, name: str):
        self.config = LoadBalancerConfig(
            name=name,
            algorithm="round_robin",
            forwarding_rules=[],
            health_check={
                "protocol": "http",
                "port": 80,
                "path": "/",
                "check_interval_seconds": 10,
                "response_timeout_seconds": 5,
                "healthy_threshold": 5,
                "unhealthy_threshold": 3
            },
            droplet_ids=[]
        )
        self._region = None
        self.do_client = DoClient()
    
    def region(self, region: str) -> 'StandaloneLoadBalancer':
        """Set the region for the load balancer"""
        self._region = region
        return self
    
    def size(self, size: str) -> 'StandaloneLoadBalancer':
        """Set the load balancer size (e.g., lb-small-1vcpu-1gb)"""
        self.config.size = size
        return self
    
    def algorithm(self, algorithm: str) -> 'StandaloneLoadBalancer':
        """Set the load balancing algorithm (round_robin, least_connections)"""
        self.config.algorithm = algorithm
        return self
    
    def forwarding_rule(self, entry_protocol: str, entry_port: int, target_protocol: str, target_port: int, tls_passthrough: bool = False) -> 'StandaloneLoadBalancer':
        """Add a forwarding rule"""
        rule = {
            "entry_protocol": entry_protocol,
            "entry_port": entry_port,
            "target_protocol": target_protocol,
            "target_port": target_port,
            "tls_passthrough": tls_passthrough
        }
        self.config.forwarding_rules.append(rule)
        return self
    
    def forwarding_rules(self, *rules) -> 'StandaloneLoadBalancer':
        """Add multiple forwarding rules"""
        for rule in rules:
            if hasattr(rule, 'to_dict'):
                # It's a ForwardingRule object
                self.config.forwarding_rules.append(rule.to_dict())
            else:
                # It's a dictionary
                self.config.forwarding_rules.append(rule)
        return self
    
    def health_check(self, protocol: str, port: int, path: str = "/", check_interval: int = 10, timeout: int = 5, healthy_threshold: int = 5, unhealthy_threshold: int = 3) -> 'StandaloneLoadBalancer':
        """Configure health check settings"""
        self.config.health_check = {
            "protocol": protocol,
            "port": port,
            "path": path,
            "check_interval_seconds": check_interval,
            "response_timeout_seconds": timeout,
            "healthy_threshold": healthy_threshold,
            "unhealthy_threshold": unhealthy_threshold
        }
        return self
    
    def droplet_ids(self, droplet_ids: List[int]) -> 'StandaloneLoadBalancer':
        """Attach load balancer to specific droplets by ID"""
        self.config.droplet_ids = droplet_ids
        return self
    
    def authenticate(self, token: str) -> 'StandaloneLoadBalancer':
        """Set the DigitalOcean API token"""
        self.do_client.authenticate(token)
        return self

    def _discover_existing_load_balancers(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DigitalOcean Load Balancers"""
        existing_lbs = {}
        
        try:
            manager = self.do_client.client
            resp = manager.load_balancers.list()
            
            for lb in resp.get("load_balancers", []):
                if lb.get("name") == self.config.name:
                    existing_lbs[self.config.name] = {
                        "name": lb.get("name"),
                        "id": lb.get("id"),
                        "ip": lb.get("ip"),
                        "status": lb.get("status", "unknown"),
                        "algorithm": lb.get("algorithm"),
                        "forwarding_rules": lb.get("forwarding_rules", []),
                        "health_check": lb.get("health_check", {}),
                        "droplet_ids": lb.get("droplet_ids", []),
                        "region": lb.get("region", {}).get("slug"),
                        "size": lb.get("size_unit", 1),
                        "created_at": lb.get("created_at")
                    }
                    break
                    
        except Exception as e:
            # Silently handle discovery errors
            pass
            
        return existing_lbs
    
    def preview(self) -> Dict[str, Any]:
        """Preview DigitalOcean Load Balancer with smart state management"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        if not self._region:
            raise ValueError("Region is required. Use .region() to set it.")
        
        print(f"╭─ ⚖️  DigitalOcean Load Balancer Preview: {self.config.name}")
        print(f"├─ 🌍 Region: {self._region}")
        print(f"├─ 🔄 Algorithm: {self.config.algorithm}")
        
        # Discover existing load balancers
        existing_lbs = self._discover_existing_load_balancers()
        
        # Determine changes needed
        to_create = []
        to_update = []
        to_keep = []
        
        if self.config.name not in existing_lbs:
            to_create.append(self.config.name)
        else:
            existing_lb = existing_lbs[self.config.name]
            # Check if update is needed
            needs_update = (
                existing_lb.get("algorithm") != self.config.algorithm or
                len(existing_lb.get("forwarding_rules", [])) != len(self.config.forwarding_rules)
            )
            
            if needs_update:
                to_update.append(self.config.name)
            else:
                to_keep.append(self.config.name)
        
        print(f"├─ 🌍 Cost: ~$12/month (lb-small)")
        
        # Show only actionable changes
        if to_create:
            print(f"├─ 🔧 Load Balancers to CREATE:")
            print(f"│  ├─ ⚖️  {self.config.name}")
            if self.config.forwarding_rules:
                print(f"│  │  ├─ Forwarding Rules:")
                for rule in self.config.forwarding_rules:
                    tls = " (TLS)" if rule.get("tls_passthrough") else ""
                    print(f"│  │  │  ├─ {rule['entry_protocol'].upper()}:{rule['entry_port']} → {rule['target_protocol'].upper()}:{rule['target_port']}{tls}")
                
        if to_update:
            print(f"├─ 🔄 Load Balancers to UPDATE:")
            existing_lb = existing_lbs[self.config.name]
            print(f"│  ├─ ⚖️  {self.config.name}")
            print(f"│  │  ├─ Algorithm: {existing_lb.get('algorithm')} → {self.config.algorithm}")
            print(f"│  │  ├─ Rules: {len(existing_lb.get('forwarding_rules', []))} → {len(self.config.forwarding_rules)}")
            
        if existing_lbs and self.config.name in existing_lbs:
            existing_lb = existing_lbs[self.config.name]
            print(f"├─ ✅ Current status: {existing_lb.get('status', 'unknown')}")
            if existing_lb.get('ip'):
                print(f"├─ 🌐 Current IP: {existing_lb['ip']}")
            if existing_lb.get('droplet_ids'):
                print(f"├─ 🔷 Attached to {len(existing_lb.get('droplet_ids', []))} droplets")
        
        print(f"╰─ 💡 Run .create() to deploy load balancer")
        
        return {
            "name": self.config.name,
            "to_create": to_create,
            "to_update": to_update,
            "existing_lbs": existing_lbs,
            "region": self._region,
            "algorithm": self.config.algorithm,
            "forwarding_rules": self.config.forwarding_rules,
            "health_check": self.config.health_check,
            "droplet_ids": self.config.droplet_ids,
            "changes": len(to_create) + len(to_update) > 0
        }
    
    def create(self) -> Dict[str, Any]:
        """Create or update the standalone load balancer with smart state management"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        if not self._region:
            raise ValueError("Region is required. Use .region() to set it.")

        # Discover existing load balancers first
        existing_lbs = self._discover_existing_load_balancers()
        
        # Determine changes needed
        action = "CREATE"
        existing_lb = None
        if self.config.name in existing_lbs:
            existing_lb = existing_lbs[self.config.name]
            # Check if update is needed
            needs_update = (
                existing_lb.get("algorithm") != self.config.algorithm or
                len(existing_lb.get("forwarding_rules", [])) != len(self.config.forwarding_rules)
            )
            action = "UPDATE" if needs_update else "KEEP"
        
        print(f"⚖️  {action}ING DigitalOcean Load Balancer: {self.config.name}")
        
        if action == "KEEP":
            print(f"✅ Load balancer already exists with desired configuration")
            return {
                "id": existing_lb.get("id"),
                "name": self.config.name,
                "ip": existing_lb.get("ip"),
                "status": existing_lb.get("status"),
                "action": "kept",
                "changes": False
            }

        manager = self.do_client.client

        try:
            if action == "CREATE":
                print(f"╭─ 🔧 Creating new load balancer...")
                
                create_req = {
                    "name": self.config.name,
                    "algorithm": self.config.algorithm,
                    "region": self._region,
                    "forwarding_rules": self.config.forwarding_rules,
                    "health_check": self.config.health_check,
                    "droplet_ids": self.config.droplet_ids
                }
                
                # Add size if specified
                if self.config.size:
                    create_req["size"] = self.config.size
                
                create_resp = manager.load_balancers.create(body=create_req)
                load_balancer = create_resp['load_balancer']
                print(f"│  ├─ ⏳ Waiting for IP assignment...")
                
            else:  # UPDATE
                print(f"╭─ 🔄 Using existing load balancer...")
                load_balancer = existing_lb

            # Wait for IP to be assigned (for new LBs)
            if action == "CREATE":
                lb_id = load_balancer['id']
                for _ in range(30):  # Try for 60 seconds
                    try:
                        get_resp = manager.load_balancers.get(lb_id)
                        load_balancer = get_resp['load_balancer']
                        if load_balancer.get('ip'):
                            break
                        time.sleep(2)
                    except Exception:
                        time.sleep(2)
                        continue

            print(f"├─ ✅ Load balancer {action.lower()}d successfully!")
            print(f"├─ ⚖️  Name: {self.config.name}")
            print(f"├─ 🌐 IP: {load_balancer.get('ip', 'Pending...')}")
            print(f"├─ 🔄 Algorithm: {self.config.algorithm}")
            print(f"├─ 📋 Rules: {len(self.config.forwarding_rules)}")
            if self.config.droplet_ids:
                print(f"├─ 🔷 Attached to {len(self.config.droplet_ids)} droplets")
            print(f"╰─ 🆔 ID: {load_balancer['id']}")

            return {
                "id": load_balancer['id'],
                "name": self.config.name,
                "ip": load_balancer.get('ip'),
                "status": load_balancer.get('status'),
                "algorithm": self.config.algorithm,
                "forwarding_rules": self.config.forwarding_rules,
                "droplet_ids": self.config.droplet_ids,
                "region": self._region,
                "action": action.lower(),
                "changes": True
            }

        except Exception as e:
            if "already a load balancer with that name" in str(e):
                print(f"⚖️  Load balancer '{self.config.name}' already exists, fetching it...")
                # Refetch the load balancer if creation fails due to existence
                existing_lbs = self._discover_existing_load_balancers()
                if self.config.name in existing_lbs:
                    load_balancer = existing_lbs[self.config.name]
                    print(f"✅ Using existing load balancer: {load_balancer.get('ip', 'No IP')}")
                    return {
                        "id": load_balancer.get("id"),
                        "name": self.config.name,
                        "ip": load_balancer.get("ip"),
                        "status": load_balancer.get("status"),
                        "action": "found_existing",
                        "changes": False
                    }
            raise Exception(f"Failed to {action.lower()} load balancer: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Destroy the standalone load balancer"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        if not self._region:
            raise ValueError("Region is required. Use .region() to set it.")
        
        print(f"\n🗑️  Destroying load balancer: {self.config.name}")
        
        manager = self.do_client.client
        load_balancer = None

        # Find the load balancer
        try:
            list_resp = manager.load_balancers.list()
            for lb in list_resp.get("load_balancers", []):
                if lb['name'] == self.config.name and lb['region']['slug'] == self._region:
                    load_balancer = lb
                    break
        except Exception as e:
            print(f"⚠️  Warning: Failed to check for existing load balancers: {e}")
            return {"load_balancer": False}

        if not load_balancer:
            print(f"✅ No load balancer found with name: {self.config.name}")
            return {"load_balancer": False}
        
        # Destroy the load balancer
        try:
            print(f"🗑️  Destroying load balancer: {load_balancer['name']} (ID: {load_balancer['id']})")
            manager.load_balancers.delete(load_balancer['id'])
            print(f"✅ Load balancer destroyed successfully")
            return {"load_balancer": True}
        except Exception as e:
            print(f"⚠️  Warning: Failed to destroy load balancer: {e}")
            return {"load_balancer": False} 