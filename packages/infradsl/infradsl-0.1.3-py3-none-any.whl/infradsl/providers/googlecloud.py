"""
Google Cloud Provider - Main Entry Point

This module provides a clean, Rails-like interface for Google Cloud Platform resources.
It acts as the main entry point and imports all components from their respective modules.

Usage:
    from infradsl.providers.googlecloud import GoogleCloud

    # Create a VM
    vm = GoogleCloud.Vm("my-vm").machine_type("e2-micro").zone("us-central1-a").create()

    # Create a Cloud Run service
    webapp = GoogleCloud.CloudRun("my-webapp").container("app", "templates/nodejs-webapp").public().create()

    # Create a VM group
    group = GoogleCloud.VmGroup("web-servers", 3).machine_type("e2-small").create()

    # Create a GKE cluster
    cluster = GoogleCloud.GKE("my-cluster").location("us-central1").nodes(3).create()
"""

from .googlecloud_resources import (
    Vm,
    VmGroup,
    CloudRun,
    GKE,
    LoadBalancer,
    Storage,
    CloudSQL,
    BigQuery,
    CloudFunctions,
    Memorystore,
    PubSub,
    GcpAuthenticationService,
    BaseGcpResource,
    # Firebase services
    FirebaseHosting,
    FirebaseAuth,
    Firestore,
    FirebaseFunctions,
    FirebaseStorage,
    # CI/CD services
    CloudBuild,
)

# Re-export all resource classes for direct import
__all__ = [
    'GoogleCloud',
    'Vm',
    'VmGroup',
    'CloudRun',
    'GKE',
    'LoadBalancer',
    'Storage',
    'CloudSQL',
    'create_load_balancer',
    'GcpAuthenticationService',
    'BaseGcpResource',
    # Firebase services
    'FirebaseHosting',
    'FirebaseAuth',
    'Firestore',
    'FirebaseFunctions',
    'FirebaseStorage',
]


