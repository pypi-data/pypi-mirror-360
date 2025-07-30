"""
GCP GKE Lifecycle Mixin

Lifecycle operations for Google Kubernetes Engine (GKE).
Handles create, destroy, and preview operations with smart state management.
"""

import time
from typing import Dict, Any, List, Optional


class GKELifecycleMixin:
    """
    Mixin for GKE lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Cluster scaling and upgrade operations
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
        self._validate_gke_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_gke_actions(current_state)
        
        # Display preview
        self._display_gke_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_gke',
            'name': self.cluster_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_gke_cost(),
            'configuration': self._get_gke_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the GKE cluster with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_gke_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_gke_actions(current_state)
        
        # Execute actions
        result = self._execute_gke_actions(actions, current_state)
        
        # Update state
        self.cluster_exists = True
        self.cluster_created = True
        self.cluster_ready = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the GKE cluster and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying GKE cluster: {self.cluster_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  GKE cluster '{self.cluster_name}' does not exist")
                return {"success": True, "message": "Cluster does not exist", "name": self.cluster_name}
            
            # Show what will be destroyed
            self._display_gke_destruction_preview(current_state)
            
            # Perform destruction
            destruction_results = []
            
            # 1. Scale down node pools first (graceful shutdown)
            print(f"📉 Scaling down node pools...")
            for pool in current_state.get("node_pools", []):
                if self.gke_manager:
                    result = self.gke_manager.scale_node_pool(
                        self.cluster_name, self.location, pool["name"], 0
                    )
                    destruction_results.append(("node_pool_scale", pool["name"], result))
            
            # Wait a moment for graceful shutdown
            time.sleep(10)
            
            # 2. Delete the GKE cluster
            if self.gke_manager:
                result = self.gke_manager.delete_cluster(self.cluster_name, self.location)
                destruction_results.append(("cluster", self.cluster_name, result))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ GKE cluster '{self.cluster_name}' destroyed successfully")
                self.cluster_exists = False
                self.cluster_created = False
                self.cluster_ready = False
                return {"success": True, "name": self.cluster_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying cluster. Failed: {failed_resources}")
                return {"success": False, "name": self.cluster_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying GKE cluster: {str(e)}")
            return {"success": False, "name": self.cluster_name, "error": str(e)}
            
    def scale(self, node_count: int, node_pool: str = "default-pool") -> Dict[str, Any]:
        """
        Scale cluster node pool to specific count.
        
        Args:
            node_count: Target number of nodes
            node_pool: Node pool name to scale
            
        Returns:
            Dict containing scaling results
        """
        self._ensure_authenticated()
        
        print(f"📊 Scaling node pool '{node_pool}' to {node_count} nodes...")
        
        try:
            if self.gke_manager:
                result = self.gke_manager.scale_node_pool(
                    self.cluster_name, self.location, node_pool, node_count
                )
                print(f"✅ Node pool scaled successfully to {node_count} nodes")
                return {"success": True, "node_pool": node_pool, "node_count": node_count}
            else:
                return {"success": False, "error": "GKE manager not available"}
                
        except Exception as e:
            print(f"❌ Failed to scale node pool: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def upgrade(self, kubernetes_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Upgrade cluster to newer Kubernetes version.
        
        Args:
            kubernetes_version: Target version, or None for latest
            
        Returns:
            Dict containing upgrade results
        """
        self._ensure_authenticated()
        
        version_info = f" to {kubernetes_version}" if kubernetes_version else " to latest"
        print(f"⬆️  Upgrading cluster {self.cluster_name}{version_info}...")
        
        try:
            if self.gke_manager:
                result = self.gke_manager.upgrade_cluster(
                    self.cluster_name, self.location, kubernetes_version
                )
                print(f"✅ Cluster upgrade initiated successfully")
                return {"success": True, "cluster": self.cluster_name, "version": kubernetes_version}
            else:
                return {"success": False, "error": "GKE manager not available"}
                
        except Exception as e:
            print(f"❌ Failed to upgrade cluster: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def get_credentials(self) -> Dict[str, Any]:
        """
        Get kubectl credentials for the cluster.
        
        Returns:
            Dict containing credential setup results
        """
        self._ensure_authenticated()
        
        try:
            if self.gke_manager:
                result = self.gke_manager.get_cluster_credentials(
                    self.cluster_name, self.location
                )
                print(f"✅ Credentials configured for cluster: {self.cluster_name}")
                return {"success": True, "cluster": self.cluster_name, "credentials": result}
            else:
                return {"success": False, "error": "GKE manager not available"}
                
        except Exception as e:
            print(f"❌ Failed to get credentials: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _validate_gke_configuration(self):
        """Validate the GKE configuration before creation"""
        errors = []
        warnings = []
        
        # Validate cluster name
        if not self.cluster_name:
            errors.append("Cluster name is required")
        
        # Validate location
        if not self.location:
            errors.append("Location is required")
        elif not self._is_valid_location(self.location):
            errors.append(f"Invalid location: {self.location}")
        
        # Validate machine type
        if not self._is_valid_machine_type(self.machine_type):
            errors.append(f"Invalid machine type: {self.machine_type}")
        
        # Validate node count
        if not (0 <= self.initial_node_count <= 1000):
            errors.append(f"Invalid initial node count: {self.initial_node_count}")
        
        # Validate auto-scaling configuration
        if self.auto_scaling_enabled:
            if self.min_node_count > self.max_node_count:
                errors.append(f"Min nodes ({self.min_node_count}) cannot exceed max nodes ({self.max_node_count})")
            
            if not (0 <= self.min_node_count <= 1000):
                errors.append(f"Invalid min node count: {self.min_node_count}")
                
            if not (1 <= self.max_node_count <= 1000):
                errors.append(f"Invalid max node count: {self.max_node_count}")
        
        # Validate Kubernetes version if specified
        if self.kubernetes_version and not self._is_valid_kubernetes_version(self.kubernetes_version):
            warnings.append(f"Kubernetes version format may be invalid: {self.kubernetes_version}")
        
        # Validate release channel
        if not self._is_valid_release_channel(self.release_channel):
            errors.append(f"Invalid release channel: {self.release_channel}")
        
        # Validate disk configuration
        if not (10 <= self.disk_size_gb <= 65536):
            errors.append(f"Invalid disk size: {self.disk_size_gb}GB")
        
        # Performance warnings
        if self.initial_node_count > 50:
            warnings.append(f"High initial node count ({self.initial_node_count}) will increase costs significantly")
        
        if self.machine_type.startswith("n2-") and self.disk_type == "pd-standard":
            warnings.append("N2 machine types perform better with SSD disks")
        
        # Security warnings
        if not self.enable_shielded_nodes:
            warnings.append("Shielded nodes disabled - consider enabling for enhanced security")
        
        if not self.enable_workload_identity and self.cluster_type == "standard":
            warnings.append("Workload Identity disabled - consider enabling for secure pod-to-GCP access")
        
        if not self.enable_network_policy:
            warnings.append("Network policy disabled - consider enabling for pod-to-pod security")
        
        # Private cluster warnings
        if self.enable_private_nodes and not self.master_ipv4_cidr_block:
            warnings.append("Private nodes enabled but no master CIDR specified")
        
        # Node pool validation
        for pool in self.node_pools:
            if not self._validate_node_pool_config(pool):
                errors.append(f"Invalid node pool configuration: {pool.get('name', 'unknown')}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_gke_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_cluster": False,
            "update_cluster": False,
            "keep_cluster": False,
            "scale_nodes": False,
            "upgrade_version": False,
            "add_node_pools": False,
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_cluster"] = True
            actions["changes"].append("Create new GKE cluster")
            
            if self.node_pools:
                actions["add_node_pools"] = True
                actions["changes"].append(f"Add {len(self.node_pools)} additional node pools")
        else:
            # Compare current state with desired state
            config_changes = self._detect_cluster_configuration_drift(current_state)
            scaling_changes = self._detect_scaling_drift(current_state)
            version_changes = self._detect_version_drift(current_state)
            node_pool_changes = self._detect_node_pool_drift(current_state)
            
            if config_changes:
                actions["update_cluster"] = True
                actions["changes"].extend(config_changes)
            
            if scaling_changes:
                actions["scale_nodes"] = True
                actions["changes"].extend(scaling_changes)
            
            if version_changes:
                actions["upgrade_version"] = True
                actions["changes"].extend(version_changes)
            
            if node_pool_changes:
                actions["add_node_pools"] = True
                actions["changes"].extend(node_pool_changes)
            
            if not actions["changes"]:
                actions["keep_cluster"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_cluster_configuration_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired cluster configuration"""
        changes = []
        
        # Compare node count
        current_nodes = current_state.get("current_node_count", 0)
        if current_nodes != self.initial_node_count:
            changes.append(f"Node count: {current_nodes} → {self.initial_node_count}")
        
        # Compare machine type (simplified check)
        current_machine_types = current_state.get("machine_types", [])
        if current_machine_types and self.machine_type not in current_machine_types:
            changes.append(f"Machine type: {current_machine_types[0] if current_machine_types else 'unknown'} → {self.machine_type}")
        
        # Compare monitoring/logging
        current_monitoring = current_state.get("monitoring_enabled", False)
        if current_monitoring != self.enable_cloud_monitoring:
            changes.append(f"Monitoring: {'enabled' if current_monitoring else 'disabled'} → {'enabled' if self.enable_cloud_monitoring else 'disabled'}")
        
        current_logging = current_state.get("logging_enabled", False)
        if current_logging != self.enable_cloud_logging:
            changes.append(f"Logging: {'enabled' if current_logging else 'disabled'} → {'enabled' if self.enable_cloud_logging else 'disabled'}")
        
        return changes
        
    def _detect_scaling_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences in auto-scaling configuration"""
        changes = []
        
        current_autoscaling = current_state.get("autoscaling", False)
        if current_autoscaling != self.auto_scaling_enabled:
            changes.append(f"Auto-scaling: {'enabled' if current_autoscaling else 'disabled'} → {'enabled' if self.auto_scaling_enabled else 'disabled'}")
        
        return changes
        
    def _detect_version_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences in Kubernetes version"""
        changes = []
        
        current_version = current_state.get("current_master_version", "")
        if self.kubernetes_version and current_version != self.kubernetes_version:
            changes.append(f"Kubernetes version: {current_version} → {self.kubernetes_version}")
        
        return changes
        
    def _detect_node_pool_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences in node pool configuration"""
        changes = []
        
        current_pools = len(current_state.get("node_pools", []))
        desired_pools = len(self.node_pools) + 1  # +1 for default pool
        
        if current_pools != desired_pools:
            changes.append(f"Node pools: {current_pools} → {desired_pools}")
        
        return changes
        
    def _execute_gke_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_cluster"]:
            return self._create_gke_cluster()
        elif actions["update_cluster"]:
            return self._update_gke_cluster(current_state, actions)
        else:
            return self._keep_gke_cluster(current_state)
            
    def _create_gke_cluster(self) -> Dict[str, Any]:
        """Create a new GKE cluster"""
        print(f"\n🚀 Creating GKE cluster: {self.cluster_name}")
        print(f"   📍 Location: {self.location}")
        print(f"   🖥️  Machine Type: {self.machine_type}")
        print(f"   📊 Initial Nodes: {self.initial_node_count}")
        
        if self.auto_scaling_enabled:
            print(f"   📈 Auto-scaling: {self.min_node_count}-{self.max_node_count} nodes")
        
        if self.preemptible_nodes:
            print(f"   💰 Preemptible nodes: Enabled (cost savings)")
        
        print(f"   ⚓ Kubernetes: {self.kubernetes_version or 'Latest'}")
        print(f"   🛡️  Security: {'Enhanced' if self.enable_shielded_nodes else 'Standard'}")
        print(f"   ⏳ This may take several minutes...")
        
        try:
            # Prepare cluster configuration
            cluster_config = self._build_cluster_config()
            
            # Create the cluster
            if self.gke_manager:
                result = self.gke_manager.create_cluster(cluster_config)
                
                print(f"\n✅ GKE cluster created successfully!")
                print(f"   🚀 Cluster: {self.cluster_name}")
                print(f"   📍 Location: {self.location}")
                print(f"   🔗 Endpoint: {result.get('endpoint', 'Unknown')}")
                print(f"   📊 Nodes: {result.get('node_count', 'Unknown')}")
                print(f"   ⚓ Version: {result.get('version', 'Unknown')}")
                print(f"   💰 Estimated Cost: {self._calculate_gke_cost()}")
                
                return {
                    "success": True,
                    "name": self.cluster_name,
                    "location": self.location,
                    "endpoint": result.get("endpoint"),
                    "node_count": result.get("node_count"),
                    "version": result.get("version"),
                    "estimated_cost": self._calculate_gke_cost(),
                    "created": True
                }
            else:
                raise RuntimeError("GKE manager not available")
                
        except Exception as e:
            print(f"❌ Failed to create GKE cluster: {str(e)}")
            raise
            
    def _update_gke_cluster(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing GKE cluster"""
        print(f"\n🔄 Updating GKE cluster: {self.cluster_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            results = []
            
            # Handle scaling changes
            if actions["scale_nodes"]:
                scale_result = self.scale(self.initial_node_count)
                results.append(("scale", scale_result))
            
            # Handle version upgrades
            if actions["upgrade_version"]:
                upgrade_result = self.upgrade(self.kubernetes_version)
                results.append(("upgrade", upgrade_result))
            
            # Handle node pool additions
            if actions["add_node_pools"]:
                for pool in self.node_pools:
                    if self.gke_manager:
                        pool_result = self.gke_manager.create_node_pool(
                            self.cluster_name, self.location, pool
                        )
                        results.append(("node_pool", pool_result))
            
            print(f"✅ GKE cluster updated successfully!")
            print(f"   🚀 Cluster: {self.cluster_name}")
            print(f"   🔄 Changes Applied: {len(actions['changes'])}")
            
            return {
                "success": True,
                "name": self.cluster_name,
                "changes_applied": len(actions["changes"]),
                "results": results,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update GKE cluster: {str(e)}")
            raise
            
    def _keep_gke_cluster(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing GKE cluster (no changes needed)"""
        print(f"\n✅ GKE cluster '{self.cluster_name}' is up to date")
        print(f"   🚀 Cluster: {self.cluster_name}")
        print(f"   📍 Location: {current_state.get('location', 'Unknown')}")
        print(f"   🔗 Endpoint: {current_state.get('endpoint', 'Unknown')}")
        print(f"   📊 Nodes: {current_state.get('current_node_count', 'Unknown')}")
        print(f"   ⚓ Version: {current_state.get('current_master_version', 'Unknown')}")
        print(f"   📈 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.cluster_name,
            "location": current_state.get('location'),
            "endpoint": current_state.get('endpoint'),
            "node_count": current_state.get('current_node_count'),
            "version": current_state.get('current_master_version'),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _build_cluster_config(self) -> Dict[str, Any]:
        """Build complete cluster configuration for creation"""
        config = {
            "name": self.cluster_name,
            "description": self.cluster_description,
            "location": self.location,
            "initial_node_count": self.initial_node_count,
            "machine_type": self.machine_type,
            "disk_size_gb": self.disk_size_gb,
            "disk_type": self.disk_type,
            "image_type": self.image_type,
            "kubernetes_version": self.kubernetes_version,
            "release_channel": self.release_channel,
            "network": self.network,
            "subnetwork": self.subnetwork,
            "enable_ip_alias": self.enable_ip_alias,
            "cluster_ipv4_cidr": self.cluster_ipv4_cidr,
            "services_ipv4_cidr": self.services_ipv4_cidr,
            "enable_private_nodes": self.enable_private_nodes,
            "enable_private_endpoint": self.enable_private_endpoint,
            "master_ipv4_cidr_block": self.master_ipv4_cidr_block,
            "enable_shielded_nodes": self.enable_shielded_nodes,
            "enable_workload_identity": self.enable_workload_identity,
            "enable_network_policy": self.enable_network_policy,
            "enable_cloud_logging": self.enable_cloud_logging,
            "enable_cloud_monitoring": self.enable_cloud_monitoring,
            "logging_service": self.logging_service,
            "monitoring_service": self.monitoring_service,
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "min_node_count": self.min_node_count,
            "max_node_count": self.max_node_count,
            "auto_upgrade": self.auto_upgrade,
            "auto_repair": self.auto_repair,
            "preemptible_nodes": self.preemptible_nodes,
            "spot_instances": self.spot_instances,
            "service_account": self.service_account,
            "oauth_scopes": self.oauth_scopes,
            "cluster_labels": self.cluster_labels,
            "node_labels": self.node_labels,
            "node_tags": self.node_tags,
            "node_taints": self.node_taints,
            "master_auth_networks": self.master_auth_networks,
            "enable_legacy_abac": self.enable_legacy_abac,
            "enable_pod_security_policy": self.enable_pod_security_policy,
            "http_load_balancing_disabled": self.http_load_balancing_disabled,
            "horizontal_pod_autoscaling_disabled": self.horizontal_pod_autoscaling_disabled,
            "kubernetes_dashboard_disabled": self.kubernetes_dashboard_disabled,
            "network_policy_config_disabled": self.network_policy_config_disabled,
            "dns_cache_config_enabled": self.dns_cache_config_enabled,
            "config_connector_config_enabled": self.config_connector_config_enabled,
            "maintenance_window": self.maintenance_window,
            "maintenance_exclusions": self.maintenance_exclusions,
            "node_pools": self.node_pools
        }
        
        return config
        
    def _display_gke_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n⚓ Google Kubernetes Engine Preview")
        print(f"   🎯 Cluster: {self.cluster_name}")
        print(f"   📍 Location: {self.location}")
        print(f"   🖥️  Machine Type: {self.machine_type}")
        print(f"   📊 Nodes: {self.initial_node_count}")
        
        if actions["create_cluster"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ ⚓ Cluster: {self.cluster_name}")
            print(f"├─ 📍 Location: {self.location} ({self.location_type})")
            print(f"├─ 🖥️  Machine Type: {self.machine_type}")
            print(f"├─ 📊 Initial Nodes: {self.initial_node_count}")
            print(f"├─ 💾 Disk: {self.disk_size_gb}GB {self.disk_type}")
            print(f"├─ ⚓ Kubernetes: {self.kubernetes_version or 'Latest'}")
            print(f"├─ 📈 Release Channel: {self.release_channel}")
            
            if self.auto_scaling_enabled:
                print(f"├─ 📈 Auto-scaling: {self.min_node_count}-{self.max_node_count} nodes")
            
            if self.preemptible_nodes:
                print(f"├─ 💰 Preemptible: Enabled (cost savings)")
            
            if self.enable_private_nodes:
                print(f"├─ 🔒 Private nodes: Enabled")
            
            if self.enable_shielded_nodes:
                print(f"├─ 🛡️  Shielded nodes: Enabled")
            
            if self.enable_workload_identity:
                print(f"├─ 🔐 Workload Identity: Enabled")
            
            if self.enable_network_policy:
                print(f"├─ 🌐 Network Policy: Enabled")
            
            if self.node_pools:
                print(f"├─ 📦 Additional Node Pools: {len(self.node_pools)}")
            
            print(f"╰─ 💰 Estimated Cost: {self._calculate_gke_cost()}")
            
        elif any([actions["update_cluster"], actions["scale_nodes"], actions["upgrade_version"], actions["add_node_pools"]]):
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ ⚓ Cluster: {self.cluster_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_gke_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ ⚓ Cluster: {self.cluster_name}")
            print(f"├─ 📍 Location: {current_state.get('location', 'Unknown')}")
            print(f"├─ 🔗 Endpoint: {current_state.get('endpoint', 'Unknown')}")
            print(f"├─ 📊 Nodes: {current_state.get('current_node_count', 'Unknown')}")
            print(f"├─ ⚓ Version: {current_state.get('current_master_version', 'Unknown')}")
            print(f"╰─ 📈 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_gke_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Cluster: {self.cluster_name}")
        print(f"   📍 Location: {current_state.get('location', 'Unknown')}")
        print(f"   🔗 Endpoint: {current_state.get('endpoint', 'Unknown')}")
        print(f"   📊 Nodes: {current_state.get('current_node_count', 'Unknown')}")
        print(f"   📦 Node Pools: {current_state.get('node_pools_count', 'Unknown')}")
        print(f"   ⚠️  ALL CLUSTER DATA AND WORKLOADS WILL BE PERMANENTLY LOST")
        print(f"   ⚠️  PERSISTENT VOLUMES AND DATA MAY BE DELETED")
        
    def _calculate_gke_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_gke_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_gke_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current GKE configuration"""
        return {
            "cluster_name": self.cluster_name,
            "description": self.cluster_description,
            "location": self.location,
            "location_type": self.location_type,
            "kubernetes_version": self.kubernetes_version,
            "release_channel": self.release_channel,
            "machine_type": self.machine_type,
            "initial_node_count": self.initial_node_count,
            "disk_size_gb": self.disk_size_gb,
            "disk_type": self.disk_type,
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "min_node_count": self.min_node_count,
            "max_node_count": self.max_node_count,
            "preemptible_nodes": self.preemptible_nodes,
            "spot_instances": self.spot_instances,
            "enable_private_nodes": self.enable_private_nodes,
            "enable_shielded_nodes": self.enable_shielded_nodes,
            "enable_workload_identity": self.enable_workload_identity,
            "enable_network_policy": self.enable_network_policy,
            "enable_cloud_monitoring": self.enable_cloud_monitoring,
            "enable_cloud_logging": self.enable_cloud_logging,
            "cluster_labels": self.cluster_labels,
            "node_pools_count": len(self.node_pools)
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing GKE for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective Kubernetes cluster")
            # Use cost-effective settings
            self.machine_type = "e2-medium"
            self.preemptible_nodes = True
            self.disk_type = "pd-standard"
            self.auto_scaling_enabled = True
            self.min_node_count = 1
            self.max_node_count = 5
            self.cluster_labels.update({"optimization": "cost"})
            print("   💡 Configured for preemptible nodes and minimal resources")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance Kubernetes cluster")
            # Use high-performance settings
            self.machine_type = "n2-standard-4"
            self.disk_type = "pd-ssd"
            self.auto_scaling_enabled = True
            self.min_node_count = 3
            self.max_node_count = 20
            self.enable_dns_cache = True
            self.cluster_labels.update({"optimization": "performance"})
            print("   💡 Configured for high-performance nodes and SSD storage")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable Kubernetes cluster")
            # Use reliability-focused settings
            self.location_type = "regional"  # Multi-zone
            self.machine_type = "n1-standard-4"
            self.auto_scaling_enabled = True
            self.min_node_count = 3
            self.max_node_count = 15
            self.auto_upgrade = True
            self.auto_repair = True
            self.cluster_labels.update({"optimization": "reliability"})
            print("   💡 Configured for multi-zone deployment and auto-repair")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant Kubernetes cluster")
            # Use security and compliance settings
            self.enable_shielded_nodes = True
            self.enable_workload_identity = True
            self.enable_network_policy = True
            self.enable_private_nodes = True
            self.enable_pod_security_policy = True
            self.enable_cloud_monitoring = True
            self.enable_cloud_logging = True
            self.cluster_labels.update({
                "optimization": "compliance",
                "security": "enhanced",
                "audit": "enabled"
            })
            print("   💡 Configured for enhanced security and compliance")
            
        return self