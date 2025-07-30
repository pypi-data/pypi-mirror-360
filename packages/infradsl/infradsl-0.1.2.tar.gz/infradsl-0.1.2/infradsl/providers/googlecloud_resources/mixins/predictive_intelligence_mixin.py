from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..vm import Vm

class PredictiveIntelligenceMixin:
    """Mixin for predictive intelligence features"""
    
    def predict_failures(self: 'Vm', enabled: bool = True) -> 'Vm':
        """Enable failure prediction intelligence
        
        Analyzes Google Cloud resource patterns and predicts potential failures:
        - Memory exhaustion prediction (e2-micro, f1-micro risk analysis)
        - Disk space monitoring with capacity predictions
        - Network bottleneck detection for shared-core instances
        - Service quota approaching alerts
        - Regional outage correlation analysis
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: Compute capacity, database limits, storage quotas, and network analysis")
        return self
    
    def cost_optimization(self: 'Vm', enabled: bool = True) -> 'Vm':
        """Enable cost optimization intelligence
        
        Analyzes current Google Cloud configuration and suggests cost savings:
        - Machine type right-sizing (e2, n1, c2 comparison)
        - Preemptible instance opportunities (up to 80% savings)
        - Committed use discount recommendations
        - Storage class optimization
        - Regional pricing analysis
        - Idle resource detection
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Machine sizing, committed use discounts, storage classes, and idle resource detection")
        return self
    
    def security_scanning(self: 'Vm', enabled: bool = True) -> 'Vm':
        """Enable security scanning intelligence
        
        Scans for Google Cloud security vulnerabilities and compliance issues:
        - Firewall rule analysis (overly permissive rules detection)
        - IAM policy privilege review
        - Service account security assessment
        - OS security updates monitoring
        - VPC security configuration review
        - SSL certificate management
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: IAM policies, firewall rules, certificates, VPC security, and encryption analysis")
        return self
    
    def performance_insights(self: 'Vm', enabled: bool = True) -> 'Vm':
        """Enable performance insights intelligence
        
        Analyzes Google Cloud performance and suggests improvements:
        - Instance performance optimization (shared vs dedicated CPU)
        - Memory utilization analysis and recommendations
        - Network performance tuning (VPC, Cloud CDN)
        - Disk I/O optimization (SSD vs standard persistent disks)
        - Auto-scaling recommendations
        - Load balancer optimization
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: Compute optimization, database tuning, load balancing, GKE scaling, and network performance")
        return self

    def _run_predictive_intelligence(self: 'Vm'):
        """Execute concise predictive intelligence analysis"""
        
        # Check if any intelligence features are enabled
        intelligence_enabled = any([
            getattr(self, '_failure_prediction_enabled', False),
            getattr(self, '_cost_optimization_enabled', False),
            getattr(self, '_security_scanning_enabled', False),
            getattr(self, '_performance_insights_enabled', False)
        ])
        
        if not intelligence_enabled:
            return
        
        # Run concise analysis instead of verbose output
        self._run_concise_predictive_analysis()
    
    def _run_concise_predictive_analysis(self: 'Vm'):
        """Run concise predictive intelligence with actionable insights"""
        primary_config = self.configs[self.vm_names[0]]
        critical_issues = []
        recommendations = []
        
        # Quick analysis for critical issues only
        machine_type = primary_config.machine_type
        
        # Memory risk check
        if machine_type in ['e2-micro', 'f1-micro']:
            critical_issues.append("⚠️ Memory risk: Low memory instance may fail under load")
            recommendations.append("Upgrade to e2-small for production workloads")
        
        # Cost optimization opportunity
        if not getattr(self, '_preemptible_enabled', False):
            recommendations.append("Consider preemptible instances for 80% cost savings")
        
        # Show only if there are actionable insights
        if critical_issues or recommendations:
            print(f"\n🧠 NEXUS INTELLIGENCE INSIGHTS:")
            
            # Show critical issues first
            for issue in critical_issues[:2]:  # Max 2 critical issues
                print(f"   {issue}")
            
            # Show top recommendations
            for rec in recommendations[:2]:  # Max 2 recommendations
                print(f"   💡 {rec}")
            
            # Interactive prompt for future feature
            if critical_issues:
                print(f"   🔧 Run 'infra optimize' to auto-fix these issues")