class GoogleCloud:
    """
    Main entry point for Google Cloud resources.

    This class provides static factory methods for creating Google Cloud resources
    with a Rails-like, convention-over-configuration approach.
    """

    @staticmethod
    def Vm(name: str) -> Vm:
        """
        Create a single Google Cloud VM resource.

        Args:
            name: Name of the VM instance

        Returns:
            Vm: A configured VM instance ready for chaining

        Example:
            vm = (GoogleCloud.Vm("web-server")
                    .machine_type("e2-micro")
                    .zone("us-central1-a")
                    .image("debian-11")
                    .create())
        """
        return Vm(name)

    @staticmethod
    def VmGroup(name: str, count: int) -> VmGroup:
        """
        Create a group of identical Google Cloud VM resources.

        Args:
            name: Base name for the VM group (VMs will be named {name}-1, {name}-2, etc.)
            count: Number of VMs to create in the group

        Returns:
            VmGroup: A configured VM group ready for chaining

        Example:
            group = (GoogleCloud.VmGroup("web-servers", 3)
                       .machine_type("e2-small")
                       .zone("us-central1-a")
                       .create())
        """
        return VmGroup(name, count)

    @staticmethod
    def GKE(name: str) -> GKE:
        """
        Create a GKE cluster with Rails-like simplicity.

        Args:
            name: Name of the GKE cluster

        Returns:
            GKE: A configured GKE cluster ready for chaining

        Example:
            cluster = (GoogleCloud.GKE("my-cluster")
                         .location("us-central1")
                         .nodes(3)
                         .machine_type("e2-standard-2")
                         .auto_scale(1, 10)
                         .create())
        """
        return GKE(name)

    @staticmethod
    def CloudRun(name: str) -> CloudRun:
        """
        Create a serverless container service with Rails magic.

        Args:
            name: Name of the Cloud Run service

        Returns:
            CloudRun: A configured Cloud Run service ready for chaining

        Example:
            webapp = (GoogleCloud.CloudRun("my-webapp")
                        .container("webapp", "templates/nodejs-webapp", 8080)
                        .public()
                        .create())
        """
        return CloudRun(name)

    @staticmethod
    def LoadBalancer(name: str) -> LoadBalancer:
        """
        Create a standalone load balancer for web services.

        Args:
            name: Name of the load balancer

        Returns:
            LoadBalancer: A configured load balancer ready for chaining

        Example:
            lb = (GoogleCloud.LoadBalancer("web-lb")
                    .backend("web-server-1", "us-central1-a", 80)
                    .ssl_certificate("my-cert")
                    .create())
        """
        return LoadBalancer(name)

    @staticmethod
    def Storage(name: str) -> Storage:
        """
        Create a Cloud Storage bucket with Rails-like simplicity.

        Args:
            name: Name of the storage bucket

        Returns:
            Storage: A configured storage bucket ready for chaining

        Example:
            bucket = (GoogleCloud.Storage("my-app-data")
                        .location("US")
                        .lifecycle("general")
                        .upload("./data.json")
                        .create())
        """
        return Storage(name)

    @staticmethod
    def CloudSQL(name: str) -> CloudSQL:
        """
        Create a Cloud SQL database with Rails-like simplicity.

        Args:
            name: Name of the database instance

        Returns:
            CloudSQL: A configured database instance ready for chaining

        Example:
            database = (GoogleCloud.CloudSQL("my-app-db")
                           .postgres()
                           .production_db()
                           .region("us-central1")
                           .create())
        """
        return CloudSQL(name)

    @staticmethod
    def BigQuery(name: str) -> BigQuery:
        """
        Create a BigQuery data warehouse with Rails-like simplicity.

        Args:
            name: Name of the dataset

        Returns:
            BigQuery: A configured BigQuery dataset ready for chaining

        Example:
            # Simple analytics dataset
            warehouse = GoogleCloud.BigQuery("analytics").analytics_dataset().create()

            # Complete data pipeline
            pipeline = (GoogleCloud.BigQuery("user_analytics")
                       .analytics_dataset()
                       .web_analytics_table("page_views")
                       .user_events_table("events")
                       .create())
        """
        return BigQuery(name)

    @staticmethod
    def CloudFunctions(name: str) -> CloudFunctions:
        """
        Create a Cloud Function with Rails-like simplicity.

        Args:
            name: Name of the function

        Returns:
            CloudFunctions: A configured Cloud Function ready for chaining

        Example:
            # Simple HTTP API
            api = GoogleCloud.CloudFunctions("hello-api").http().source("functions/hello/").create()

            # Data processor
            processor = (GoogleCloud.CloudFunctions("data-processor")
                        .storage_trigger("uploads")
                        .processor_function()
                        .source("functions/processor/")
                        .create())
        """
        return CloudFunctions(name)

    @staticmethod
    def Memorystore(name: str):
        """
        Create a Memorystore Redis instance with Rails-like simplicity.

        Args:
            name: Name of the Redis instance

        Returns:
            Memorystore: A configured Redis instance ready for chaining

        Examples:
            # Simple Redis cache
            cache = GoogleCloud.Memorystore("app-cache").simple_cache().create()

            # Session store with high availability
            sessions = (GoogleCloud.Memorystore("user-sessions")
                       .session_store()
                       .standard_ha()
                       .memory_size(4)
                       .create())

            # High-performance cache with read replicas
            cluster = (GoogleCloud.Memorystore("api-cache")
                      .high_performance_cache()
                      .read_replicas(2)
                      .persistence(True)
                      .create())

            # Production setup with maintenance window
            prod_cache = (GoogleCloud.Memorystore("prod-cache")
                         .production()
                         .memory_size(16)
                         .encryption()
                         .maintenance_window("SUNDAY", 3)
                         .create())
        """
        from .googlecloud_resources.memorystore import Memorystore
        return Memorystore(name)

    @staticmethod
    def PubSub(name: str):
        """Create Google Cloud Pub/Sub resource"""
        from .googlecloud_resources.pubsub import PubSub
        return PubSub(name)

    @staticmethod
    def CertificateManager(name: str):
        """Create Google Cloud Certificate Manager resource"""
        from .googlecloud_resources.certificate_manager import CertificateManager
        return CertificateManager(name)

    @staticmethod
    def SecretManager(name: str):
        """Create Google Cloud Secret Manager resource"""
        from .googlecloud_resources.secret_manager import SecretManager
        return SecretManager(name)

    # ========== CI/CD Services ==========
    
    @staticmethod
    def CloudBuild(name: str) -> CloudBuild:
        """
        Create Cloud Build CI/CD pipeline for automation.
        
        Args:
            name: Name of the build pipeline
            
        Returns:
            CloudBuild: A configured build pipeline ready for chaining
            
        Example:
            pipeline = (GoogleCloud.CloudBuild("my-pipeline")
                          .project("my-project")
                          .github_repo("https://github.com/user/repo")
                          .step("test").image("node:18").script(["npm test"])
                          .create())
        """
        return CloudBuild(name)

    # ========== Firebase Services ==========
    
    @staticmethod
    def FirebaseHosting(name: str) -> FirebaseHosting:
        """
        Create Firebase Hosting site for web applications.
        
        Args:
            name: Name of the hosting site
            
        Returns:
            FirebaseHosting: A configured hosting site ready for chaining
            
        Example:
            site = (GoogleCloud.FirebaseHosting("my-app")
                      .project("my-project")
                      .custom_domain("myapp.com")
                      .create())
        """
        return FirebaseHosting(name)
    
    @staticmethod  
    def FirebaseAuth(name: str) -> FirebaseAuth:
        """
        Create Firebase Authentication service.
        
        Args:
            name: Name of the authentication service
            
        Returns:
            FirebaseAuth: A configured auth service ready for chaining
            
        Example:
            auth = (GoogleCloud.FirebaseAuth("app-auth")
                      .project("my-project")
                      .google_oauth()
                      .create())
        """
        return FirebaseAuth(name)
    
    @staticmethod
    def Firestore(name: str) -> Firestore:
        """
        Create Firestore database.
        
        Args:
            name: Name of the database
            
        Returns:
            Firestore: A configured database ready for chaining
            
        Example:
            db = (GoogleCloud.Firestore("app-db")
                    .project("my-project")
                    .production_database()
                    .create())
        """
        return Firestore(name)
    
    @staticmethod
    def FirebaseFunctions(name: str) -> FirebaseFunctions:
        """
        Create Firebase Functions for serverless backend.
        
        Args:
            name: Name of the functions service
            
        Returns:
            FirebaseFunctions: A configured functions service ready for chaining
            
        Example:
            functions = (GoogleCloud.FirebaseFunctions("api")
                           .project("my-project")
                           .node_runtime("18")
                           .create())
        """
        return FirebaseFunctions(name)
    
    @staticmethod
    def FirebaseStorage(name: str) -> FirebaseStorage:
        """
        Create Firebase Storage for file uploads.
        
        Args:
            name: Name of the storage service
            
        Returns:
            FirebaseStorage: A configured storage service ready for chaining
            
        Example:
            storage = (GoogleCloud.FirebaseStorage("uploads")
                         .project("my-project")
                         .public_access()
                         .create())
        """
        return FirebaseStorage(name)

    @staticmethod
    def APIGateway(name: str):
        """
        Create an API Gateway with Rails-like simplicity.

        Args:
            name: API Gateway name

        Returns:
            APIGateway: A configured API Gateway ready for chaining

        Examples:
            # Simple Cloud Function API
            api = (GoogleCloud.APIGateway("my-api")
                  .function_api("hello-function")
                  .create())

            # REST API with multiple routes
            rest_api = (GoogleCloud.APIGateway("user-api")
                       .cloud_function_backend("user-service")
                       .get("/users", "cloud_function", "user-service")
                       .post("/users", "cloud_function", "user-service")
                       .cors()
                       .create())

            # Microservice with Cloud Run backend
            service = (GoogleCloud.APIGateway("orders-gateway")
                      .cloud_run_backend("orders-service", "https://orders-xyz.run.app")
                      .get("/orders", "cloud_run", "orders-service")
                      .microservice_api()
                      .create())
        """
        from .googlecloud_resources.api_gateway import APIGateway
        return APIGateway(name)

    @staticmethod
    def authenticate(credentials_path: str | None = None) -> bool:
        """
        Manually authenticate with Google Cloud Platform.

        Note: Authentication is handled automatically by default.
        This method is provided for cases where manual authentication is needed.

        Args:
            credentials_path: Path to service account JSON file (optional)

        Returns:
            bool: True if authentication was successful

        Example:
            GoogleCloud.authenticate("path/to/service-account.json")
        """
        from .googlecloud_managers.gcp_client import GcpClient

        try:
            client = GcpClient()
            if credentials_path:
                client.authenticate(credentials_path=credentials_path)
            else:
                GcpAuthenticationService.authenticate_client(client)
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False

    @staticmethod
    def version() -> str:
        """Get the version of the Google Cloud provider."""
        return "1.0.0"

    @staticmethod
    def help() -> None:
        """Display help information for Google Cloud resources."""
        help_text = """
🌩️  Google Cloud Provider - InfraDSL

Available Resources:
  🖥️  VM          - Single virtual machine
  👥 VmGroup      - Group of identical VMs
  🚀 CloudRun     - Serverless containers
  ☸️  GKE         - Kubernetes clusters
  🔧 LoadBalancer - HTTP/HTTPS load balancing
  💾 Storage      - Cloud Storage buckets
  🗄️  CloudSQL    - Managed databases
  📊 BigQuery     - Analytics data warehouse
  ⚡ CloudFunctions - Serverless functions

Quick Start:
  # Single VM
  vm = GoogleCloud.Vm("my-vm").machine_type("e2-micro").create()

  # VM Group
  group = GoogleCloud.VmGroup("web-servers", 3).machine_type("e2-small").create()

  # Cloud Run (serverless)
  app = GoogleCloud.CloudRun("my-app").container("app", "templates/nodejs").public().create()

  # GKE Cluster
  cluster = GoogleCloud.GKE("my-cluster").location("us-central1").nodes(3).create()

  # Load Balancer
  lb = GoogleCloud.LoadBalancer("web-lb").backend_group(group).create()

Configuration:
  Place your service account JSON file as 'oopscli.json' in your project root.

Documentation:
  Each resource supports .preview() to see what will be created before .create()

Examples: https://github.com/your-org/infradsl/examples/googlecloud/
        """
        print(help_text)


# Convenience function for creating load balancers (maintains backward compatibility)
def create_load_balancer(name: str) -> LoadBalancer:
    """
    Create a new standalone load balancer definition.

    This is a convenience function that's equivalent to GoogleCloud.LoadBalancer(name).

    Args:
        name: Name of the load balancer

    Returns:
        LoadBalancer: A configured load balancer ready for chaining
    """
    return GoogleCloud.LoadBalancer(name)


# Module metadata
__version__ = "1.0.0"
__author__ = "InfraDSL Team"
__description__ = "Rails-like Google Cloud Platform provider for InfraDSL"
