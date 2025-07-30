"""
AWS Provider for InfraDSL

Rails-like infrastructure management for Amazon Web Services.
Makes AWS as simple as writing business logic.

Philosophy:
- Convention over configuration
- Rails-like chainable methods
- Zero-config authentication
- Intelligent defaults
- Developer happiness first

Example:
    # Simple EC2 instance
    server = AWS.EC2("web-server").t3_micro().create()

    # Containerized app on ECS Fargate
    app = AWS.ECS("my-app").fargate().container("nginx").create()

    # S3 bucket with website hosting
    site = AWS.S3("my-site").website().public_read().create()
"""

from typing import Dict, Any, Optional
from .aws_resources.ec2 import EC2
from .aws_resources.s3 import S3
from .aws_resources.rds import RDS
from .aws_resources.ecs import ECS
from .aws_resources.route53 import Route53
from .aws_resources.cloudfront import CloudFront
from .aws_resources.load_balancer import LoadBalancer
from .aws_resources.lambda_function import Lambda
from .aws_resources.cloudfront_function import CloudFrontFunction
from .aws_resources.sqs import SQS
from .aws_resources.sns import SNS
from .aws_resources.elasticache import ElastiCache
from .aws_resources.domain_registration import DomainRegistration
from .aws_resources.auth_service import AwsAuthenticationService
from .aws_resources.security_group import SecurityGroup


