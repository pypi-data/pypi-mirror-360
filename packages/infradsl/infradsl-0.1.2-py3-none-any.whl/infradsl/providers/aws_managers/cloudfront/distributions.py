"""
AWS CloudFront Distributions

Handles CloudFront distribution operations including discovery, creation, update, and deletion.
Contains the stateless drift detection logic for existing distributions.
Enhanced with smart resource fingerprinting and predictive change impact analysis.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from botocore.exceptions import ClientError
from ....core.stateless_intelligence import (
    StatelessIntelligence, 
    ResourceType, 
    ResourceFingerprint,
    ChangeImpactAnalysis,
    ResourceHealth
)


class CloudFrontDistributions:
    """Manages CloudFront distribution operations with stateless intelligence"""

    def __init__(self, aws_client):
        self.aws_client = aws_client
        self.cloudfront_client = None
        self.intelligence = StatelessIntelligence()

    def _get_client(self):
        """Get CloudFront client"""
        if not self.cloudfront_client:
            try:
                import boto3
                self.cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')  # CloudFront is global
            except Exception as e:
                print(f"⚠️  Failed to create CloudFront client: {e}")
                return None
        return self.cloudfront_client

    def discover_existing_with_intelligence(self, resource_config: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Advanced resource discovery with smart fingerprinting
        Goes beyond traditional tagging to identify resources with high confidence
        """
        existing_distributions = self.discover_existing()
        
        if not resource_config:
            return existing_distributions
        
        # Enhance each discovered resource with intelligence
        enhanced_distributions = {}
        
        for dist_id, dist_data in existing_distributions.items():
            try:
                # Generate resource fingerprint
                fingerprint = self.intelligence.generate_resource_fingerprint(
                    resource_config=resource_config,
                    cloud_state=dist_data,
                    resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION
                )
                
                # Check resource health
                health = self.intelligence.check_resource_health(
                    resource_id=dist_id,
                    cloud_state=dist_data,
                    resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION
                )
                
                # Generate optimization recommendations
                recommendations = self.intelligence.generate_optimization_recommendations(
                    resource_config=resource_config,
                    cloud_state=dist_data,
                    resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION
                )
                
                # Enhance distribution data
                enhanced_distributions[dist_id] = {
                    **dist_data,
                    'fingerprint': fingerprint,
                    'health': health,
                    'recommendations': recommendations,
                    'confidence_score': fingerprint.confidence_score
                }
                
            except Exception as e:
                print(f"⚠️  Failed to enhance distribution {dist_id}: {str(e)}")
                enhanced_distributions[dist_id] = dist_data
        
        return enhanced_distributions
    
    def predict_change_impact(self, current_state: Dict[str, Any], 
                            desired_config: Dict[str, Any]) -> ChangeImpactAnalysis:
        """
        Predict the impact of proposed changes
        Revolutionary feature for preventing deployment issues
        """
        return self.intelligence.predict_change_impact(
            current_state=current_state,
            desired_state=desired_config,
            resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION
        )
    
    def detect_conflicts(self, desired_config: Dict[str, Any]) -> List[str]:
        """Detect potential conflicts with existing resources"""
        existing = self.discover_existing()
        return self.intelligence.detect_resource_conflicts(desired_config, existing)
    
    def find_matching_distribution(self, resource_config: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """
        Find existing distribution that matches desired configuration
        Returns: (distribution_id, distribution_data, confidence_score)
        """
        enhanced_distributions = self.discover_existing_with_intelligence(resource_config)
        
        best_match = None
        highest_confidence = 0.0
        
        for dist_id, dist_data in enhanced_distributions.items():
            confidence = dist_data.get('confidence_score', 0.0)
            
            if confidence > highest_confidence and confidence >= 0.7:  # 70% confidence threshold
                highest_confidence = confidence
                best_match = (dist_id, dist_data, confidence)
        
        return best_match

    def discover_existing(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing CloudFront distributions with proper null handling"""
        existing_distributions = {}
        
        client = self._get_client()
        if not client:
            print(f"⚠️  CloudFront client not available for distribution discovery")
            return existing_distributions
        
        try:
            # List all CloudFront distributions
            paginator = client.get_paginator('list_distributions')
            
            for page in paginator.paginate():
                distribution_list = page.get('DistributionList', {})
                if distribution_list.get('Quantity', 0) > 0:
                    for dist in distribution_list.get('Items', []):
                        dist_id = dist['Id']
                        
                        try:
                            # Get detailed distribution info
                            detail_response = client.get_distribution(Id=dist_id)
                            distribution = detail_response['Distribution']
                            
                            # **FIX: Properly handle None values from AWS API**
                            aliases_data = dist.get('Aliases')
                            if aliases_data is None:
                                aliases = []
                            else:
                                aliases = aliases_data.get('Items', [])

                            origins_data = dist.get('Origins')
                            if origins_data is None:
                                origins = []
                            else:
                                origins = origins_data.get('Items', [])
                            
                            existing_distributions[dist_id] = {
                                'id': dist_id,
                                'domain_name': dist['DomainName'],
                                'status': dist['Status'],
                                'enabled': dist['Enabled'],
                                'origins': origins,
                                'comment': dist.get('Comment', ''),
                                'aliases': aliases,  # Now guaranteed to be a list, never None
                                'price_class': dist.get('PriceClass', 'PriceClass_All'),
                                'created_date': dist.get('LastModifiedTime'),
                                'etag': detail_response['ETag']
                            }
                            
                        except ClientError as e:
                            print(f"⚠️  Failed to get details for distribution {dist_id}: {str(e)}")
                            existing_distributions[dist_id] = {
                                'id': dist_id,
                                'domain_name': dist['DomainName'],
                                'status': dist['Status'],
                                'aliases': [],  # Default empty list
                                'origins': [],  # Default empty list  
                                'comment': '',  # Default empty string
                                'error': str(e)
                            }
            
        except Exception as e:
            print(f"⚠️  Failed to discover existing distributions: {str(e)}")
        
        return existing_distributions

    def create(self, distribution_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a CloudFront distribution"""
        client = self._get_client()
        if not client:
            raise Exception("CloudFront client not initialized")

        try:
            response = client.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution = response['Distribution']
            return {
                'distribution_id': distribution['Id'],
                'domain_name': distribution['DomainName'],
                'status': distribution['Status'],
                'etag': response['ETag']
            }
            
        except Exception as e:
            print(f"❌ Failed to create CloudFront distribution: {str(e)}")
            raise

    def update(self, distribution_id: str, distribution_config: Dict[str, Any], etag: str) -> Dict[str, Any]:
        """Update a CloudFront distribution"""
        client = self._get_client()
        if not client:
            raise Exception("CloudFront client not initialized")

        try:
            response = client.update_distribution(
                Id=distribution_id,
                DistributionConfig=distribution_config,
                IfMatch=etag
            )
            
            distribution = response['Distribution']
            return {
                'distribution_id': distribution['Id'],
                'domain_name': distribution['DomainName'],
                'status': distribution['Status'],
                'etag': response['ETag']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'PreconditionFailed':
                print(f"⚠️  Distribution {distribution_id} was modified during update. Retry required.")
            print(f"❌ Failed to update distribution: {str(e)}")
            raise
            
        except Exception as e:
            print(f"❌ Failed to update distribution: {str(e)}")
            raise

    def delete(self, distribution_id: str) -> Dict[str, Any]:
        """Delete a CloudFront distribution"""
        client = self._get_client()
        if not client:
            raise Exception("CloudFront client not initialized")

        try:
            # First, disable the distribution
            config_response = client.get_distribution_config(Id=distribution_id)
            config = config_response['DistributionConfig']
            etag = config_response['ETag']
            
            if config['Enabled']:
                print(f"🔄 Disabling distribution {distribution_id} before deletion...")
                config['Enabled'] = False
                
                client.update_distribution(
                    Id=distribution_id,
                    DistributionConfig=config,
                    IfMatch=etag
                )
                
                print(f"⏳ Waiting for distribution to be disabled...")
                # In production, would wait for deployment to complete
                
            # Then delete the distribution
            response = client.delete_distribution(
                Id=distribution_id,
                IfMatch=etag
            )
            
            return {
                'distribution_id': distribution_id,
                'status': 'Deleting',
                'deleted': True
            }
            
        except Exception as e:
            print(f"❌ Failed to delete distribution: {str(e)}")
            raise

    def get(self, distribution_id: str) -> Dict[str, Any]:
        """Get detailed information about a distribution"""
        client = self._get_client()
        if not client:
            raise Exception("CloudFront client not initialized")

        try:
            response = client.get_distribution(Id=distribution_id)
            distribution = response['Distribution']
            
            return {
                'distribution_id': distribution['Id'],
                'domain_name': distribution['DomainName'],
                'status': distribution['Status'],
                'enabled': distribution['Enabled'],
                'comment': distribution.get('Comment', ''),
                'etag': response['ETag'],
                'last_modified': distribution.get('LastModifiedTime'),
                'origins': distribution.get('Origins', {}).get('Items', []),
                'aliases': distribution.get('Aliases', {}).get('Items', [])
            }
            
        except Exception as e:
            print(f"❌ Failed to get distribution {distribution_id}: {str(e)}")
            raise

    def list(self) -> List[Dict[str, Any]]:
        """List all CloudFront distributions"""
        client = self._get_client()
        if not client:
            return []

        distributions = []
        
        try:
            paginator = client.get_paginator('list_distributions')
            
            for page in paginator.paginate():
                distribution_list = page.get('DistributionList', {})
                if distribution_list.get('Quantity', 0) > 0:
                    for dist in distribution_list.get('Items', []):
                        distributions.append({
                            'distribution_id': dist['Id'],
                            'domain_name': dist['DomainName'],
                            'status': dist['Status'],
                            'enabled': dist['Enabled'],
                            'comment': dist.get('Comment', ''),
                            'last_modified': dist.get('LastModifiedTime')
                        })
                        
        except Exception as e:
            print(f"❌ Failed to list distributions: {str(e)}")
        
        return distributions

    def wait_for_deployment(self, distribution_id: str, timeout: int = 1800) -> bool:
        """Wait for distribution deployment to complete"""
        client = self._get_client()
        if not client:
            return False

        print(f"⏳ Waiting for distribution {distribution_id} deployment...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = client.get_distribution(Id=distribution_id)
                status = response['Distribution']['Status']
                
                if status == 'Deployed':
                    print(f"✅ Distribution deployment completed")
                    return True
                elif status == 'InProgress':
                    print(f"⏳ Deployment in progress... ({int(time.time() - start_time)}s)")
                    time.sleep(30)  # Check every 30 seconds
                else:
                    print(f"⚠️  Unexpected status: {status}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking deployment status: {str(e)}")
                return False
        
        print(f"⏰ Deployment timeout after {timeout} seconds")
        return False

    def _discover_current_state(self, resource_name: str) -> Dict[str, Any]:
        """
        Discover current state of CloudFront distribution
        Standardized method matching STATE-MANAGEMENT.md pattern
        """
        existing_distributions = self.discover_existing()
        
        # Find distribution by InfraDSL comment or name pattern
        for dist_id, dist_data in existing_distributions.items():
            comment = dist_data.get('comment', '')
            
            # Check if this distribution matches our resource
            if resource_name in comment or f"infradsl:{resource_name}" in comment:
                return {
                    'exists': True,
                    'distribution_id': dist_id,
                    'domain_name': dist_data['domain_name'],
                    'status': dist_data['status'],
                    'enabled': dist_data['enabled'],
                    'origins': dist_data.get('origins', []),
                    'aliases': dist_data.get('aliases', []),
                    'comment': comment,
                    'price_class': dist_data.get('price_class', 'PriceClass_All'),
                    'etag': dist_data.get('etag'),
                    'last_modified': dist_data.get('created_date')
                }
        
        return {'exists': False}
    
    def _build_desired_state(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build desired state based on current configuration
        Standardized method matching STATE-MANAGEMENT.md pattern
        """
        return {
            'exists': True,
            'enabled': resource_config.get('enabled', True),
            'origins': resource_config.get('origins', []),
            'aliases': resource_config.get('aliases', []),
            'comment': resource_config.get('comment', ''),
            'price_class': resource_config.get('price_class', 'PriceClass_All'),
            'default_cache_behavior': resource_config.get('default_cache_behavior', {}),
            'viewer_certificate': resource_config.get('viewer_certificate', {}),
            'custom_error_responses': resource_config.get('custom_error_responses', []),
            'web_acl_id': resource_config.get('web_acl_id', ''),
            'restrictions': resource_config.get('restrictions', {}),
            'logging': resource_config.get('logging', {})
        }
    
    def _calculate_diff(self, current: Dict[str, Any], desired: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate differences between current and desired state
        Standardized method matching STATE-MANAGEMENT.md pattern
        """
        if not current['exists'] and desired['exists']:
            return {'action': 'create', 'resource': desired}
        
        if current['exists'] and not desired['exists']:
            return {'action': 'delete', 'resource': current}
        
        # Calculate specific changes needed
        changes = {}
        
        # Check enabled state
        if current.get('enabled') != desired.get('enabled'):
            changes['enabled'] = {
                'from': current.get('enabled'),
                'to': desired.get('enabled'),
                'requires': 'update'
            }
        
        # Check origins
        if current.get('origins') != desired.get('origins'):
            changes['origins'] = {
                'from': current.get('origins'),
                'to': desired.get('origins'),
                'requires': 'update'
            }
        
        # Check aliases
        current_aliases = set(current.get('aliases', []))
        desired_aliases = set(desired.get('aliases', []))
        
        if current_aliases != desired_aliases:
            changes['aliases'] = {
                'from': list(current_aliases),
                'to': list(desired_aliases),
                'requires': 'update'
            }
        
        # Check price class
        if current.get('price_class') != desired.get('price_class'):
            changes['price_class'] = {
                'from': current.get('price_class'),
                'to': desired.get('price_class'),
                'requires': 'update'
            }
        
        # Check comment
        if current.get('comment') != desired.get('comment'):
            changes['comment'] = {
                'from': current.get('comment'),
                'to': desired.get('comment'),
                'requires': 'update'
            }
        
        return {'action': 'update', 'changes': changes} if changes else {'action': 'no_change'}
    
    def preview_changes(self, resource_name: str, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview changes that would be made to the distribution
        Enhanced with predictive impact analysis
        """
        current_state = self._discover_current_state(resource_name)
        desired_state = self._build_desired_state(resource_config)
        diff = self._calculate_diff(current_state, desired_state)
        
        result = {
            'resource_name': resource_name,
            'current_state': current_state,
            'desired_state': desired_state,
            'diff': diff
        }
        
        # Add predictive impact analysis
        if diff['action'] in ['create', 'update']:
            impact_analysis = self.predict_change_impact(current_state, desired_state)
            result['impact_analysis'] = {
                'change_type': impact_analysis.change_type,
                'impact_level': impact_analysis.impact_level.value,
                'estimated_downtime': impact_analysis.estimated_downtime,
                'propagation_time': impact_analysis.propagation_time,
                'cost_impact': impact_analysis.cost_impact,
                'affected_resources': impact_analysis.affected_resources,
                'recommendations': impact_analysis.recommendations,
                'rollback_complexity': impact_analysis.rollback_complexity
            }
        
        # Add conflict detection
        conflicts = self.detect_conflicts(desired_state)
        if conflicts:
            result['conflicts'] = conflicts
        
        return result 