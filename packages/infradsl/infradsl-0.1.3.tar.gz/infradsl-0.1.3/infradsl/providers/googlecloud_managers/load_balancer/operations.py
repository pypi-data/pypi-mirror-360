import time
from google.cloud import compute_v1

class OperationManager:
    """Manages Google Cloud operations with proper waiting and error handling"""
    
    def __init__(self, project_id: str, credentials):
        self.project_id = project_id
        self.credentials = credentials
    
    def wait_for_global_operation(self, operation, timeout: int = 180):
        """Wait for a global operation to complete"""
        try:
            print(f"         ⏳ Waiting for global operation to complete (timeout: {timeout}s)...")
            result = operation.result(timeout=timeout)
            
            if operation.error_code:
                print(f"   ❌ Global operation failed: [Code: {operation.error_code}] {operation.error_message}")
                raise operation.exception() or RuntimeError(operation.error_message)
            
            if operation.warnings:
                print(f"   ⚠️  Warnings during global operation:")
                for warning in operation.warnings:
                    print(f"      - {warning.code}: {warning.message}")
            
            print(f"         ✅ Global operation completed successfully")
            return result

        except Exception as e:
            print(f"         ⏰ Timeout waiting for global operation (after {timeout}s)")
            print(f"         💡 You can check the operation status manually:")
            print(f"         💡 gcloud compute operations describe {operation.name} --global")
            raise e
    
    def wait_for_zone_operation(self, operation, zone: str, timeout: int = 180):
        """Wait for a zone operation to complete"""
        try:
            print(f"         ⏳ Waiting for zone operation to complete (timeout: {timeout}s)...")
            result = operation.result(timeout=timeout)

            if operation.error_code:
                print(f"   ❌ Zone operation failed: [Code: {operation.error_code}] {operation.error_message}")
                raise operation.exception() or RuntimeError(operation.error_message)
            
            if operation.warnings:
                print(f"   ⚠️  Warnings during zone operation:")
                for warning in operation.warnings:
                    print(f"      - {warning.code}: {warning.message}")
            
            print(f"         ✅ Zone operation completed successfully")
            return result

        except Exception as e:
            print(f"         ⏰ Timeout waiting for zone operation (after {timeout}s)")
            print(f"         💡 You can check the operation status manually:")
            print(f"         💡 gcloud compute operations describe {operation.name} --zone={zone}")
            raise e 