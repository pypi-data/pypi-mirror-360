from typing import TYPE_CHECKING, List, Optional
from google.cloud import compute_v1

if TYPE_CHECKING:
    from ..vm import Vm
    from ...googlecloud_managers.firewall_manager import FirewallRule

class FirewallManagementMixin:
    """Mixin for firewall rule management"""
    
    def firewall(self: 'Vm', name: str, source_ranges_or_port, protocol_or_port: Optional[str] = None, source_ranges: Optional[List[str]] = None) -> 'Vm':
        """Add a firewall rule for this VM
        
        Supports multiple calling patterns:
        - firewall("allow-http", 80, "tcp", ["0.0.0.0/0"])
        - firewall("allow-http", "0.0.0.0/0", "tcp:80")
        """
        from ...googlecloud_managers.firewall_manager import FirewallRule
        
        # Parse the calling pattern
        if isinstance(source_ranges_or_port, int):
            # Pattern: firewall("allow-http", 80, "tcp", ["0.0.0.0/0"])
            port = source_ranges_or_port
            protocol = protocol_or_port or "tcp"
            ranges = source_ranges or ["0.0.0.0/0"]
        else:
            # Pattern: firewall("allow-http", "0.0.0.0/0", "tcp:80")
            ranges = [source_ranges_or_port] if source_ranges_or_port else ["0.0.0.0/0"]
            if protocol_or_port and ":" in protocol_or_port:
                protocol, port_str = protocol_or_port.split(":", 1)
                port = int(port_str)
            else:
                protocol = protocol_or_port or "tcp"
                port = 80  # Default port
        
        self.firewall_rules.append(FirewallRule(name, port, protocol, ranges))
        return self

    def _smart_update_firewall_rules_for_vm(self: 'Vm', vm_name: str, config):
        """Intelligently manage firewall rules for a specific VM - Rails-like state management"""
        try:
            # Get existing firewall rules for this VM
            existing_rules = self._get_existing_firewall_rules_for_vm(vm_name)
            desired_rules = {f"{vm_name}-{rule.name}": rule for rule in self.firewall_rules}

            print(f"🔍 Analyzing firewall rules for {vm_name}...")
            print(f"   📋 Current rules: {len(existing_rules)}")
            print(f"   📋 Desired rules: {len(desired_rules)}")

            changes_made = []

            # Create new rules that don't exist
            for rule_name, rule in desired_rules.items():
                if rule_name not in existing_rules:
                    try:
                        self.firewall_manager.create_firewall_rules(vm_name, config.zone, [rule])
                        print(f"   ➕ Created firewall rule: {rule.name}")
                        changes_made.append(f"created {rule.name}")
                    except Exception as e:
                        print(f"   ⚠️  Warning: Failed to create firewall rule {rule.name}: {str(e)}")

            # Remove rules that are no longer needed
            for existing_rule_name in existing_rules:
                if existing_rule_name not in desired_rules:
                    try:
                        success = self._delete_firewall_rule(existing_rule_name)
                        if success:
                            print(f"   🗑️  Removed firewall rule: {existing_rule_name}")
                            changes_made.append(f"removed {existing_rule_name}")
                    except Exception as e:
                        print(f"   ⚠️  Warning: Failed to remove firewall rule {existing_rule_name}: {str(e)}")

            if changes_made:
                print(f"🎯 Firewall update complete for {vm_name}! Changes: {', '.join(changes_made)}")
            else:
                print(f"✅ Firewall rules for {vm_name} already match desired state")

        except Exception as e:
            print(f"⚠️  Warning: Failed to update firewall rules for {vm_name}: {str(e)}")

    def _get_existing_firewall_rules_for_vm(self: 'Vm', vm_name: str) -> dict:
        """Get existing firewall rules for a specific VM"""
        try:
            # Get all firewall rules that match our VM naming pattern
            existing_rules = {}

            # Use the firewall client to list all firewalls
            request = compute_v1.ListFirewallsRequest(project=self.gcp_client.project)
            firewalls = self.firewall_manager.firewall_client.list(request=request)

            vm_rule_prefix = f"{vm_name}-"
            for firewall in firewalls:
                if firewall.name.startswith(vm_rule_prefix):
                    existing_rules[firewall.name] = firewall

            return existing_rules

        except Exception as e:
            print(f"   ⚠️  Warning: Failed to get existing firewall rules for {vm_name}: {str(e)}")
            return {}

    def _delete_firewall_rule(self: 'Vm', firewall_name: str) -> bool:
        """Delete a single firewall rule"""
        try:
            request = compute_v1.DeleteFirewallRequest(
                project=self.gcp_client.project,
                firewall=firewall_name
            )
            operation = self.firewall_manager.firewall_client.delete(request=request)
            print(f"   🗑️  Firewall rule deletion initiated: {firewall_name}")
            return True
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete firewall rule {firewall_name}: {str(e)}")
            return False 