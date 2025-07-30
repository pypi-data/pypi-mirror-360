"""
AWS CloudFront Origins

Handles CloudFront origin configurations including S3 origins, custom origins,
and Origin Access Control (OAC) settings.
"""

from typing import Dict, Any, List


class CloudFrontOrigins:
    """Manages CloudFront origin configurations"""

    def __init__(self, aws_client):
        self.aws_client = aws_client

    def build_origins_config(self, origins_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build origins configuration from list of origin definitions"""
        origins = []
        
        for origin in origins_config:
            origins.append(self.build_single_origin_config(origin))
            
        return origins

    def build_single_origin_config(self, origin: Dict[str, Any]) -> Dict[str, Any]:
        """Build individual origin configuration"""
        origin_config = {
            'Id': origin['id'],
            'DomainName': origin['domain_name'],
            'OriginPath': origin.get('origin_path', ''),
            'ConnectionAttempts': origin.get('connection_attempts', 3),
            'ConnectionTimeout': origin.get('connection_timeout', 10)
        }
        
        # Configure origin based on type
        if origin.get('origin_type') == 'S3':
            origin_config.update(self._build_s3_origin_config(origin))
        else:
            origin_config.update(self._build_custom_origin_config(origin))
            
        # Add custom headers if specified
        custom_headers = origin.get('custom_headers', {})
        if custom_headers:
            origin_config['CustomHeaders'] = {
                'Quantity': len(custom_headers),
                'Items': [
                    {
                        'HeaderName': key,
                        'HeaderValue': value
                    }
                    for key, value in custom_headers.items()
                ]
            }
        else:
            origin_config['CustomHeaders'] = {'Quantity': 0}
            
        return origin_config

    def _build_s3_origin_config(self, origin: Dict[str, Any]) -> Dict[str, Any]:
        """Build S3 origin specific configuration"""
        s3_config = {
            'S3OriginConfig': {
                'OriginAccessIdentity': ''  # Empty for OAC (Origin Access Control)
            }
        }
        
        # Add OAC configuration if specified
        if origin.get('origin_access_control'):
            # In a real implementation, this would handle OAC creation/reference
            pass
            
        return s3_config

    def _build_custom_origin_config(self, origin: Dict[str, Any]) -> Dict[str, Any]:
        """Build custom origin (HTTP/HTTPS) configuration"""
        custom_config = {
            'CustomOriginConfig': {
                'HTTPPort': origin.get('http_port', 80),
                'HTTPSPort': origin.get('https_port', 443),
                'OriginProtocolPolicy': origin.get('protocol_policy', 'https-only'),
                'OriginSslProtocols': {
                    'Quantity': len(origin.get('ssl_protocols', ['TLSv1.2'])),
                    'Items': origin.get('ssl_protocols', ['TLSv1.2'])
                },
                'OriginReadTimeout': origin.get('origin_read_timeout', 30),
                'OriginKeepaliveTimeout': origin.get('origin_keepalive_timeout', 5)
            }
        }
        
        return custom_config

    def create_s3_origin(self, origin_id: str, bucket_domain: str, path: str = '') -> Dict[str, Any]:
        """Create S3 origin configuration"""
        return {
            'id': origin_id,
            'domain_name': bucket_domain,
            'origin_type': 'S3',
            'origin_path': f"/{path.strip('/')}" if path else '',
            'origin_access_control': True,
            'connection_attempts': 3,
            'connection_timeout': 10
        }

    def create_custom_origin(
        self, 
        origin_id: str, 
        domain: str, 
        protocol: str = 'https',
        path: str = '',
        custom_headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create custom origin configuration"""
        return {
            'id': origin_id,
            'domain_name': domain,
            'origin_type': 'Custom',
            'origin_path': f"/{path.strip('/')}" if path else '',
            'protocol_policy': f"{protocol}-only",
            'http_port': 80,
            'https_port': 443,
            'connection_attempts': 3,
            'connection_timeout': 10,
            'origin_read_timeout': 30,
            'origin_keepalive_timeout': 5,
            'ssl_protocols': ['TLSv1.2'],
            'custom_headers': custom_headers or {}
        }

    def create_load_balancer_origin(self, origin_id: str, lb_domain: str, path: str = '') -> Dict[str, Any]:
        """Create load balancer origin configuration"""
        return self.create_custom_origin(
            origin_id=origin_id,
            domain=lb_domain,
            protocol='https',
            path=path,
            custom_headers={
                'X-Forwarded-Proto': 'https',
                'X-Real-IP': '$remote_addr'
            }
        )

    def create_api_gateway_origin(self, origin_id: str, api_domain: str, stage: str = 'prod') -> Dict[str, Any]:
        """Create API Gateway origin configuration"""
        path = f"/{stage}" if stage and stage != 'prod' else ''
        
        return self.create_custom_origin(
            origin_id=origin_id,
            domain=api_domain,
            protocol='https',
            path=path,
            custom_headers={
                'X-Forwarded-Proto': 'https',
                'X-API-Gateway': 'CloudFront'
            }
        )

    def validate_origin_domain(self, domain: str, origin_type: str = 'Custom') -> bool:
        """Validate origin domain format"""
        if not domain:
            return False
            
        # Basic domain validation
        if origin_type == 'S3':
            # S3 bucket domain validation
            return domain.endswith('.s3.amazonaws.com') or domain.endswith('.s3-website')
        else:
            # Custom domain validation
            return '.' in domain and not domain.startswith('http')

    def get_origin_health_check_url(self, origin: Dict[str, Any]) -> str:
        """Generate health check URL for origin"""
        domain = origin['domain_name']
        path = origin.get('origin_path', '')
        
        if origin.get('origin_type') == 'S3':
            protocol = 'https'
        else:
            protocol_policy = origin.get('protocol_policy', 'https-only')
            protocol = 'https' if 'https' in protocol_policy else 'http'
            
        return f"{protocol}://{domain}{path}/health" if path else f"{protocol}://{domain}/health" 