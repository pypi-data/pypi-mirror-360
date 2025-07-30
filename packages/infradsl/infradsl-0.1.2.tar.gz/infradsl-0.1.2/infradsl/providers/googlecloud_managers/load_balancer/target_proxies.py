from google.cloud import compute_v1
from .operations import OperationManager
import time

class TargetProxyManager:
    """Manages target proxies for load balancers"""
    
    def __init__(self, project_id: str, credentials, operation_manager: OperationManager = None):
        self.project_id = project_id
        self.credentials = credentials
        self.operation_manager = operation_manager or OperationManager(project_id, credentials)
        self._target_http_proxies_client = None
        self._target_https_proxies_client = None
    
    @property
    def target_http_proxies_client(self):
        """Get the target HTTP proxies client (lazy loading)"""
        if not self._target_http_proxies_client:
            self._target_http_proxies_client = compute_v1.TargetHttpProxiesClient(credentials=self.credentials)
        return self._target_http_proxies_client
    
    @property
    def target_https_proxies_client(self):
        """Get the target HTTPS proxies client (lazy loading)"""
        if not self._target_https_proxies_client:
            self._target_https_proxies_client = compute_v1.TargetHttpsProxiesClient(credentials=self.credentials)
        return self._target_https_proxies_client
    
    def create_http_proxy(self, name: str, url_map: str) -> str:
        """Create an HTTP target proxy"""
        print(f"   🔗 Creating HTTP proxy: {name}")
        
        # Check if proxy already exists
        existing_proxy = self._get_http_proxy(name)
        if existing_proxy:
            print(f"   ✅ HTTP proxy already exists: {name}")
            return name
        
        # Create HTTP target proxy
        target_proxy = compute_v1.TargetHttpProxy()
        target_proxy.name = name
        target_proxy.url_map = f"projects/{self.project_id}/global/urlMaps/{url_map}"
        
        request = compute_v1.InsertTargetHttpProxyRequest(
            project=self.project_id,
            target_http_proxy_resource=target_proxy
        )
        
        try:
            operation = self.target_http_proxies_client.insert(request=request)
            print(f"   ⏳ Creating HTTP proxy...")
            print(f"   💡 This may take a few minutes. Google Cloud is setting up the HTTP proxy...")
            
            # Small delay to allow operation to start
            time.sleep(1)
            
            # Use a longer timeout for proxy creation and provide better feedback
            try:
                self.operation_manager.wait_for_global_operation(operation, timeout=300)  # 5 minutes
                print(f"   ✅ HTTP proxy created: {name}")
            except Exception as timeout_error:
                print(f"   ⏳ Operation is taking longer than expected...")
                print(f"   🔍 Checking if HTTP proxy was created despite timeout...")
                
                # Check if the proxy was actually created
                try:
                    existing_proxy = self._get_http_proxy(name)
                    if existing_proxy:
                        print(f"   ✅ HTTP proxy was created successfully: {name}")
                        print(f"   💡 Google Cloud sometimes takes extra time to report operation completion")
                    else:
                        # If not found, try one more time with extended timeout
                        print(f"   🔄 Retrying operation with extended timeout...")
                        self.operation_manager.wait_for_global_operation(operation, timeout=600)  # 10 minutes
                        print(f"   ✅ HTTP proxy created: {name}")
                except Exception as retry_error:
                    print(f"   ❌ Failed to create HTTP proxy {name}: {retry_error}")
                    print(f"   💡 This might be due to:")
                    print(f"      - Network connectivity issues")
                    print(f"      - Insufficient permissions")
                    print(f"      - Invalid URL map configuration")
                    print(f"   💡 You can try creating the HTTP proxy manually in the Google Cloud Console")
                    return None
            
            return name
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✅ HTTP proxy already exists: {name}")
                return name
            print(f"   ❌ Failed to create HTTP proxy {name}: {e}")
            print(f"   💡 This might be due to:")
            print(f"      - Network connectivity issues")
            print(f"      - Insufficient permissions")
            print(f"      - Invalid URL map configuration")
            print(f"   💡 You can try creating the HTTP proxy manually in the Google Cloud Console")
            return None
    
    def create_https_proxy(self, name: str, url_map: str, ssl_certificate: str) -> str:
        """Create an HTTPS target proxy"""
        print(f"   🔗 Creating HTTPS proxy: {name}")
        
        # Check if proxy already exists
        existing_proxy = self._get_https_proxy(name)
        if existing_proxy:
            print(f"   ✅ HTTPS proxy already exists: {name}")
            return name
        
        # Create HTTPS target proxy
        target_proxy = compute_v1.TargetHttpsProxy()
        target_proxy.name = name
        target_proxy.url_map = f"projects/{self.project_id}/global/urlMaps/{url_map}"
        target_proxy.ssl_certificates = [ssl_certificate]
        
        request = compute_v1.InsertTargetHttpsProxyRequest(
            project=self.project_id,
            target_https_proxy_resource=target_proxy
        )
        
        try:
            operation = self.target_https_proxies_client.insert(request=request)
            print(f"   ⏳ Creating HTTPS proxy...")
            print(f"   💡 This may take a few minutes. Google Cloud is setting up the HTTPS proxy...")
            
            # Small delay to allow operation to start
            time.sleep(1)
            
            # Use a longer timeout for proxy creation and provide better feedback
            try:
                self.operation_manager.wait_for_global_operation(operation, timeout=300)  # 5 minutes
                print(f"   ✅ HTTPS proxy created: {name}")
            except Exception as timeout_error:
                print(f"   ⏳ Operation is taking longer than expected...")
                print(f"   🔍 Checking if HTTPS proxy was created despite timeout...")
                
                # Check if the proxy was actually created
                try:
                    existing_proxy = self._get_https_proxy(name)
                    if existing_proxy:
                        print(f"   ✅ HTTPS proxy was created successfully: {name}")
                        print(f"   💡 Google Cloud sometimes takes extra time to report operation completion")
                    else:
                        # If not found, try one more time with extended timeout
                        print(f"   🔄 Retrying operation with extended timeout...")
                        self.operation_manager.wait_for_global_operation(operation, timeout=600)  # 10 minutes
                        print(f"   ✅ HTTPS proxy created: {name}")
                except Exception as retry_error:
                    print(f"   ❌ Failed to create HTTPS proxy {name}: {retry_error}")
                    print(f"   💡 This might be due to:")
                    print(f"      - Network connectivity issues")
                    print(f"      - Insufficient permissions")
                    print(f"      - Invalid URL map or SSL certificate configuration")
                    print(f"   💡 You can try creating the HTTPS proxy manually in the Google Cloud Console")
                    return None
            
            return name
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✅ HTTPS proxy already exists: {name}")
                return name
            print(f"   ❌ Failed to create HTTPS proxy {name}: {e}")
            print(f"   💡 This might be due to:")
            print(f"      - Network connectivity issues")
            print(f"      - Insufficient permissions")
            print(f"      - Invalid URL map or SSL certificate configuration")
            print(f"   💡 You can try creating the HTTPS proxy manually in the Google Cloud Console")
            return None
    
    def get_http_proxy(self, name: str):
        """Get an HTTP proxy by name"""
        return self._get_http_proxy(name)
    
    def get_https_proxy(self, name: str):
        """Get an HTTPS proxy by name"""
        return self._get_https_proxy(name)
    
    def _get_http_proxy(self, name: str):
        """Get an HTTP proxy by name"""
        try:
            request = compute_v1.GetTargetHttpProxyRequest(project=self.project_id, target_http_proxy=name)
            return self.target_http_proxies_client.get(request=request)
        except Exception:
            return None
    
    def _get_https_proxy(self, name: str):
        """Get an HTTPS proxy by name"""
        try:
            request = compute_v1.GetTargetHttpsProxyRequest(project=self.project_id, target_https_proxy=name)
            return self.target_https_proxies_client.get(request=request)
        except Exception:
            return None
    
    def delete_http_proxy(self, name: str):
        """Delete an HTTP proxy"""
        try:
            request = compute_v1.DeleteTargetHttpProxyRequest(project=self.project_id, target_http_proxy=name)
            operation = self.target_http_proxies_client.delete(request=request)
            self.operation_manager.wait_for_global_operation(operation)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete HTTP proxy {name}: {e}")
    
    def delete_https_proxy(self, name: str):
        """Delete an HTTPS proxy"""
        try:
            request = compute_v1.DeleteTargetHttpsProxyRequest(project=self.project_id, target_https_proxy=name)
            operation = self.target_https_proxies_client.delete(request=request)
            self.operation_manager.wait_for_global_operation(operation)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete HTTPS proxy {name}: {e}") 