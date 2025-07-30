class VPCLifecycleMixin:
    """
    Mixin for VPC lifecycle operations (create, update, destroy).
    """
    def create(self):
        """Create/update VPC and all its components"""
        self._ensure_authenticated()
        
        vpc_name = self._vpc_name or self.name
        cidr = self.cidr_block or "10.0.0.0/16"
        
        print(f"🏗️ Creating VPC: {vpc_name}")
        print(f"   CIDR Block: {cidr}")
        print(f"   Instance Tenancy: {self.instance_tenancy}")
        
        # Mock VPC creation
        self.vpc_id = f"vpc-{vpc_name.lower().replace('_', '-')}-12345"
        self.state = "available"
        self.vpc_exists = True
        
        print(f"✅ VPC created: {self.vpc_id}")
        
        # Create subnets
        if self.subnets:
            print(f"🔗 Creating {len(self.subnets)} subnets...")
            for i, subnet in enumerate(self.subnets):
                subnet_id = f"subnet-{subnet['name']}-{i:02d}"
                subnet['subnet_id'] = subnet_id
                print(f"   - {subnet['name']}: {subnet_id} ({subnet['cidr_block']}, {subnet['type']})")
        
        # Create Internet Gateway
        if self.internet_gateway_id:
            print(f"🌐 Creating Internet Gateway: {self.internet_gateway_id}")
        
        # Create NAT Gateways
        if self.nat_gateways:
            print(f"🔄 Creating {len(self.nat_gateways)} NAT Gateways...")
            for i, nat in enumerate(self.nat_gateways):
                nat_id = f"nat-{nat['name']}-{i:02d}"
                nat['nat_gateway_id'] = nat_id
                print(f"   - {nat['name']}: {nat_id}")
        
        # Create VPC Endpoints
        if self.endpoints:
            print(f"🔌 Creating {len(self.endpoints)} VPC Endpoints...")
            for i, endpoint in enumerate(self.endpoints):
                endpoint_id = f"vpce-{endpoint['service_name']}-{i:02d}"
                endpoint['vpc_endpoint_id'] = endpoint_id
                print(f"   - {endpoint['service_name']}: {endpoint_id}")
        
        # Create Route Tables
        if self.route_tables:
            print(f"🗺️ Creating {len(self.route_tables)} Route Tables...")
            for i, rt in enumerate(self.route_tables):
                rt_id = f"rtb-{rt['name']}-{i:02d}"
                rt['route_table_id'] = rt_id
                print(f"   - {rt['name']}: {rt_id}")
        
        print(f"🎉 VPC infrastructure created successfully!")
        
        return {
            'vpc_id': self.vpc_id,
            'vpc_name': vpc_name,
            'cidr_block': cidr,
            'state': self.state,
            'subnets_created': len(self.subnets),
            'nat_gateways_created': len(self.nat_gateways),
            'endpoints_created': len(self.endpoints)
        }

    def destroy(self):
        """Destroy the VPC and all its components"""
        self._ensure_authenticated()
        
        if not self.vpc_exists:
            print("⚠️  No VPC to destroy")
            return {'destroyed': False, 'reason': 'VPC does not exist'}
        
        vpc_name = self._vpc_name or self.name
        print(f"🗑️  Destroying VPC: {vpc_name} ({self.vpc_id})")
        
        # Destroy in reverse order (dependencies first)
        
        # Destroy NAT Gateways
        if self.nat_gateways:
            print(f"   🔄 Destroying {len(self.nat_gateways)} NAT Gateways...")
            for nat in self.nat_gateways:
                print(f"      - {nat.get('nat_gateway_id', nat['name'])}")
        
        # Destroy VPC Endpoints
        if self.endpoints:
            print(f"   🔌 Destroying {len(self.endpoints)} VPC Endpoints...")
            for endpoint in self.endpoints:
                print(f"      - {endpoint.get('vpc_endpoint_id', endpoint['service_name'])}")
        
        # Destroy Route Tables
        if self.route_tables:
            print(f"   🗺️ Destroying {len(self.route_tables)} Route Tables...")
            for rt in self.route_tables:
                print(f"      - {rt.get('route_table_id', rt['name'])}")
        
        # Destroy Subnets
        if self.subnets:
            print(f"   🔗 Destroying {len(self.subnets)} subnets...")
            for subnet in self.subnets:
                print(f"      - {subnet.get('subnet_id', subnet['name'])}")
        
        # Destroy Internet Gateway
        if self.internet_gateway_id:
            print(f"   🌐 Destroying Internet Gateway: {self.internet_gateway_id}")
        
        # Finally destroy VPC
        print(f"   🏗️ Destroying VPC: {self.vpc_id}")
        
        # Update state
        self.vpc_exists = False
        self.state = "deleted"
        
        print("✅ VPC destroyed successfully")
        
        return {
            'destroyed': True,
            'vpc_id': self.vpc_id,
            'vpc_name': vpc_name
        }
    
    def _display_preview(self, to_create, to_keep, to_remove):
        """Display preview of changes"""
        print("\n📋 VPC Preview:")
        print("=" * 50)
        
        if to_create:
            print("✨ To Create:")
            for resource in to_create:
                print(f"   - {resource['type']}: {resource['name']}")
        
        if to_keep:
            print("✅ To Keep:")
            for resource in to_keep:
                print(f"   - {resource['type']}: {resource['name']} (No changes)")
        
        if to_remove:
            print("🗑️  To Remove:")
            for resource in to_remove:
                print(f"   - {resource['type']}: {resource['name']}")
        
        print("=" * 50)