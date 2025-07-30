import time
from typing import Dict, Any, Optional, List
from google.cloud import compute_v1
from .gcp_client import GcpClient

class FirewallRule:
    """Represents a firewall rule configuration"""
    def __init__(self, name: str, port: int, protocol: str = "tcp", source_ranges: List[str] = None):
        self.name = name
        self.port = port
        self.protocol = protocol
        self.source_ranges = source_ranges or ["0.0.0.0/0"]

class GcpFirewallManager:
    """Manages Google Cloud firewall operations"""
    
    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._project_id = None
        self._firewall_client = None
    
    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id
    
    @property
    def firewall_client(self):
        """Get the firewall client (lazy loading after authentication)"""
        if not self._firewall_client:
            self._firewall_client = compute_v1.FirewallsClient(credentials=self.gcp_client.credentials)
        return self._firewall_client
    
    def create_firewall_rules(self, vm_name: str, vm_zone: str, rules: List[FirewallRule]) -> List[str]:
        """Create firewall rules for a VM"""
        if not rules:
            return []
        
        firewall_ids = []
        
        for rule in rules:
            firewall_name = f"{vm_name}-{rule.name}"
            
            # Check if firewall already exists
            existing_firewall = self._get_firewall(firewall_name)
            if existing_firewall:
                print(f"🔄 Using existing firewall: {firewall_name}")
                firewall_ids.append(existing_firewall.name)
                continue
            
            print(f"🔥 Creating firewall rule: {firewall_name}")
            
            # Create firewall rule
            firewall = compute_v1.Firewall()
            firewall.name = firewall_name
            firewall.network = f"projects/{self.project_id}/global/networks/default"
            firewall.direction = "INGRESS"
            firewall.priority = 1000
            
            # Configure allowed rules
            allowed = compute_v1.Allowed()
            allowed.I_p_protocol = rule.protocol
            allowed.ports = [str(rule.port)]
            firewall.allowed = [allowed]
            
            # Configure source ranges
            firewall.source_ranges = rule.source_ranges
            
            # Add target tags if VM has tags
            vm_tags = self._get_vm_tags(vm_name, vm_zone)
            if vm_tags:
                firewall.target_tags = vm_tags
            
            # Create the firewall
            request = compute_v1.InsertFirewallRequest(
                project=self.project_id,
                firewall_resource=firewall
            )
            
            try:
                operation = self.firewall_client.insert(request=request)
                print(f"   ⏳ Creating firewall rule...")
                
                # Small delay to allow operation to start
                time.sleep(1)
                
                # Wait for operation to complete (brief wait)
                self._wait_for_firewall_operation(operation)
                
                print(f"   ✅ Firewall rule created: {firewall_name}")
                firewall_ids.append(firewall_name)
                
            except Exception as e:
                print(f"   ⚠️  Warning: Failed to create firewall rule {firewall_name}: {e}")
        
        return firewall_ids
    
    def delete_firewall_rules(self, vm_name: str) -> bool:
        """Delete firewall rules associated with a VM"""
        try:
            # List all firewalls and find ones associated with this VM
            request = compute_v1.ListFirewallsRequest(project=self.project_id)
            firewalls = self.firewall_client.list(request=request)
            
            deleted_count = 0
            for firewall in firewalls:
                if firewall.name.startswith(f"{vm_name}-"):
                    print(f"🗑️  Deleting firewall rule: {firewall.name}")
                    
                    delete_request = compute_v1.DeleteFirewallRequest(
                        project=self.project_id,
                        firewall=firewall.name
                    )
                    
                    try:
                        operation = self.firewall_client.delete(request=delete_request)
                        self._wait_for_firewall_operation(operation)
                        print(f"   ✅ Firewall rule deleted: {firewall.name}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Warning: Failed to delete firewall rule {firewall.name}: {e}")
            
            if deleted_count > 0:
                print(f"✅ Deleted {deleted_count} firewall rules for VM: {vm_name}")
            else:
                print(f"✅ No firewall rules found for VM: {vm_name}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete firewall rules: {e}")
            return False
    
    def _get_firewall(self, firewall_name: str) -> Optional[compute_v1.Firewall]:
        """Get firewall by name"""
        try:
            request = compute_v1.GetFirewallRequest(
                project=self.project_id,
                firewall=firewall_name
            )
            return self.firewall_client.get(request=request)
        except Exception:
            return None
    
    def _get_vm_tags(self, vm_name: str, vm_zone: str) -> Optional[List[str]]:
        """Get tags from a VM instance"""
        try:
            from .vm_manager import VmManager
            vm_manager = VmManager(self.gcp_client)
            vm_info = vm_manager.get_vm_info(vm_name, vm_zone)
            if vm_info and 'tags' in vm_info:
                return vm_info['tags']
        except Exception:
            pass
        return None
    
    def _wait_for_firewall_operation(self, operation, timeout: int = 180):
        """Wait for firewall operation to complete"""
        try:
            print(f"         ⏳ Waiting for firewall operation to complete (timeout: {timeout}s)...")
            result = operation.result(timeout=timeout)
            
            if operation.error_code:
                print(f"   ❌ Firewall operation failed: [Code: {operation.error_code}] {operation.error_message}")
                raise operation.exception() or RuntimeError(operation.error_message)
            
            if operation.warnings:
                print(f"   ⚠️  Warnings during firewall operation:")
                for warning in operation.warnings:
                    print(f"      - {warning.code}: {warning.message}")
            
            print(f"         ✅ Firewall operation completed successfully")
            return result

        except Exception as e:
            print(f"         ⏰ Timeout waiting for firewall operation (after {timeout}s)")
            print(f"         💡 You can check the operation status manually:")
            print(f"         💡 gcloud compute operations describe {operation.name} --global")
            raise e