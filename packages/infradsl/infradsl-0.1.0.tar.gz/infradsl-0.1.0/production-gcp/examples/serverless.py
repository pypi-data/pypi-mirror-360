"""
Serverless Application - Google Cloud Example
Production Environment
"""

from infradsl import GoogleCloud

# Cloud Run service
api = (GoogleCloud.CloudRun("api-service")
    .container("myapp:latest")
    .public()
    .create())

# Cloud Functions
function = (GoogleCloud.CloudFunctions("webhook")
    .runtime("python39")
    .trigger("http")
    .create())

print(f"🚀 API: {api['url']}")
print(f"⚡ Function: {function['url']}")
