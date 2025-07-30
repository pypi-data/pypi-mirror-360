from typing import Dict, Any, List, Optional
import boto3


class ECSDiscoveryMixin:
    def _discover_existing_services(self) -> Dict[str, Any]:
        try:
            existing_services = {}
            
            region = self.aws_client.get_region()
            ecs_client = boto3.client('ecs', region_name=region)
            
            clusters_response = ecs_client.list_clusters()
            cluster_arns = clusters_response.get('clusterArns', [])
            
            if not cluster_arns:
                return existing_services
            
            base_name = self.name.lower().replace('_', '-')
            target_cluster_name = self.cluster_name.lower()
            
            for cluster_arn in cluster_arns:
                try:
                    cluster_name = cluster_arn.split('/')[-1]
                    
                    services_response = ecs_client.list_services(cluster=cluster_arn)
                    service_arns = services_response.get('serviceArns', [])
                    
                    if not service_arns:
                        continue
                    
                    services_detail = ecs_client.describe_services(
                        cluster=cluster_arn,
                        services=service_arns
                    )
                    
                    for service in services_detail.get('services', []):
                        service_name = service['serviceName']
                        
                        is_related = False
                        
                        if service_name == self.name:
                            is_related = True
                        
                        elif base_name in service_name.lower():
                            is_related = True
                        
                        elif target_cluster_name in cluster_name.lower():
                            is_related = True
                        
                        try:
                            tags_response = ecs_client.list_tags_for_resource(resourceArn=service['serviceArn'])
                            tags = {tag['key']: tag['value'] for tag in tags_response.get('tags', [])}
                            if any(tag_key.lower() in ['infradsl', 'managedby'] for tag_key in tags.keys()):
                                is_related = True
                        except Exception:
                            pass
                        
                        if is_related:
                            created_at = 'unknown'
                            if service.get('createdAt'):
                                try:
                                    created_at = service['createdAt'].strftime('%Y-%m-%d %H:%M')
                                except Exception:
                                    pass
                            
                            existing_services[service_name] = {
                                'service_name': service_name,
                                'service_arn': service['serviceArn'],
                                'cluster': cluster_name,
                                'cluster_arn': cluster_arn,
                                'status': service.get('status', 'unknown'),
                                'running_count': service.get('runningCount', 0),
                                'pending_count': service.get('pendingCount', 0),
                                'desired_count': service.get('desiredCount', 0),
                                'task_definition': service.get('taskDefinition', ''),
                                'launch_type': service.get('launchType', 'unknown'),
                                'platform_version': service.get('platformVersion', ''),
                                'created_at': created_at,
                                'tags': tags if 'tags' in locals() else {}
                            }
                            
                except Exception as e:
                    print(f"   ⚠️  Warning: Failed to list services in cluster {cluster_arn}: {str(e)}")
                    continue
            
            return existing_services
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing ECS services: {str(e)}")
            return {}
