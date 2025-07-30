"""
Help system and documentation for Google Cloud Load Balancer operations.
This module provides comprehensive help, examples, and troubleshooting guides.
"""

from typing import Dict, List, Any


class LoadBalancerHelpSystem:
    """Provides comprehensive help and documentation for load balancer operations"""
    
    @staticmethod
    def get_quick_start_guide() -> str:
        """Get a quick start guide for load balancer creation"""
        return """
🚀 Quick Start Guide: Google Cloud Load Balancer

1. **Basic Load Balancer**
   ```python
   from ..googlecloud_managers.load_balancer import LoadBalancerConfig, BackendConfig
   
   # Create backend configuration
   backend = BackendConfig(
       name="web-backend",
       zone="us-central1-a",
       vms=["web-server-1", "web-server-2"],
       port=80
   )
   
   # Create load balancer configuration
   config = LoadBalancerConfig(
       name="my-load-balancer",
       port=80,
       backends=[backend]
   )
   
   # Create the load balancer
   manager = LoadBalancerManager(project_id, credentials)
   result = manager.create_load_balancer(config)
   ```

2. **HTTPS Load Balancer**
   ```python
   config = LoadBalancerConfig(
       name="secure-lb",
       port=80,
       ssl_certificate="my-ssl-cert",
       ssl_port=443,
       backends=[backend]
   )
   ```

3. **Multiple Backends**
   ```python
   backend1 = BackendConfig(name="web-backend", zone="us-central1-a", vms=["web1"], port=80)
   backend2 = BackendConfig(name="api-backend", zone="us-central1-b", vms=["api1"], port=8080)
   
   config = LoadBalancerConfig(
       name="multi-backend-lb",
       port=80,
       backends=[backend1, backend2]
   )
   ```
"""

    @staticmethod
    def get_configuration_reference() -> str:
        """Get configuration reference documentation"""
        return """
📋 Configuration Reference

**LoadBalancerConfig**
- `name` (str): Load balancer name (lowercase, hyphens, numbers)
- `port` (int): HTTP port (1-65535)
- `ssl_certificate` (str, optional): SSL certificate name
- `ssl_port` (int, optional): HTTPS port (1-65535)
- `backends` (List[BackendConfig]): List of backend configurations

**BackendConfig**
- `name` (str): Backend name (lowercase, hyphens, numbers)
- `zone` (str): Google Cloud zone (e.g., "us-central1-a")
- `vms` (List[str], optional): List of VM names
- `port` (int, optional): Backend port (defaults to load balancer port)

**Naming Rules**
- Names must be 1-63 characters
- Only lowercase letters, numbers, hyphens
- Must start with a letter
- Cannot start with "goog" or "google"
- Must end with a letter or number
"""

    @staticmethod
    def get_troubleshooting_guide() -> str:
        """Get comprehensive troubleshooting guide"""
        return """
🔧 Troubleshooting Guide

**Common Issues & Solutions**

1. **Permission Errors**
   ```
   Error: "The caller does not have permission"
   Solution: Add these IAM roles to your service account:
   - Compute Load Balancer Admin
   - Compute Instance Admin
   - Compute Network Admin
   - Service Account User
   ```

2. **Timeout Errors**
   ```
   Error: "Operation timed out"
   Solution: This is normal for Google Cloud operations
   - Check Google Cloud Console for resource status
   - Resources may be created despite timeout
   - Try again in a few minutes
   ```

3. **Resource Not Found**
   ```
   Error: "Resource not found"
   Solution: 
   - VMs may still be being created
   - Check zone specifications
   - Verify resource names
   ```

4. **Already Exists Errors**
   ```
   Error: "Resource already exists"
   Solution: This is usually not a problem
   - System will use existing resource
   - Delete existing resource if you want to recreate
   ```

5. **Health Check Failures**
   ```
   Issue: Backends showing as unhealthy
   Solution:
   - Ensure VMs are running
   - Check firewall rules allow traffic
   - Verify applications are listening on correct ports
   - Check health check configuration
   ```

**Debugging Steps**
1. Check Google Cloud Console for resource status
2. Verify service account permissions
3. Check VM status and network configuration
4. Review operation logs in Google Cloud Console
5. Try the operation again in a few minutes
"""

    @staticmethod
    def get_best_practices() -> str:
        """Get best practices for load balancer configuration"""
        return """
💡 Best Practices

**Naming Conventions**
- Use descriptive names: `web-load-balancer`, `api-lb-prod`
- Include environment: `web-lb-dev`, `web-lb-staging`, `web-lb-prod`
- Use consistent patterns across your infrastructure

**Zone Distribution**
- Distribute backends across multiple zones for high availability
- Use zones in the same region for better performance
- Consider disaster recovery scenarios

**Security**
- Use HTTPS for production workloads
- Configure proper firewall rules
- Use managed SSL certificates when possible
- Implement proper IAM roles and permissions

**Performance**
- Use appropriate instance types for your workload
- Monitor backend health and performance
- Configure proper health checks
- Consider using managed instance groups for auto-scaling

**Monitoring**
- Set up monitoring and alerting
- Monitor backend health status
- Track request latency and throughput
- Set up logging for debugging

**Cost Optimization**
- Use appropriate instance types
- Consider using preemptible instances for non-critical workloads
- Monitor and optimize resource usage
- Use committed use discounts for predictable workloads
"""

    @staticmethod
    def get_examples() -> str:
        """Get comprehensive examples"""
        return """
📚 Examples

**Example 1: Simple Web Server Load Balancer**
```python
from ..googlecloud_managers.load_balancer import (
    LoadBalancerConfig, BackendConfig, LoadBalancerManager
)

# Create backend for web servers
web_backend = BackendConfig(
    name="web-servers",
    zone="us-central1-a",
    vms=["web-server-1", "web-server-2", "web-server-3"],
    port=80
)

# Create load balancer
config = LoadBalancerConfig(
    name="web-load-balancer",
    port=80,
    backends=[web_backend]
)

# Deploy
manager = LoadBalancerManager(project_id, credentials)
result = manager.create_load_balancer(config)
print(f"Load balancer IP: {result['ip_address']}")
```

**Example 2: Multi-Zone High Availability**
```python
# Backend in zone A
backend_a = BackendConfig(
    name="web-backend-a",
    zone="us-central1-a",
    vms=["web-a-1", "web-a-2"],
    port=80
)

# Backend in zone B
backend_b = BackendConfig(
    name="web-backend-b", 
    zone="us-central1-b",
    vms=["web-b-1", "web-b-2"],
    port=80
)

# High availability load balancer
config = LoadBalancerConfig(
    name="ha-web-lb",
    port=80,
    backends=[backend_a, backend_b]
)
```

**Example 3: HTTPS Load Balancer**
```python
# Backend for API servers
api_backend = BackendConfig(
    name="api-servers",
    zone="us-central1-a",
    vms=["api-server-1", "api-server-2"],
    port=8080
)

# HTTPS load balancer
config = LoadBalancerConfig(
    name="secure-api-lb",
    port=80,
    ssl_certificate="my-ssl-certificate",
    ssl_port=443,
    backends=[api_backend]
)
```

**Example 4: Microservices Load Balancer**
```python
# Web service backend
web_backend = BackendConfig(
    name="web-service",
    zone="us-central1-a",
    vms=["web-1", "web-2"],
    port=3000
)

# API service backend
api_backend = BackendConfig(
    name="api-service",
    zone="us-central1-b", 
    vms=["api-1", "api-2"],
    port=8080
)

# Database service backend
db_backend = BackendConfig(
    name="db-service",
    zone="us-central1-c",
    vms=["db-1"],
    port=5432
)

# Microservices load balancer
config = LoadBalancerConfig(
    name="microservices-lb",
    port=80,
    backends=[web_backend, api_backend, db_backend]
)
```
"""

    @staticmethod
    def get_help_menu() -> str:
        """Get interactive help menu"""
        return """
🎯 Load Balancer Help Menu

Choose a topic:
1. Quick Start Guide
2. Configuration Reference  
3. Examples
4. Troubleshooting Guide
5. Best Practices
6. All Documentation

Enter a number (1-6) or 'q' to quit:
"""

    @staticmethod
    def show_help(topic: str = None) -> str:
        """Show help for a specific topic or all topics"""
        if topic == "quick-start":
            return LoadBalancerHelpSystem.get_quick_start_guide()
        elif topic == "config":
            return LoadBalancerHelpSystem.get_configuration_reference()
        elif topic == "examples":
            return LoadBalancerHelpSystem.get_examples()
        elif topic == "troubleshooting":
            return LoadBalancerHelpSystem.get_troubleshooting_guide()
        elif topic == "best-practices":
            return LoadBalancerHelpSystem.get_best_practices()
        elif topic == "all":
            return (
                LoadBalancerHelpSystem.get_quick_start_guide() + "\n" +
                LoadBalancerHelpSystem.get_configuration_reference() + "\n" +
                LoadBalancerHelpSystem.get_examples() + "\n" +
                LoadBalancerHelpSystem.get_troubleshooting_guide() + "\n" +
                LoadBalancerHelpSystem.get_best_practices()
            )
        else:
            return LoadBalancerHelpSystem.get_help_menu()


