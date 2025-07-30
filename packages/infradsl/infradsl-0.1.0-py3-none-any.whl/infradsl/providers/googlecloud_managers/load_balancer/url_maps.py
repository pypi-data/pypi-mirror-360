from google.cloud import compute_v1
from .operations import OperationManager
import time

class UrlMapManager:
    """Manages URL maps for load balancers"""
    
    def __init__(self, project_id: str, credentials, operation_manager: OperationManager = None):
        self.project_id = project_id
        self.credentials = credentials
        self.operation_manager = operation_manager or OperationManager(project_id, credentials)
        self._url_maps_client = None
    
    @property
    def url_maps_client(self):
        """Get the URL maps client (lazy loading)"""
        if not self._url_maps_client:
            self._url_maps_client = compute_v1.UrlMapsClient(credentials=self.credentials)
        return self._url_maps_client
    
    def create_url_map(self, name: str, backend_service: str) -> str:
        """Create a URL map"""
        print(f"   🗺️  Creating URL map: {name}")
        
        # Check if URL map already exists
        existing_map = self._get_url_map(name)
        if existing_map:
            print(f"   ✅ URL map already exists: {name}")
            return name
        
        # Create URL map
        url_map = compute_v1.UrlMap()
        url_map.name = name
        url_map.default_service = f"projects/{self.project_id}/global/backendServices/{backend_service}"
        
        request = compute_v1.InsertUrlMapRequest(
            project=self.project_id,
            url_map_resource=url_map
        )
        
        try:
            operation = self.url_maps_client.insert(request=request)
            print(f"   ⏳ Creating URL map...")
            print(f"   💡 This may take a few minutes. Google Cloud is setting up the URL map...")
            
            # Small delay to allow operation to start
            time.sleep(1)
            
            # Use a longer timeout for URL map creation and provide better feedback
            try:
                self.operation_manager.wait_for_global_operation(operation, timeout=300)  # 5 minutes
                print(f"   ✅ URL map created: {name}")
            except Exception as timeout_error:
                print(f"   ⏳ Operation is taking longer than expected...")
                print(f"   🔍 Checking if URL map was created despite timeout...")
                
                # Check if the URL map was actually created
                try:
                    existing_map = self._get_url_map(name)
                    if existing_map:
                        print(f"   ✅ URL map was created successfully: {name}")
                        print(f"   💡 Google Cloud sometimes takes extra time to report operation completion")
                    else:
                        # If not found, try one more time with extended timeout
                        print(f"   🔄 Retrying operation with extended timeout...")
                        self.operation_manager.wait_for_global_operation(operation, timeout=600)  # 10 minutes
                        print(f"   ✅ URL map created: {name}")
                except Exception as retry_error:
                    print(f"   ❌ Failed to create URL map {name}: {retry_error}")
                    print(f"   💡 This might be due to:")
                    print(f"      - Network connectivity issues")
                    print(f"      - Insufficient permissions")
                    print(f"      - Invalid backend service configuration")
                    print(f"   💡 You can try creating the URL map manually in the Google Cloud Console")
                    return None
            
            return name
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✅ URL map already exists: {name}")
                return name
            print(f"   ❌ Failed to create URL map {name}: {e}")
            print(f"   💡 This might be due to:")
            print(f"      - Network connectivity issues")
            print(f"      - Insufficient permissions")
            print(f"      - Invalid backend service configuration")
            print(f"   💡 You can try creating the URL map manually in the Google Cloud Console")
            return None
    
    def get_url_map(self, name: str):
        """Get a URL map by name"""
        return self._get_url_map(name)
    
    def _get_url_map(self, name: str):
        """Get a URL map by name"""
        try:
            request = compute_v1.GetUrlMapRequest(project=self.project_id, url_map=name)
            return self.url_maps_client.get(request=request)
        except Exception:
            return None
    
    def delete_url_map(self, name: str):
        """Delete a URL map"""
        try:
            request = compute_v1.DeleteUrlMapRequest(project=self.project_id, url_map=name)
            operation = self.url_maps_client.delete(request=request)
            self.operation_manager.wait_for_global_operation(operation)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete URL map {name}: {e}") 