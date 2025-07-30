"""
S3 Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for S3 buckets.
Extends the AWS intelligence base with S3-specific capabilities.
"""

import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType,
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class S3Intelligence(AWSIntelligenceBase):
    """S3-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(ResourceType.S3_BUCKET)
        self.s3_client = None
    
    def _get_s3_client(self):
        """Get S3 client with error handling"""
        if not self.s3_client:
            try:
                self.s3_client = boto3.client('s3')
            except (NoCredentialsError, Exception) as e:
                print(f"⚠️  Failed to create S3 client: {e}")
                return None
        return self.s3_client
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing S3 buckets"""
        existing_buckets = {}
        
        client = self._get_s3_client()
        if not client:
            return existing_buckets
        
        try:
            # List all buckets
            response = client.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                try:
                    # Get detailed bucket information
                    bucket_data = self._get_bucket_details(bucket_name)
                    existing_buckets[bucket_name] = bucket_data
                    
                except ClientError as e:
                    print(f"⚠️  Failed to get details for bucket {bucket_name}: {str(e)}")
                    existing_buckets[bucket_name] = {
                        'name': bucket_name,
                        'creation_date': bucket['CreationDate'],
                        'error': str(e)
                    }
        
        except Exception as e:
            print(f"⚠️  Failed to discover S3 buckets: {str(e)}")
        
        return existing_buckets
    
    def _get_bucket_details(self, bucket_name: str) -> Dict[str, Any]:
        """Get comprehensive bucket details"""
        client = self._get_s3_client()
        bucket_data = {
            'name': bucket_name,
            'region': None,
            'versioning': False,
            'encryption': None,
            'public_access_block': {},
            'website_configuration': None,
            'cors_configuration': None,
            'lifecycle_configuration': None,
            'logging': None,
            'tags': {},
            'acl': None,
            'policy': None
        }
        
        try:
            # Get bucket location
            location_response = client.get_bucket_location(Bucket=bucket_name)
            bucket_data['region'] = location_response.get('LocationConstraint') or 'us-east-1'
            
            # Get versioning
            try:
                versioning_response = client.get_bucket_versioning(Bucket=bucket_name)
                bucket_data['versioning'] = versioning_response.get('Status') == 'Enabled'
            except ClientError:
                pass
            
            # Get encryption
            try:
                encryption_response = client.get_bucket_encryption(Bucket=bucket_name)
                bucket_data['encryption'] = encryption_response.get('ServerSideEncryptionConfiguration', {})
            except ClientError:
                pass
            
            # Get public access block
            try:
                pab_response = client.get_public_access_block(Bucket=bucket_name)
                bucket_data['public_access_block'] = pab_response.get('PublicAccessBlockConfiguration', {})
            except ClientError:
                pass
            
            # Get website configuration
            try:
                website_response = client.get_bucket_website(Bucket=bucket_name)
                bucket_data['website_configuration'] = website_response
            except ClientError:
                pass
            
            # Get CORS configuration
            try:
                cors_response = client.get_bucket_cors(Bucket=bucket_name)
                bucket_data['cors_configuration'] = cors_response.get('CORSRules', [])
            except ClientError:
                pass
            
            # Get lifecycle configuration
            try:
                lifecycle_response = client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                bucket_data['lifecycle_configuration'] = lifecycle_response.get('Rules', [])
            except ClientError:
                pass
            
            # Get logging
            try:
                logging_response = client.get_bucket_logging(Bucket=bucket_name)
                bucket_data['logging'] = logging_response.get('LoggingEnabled', {})
            except ClientError:
                pass
            
            # Get tags
            try:
                tags_response = client.get_bucket_tagging(Bucket=bucket_name)
                tag_set = tags_response.get('TagSet', [])
                bucket_data['tags'] = {tag['Key']: tag['Value'] for tag in tag_set}
            except ClientError:
                pass
            
            # Get ACL
            try:
                acl_response = client.get_bucket_acl(Bucket=bucket_name)
                bucket_data['acl'] = {
                    'owner': acl_response.get('Owner', {}),
                    'grants': acl_response.get('Grants', [])
                }
            except ClientError:
                pass
            
            # Get bucket policy
            try:
                policy_response = client.get_bucket_policy(Bucket=bucket_name)
                bucket_data['policy'] = policy_response.get('Policy')
            except ClientError:
                pass
        
        except Exception as e:
            print(f"⚠️  Error getting details for bucket {bucket_name}: {str(e)}")
        
        return bucket_data
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from S3 bucket state"""
        return {
            'name': cloud_state.get('name'),
            'region': cloud_state.get('region'),
            'versioning': cloud_state.get('versioning', False),
            'encryption': bool(cloud_state.get('encryption')),
            'public_access_block': cloud_state.get('public_access_block', {}),
            'website_hosting': bool(cloud_state.get('website_configuration')),
            'cors_enabled': bool(cloud_state.get('cors_configuration')),
            'lifecycle_rules': len(cloud_state.get('lifecycle_configuration', [])),
            'logging_enabled': bool(cloud_state.get('logging', {}).get('TargetBucket')),
            'tags': cloud_state.get('tags', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate S3-specific fingerprint data"""
        fingerprint_data = {}
        
        # Bucket naming pattern
        bucket_name = cloud_state.get('name', '')
        if bucket_name:
            fingerprint_data['name_pattern'] = {
                'length': len(bucket_name),
                'has_prefix': any(bucket_name.startswith(p) for p in ['dev-', 'prod-', 'staging-', 'test-']),
                'has_suffix': any(bucket_name.endswith(s) for s in ['-logs', '-backup', '-data', '-assets']),
                'contains_company': any(term in bucket_name.lower() for term in ['company', 'corp', 'inc'])
            }
        
        # Security configuration fingerprint
        pab = cloud_state.get('public_access_block', {})
        fingerprint_data['security_posture'] = {
            'block_public_acls': pab.get('BlockPublicAcls', False),
            'ignore_public_acls': pab.get('IgnorePublicAcls', False),
            'block_public_policy': pab.get('BlockPublicPolicy', False),
            'restrict_public_buckets': pab.get('RestrictPublicBuckets', False),
            'has_encryption': bool(cloud_state.get('encryption')),
            'versioning_enabled': cloud_state.get('versioning', False)
        }
        
        # Usage pattern fingerprint
        fingerprint_data['usage_pattern'] = {
            'is_website': bool(cloud_state.get('website_configuration')),
            'has_cors': bool(cloud_state.get('cors_configuration')),
            'has_lifecycle': bool(cloud_state.get('lifecycle_configuration')),
            'has_logging': bool(cloud_state.get('logging', {}).get('TargetBucket')),
            'has_policy': bool(cloud_state.get('policy'))
        }
        
        return fingerprint_data
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict S3-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 30  # S3 changes are usually fast
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Analyze specific S3 changes
        
        # 1. Public access changes
        current_pab = current.get('public_access_block', {})
        desired_pab = desired.get('public_access_block', {})
        
        if current_pab != desired_pab:
            changes.append("public_access_modification")
            # Making bucket more public = higher impact
            if self._is_making_more_public(current_pab, desired_pab):
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                recommendations.append("WARNING: Reducing public access restrictions")
                recommendations.append("Verify this change is intentional for security")
                rollback_complexity = "medium"
            else:
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                recommendations.append("Improving security by restricting public access")
        
        # 2. Versioning changes
        if current.get('versioning') != desired.get('versioning'):
            changes.append("versioning_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired.get('versioning') and not current.get('versioning'):
                recommendations.append("Enabling versioning will increase storage costs")
                cost_impact += 20  # Rough estimate
            elif not desired.get('versioning') and current.get('versioning'):
                recommendations.append("WARNING: Disabling versioning cannot be easily undone")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                rollback_complexity = "high"
        
        # 3. Encryption changes
        current_encryption = bool(current.get('encryption'))
        desired_encryption = bool(desired.get('encryption'))
        
        if current_encryption != desired_encryption:
            changes.append("encryption_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired_encryption and not current_encryption:
                recommendations.append("Enabling encryption will apply to new objects only")
                recommendations.append("Consider encrypting existing objects separately")
            else:
                recommendations.append("WARNING: Disabling encryption affects security")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
        
        # 4. Website hosting changes
        current_website = bool(current.get('website_configuration'))
        desired_website = bool(desired.get('website_configuration'))
        
        if current_website != desired_website:
            changes.append("website_hosting_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 300)  # 5 minutes for DNS propagation
            
            if desired_website:
                recommendations.append("Configure CloudFront for better website performance")
                affected_resources.append("route53_records")
            else:
                recommendations.append("WARNING: Disabling website hosting will break web access")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
        
        # 5. CORS changes
        if current.get('cors_configuration') != desired.get('cors_configuration'):
            changes.append("cors_modification")
            impact_level = ChangeImpact.LOW if impact_level.value < ChangeImpact.LOW.value else impact_level
            recommendations.append("Test cross-origin requests after CORS changes")
        
        # Find affected resources
        bucket_name = current.get('name') or desired.get('name')
        if bucket_name:
            # CloudFront distributions might use this bucket
            affected_resources.append(f"cloudfront_distributions_using_{bucket_name}")
            # Applications might access this bucket
            affected_resources.append(f"applications_accessing_{bucket_name}")
        
        change_type = ", ".join(changes) if changes else "configuration_update"
        
        return ChangeImpactAnalysis(
            change_type=change_type,
            impact_level=impact_level,
            estimated_downtime=downtime,
            propagation_time=propagation_time,
            cost_impact=cost_impact,
            affected_resources=affected_resources,
            recommendations=recommendations,
            rollback_complexity=rollback_complexity
        )
    
    def _is_making_more_public(self, current_pab: Dict[str, Any], 
                              desired_pab: Dict[str, Any]) -> bool:
        """Check if changes make bucket more publicly accessible"""
        public_settings = ['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']
        
        for setting in public_settings:
            current_blocked = current_pab.get(setting, True)
            desired_blocked = desired_pab.get(setting, True)
            
            # If we're changing from blocked to not blocked, it's more public
            if current_blocked and not desired_blocked:
                return True
        
        return False
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check S3 bucket health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Security health checks
        pab = cloud_state.get('public_access_block', {})
        if not all(pab.get(setting, False) for setting in 
                  ['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']):
            health_score -= 0.3
            issues.append("Public access not fully restricted")
        
        # Encryption check
        if not cloud_state.get('encryption'):
            health_score -= 0.2
            issues.append("Bucket encryption not enabled")
        
        # Versioning check for important buckets
        if not cloud_state.get('versioning'):
            health_score -= 0.1
            issues.append("Versioning not enabled (recommended for data protection)")
        
        # Lifecycle management check
        if not cloud_state.get('lifecycle_configuration'):
            issues.append("No lifecycle rules configured (consider for cost optimization)")
        
        # Logging check
        if not cloud_state.get('logging', {}).get('TargetBucket'):
            issues.append("Access logging not enabled")
        
        # Calculate metrics
        metrics['security_features_enabled'] = sum([
            bool(cloud_state.get('encryption')),
            bool(cloud_state.get('versioning')),
            bool(pab.get('BlockPublicAcls')),
            bool(pab.get('RestrictPublicBuckets'))
        ])
        
        metrics['management_features_enabled'] = sum([
            bool(cloud_state.get('lifecycle_configuration')),
            bool(cloud_state.get('logging', {}).get('TargetBucket')),
            bool(cloud_state.get('tags'))
        ])
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate S3-specific changes"""
        changes = {}
        
        # Check versioning
        if current.get('versioning') != desired.get('versioning'):
            changes['versioning'] = {
                'from': current.get('versioning'),
                'to': desired.get('versioning'),
                'requires': 'update'
            }
        
        # Check encryption
        if current.get('encryption') != desired.get('encryption'):
            changes['encryption'] = {
                'from': bool(current.get('encryption')),
                'to': bool(desired.get('encryption')),
                'requires': 'update'
            }
        
        # Check public access block
        current_pab = current.get('public_access_block', {})
        desired_pab = desired.get('public_access_block', {})
        
        if current_pab != desired_pab:
            changes['public_access_block'] = {
                'from': current_pab,
                'to': desired_pab,
                'requires': 'update'
            }
        
        # Check website configuration
        current_website = bool(current.get('website_configuration'))
        desired_website = bool(desired.get('website_configuration'))
        
        if current_website != desired_website:
            changes['website_hosting'] = {
                'from': current_website,
                'to': desired_website,
                'requires': 'update'
            }
        
        return changes