class LoadBalancerCLIHelp:
    """CLI-specific help and usage information"""
    
    @staticmethod
    def get_cli_usage() -> str:
        """Get CLI usage information"""
        return """
🌐 Load Balancer CLI Usage

**Basic Commands**
```bash
# Create a load balancer
oopscli googlecloud load-balancer create --config config.yaml

# List load balancers
oopscli googlecloud load-balancer list

# Delete a load balancer
oopscli googlecloud load-balancer delete --name my-lb

# Get load balancer status
oopscli googlecloud load-balancer status --name my-lb
```

**Configuration File Format (YAML)**
```yaml
name: my-load-balancer
port: 80
ssl_certificate: my-ssl-cert  # optional
ssl_port: 443                 # optional
backends:
  - name: web-backend
    zone: us-central1-a
    vms:
      - web-server-1
      - web-server-2
    port: 80
  - name: api-backend
    zone: us-central1-b
    vms:
      - api-server-1
    port: 8080
```

**Command Options**
- `--config`: Path to configuration file
- `--name`: Load balancer name
- `--project`: Google Cloud project ID
- `--zone`: Default zone for resources
- `--dry-run`: Show what would be created without actually creating
- `--verbose`: Show detailed output
- `--help`: Show help information
"""

    @staticmethod
    def get_cli_examples() -> str:
        """Get CLI usage examples"""
        return """
📖 CLI Examples

**Create a simple load balancer**
```bash
# Create config.yaml
cat > config.yaml << EOF
name: web-lb
port: 80
backends:
  - name: web-backend
    zone: us-central1-a
    vms: [web-1, web-2]
    port: 80
EOF

# Create the load balancer
oopscli googlecloud load-balancer create --config config.yaml
```

**Create HTTPS load balancer**
```bash
cat > https-config.yaml << EOF
name: secure-web-lb
port: 80
ssl_certificate: my-ssl-cert
ssl_port: 443
backends:
  - name: web-backend
    zone: us-central1-a
    vms: [web-1, web-2]
    port: 80
EOF

oopscli googlecloud load-balancer create --config https-config.yaml
```

**Check load balancer status**
```bash
oopscli googlecloud load-balancer status --name web-lb
```

**Delete load balancer**
```bash
oopscli googlecloud load-balancer delete --name web-lb
```

**Dry run (preview)**
```bash
oopscli googlecloud load-balancer create --config config.yaml --dry-run
```
""" 