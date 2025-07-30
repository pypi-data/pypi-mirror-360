"""
GCP Secret Manager Configuration Mixin

Chainable configuration methods for Google Cloud Secret Manager.
Provides Rails-like method chaining for fluent secret configuration.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Union


class SecretManagerConfigurationMixin:
    """
    Mixin for Secret Manager configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Secret value and type configuration
    - Replication and high availability settings
    - Rotation and lifecycle management
    - Access control and security settings
    """
    
    def description(self, description: str):
        """Set description for the secret"""
        self.secret_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for Secret Manager operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id:
            self.secret_resource_name = f"projects/{self.project_id}/secrets/{self.secret_name}"
        return self
        
    # Secret value configuration
    def value(self, secret_value: Union[str, dict]):
        """Set secret value (string or JSON object)"""
        self.secret_value = secret_value
        self.secret_binary = None
        self.secret_type = self._get_secret_type_from_value()
        return self
        
    def binary(self, binary_data: bytes):
        """Set binary secret data"""
        self.secret_binary = binary_data
        self.secret_value = None
        self.secret_type = "binary"
        return self
        
    def from_file(self, file_path: str, binary: bool = False):
        """Load secret from file"""
        try:
            with open(file_path, 'rb' if binary else 'r') as f:
                if binary:
                    return self.binary(f.read())
                else:
                    content = f.read()
                    # Try to parse as JSON
                    try:
                        json_content = json.loads(content)
                        return self.value(json_content)
                    except json.JSONDecodeError:
                        return self.value(content)
        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}: {str(e)}")
        
    def from_base64(self, base64_string: str):
        """Set secret from base64 encoded string"""
        try:
            decoded_data = base64.b64decode(base64_string)
            return self.binary(decoded_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 string: {str(e)}")
            
    # Specific secret types
    def database_credentials(self, host: str, username: str, password: str, 
                           database: str = None, port: int = None, engine: str = "postgres"):
        """Configure database credentials"""
        credentials = {
            'host': host,
            'username': username,
            'password': password,
            'engine': engine
        }
        if database:
            credentials['database'] = database
        if port:
            credentials['port'] = port
            
        self.secret_value = credentials
        self.secret_type = "database"
        self.label("type", "database")
        self.label("engine", engine)
        return self
        
    def api_key(self, key: str, additional_data: dict = None):
        """Configure API key with optional metadata"""
        secret_data = {'api_key': key}
        if additional_data:
            secret_data.update(additional_data)
        self.secret_value = secret_data
        self.secret_type = "api_key"
        self.label("type", "api_key")
        return self
        
    def jwt_secret(self, secret: str, algorithm: str = "HS256", additional_config: dict = None):
        """Configure JWT signing secret"""
        jwt_config = {
            'secret': secret,
            'algorithm': algorithm
        }
        if additional_config:
            jwt_config.update(additional_config)
        self.secret_value = jwt_config
        self.secret_type = "jwt"
        self.label("type", "jwt")
        return self
        
    def oauth_credentials(self, client_id: str, client_secret: str, additional_config: dict = None):
        """Configure OAuth application credentials"""
        config = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        if additional_config:
            config.update(additional_config)
        self.secret_value = config
        self.secret_type = "oauth"
        self.label("type", "oauth")
        return self
        
    def certificate(self, private_key: str, certificate: str, ca_chain: str = None):
        """Configure SSL/TLS certificate"""
        cert_config = {
            'private_key': private_key,
            'certificate': certificate
        }
        if ca_chain:
            cert_config['ca_chain'] = ca_chain
        self.secret_value = cert_config
        self.secret_type = "certificate"
        self.label("type", "certificate")
        return self
        
    # Replication configuration
    def automatic_replication(self):
        """Use automatic replication (global availability)"""
        self.replication_policy = "automatic"
        self.replica_locations = []
        return self
        
    def user_managed_replication(self, locations: List[str]):
        """Use user-managed replication in specific locations"""
        # Validate locations
        for location in locations:
            if not self._is_valid_location(location):
                print(f"⚠️  Warning: Invalid location '{location}'. Use valid GCP regions.")
                
        self.replication_policy = "user_managed"
        self.replica_locations = locations
        return self
        
    def single_region(self, region: str):
        """Configure single-region replication"""
        return self.user_managed_replication([region])
        
    def multi_region(self, regions: List[str]):
        """Configure multi-region replication"""
        return self.user_managed_replication(regions)
        
    def global_replication(self):
        """Configure global replication - alias for automatic_replication()"""
        return self.automatic_replication()
        
    # Rotation configuration
    def rotation(self, period_days: int = 90, topic: str = None, next_time: str = None):
        """Enable automatic rotation"""
        if not self._is_valid_rotation_period(period_days * 86400):
            print(f"⚠️  Warning: Invalid rotation period {period_days} days. Must be 1-365 days.")
            
        self.rotation_enabled = True
        self.rotation_period = period_days * 86400  # Convert days to seconds
        
        if topic:
            self.rotation_topic = f"projects/{self.project_id}/topics/{topic}"
        if next_time:
            self.next_rotation_time = next_time
            
        return self
        
    def rotation_days(self, days: int):
        """Set rotation period in days - alias for rotation()"""
        return self.rotation(days)
        
    def weekly_rotation(self):
        """Configure weekly rotation"""
        return self.rotation(7)
        
    def monthly_rotation(self):
        """Configure monthly rotation"""
        return self.rotation(30)
        
    def quarterly_rotation(self):
        """Configure quarterly rotation"""
        return self.rotation(90)
        
    def no_rotation(self):
        """Disable automatic rotation"""
        self.rotation_enabled = False
        self.rotation_period = None
        self.rotation_topic = None
        self.next_rotation_time = None
        return self
        
    # Security and encryption
    def encryption_key(self, kms_key_name: str):
        """Set customer-managed encryption key"""
        self.kms_key_name = kms_key_name
        return self
        
    def allow_access(self, identities: List[str]):
        """Set allowed access identities"""
        self.allowed_access_identities.extend(identities)
        return self
        
    def allow_user(self, email: str):
        """Allow access for specific user"""
        self.allowed_access_identities.append(f"user:{email}")
        return self
        
    def allow_service_account(self, email: str):
        """Allow access for service account"""
        self.allowed_access_identities.append(f"serviceAccount:{email}")
        return self
        
    def allow_group(self, email: str):
        """Allow access for group"""
        self.allowed_access_identities.append(f"group:{email}")
        return self
        
    # Version management
    def max_versions(self, count: int):
        """Set maximum number of versions to keep"""
        if count < 1:
            print(f"⚠️  Warning: Max versions must be at least 1")
            count = 1
        self.max_versions = count
        return self
        
    def version_alias(self, alias: str, version: str = "latest"):
        """Add version alias"""
        self.version_aliases[alias] = version
        return self
        
    def destroy_ttl(self, days: int):
        """Set TTL for destroyed versions"""
        self.version_destroy_ttl = f"{days * 86400}s"
        return self
        
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to secret"""
        self.secret_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.secret_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add annotations to secret"""
        self.secret_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.secret_annotations[key] = value
        return self
        
    # Environment configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.automatic_replication()
                .no_rotation()
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.automatic_replication()
                .monthly_rotation()
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.automatic_replication()
                .quarterly_rotation()
                .max_versions(5)
                .label("environment", "production")
                .label("security", "enhanced"))
                
    # Common service patterns
    def mysql_database(self, host: str, username: str, password: str, database: str = None):
        """Rails convenience: MySQL database credentials"""
        return self.database_credentials(host, username, password, database, 3306, "mysql")
        
    def postgresql_database(self, host: str, username: str, password: str, database: str = None):
        """Rails convenience: PostgreSQL database credentials"""
        return self.database_credentials(host, username, password, database, 5432, "postgres")
        
    def redis_credentials(self, host: str, password: str, port: int = 6379):
        """Rails convenience: Redis credentials"""
        return (self.value({
                    'host': host,
                    'password': password,
                    'port': port,
                    'engine': 'redis'
                })
                .label("type", "cache")
                .label("engine", "redis"))
                
    def mongodb_credentials(self, host: str, username: str, password: str, database: str = None):
        """Rails convenience: MongoDB credentials"""
        return self.database_credentials(host, username, password, database, 27017, "mongodb")
        
    # Third-party service credentials
    def stripe_keys(self, public_key: str, secret_key: str, webhook_secret: str = None):
        """Rails convenience: Stripe API credentials"""
        config = {
            'public_key': public_key,
            'secret_key': secret_key
        }
        if webhook_secret:
            config['webhook_secret'] = webhook_secret
        return (self.value(config)
                .label("type", "payment")
                .label("provider", "stripe"))
                
    def sendgrid_api_key(self, api_key: str, from_email: str = None):
        """Rails convenience: SendGrid API credentials"""
        config = {'api_key': api_key}
        if from_email:
            config['from_email'] = from_email
        return (self.value(config)
                .label("type", "email")
                .label("provider", "sendgrid"))
                
    def twilio_credentials(self, account_sid: str, auth_token: str, phone_number: str = None):
        """Rails convenience: Twilio API credentials"""
        config = {
            'account_sid': account_sid,
            'auth_token': auth_token
        }
        if phone_number:
            config['phone_number'] = phone_number
        return (self.value(config)
                .label("type", "sms")
                .label("provider", "twilio"))
                
    def aws_credentials(self, access_key_id: str, secret_access_key: str, region: str = "us-east-1"):
        """Rails convenience: AWS credentials"""
        return (self.value({
                    'access_key_id': access_key_id,
                    'secret_access_key': secret_access_key,
                    'region': region
                })
                .label("type", "cloud_credentials")
                .label("provider", "aws"))
                
    def gcp_service_account(self, key_json: dict):
        """Rails convenience: GCP service account key"""
        return (self.value(key_json)
                .label("type", "service_account")
                .label("provider", "gcp"))
                
    def azure_credentials(self, client_id: str, client_secret: str, tenant_id: str):
        """Rails convenience: Azure credentials"""
        return (self.value({
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'tenant_id': tenant_id
                })
                .label("type", "cloud_credentials")
                .label("provider", "azure"))
                
    # Security patterns
    def high_security(self):
        """Configure for high security requirements"""
        return (self.quarterly_rotation()
                .max_versions(10)
                .label("security", "high")
                .label("compliance", "required"))
                
    def compliance_ready(self):
        """Configure for compliance requirements"""
        return (self.monthly_rotation()
                .max_versions(12)  # Keep 1 year of versions
                .label("compliance", "sox")
                .label("audit", "required")
                .label("retention", "1year"))
                
    def cost_optimized(self):
        """Configure for cost optimization"""
        return (self.automatic_replication()
                .no_rotation()
                .max_versions(2)
                .label("optimization", "cost"))
                
    # Common deployment patterns
    def microservice_secret(self, service_name: str):
        """Configure for microservice pattern"""
        return (self.label("service", service_name)
                .label("pattern", "microservice")
                .automatic_replication())
                
    def shared_secret(self, shared_by: List[str]):
        """Configure for shared secret pattern"""
        return (self.label("pattern", "shared")
                .label("shared_by", ",".join(shared_by))
                .production())
                
    def temporary_secret(self, ttl_days: int = 7):
        """Configure for temporary secret pattern"""
        return (self.label("pattern", "temporary")
                .label("ttl", f"{ttl_days}days")
                .destroy_ttl(ttl_days)
                .max_versions(1))
                
    # Utility methods
    def clear_value(self):
        """Clear secret value and binary data"""
        self.secret_value = None
        self.secret_binary = None
        self.secret_type = "generic"
        return self
        
    def get_value_type(self) -> str:
        """Get the type of secret value"""
        return self.secret_type
        
    def has_value(self) -> bool:
        """Check if secret has a value set"""
        return self.secret_value is not None or self.secret_binary is not None