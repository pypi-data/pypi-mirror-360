import time
from typing import Optional, List
from google.cloud import compute_v1
from .operations import OperationManager

class InstanceGroupManager:
    """Manages instance groups for load balancer backends"""
    
    def __init__(self, project_id: str, credentials, operation_manager: OperationManager = None):
        self.project_id = project_id
        self.credentials = credentials
        self.operation_manager = operation_manager or OperationManager(project_id, credentials)
        self._instance_groups_client = None
    
    @property
    def instance_groups_client(self):
        """Get the instance groups client"""
        if not self._instance_groups_client:
            self._instance_groups_client = compute_v1.InstanceGroupsClient(credentials=self.credentials)
        return self._instance_groups_client
    
    def create_instance_group(self, name: str, zone: str, vms: List[str] = None, port: int = None) -> str:
        """Create an instance group in the specified zone"""
        try:
            print(f"      🔧 Creating instance group: {name} in zone: {zone}")
            
            # Check if instance group already exists
            existing_group = self.get_instance_group(name, zone)
            if existing_group:
                print(f"      ✅ Instance group already exists: {name}")
                if port:
                    self.set_named_ports_on_instance_group(name, zone, port)
                return name
            
            # Create the instance group
            instance_group = compute_v1.InstanceGroup()
            instance_group.name = name
            instance_group.description = f"Instance group for load balancer backend: {name}"
            
            request = compute_v1.InsertInstanceGroupRequest(
                project=self.project_id,
                zone=zone,
                instance_group_resource=instance_group
            )
            
            operation = self.instance_groups_client.insert(request=request)
            print(f"      ⏳ Creating instance group...")
            
            # Wait for operation to complete
            self.operation_manager.wait_for_zone_operation(operation, zone, timeout=120)
            print(f"      ✅ Instance group created: {name}")
            
            # Set named port if provided
            if port:
                self.set_named_ports_on_instance_group(name, zone, port)

            # Add VMs if provided
            if vms:
                print(f"      🔄 Adding {len(vms)} VMs to instance group...")
                self.add_vms_to_instance_group(name, vms, zone)
            
            return name
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"      ✅ Instance group already exists: {name}")
                if port:
                    self.set_named_ports_on_instance_group(name, zone, port)
                return name
            print(f"      ❌ Failed to create instance group {name}: {e}")
            print(f"      💡 This might be due to:")
            print(f"         - Insufficient permissions")
            print(f"         - Invalid zone specification")
            print(f"         - Network connectivity issues")
            return None
    
    def add_vms_to_instance_group(self, name: str, vms: List[str], zone: str = None) -> bool:
        """Add VMs to an instance group"""
        try:
            print(f"         🔄 Adding {len(vms)} VMs to instance group: {name}")
            
            # Get the instance group to find its zone if not provided
            if not zone:
                # Try to find the instance group in common zones
                for common_zone in ['us-central1-a', 'us-central1-b', 'us-central1-c', 'us-east1-b', 'us-east1-c']:
                    group = self.get_instance_group(name, common_zone)
                    if group:
                        zone = common_zone
                        break
                
                if not zone:
                    print(f"         ❌ Could not find instance group {name} in common zones")
                    return False
            
            # Create the request to add instances
            instances = []
            for vm in vms:
                # Create proper InstanceReference object
                instance_ref = compute_v1.InstanceReference()
                instance_ref.instance = f"projects/{self.project_id}/zones/{zone}/instances/{vm}"
                instances.append(instance_ref)
            
            request = compute_v1.AddInstancesInstanceGroupRequest(
                project=self.project_id,
                zone=zone,
                instance_group=name,
                instance_groups_add_instances_request_resource=compute_v1.InstanceGroupsAddInstancesRequest(
                    instances=instances
                )
            )
            
            operation = self.instance_groups_client.add_instances(request=request)
            print(f"         ⏳ Adding VMs to instance group...")
            
            # Wait for operation to complete
            self.operation_manager.wait_for_zone_operation(operation, zone, timeout=60)
            print(f"         ✅ Successfully added {len(vms)} VMs to instance group: {name}")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower() or "already a member" in str(e).lower():
                print(f"         ✅ VMs are already in instance group: {name}")
                return True
            elif "not found" in str(e).lower():
                print(f"         ⚠️  Some VMs not found. They may still be being created.")
                print(f"         💡 This is normal - VMs will be added when they become available")
                return False
            else:
                print(f"         ❌ Failed to add VMs to instance group {name}: {e}")
                print(f"         💡 This might be due to:")
                print(f"            - VMs not yet created")
                print(f"            - VMs in different zones")
                print(f"            - Insufficient permissions")
                return False
    
    def set_named_ports_on_instance_group(self, name: str, zone: str, port: int, port_name: str = "http") -> bool:
        """Sets named ports on an instance group"""
        try:
            print(f"      🔧 Setting named port '{port_name}:{port}' on instance group: {name}")
            
            named_port = compute_v1.NamedPort()
            named_port.name = port_name
            named_port.port = port
            
            request = compute_v1.SetNamedPortsInstanceGroupRequest(
                project=self.project_id,
                zone=zone,
                instance_group=name,
                instance_groups_set_named_ports_request_resource=compute_v1.InstanceGroupsSetNamedPortsRequest(
                    named_ports=[named_port]
                )
            )
            
            operation = self.instance_groups_client.set_named_ports(request=request)
            print(f"      ⏳ Setting named port...")
            
            self.operation_manager.wait_for_zone_operation(operation, zone, timeout=60)
            print(f"      ✅ Named port set successfully on instance group: {name}")
            return True
        except Exception as e:
            # Don't error if the port is already set, just log it
            if "already has named port" in str(e).lower():
                print(f"      ✅ Named port already set on instance group: {name}")
                return True
            print(f"      ❌ Failed to set named port on instance group {name}: {e}")
            return False

    def get_instance_group(self, name: str, zone: str) -> Optional[compute_v1.InstanceGroup]:
        """Get an instance group by name and zone"""
        try:
            request = compute_v1.GetInstanceGroupRequest(
                project=self.project_id,
                zone=zone,
                instance_group=name
            )
            return self.instance_groups_client.get(request=request)
        except Exception:
            return None 