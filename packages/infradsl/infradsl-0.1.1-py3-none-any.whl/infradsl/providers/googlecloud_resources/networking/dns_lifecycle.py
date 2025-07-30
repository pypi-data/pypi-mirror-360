"""
GCP Cloud DNS Lifecycle Mixin

Lifecycle operations for Google Cloud DNS zones.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class DNSLifecycleMixin:
    """
    Mixin for DNS zone lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - State comparison and drift detection
    """
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created, kept, and removed.
        
        Returns:
            Dict containing preview information and cost estimates
        """
        self._ensure_authenticated()
        
        # Validate configuration
        if not self.dns_name:
            raise ValueError("Domain name is required. Use .domain('example.com') to set it.")
            
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_dns_actions(current_state)
        
        # Display preview
        self._display_dns_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_cloud_dns',
            'name': self.zone_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_dns_cost(),
            'configuration': self._get_dns_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the DNS zone with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        if not self.dns_name:
            raise ValueError("Domain name is required. Use .domain('example.com') to set it.")
            
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_dns_actions(current_state)
        
        # Execute actions
        result = self._execute_dns_actions(actions, current_state)
        
        # Update state
        self.zone_exists = True
        self.zone_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the DNS zone and all associated records.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying DNS zone: {self.zone_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  DNS zone '{self.zone_name}' does not exist")
                return {"success": True, "message": "DNS zone does not exist", "name": self.zone_name}
            
            # Show what will be destroyed
            self._display_dns_destruction_preview(current_state)
            
            # Perform destruction
            if self.dns_manager:
                success = self.dns_manager.delete_zone(self.zone_name)
                
                if success:
                    print(f"✅ DNS zone '{self.zone_name}' destroyed successfully")
                    self.zone_exists = False
                    self.zone_created = False
                    return {"success": True, "name": self.zone_name}
                else:
                    print(f"❌ Failed to destroy DNS zone '{self.zone_name}'")
                    return {"success": False, "name": self.zone_name, "error": "Destruction failed"}
            else:
                print(f"❌ DNS manager not available")
                return {"success": False, "name": self.zone_name, "error": "Manager not initialized"}
                
        except Exception as e:
            print(f"❌ Error destroying DNS zone: {str(e)}")
            return {"success": False, "name": self.zone_name, "error": str(e)}
            
    def add_records(self) -> Dict[str, Any]:
        """
        Add DNS records to existing zone without creating the zone.
        
        Returns:
            Dict containing record addition results
        """
        self._ensure_authenticated()
        
        if not self.dns_name:
            raise ValueError("Domain name is required. Use .domain('example.com') to set it.")
            
        if not self.dns_records:
            print("⚠️  No DNS records to add")
            return {"success": True, "message": "No records to add", "records_added": 0}
        
        print(f"\\n📋 Adding DNS records to zone: {self.zone_name}")
        
        try:
            # Add records through manager
            if self.dns_manager:
                result = self.dns_manager.add_records(self.zone_name, self.dns_records)
                
                print(f"✅ Successfully added {len(self.dns_records)} DNS records")
                return {
                    "success": True,
                    "name": self.zone_name,
                    "records_added": len(self.dns_records),
                    "records": [record.to_dict() for record in self.dns_records]
                }
            else:
                raise Exception("DNS manager not available")
                
        except Exception as e:
            print(f"❌ Failed to add DNS records: {str(e)}")
            raise
            
    def _determine_dns_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_zone": False,
            "update_zone": False,
            "keep_zone": False,
            "create_records": [],
            "update_records": [],
            "delete_records": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_zone"] = True
            actions["create_records"] = self.dns_records
            actions["changes"].append("Create new DNS zone")
            actions["changes"].append(f"Create {len(self.dns_records)} DNS records")
        else:
            # Compare current state with desired state
            zone_changes = self._detect_zone_configuration_drift(current_state)
            record_changes = self._detect_record_drift(current_state)
            
            if zone_changes:
                actions["update_zone"] = True
                actions["changes"].extend(zone_changes)
            else:
                actions["keep_zone"] = True
                
            if record_changes:
                actions["create_records"] = record_changes.get("create", [])
                actions["update_records"] = record_changes.get("update", [])
                actions["delete_records"] = record_changes.get("delete", [])
                
                if record_changes.get("create"):
                    actions["changes"].append(f"Create {len(record_changes['create'])} new records")
                if record_changes.get("update"):
                    actions["changes"].append(f"Update {len(record_changes['update'])} existing records")
                if record_changes.get("delete"):
                    actions["changes"].append(f"Delete {len(record_changes['delete'])} obsolete records")
                    
            if not actions["changes"]:
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_zone_configuration_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired zone configuration"""
        changes = []
        
        # Check description
        if current_state.get("description") != self.dns_description:
            changes.append(f"Description: '{current_state.get('description')}' → '{self.dns_description}'")
            
        # Check visibility
        if current_state.get("visibility") != self.dns_visibility:
            changes.append(f"Visibility: {current_state.get('visibility')} → {self.dns_visibility}")
            
        # Check DNSSEC
        current_dnssec = current_state.get("dnssec_enabled", False)
        if current_dnssec != self.dnssec_enabled:
            changes.append(f"DNSSEC: {current_dnssec} → {self.dnssec_enabled}")
            
        # Check VPC networks for private zones
        if self.dns_visibility == "private":
            current_vpcs = set(current_state.get("vpc_networks", []))
            desired_vpcs = set(self.vpc_networks)
            if current_vpcs != desired_vpcs:
                changes.append(f"VPC networks: {len(current_vpcs)} → {len(desired_vpcs)}")
                
        return changes
        
    def _detect_record_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired DNS records"""
        current_records = current_state.get("records", [])
        desired_records = self.dns_records
        
        # Create lookup dictionaries
        current_lookup = {f"{r['name']}-{r['type']}": r for r in current_records}
        desired_lookup = {f"{r.name}-{r.record_type}": r for r in desired_records}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find records to create (in desired but not in current)
        for key, record in desired_lookup.items():
            if key not in current_lookup:
                changes["create"].append(record)
            else:
                # Check if record needs updating
                current_record = current_lookup[key]
                if (current_record.get("ttl") != record.ttl or 
                    set(current_record.get("rrdatas", [])) != set(record.values)):
                    changes["update"].append(record)
                    
        # Find records to delete (in current but not in desired)
        for key, record in current_lookup.items():
            if key not in desired_lookup:
                # Only mark for deletion if it's not a system record (SOA, NS)
                if record.get("type") not in ["SOA", "NS"]:
                    changes["delete"].append(record)
                    
        return changes
        
    def _execute_dns_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_zone"]:
            return self._create_dns_zone()
        elif actions["update_zone"] or actions["create_records"] or actions["update_records"] or actions["delete_records"]:
            return self._update_dns_zone(current_state, actions)
        else:
            return self._keep_dns_zone(current_state)
            
    def _create_dns_zone(self) -> Dict[str, Any]:
        """Create a new DNS zone"""
        print(f"\\n🌐 Creating DNS zone: {self.zone_name}")
        print(f"   🌍 Domain: {self.dns_name}")
        print(f"   👁️  Visibility: {self.dns_visibility.title()}")
        print(f"   📝 Description: {self.dns_description}")
        print(f"   🔒 DNSSEC: {'Enabled' if self.dnssec_enabled else 'Disabled'}")
        print(f"   📋 Records: {len(self.dns_records)} to create")
        
        if self.dns_visibility == "private" and self.vpc_networks:
            print(f"   🔗 VPC Networks: {len(self.vpc_networks)} configured")
        
        try:
            # Create through manager
            if self.dns_manager:
                result = self.dns_manager.create_zone(
                    zone_name=self.zone_name,
                    dns_name=self.dns_name,
                    description=self.dns_description,
                    visibility=self.dns_visibility,
                    dnssec_enabled=self.dnssec_enabled,
                    vpc_networks=self.vpc_networks,
                    labels=self.dns_labels
                )
                
                if result:
                    # Add DNS records
                    records_result = []
                    if self.dns_records:
                        records_result = self.dns_manager.add_records(self.zone_name, self.dns_records)
                    
                    print(f"\\n✅ DNS zone created successfully!")
                    print(f"   🌐 Zone Name: {result.get('name', self.zone_name)}")
                    print(f"   🌍 Domain: {result.get('dnsName', self.dns_name)}")
                    print(f"   📋 Records: {len(records_result)} created")
                    
                    # Show name servers
                    name_servers = result.get('nameServers', [])
                    if name_servers:
                        print(f"   🔗 Name Servers:")
                        for ns in name_servers[:4]:  # Show first 4
                            print(f"      • {ns}")
                        if len(name_servers) > 4:
                            print(f"      ... and {len(name_servers) - 4} more")
                    
                    # Update internal state
                    self.name_servers = name_servers
                    
                    return {
                        "success": True,
                        "name": self.zone_name,
                        "dns_name": self.dns_name,
                        "name_servers": name_servers,
                        "records_created": len(records_result),
                        "visibility": self.dns_visibility,
                        "dnssec_enabled": self.dnssec_enabled,
                        "created": True
                    }
                else:
                    raise Exception("DNS zone creation failed")
            else:
                raise Exception("DNS manager not available")
                
        except Exception as e:
            print(f"❌ Failed to create DNS zone: {str(e)}")
            raise
            
    def _update_dns_zone(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing DNS zone"""
        print(f"\\n🔄 Updating DNS zone: {self.zone_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            # Update through manager
            if self.dns_manager:
                result = self.dns_manager.update_zone(
                    zone_name=self.zone_name,
                    current_config=current_state,
                    desired_config=self._get_dns_configuration_summary(),
                    record_changes={
                        "create": actions["create_records"],
                        "update": actions["update_records"],
                        "delete": actions["delete_records"]
                    }
                )
                
                print(f"✅ DNS zone updated successfully!")
                print(f"   🌐 Zone Name: {self.zone_name}")
                print(f"   🔄 Changes Applied: {len(actions['changes'])}")
                
                return {
                    "success": True,
                    "name": self.zone_name,
                    "changes_applied": len(actions["changes"]),
                    "updated": True
                }
            else:
                raise Exception("DNS manager not available")
                
        except Exception as e:
            print(f"❌ Failed to update DNS zone: {str(e)}")
            raise
            
    def _keep_dns_zone(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing DNS zone (no changes needed)"""
        print(f"\\n✅ DNS zone '{self.zone_name}' is up to date")
        print(f"   🌍 Domain: {current_state.get('dns_name', 'Unknown')}")
        print(f"   👁️  Visibility: {current_state.get('visibility', 'Unknown').title()}")
        print(f"   📋 Records: {current_state.get('records_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.zone_name,
            "dns_name": current_state.get('dns_name'),
            "records_count": current_state.get('records_count', 0),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_dns_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\\n🌐 Google Cloud DNS Preview")
        print(f"   🎯 Zone: {self.zone_name}")
        print(f"   🌍 Domain: {self.dns_name}")
        print(f"   👁️  Visibility: {self.dns_visibility.title()}")
        
        if actions["create_zone"]:
            print(f"\\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🌐 DNS Zone: {self.zone_name}")
            print(f"├─ 🌍 Domain: {self.dns_name}")
            print(f"├─ 📝 Description: {self.dns_description}")
            print(f"├─ 👁️  Visibility: {self.dns_visibility.title()}")
            print(f"├─ 🔒 DNSSEC: {'Enabled' if self.dnssec_enabled else 'Disabled'}")
            if self.dns_visibility == "private" and self.vpc_networks:
                print(f"├─ 🔗 VPC Networks: {len(self.vpc_networks)}")
            print(f"├─ 📋 Records: {len(self.dns_records)} to create")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_dns_cost()}")
            
            # Show sample records
            if self.dns_records:
                print(f"\\n📋 DNS Records to Create:")
                for i, record in enumerate(self.dns_records[:5]):  # Show first 5
                    values_str = ', '.join(record.values)
                    print(f"   {record.record_type:>6} {record.name:<35} → {values_str}")
                if len(self.dns_records) > 5:
                    print(f"   ... and {len(self.dns_records) - 5} more records")
            
        elif actions["update_zone"] or actions["create_records"] or actions["update_records"] or actions["delete_records"]:
            print(f"\\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🌐 DNS Zone: {self.zone_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_dns_cost()}")
            
        else:
            print(f"\\n╭─ ✅ WILL KEEP")
            print(f"├─ 🌐 DNS Zone: {self.zone_name}")
            print(f"├─ 🌍 Domain: {current_state.get('dns_name', 'Unknown')}")
            print(f"├─ 📋 Records: {current_state.get('records_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_dns_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  DNS Zone: {self.zone_name}")
        print(f"   🌍 Domain: {current_state.get('dns_name', 'Unknown')}")
        print(f"   📋 Records: {current_state.get('records_count', 0)}")
        print(f"   👁️  Visibility: {current_state.get('visibility', 'Unknown').title()}")
        print(f"   ⚠️  ALL DNS RESOLUTION WILL BE PERMANENTLY LOST")
        
    def _calculate_dns_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_dns_cost()
        
        # Add additional costs based on features
        total_cost = base_cost
        
        # Query cost (estimated based on traffic)
        estimated_queries = 1000000  # 1M queries per month
        query_cost = (estimated_queries / 1000000) * 0.40
        total_cost += query_cost
        
        # No additional cost for DNSSEC or private zones
        
        return f"${total_cost:.2f}/month"
        
    def _get_dns_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current DNS configuration"""
        return {
            "zone_name": self.zone_name,
            "dns_name": self.dns_name,
            "description": self.dns_description,
            "visibility": self.dns_visibility,
            "dnssec_enabled": self.dnssec_enabled,
            "dnssec_state": self.dnssec_state,
            "vpc_networks": self.vpc_networks,
            "labels": self.dns_labels,
            "logging_enabled": self.logging_enabled,
            "logging_config": self.logging_config,
            "default_ttl": self.default_ttl,
            "soa_ttl": self.soa_ttl,
            "ns_ttl": self.ns_ttl,
            "records_count": len(self.dns_records),
            "records": [record.to_dict() for record in self.dns_records]
        }
        
    def optimize_for(self, priority: str):
        """
        Use Cross-Cloud Magic to optimize for cost/performance/reliability/compliance
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        print(f"🎯 Cross-Cloud Magic: Optimizing DNS for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective DNS")
            # Use longer TTLs for cost savings
            if self.default_ttl < 3600:
                print("   💡 Increasing TTL to reduce query costs")
                self.default_ttl = 3600
            # Disable logging for cost savings
            if self.logging_enabled:
                print("   💡 Disabling query logging for cost savings")
                self.logging_enabled = False
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance DNS")
            # Use shorter TTLs for faster updates
            if self.default_ttl > 300:
                print("   💡 Reducing TTL for faster DNS propagation")
                self.default_ttl = 300
            # Enable DNS query logging for performance monitoring
            if not self.logging_enabled:
                print("   💡 Enabling query logging for performance monitoring")
                self.logging_enabled = True
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable DNS")
            # Enable DNSSEC for security
            if not self.dnssec_enabled:
                print("   💡 Enabling DNSSEC for enhanced security")
                self.dnssec_enabled = True
            # Use medium TTL for balance
            if self.default_ttl != 1800:
                print("   💡 Setting balanced TTL for reliability")
                self.default_ttl = 1800
            # Enable logging for monitoring
            if not self.logging_enabled:
                print("   💡 Enabling query logging for monitoring")
                self.logging_enabled = True
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant DNS")
            # Enable DNSSEC for compliance
            if not self.dnssec_enabled:
                print("   💡 Enabling DNSSEC for compliance")
                self.dnssec_enabled = True
            # Enable logging for audit trails
            if not self.logging_enabled:
                print("   💡 Enabling query logging for audit compliance")
                self.logging_enabled = True
            # Add compliance labels
            self.dns_labels.update({
                "compliance": "enabled",
                "audit": "required"
            })
            print("   💡 Added compliance labels")
            
        return self