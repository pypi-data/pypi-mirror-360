"""
Simple Web Server - AWS Example
Test Environment
"""

from infradsl import AWS

# Simple web server with nginx
server = (AWS.EC2("simple-web")
    .t3_micro()
    .ubuntu()
    .service("nginx")
    .public_ip()
    .create())

print(f"🌐 Web server ready at: {server['ip_address']}")
