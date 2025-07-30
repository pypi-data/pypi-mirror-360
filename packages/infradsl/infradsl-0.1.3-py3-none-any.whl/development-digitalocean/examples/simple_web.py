"""
Simple Web Server - DigitalOcean Example
Development Environment
"""

from infradsl import DigitalOcean

# Simple web server with nginx
server = (DigitalOcean.Droplet("simple-web")
    .basic()
    .ubuntu()
    .service("nginx")
    .public_ip()
    .create())

print(f"🌐 Web server ready at: {server['ip_address']}")
