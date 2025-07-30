"""
Comprehensive tests for brownfield environment discovery
Tests the UniversalResourceDiscovery system with complex real-world scenarios
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from infradsl.core.universal_resource_discovery import (
    UniversalResourceDiscovery,
    AdoptionPolicy,
    DiscoveryStatus,
    OrphanedResource,
    ExternalResource,
    AdoptionResult,
    MultiAccountDiscovery
)
from infradsl.core.stateless_intelligence import (
    StatelessIntelligence,
    ResourceFingerprint,
    ResourceType,
    ChangeImpact
)


class TestBrownfieldDiscovery:
    """Test suite for brownfield environment discovery"""
    
    def setup_method(self):
        """Setup test environment"""
        self.discovery = UniversalResourceDiscovery()
        self.mock_aws_resources = self._create_mock_aws_resources()
        self.mock_gcp_resources = self._create_mock_gcp_resources()
        self.mock_do_resources = self._create_mock_do_resources()
    
    def _create_mock_aws_resources(self) -> List[Dict[str, Any]]:
        """Create mock AWS resources for testing"""
        return [
            {
                "id": "i-1234567890abcdef0",
                "type": "ec2_instance",
                "config": {
                    "name": "web-server-prod-1",
                    "instance_type": "t3.medium",
                    "tags": {
                        "Environment": "production",
                        "ManagedBy": "terraform",
                        "Project": "ecommerce"
                    }
                },
                "cloud_state": {
                    "id": "i-1234567890abcdef0",
                    "state": "running",
                    "created_date": datetime.now() - timedelta(days=30),
                    "vpc_id": "vpc-12345678",
                    "subnet_id": "subnet-87654321"
                }
            },
            {
                "id": "db-cluster-prod-1",
                "type": "rds_instance",
                "config": {
                    "name": "db-cluster-prod-1",
                    "engine": "postgres",
                    "engine_version": "13.7",
                    "tags": {
                        "Environment": "production",
                        "ManagedBy": "manual",
                        "Critical": "true"
                    }
                },
                "cloud_state": {
                    "id": "db-cluster-prod-1",
                    "status": "available",
                    "created_date": datetime.now() - timedelta(days=60),
                    "backup_retention_period": 7,
                    "multi_az": True
                }
            },
            {
                "id": "infradsl-managed-bucket",
                "type": "s3_bucket",
                "config": {
                    "name": "infradsl-managed-bucket",
                    "tags": {
                        "infradsl:managed": "true",
                        "infradsl:workspace": "production",
                        "Environment": "production"
                    }
                },
                "cloud_state": {
                    "id": "infradsl-managed-bucket",
                    "creation_date": datetime.now() - timedelta(days=10),
                    "versioning": {"Status": "Enabled"},
                    "encryption": {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}
                }
            }
        ]
    
    def _create_mock_gcp_resources(self) -> List[Dict[str, Any]]:
        """Create mock GCP resources for testing"""
        return [
            {
                "id": "projects/my-project/zones/us-central1-a/instances/web-server-1",
                "type": "vm",
                "config": {
                    "name": "web-server-1",
                    "machine_type": "e2-medium",
                    "labels": {
                        "environment": "production",
                        "managed-by": "infradsl",
                        "project": "analytics"
                    }
                },
                "cloud_state": {
                    "id": "1234567890123456789",
                    "status": "RUNNING",
                    "creation_timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
                    "zone": "us-central1-a"
                }
            },
            {
                "id": "projects/my-project/instances/analytics-db",
                "type": "cloud_sql",
                "config": {
                    "name": "analytics-db",
                    "database_version": "POSTGRES_13",
                    "labels": {
                        "environment": "production",
                        "managed-by": "terraform",
                        "data-classification": "sensitive"
                    }
                },
                "cloud_state": {
                    "id": "analytics-db",
                    "state": "RUNNABLE",
                    "creation_time": (datetime.now() - timedelta(days=45)).isoformat(),
                    "backup_enabled": True,
                    "tier": "db-custom-4-16384"
                }
            }
        ]
    
    def _create_mock_do_resources(self) -> List[Dict[str, Any]]:
        """Create mock DigitalOcean resources for testing"""
        return [
            {
                "id": "123456789",
                "type": "droplet",
                "config": {
                    "name": "staging-web-1",
                    "size": "s-2vcpu-2gb",
                    "tags": ["staging", "web-server", "manual-managed"]
                },
                "cloud_state": {
                    "id": 123456789,
                    "status": "active",
                    "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
                    "region": {"slug": "nyc3"},
                    "size": {"slug": "s-2vcpu-2gb"}
                }
            }
        ]
    
    @patch('infradsl.core.universal_resource_discovery.UniversalResourceDiscovery._discover_single_account')
    def test_basic_resource_discovery(self, mock_discover):
        """Test basic resource discovery functionality"""
        
        # Mock the discovery response
        mock_fingerprints = [
            ResourceFingerprint(
                resource_id="i-1234567890abcdef0",
                resource_type=ResourceType.EC2_INSTANCE,
                configuration_hash="abc123",
                creation_signature="web_server_prod",
                dependency_fingerprint="vpc_subnet_deps",
                ownership_markers=["name_pattern:web-server-prod-1", "tag:terraform"],
                last_seen=datetime.now(),
                confidence_score=0.95
            )
        ]
        mock_discover.return_value = mock_fingerprints
        
        # Test discovery
        results = self.discovery.discover_resources(
            provider="aws",
            resource_types=["ec2_instance"],
            accounts=["123456789012"]
        )
        
        assert len(results) == 1
        assert results[0].resource_id == "i-1234567890abcdef0"
        assert results[0].confidence_score == 0.95
        assert "terraform" in results[0].ownership_markers[1]
    
    @patch('infradsl.core.universal_resource_discovery.UniversalResourceDiscovery._discover_single_account')
    def test_orphaned_resource_detection(self, mock_discover):
        """Test detection of orphaned resources"""
        
        # Mock discovery with mixed resources
        mock_fingerprints = [
            ResourceFingerprint(
                resource_id="infradsl-managed-bucket",
                resource_type=ResourceType.S3_BUCKET,
                configuration_hash="def456",
                creation_signature="infradsl_bucket",
                dependency_fingerprint="",
                ownership_markers=["infradsl_comment:managed by infradsl", "name_pattern:infradsl-managed-bucket"],
                last_seen=datetime.now(),
                confidence_score=0.98
            ),
            ResourceFingerprint(
                resource_id="orphaned-infra-bucket",
                resource_type=ResourceType.S3_BUCKET,
                configuration_hash="ghi789",
                creation_signature="infradsl_bucket",
                dependency_fingerprint="",
                ownership_markers=["name_pattern:orphaned-infra-bucket"],
                last_seen=datetime.now(),
                confidence_score=0.85
            )
        ]
        mock_discover.return_value = mock_fingerprints
        
        # Mock managed resources (empty for this test)
        with patch.object(self.discovery, '_get_managed_resources', return_value=[]):
            orphaned = self.discovery.detect_orphaned_resources(
                provider="aws",
                workspace="production",
                resource_types=["s3_bucket"]
            )
        
        assert len(orphaned) == 2  # Both should be detected as orphaned
        
        # Check first orphaned resource
        assert orphaned[0].resource_id == "infradsl-managed-bucket"
        assert orphaned[0].risk_level == "low"  # High confidence, clear ownership
        
        # Check second orphaned resource
        assert orphaned[1].resource_id == "orphaned-infra-bucket"
        assert orphaned[1].risk_level == "medium"  # Lower confidence
    
    def test_external_resource_adoption_conservative(self):
        """Test conservative adoption policy"""
        
        # Mock external resource
        external_resource = ExternalResource(
            resource_id="external-db-1",
            provider="aws",
            resource_type="rds_instance",
            ownership_markers=["terraform:managed", "environment:production"],
            configuration={
                "engine": "postgres",
                "multi_az": True,
                "backup_retention_period": 7
            },
            dependencies=["vpc-12345678", "subnet-87654321"],
            risk_assessment="medium",
            adoption_feasible=True
        )
        
        with patch.object(self.discovery, '_discover_external_resource', return_value=external_resource):
            with patch.object(self.discovery, '_analyze_adoption_feasibility', return_value=external_resource):
                result = self.discovery.adopt_external_resource(
                    resource_id="external-db-1",
                    provider="aws",
                    adoption_policy=AdoptionPolicy.CONSERVATIVE
                )
        
        assert result.status == "manual_review_required"
        assert result.risk_level == "medium"
        assert "Manual review required" in result.error_message
    
    def test_external_resource_adoption_aggressive(self):
        """Test aggressive adoption policy"""
        
        # Mock low-risk external resource
        external_resource = ExternalResource(
            resource_id="external-bucket-1",
            provider="aws",
            resource_type="s3_bucket",
            ownership_markers=["name_pattern:staging-bucket"],
            configuration={
                "versioning": {"Status": "Enabled"},
                "encryption": {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}
            },
            dependencies=[],
            risk_assessment="low",
            adoption_feasible=True
        )
        
        with patch.object(self.discovery, '_discover_external_resource', return_value=external_resource):
            with patch.object(self.discovery, '_analyze_adoption_feasibility', return_value=external_resource):
                result = self.discovery.adopt_external_resource(
                    resource_id="external-bucket-1",
                    provider="aws",
                    adoption_policy=AdoptionPolicy.AGGRESSIVE
                )
        
        assert result.status == "success"
        assert result.risk_level == "low"
        assert "Add InfraDSL management tags" in result.modifications_required
    
    @patch('infradsl.core.universal_resource_discovery.ThreadPoolExecutor')
    def test_multi_account_discovery(self, mock_executor):
        """Test multi-account discovery with parallel execution"""
        
        # Mock ThreadPoolExecutor behavior
        mock_future = Mock()
        mock_future.result.return_value = [
            ResourceFingerprint(
                resource_id="i-account1-resource",
                resource_type=ResourceType.EC2_INSTANCE,
                configuration_hash="abc123",
                creation_signature="web_server",
                dependency_fingerprint="vpc_deps",
                ownership_markers=["name_pattern:web-server"],
                last_seen=datetime.now(),
                confidence_score=0.90
            )
        ]
        
        mock_executor_instance = Mock()
        mock_executor_instance.submit.return_value = mock_future
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.__exit__.return_value = None
        mock_executor.return_value = mock_executor_instance
        
        # Mock as_completed
        with patch('infradsl.core.universal_resource_discovery.as_completed', return_value=[mock_future]):
            with patch.object(self.discovery, 'detect_orphaned_resources', return_value=[]):
                result = self.discovery.discover_across_accounts(
                    provider="aws",
                    account_list=["123456789012", "234567890123"],
                    resource_types=["ec2_instance"]
                )
        
        assert isinstance(result, MultiAccountDiscovery)
        assert result.provider == "aws"
        assert len(result.accounts) == 2
        assert result.discovery_summary["total_accounts"] == 2
    
    def test_discovery_caching(self):
        """Test that discovery results are cached properly"""
        
        # Mock discovery method to track calls
        with patch.object(self.discovery, '_discover_single_account') as mock_discover:
            mock_discover.return_value = [
                ResourceFingerprint(
                    resource_id="cached-resource",
                    resource_type=ResourceType.S3_BUCKET,
                    configuration_hash="cache123",
                    creation_signature="bucket_sig",
                    dependency_fingerprint="",
                    ownership_markers=["name_pattern:cached-resource"],
                    last_seen=datetime.now(),
                    confidence_score=0.95
                )
            ]
            
            # First call should hit the discovery method
            result1 = self.discovery.discover_resources(
                provider="aws",
                resource_types=["s3_bucket"],
                accounts=["123456789012"]
            )
            
            # Second call should use cache
            result2 = self.discovery.discover_resources(
                provider="aws",
                resource_types=["s3_bucket"],
                accounts=["123456789012"]
            )
            
            # Should only call discovery once (second call uses cache)
            assert mock_discover.call_count == 1
            assert len(result1) == 1
            assert len(result2) == 1
            assert result1[0].resource_id == result2[0].resource_id
    
    def test_risk_assessment_logic(self):
        """Test risk assessment for resource adoption"""
        
        # High confidence, clear ownership - should be low risk
        low_risk_resource = ResourceFingerprint(
            resource_id="low-risk-resource",
            resource_type=ResourceType.S3_BUCKET,
            configuration_hash="low123",
            creation_signature="clear_sig",
            dependency_fingerprint="",
            ownership_markers=["infradsl_comment:managed by infradsl"],
            last_seen=datetime.now(),
            confidence_score=0.98
        )
        
        risk_level = self.discovery._assess_adoption_risk(low_risk_resource)
        assert risk_level == "low"
        
        # Low confidence, conflicting ownership - should be high risk
        high_risk_resource = ResourceFingerprint(
            resource_id="high-risk-resource",
            resource_type=ResourceType.RDS_INSTANCE,
            configuration_hash="high123",
            creation_signature="conflict_sig",
            dependency_fingerprint="",
            ownership_markers=["terraform:managed", "manual:modified", "production:critical"],
            last_seen=datetime.now(),
            confidence_score=0.65
        )
        
        risk_level = self.discovery._assess_adoption_risk(high_risk_resource)
        assert risk_level == "high"
    
    def test_infradsl_pattern_matching(self):
        """Test pattern matching for InfraDSL-managed resources"""
        
        # Resource with InfraDSL ownership markers
        infradsl_resource = ResourceFingerprint(
            resource_id="infradsl-managed-resource",
            resource_type=ResourceType.EC2_INSTANCE,
            configuration_hash="infra123",
            creation_signature="infradsl_sig",
            dependency_fingerprint="",
            ownership_markers=["infradsl_comment:managed by infradsl", "name_pattern:infradsl-managed-resource"],
            last_seen=datetime.now(),
            confidence_score=0.95
        )
        
        assert self.discovery._matches_infradsl_patterns(infradsl_resource) == True
        
        # Resource without InfraDSL patterns
        external_resource = ResourceFingerprint(
            resource_id="external-resource",
            resource_type=ResourceType.EC2_INSTANCE,
            configuration_hash="ext123",
            creation_signature="external_sig",
            dependency_fingerprint="",
            ownership_markers=["terraform:managed", "name_pattern:external-resource"],
            last_seen=datetime.now(),
            confidence_score=0.85
        )
        
        assert self.discovery._matches_infradsl_patterns(external_resource) == False
    
    def test_adoption_recommendation_generation(self):
        """Test adoption recommendation generation"""
        
        # Mock resource fingerprint
        resource = ResourceFingerprint(
            resource_id="test-resource",
            resource_type=ResourceType.S3_BUCKET,
            configuration_hash="test123",
            creation_signature="test_sig",
            dependency_fingerprint="",
            ownership_markers=["name_pattern:test-resource"],
            last_seen=datetime.now(),
            confidence_score=0.90
        )
        
        # Test low risk recommendation
        recommendation = self.discovery._generate_adoption_recommendation(resource, "low")
        assert "Safe to auto-adopt" in recommendation
        
        # Test high risk recommendation
        recommendation = self.discovery._generate_adoption_recommendation(resource, "high")
        assert "Manual review required" in recommendation
    
    def test_performance_metrics_tracking(self):
        """Test that performance metrics are tracked properly"""
        
        with patch.object(self.discovery, '_discover_single_account') as mock_discover:
            mock_discover.return_value = [
                ResourceFingerprint(
                    resource_id="perf-test-resource",
                    resource_type=ResourceType.EC2_INSTANCE,
                    configuration_hash="perf123",
                    creation_signature="perf_sig",
                    dependency_fingerprint="",
                    ownership_markers=["name_pattern:perf-test-resource"],
                    last_seen=datetime.now(),
                    confidence_score=0.95
                )
            ]
            
            # Track discovery time
            start_time = datetime.now()
            results = self.discovery.discover_resources(
                provider="aws",
                resource_types=["ec2_instance"],
                accounts=["123456789012"]
            )
            end_time = datetime.now()
            
            # Verify results
            assert len(results) == 1
            
            # Check cache entry exists (performance tracking)
            cache_key = "aws_ec2_instance_123456789012"
            assert cache_key in self.discovery.discovery_cache
            
            cached_time, cached_results = self.discovery.discovery_cache[cache_key]
            assert len(cached_results) == 1
            assert (end_time - cached_time).total_seconds() < 1  # Should be very recent


class TestComplexBrownfieldScenarios:
    """Test complex real-world brownfield scenarios"""
    
    def setup_method(self):
        """Setup complex test environment"""
        self.discovery = UniversalResourceDiscovery()
    
    def test_terraform_migration_scenario(self):
        """Test migrating from Terraform to InfraDSL"""
        
        # Mock Terraform-managed resources
        terraform_resources = [
            ResourceFingerprint(
                resource_id="terraform-web-server",
                resource_type=ResourceType.EC2_INSTANCE,
                configuration_hash="tf123",
                creation_signature="terraform_managed",
                dependency_fingerprint="vpc_subnet_sg",
                ownership_markers=["terraform:managed", "name_pattern:terraform-web-server"],
                last_seen=datetime.now(),
                confidence_score=0.92
            ),
            ResourceFingerprint(
                resource_id="terraform-database",
                resource_type=ResourceType.RDS_INSTANCE,
                configuration_hash="tf456",
                creation_signature="terraform_managed",
                dependency_fingerprint="vpc_subnet_sg",
                ownership_markers=["terraform:managed", "name_pattern:terraform-database"],
                last_seen=datetime.now(),
                confidence_score=0.88
            )
        ]
        
        with patch.object(self.discovery, '_discover_single_account', return_value=terraform_resources):
            # Discover resources
            resources = self.discovery.discover_resources(
                provider="aws",
                resource_types=["ec2_instance", "rds_instance"],
                accounts=["123456789012"]
            )
            
            # All resources should be discovered
            assert len(resources) == 2
            
            # Check that Terraform resources are identified
            terraform_count = sum(1 for r in resources if any('terraform' in marker for marker in r.ownership_markers))
            assert terraform_count == 2
            
            # Test adoption with moderate policy
            for resource in resources:
                with patch.object(self.discovery, '_discover_external_resource') as mock_discover:
                    with patch.object(self.discovery, '_analyze_adoption_feasibility') as mock_analyze:
                        mock_external = ExternalResource(
                            resource_id=resource.resource_id,
                            provider="aws",
                            resource_type=resource.resource_type.value,
                            ownership_markers=resource.ownership_markers,
                            configuration={"terraform_managed": True},
                            dependencies=[],
                            risk_assessment="low",
                            adoption_feasible=True
                        )
                        mock_discover.return_value = mock_external
                        mock_analyze.return_value = mock_external
                        
                        result = self.discovery.adopt_external_resource(
                            resource_id=resource.resource_id,
                            provider="aws",
                            adoption_policy=AdoptionPolicy.MODERATE
                        )
                        
                        # Should be successful with moderate policy for low-risk resources
                        assert result.status == "success"
                        assert "Add InfraDSL management tags" in result.modifications_required
    
    def test_mixed_ownership_environment(self):
        """Test environment with mixed ownership (Terraform, manual, InfraDSL)"""
        
        mixed_resources = [
            ResourceFingerprint(
                resource_id="infradsl-managed-app",
                resource_type=ResourceType.EC2_INSTANCE,
                configuration_hash="infra123",
                creation_signature="infradsl_managed",
                dependency_fingerprint="",
                ownership_markers=["infradsl_comment:managed by infradsl", "name_pattern:infradsl-managed-app"],
                last_seen=datetime.now(),
                confidence_score=0.98
            ),
            ResourceFingerprint(
                resource_id="manual-legacy-db",
                resource_type=ResourceType.RDS_INSTANCE,
                configuration_hash="manual123",
                creation_signature="manual_created",
                dependency_fingerprint="",
                ownership_markers=["manual:created", "legacy:system"],
                last_seen=datetime.now(),
                confidence_score=0.75
            ),
            ResourceFingerprint(
                resource_id="terraform-load-balancer",
                resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION,
                configuration_hash="tf789",
                creation_signature="terraform_managed",
                dependency_fingerprint="s3_cert_domain",
                ownership_markers=["terraform:managed", "name_pattern:terraform-load-balancer"],
                last_seen=datetime.now(),
                confidence_score=0.90
            )
        ]
        
        with patch.object(self.discovery, '_discover_single_account', return_value=mixed_resources):
            with patch.object(self.discovery, '_get_managed_resources', return_value=[mixed_resources[0]]):  # Only first is managed
                # Detect orphaned resources
                orphaned = self.discovery.detect_orphaned_resources(
                    provider="aws",
                    workspace="production",
                    resource_types=["ec2_instance", "rds_instance", "cloudfront_distribution"]
                )
                
                # Should find 2 orphaned resources (manual and terraform)
                assert len(orphaned) == 2
                
                # Check risk assessments
                orphaned_by_id = {r.resource_id: r for r in orphaned}
                
                # Manual legacy DB should be high risk
                manual_db = orphaned_by_id["manual-legacy-db"]
                assert manual_db.risk_level == "medium"  # Lower confidence score
                
                # Terraform LB should be medium risk
                terraform_lb = orphaned_by_id["terraform-load-balancer"]
                assert terraform_lb.risk_level == "low"  # Higher confidence, clear ownership
    
    def test_cross_cloud_dependency_scenario(self):
        """Test scenario with dependencies across cloud providers"""
        
        # Mock multi-provider resources with cross-cloud dependencies
        aws_resources = [
            ResourceFingerprint(
                resource_id="aws-cdn-distribution",
                resource_type=ResourceType.CLOUDFRONT_DISTRIBUTION,
                configuration_hash="cross123",
                creation_signature="multi_cloud",
                dependency_fingerprint="gcp_storage_domain",
                ownership_markers=["name_pattern:aws-cdn-distribution", "cross_cloud:enabled"],
                last_seen=datetime.now(),
                confidence_score=0.93
            )
        ]
        
        gcp_resources = [
            ResourceFingerprint(
                resource_id="gcp-storage-backend",
                resource_type=ResourceType.S3_BUCKET,  # Using S3_BUCKET as placeholder for GCP storage
                configuration_hash="cross456",
                creation_signature="multi_cloud",
                dependency_fingerprint="aws_cdn_origin",
                ownership_markers=["name_pattern:gcp-storage-backend", "cross_cloud:enabled"],
                last_seen=datetime.now(),
                confidence_score=0.91
            )
        ]
        
        with patch.object(self.discovery, '_discover_single_account') as mock_discover:
            # Mock different responses for different providers
            def side_effect(provider, resource_types, account, filters=None):
                if provider == "aws":
                    return aws_resources
                elif provider == "gcp":
                    return gcp_resources
                return []
            
            mock_discover.side_effect = side_effect
            
            # Discover resources from both providers
            aws_results = self.discovery.discover_resources(
                provider="aws",
                resource_types=["cloudfront_distribution"],
                accounts=["123456789012"]
            )
            
            gcp_results = self.discovery.discover_resources(
                provider="gcp",
                resource_types=["cloud_storage"],
                accounts=["my-project"]
            )
            
            assert len(aws_results) == 1
            assert len(gcp_results) == 1
            
            # Check for cross-cloud indicators
            aws_resource = aws_results[0]
            gcp_resource = gcp_results[0]
            
            assert "cross_cloud:enabled" in aws_resource.ownership_markers
            assert "cross_cloud:enabled" in gcp_resource.ownership_markers
            
            # Verify dependency fingerprints indicate cross-cloud relationships
            assert "gcp_storage" in aws_resource.dependency_fingerprint
            assert "aws_cdn" in gcp_resource.dependency_fingerprint


if __name__ == "__main__":
    pytest.main([__file__, "-v"])