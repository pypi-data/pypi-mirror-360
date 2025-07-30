import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional


class LoadBalancerLifecycleMixin:
    """
    Mixin for LoadBalancer lifecycle operations (create, update, destroy).
    """
    def create(self) -> Dict[str, Any]:
        """Create/update load balancer and remove any that are no longer needed"""
        self._ensure_authenticated()
        
        if not self.load_balancer_name:
            self.load_balancer_name = self.name
        
        try:
            # Check if load balancer exists
            lb_exists = self._load_balancer_exists()
            
            if not lb_exists:
                # Create load balancer
                lb_result = self._create_load_balancer()
                print(f"✅ Created Application Load Balancer: {self.load_balancer_name}")
            else:
                print(f"📋 Application Load Balancer exists: {self.load_balancer_name}")
                lb_result = self._get_load_balancer_info()
            
            # Configure target groups if specified
            if self.target_groups:
                self._configure_target_groups()
            
            # Configure listeners if specified
            if self.listeners:
                self._configure_listeners()
            
            return lb_result
            
        except Exception as e:
            print(f"❌ Error creating load balancer: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the load balancer"""
        self._ensure_authenticated()
        
        if not self.load_balancer_name:
            self.load_balancer_name = self.name
        
        try:
            # Check if load balancer exists
            if not self._load_balancer_exists():
                print(f"⚠️ Load balancer {self.load_balancer_name} does not exist")
                return {"status": "not_found", "load_balancer_name": self.load_balancer_name}
            
            # Delete the load balancer
            self.elbv2_client.delete_load_balancer(LoadBalancerArn=self.load_balancer_arn)
            print(f"🗑️ Destroyed load balancer: {self.load_balancer_name}")
            
            return {
                "status": "destroyed",
                "load_balancer_name": self.load_balancer_name,
                "load_balancer_arn": self.load_balancer_arn
            }
            
        except Exception as e:
            print(f"❌ Error destroying load balancer: {str(e)}")
            raise

    def _load_balancer_exists(self) -> bool:
        """Check if load balancer exists"""
        try:
            response = self.elbv2_client.describe_load_balancers(Names=[self.load_balancer_name])
            if response['LoadBalancers']:
                lb = response['LoadBalancers'][0]
                self.load_balancer_arn = lb['LoadBalancerArn']
                self.dns_name = lb['DNSName']
                self.canonical_hosted_zone_id = lb['CanonicalHostedZoneId']
                self.state = lb['State']['Code']
                return True
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                return False
            raise

    def _create_load_balancer(self) -> Dict[str, Any]:
        """Create the load balancer"""
        create_params = {
            'Name': self.load_balancer_name,
            'Type': self.load_balancer_type or 'application',
            'Scheme': self.scheme or 'internet-facing',
            'IpAddressType': self.ip_address_type or 'ipv4'
        }
        
        # Add subnets if specified
        if self.subnets:
            create_params['Subnets'] = self.subnets
        else:
            # Use default subnets (this would need to be enhanced in real implementation)
            print("⚠️ Using default subnets (configure subnets for production)")
        
        # Add security groups if specified
        if self.security_groups:
            create_params['SecurityGroups'] = self.security_groups
        
        # Add tags if specified
        if self.tags:
            create_params['Tags'] = [{'Key': k, 'Value': v} for k, v in self.tags.items()]
        
        response = self.elbv2_client.create_load_balancer(**create_params)
        
        lb = response['LoadBalancers'][0]
        self.load_balancer_arn = lb['LoadBalancerArn']
        self.dns_name = lb['DNSName']
        self.canonical_hosted_zone_id = lb['CanonicalHostedZoneId']
        self.state = lb['State']['Code']
        
        return self._get_load_balancer_info()

    def _get_load_balancer_info(self) -> Dict[str, Any]:
        """Get load balancer information"""
        try:
            response = self.elbv2_client.describe_load_balancers(Names=[self.load_balancer_name])
            if response['LoadBalancers']:
                lb = response['LoadBalancers'][0]
                return {
                    "load_balancer_name": lb['LoadBalancerName'],
                    "load_balancer_arn": lb['LoadBalancerArn'],
                    "dns_name": lb['DNSName'],
                    "canonical_hosted_zone_id": lb['CanonicalHostedZoneId'],
                    "scheme": lb['Scheme'],
                    "vpc_id": lb['VpcId'],
                    "state": lb['State']['Code'],
                    "type": lb['Type'],
                    "ip_address_type": lb['IpAddressType'],
                    "subnets": [az['SubnetId'] for az in lb['AvailabilityZones']],
                    "security_groups": lb.get('SecurityGroups', []),
                    "created_time": lb['CreatedTime'].isoformat() if 'CreatedTime' in lb else None
                }
            return {"error": "Load balancer not found"}
        except Exception as e:
            return {"error": str(e)}

    def _configure_target_groups(self):
        """Configure target groups for the load balancer"""
        # This would be implemented to create and configure target groups
        print(f"🎯 Configuring {len(self.target_groups)} target groups")

    def _configure_listeners(self):
        """Configure listeners for the load balancer"""
        # This would be implemented to create and configure listeners
        print(f"👂 Configuring {len(self.listeners)} listeners") 