import time
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel
from google.cloud import compute_v1
from .gcp_client import GcpClient

class VmConfig(BaseModel):
    name: str
    machine_type: str = "e2-micro"
    zone: str = "us-central1-a"
    image_family: str = "debian-11"
    image_project: str = "debian-cloud"
    network: str = "default"
    subnetwork: str = "default"
    disk_size_gb: int = 10
    tags: Optional[list] = None
    metadata: Optional[Dict[str, str]] = None
    startup_script: Optional[str] = None
    service_account_email: Optional[str] = None
    scopes: Optional[list] = None
    health_check: Optional[Dict[str, Any]] = None

class VmManager:
    """Manages Google Cloud Compute Engine VM operations"""

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._compute_client = None
        self._project_id = None
        self._images_client = None
        self._zone_ops_client = None

    @property
    def compute_client(self):
        """Get the compute client (lazy loading after authentication)"""
        if not self._compute_client:
            self._compute_client = self.gcp_client.client
        return self._compute_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    @property
    def images_client(self):
        """Get the images client (lazy loading after authentication)"""
        if not self._images_client:
            self._images_client = compute_v1.ImagesClient(credentials=self.gcp_client.credentials)
        return self._images_client

    @property
    def zone_ops_client(self):
        """Get the zone operations client (lazy loading after authentication)"""
        if not self._zone_ops_client:
            self._zone_ops_client = compute_v1.ZoneOperationsClient(credentials=self.gcp_client.credentials)
        return self._zone_ops_client

    def create_vm(self, config: VmConfig) -> Dict[str, Any]:
        if not self.gcp_client.check_authenticated():
            raise ValueError("Authentication not set. Use .authenticate() first.")
        try:
            existing_instance = self._get_instance(config.name, config.zone)
            if existing_instance:
                print(f"🔄 Found existing VM instance: {config.name}")
                return {
                    'name': existing_instance.name,
                    'id': existing_instance.id,
                    'ip_address': existing_instance.network_interfaces[0].access_configs[0].nat_i_p,
                    'status': existing_instance.status,
                    'zone': config.zone,
                    'machine_type': config.machine_type
                }

            print(f"🚀 Creating VM instance: {config.name}")
            image_request = compute_v1.GetFromFamilyImageRequest(
                project=config.image_project,
                family=config.image_family
            )
            image_response = self.images_client.get_from_family(request=image_request)
            instance = compute_v1.Instance()
            instance.name = config.name
            instance.machine_type = f"zones/{config.zone}/machineTypes/{config.machine_type}"
            disk = compute_v1.AttachedDisk()
            disk.auto_delete = True
            disk.boot = True
            disk.device_name = config.name
            disk.disk_size_gb = config.disk_size_gb
            disk.type_ = f"zones/{config.zone}/diskTypes/pd-standard"
            disk.initialize_params = compute_v1.AttachedDiskInitializeParams()
            disk.initialize_params.source_image = image_response.self_link
            instance.disks = [disk]
            network_interface = compute_v1.NetworkInterface()
            network_interface.name = "nic0"
            network_interface.network = f"projects/{self.project_id}/global/networks/{config.network}"
            network_interface.subnetwork = f"regions/{config.zone.split('-')[0]}-{config.zone.split('-')[1]}/subnetworks/{config.subnetwork}"
            access_config = compute_v1.AccessConfig()
            access_config.name = "External NAT"
            access_config.type_ = "ONE_TO_ONE_NAT"
            network_interface.access_configs = [access_config]
            instance.network_interfaces = [network_interface]
            if config.tags:
                instance.tags = compute_v1.Tags()
                instance.tags.items = config.tags
            if config.metadata or config.startup_script:
                instance.metadata = compute_v1.Metadata()
                metadata_items = []
                if config.metadata:
                    for key, value in config.metadata.items():
                        metadata_items.append(compute_v1.Items(key=key, value=value))
                if config.startup_script:
                    metadata_items.append(compute_v1.Items(key="startup-script", value=config.startup_script))
                instance.metadata.items = metadata_items
            if config.service_account_email:
                instance.service_accounts = [compute_v1.ServiceAccount(
                    email=config.service_account_email,
                    scopes=config.scopes or ["https://www.googleapis.com/auth/cloud-platform"]
                )]
            request = compute_v1.InsertInstanceRequest(
                project=self.project_id,
                zone=config.zone,
                instance_resource=instance
            )

            try:
                operation = self.compute_client.insert(request=request)
                print(f"✅ VM creation initiated: {config.name}")
                print(f"   Operation: {operation.name}")
                print(f"   Note: VM provisioning may take a few minutes to complete")

                # Try to get the instance immediately (it might already exist)
                time.sleep(2)  # Brief wait
                created_instance = self._get_instance(config.name, config.zone)
                if created_instance:
                    external_ip = created_instance.network_interfaces[0].access_configs[0].nat_i_p
                    print(f"✅ VM instance ready: {config.name}")
                    print(f"   IP Address: {external_ip}")
                    print(f"   Zone: {config.zone}")
                    return {
                        'name': created_instance.name,
                        'id': created_instance.id,
                        'ip_address': external_ip,
                        'status': created_instance.status,
                        'zone': config.zone,
                        'machine_type': config.machine_type
                    }
                else:
                    # If not immediately available, return placeholder info
                    print(f"⏳ VM creation in progress...")
                    print(f"   You can check status in Google Cloud Console")
                    print(f"   Or run: gcloud compute instances describe {config.name} --zone={config.zone}")
                    return {
                        'name': config.name,
                        'id': "creating",
                        'ip_address': "pending",
                        'status': "PROVISIONING",
                        'zone': config.zone,
                        'machine_type': config.machine_type
                    }
            except Exception as e:
                # If the insert fails (e.g., VM already exists), try to get the existing VM
                print(f"⚠️  VM creation failed, checking for existing VM: {e}")
                existing_instance = self._get_instance(config.name, config.zone)
                if existing_instance:
                    print(f"🔄 Found existing VM instance: {config.name}")
                    return {
                        'name': existing_instance.name,
                        'id': existing_instance.id,
                        'ip_address': existing_instance.network_interfaces[0].access_configs[0].nat_i_p,
                        'status': existing_instance.status,
                        'zone': config.zone,
                        'machine_type': config.machine_type
                    }
                else:
                    raise Exception(f"Failed to create VM instance and no existing VM found: {str(e)}")

        except Exception as e:
            raise Exception(f"Failed to create VM instance: {str(e)}")

    def get_vm_info(self, instance_name: str, zone: str) -> Optional[Dict[str, Any]]:
        """Get VM information by name and zone"""
        try:
            instance = self._get_instance(instance_name, zone)
            if not instance:
                return None

            return {
                'id': instance.id,
                'name': instance.name,
                'ip': instance.network_interfaces[0].access_configs[0].nat_i_p,
                'status': instance.status,
                'zone': zone,
                'machine_type': instance.machine_type.split('/')[-1]
            }
        except Exception as e:
            return None  # Return None instead of raising exception for discovery purposes

    def delete_vm(self, instance_name: str, zone: str) -> bool:
        try:
            instance = self._get_instance(instance_name, zone)
            if not instance:
                print(f"✅ No VM instance found with name: {instance_name}")
                return True

            print(f"🗑️  Deleting VM instance: {instance_name}")

            request = compute_v1.DeleteInstanceRequest(
                project=self.project_id,
                zone=zone,
                instance=instance_name
            )

            operation = self.compute_client.delete(request=request)
            print(f"✅ VM deletion initiated: {instance_name}")
            print(f"   Operation: {operation.name}")
            print(f"   Note: VM deletion may take a few minutes to complete")

            return True

        except Exception as e:
            print(f"⚠️  Warning: Failed to delete VM instance: {e}")
            return False

    def _wait_for_instance_deleted(self, instance_name: str, zone: str, timeout: int = 120) -> bool:
        """Wait for instance to be fully deleted"""
        print(f"⏳ Waiting for instance to be deleted (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                instance = self._get_instance(instance_name, zone)
                if not instance:
                    print(f"✅ Instance successfully deleted!")
                    return True

                elapsed = int(time.time() - start_time)
                print(f"   Instance still exists, status: {instance.status} (elapsed: {elapsed}s)")
                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                # If we get a 404 error, the instance is deleted
                if "404" in str(e) or "not found" in str(e).lower():
                    print(f"✅ Instance successfully deleted!")
                    return True
                else:
                    print(f"   Error checking instance status: {e}")
                    time.sleep(5)

        print(f"⚠️  Timeout waiting for instance deletion after {timeout} seconds")
        return False

    def _get_instance(self, instance_name: str, zone: str) -> Optional[compute_v1.Instance]:
        """Get instance by name and zone"""
        try:
            request = compute_v1.GetInstanceRequest(
                project=self.project_id,
                zone=zone,
                instance=instance_name
            )
            return self.compute_client.get(request=request)
        except Exception:
            return None

    def _wait_for_operation(self, operation, zone: str, timeout: int = 180):
        """Wait for a compute operation to complete"""
        try:
            print(f"⏳ Waiting for operation to complete (timeout: {timeout}s)...")
            result = operation.result(timeout=timeout)

            if operation.error_code:
                print(f"   ❌ Operation failed: [Code: {operation.error_code}] {operation.error_message}")
                raise operation.exception() or RuntimeError(operation.error_message)

            if operation.warnings:
                print(f"   ⚠️  Warnings during operation:")
                for warning in operation.warnings:
                    print(f"      - {warning.code}: {warning.message}")

            print(f"         ✅ Operation completed successfully")
            return result

        except Exception as e:
            print(f"         ⏰ Timeout waiting for operation (after {timeout}s)")
            print(f"         💡 You can check the operation status manually:")
            print(f"         💡 gcloud compute operations describe {operation.name} --zone={zone}")
            raise e

    def validate_vm_config(self, config: VmConfig) -> bool:
        """Validate the VM configuration"""
        if not config.name:
            raise ValueError("Instance name is required.")
        if not config.zone:
            raise ValueError("Zone must be specified")
        return True

    def _wait_for_instance_ready(self, instance_name: str, zone: str, timeout: int = 300) -> Optional[compute_v1.Instance]:
        """Wait for instance to be in RUNNING state"""
        print(f"⏳ Waiting for instance to be ready (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                instance = self._get_instance(instance_name, zone)
                if instance and instance.status == 'RUNNING':
                    print(f"✅ Instance is RUNNING!")
                    return instance

                elapsed = int(time.time() - start_time)
                print(f"   Instance not ready yet, status: {instance.status if instance else 'N/A'} (elapsed: {elapsed}s)")
                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"   Error checking instance status: {e}")
                time.sleep(5)

        print(f"⚠️  Timeout waiting for instance to be ready after {timeout} seconds")
        return None
