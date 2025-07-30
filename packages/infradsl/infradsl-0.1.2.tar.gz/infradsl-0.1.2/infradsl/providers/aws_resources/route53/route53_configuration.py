from typing import List, Dict, Any

class Route53ConfigurationMixin:
    """
    Mixin for Route53 chainable configuration methods.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize configuration-specific attributes
        if not hasattr(self, 'private_zone'):
            self.private_zone = False
        if not hasattr(self, 'health_checks'):
            self.health_checks = []
        if not hasattr(self, 'vpc_associations'):
            self.vpc_associations = []
        if not hasattr(self, 'comment_text'):
            self.comment_text = None

    def zone(self, domain_name: str):
        """Set the domain name for the hosted zone"""
        self.domain_name = domain_name
        return self

    def private(self):
        """Set the zone as private"""
        self.private_zone = True
        self.zone_type = 'private' # For compatibility with Route53Core
        return self

    def public(self):
        """Set the zone as public"""
        self.private_zone = False
        self.zone_type = 'public' # For compatibility with Route53Core
        return self

    def record(self, name: str, type_: str, value: str, ttl: int = 300):
        """Add a DNS record to the hosted zone"""
        self.records.append({'name': name, 'type': type_, 'value': value, 'ttl': ttl})
        return self

    def a_record(self, name: str, value: str, ttl: int = 300):
        """Add an A record"""
        return self.record(name, "A", value, ttl)

    def cname_record(self, name: str, value: str, ttl: int = 300):
        """Add a CNAME record"""
        return self.record(name, "CNAME", value, ttl)

    def mx_record(self, name: str, priority: int, value: str, ttl: int = 300):
        """Add an MX record"""
        # MX records have a specific format for value
        mx_value = f"{priority} {value}"
        return self.record(name, "MX", mx_value, ttl)

    def txt_record(self, name: str, value: str, ttl: int = 300):
        """Add a TXT record"""
        return self.record(name, "TXT", value, ttl)

    def aaaa_record(self, name: str, value: str, ttl: int = 300):
        """Add an AAAA record"""
        return self.record(name, "AAAA", value, ttl)

    def srv_record(self, name: str, priority: int, weight: int, port: int, target: str, ttl: int = 300):
        """Add an SRV record"""
        srv_value = f"{priority} {weight} {port} {target}"
        return self.record(name, "SRV", srv_value, ttl)

    def ns_record(self, name: str, value: str, ttl: int = 172800):
        """Add an NS record"""
        return self.record(name, "NS", value, ttl)

    def web(self, ip: str, ttl: int = 300):
        """Convenience method for a web A record"""
        return self.a_record("www", ip, ttl)

    def api(self, ip: str, ttl: int = 300):
        """Convenience method for an API A record"""
        return self.a_record("api", ip, ttl)

    def email_record(self, value: str, priority: int = 10, ttl: int = 300):
        """Convenience method for mail MX record"""
        return self.mx_record("@", priority, value, ttl)

    def subdomain(self, name: str, ip: str = None, cname: str = None, ttl: int = 300):
        """Convenience method for a subdomain A or CNAME record"""
        if ip:
            return self.a_record(name, ip, ttl)
        elif cname:
            return self.cname_record(name, cname, ttl)
        return self

    def health_check(self, name: str, endpoint: str, port: int, path: str, protocol: str = "HTTP", ttl: int = 60):
        """Add a health check configuration"""
        self.health_checks.append({'name': name, 'endpoint': endpoint, 'port': port, 'path': path, 'protocol': protocol, 'ttl': ttl})
        return self

    def cdn_setup(self, cdn_domain: str, ttl: int = 300):
        """Convenience method for CDN integration (CNAME for root and www)"""
        self.cname_record("@", cdn_domain, ttl)
        self.cname_record("www", cdn_domain, ttl)
        return self

    def load_balancer(self, name: str, lb_dns_name: str, ttl: int = 60):
        """Convenience method for Load Balancer integration (A record alias)"""
        # In a real scenario, this would create an ALIAS record. For now, a CNAME.
        return self.cname_record(name, lb_dns_name, ttl)
    
    def alias_record(self, name: str, target_dns_name: str, target_hosted_zone_id: str, evaluate_target_health: bool = False):
        """Add an ALIAS record (for CloudFront, ELB, S3, etc.)"""
        alias_target = {
            'HostedZoneId': target_hosted_zone_id,
            'DNSName': target_dns_name,
            'EvaluateTargetHealth': evaluate_target_health
        }
        self.records.append({
            'name': name,
            'type': 'A',
            'alias_target': alias_target,
            'is_alias': True
        })
        return self
    
    def cloudfront_alias(self, name: str, distribution_domain: str, evaluate_health: bool = False):
        """Create an ALIAS record for CloudFront distribution"""
        # CloudFront's hosted zone ID is always Z2FDTNDATAQYW2
        cloudfront_zone_id = 'Z2FDTNDATAQYW2'
        return self.alias_record(name, distribution_domain, cloudfront_zone_id, evaluate_health)
    
    def elb_alias(self, name: str, elb_dns_name: str, elb_zone_id: str, evaluate_health: bool = True):
        """Create an ALIAS record for Elastic Load Balancer"""
        return self.alias_record(name, elb_dns_name, elb_zone_id, evaluate_health)
    
    def s3_website_alias(self, name: str, bucket_website_endpoint: str, bucket_region: str = 'us-east-1'):
        """Create an ALIAS record for S3 static website"""
        # S3 website hosted zone IDs by region
        s3_zone_ids = {
            'us-east-1': 'Z3AQBSTGFYJSTF',
            'us-west-2': 'Z3BJ6K6RIION7M',
            'eu-west-1': 'Z1BKCTXD74EZPE',
            # Add more regions as needed
        }
        zone_id = s3_zone_ids.get(bucket_region, 'Z3AQBSTGFYJSTF')
        return self.alias_record(name, bucket_website_endpoint, zone_id, False)

    def wildcard(self, cname: str = None, ip: str = None, ttl: int = 300):
        """Add a wildcard record"""
        if cname:
            return self.cname_record("*", cname, ttl)
        elif ip:
            return self.a_record("*", ip, ttl)
        return self

    def email_verification(self, service: str):
        """Add records for email verification (e.g., SES, Mailgun)"""
        # This is a placeholder. Actual implementation would add specific TXT/CNAME records.
        print(f"Adding email verification records for {service}")
        return self

    def vpc(self, vpc_id: str, region: str):
        """Associate a VPC with a private hosted zone"""
        self.vpc_associations.append({'vpc_id': vpc_id, 'region': region})
        return self

    def comment(self, text: str):
        """Add a comment to the hosted zone"""
        self.comment_text = text
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the hosted zone"""
        self.tags[key] = value
        return self

    def tags(self, tags_dict: Dict[str, str]):
        """Add multiple tags to the hosted zone"""
        self.tags.update(tags_dict)
        return self
    
    def cloudfront_routing(self, *args, **kwargs):
        """Nexus Engine: Intelligent CloudFront routing setup
        
        Usage:
        # Auto-mapping from distributions
        .cloudfront_routing(cdn, prod_cdn)
        
        # Explicit mapping with custom domains
        .cloudfront_routing(
            ec="d2jttkc09t51g9.cloudfront.net",
            eg="d2jttkc09t51g9.cloudfront.net", 
            prod="dpyrx6csm3g36.cloudfront.net"
        )
        
        # Mixed approach
        .cloudfront_routing(cdn, prod="dpyrx6csm3g36.cloudfront.net")
        """
        # Handle explicit subdomain -> CloudFront domain mapping
        for subdomain, cloudfront_domain in kwargs.items():
            self.cname_record(subdomain, cloudfront_domain, 300)
        
        # Handle distribution objects (auto-mapping)
        for distribution in args:
            if hasattr(distribution, 'custom_domains'):
                for domain in distribution.custom_domains:
                    subdomain = domain.split('.')[0]  # Extract subdomain part
                    dist_domain = distribution.get("distribution_domain", f"{subdomain}.cloudfront.net")
                    self.cname_record(subdomain, dist_domain, 300)
        
        return self
    
    def load_balancer_records(self, name: str, ips: List[str]):
        """Nexus Engine: Load balancer A record setup"""
        for ip in ips:
            self.a_record(name, ip, 300)
        return self
    
    def apex_alias(self, cloudfront_domain: str):
        """Nexus Engine: Root domain ALIAS to CloudFront"""
        return self.cloudfront_alias("@", cloudfront_domain) 