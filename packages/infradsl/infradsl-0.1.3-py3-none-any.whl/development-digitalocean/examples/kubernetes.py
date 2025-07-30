"""
Kubernetes Cluster - DigitalOcean Example
Development Environment
"""

from infradsl import DigitalOcean

# Kubernetes cluster
cluster = (DigitalOcean.KubernetesCluster("app-cluster")
    .basic()
    .node_pool("default", 2)
    .create())

print(f"☸️  Kubernetes cluster: {cluster['cluster_name']}")
print(f"🔗 Kubeconfig: {cluster['kubeconfig']}")
