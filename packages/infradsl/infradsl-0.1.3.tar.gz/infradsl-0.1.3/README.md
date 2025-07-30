# InfraDSL - The Rails of Modern Infrastructure

> "Infrastructure as simple as business logic"

InfraDSL brings Rails-like simplicity to cloud infrastructure management. Deploy production-ready applications to AWS, Google Cloud, and DigitalOcean with 95% less code than traditional tools. Currently, in active development. Any feedback is welcome!

## 🚀 Quick Start

### Install
```bash
pip install infradsl
```

### Deploy in 30 seconds
```python
from infradsl import AWS, GoogleCloud, DigitalOcean

# Deploy a web server in one line
server = AWS.EC2("web-server").t3_micro().ubuntu().service("nginx").create()

# Container app to Google Cloud Run
app = GoogleCloud.CloudRun("my-app").container("webapp", "./src").public().create()

# Complete production stack
database = AWS.RDS("app-db").postgresql().production().create()
storage = AWS.S3("app-assets").website().public().create()
api = AWS.ECS("app-api").fargate().container("api:latest").create()
```

**Result**: Production infrastructure with auto-scaling, HTTPS, monitoring, and enterprise security.

## 🎯 Revolutionary Features

### Cross-Cloud Magic
InfraDSL automatically selects optimal cloud providers per service based on cost, performance, and compliance:

```python
from infradsl import InfraDSL

app = InfraDSL.Application("my-app")
    .auto_optimize()
    .database("postgresql")      # → GCP (best price/performance)
    .compute("web-servers")      # → AWS (best global coverage)
    .cdn("static-assets")        # → Cloudflare (best edge network)
    .storage("user-uploads")     # → DigitalOcean (best simplicity)
    .create()
```

### Universal Provider Support
- **AWS**: EC2, ECS, RDS, S3, Lambda, CloudFront, Route53
- **Google Cloud**: GKE, Cloud Run, Compute Engine, Cloud SQL, Cloud Storage
- **DigitalOcean**: Droplets, Kubernetes, Databases, Spaces, Load Balancers
- **Cloudflare**: CDN, DNS, Workers, R2 Storage, SSL/TLS

### CLI Commands
```bash
infradsl init my-project aws          # Initialize new project
infradsl preview main.py              # Preview changes
infradsl apply main.py                # Deploy infrastructure
infradsl destroy main.py              # Clean up resources
infradsl doctor                       # Check setup and diagnose issues
```

## 🔧 Setup & Authentication

### AWS Credentials
```bash
# Via AWS CLI
aws configure

# Or environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Google Cloud Credentials
```bash
# Via gcloud CLI
gcloud auth application-default login

# Or service account key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### DigitalOcean Token
```bash
export DIGITALOCEAN_TOKEN=your_do_token
```

## 💻 Usage Examples

### AWS Infrastructure
```python
from infradsl import AWS

# Simple web server
server = AWS.EC2("web-server").t3_micro().ubuntu().create()

# Production API with load balancer
api = (AWS.ECS("production-api")
    .fargate()
    .container("api:latest")
    .auto_scale(min=2, max=50)
    .load_balancer()
    .create())

# Database with automated backups
db = (AWS.RDS("app-db")
    .postgresql()
    .production()
    .encrypted()
    .create())
```

### Google Cloud
```python
from infradsl import GoogleCloud

# Serverless container
app = (GoogleCloud.CloudRun("my-app")
    .container("webapp", "./src")
    .public()
    .create())

# Kubernetes cluster
cluster = (GoogleCloud.GKE("production")
    .location("us-central1")
    .auto_scale(min_nodes=3, max_nodes=20)
    .create())
```

### DigitalOcean
```python
from infradsl import DigitalOcean

# Simple droplet
droplet = (DigitalOcean.Droplet("web-server")
    .size("s-2vcpu-2gb")
    .region("nyc1")
    .create())

# Kubernetes cluster
cluster = (DigitalOcean.Kubernetes("app-cluster")
    .region("fra1")
    .nodes(3)
    .create())
```

## 🏗️ Key Benefits

### 95% Code Reduction
- **Kubernetes YAML**: 500+ lines → 1 line
- **Terraform**: 100+ lines → 1 line  
- **Docker Configuration**: 50+ lines → 0 lines (automatic)

### Developer Experience
- **Time to Production**: Days → Minutes
- **Learning Curve**: Weeks → 5 minutes
- **Rails-like Simplicity**: Intuitive, chainable API

### Production Ready
- **Security**: Automatic best practices
- **Auto-scaling**: Built-in by default
- **Monitoring**: Enterprise-grade observability

## 🛣️ What's Next

- **Template Marketplace**: Reusable infrastructure patterns
- **Cost Optimization**: Automatic resource rightsizing
- **Multi-Cloud Intelligence**: Cross-provider optimization
- **IDE Integration**: VS Code and JetBrains extensions

## 📚 Documentation

Visit **https://docs.infradsl.dev** for complete documentation, tutorials, and examples.

## 🤝 Contributing

We welcome contributions! Check out our [GitHub repository](https://github.com/biaandersson/infradsl.dev) for issues and contribution guidelines.

---

*Built with ❤️ for Engineers who want to ship, not configure infrastructure.*
