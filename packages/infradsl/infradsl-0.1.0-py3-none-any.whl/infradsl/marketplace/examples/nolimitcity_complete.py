"""
NolimitCity Complete Infrastructure Templates

This example shows how a gaming company can create templates for their
entire technology stack, from game servers to payment processing,
all inheriting company policies automatically.
"""

from infradsl.providers import AWS, GoogleCloud, DigitalOcean, Cloudflare
from infradsl.marketplace.company_templates import NolimitCityBase


# =============================================================================
# COMPUTE RESOURCES
# =============================================================================

class GameServer(NolimitCityBase, GoogleCloud.VM):
    """High-performance game server optimized for real-time gaming"""
    
    def __init__(self, name):
        super().__init__(name)
        # Gaming-optimized configuration
        self.machine_type("c2-standard-16")  # High CPU for game logic
        self.disk_type("ssd")
        self.disk_size(100)
        self.network_tier("premium")        # Low latency networking
        
        # Gaming-specific policies
        self._apply_gaming_policies()
    
    def _apply_gaming_policies(self):
        """Gaming-specific configurations"""
        self.real_time_monitoring(enabled=True)
        self.latency_threshold("50ms")
        self.auto_scaling(
            min_instances=2,
            max_instances=50,
            scale_metric="cpu_and_network"
        )


class PaymentProcessor(NolimitCityBase, AWS.Lambda):
    """PCI-compliant payment processing with enhanced security"""
    
    def __init__(self, name):
        super().__init__(name)
        # Security-first configuration
        self.runtime("python3.11")
        self.memory(1024)
        self.timeout(30)
        
        # PCI compliance policies
        self._apply_pci_compliance()
    
    def _apply_pci_compliance(self):
        """PCI DSS compliance requirements"""
        self.encryption("AES-256")
        self.vpc_isolation(True)
        self.audit_logging(True)
        self.security_scanning("continuous")
        self.compliance_frameworks(["PCI-DSS", "SOC2"])


class APIGateway(NolimitCityBase, AWS.APIGateway):
    """Company API gateway with rate limiting and authentication"""
    
    def __init__(self, name):
        super().__init__(name)
        # API-specific configuration
        self.throttling(
            rate_limit="10000/minute",
            burst_limit="5000"
        )
        self.cors_enabled(True)
        self.api_key_required(True)


# =============================================================================
# DATABASE RESOURCES  
# =============================================================================

class PlayerDatabase(NolimitCityBase, GoogleCloud.CloudSQL):
    """GDPR-compliant player data storage"""
    
    def __init__(self, name):
        super().__init__(name)
        # Player data requirements
        self.engine("postgresql-14")
        self.instance_type("db-standard-4")
        self.storage_size(500)
        self.high_availability(True)
        
        # GDPR-specific policies
        self._apply_gdpr_policies()
    
    def _apply_gdpr_policies(self):
        """GDPR compliance for player data"""
        self.encryption_at_rest(True)
        self.encryption_in_transit(True)
        self.backup_retention("5y")  # GDPR requirement
        self.point_in_time_recovery(True)
        self.data_anonymization(enabled=True)
        self.right_to_be_forgotten(enabled=True)


class GameAnalytics(NolimitCityBase, GoogleCloud.BigQuery):
    """Real-time game analytics and reporting"""
    
    def __init__(self, name):
        super().__init__(name)
        # Analytics configuration
        self.dataset_location("EU")  # GDPR compliance
        self.partition_strategy("daily")
        self.clustering_fields(["game_id", "player_id", "timestamp"])


class SessionCache(NolimitCityBase, AWS.ElastiCache):
    """High-performance session and game state caching"""
    
    def __init__(self, name):
        super().__init__(name)
        # Cache configuration
        self.engine("redis")
        self.node_type("cache.r6g.large")
        self.cluster_mode(True)
        self.replication_groups(3)


# =============================================================================
# STORAGE RESOURCES
# =============================================================================

