from google.cloud import compute_v1
from .operations import OperationManager
import time

class ForwardingRuleManager:
    """Manages global forwarding rules for load balancers"""
    
    def __init__(self, project_id: str, credentials, operation_manager: OperationManager = None):
        self.project_id = project_id
        self.credentials = credentials
        self.operation_manager = operation_manager or OperationManager(project_id, credentials)
        self._global_forwarding_rules_client = None
    
    @property
    def global_forwarding_rules_client(self):
        """Get the global forwarding rules client (lazy loading)"""
        if not self._global_forwarding_rules_client:
            print(f"   🔐 Creating global forwarding rules client...")
            print(f"      - Project ID: {self.project_id}")
            print(f"      - Credentials type: {type(self.credentials)}")
            try:
                self._global_forwarding_rules_client = compute_v1.GlobalForwardingRulesClient(credentials=self.credentials)
                print(f"      ✅ Global forwarding rules client created successfully")
            except Exception as e:
                print(f"      ❌ Failed to create global forwarding rules client: {e}")
                raise
        return self._global_forwarding_rules_client
    
    def create_forwarding_rule(self, name: str, target_proxy: str, port: int, is_https: bool = False) -> compute_v1.ForwardingRule:
        """Create a global forwarding rule"""
        print(f"   🌐 Creating forwarding rule: {name}")
        
        # Check if forwarding rule already exists
        existing_rule = self._get_forwarding_rule(name)
        if existing_rule:
            print(f"   ✅ Forwarding rule already exists: {name}")
            return existing_rule
        
        # Create global forwarding rule
        forwarding_rule = compute_v1.ForwardingRule()
        forwarding_rule.name = name
        forwarding_rule.I_p_protocol = "TCP"
        forwarding_rule.load_balancing_scheme = "EXTERNAL_MANAGED"
        forwarding_rule.port_range = str(port)
        
        if is_https:
            proxy_type = "targetHttpsProxies"
        else:
            proxy_type = "targetHttpProxies"
            
        forwarding_rule.target = f"projects/{self.project_id}/global/{proxy_type}/{target_proxy}"
        
        request = compute_v1.InsertGlobalForwardingRuleRequest(
            project=self.project_id,
            forwarding_rule_resource=forwarding_rule
        )
        
        try:
            operation = self.global_forwarding_rules_client.insert(request=request)
            print(f"   ⏳ Creating forwarding rule and allocating IP address...")
            print(f"   💡 This may take a few minutes. Google Cloud is setting up the forwarding rule...")
            
            # Small delay to allow operation to start
            time.sleep(1)
            
            # Use a longer timeout for forwarding rule creation and provide better feedback
            try:
                self.operation_manager.wait_for_global_operation(operation, timeout=300)  # 5 minutes
                
                # Get the created forwarding rule to get the IP address
                created_rule = self._get_forwarding_rule(name)
                print(f"   ✅ Forwarding rule created: {name}")
                return created_rule
            except Exception as timeout_error:
                print(f"   ⏳ Operation is taking longer than expected...")
                print(f"   🔍 Checking if forwarding rule was created despite timeout...")
                
                # Check if the forwarding rule was actually created
                try:
                    created_rule = self._get_forwarding_rule(name)
                    if created_rule:
                        print(f"   ✅ Forwarding rule was created successfully: {name}")
                        print(f"   💡 Google Cloud sometimes takes extra time to report operation completion")
                        return created_rule
                    else:
                        # If not found, try one more time with extended timeout
                        print(f"   🔄 Retrying operation with extended timeout...")
                        self.operation_manager.wait_for_global_operation(operation, timeout=600)  # 10 minutes
                        
                        # Get the created forwarding rule to get the IP address
                        created_rule = self._get_forwarding_rule(name)
                        print(f"   ✅ Forwarding rule created: {name}")
                        return created_rule
                except Exception as retry_error:
                    print(f"   ❌ Failed to create forwarding rule {name}: {retry_error}")
                    print(f"   💡 This might be due to:")
                    print(f"      - Network connectivity issues")
                    print(f"      - Insufficient permissions")
                    print(f"      - Invalid target proxy configuration")
                    print(f"   💡 You can try creating the forwarding rule manually in the Google Cloud Console")
                    return None
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✅ Forwarding rule already exists: {name}")
                return self._get_forwarding_rule(name)
            print(f"   ❌ Failed to create forwarding rule {name}: {e}")
            print(f"   💡 This might be due to:")
            print(f"      - Network connectivity issues")
            print(f"      - Insufficient permissions")
            print(f"      - Invalid target proxy configuration")
            print(f"   💡 You can try creating the forwarding rule manually in the Google Cloud Console")
            return None
    
    def get_forwarding_rule(self, name: str):
        """Get a forwarding rule by name"""
        return self._get_forwarding_rule(name)
    
    def _get_forwarding_rule(self, name: str):
        """Get a forwarding rule by name"""
        try:
            request = compute_v1.GetGlobalForwardingRuleRequest(project=self.project_id, forwarding_rule=name)
            return self.global_forwarding_rules_client.get(request=request)
        except Exception:
            return None
    
    def delete_forwarding_rule(self, name: str):
        """Delete a forwarding rule"""
        try:
            request = compute_v1.DeleteGlobalForwardingRuleRequest(project=self.project_id, forwarding_rule=name)
            operation = self.global_forwarding_rules_client.delete(request=request)
            self.operation_manager.wait_for_global_operation(operation)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete forwarding rule {name}: {e}") 