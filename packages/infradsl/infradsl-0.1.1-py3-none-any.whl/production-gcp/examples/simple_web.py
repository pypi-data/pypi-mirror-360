"""
Simple Web Server - Google Cloud Example
Production Environment

This example shows how to create a simple web server with nginx.

It uses the default machine type and image, and installs nginx.

It also creates a public IP address for the server.

Fetching the service from the templates directory.
"""

from infradsl import GoogleCloud

# Simple web server with nginx
server = (GoogleCloud.VM("simple-web")
    .e2_micro()
    .ubuntu()
    .service("nginx")
    .public_ip()
    .create())

print(f"🌐 Web server ready at: {server['ip_address']}")