class GameAssets(NolimitCityBase, Cloudflare.R2):
    """CDN-optimized game asset storage"""
    
    def __init__(self, name):
        super().__init__(name)
        # Asset-specific configuration
        self.public_access(True)
        self.versioning(True)
        self.cdn_integration(True)
        
        # Gaming asset policies
        self._apply_asset_policies()
    
    def _apply_asset_policies(self):
        """Optimize for game asset delivery"""
        self.cache_control({
            "images": "max-age=31536000",     # 1 year
            "audio": "max-age=31536000",      # 1 year  
            "config": "max-age=300",          # 5 minutes
            "html": "max-age=3600"            # 1 hour
        })


class PlayerBackups(NolimitCityBase, AWS.S3):
    """Encrypted backups with GDPR compliance"""
    
    def __init__(self, name):
        super().__init__(name)
        # Backup configuration
        self.encryption("SSE-KMS")
        self.versioning(True)
        self.lifecycle_policy({
            "archive_after": "90d",
            "delete_after": "7y"  # Legal requirement
        })


# =============================================================================
# NETWORKING RESOURCES
# =============================================================================

class GamingVPC(NolimitCityBase, GoogleCloud.VPC):
    """Gaming-optimized network with DDoS protection"""
    
    def __init__(self, name):
        super().__init__(name)
        # Network configuration
        self.cidr_block("10.0.0.0/16")
        self.ddos_protection(True)
        self.flow_logs(True)
        
        # Gaming network policies
        self._apply_gaming_network()
    
    def _apply_gaming_network(self):
        """Gaming-specific network optimizations"""
        self.low_latency_routing(True)
        self.qos_enabled(True)
        self.game_traffic_priority("high")


class GameLoadBalancer(NolimitCityBase, AWS.ApplicationLoadBalancer):
    """High-availability load balancer for game traffic"""
    
    def __init__(self, name):
        super().__init__(name)
        # Load balancer configuration
        self.scheme("internet-facing")
        self.ip_address_type("ipv4")
        self.deletion_protection(True)
        
        # Gaming-specific LB policies
        self._apply_gaming_lb_policies()
    
    def _apply_gaming_lb_policies(self):
        """Gaming load balancer optimizations"""
        self.sticky_sessions(True)
        self.health_check({
            "path": "/health",
            "interval": "10s",
            "timeout": "5s",
            "healthy_threshold": 2,
            "unhealthy_threshold": 3
        })
        self.target_group_stickiness("lb_cookie")


# =============================================================================
# MONITORING & SECURITY
# =============================================================================

class GamingMonitoring(NolimitCityBase, GoogleCloud.Monitoring):
    """Comprehensive gaming platform monitoring"""
    
    def __init__(self, name):
        super().__init__(name)
        # Gaming-specific metrics
        self.custom_metrics([
            "player_count",
            "game_latency", 
            "transaction_volume",
            "error_rate",
            "concurrent_games"
        ])
        
        # Alert configuration
        self._setup_gaming_alerts()
    
    def _setup_gaming_alerts(self):
        """Gaming-specific alerting"""
        self.alerts({
            "high_latency": {
                "threshold": "100ms",
                "duration": "5m",
                "severity": "critical"
            },
            "player_drop": {
                "threshold": "20%",
                "duration": "2m", 
                "severity": "warning"
            },
            "payment_failure": {
                "threshold": "5%",
                "duration": "1m",
                "severity": "critical"
            }
        })


class SecurityScanner(NolimitCityBase, AWS.SecurityHub):
    """Automated security scanning and compliance"""
    
    def __init__(self, name):
        super().__init__(name)
        # Security configuration
        self.compliance_standards([
            "AWS-Foundational-Security",
            "PCI-DSS",
            "SOC2-Type2"
        ])
        self.continuous_scanning(True)


# =============================================================================
# COMPLETE APPLICATION STACKS
# =============================================================================

