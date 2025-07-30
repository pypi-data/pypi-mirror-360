"""
Comprehensive Dependency Tracking System for InfraDSL
Advanced dependency analysis for mixed infrastructure environments
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
try:
    import networkx as nx
except ImportError:
    nx = None  # NetworkX not available
from pathlib import Path

from .stateless_intelligence import StatelessIntelligence, ResourceFingerprint, ResourceType
from .universal_resource_discovery import UniversalResourceDiscovery


class DependencyType(Enum):
    """Types of dependencies between resources"""
    NETWORK = "network"                    # VPC, subnet, security group dependencies
    COMPUTE = "compute"                    # Instance-to-instance dependencies
    STORAGE = "storage"                    # Storage access dependencies
    DATABASE = "database"                  # Database connection dependencies
    LOAD_BALANCER = "load_balancer"        # Load balancer target dependencies
    DNS = "dns"                           # DNS resolution dependencies
    CERTIFICATE = "certificate"           # SSL/TLS certificate dependencies
    IAM = "iam"                           # Identity and access dependencies
    CONFIGURATION = "configuration"       # Configuration-based dependencies
    CROSS_CLOUD = "cross_cloud"          # Dependencies spanning cloud providers
    CROSS_TOOL = "cross_tool"            # Dependencies across management tools


class DependencyStrength(Enum):
    """Strength/criticality of dependencies"""
    CRITICAL = "critical"        # Breaking this dependency causes service failure
    STRONG = "strong"           # Breaking this dependency causes degraded performance
    WEAK = "weak"              # Breaking this dependency causes minor issues
    OPTIONAL = "optional"       # Breaking this dependency has minimal impact


class ManagementTool(Enum):
    """Infrastructure management tools"""
    INFRADSL = "infradsl"
    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"
    MANUAL = "manual"
    ANSIBLE = "ansible"
    PULUMI = "pulumi"
    UNKNOWN = "unknown"


@dataclass
class Dependency:
    """Represents a dependency between two resources"""
    source_resource_id: str
    target_resource_id: str
    source_provider: str
    target_provider: str
    dependency_type: DependencyType
    strength: DependencyStrength
    description: str
    discovered_at: datetime
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Management tool information
    source_managed_by: ManagementTool = ManagementTool.UNKNOWN
    target_managed_by: ManagementTool = ManagementTool.UNKNOWN
    
    # Change impact
    estimated_impact_if_broken: str = "unknown"
    mitigation_strategies: List[str] = field(default_factory=list)


@dataclass
class DependencyChain:
    """Represents a chain of dependencies"""
    chain_id: str
    resources: List[str]
    total_strength: str  # Overall strength of the chain
    cross_cloud: bool
    cross_tool: bool
    length: int
    risk_level: str
    critical_points: List[str]  # Single points of failure


@dataclass
class ImpactAnalysis:
    """Analysis of impact when a resource is modified/removed"""
    resource_id: str
    direct_dependents: List[str]
    indirect_dependents: List[str]
    affected_services: List[str]
    estimated_downtime: int  # seconds
    business_impact: str
    mitigation_required: bool
    recommendations: List[str]


@dataclass
class DependencySnapshot:
    """Snapshot of dependency state at a point in time"""
    snapshot_id: str
    timestamp: datetime
    total_resources: int
    total_dependencies: int
    cross_cloud_dependencies: int
    cross_tool_dependencies: int
    critical_dependencies: int
    orphaned_resources: List[str]
    circular_dependencies: List[List[str]]
    single_points_of_failure: List[str]


class DependencyTracker:
    """
    Comprehensive dependency tracking system for mixed infrastructure
    
    Features:
    - Multi-cloud dependency mapping
    - Cross-tool dependency tracking
    - Real-time dependency discovery
    - Impact analysis and blast radius calculation
    - Dependency visualization and reporting
    - Circular dependency detection
    - Single point of failure identification
    """
    
    def __init__(self):
        self.discovery = UniversalResourceDiscovery()
        self.stateless_intelligence = StatelessIntelligence()
        self.logger = logging.getLogger(__name__)
        
        # Dependency graph using NetworkX (if available)
        if nx:
            self.dependency_graph = nx.DiGraph()
        else:
            self.dependency_graph = None
            self.logger.warning("NetworkX not available - dependency graph features disabled")
        
        # Caching for performance
        self.dependency_cache: Dict[str, Tuple[datetime, List[Dependency]]] = {}
        self.analysis_cache: Dict[str, Tuple[datetime, ImpactAnalysis]] = {}
        self.cache_ttl = timedelta(minutes=30)
        
        # Discovery patterns for different dependency types
        self.dependency_patterns = self._initialize_dependency_patterns()
        
        # Provider-specific dependency analyzers
        self.provider_analyzers = {
            "aws": self._get_aws_analyzer,
            "gcp": self._get_gcp_analyzer,
            "digitalocean": self._get_do_analyzer
        }
        
        # Snapshots for historical tracking
        self.snapshots: List[DependencySnapshot] = []
    
    def discover_dependencies(self, providers: List[str], 
                            include_cross_cloud: bool = True,
                            include_cross_tool: bool = True,
                            deep_analysis: bool = False) -> List[Dependency]:
        """
        Discover all dependencies across specified providers
        
        Args:
            providers: List of cloud providers to analyze
            include_cross_cloud: Whether to analyze cross-cloud dependencies
            include_cross_tool: Whether to analyze cross-tool dependencies
            deep_analysis: Whether to perform deep dependency analysis
            
        Returns:
            List of discovered dependencies
        """
        
        cache_key = f"discovery_{','.join(sorted(providers))}_{include_cross_cloud}_{include_cross_tool}"
        
        # Check cache first
        if cache_key in self.dependency_cache:
            cached_time, cached_deps = self.dependency_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                self.logger.info(f"Returning cached dependencies for {cache_key}")
                return cached_deps
        
        self.logger.info(f"Starting dependency discovery for providers: {providers}")
        start_time = datetime.now()
        
        all_dependencies = []
        all_resources = {}
        
        # Step 1: Discover all resources from each provider
        for provider in providers:
            self.logger.info(f"Discovering resources from {provider}")
            resources = self.discovery.discover_resources(
                provider=provider,
                resource_types=self._get_all_resource_types(provider)
            )
            all_resources[provider] = resources
            self.logger.info(f"Found {len(resources)} resources in {provider}")
        
        # Step 2: Analyze intra-provider dependencies
        for provider, resources in all_resources.items():
            provider_deps = self._analyze_provider_dependencies(provider, resources, deep_analysis)
            all_dependencies.extend(provider_deps)
            self.logger.info(f"Found {len(provider_deps)} dependencies within {provider}")
        
        # Step 3: Analyze cross-cloud dependencies
        if include_cross_cloud and len(providers) > 1:
            cross_cloud_deps = self._analyze_cross_cloud_dependencies(all_resources, deep_analysis)
            all_dependencies.extend(cross_cloud_deps)
            self.logger.info(f"Found {len(cross_cloud_deps)} cross-cloud dependencies")
        
        # Step 4: Analyze cross-tool dependencies
        if include_cross_tool:
            cross_tool_deps = self._analyze_cross_tool_dependencies(all_resources, deep_analysis)
            all_dependencies.extend(cross_tool_deps)
            self.logger.info(f"Found {len(cross_tool_deps)} cross-tool dependencies")
        
        # Step 5: Update dependency graph
        self._update_dependency_graph(all_dependencies)
        
        # Cache results
        self.dependency_cache[cache_key] = (datetime.now(), all_dependencies)
        
        discovery_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Dependency discovery completed in {discovery_time:.2f} seconds: "
                        f"{len(all_dependencies)} total dependencies")
        
        return all_dependencies
    
    def analyze_impact(self, resource_id: str, change_type: str = "remove") -> ImpactAnalysis:
        """
        Analyze the impact of changing or removing a resource
        
        Args:
            resource_id: Resource to analyze
            change_type: Type of change (remove, modify, relocate)
            
        Returns:
            ImpactAnalysis with detailed impact assessment
        """
        
        cache_key = f"impact_{resource_id}_{change_type}"
        
        # Check cache
        if cache_key in self.analysis_cache:
            cached_time, cached_analysis = self.analysis_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_analysis
        
        self.logger.info(f"Analyzing impact of {change_type} for resource {resource_id}")
        
        # Find all resources that depend on this resource
        direct_dependents = []
        indirect_dependents = []
        
        if self.dependency_graph and resource_id in self.dependency_graph:
            # Direct dependents (resources that directly depend on this one)
            direct_dependents = list(self.dependency_graph.successors(resource_id))
            
            # Indirect dependents (resources that depend on direct dependents, etc.)
            for direct_dep in direct_dependents:
                if nx:  # Only if NetworkX is available
                    indirect_paths = nx.single_source_shortest_path(
                        self.dependency_graph, direct_dep, cutoff=5
                    )
                    for target in indirect_paths:
                        if target != direct_dep and target not in direct_dependents:
                            indirect_dependents.append(target)
        
        # Analyze affected services
        affected_services = self._identify_affected_services(
            direct_dependents + indirect_dependents
        )
        
        # Estimate downtime
        estimated_downtime = self._estimate_downtime(
            resource_id, direct_dependents, indirect_dependents, change_type
        )
        
        # Assess business impact
        business_impact = self._assess_business_impact(
            resource_id, direct_dependents, indirect_dependents
        )
        
        # Determine if mitigation is required
        mitigation_required = (
            len(direct_dependents) > 0 or 
            estimated_downtime > 300 or 
            business_impact in ["high", "critical"]
        )
        
        # Generate recommendations
        recommendations = self._generate_impact_recommendations(
            resource_id, direct_dependents, indirect_dependents, change_type
        )
        
        analysis = ImpactAnalysis(
            resource_id=resource_id,
            direct_dependents=direct_dependents,
            indirect_dependents=indirect_dependents,
            affected_services=affected_services,
            estimated_downtime=estimated_downtime,
            business_impact=business_impact,
            mitigation_required=mitigation_required,
            recommendations=recommendations
        )
        
        # Cache the analysis
        self.analysis_cache[cache_key] = (datetime.now(), analysis)
        
        return analysis
    
    def find_dependency_chains(self, max_length: int = 10) -> List[DependencyChain]:
        """
        Find dependency chains in the infrastructure
        
        Args:
            max_length: Maximum chain length to consider
            
        Returns:
            List of dependency chains found
        """
        
        self.logger.info("Finding dependency chains")
        chains = []
        
        # Find all simple paths in the dependency graph
        for source in self.dependency_graph.nodes():
            for target in self.dependency_graph.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.dependency_graph, source, target, cutoff=max_length
                        ))
                        
                        for path in paths:
                            if len(path) >= 3:  # Only consider chains of 3+ resources
                                chain = self._create_dependency_chain(path)
                                chains.append(chain)
                    except nx.NetworkXNoPath:
                        continue
        
        # Sort by risk level and length
        chains.sort(key=lambda x: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x.risk_level, 0),
            x.length
        ), reverse=True)
        
        self.logger.info(f"Found {len(chains)} dependency chains")
        return chains
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the infrastructure
        
        Returns:
            List of cycles found (each cycle is a list of resource IDs)
        """
        
        self.logger.info("Detecting circular dependencies")
        
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            
            if cycles:
                self.logger.warning(f"Found {len(cycles)} circular dependencies")
                for i, cycle in enumerate(cycles):
                    self.logger.warning(f"Cycle {i+1}: {' -> '.join(cycle)} -> {cycle[0]}")
            else:
                self.logger.info("No circular dependencies detected")
            
            return cycles
            
        except Exception as e:
            self.logger.error(f"Error detecting circular dependencies: {str(e)}")
            return []
    
    def find_single_points_of_failure(self) -> List[str]:
        """
        Identify single points of failure in the infrastructure
        
        Returns:
            List of resource IDs that are single points of failure
        """
        
        self.logger.info("Finding single points of failure")
        spofs = []
        
        # A resource is a SPOF if removing it disconnects the graph
        for node in self.dependency_graph.nodes():
            # Create a copy of the graph without this node
            temp_graph = self.dependency_graph.copy()
            temp_graph.remove_node(node)
            
            # Check if the graph becomes disconnected
            if not nx.is_connected(temp_graph.to_undirected()):
                # Check if this node has significant impact
                dependents = list(self.dependency_graph.successors(node))
                if len(dependents) > 1:  # Must affect multiple resources
                    spofs.append(node)
        
        self.logger.info(f"Found {len(spofs)} single points of failure: {spofs}")
        return spofs
    
    def create_dependency_snapshot(self) -> DependencySnapshot:
        """
        Create a snapshot of current dependency state
        
        Returns:
            DependencySnapshot with current state
        """
        
        self.logger.info("Creating dependency snapshot")
        
        # Count different types of dependencies
        total_deps = self.dependency_graph.number_of_edges()
        cross_cloud_deps = 0
        cross_tool_deps = 0
        critical_deps = 0
        
        for source, target, data in self.dependency_graph.edges(data=True):
            dependency = data.get('dependency')
            if dependency:
                if dependency.dependency_type == DependencyType.CROSS_CLOUD:
                    cross_cloud_deps += 1
                if dependency.dependency_type == DependencyType.CROSS_TOOL:
                    cross_tool_deps += 1
                if dependency.strength == DependencyStrength.CRITICAL:
                    critical_deps += 1
        
        # Find orphaned resources (no dependencies in or out)
        orphaned = [
            node for node in self.dependency_graph.nodes()
            if self.dependency_graph.degree(node) == 0
        ]
        
        # Detect circular dependencies
        circular_deps = self.detect_circular_dependencies()
        
        # Find single points of failure
        spofs = self.find_single_points_of_failure()
        
        snapshot = DependencySnapshot(
            snapshot_id=f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            total_resources=self.dependency_graph.number_of_nodes(),
            total_dependencies=total_deps,
            cross_cloud_dependencies=cross_cloud_deps,
            cross_tool_dependencies=cross_tool_deps,
            critical_dependencies=critical_deps,
            orphaned_resources=orphaned,
            circular_dependencies=circular_deps,
            single_points_of_failure=spofs
        )
        
        self.snapshots.append(snapshot)
        self.logger.info(f"Created snapshot {snapshot.snapshot_id}")
        
        return snapshot
    
    def visualize_dependencies(self, output_format: str = "graphml") -> str:
        """
        Export dependency graph for visualization
        
        Args:
            output_format: Format for export (graphml, gexf, json)
            
        Returns:
            Path to exported file
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dependency_graph_{timestamp}.{output_format}"
        filepath = f"/tmp/{filename}"
        
        if output_format == "graphml":
            nx.write_graphml(self.dependency_graph, filepath)
        elif output_format == "gexf":
            nx.write_gexf(self.dependency_graph, filepath)
        elif output_format == "json":
            data = nx.node_link_data(self.dependency_graph)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Exported dependency graph to {filepath}")
        return filepath
    
    def _analyze_provider_dependencies(self, provider: str, 
                                     resources: List[ResourceFingerprint],
                                     deep_analysis: bool) -> List[Dependency]:
        """Analyze dependencies within a single provider"""
        
        dependencies = []
        analyzer = self.provider_analyzers[provider]()
        
        for resource in resources:
            resource_deps = analyzer.analyze_resource_dependencies(resource, resources, deep_analysis)
            dependencies.extend(resource_deps)
        
        return dependencies
    
    def _analyze_cross_cloud_dependencies(self, all_resources: Dict[str, List[ResourceFingerprint]],
                                        deep_analysis: bool) -> List[Dependency]:
        """Analyze dependencies that span cloud providers"""
        
        cross_cloud_deps = []
        
        # Check for DNS dependencies pointing across clouds
        for source_provider, source_resources in all_resources.items():
            for target_provider, target_resources in all_resources.items():
                if source_provider != target_provider:
                    deps = self._find_cross_provider_dependencies(
                        source_provider, source_resources,
                        target_provider, target_resources,
                        deep_analysis
                    )
                    cross_cloud_deps.extend(deps)
        
        return cross_cloud_deps
    
    def _analyze_cross_tool_dependencies(self, all_resources: Dict[str, List[ResourceFingerprint]],
                                       deep_analysis: bool) -> List[Dependency]:
        """Analyze dependencies across different management tools"""
        
        cross_tool_deps = []
        
        # Group resources by management tool
        resources_by_tool = defaultdict(list)
        for provider, resources in all_resources.items():
            for resource in resources:
                tool = self._identify_management_tool(resource)
                resources_by_tool[tool].append((provider, resource))
        
        # Find dependencies between different tools
        for source_tool, source_resources in resources_by_tool.items():
            for target_tool, target_resources in resources_by_tool.items():
                if source_tool != target_tool:
                    deps = self._find_cross_tool_dependencies(
                        source_tool, source_resources,
                        target_tool, target_resources,
                        deep_analysis
                    )
                    cross_tool_deps.extend(deps)
        
        return cross_tool_deps
    
    def _update_dependency_graph(self, dependencies: List[Dependency]):
        """Update the internal dependency graph"""
        
        # Clear existing graph (if available)
        if self.dependency_graph:
            self.dependency_graph.clear()
        
        # Add all dependencies to the graph (if available)
        if self.dependency_graph:
            for dep in dependencies:
                self.dependency_graph.add_edge(
                    dep.source_resource_id,
                    dep.target_resource_id,
                    dependency=dep,
                    weight=self._dependency_weight(dep)
                )
    
    def _dependency_weight(self, dependency: Dependency) -> float:
        """Calculate weight for a dependency based on strength and confidence"""
        
        strength_weights = {
            DependencyStrength.CRITICAL: 4.0,
            DependencyStrength.STRONG: 3.0,
            DependencyStrength.WEAK: 2.0,
            DependencyStrength.OPTIONAL: 1.0
        }
        
        return strength_weights.get(dependency.strength, 2.0) * dependency.confidence
    
    def _create_dependency_chain(self, path: List[str]) -> DependencyChain:
        """Create a DependencyChain object from a path"""
        
        # Analyze the chain
        cross_cloud = self._is_cross_cloud_chain(path)
        cross_tool = self._is_cross_tool_chain(path)
        
        # Determine overall strength
        min_strength = DependencyStrength.CRITICAL
        for i in range(len(path) - 1):
            if self.dependency_graph.has_edge(path[i], path[i + 1]):
                edge_data = self.dependency_graph[path[i]][path[i + 1]]
                dep = edge_data.get('dependency')
                if dep and dep.strength.value < min_strength.value:
                    min_strength = dep.strength
        
        # Assess risk level
        risk_level = self._assess_chain_risk(path, cross_cloud, cross_tool, min_strength)
        
        # Find critical points (nodes with high out-degree in the chain)
        critical_points = []
        for node in path:
            if self.dependency_graph.out_degree(node) > 2:
                critical_points.append(node)
        
        return DependencyChain(
            chain_id=hashlib.md5('->'.join(path).encode()).hexdigest()[:12],
            resources=path,
            total_strength=min_strength.value,
            cross_cloud=cross_cloud,
            cross_tool=cross_tool,
            length=len(path),
            risk_level=risk_level,
            critical_points=critical_points
        )
    
    def _is_cross_cloud_chain(self, path: List[str]) -> bool:
        """Check if chain spans multiple cloud providers"""
        
        providers = set()
        for resource_id in path:
            # Extract provider from resource ID (simplified)
            if resource_id.startswith('i-'):
                providers.add('aws')
            elif 'projects/' in resource_id:
                providers.add('gcp')
            elif resource_id.isdigit():
                providers.add('digitalocean')
        
        return len(providers) > 1
    
    def _is_cross_tool_chain(self, path: List[str]) -> bool:
        """Check if chain spans multiple management tools"""
        
        tools = set()
        for resource_id in path:
            # This would need to look up the actual resource to determine tool
            # For now, use simplified heuristics
            if 'terraform' in resource_id:
                tools.add('terraform')
            elif 'infradsl' in resource_id:
                tools.add('infradsl')
            else:
                tools.add('unknown')
        
        return len(tools) > 1
    
    def _assess_chain_risk(self, path: List[str], cross_cloud: bool, 
                          cross_tool: bool, min_strength: DependencyStrength) -> str:
        """Assess risk level of a dependency chain"""
        
        risk_score = 0
        
        # Length factor
        if len(path) > 5:
            risk_score += 2
        elif len(path) > 3:
            risk_score += 1
        
        # Cross-cloud factor
        if cross_cloud:
            risk_score += 2
        
        # Cross-tool factor
        if cross_tool:
            risk_score += 1
        
        # Strength factor
        if min_strength == DependencyStrength.CRITICAL:
            risk_score += 2
        elif min_strength == DependencyStrength.STRONG:
            risk_score += 1
        
        # Map score to risk level
        if risk_score >= 6:
            return "critical"
        elif risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _identify_affected_services(self, dependent_resources: List[str]) -> List[str]:
        """Identify services that would be affected"""
        
        services = set()
        
        for resource_id in dependent_resources:
            # Extract service information from resource ID or tags
            if 'web' in resource_id.lower():
                services.add('web-service')
            elif 'api' in resource_id.lower():
                services.add('api-service')
            elif 'db' in resource_id.lower() or 'database' in resource_id.lower():
                services.add('database-service')
            elif 'lb' in resource_id.lower() or 'load' in resource_id.lower():
                services.add('load-balancer-service')
        
        return list(services)
    
    def _estimate_downtime(self, resource_id: str, direct_deps: List[str], 
                          indirect_deps: List[str], change_type: str) -> int:
        """Estimate downtime in seconds"""
        
        base_downtime = {
            "remove": 300,    # 5 minutes
            "modify": 60,     # 1 minute
            "relocate": 180   # 3 minutes
        }.get(change_type, 300)
        
        # Multiply by number of affected resources
        affected_count = len(direct_deps) + len(indirect_deps)
        multiplier = min(1 + (affected_count * 0.1), 3.0)  # Cap at 3x
        
        return int(base_downtime * multiplier)
    
    def _assess_business_impact(self, resource_id: str, direct_deps: List[str], 
                              indirect_deps: List[str]) -> str:
        """Assess business impact level"""
        
        total_affected = len(direct_deps) + len(indirect_deps)
        
        # Check for production indicators
        prod_indicators = ['prod', 'production', 'critical']
        is_production = any(indicator in resource_id.lower() for indicator in prod_indicators)
        
        if is_production and total_affected > 5:
            return "critical"
        elif is_production or total_affected > 3:
            return "high"
        elif total_affected > 1:
            return "medium"
        else:
            return "low"
    
    def _generate_impact_recommendations(self, resource_id: str, direct_deps: List[str], 
                                       indirect_deps: List[str], change_type: str) -> List[str]:
        """Generate recommendations for mitigating impact"""
        
        recommendations = []
        
        if len(direct_deps) > 0:
            recommendations.append("Update dependent resources before making changes")
        
        if len(indirect_deps) > 2:
            recommendations.append("Consider phased rollout to minimize impact")
        
        if change_type == "remove":
            recommendations.append("Ensure all data is backed up before removal")
            recommendations.append("Verify no critical processes depend on this resource")
        
        if len(direct_deps) + len(indirect_deps) > 5:
            recommendations.append("Schedule change during maintenance window")
            recommendations.append("Prepare rapid rollback procedure")
        
        return recommendations
    
    def _find_cross_provider_dependencies(self, source_provider: str, source_resources: List[ResourceFingerprint],
                                        target_provider: str, target_resources: List[ResourceFingerprint],
                                        deep_analysis: bool) -> List[Dependency]:
        """Find dependencies between different cloud providers"""
        
        dependencies = []
        
        # DNS dependencies (common cross-cloud pattern)
        for source_resource in source_resources:
            if source_resource.resource_type == ResourceType.ROUTE53_RECORD:
                # Check if DNS points to resources in other providers
                for target_resource in target_resources:
                    if self._has_dns_dependency(source_resource, target_resource):
                        dep = Dependency(
                            source_resource_id=source_resource.resource_id,
                            target_resource_id=target_resource.resource_id,
                            source_provider=source_provider,
                            target_provider=target_provider,
                            dependency_type=DependencyType.CROSS_CLOUD,
                            strength=DependencyStrength.STRONG,
                            description=f"DNS resolution from {source_provider} to {target_provider}",
                            discovered_at=datetime.now(),
                            confidence=0.85
                        )
                        dependencies.append(dep)
        
        return dependencies
    
    def _find_cross_tool_dependencies(self, source_tool: ManagementTool, source_resources: List[Tuple[str, ResourceFingerprint]],
                                    target_tool: ManagementTool, target_resources: List[Tuple[str, ResourceFingerprint]],
                                    deep_analysis: bool) -> List[Dependency]:
        """Find dependencies between different management tools"""
        
        dependencies = []
        
        # Look for shared infrastructure (VPCs, security groups, etc.)
        for source_provider, source_resource in source_resources:
            for target_provider, target_resource in target_resources:
                if source_provider == target_provider:  # Same cloud, different tools
                    if self._has_shared_infrastructure(source_resource, target_resource):
                        dep = Dependency(
                            source_resource_id=source_resource.resource_id,
                            target_resource_id=target_resource.resource_id,
                            source_provider=source_provider,
                            target_provider=target_provider,
                            dependency_type=DependencyType.CROSS_TOOL,
                            strength=DependencyStrength.WEAK,
                            description=f"Shared infrastructure between {source_tool.value} and {target_tool.value}",
                            discovered_at=datetime.now(),
                            confidence=0.70,
                            source_managed_by=source_tool,
                            target_managed_by=target_tool
                        )
                        dependencies.append(dep)
        
        return dependencies
    
    def _has_dns_dependency(self, source_resource: ResourceFingerprint, 
                          target_resource: ResourceFingerprint) -> bool:
        """Check if there's a DNS dependency between resources"""
        # Simplified check - would be more sophisticated in practice
        return "dns" in source_resource.dependency_fingerprint and target_resource.resource_id in source_resource.dependency_fingerprint
    
    def _has_shared_infrastructure(self, resource1: ResourceFingerprint, 
                                 resource2: ResourceFingerprint) -> bool:
        """Check if resources share infrastructure (VPC, security groups, etc.)"""
        # Simplified check - would be more sophisticated in practice
        return len(set(resource1.dependency_fingerprint.split(',')) & 
                  set(resource2.dependency_fingerprint.split(','))) > 0
    
    def _identify_management_tool(self, resource: ResourceFingerprint) -> ManagementTool:
        """Identify which tool manages a resource"""
        
        for marker in resource.ownership_markers:
            marker_lower = marker.lower()
            if 'terraform' in marker_lower:
                return ManagementTool.TERRAFORM
            elif 'infradsl' in marker_lower:
                return ManagementTool.INFRADSL
            elif 'cloudformation' in marker_lower:
                return ManagementTool.CLOUDFORMATION
            elif 'ansible' in marker_lower:
                return ManagementTool.ANSIBLE
            elif 'pulumi' in marker_lower:
                return ManagementTool.PULUMI
            elif 'manual' in marker_lower:
                return ManagementTool.MANUAL
        
        return ManagementTool.UNKNOWN
    
    def _initialize_dependency_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for dependency discovery"""
        
        return {
            "network_patterns": [
                r"vpc-[a-f0-9]+",
                r"subnet-[a-f0-9]+",
                r"sg-[a-f0-9]+"
            ],
            "dns_patterns": [
                r"[a-zA-Z0-9.-]+\.(com|org|net|io)",
                r"[a-zA-Z0-9-]+\.amazonaws\.com",
                r"[a-zA-Z0-9-]+\.googleapis\.com"
            ],
            "certificate_patterns": [
                r"arn:aws:acm:[^:]+:[^:]+:certificate/[a-f0-9-]+",
                r"projects/[^/]+/global/sslCertificates/[^/]+"
            ]
        }
    
    def _get_all_resource_types(self, provider: str) -> List[str]:
        """Get all resource types for a provider"""
        
        types = {
            "aws": ["ec2_instance", "rds_instance", "s3_bucket", "lambda_function", 
                   "cloudfront_distribution", "route53_record", "load_balancer"],
            "gcp": ["vm", "cloud_sql", "cloud_storage", "cloud_functions", 
                   "load_balancer", "cloud_dns"],
            "digitalocean": ["droplet", "database", "load_balancer", "spaces"]
        }
        
        return types.get(provider, [])
    
    def _get_aws_analyzer(self):
        """Get AWS-specific dependency analyzer"""
        
        class AWSAnalyzer:
            def analyze_resource_dependencies(self, resource, all_resources, deep_analysis):
                dependencies = []
                
                # Network dependencies
                if hasattr(resource, 'vpc_id'):
                    for other in all_resources:
                        if other.resource_id != resource.resource_id and hasattr(other, 'vpc_id'):
                            if getattr(other, 'vpc_id', None) == getattr(resource, 'vpc_id', None):
                                dep = Dependency(
                                    source_resource_id=resource.resource_id,
                                    target_resource_id=other.resource_id,
                                    source_provider="aws",
                                    target_provider="aws",
                                    dependency_type=DependencyType.NETWORK,
                                    strength=DependencyStrength.WEAK,
                                    description="Shared VPC dependency",
                                    discovered_at=datetime.now(),
                                    confidence=0.9
                                )
                                dependencies.append(dep)
                
                return dependencies
        
        return AWSAnalyzer()
    
    def _get_gcp_analyzer(self):
        """Get GCP-specific dependency analyzer"""
        
        class GCPAnalyzer:
            def analyze_resource_dependencies(self, resource, all_resources, deep_analysis):
                return []
        
        return GCPAnalyzer()
    
    def _get_do_analyzer(self):
        """Get DigitalOcean-specific dependency analyzer"""
        
        class DOAnalyzer:
            def analyze_resource_dependencies(self, resource, all_resources, deep_analysis):
                return []
        
        return DOAnalyzer()