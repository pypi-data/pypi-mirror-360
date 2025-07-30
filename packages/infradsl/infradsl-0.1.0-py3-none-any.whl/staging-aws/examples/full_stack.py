"""
Full Stack Application - AWS Example
Staging Environment
"""

from infradsl import AWS

# Database
db = (AWS.RDS("app-db")
    .postgresql()
    .db_t3_micro()
    .storage(20)
    .create())

# Web application
app = (AWS.ECS("app-api")
    .fargate()
    .container("myapp:latest")
    .environment("DATABASE_URL", db['endpoint'])
    .create())

# CDN for static assets
cdn = (AWS.CloudFront("app-cdn")
    .static_site("app-assets")
    .create())

print(f"🗄️  Database: {db['endpoint']}")
print(f"🚀 API: {app['url']}")
print(f"📦 CDN: {cdn['domain']}")