class SlotGameStack(NolimitCityBase):
    """Complete slot game infrastructure stack"""
    
    def __init__(self, game_name):
        super().__init__(game_name)
        self.game_name = game_name
        
        # Infrastructure components
        self.vpc = GamingVPC(f"{game_name}-vpc")
        
        # Game servers
        self.game_servers = [
            GameServer(f"{game_name}-game-{i}")
            for i in range(5)  # Start with 5 servers
        ]
        
        # Database tier
        self.player_db = PlayerDatabase(f"{game_name}-players")
        self.analytics_db = GameAnalytics(f"{game_name}-analytics")
        self.cache = SessionCache(f"{game_name}-cache")
        
        # Payment processing
        self.payment_processor = PaymentProcessor(f"{game_name}-payments")
        self.api_gateway = APIGateway(f"{game_name}-api")
        
        # Storage
        self.game_assets = GameAssets(f"{game_name}-assets")
        self.backups = PlayerBackups(f"{game_name}-backups")
        
        # Networking
        self.load_balancer = GameLoadBalancer(f"{game_name}-lb")
        
        # Monitoring & Security
        self.monitoring = GamingMonitoring(f"{game_name}-monitoring")
        self.security = SecurityScanner(f"{game_name}-security")
    
    def create(self):
        """Deploy complete slot game infrastructure"""
        print(f"🎰 Deploying {self.game_name} slot game infrastructure")
        
        # Create in dependency order
        self.vpc.create()
        
        # Database tier
        self.player_db.create()
        self.analytics_db.create()
        self.cache.create()
        
        # Game servers
        for server in self.game_servers:
            server.environment({
                "PLAYER_DB_URL": self.player_db.connection_string,
                "CACHE_URL": self.cache.connection_string,
                "GAME_NAME": self.game_name
            })
            server.create()
        
        # Payment processing
        self.payment_processor.environment({
            "PLAYER_DB_URL": self.player_db.connection_string,
            "COMPLIANCE_MODE": "PCI_DSS"
        })
        self.payment_processor.create()
        
        # API Gateway
        self.api_gateway.add_targets([
            *self.game_servers,
            self.payment_processor
        ])
        self.api_gateway.create()
        
        # Load balancer
        self.load_balancer.add_targets(self.game_servers)
        self.load_balancer.create()
        
        # Storage
        self.game_assets.create()
        self.backups.create()
        
        # Monitoring & Security
        self.monitoring.add_targets([
            *self.game_servers,
            self.player_db,
            self.cache,
            self.payment_processor
        ])
        self.monitoring.create()
        self.security.create()
        
        print(f"✅ {self.game_name} infrastructure deployed successfully")
        print(f"🌍 Game URL: {self.load_balancer.dns_name}")
        print(f"📊 Monitoring: {self.monitoring.dashboard_url}")
        print(f"🔒 Security Dashboard: {self.security.dashboard_url}")
        
        return {
            "game_url": self.load_balancer.dns_name,
            "api_url": self.api_gateway.url,
            "monitoring_dashboard": self.monitoring.dashboard_url,
            "security_dashboard": self.security.dashboard_url
        }


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Deploy a new slot game with complete infrastructure
    slot_game = SlotGameStack("golden-pharaoh")
    deployment_info = slot_game.create()
    
    # All resources automatically include:
    # ✅ GDPR compliance (EU regions, data protection)
    # ✅ PCI-DSS compliance (for payments)
    # ✅ Company monitoring (Discord webhooks)
    # ✅ Security scanning and compliance
    # ✅ Backup and disaster recovery
    # ✅ Auto-scaling and load balancing
    # ✅ Cost tracking and optimization
    # ✅ Network security and DDoS protection
    
    print("\n🎰 Golden Pharaoh Slot Game Infrastructure:")
    print(f"   🌍 Game URL: {deployment_info['game_url']}")
    print(f"   🔗 API: {deployment_info['api_url']}")
    print(f"   📊 Monitoring: {deployment_info['monitoring_dashboard']}")
    print(f"   🔒 Security: {deployment_info['security_dashboard']}")
    print(f"\n✨ 60+ resources created with 5 lines of code!")
    print(f"🏆 All company policies automatically applied!")