class AWS:
    """
    AWS provider with Rails-like simplicity.

    Makes Amazon Web Services as easy to use as Rails for web apps.
    """

    @staticmethod
    def EC2(name: str) -> EC2:
        """
        Create an EC2 instance with Rails-like simplicity.

        Args:
            name: Name of the EC2 instance

        Returns:
            EC2: A configured EC2 instance ready for chaining

        Examples:
            # Simple web server
            server = AWS.EC2("web-server").t3_micro().ubuntu().create()

            # High-performance database server
            db = (AWS.EC2("db-server")
                 .c5_xlarge()
                 .disk_size(100)
                 .security_group("db-sg")
                 .create())

            # Auto-scaling web tier
            web_tier = (AWS.EC2("web-tier")
                       .t3_medium()
                       .auto_scale(min_size=2, max_size=10)
                       .load_balancer()
                       .create())
        """
        return EC2(name)

    @staticmethod
    def S3(name: str) -> S3:
        """
        Create an S3 bucket with Rails-like conventions.

        Args:
            name: Resource name (bucket name will be auto-generated)

        Returns:
            S3: A configured S3 bucket ready for chaining

        Examples:
            # Simple storage bucket
            storage = AWS.S3("my-data").private().create()

            # Static website hosting
            website = (AWS.S3("my-website")
                      .website()
                      .public()
                      .upload_directory("./site")
                      .create())

            # Backup storage with lifecycle
            backups = (AWS.S3("app-backups")
                      .backup_bucket()
                      .upload("./backups", "daily/")
                      .create())
        """
        return S3(name)

    @staticmethod
    def RDS(database_name: str) -> RDS:
        """
        Create an RDS database with Rails conventions.

        Args:
            database_name: Name of the database instance

        Returns:
            RDS: A configured RDS instance ready for chaining

        Examples:
            # Development MySQL database
            dev_db = (AWS.RDS("dev-database")
                     .mysql()
                     .db_t3_micro()
                     .development()
                     .create())

            # Production PostgreSQL with high availability
            prod_db = (AWS.RDS("prod-database")
                      .postgresql()
                      .db_r5_large()
                      .multi_az()
                      .encrypted()
                      .backup_retention(30)
                      .create())
        """
        return RDS(database_name)

    @staticmethod
    def Route53(dns_name: str) -> Route53:
        """
        Create a Route53 DNS configuration with Rails-like management.

        Args:
            dns_name: Name for the DNS configuration

        Returns:
            Route53: A configured Route53 instance ready for chaining

        Examples:
            # Simple domain with web records
            dns = (AWS.Route53("my-domain")
                  .zone("example.com")
                  .web("192.0.2.1")
                  .api("api.example.com")
                  .mail("mail.example.com")
                  .create())

            # Complex DNS setup
            dns = (AWS.Route53("complex-dns")
                  .zone("myapp.com")
                  .record("api", "A", "192.0.2.1")
                  .record("www", "CNAME", "myapp.com")
                  .subdomain("blog", cname="ghost.myapp.com")
                  .health_check("api", "192.0.2.1", 8080, "/health")
                  .create())
        """
        return Route53(dns_name)

    @staticmethod
    def CloudFront(cdn_name: str) -> CloudFront:
        """
        Create a CloudFront CDN distribution with Rails-like management.

        Args:
            cdn_name: Name for the CDN distribution

        Returns:
            CloudFront: A configured CloudFront instance ready for chaining

        Examples:
            # Static website CDN
            cdn = (AWS.CloudFront("website-cdn")
                  .static_site("my-bucket", "www.example.com")
                  .ssl_certificate("arn:aws:acm:...")
                  .create())

            # API acceleration
            api_cdn = (AWS.CloudFront("api-cdn")
                      .api_acceleration("api.example.com")
                      .custom_domain("fast-api.example.com")
                      .waf("web-acl-id")
                      .create())

            # Assets delivery
            assets = (AWS.CloudFront("assets-cdn")
                     .assets_delivery("assets-bucket")
                     .domains(["cdn.example.com", "static.example.com"])
                     .price_class_200()
                     .create())
        """
        return CloudFront(cdn_name)

    @staticmethod
    def CloudFrontFunction(name: str) -> CloudFrontFunction:
        """
        Create a CloudFront Function for edge computing with Rails-like simplicity.

        Args:
            name: Function name

        Returns:
            CloudFrontFunction: A configured CloudFront Function ready for chaining

        Examples:
            # Simple security headers function
            security = (AWS.CloudFrontFunction("security-headers")
                       .viewer_response()
                       .add_security_headers()
                       .create())

            # Authentication check function
            auth = (AWS.CloudFrontFunction("auth-check")
                   .viewer_request()
                   .auth_check("Authorization")
                   .attach_to_distribution("E123456789")
                   .create())

            # Custom JavaScript function
            custom = (AWS.CloudFrontFunction("url-rewrite")
                     .viewer_request()
                     .javascript_code("function handler(event) { return event.request; }")
                     .create())

            # Function from file
            advanced = (AWS.CloudFrontFunction("advanced-logic")
                       .viewer_request()
                       .code_from_file("./functions/advanced.js")
                       .attach_to_distribution("E123456789", "/api/*")
                       .create())
        """
        return CloudFrontFunction(name)

    @staticmethod
    def ECS(service_name: str) -> ECS:
        """
        Create an ECS service with Rails-like container orchestration.

        Args:
            service_name: Name of the ECS service

        Returns:
            ECS: A configured ECS service ready for chaining

        Examples:
            # Simple containerized web app
            webapp = (AWS.ECS("my-webapp")
                     .fargate()
                     .container("nginx")
                     .port(80)
                     .create())

            # Microservice with load balancer
            api = (AWS.ECS("user-api")
                  .fargate()
                  .container("my-api", "templates/api/")
                  .port(8080)
                  .load_balancer()
                  .auto_scale(min=2, max=10)
                  .create())
        """
        return ECS(service_name)

    @staticmethod
    def Lambda(name: str) -> 'Lambda':
        """
        Create a Lambda function with Rails-like simplicity.

        Args:
            name: Function name

        Returns:
            Lambda: A configured Lambda function ready for chaining

        Examples:
            # Simple API function
            api = (AWS.Lambda("my-api")
                  .trigger("api-gateway")
                  .memory("512MB")
                  .create())

            # Container-based function
            service = (AWS.Lambda("my-service")
                      .container("api", "templates/fastapi-lambda", 8080)
                      .trigger("api-gateway")
                      .create())

            # Serverless web app
            webapp = (AWS.Lambda("my-webapp")
                     .nodejs18()
                     .memory("1024MB")
                     .timeout(30)
                     .trigger("api-gateway")
                     .create())
        """
        return Lambda(name)

    @staticmethod
    def SQS(name: str) -> SQS:
        """
        Create an SQS queue with Rails-like simplicity.

        Args:
            name: Queue name

        Returns:
            SQS: A configured SQS queue ready for chaining

        Examples:
            # Simple message queue
            queue = AWS.SQS("work-queue").standard().create()

            # FIFO queue with dead letter queue
            orders = (AWS.SQS("order-processing")
                     .fifo()
                     .dead_letter_queue()
                     .retention(14)  # 14 days
                     .create())

            # High-performance queue with long polling
            events = (AWS.SQS("event-stream")
                     .standard()
                     .long_polling(20)
                     .visibility_timeout(60)
                     .create())
        """
        return SQS(name)

    @staticmethod
    def SNS(name: str) -> SNS:
        """
        Create an SNS topic with Rails-like simplicity.

        Args:
            name: Topic name

        Returns:
            SNS: A configured SNS topic ready for chaining

        Examples:
            # Simple notification topic
            notifications = AWS.SNS("app-notifications").notification_topic(["admin@example.com"]).create()

            # Alert topic with email and SMS
            alerts = (AWS.SNS("critical-alerts")
                     .alert_topic(emails=["ops@example.com"], sms=["+1234567890"])
                     .production()
                     .create())

            # Microservice event bus
            events = (AWS.SNS("service-events")
                     .microservice_topic(queue_arns=["arn:aws:sqs:..."])
                     .fifo()
                     .create())

            # Webhook notifications
            webhooks = (AWS.SNS("webhook-events")
                       .webhook_topic(["https://api.example.com/webhook"])
                       .create())
        """
        return SNS(name)

    @staticmethod
    def ElastiCache(name: str) -> ElastiCache:
        """
        Create an ElastiCache cluster with Rails-like simplicity.

        Args:
            name: Cache cluster name

        Returns:
            ElastiCache: A configured ElastiCache cluster ready for chaining

        Examples:
            # Simple Redis cache
            cache = AWS.ElastiCache("app-cache").redis().simple_cache().create()

            # Session store with replication
            sessions = (AWS.ElastiCache("user-sessions")
                       .session_store()
                       .replication(2)
                       .multi_az()
                       .create())

            # High-performance Redis cluster
            cluster = (AWS.ElastiCache("api-cache")
                      .high_performance_cache()
                      .cluster_mode(3, 2)  # 3 shards, 2 replicas each
                      .encryption()
                      .create())

            # Memcached for distributed caching
            memcache = (AWS.ElastiCache("distributed-cache")
                       .memcached_cluster(5)
                       .node_type("cache.r6g.large")
                       .create())
        """
        return ElastiCache(name)

    @staticmethod
    def CertificateManager(name: str):
        """Create AWS Certificate Manager resource"""
        from .aws_resources.certificate_manager import CertificateManager
        return CertificateManager(name)

    @staticmethod
    def DomainRegistration(name: str) -> DomainRegistration:
        """
        Register domains automatically through Route53 Domains API.

        Args:
            name: Name for the domain registration configuration

        Returns:
            DomainRegistration: A configured domain registration ready for chaining

        Examples:
            # Simple domain registration
            domain = (AWS.DomainRegistration("my-domain")
                     .domain("example.com")
                     .contact("admin@example.com")
                     .duration(2)
                     .create())

            # Complete domain setup with SSL
            secure_domain = (AWS.DomainRegistration("secure-site")
                           .domain("securesite.com")
                           .contact("admin@company.com", "John", "Doe", "Company Inc")
                           .privacy(True)
                           .auto_renewal(True)
                           .with_hosted_zone()
                           .create())
        """
        return DomainRegistration(name)

    @staticmethod
    def SecretsManager(name: str):
        """Create AWS Secrets Manager resource"""
        from .aws_resources.secrets_manager import SecretsManager
        return SecretsManager(name)

    @staticmethod
    def SecurityGroup(name: str) -> SecurityGroup:
        """
        Create an EC2 Security Group with Rails-like simplicity.

        Args:
            name: Name of the Security Group

        Returns:
            SecurityGroup: A configured Security Group ready for chaining

        Examples:
            # Simple web security group
            web_sg = (AWS.SecurityGroup("web-sg")
                     .ingress("80", "0.0.0.0/0")
                     .ingress("443", "0.0.0.0/0")
                     .egress("all", "0.0.0.0/0")
                     .create())
        """
        return SecurityGroup(name)

    @staticmethod
    def APIGateway(name: str):
        """
        Create an API Gateway with Rails-like simplicity.

        Args:
            name: API Gateway name

        Returns:
            APIGateway: A configured API Gateway ready for chaining

        Examples:
            # Simple Lambda-backed API
            api = (AWS.APIGateway("my-api")
                  .lambda_api(lambda_arn)
                  .create())

            # Microservice API with auth
            service = (AWS.APIGateway("user-service")
                      .microservice_api()
                      .lambda_proxy(user_lambda_arn)
                      .cors()
                      .throttling(5000, 10000)
                      .create())

            # REST API with multiple routes
            rest_api = (AWS.APIGateway("orders-api")
                       .rest_api()
                       .get("/orders", lambda_function_arn=list_orders_arn)
                       .post("/orders", lambda_function_arn=create_order_arn)
                       .cors()
                       .create())
        """
        from .aws_resources.api_gateway import APIGateway
        return APIGateway(name)

    @staticmethod
    def LoadBalancer(name: str) -> LoadBalancer:
        """
        Create an Application Load Balancer with Rails-like management.

        Args:
            name: Name of the load balancer

        Returns:
            LoadBalancer: A configured ALB ready for chaining

        Examples:
            # Simple web load balancer
            web_lb = (AWS.LoadBalancer("web-lb")
                     .web()
                     .https()
                     .ssl_certificate("arn:aws:acm:...")
                     .health_check("/health")
                     .create())

            # API load balancer with WAF
            api_lb = (AWS.LoadBalancer("api-lb")
                     .api()
                     .https(443)
                     .waf("arn:aws:wafv2:...")
                     .integration("ecs", "api-service")
                     .access_logs("api-logs-bucket")
                     .create())

            # Internal microservice load balancer
            micro_lb = (AWS.LoadBalancer("micro-lb")
                       .microservice()
                       .internal()
                       .target_group("services", "HTTP", 3000)
                       .health_check("/metrics", 15)
                       .create())
        """
        return LoadBalancer(name)

    @staticmethod
    def ALB(name: str) -> LoadBalancer:
        """
        Create an Application Load Balancer (alias for LoadBalancer).

        Args:
            name: Name of the load balancer

        Returns:
            LoadBalancer: A configured ALB ready for chaining

        Examples:
            # Same as AWS.LoadBalancer() but shorter
            web_alb = (AWS.ALB("web-alb")
                      .web()
                      .https()
                      .create())
        """
        return LoadBalancer(name)

    @staticmethod
    def authenticate(
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None
    ) -> bool:
        """
        Manually authenticate with AWS.

        Note: Authentication is handled automatically by default.
        This method is provided for cases where manual authentication is needed.

        Args:
            access_key_id: AWS Access Key ID (optional)
            secret_access_key: AWS Secret Access Key (optional)
            region: AWS region (optional, defaults to us-east-1)
            profile: AWS profile name (optional)

        Returns:
            bool: True if authentication was successful

        Examples:
            # Use default credentials (recommended)
            AWS.authenticate()

            # Use specific profile
            AWS.authenticate(profile="production")

            # Use explicit credentials
            AWS.authenticate(
                access_key_id="AKIA...",
                secret_access_key="...",
                region="us-west-2"
            )
        """
        try:
            return AwsAuthenticationService.authenticate(
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
                region=region,
                profile=profile
            )
        except Exception as e:
            print(f"❌ AWS authentication failed: {str(e)}")
            return False

    @staticmethod
    def version() -> str:
        """Get the version of the AWS provider."""
        return "1.0.0"

    @staticmethod
    def regions() -> Dict[str, str]:
        """
        Get available AWS regions with friendly names.

        Returns:
            Dict mapping region codes to friendly names
        """
        return {
            # US Regions
            "us-east-1": "US East (N. Virginia)",
            "us-east-2": "US East (Ohio)",
            "us-west-1": "US West (N. California)",
            "us-west-2": "US West (Oregon)",

            # Europe Regions
            "eu-west-1": "Europe (Ireland)",
            "eu-west-2": "Europe (London)",
            "eu-west-3": "Europe (Paris)",
            "eu-central-1": "Europe (Frankfurt)",
            "eu-north-1": "Europe (Stockholm)",

            # Asia Pacific Regions
            "ap-northeast-1": "Asia Pacific (Tokyo)",
            "ap-northeast-2": "Asia Pacific (Seoul)",
            "ap-southeast-1": "Asia Pacific (Singapore)",
            "ap-southeast-2": "Asia Pacific (Sydney)",
            "ap-south-1": "Asia Pacific (Mumbai)",

            # Other Regions
            "ca-central-1": "Canada (Central)",
            "sa-east-1": "South America (São Paulo)",
        }

    @staticmethod
    def help() -> None:
        """Display helpful information about using the AWS provider."""
        print("🏗️  AWS Provider for InfraDSL")
        print("=" * 40)
        print("Rails-like infrastructure management for Amazon Web Services")
        print()
        print("💡 Quick Start:")
        print("   server = AWS.EC2('web-server').t3_micro().create()")
        print("   bucket = AWS.S3('my-data').private().create()")
        print("   app = AWS.ECS('my-app').fargate().container('nginx').create()")
        print()
        print("🔧 Available Services:")
        print("   • EC2      - Virtual machines and compute")
        print("   • S3       - Object storage and static websites")
        print("   • RDS      - Managed relational databases")
        print("   • ECS      - Container orchestration (Fargate)")
        print("   • Route53  - DNS management and domain registration")
        print("   • CloudFront - CDN and edge delivery")
        print("   • CloudFrontFunction - Edge computing and request/response manipulation")
        print("   • ALB/ELB  - Load balancers and traffic distribution")
        print()
        print("🌍 Popular Regions:")
        regions = AWS.regions()
        for code, name in list(regions.items())[:5]:
            print(f"   • {code:<12} - {name}")
        print()
        print("📚 Documentation: https://github.com/your-org/oopscli")


# Convenience imports for direct usage
__all__ = [
    'AWS',
    'EC2',
    'S3',
    'RDS',
    'ECS',
    'Route53',
    'CloudFront',
    'CloudFrontFunction',
    'LoadBalancer',
    'ALB',
    'SecurityGroup'
]
