"""
Error handling and user experience improvements for Google Cloud Load Balancer operations.
This module provides intelligent error handling, user-friendly messages, and actionable solutions.
"""

import time
from typing import Dict, List, Optional, Tuple
from google.api_core import exceptions as google_exceptions


class LoadBalancerErrorHandler:
    """Handles errors gracefully and provides user-friendly solutions"""
    
    # Common error patterns and their solutions
    ERROR_SOLUTIONS = {
        "permission": {
            "patterns": ["permission", "forbidden", "access denied", "not authorized"],
            "solutions": [
                "Ensure your service account has the following roles:",
                "  • Compute Load Balancer Admin",
                "  • Compute Instance Admin",
                "  • Compute Network Admin",
                "  • Service Account User",
                "Run: gcloud projects add-iam-policy-binding PROJECT_ID --member='serviceAccount:YOUR_SA@PROJECT_ID.iam.gserviceaccount.com' --role='roles/compute.loadBalancerAdmin'"
            ]
        },
        "quota": {
            "patterns": ["quota", "limit exceeded", "resource exhausted"],
            "solutions": [
                "You've reached your Google Cloud quota limits.",
                "Solutions:",
                "  • Request quota increase: https://console.cloud.google.com/iam-admin/quotas",
                "  • Delete unused resources",
                "  • Use a different project"
            ]
        },
        "network": {
            "patterns": ["network", "subnet", "vpc", "connectivity"],
            "solutions": [
                "Network configuration issue detected.",
                "Solutions:",
                "  • Ensure VPC exists and is properly configured",
                "  • Check firewall rules allow required traffic",
                "  • Verify subnets are in the correct regions"
            ]
        },
        "resource_not_found": {
            "patterns": ["not found", "does not exist", "resource not found"],
            "solutions": [
                "Resource not found. This usually means:",
                "  • The resource is still being created (wait a few minutes)",
                "  • The resource was created in a different project/region",
                "  • There was a naming conflict",
                "💡 Try running the command again in a few minutes"
            ]
        },
        "timeout": {
            "patterns": ["timeout", "deadline exceeded", "operation timed out"],
            "solutions": [
                "Operation timed out. This is common with Google Cloud.",
                "Solutions:",
                "  • The resource may have been created successfully despite the timeout",
                "  • Check the Google Cloud Console to verify",
                "  • Try the operation again with a longer timeout",
                "  • Google Cloud operations can take 5-10 minutes"
            ]
        },
        "already_exists": {
            "patterns": ["already exists", "duplicate", "conflict"],
            "solutions": [
                "Resource already exists. This is usually not a problem.",
                "The system will use the existing resource.",
                "💡 If you want to recreate, delete the existing resource first"
            ]
        },
        "invalid_config": {
            "patterns": ["invalid", "malformed", "bad request"],
            "solutions": [
                "Invalid configuration detected.",
                "Check:",
                "  • Resource names (only lowercase letters, numbers, hyphens)",
                "  • Zone/region specifications",
                "  • Port numbers (1-65535)",
                "  • SSL certificate format"
            ]
        }
    }
    
    @classmethod
    def analyze_error(cls, error: Exception, context: str = "") -> Dict[str, any]:
        """Analyze an error and provide user-friendly solutions"""
        error_str = str(error).lower()
        
        # Determine error type
        error_type = "unknown"
        for err_type, info in cls.ERROR_SOLUTIONS.items():
            if any(pattern in error_str for pattern in info["patterns"]):
                error_type = err_type
                break
        
        # Get solutions
        solutions = cls.ERROR_SOLUTIONS.get(error_type, {}).get("solutions", [
            "An unexpected error occurred.",
            "Check the error message above for details.",
            "💡 Try running the command again or check your configuration."
        ])
        
        # Additional context-specific solutions
        if context:
            context_solutions = cls._get_context_specific_solutions(context, error_str)
            solutions.extend(context_solutions)
        
        return {
            "type": error_type,
            "message": str(error),
            "solutions": solutions,
            "is_recoverable": error_type in ["timeout", "already_exists", "resource_not_found"],
            "should_retry": error_type in ["timeout", "resource_not_found"]
        }
    
    @classmethod
    def _get_context_specific_solutions(cls, context: str, error_str: str) -> List[str]:
        """Get context-specific solutions based on the operation being performed"""
        solutions = []
        
        if "backend service" in context.lower():
            solutions.extend([
                "Backend service specific solutions:",
                "  • Ensure instance groups exist and are in the correct zones",
                "  • Check that VMs are running and accessible",
                "  • Verify health check configuration"
            ])
        
        if "forwarding rule" in context.lower():
            solutions.extend([
                "Forwarding rule specific solutions:",
                "  • Check if IP address is already in use",
                "  • Verify target proxy exists",
                "  • Ensure port is not already allocated"
            ])
        
        if "instance group" in context.lower():
            solutions.extend([
                "Instance group specific solutions:",
                "  • Ensure VMs exist and are in the correct zone",
                "  • Check VM status (should be RUNNING)",
                "  • Verify VM network configuration"
            ])
        
        return solutions
    
    @classmethod
    def format_error_message(cls, error_analysis: Dict[str, any]) -> str:
        """Format error analysis into a user-friendly message"""
        lines = []
        
        # Error type indicator
        error_type = error_analysis["type"]
        if error_type == "timeout":
            lines.append("⏰ Timeout Error")
        elif error_type == "permission":
            lines.append("🔒 Permission Error")
        elif error_type == "quota":
            lines.append("📊 Quota Error")
        elif error_type == "network":
            lines.append("🌐 Network Error")
        elif error_type == "resource_not_found":
            lines.append("🔍 Resource Not Found")
        elif error_type == "already_exists":
            lines.append("✅ Resource Already Exists")
        elif error_type == "invalid_config":
            lines.append("⚠️  Configuration Error")
        else:
            lines.append("❌ Error")
        
        lines.append("")
        
        # Solutions
        for solution in error_analysis["solutions"]:
            lines.append(solution)
        
        # Recovery hints
        if error_analysis["is_recoverable"]:
            lines.append("")
            lines.append("💡 This error is usually recoverable. Try:")
            if error_analysis["should_retry"]:
                lines.append("  • Running the command again in a few minutes")
            lines.append("  • Checking the Google Cloud Console for resource status")
            lines.append("  • Verifying your configuration")
        
        return "\n".join(lines)
    
    @classmethod
    def should_retry_operation(cls, error: Exception, attempt: int, max_attempts: int = 3) -> bool:
        """Determine if an operation should be retried"""
        if attempt >= max_attempts:
            return False
        
        error_analysis = cls.analyze_error(error)
        return error_analysis["should_retry"]
    
    @classmethod
    def get_retry_delay(cls, attempt: int, base_delay: float = 5.0) -> float:
        """Calculate retry delay with exponential backoff"""
        return min(base_delay * (2 ** attempt), 60.0)  # Max 60 seconds


