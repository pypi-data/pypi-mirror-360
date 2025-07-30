"""
GCP Load Balancer Lifecycle Mixin

Lifecycle operations for Google Cloud Load Balancers.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class LoadBalancerLifecycleMixin:
    """
    Mixin for Load Balancer lifecycle operations.
    
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
        if not self.backends:
            raise ValueError("At least one backend is required for load balancer")
            
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_actions(current_state)
        
        # Display preview
        self._display_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_load_balancer',
            'name': self.lb_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_estimated_cost(),
            'configuration': self._get_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the load balancer with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        if not self.backends:
            raise ValueError("At least one backend is required for load balancer")
            
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_actions(current_state)
        
        # Execute actions
        result = self._execute_actions(actions, current_state)
        
        # Update state
        self.lb_exists = True
        self.lb_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the load balancer and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying load balancer: {self.lb_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Load balancer '{self.lb_name}' does not exist")
                return {"success": True, "message": "Load balancer does not exist", "name": self.lb_name}
            
            # Show what will be destroyed
            self._display_destruction_preview(current_state)
            
            # Perform destruction
            if self.load_balancer_manager:
                success = self.load_balancer_manager.delete_load_balancer(self.lb_name)
                
                if success:
                    print(f"✅ Load balancer '{self.lb_name}' destroyed successfully")
                    self.lb_exists = False
                    self.lb_created = False
                    return {"success": True, "name": self.lb_name}
                else:
                    print(f"❌ Failed to destroy load balancer '{self.lb_name}'")
                    return {"success": False, "name": self.lb_name, "error": "Destruction failed"}
            else:
                print(f"❌ Load balancer manager not available")
                return {"success": False, "name": self.lb_name, "error": "Manager not initialized"}
                
        except Exception as e:
            print(f"❌ Error destroying load balancer: {str(e)}")
            return {"success": False, "name": self.lb_name, "error": str(e)}
            
    def _determine_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create": False,
            "update": False,
            "keep": False,
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create"] = True
            actions["changes"].append("Create new load balancer")
        else:
            # Compare current state with desired state
            changes = self._detect_configuration_drift(current_state)
            if changes:
                actions["update"] = True
                actions["changes"] = changes
            else:
                actions["keep"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_configuration_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired configuration"""
        changes = []
        
        # Check load balancer type
        if current_state.get("lb_type") != self.lb_type:
            changes.append(f"Load balancer type: {current_state.get('lb_type')} → {self.lb_type}")
            
        # Check scheme
        if current_state.get("scheme") != self.lb_scheme:
            changes.append(f"Scheme: {current_state.get('scheme')} → {self.lb_scheme}")
            
        # Check protocol
        if current_state.get("protocol") != self.lb_protocol:
            changes.append(f"Protocol: {current_state.get('protocol')} → {self.lb_protocol}")
            
        # Check backend count
        current_backend_count = current_state.get("backend_count", 0)
        desired_backend_count = len(self.backends)
        if current_backend_count != desired_backend_count:
            changes.append(f"Backend count: {current_backend_count} → {desired_backend_count}")
            
        # Check SSL certificate
        if current_state.get("ssl_certificate") != self.ssl_certificate:
            changes.append(f"SSL certificate: {current_state.get('ssl_certificate')} → {self.ssl_certificate}")
            
        # Check health check settings
        if current_state.get("health_check_path") != self.health_check_path:
            changes.append(f"Health check path: {current_state.get('health_check_path')} → {self.health_check_path}")
            
        return changes
        
    def _execute_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create"]:
            return self._create_load_balancer()
        elif actions["update"]:
            return self._update_load_balancer(current_state, actions["changes"])
        else:
            return self._keep_load_balancer(current_state)
            
    def _create_load_balancer(self) -> Dict[str, Any]:
        """Create a new load balancer"""
        print(f"\\n🌐 Creating load balancer: {self.lb_name}")
        print(f"   🔧 Type: {self._get_load_balancer_type_display()}")
        print(f"   🌍 Scheme: {self.lb_scheme}")
        print(f"   📡 Protocol: {self.lb_protocol}")
        print(f"   🔌 HTTP Port: {self.http_port}")
        print(f"   🔒 HTTPS Port: {self.https_port}")
        print(f"   🖥️  Backends: {len(self.backends)}")
        
        # Show backend details
        if self.backends:
            print(f"   📋 Backend Configuration:")
            for i, backend in enumerate(self.backends[:3]):  # Show first 3
                print(f"      {i+1}. {backend.get('name', 'Unknown')} ({backend.get('type', 'unknown')})")
            if len(self.backends) > 3:
                print(f"      ... and {len(self.backends) - 3} more backends")
        
        try:
            # Create through manager
            if self.load_balancer_manager:
                result = self.load_balancer_manager.create_load_balancer(
                    name=self.lb_name,
                    lb_type=self.lb_type,
                    scheme=self.lb_scheme,
                    protocol=self.lb_protocol,
                    region=self.lb_region,
                    backends=self.backends,
                    health_check_config={
                        "enabled": self.health_check_enabled,
                        "path": self.health_check_path,
                        "protocol": self.health_check_protocol,
                        "port": self.health_check_port
                    },
                    ssl_config={
                        "certificate": self.ssl_certificate,
                        "policy": self.ssl_policy,
                        "redirect_http_to_https": self.redirect_http_to_https
                    },
                    traffic_config={
                        "session_affinity": self.session_affinity,
                        "connection_draining_timeout": self.connection_draining_timeout,
                        "timeout_seconds": self.timeout_seconds
                    },
                    security_config={
                        "enable_cdn": self.enable_cdn,
                        "security_policy": self.security_policy,
                        "allowed_regions": self.allowed_regions
                    },
                    labels=self.lb_labels
                )
                
                if result:
                    print(f"\\n✅ Load balancer created successfully!")
                    print(f"   🌐 Name: {result.get('name', self.lb_name)}")
                    print(f"   🌍 Frontend IP: {result.get('frontend_ip', 'Pending')}")
                    print(f"   🔌 Ports: HTTP:{self.http_port}, HTTPS:{self.https_port}")
                    print(f"   🖥️  Backends: {len(self.backends)} configured")
                    print(f"   ⚡ Status: {result.get('status', 'Creating')}")
                    
                    # Update internal state
                    self.frontend_ip = result.get('frontend_ip')
                    self.backend_service_url = result.get('backend_service_url')
                    self.url_map_url = result.get('url_map_url')
                    self.target_proxy_url = result.get('target_proxy_url')
                    
                    return {
                        "success": True,
                        "name": self.lb_name,
                        "frontend_ip": self.frontend_ip,
                        "backend_count": len(self.backends),
                        "status": result.get('status', 'Creating'),
                        "created": True
                    }
                else:
                    raise Exception("Load balancer creation failed")
            else:
                raise Exception("Load balancer manager not available")
                
        except Exception as e:
            print(f"❌ Failed to create load balancer: {str(e)}")
            raise
            
    def _update_load_balancer(self, current_state: Dict[str, Any], changes: List[str]) -> Dict[str, Any]:
        """Update an existing load balancer"""
        print(f"\\n🔄 Updating load balancer: {self.lb_name}")
        print(f"   📋 Changes to apply:")
        for change in changes:
            print(f"      • {change}")
            
        try:
            # Update through manager
            if self.load_balancer_manager:
                result = self.load_balancer_manager.update_load_balancer(
                    name=self.lb_name,
                    current_config=current_state,
                    desired_config=self._get_configuration_summary()
                )
                
                print(f"✅ Load balancer updated successfully!")
                print(f"   🌐 Name: {self.lb_name}")
                print(f"   🔄 Changes Applied: {len(changes)}")
                
                return {
                    "success": True,
                    "name": self.lb_name,
                    "changes_applied": len(changes),
                    "updated": True
                }
            else:
                raise Exception("Load balancer manager not available")
                
        except Exception as e:
            print(f"❌ Failed to update load balancer: {str(e)}")
            raise
            
    def _keep_load_balancer(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing load balancer (no changes needed)"""
        print(f"\\n✅ Load balancer '{self.lb_name}' is up to date")
        print(f"   🌍 Frontend IP: {current_state.get('frontend_ip', 'Unknown')}")
        print(f"   🖥️  Backend Count: {current_state.get('backend_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.lb_name,
            "frontend_ip": current_state.get('frontend_ip'),
            "backend_count": current_state.get('backend_count', 0),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\\n🌐 Google Cloud Load Balancer Preview")
        print(f"   🎯 Load Balancer: {self.lb_name}")
        print(f"   🔧 Type: {self._get_load_balancer_type_display()}")
        print(f"   🌍 Scheme: {self.lb_scheme}")
        print(f"   📡 Protocol: {self.lb_protocol}")
        
        if actions["create"]:
            print(f"\\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🌐 Load Balancer: {self.lb_name}")
            print(f"├─ 🔌 HTTP Port: {self.http_port}")
            print(f"├─ 🔒 HTTPS Port: {self.https_port}")
            print(f"├─ 🖥️  Backends: {len(self.backends)}")
            if self.ssl_certificate:
                print(f"├─ 🔐 SSL Certificate: {self.ssl_certificate}")
            if self.enable_cdn:
                print(f"├─ 🚀 CDN: Enabled")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_estimated_cost()}")
            
        elif actions["update"]:
            print(f"\\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🌐 Load Balancer: {self.lb_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_estimated_cost()}")
            
        else:
            print(f"\\n╭─ ✅ WILL KEEP")
            print(f"├─ 🌐 Load Balancer: {self.lb_name}")
            print(f"├─ 🌍 Frontend IP: {current_state.get('frontend_ip', 'Unknown')}")
            print(f"├─ 🖥️  Backend Count: {current_state.get('backend_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Load Balancer: {self.lb_name}")
        print(f"   🌍 Frontend IP: {current_state.get('frontend_ip', 'Unknown')}")
        print(f"   🖥️  Backend Count: {current_state.get('backend_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        print(f"   ⚠️  ALL TRAFFIC ROUTING WILL BE PERMANENTLY LOST")
        
    def _calculate_estimated_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_base_cost()
        
        # Add additional costs
        total_cost = base_cost
        
        # SSL certificate cost
        if self.ssl_certificate:
            total_cost += 0.75  # $0.75/month per certificate
            
        # CDN cost (if enabled)
        if self.enable_cdn:
            total_cost += 5.0  # Approximate CDN cost
            
        # Health check cost
        if self.health_check_enabled:
            health_check_cost = 0.50 * len(self.backends)  # $0.50/month per health check
            total_cost += health_check_cost
            
        return f"${total_cost:.2f}/month"
        
    def _get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            "lb_name": self.lb_name,
            "lb_type": self.lb_type,
            "lb_scheme": self.lb_scheme,
            "lb_protocol": self.lb_protocol,
            "lb_region": self.lb_region,
            "http_port": self.http_port,
            "https_port": self.https_port,
            "backend_port": self.backend_port,
            "backends": self.backends,
            "backend_count": len(self.backends),
            "ssl_certificate": self.ssl_certificate,
            "ssl_policy": self.ssl_policy,
            "redirect_http_to_https": self.redirect_http_to_https,
            "health_check_enabled": self.health_check_enabled,
            "health_check_path": self.health_check_path,
            "health_check_protocol": self.health_check_protocol,
            "health_check_port": self.health_check_port,
            "session_affinity": self.session_affinity,
            "connection_draining_timeout": self.connection_draining_timeout,
            "timeout_seconds": self.timeout_seconds,
            "enable_cdn": self.enable_cdn,
            "security_policy": self.security_policy,
            "allowed_regions": self.allowed_regions,
            "labels": self.lb_labels,
            "custom_headers": self.custom_headers,
            "url_map": self.url_map
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Load Balancer for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective load balancer")
            # Use internal scheme for cost savings when possible
            if self.lb_scheme == "EXTERNAL":
                print("   💡 Consider using internal scheme for cost savings")
            # Disable CDN for cost savings
            if self.enable_cdn:
                print("   💡 Disabling CDN for cost savings")
                self.enable_cdn = False
            # Longer connection draining for cost efficiency
            if self.connection_draining_timeout < 300:
                print("   💡 Increasing connection draining timeout for efficiency")
                self.connection_draining_timeout = 300
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance load balancer")
            # Enable CDN for performance
            if not self.enable_cdn:
                print("   💡 Enabling CDN for better performance")
                self.enable_cdn = True
            # Shorter timeouts for faster failover
            if self.timeout_seconds > 30:
                print("   💡 Reducing timeout for faster failover")
                self.timeout_seconds = 30
            # Optimize session affinity for performance
            if self.session_affinity == "NONE":
                print("   💡 Enabling client IP affinity for connection reuse")
                self.session_affinity = "CLIENT_IP"
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable load balancer")
            # Enable health checks
            if not self.health_check_enabled:
                print("   💡 Enabling health checks for reliability")
                self.health_check_enabled = True
            # Longer connection draining for graceful shutdown
            if self.connection_draining_timeout < 300:
                print("   💡 Increasing connection draining timeout for reliability")
                self.connection_draining_timeout = 300
            # Multiple health check protocols
            if self.health_check_protocol == "HTTP":
                print("   💡 Health checks configured for HTTP")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant load balancer")
            # Use internal scheme for compliance
            if self.lb_scheme == "EXTERNAL":
                print("   💡 Consider using internal scheme for compliance")
            # Require HTTPS
            if self.lb_protocol == "HTTP":
                print("   💡 Consider requiring HTTPS for compliance")
            # Enable security policy
            if not self.security_policy:
                print("   💡 Consider adding security policy for compliance")
            # Add compliance labels
            self.lb_labels.update({
                "compliance": "enabled",
                "security": "enhanced"
            })
            print("   💡 Added compliance labels")
            
        return self