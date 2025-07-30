from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource
from ..compute.vm_group import VmGroup
from ...googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager, LoadBalancerConfig, BackendConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter


class LoadBalancer(BaseGcpResource):
    """A standalone load balancer for web services"""

    def __init__(self, name: str):
        self.config = LoadBalancerConfig(name=name)
        self.status_reporter = GcpStatusReporter()
        super().__init__(name)

    def _initialize_managers(self):
        """Initialize Load Balancer specific managers"""
        self.load_balancer_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.load_balancer_manager = GcpLoadBalancerManager(self.gcp_client)

    def _discover_existing_load_balancers(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Google Cloud Load Balancers"""
        existing_load_balancers = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            service = discovery.build('compute', 'v1', credentials=self.gcp_client.credentials)
            
            # Get forwarding rules (main entry point for load balancers)
            request = service.forwardingRules().list(project=self.gcp_client.project_id, region=self.gcp_client.region)
            forwarding_rules = request.execute()
            
            for rule in forwarding_rules.get('items', []):
                lb_name = rule['name']
                
                try:
                    # Get target pools and backend services
                    backends = []
                    backend_service = None
                    
                    if 'target' in rule:
                        target_url = rule['target']
                        
                        # Check if it's a target pool or backend service
                        if 'targetPools' in target_url:
                            # Get target pool details
                            pool_name = target_url.split('/')[-1]
                            pool_request = service.targetPools().get(
                                project=self.gcp_client.project_id,
                                region=self.gcp_client.region,
                                targetPool=pool_name
                            )
                            pool = pool_request.execute()
                            
                            # Extract backend instances
                            for instance_url in pool.get('instances', []):
                                instance_name = instance_url.split('/')[-1]
                                zone = instance_url.split('/')[-3]
                                backends.append({
                                    'vm_name': instance_name,
                                    'zone': zone,
                                    'type': 'instance'
                                })
                        
                        elif 'backendServices' in target_url:
                            # Get backend service details
                            service_name = target_url.split('/')[-1]
                            bs_request = service.backendServices().get(
                                project=self.gcp_client.project_id,
                                backendService=service_name
                            )
                            backend_service = bs_request.execute()
                            
                            # Extract backend groups
                            for backend in backend_service.get('backends', []):
                                group_url = backend['group']
                                group_name = group_url.split('/')[-1]
                                zone = group_url.split('/')[-3] if 'zones' in group_url else 'global'
                                backends.append({
                                    'group_name': group_name,
                                    'zone': zone,
                                    'type': 'instance_group'
                                })
                    
                    existing_load_balancers[lb_name] = {
                        'lb_name': lb_name,
                        'ip_address': rule.get('IPAddress'),
                        'port_range': rule.get('portRange', '80-80'),
                        'protocol': rule.get('IPProtocol', 'TCP'),
                        'backends': backends,
                        'backend_count': len(backends),
                        'creation_timestamp': rule.get('creationTimestamp'),
                        'region': rule.get('region', '').split('/')[-1] if rule.get('region') else 'global',
                        'load_balancing_scheme': rule.get('loadBalancingScheme', 'EXTERNAL'),
                        'network_tier': rule.get('networkTier', 'PREMIUM'),
                        'target_url': rule.get('target'),
                        'backend_service': backend_service.get('name') if backend_service else None,
                        'health_checks': [hc.split('/')[-1] for hc in backend_service.get('healthChecks', [])] if backend_service else []
                    }
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        continue
                    else:
                        print(f"⚠️  Failed to get details for load balancer {lb_name}: {str(e)}")
                        existing_load_balancers[lb_name] = {
                            'lb_name': lb_name,
                            'error': str(e)
                        }
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing load balancers: {str(e)}")
        
        return existing_load_balancers

    def backend(self, *args, **kwargs) -> 'LoadBalancer':
        """Add a backend VM or VM group to the load balancer - Rails-like DRY support"""
        if args:
            # Check if it's a multi-VM instance (our new DRY approach)
            if hasattr(args[0], 'is_multi_vm') and hasattr(args[0], 'vm_names'):
                vm_instance = args[0]
                port = kwargs.get("port", 80)

                if vm_instance.is_multi_vm:
                    # Handle multiple VMs from the DRY approach
                    print(f"   🔗 Adding {len(vm_instance.vm_names)} VMs to load balancer backends")
                    for vm_name in vm_instance.vm_names:
                        config = vm_instance.configs[vm_name]
                        health_check_name = f"{vm_name}-health-check" if config.health_check else None
                        backend = BackendConfig(
                            vm_name=vm_name,
                            zone=config.zone,
                            port=port,
                            health_check_name=health_check_name
                        )
                        self.config.backends.append(backend)
                else:
                    # Handle single VM
                    vm_name = vm_instance.vm_names[0]
                    config = vm_instance.configs[vm_name]
                    health_check_name = f"{vm_name}-health-check" if config.health_check else None
                    backend = BackendConfig(
                        vm_name=vm_name,
                        zone=config.zone,
                        port=port,
                        health_check_name=health_check_name
                    )
                    self.config.backends.append(backend)
                return self

            # Handle legacy formats
            elif isinstance(args[0], dict) and "name" in args[0] and "zone" in args[0]:
                vm_info = args[0]
                vm_name = vm_info["name"]
                zone = vm_info["zone"]
                port = kwargs.get("port", 80)
                health_check_name = vm_info.get("health_check")
            else:
                vm_name = args[0]
                zone = args[1]
                port = args[2] if len(args) > 2 else 80
                health_check_name = args[3] if len(args) > 3 else None
        else:
            raise ValueError("backend() requires at least a vm_name and zone or a VM object.")

        backend = BackendConfig(vm_name=vm_name, zone=zone, port=port, health_check_name=health_check_name)
        self.config.backends.append(backend)
        return self

    def backend_group(self, vm_group: VmGroup) -> 'LoadBalancer':
        """Add a VM group as backends"""
        if not isinstance(vm_group, VmGroup):
            raise TypeError("backend_group expects a VmGroup object")

        for vm in vm_group.vms:
            health_check_name = f"{vm.config.name}-health-check" if vm.config.health_check else None

            backend = BackendConfig(
                vm_name=vm.config.name,
                zone=vm.config.zone,
                port=80,
                health_check_name=health_check_name
            )
            self.config.backends.append(backend)

        print(f"✅ Added {len(vm_group.vms)} VMs from group '{vm_group.group_name}' to the load balancer backend.")
        return self

    def ssl_certificate(self, certificate_name: str) -> 'LoadBalancer':
        """Set the SSL certificate for the load balancer"""
        self.config.ssl_certificate = certificate_name
        return self

    def domain(self, domain: str) -> 'LoadBalancer':
        """Configure domain for the load balancer"""
        self.config.domain = domain
        return self

    def port(self, port: int) -> 'LoadBalancer':
        """Set the HTTP port (default: 80)"""
        self.config.port = port
        return self

    def ssl_port(self, port: int) -> 'LoadBalancer':
        """Set the HTTPS port (default: 443)"""
        self.config.ssl_port = port
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        if not self.config.backends:
            raise ValueError("At least one backend is required")

        # Discover existing load balancers
        existing_load_balancers = self._discover_existing_load_balancers()
        
        # Categorize load balancers
        lbs_to_create = []
        lbs_to_keep = []
        lbs_to_remove = []
        
        # Check if our desired load balancer exists
        desired_lb_name = self.config.name
        lb_exists = desired_lb_name in existing_load_balancers
        
        if not lb_exists:
            lbs_to_create.append({
                'lb_name': desired_lb_name,
                'port': self.config.port,
                'ssl_port': self.config.ssl_port,
                'backends': self.config.backends,
                'backend_count': len(self.config.backends),
                'ssl_certificate': self.config.ssl_certificate,
                'domain': self.config.domain
            })
        else:
            lbs_to_keep.append(existing_load_balancers[desired_lb_name])

        print(f"\n🌐 Google Cloud Load Balancer Configuration Preview")
        
        # Show load balancers to create
        if lbs_to_create:
            print(f"╭─ 🌐 Load Balancers to CREATE: {len(lbs_to_create)}")
            for lb in lbs_to_create:
                print(f"├─ 🆕 {lb['lb_name']}")
                print(f"│  ├─ 🔌 HTTP Port: {lb['port']}")
                print(f"│  ├─ 🔒 HTTPS Port: {lb['ssl_port']}")
                print(f"│  ├─ 🖥️  Backends: {lb['backend_count']}")
                
                if lb['backends']:
                    print(f"│  ├─ 📋 Backend Details:")
                    for i, backend in enumerate(lb['backends'][:5]):  # Show first 5 backends
                        connector = "│  │  ├─" if i < min(len(lb['backends']), 5) - 1 else "│  │  └─"
                        print(f"{connector} {backend.vm_name} ({backend.zone}:{backend.port})")
                        if backend.health_check_name:
                            print(f"│  │     └─ Health Check: {backend.health_check_name}")
                    if len(lb['backends']) > 5:
                        print(f"│  │     └─ ... and {len(lb['backends']) - 5} more backends")
                
                if lb['ssl_certificate']:
                    print(f"│  ├─ 🔐 SSL Certificate: {lb['ssl_certificate']}")
                
                if lb['domain']:
                    print(f"│  ├─ 🌍 Domain: {lb['domain']}")
                
                print(f"│  └─ ⚡ Traffic Distribution: Round-robin")
            print(f"╰─")

        # Show existing load balancers being kept
        if lbs_to_keep:
            print(f"\n╭─ 🌐 Existing Load Balancers to KEEP: {len(lbs_to_keep)}")
            for lb in lbs_to_keep:
                print(f"├─ ✅ {lb['lb_name']}")
                print(f"│  ├─ 🌍 IP Address: {lb['ip_address']}")
                print(f"│  ├─ 🔌 Port Range: {lb['port_range']}")
                print(f"│  ├─ 📊 Protocol: {lb['protocol']}")
                print(f"│  ├─ 🖥️  Backends: {lb['backend_count']}")
                
                if lb['backends']:
                    print(f"│  ├─ 📋 Active Backends:")
                    for i, backend in enumerate(lb['backends'][:3]):  # Show first 3 backends
                        connector = "│  │  ├─" if i < min(len(lb['backends']), 3) - 1 else "│  │  └─"
                        if backend['type'] == 'instance':
                            print(f"{connector} {backend['vm_name']} ({backend['zone']})")
                        else:
                            print(f"{connector} {backend['group_name']} ({backend['zone']}) [group]")
                
                if lb.get('health_checks'):
                    print(f"│  ├─ 🏥 Health Checks: {len(lb['health_checks'])}")
                
                print(f"│  ├─ 📡 Scheme: {lb['load_balancing_scheme']}")
                print(f"│  ├─ 🌐 Network Tier: {lb['network_tier']}")
                print(f"│  └─ 📅 Created: {lb.get('creation_timestamp', 'Unknown')}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        if lbs_to_create:
            lb = lbs_to_create[0]
            print(f"   ├─ 🌐 Load Balancer: $22.27/month (744 hours)")
            print(f"   ├─ 📊 Forwarding Rules: $0.025/hour × {1} = $18.60/month")
            print(f"   ├─ 🔍 Health Checks: $0.50/month × {len([b for b in lb['backends'] if hasattr(b, 'health_check_name') and b.health_check_name])}")
            if lb['ssl_certificate']:
                print(f"   ├─ 🔐 SSL Certificate: $0.75/month")
            print(f"   ├─ 📈 Data Processing: $0.008/GB (first 1TB free)")
            print(f"   └─ 📊 Total: ~$40-60/month")
        else:
            print(f"   ├─ 🌐 Load Balancer: $22.27/month")
            print(f"   ├─ 📊 Forwarding Rules: $18.60/month")
            print(f"   ├─ 🔍 Health Checks: $0.50/month each")
            print(f"   └─ 📈 Data Processing: $0.008/GB")

        return {
            'resource_type': 'gcp_load_balancer',
            'name': desired_lb_name,
            'lbs_to_create': lbs_to_create,
            'lbs_to_keep': lbs_to_keep,
            'lbs_to_remove': lbs_to_remove,
            'existing_load_balancers': existing_load_balancers,
            'lb_name': desired_lb_name,
            'port': self.config.port,
            'ssl_port': self.config.ssl_port,
            'backend_count': len(self.config.backends),
            'estimated_cost': f"$40-60/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create the load balancer with smart state management"""
        self._ensure_authenticated()

        if not self.config.backends:
            raise ValueError("At least one backend is required")

        # Discover existing load balancers first
        existing_load_balancers = self._discover_existing_load_balancers()
        
        # Determine what changes need to be made
        desired_lb_name = self.config.name
        
        # Check for load balancers to remove (not in current configuration)
        lbs_to_remove = []
        for lb_name, lb_info in existing_load_balancers.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which load balancers should be removed based on configuration
            # For now, we'll focus on creating the desired load balancer
            pass
        
        # Remove load balancers no longer in configuration
        if lbs_to_remove:
            print(f"\n🗑️  Removing load balancers no longer in configuration:")
            for lb_info in lbs_to_remove:
                print(f"╭─ 🔄 Removing load balancer: {lb_info['lb_name']}")
                print(f"├─ 🌍 IP Address: {lb_info['ip_address']}")
                print(f"├─ 🔌 Port Range: {lb_info['port_range']}")
                print(f"├─ 🖥️  Backends: {lb_info['backend_count']}")
                print(f"└─ ⚠️  Load balancer and all traffic routing will be permanently deleted")
                
                # In real implementation:
                # self.load_balancer_manager.delete_load_balancer(lb_info['lb_name'])

        # Check if our desired load balancer already exists
        lb_exists = desired_lb_name in existing_load_balancers
        if lb_exists:
            existing_lb = existing_load_balancers[desired_lb_name]
            print(f"\n🔄 Load balancer '{desired_lb_name}' already exists")
            print(f"   🌍 IP Address: {existing_lb['ip_address']}")
            print(f"   🔌 Port Range: {existing_lb['port_range']}")
            print(f"   🖥️  Backends: {existing_lb['backend_count']}")
            
            # In a real implementation, we would:
            # 1. Compare existing backends with desired backends
            # 2. Update backend configurations if needed
            # 3. Update health checks and SSL certificates
            
            result = {
                'lb_name': existing_lb['lb_name'],
                'ip_address': existing_lb['ip_address'],
                'port_range': existing_lb['port_range'],
                'backend_count': existing_lb['backend_count'],
                'existing': True
            }
            if len(lbs_to_remove) > 0:
                result['changes'] = True
            return result

        print(f"\n🌐 Creating load balancer: {desired_lb_name}")
        print(f"   🔌 HTTP Port: {self.config.port}")
        print(f"   🔒 HTTPS Port: {self.config.ssl_port}")
        print(f"   🖥️  Backends: {len(self.config.backends)}")

        try:
            result = self.load_balancer_manager.create_load_balancer(self.config)
            if result is None:
                print(f"❌ Failed to create load balancer: Backend service creation failed")
                raise Exception("Failed to create load balancer: Backend service creation failed")
            
            print(f"\n✅ Load balancer created successfully!")
            print(f"   🌐 Name: {result.get('name', desired_lb_name)}")
            print(f"   🌍 IP Address: {result['ip_address']}")
            print(f"   🔌 Ports: HTTP:{self.config.port}, HTTPS:{self.config.ssl_port}")
            print(f"   🖥️  Backends: {len(self.config.backends)} configured")
            print(f"   ⚡ Traffic Distribution: Round-robin")
            
            if len(lbs_to_remove) > 0:
                result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")

            return result
        except Exception as e:
            print(f"❌ Failed to create load balancer: {e}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the load balancer"""
        self._ensure_authenticated()

        print(f"🗑️  Destroying load balancer: {self.name}")

        try:
            success = self.load_balancer_manager.delete_load_balancer(self.name)
            if success:
                print(f"✅ Load balancer deleted: {self.name}")
            else:
                print(f"⚠️  Warning: Failed to delete load balancer: {self.name}")
            return {"success": success, "name": self.name}
        except Exception as e:
            print(f"❌ Failed to delete load balancer: {e}")
            return {"success": False, "name": self.name, "error": str(e)}

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the load balancer from Google Cloud"""
        self._ensure_authenticated()
        
        existing_load_balancers = self._discover_existing_load_balancers()
        
        if self.name in existing_load_balancers:
            return existing_load_balancers[self.name]
        
        return {"status": "not_found", "name": self.name}


def create_load_balancer(name: str) -> LoadBalancer:
    """Create a new standalone load balancer definition"""
    return LoadBalancer(name)