class ProgressTracker:
    """Tracks and reports progress of long-running operations"""
    
    def __init__(self, operation_name: str, total_steps: int = 1):
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.step_times = []
    
    def start_step(self, step_name: str):
        """Start a new step"""
        self.current_step += 1
        step_start = time.time()
        self.step_times.append((step_name, step_start))
        
        elapsed = int(step_start - self.start_time)
        print(f"   🔄 Step {self.current_step}/{self.total_steps}: {step_name} (elapsed: {elapsed}s)")
    
    def complete_step(self, step_name: str, success: bool = True):
        """Complete a step"""
        if self.step_times and self.step_times[-1][0] == step_name:
            step_start = self.step_times[-1][1]
            step_duration = int(time.time() - step_start)
            
            if success:
                print(f"   ✅ Completed: {step_name} (took: {step_duration}s)")
            else:
                print(f"   ❌ Failed: {step_name} (took: {step_duration}s)")
    
    def get_progress_summary(self) -> str:
        """Get a progress summary"""
        elapsed = int(time.time() - self.start_time)
        return f"Operation '{self.operation_name}' completed in {elapsed} seconds"


class UserExperienceEnhancer:
    """Enhances user experience with helpful tips and guidance"""
    
    @staticmethod
    def show_operation_tips(operation_type: str):
        """Show helpful tips for specific operations"""
        tips = {
            "load_balancer_creation": [
                "💡 Load balancer creation typically takes 5-10 minutes",
                "💡 Google Cloud operations are eventually consistent",
                "💡 You can monitor progress in the Google Cloud Console",
                "💡 Resources may appear in the console before the CLI reports completion"
            ],
            "backend_service": [
                "💡 Backend services require healthy instance groups",
                "💡 Health checks ensure only healthy backends receive traffic",
                "💡 You can add/remove backends without recreating the load balancer"
            ],
            "instance_groups": [
                "💡 Instance groups automatically distribute traffic",
                "💡 VMs must be in the same zone as the instance group",
                "💡 Instance groups can be managed or unmanaged"
            ]
        }
        
        if operation_type in tips:
            print("\n💡 Tips:")
            for tip in tips[operation_type]:
                print(f"   {tip}")
    
    @staticmethod
    def show_next_steps(resource_type: str, resource_name: str):
        """Show next steps after resource creation"""
        next_steps = {
            "load_balancer": [
                f"🌐 Your load balancer '{resource_name}' is ready!",
                "📋 Next steps:",
                "   • Test the load balancer with: curl http://IP_ADDRESS",
                "   • Monitor health in Google Cloud Console",
                "   • Configure DNS to point to the load balancer IP",
                "   • Set up SSL certificates if needed"
            ],
            "backend_service": [
                f"🔧 Backend service '{resource_name}' created",
                "📋 Next steps:",
                "   • Add more backends if needed",
                "   • Configure health checks",
                "   • Monitor backend health"
            ]
        }
        
        if resource_type in next_steps:
            print("\n" + "\n".join(next_steps[resource_type]))
    
    @staticmethod
    def show_troubleshooting_guide():
        """Show general troubleshooting guide"""
        print("\n🔧 Troubleshooting Guide:")
        print("   • Check Google Cloud Console for resource status")
        print("   • Verify service account permissions")
        print("   • Ensure VMs are running and accessible")
        print("   • Check firewall rules and network configuration")
        print("   • Review operation logs in Google Cloud Console")
        print("   • Try the operation again in a few minutes") 