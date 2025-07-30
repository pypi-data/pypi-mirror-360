"""
ECS Cluster Management

This module handles ECS cluster creation, management, and discovery operations.
"""

from typing import Dict, Any, List, Optional
import time


class EcsClusterManager:
    """
    ECS Cluster Management
    
    Handles:
    - Cluster creation and deletion
    - Cluster discovery and validation
    - Cluster-level configuration and tags
    - Cluster status monitoring
    """
    
    def __init__(self, aws_client):
        """Initialize the cluster manager with AWS client."""
        self.aws_client = aws_client
    
    def create_cluster(self, cluster_name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create or ensure ECS cluster exists.
        
        Args:
            cluster_name: Name of the cluster to create
            tags: Optional tags to apply to the cluster
            
        Returns:
            Cluster creation result with ARN and status
        """
        try:
            # Check if cluster already exists
            existing_cluster = self.get_cluster(cluster_name)
            if existing_cluster:
                print(f"📦 ECS cluster '{cluster_name}' already exists")
                return {
                    'cluster_arn': existing_cluster['clusterArn'],
                    'cluster_name': cluster_name,
                    'status': existing_cluster['status'],
                    'created': False
                }
            
            print(f"🏗️  Creating ECS cluster: {cluster_name}")
            
            # Prepare cluster configuration
            cluster_config = {
                'clusterName': cluster_name,
                'capacityProviders': ['FARGATE', 'FARGATE_SPOT'],
                'defaultCapacityProviderStrategy': [
                    {
                        'capacityProvider': 'FARGATE',
                        'weight': 1
                    }
                ]
            }
            
            # Add tags if provided
            if tags:
                cluster_config['tags'] = [
                    {'key': key, 'value': value}
                    for key, value in tags.items()
                ]
            
            # Create cluster
            response = self.aws_client.ecs.create_cluster(**cluster_config)
            cluster = response['cluster']
            
            # Wait for cluster to become active
            self._wait_for_cluster_active(cluster_name)
            
            print(f"✅ ECS cluster created: {cluster_name}")
            
            return {
                'cluster_arn': cluster['clusterArn'],
                'cluster_name': cluster_name,
                'status': cluster['status'],
                'created': True
            }
            
        except Exception as e:
            print(f"❌ Failed to create cluster '{cluster_name}': {str(e)}")
            raise
    
    def get_cluster(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cluster information by name.
        
        Args:
            cluster_name: Name of the cluster to retrieve
            
        Returns:
            Cluster information or None if not found
        """
        try:
            response = self.aws_client.ecs.describe_clusters(
                clusters=[cluster_name],
                include=['ATTACHMENTS', 'CONFIGURATIONS', 'STATISTICS']
            )
            
            clusters = response.get('clusters', [])
            if clusters and clusters[0]['status'] != 'INACTIVE':
                return clusters[0]
            
            return None
            
        except Exception:
            # Cluster doesn't exist or other error
            return None
    
    def delete_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """
        Delete ECS cluster.
        
        Args:
            cluster_name: Name of the cluster to delete
            
        Returns:
            Deletion result
        """
        try:
            # Check if cluster exists
            cluster = self.get_cluster(cluster_name)
            if not cluster:
                print(f"🚫 ECS cluster '{cluster_name}' does not exist")
                return {'deleted': False, 'reason': 'Cluster not found'}
            
            # Check if cluster has running services
            services = self._get_cluster_services(cluster_name)
            if services:
                running_services = [s for s in services if s.get('status') == 'ACTIVE']
                if running_services:
                    print(f"⚠️  Cannot delete cluster '{cluster_name}': {len(running_services)} active services")
                    return {
                        'deleted': False, 
                        'reason': f'Cluster has {len(running_services)} active services'
                    }
            
            print(f"🗑️  Deleting ECS cluster: {cluster_name}")
            
            # Delete cluster
            response = self.aws_client.ecs.delete_cluster(cluster=cluster_name)
            
            print(f"✅ ECS cluster deleted: {cluster_name}")
            
            return {
                'deleted': True,
                'cluster_arn': response['cluster']['clusterArn']
            }
            
        except Exception as e:
            print(f"❌ Failed to delete cluster '{cluster_name}': {str(e)}")
            raise
    
    def list_clusters(self) -> List[Dict[str, Any]]:
        """
        List all ECS clusters in the account.
        
        Returns:
            List of cluster information
        """
        try:
            # Get cluster ARNs
            response = self.aws_client.ecs.list_clusters()
            cluster_arns = response.get('clusterArns', [])
            
            if not cluster_arns:
                return []
            
            # Get detailed cluster information
            response = self.aws_client.ecs.describe_clusters(
                clusters=cluster_arns,
                include=['STATISTICS', 'CONFIGURATIONS']
            )
            
            clusters = []
            for cluster in response.get('clusters', []):
                if cluster['status'] != 'INACTIVE':
                    clusters.append({
                        'name': cluster['clusterName'],
                        'arn': cluster['clusterArn'],
                        'status': cluster['status'],
                        'active_services': cluster.get('activeServicesCount', 0),
                        'running_tasks': cluster.get('runningTasksCount', 0),
                        'pending_tasks': cluster.get('pendingTasksCount', 0),
                        'created_at': cluster.get('createdAt'),
                        'tags': self._extract_tags(cluster.get('tags', []))
                    })
            
            return clusters
            
        except Exception as e:
            print(f"❌ Failed to list clusters: {str(e)}")
            return []
    
    def get_cluster_status(self, cluster_name: str) -> Dict[str, Any]:
        """
        Get detailed cluster status and statistics.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            Cluster status information
        """
        cluster = self.get_cluster(cluster_name)
        if not cluster:
            return {'exists': False}
        
        services = self._get_cluster_services(cluster_name)
        
        return {
            'exists': True,
            'name': cluster['clusterName'],
            'arn': cluster['clusterArn'],
            'status': cluster['status'],
            'active_services': cluster.get('activeServicesCount', 0),
            'running_tasks': cluster.get('runningTasksCount', 0),
            'pending_tasks': cluster.get('pendingTasksCount', 0),
            'registered_container_instances': cluster.get('registeredContainerInstancesCount', 0),
            'services': len(services),
            'capacity_providers': cluster.get('capacityProviders', []),
            'created_at': cluster.get('createdAt'),
            'tags': self._extract_tags(cluster.get('tags', []))
        }
    
    def _wait_for_cluster_active(self, cluster_name: str, timeout: int = 300):
        """Wait for cluster to become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            cluster = self.get_cluster(cluster_name)
            if cluster and cluster['status'] == 'ACTIVE':
                return
            
            time.sleep(5)
        
        raise TimeoutError(f"Cluster '{cluster_name}' did not become active within {timeout} seconds")
    
    def _get_cluster_services(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Get all services in a cluster."""
        try:
            response = self.aws_client.ecs.list_services(cluster=cluster_name)
            service_arns = response.get('serviceArns', [])
            
            if not service_arns:
                return []
            
            response = self.aws_client.ecs.describe_services(
                cluster=cluster_name,
                services=service_arns
            )
            
            return response.get('services', [])
            
        except Exception:
            return []
    
    def _extract_tags(self, tag_list: List[Dict[str, str]]) -> Dict[str, str]:
        """Convert AWS tag list to dictionary."""
        return {tag['key']: tag['value'] for tag in tag_list}
    
    def discover_existing_clusters(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all existing clusters for preview operations.
        
        Returns:
            Dictionary mapping cluster names to their information
        """
        clusters = self.list_clusters()
        return {cluster['name']: cluster for cluster in clusters}