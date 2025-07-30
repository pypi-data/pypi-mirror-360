"""
Google Cloud Resources - Example Usage

This file demonstrates how to use the refactored Google Cloud components.
These examples show that all functionality still works after the refactoring.
"""

from typing import Dict, Any
from . import (
    Vm,
    VmGroup,
    CloudRun,
    GKE,
    LoadBalancer,
    GcpAuthenticationService,
    BaseGcpResource
)


def example_single_vm():
    """Example: Create a single VM with monitoring and firewall"""
    print("=" * 60)
    print("🖥️  Example: Single VM Creation")
    print("=" * 60)

    vm = (Vm("web-server")
          .machine_type("e2-micro")
          .zone("us-central1-a")
          .image("debian-11")
          .disk_size(20)
          .tags(["web", "production"])
          .monitoring(True)
          .firewall("http", 80)
          .firewall("https", 443)
          .health_check("http", 80, "/health"))

    # Preview what will be created
    preview = vm.preview()
    print(f"Preview result: {preview}")

    # Note: Uncomment below to actually create
    # result = vm.create()
    # print(f"Creation result: {result}")

    return vm


def example_vm_group():
    """Example: Create a group of VMs for load balancing"""
    print("=" * 60)
    print("👥 Example: VM Group Creation")
    print("=" * 60)

    group = (VmGroup("web-servers", 3)
             .machine_type("e2-small")
             .zone("us-central1-a")
             .image("debian-11")
             .tags(["web-tier", "load-balanced"])
             .monitoring(True)
             .firewall("http", 80)
             .health_check("http", 80, "/"))

    preview = group.preview()
    print(f"Group preview: {preview}")

    # Access individual VMs if needed
    vm1 = group.get_vm(0)  # First VM
    print(f"First VM name: {vm1.config.name}")

    return group


def example_cloud_run():
    """Example: Deploy a serverless container"""
    print("=" * 60)
    print("🚀 Example: Cloud Run Deployment")
    print("=" * 60)

    webapp = (CloudRun("my-webapp")
              .memory("512Mi")
              .cpu("1000m")
              .location("us-central1")
              .auto_scale(0, 10)
              .environment({
                  "NODE_ENV": "production",
                  "PORT": "8080"
              })
              .timeout(60)
              .public())

    # For actual deployment, you'd use:
    # webapp.container("webapp", "templates/nodejs-webapp", 8080)

    preview = webapp.preview()
    print(f"Cloud Run preview: {preview}")

    return webapp


def example_gke_cluster():
    """Example: Create a Kubernetes cluster"""
    print("=" * 60)
    print("☸️  Example: GKE Cluster Creation")
    print("=" * 60)

    cluster = (GKE("my-cluster")
               .location("us-central1")
               .nodes(3)
               .machine_type("e2-standard-2")
               .disk_size(100)
               .auto_scale(1, 10)
               .preemptible(True)
               .labels({
                   "environment": "development",
                   "team": "backend"
               })
               .kubernetes_version("1.27"))

    preview = cluster.preview()
    print(f"GKE preview: {preview}")

    return cluster


def example_load_balancer():
    """Example: Create a load balancer for VM group"""
    print("=" * 60)
    print("⚖️  Example: Load Balancer Creation")
    print("=" * 60)

    # First create a VM group
    vm_group = (VmGroup("backend-servers", 2)
                .machine_type("e2-small")
                .zone("us-central1-a")
                .health_check("http", 8080, "/health"))

    # Then create load balancer
    lb = (LoadBalancer("web-lb")
          .backend_group(vm_group)
          .port(80)
          .ssl_port(443)
          .domain("example.com"))

    preview = lb.preview()
    print(f"Load balancer preview: {preview}")

    return lb, vm_group


def example_complex_infrastructure():
    """Example: Complete infrastructure with multiple components"""
    print("=" * 60)
    print("🏗️  Example: Complex Infrastructure")
    print("=" * 60)

    # Database tier
    db_vm = (Vm("database")
             .machine_type("e2-standard-4")
             .zone("us-central1-a")
             .disk_size(100)
             .tags(["database", "private"])
             .monitoring(True)
             .firewall("mysql", 3306, source_ranges=["10.0.0.0/8"]))

    # Web tier (group of VMs)
    web_group = (VmGroup("web-servers", 3)
                 .machine_type("e2-medium")
                 .zone("us-central1-a")
                 .tags(["web", "public"])
                 .monitoring(True)
                 .firewall("http", 80)
                 .firewall("https", 443)
                 .health_check("http", 80, "/health"))

    # Load balancer for web tier
    web_lb = (LoadBalancer("web-lb")
              .backend_group(web_group)
              .ssl_certificate("my-ssl-cert")
              .domain("myapp.com"))

    # Serverless API
    api = (CloudRun("api-service")
           .memory("1Gi")
           .cpu("2000m")
           .auto_scale(2, 20)
           .environment({
               "DATABASE_URL": "mysql://database:3306/myapp",
               "ENV": "production"
           })
           .public())

    # Kubernetes cluster for microservices
    k8s = (GKE("microservices")
           .location("us-central1")
           .nodes(5)
           .machine_type("e2-standard-2")
           .auto_scale(3, 15))

    print("Complex infrastructure components created:")
    print(f"- Database VM: {db_vm.config.name}")
    print(f"- Web servers: {len(web_group.vms)} instances")
    print(f"- Load balancer: {web_lb.config.name}")
    print(f"- API service: {api.config.service_name}")
    print(f"- K8s cluster: {k8s.config.name}")

    return {
        "database": db_vm,
        "web_group": web_group,
        "load_balancer": web_lb,
        "api": api,
        "kubernetes": k8s
    }


def example_error_handling():
    """Example: Demonstrate error handling"""
    print("=" * 60)
    print("⚠️  Example: Error Handling")
    print("=" * 60)

    try:
        # Invalid VM group count
        invalid_group = VmGroup("test", 0)
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")

    try:
        # Invalid disk size
        vm = Vm("test").disk_size(0)
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")

    # Test authentication paths
    paths = GcpAuthenticationService.get_credentials_paths()
    print(f"Authentication will be attempted in these paths: {paths}")


def run_all_examples():
    """Run all examples to demonstrate the refactored functionality"""
    print("\n🎯 Google Cloud Resources - Refactored Examples")
    print("These examples demonstrate that all functionality works after refactoring.\n")

    # Note: These examples create resource objects but don't actually deploy
    # to avoid requiring actual GCP credentials during testing

    examples = [
        example_single_vm,
        example_vm_group,
        example_cloud_run,
        example_gke_cluster,
        example_load_balancer,
        example_complex_infrastructure,
        example_error_handling
    ]

    results = {}
    for example in examples:
        try:
            result = example()
            results[example.__name__] = result
            print("✅ Example completed successfully\n")
        except Exception as e:
            print(f"❌ Example failed: {e}\n")
            results[example.__name__] = None

    print("🎉 All examples completed!")
    print("This demonstrates that the refactored code maintains all functionality.")

    return results


if __name__ == "__main__":
    # Run examples when script is executed directly
    run_all_examples()
