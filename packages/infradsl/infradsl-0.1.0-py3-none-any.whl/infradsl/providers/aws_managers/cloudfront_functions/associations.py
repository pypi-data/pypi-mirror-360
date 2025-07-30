"""
CloudFront Function Associations

Manages the association of CloudFront Functions with CloudFront distributions
and cache behaviors.
"""

from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError


class CloudFrontFunctionAssociations:
    """
    Manages CloudFront Function associations with distributions
    
    Handles attaching and detaching functions from cache behaviors
    and managing the association lifecycle.
    """
    
    def __init__(self, aws_client):
        """Initialize with AWS client"""
        self.aws_client = aws_client
        self.client = None
        
    def _get_client(self):
        """Get CloudFront service client"""
        if not self.client:
            self.client = self.aws_client.get_client('cloudfront')
        return self.client
    
    def associate_functions(self, distribution_id: str, function_associations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Associate CloudFront Functions with a distribution
        
        Args:
            distribution_id: CloudFront distribution ID
            function_associations: List of function association configs
            
        Returns:
            Dict containing association results
        """
        # This method would integrate with the existing CloudFront distribution manager
        # to update cache behaviors with function associations
        
        client = self._get_client()
        
        try:
            # Get current distribution configuration
            response = client.get_distribution(Id=distribution_id)
            distribution_config = response['Distribution']['DistributionConfig']
            etag = response['ETag']
            
            # Update cache behaviors with function associations
            self._add_function_associations_to_behaviors(
                distribution_config, 
                function_associations
            )
            
            # Update the distribution
            update_response = client.update_distribution(
                DistributionConfig=distribution_config,
                Id=distribution_id,
                IfMatch=etag
            )
            
            return {
                'distribution_id': distribution_id,
                'associations_added': len(function_associations),
                'status': update_response['Distribution']['Status'],
                'etag': update_response['ETag']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to associate functions with distribution: {str(e)}")
    
    def _add_function_associations_to_behaviors(self, distribution_config: Dict[str, Any], 
                                              function_associations: List[Dict[str, Any]]):
        """
        Add function associations to cache behaviors
        
        Args:
            distribution_config: CloudFront distribution configuration
            function_associations: Function associations to add
        """
        # Update default cache behavior
        if 'DefaultCacheBehavior' in distribution_config:
            default_behavior = distribution_config['DefaultCacheBehavior']
            self._add_functions_to_behavior(default_behavior, function_associations, '/*')
        
        # Update additional cache behaviors
        if 'CacheBehaviors' in distribution_config:
            for behavior in distribution_config['CacheBehaviors'].get('Items', []):
                path_pattern = behavior.get('PathPattern', '/*')
                self._add_functions_to_behavior(behavior, function_associations, path_pattern)
    
    def _add_functions_to_behavior(self, behavior: Dict[str, Any], 
                                 function_associations: List[Dict[str, Any]], 
                                 path_pattern: str):
        """
        Add function associations to a specific cache behavior
        
        Args:
            behavior: Cache behavior configuration
            function_associations: Function associations to add
            path_pattern: Path pattern for this behavior
        """
        # Initialize FunctionAssociations if not present
        if 'FunctionAssociations' not in behavior:
            behavior['FunctionAssociations'] = {
                'Quantity': 0,
                'Items': []
            }
        
        function_associations_config = behavior['FunctionAssociations']
        
        # Add matching function associations
        for association in function_associations:
            # Check if this association applies to this path pattern
            if self._association_matches_path(association, path_pattern):
                function_association = {
                    'FunctionARN': association['function_arn'],
                    'EventType': association['event_type']  # viewer-request or viewer-response
                }
                
                # Check if association already exists
                if not self._association_exists(function_associations_config['Items'], function_association):
                    function_associations_config['Items'].append(function_association)
                    function_associations_config['Quantity'] += 1
    
    def _association_matches_path(self, association: Dict[str, Any], path_pattern: str) -> bool:
        """
        Check if a function association should apply to a given path pattern
        
        Args:
            association: Function association configuration
            path_pattern: Cache behavior path pattern
            
        Returns:
            True if association applies to this path pattern
        """
        # If association specifies a path pattern, check for match
        if 'path_pattern' in association:
            return association['path_pattern'] == path_pattern
        
        # If no path pattern specified, apply to default behavior only
        return path_pattern == '/*'
    
    def _association_exists(self, existing_associations: List[Dict[str, Any]], 
                          new_association: Dict[str, Any]) -> bool:
        """
        Check if a function association already exists
        
        Args:
            existing_associations: List of existing associations
            new_association: New association to check
            
        Returns:
            True if association already exists
        """
        for existing in existing_associations:
            if (existing.get('FunctionARN') == new_association.get('FunctionARN') and
                existing.get('EventType') == new_association.get('EventType')):
                return True
        return False
    
    def remove_function_associations(self, distribution_id: str, 
                                   function_arns: List[str]) -> Dict[str, Any]:
        """
        Remove CloudFront Function associations from a distribution
        
        Args:
            distribution_id: CloudFront distribution ID
            function_arns: List of function ARNs to remove
            
        Returns:
            Dict containing removal results
        """
        client = self._get_client()
        
        try:
            # Get current distribution configuration
            response = client.get_distribution(Id=distribution_id)
            distribution_config = response['Distribution']['DistributionConfig']
            etag = response['ETag']
            
            # Remove function associations from behaviors
            removed_count = self._remove_function_associations_from_behaviors(
                distribution_config, 
                function_arns
            )
            
            # Update the distribution
            update_response = client.update_distribution(
                DistributionConfig=distribution_config,
                Id=distribution_id,
                IfMatch=etag
            )
            
            return {
                'distribution_id': distribution_id,
                'associations_removed': removed_count,
                'status': update_response['Distribution']['Status'],
                'etag': update_response['ETag']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to remove function associations: {str(e)}")
    
    def _remove_function_associations_from_behaviors(self, distribution_config: Dict[str, Any], 
                                                   function_arns: List[str]) -> int:
        """
        Remove function associations from cache behaviors
        
        Args:
            distribution_config: CloudFront distribution configuration
            function_arns: Function ARNs to remove
            
        Returns:
            Number of associations removed
        """
        removed_count = 0
        
        # Remove from default cache behavior
        if 'DefaultCacheBehavior' in distribution_config:
            default_behavior = distribution_config['DefaultCacheBehavior']
            removed_count += self._remove_functions_from_behavior(default_behavior, function_arns)
        
        # Remove from additional cache behaviors
        if 'CacheBehaviors' in distribution_config:
            for behavior in distribution_config['CacheBehaviors'].get('Items', []):
                removed_count += self._remove_functions_from_behavior(behavior, function_arns)
        
        return removed_count
    
    def _remove_functions_from_behavior(self, behavior: Dict[str, Any], 
                                      function_arns: List[str]) -> int:
        """
        Remove function associations from a specific cache behavior
        
        Args:
            behavior: Cache behavior configuration
            function_arns: Function ARNs to remove
            
        Returns:
            Number of associations removed from this behavior
        """
        if 'FunctionAssociations' not in behavior:
            return 0
        
        function_associations_config = behavior['FunctionAssociations']
        original_items = function_associations_config.get('Items', [])
        
        # Filter out associations with matching ARNs
        filtered_items = [
            item for item in original_items 
            if item.get('FunctionARN') not in function_arns
        ]
        
        removed_count = len(original_items) - len(filtered_items)
        
        # Update the behavior configuration
        function_associations_config['Items'] = filtered_items
        function_associations_config['Quantity'] = len(filtered_items)
        
        return removed_count
    
    def get_distribution_function_associations(self, distribution_id: str) -> List[Dict[str, Any]]:
        """
        Get all function associations for a distribution
        
        Args:
            distribution_id: CloudFront distribution ID
            
        Returns:
            List of function associations
        """
        client = self._get_client()
        
        try:
            response = client.get_distribution(Id=distribution_id)
            distribution_config = response['Distribution']['DistributionConfig']
            
            associations = []
            
            # Get associations from default cache behavior
            if 'DefaultCacheBehavior' in distribution_config:
                default_behavior = distribution_config['DefaultCacheBehavior']
                behavior_associations = self._extract_function_associations(default_behavior, '/*')
                associations.extend(behavior_associations)
            
            # Get associations from additional cache behaviors
            if 'CacheBehaviors' in distribution_config:
                for behavior in distribution_config['CacheBehaviors'].get('Items', []):
                    path_pattern = behavior.get('PathPattern', '/*')
                    behavior_associations = self._extract_function_associations(behavior, path_pattern)
                    associations.extend(behavior_associations)
            
            return associations
            
        except ClientError as e:
            raise Exception(f"Failed to get function associations: {str(e)}")
    
    def _extract_function_associations(self, behavior: Dict[str, Any], 
                                     path_pattern: str) -> List[Dict[str, Any]]:
        """
        Extract function associations from a cache behavior
        
        Args:
            behavior: Cache behavior configuration
            path_pattern: Path pattern for this behavior
            
        Returns:
            List of function associations for this behavior
        """
        associations = []
        
        if 'FunctionAssociations' in behavior:
            function_associations = behavior['FunctionAssociations']
            for item in function_associations.get('Items', []):
                associations.append({
                    'function_arn': item.get('FunctionARN'),
                    'event_type': item.get('EventType'),
                    'path_pattern': path_pattern
                })
        
        return associations