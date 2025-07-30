"""
Configuration validation for Google Cloud Load Balancer operations.
This module validates configurations before resource creation to prevent errors.
"""

import re
from typing import List, Dict, Any, Tuple
from .config import LoadBalancerConfig, BackendConfig


class LoadBalancerValidator:
    """Validates load balancer configurations before creation"""
    
    # Validation rules
    NAME_PATTERN = re.compile(r'^[a-z]([a-z0-9-]*[a-z0-9])?$')
    PORT_RANGE = (1, 65535)
    MAX_BACKENDS = 10
    MAX_VMS_PER_BACKEND = 50
    
    @classmethod
    def validate_load_balancer_config(cls, config: LoadBalancerConfig) -> Tuple[bool, List[str]]:
        """Validate a complete load balancer configuration"""
        errors = []
        
        # Validate basic configuration
        name_errors = cls._validate_name(config.name, "load balancer")
        errors.extend(name_errors)
        
        # Validate port configuration
        port_errors = cls._validate_port(config.port)
        errors.extend(port_errors)
        
        # Validate SSL configuration if present
        if config.ssl_certificate:
            ssl_errors = cls._validate_ssl_config(config)
            errors.extend(ssl_errors)
        
        # Validate backends
        backend_errors = cls._validate_backends(config.backends)
        errors.extend(backend_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_name(cls, name: str, resource_type: str) -> List[str]:
        """Validate resource names"""
        errors = []
        
        if not name:
            errors.append(f"{resource_type.capitalize()} name is required")
            return errors
        
        if len(name) > 63:
            errors.append(f"{resource_type.capitalize()} name must be 63 characters or less")
        
        if not cls.NAME_PATTERN.match(name):
            errors.append(f"{resource_type.capitalize()} name must contain only lowercase letters, numbers, and hyphens, and must start with a letter")
        
        if name.startswith('goog') or name.startswith('google'):
            errors.append(f"{resource_type.capitalize()} name cannot start with 'goog' or 'google'")
        
        return errors
    
    @classmethod
    def _validate_port(cls, port: int) -> List[str]:
        """Validate port numbers"""
        errors = []
        
        if not isinstance(port, int):
            errors.append("Port must be an integer")
        elif port < cls.PORT_RANGE[0] or port > cls.PORT_RANGE[1]:
            errors.append(f"Port must be between {cls.PORT_RANGE[0]} and {cls.PORT_RANGE[1]}")
        
        return errors
    
    @classmethod
    def _validate_ssl_config(cls, config: LoadBalancerConfig) -> List[str]:
        """Validate SSL configuration"""
        errors = []
        
        if not config.ssl_certificate:
            errors.append("SSL certificate is required when SSL port is specified")
            return errors
        
        # Validate SSL certificate name
        cert_errors = cls._validate_name(config.ssl_certificate, "SSL certificate")
        errors.extend(cert_errors)
        
        # Validate SSL port
        if config.ssl_port:
            ssl_port_errors = cls._validate_port(config.ssl_port)
            errors.extend(ssl_port_errors)
            
            if config.ssl_port == config.port:
                errors.append("SSL port cannot be the same as HTTP port")
        
        return errors
    
    @classmethod
    def _validate_backends(cls, backends: List[BackendConfig]) -> List[str]:
        """Validate backend configurations"""
        errors = []
        
        if not backends:
            errors.append("At least one backend is required")
            return errors
        
        if len(backends) > cls.MAX_BACKENDS:
            errors.append(f"Maximum {cls.MAX_BACKENDS} backends allowed")
        
        # Validate each backend
        backend_names = set()
        for i, backend in enumerate(backends):
            backend_errors = cls._validate_backend(backend, i + 1)
            errors.extend(backend_errors)
            
            # Check for duplicate names (use vm_name)
            if backend.vm_name in backend_names:
                errors.append(f"Duplicate backend name: {backend.vm_name}")
            else:
                backend_names.add(backend.vm_name)
        
        return errors
    
    @classmethod
    def _validate_backend(cls, backend: BackendConfig, index: int) -> List[str]:
        """Validate individual backend configuration"""
        errors = []
        
        # Validate backend name (use vm_name as the backend name)
        name_errors = cls._validate_name(backend.vm_name, f"backend {index}")
        errors.extend(name_errors)
        
        # Validate zone
        if not backend.zone:
            errors.append(f"Backend {index} zone is required")
        elif not cls._is_valid_zone(backend.zone):
            errors.append(f"Backend {index} zone '{backend.zone}' is not a valid Google Cloud zone")
        
        # Validate port
        if backend.port:
            port_errors = cls._validate_port(backend.port)
            errors.extend([f"Backend {index}: {error}" for error in port_errors])
        
        # Validate VMs if present (for the new interface)
        if hasattr(backend, 'vms') and backend.vms:
            vm_errors = cls._validate_vms(backend.vms, index)
            errors.extend(vm_errors)
        
        return errors
    
    @classmethod
    def _validate_vms(cls, vms: List[str], backend_index: int) -> List[str]:
        """Validate VM configurations"""
        errors = []
        
        if len(vms) > cls.MAX_VMS_PER_BACKEND:
            errors.append(f"Backend {backend_index}: Maximum {cls.MAX_VMS_PER_BACKEND} VMs per backend")
        
        # Validate VM names
        vm_names = set()
        for i, vm in enumerate(vms):
            if not vm:
                errors.append(f"Backend {backend_index}: VM {i + 1} name is required")
            else:
                vm_name_errors = cls._validate_name(vm, f"VM {i + 1} in backend {backend_index}")
                errors.extend(vm_name_errors)
                
                if vm in vm_names:
                    errors.append(f"Backend {backend_index}: Duplicate VM name: {vm}")
                else:
                    vm_names.add(vm)
        
        return errors
    
    @classmethod
    def _is_valid_zone(cls, zone: str) -> bool:
        """Check if a zone is valid (basic validation)"""
        if not zone:
            return False
        
        # Basic zone pattern validation
        zone_pattern = re.compile(r'^[a-z]+-[a-z]+[0-9]+-[a-z]$')
        return bool(zone_pattern.match(zone))
    
    @classmethod
    def format_validation_errors(cls, errors: List[str]) -> str:
        """Format validation errors into a user-friendly message"""
        if not errors:
            return "✅ Configuration is valid"
        
        lines = ["❌ Configuration validation failed:"]
        lines.append("")
        
        for i, error in enumerate(errors, 1):
            lines.append(f"   {i}. {error}")
        
        lines.append("")
        lines.append("💡 Please fix these issues and try again.")
        
        return "\n".join(lines)


class ResourceAvailabilityChecker:
    """Checks resource availability before creation"""
    
    def __init__(self, project_id: str, credentials):
        self.project_id = project_id
        self.credentials = credentials
    
    def check_backend_availability(self, backends: List[BackendConfig]) -> Dict[str, Any]:
        """Check if backend resources are available"""
        results = {
            "available": [],
            "unavailable": [],
            "warnings": []
        }
        
        for backend in backends:
            backend_status = self._check_backend_status(backend)
            
            if backend_status["available"]:
                results["available"].append(backend_status)
            else:
                results["unavailable"].append(backend_status)
            
            if backend_status["warnings"]:
                results["warnings"].extend(backend_status["warnings"])
        
        return results
    
    def _check_backend_status(self, backend: BackendConfig) -> Dict[str, Any]:
        """Check status of a single backend"""
        status = {
            "backend": backend,
            "available": True,
            "issues": [],
            "warnings": []
        }
        
        # Check if VMs exist and are running
        # For the current interface, we use vm_name as a single VM
        if hasattr(backend, 'vms') and backend.vms:
            # New interface with multiple VMs
            vm_status = self._check_vm_status(backend.vms, backend.zone)
            if not vm_status["all_running"]:
                status["available"] = False
                status["issues"].extend(vm_status["issues"])
            
            if vm_status["warnings"]:
                status["warnings"].extend(vm_status["warnings"])
        else:
            # Legacy interface with single vm_name
            vm_status = self._check_vm_status([backend.vm_name], backend.zone)
            if not vm_status["all_running"]:
                status["available"] = False
                status["issues"].extend(vm_status["issues"])
            
            if vm_status["warnings"]:
                status["warnings"].extend(vm_status["warnings"])
        
        return status
    
    def _check_vm_status(self, vms: List[str], zone: str) -> Dict[str, Any]:
        """Check VM status"""
        try:
            from google.cloud import compute_v1
            
            vm_client = compute_v1.InstancesClient(credentials=self.credentials)
            
            status = {
                "all_running": True,
                "issues": [],
                "warnings": []
            }
            
            for vm_name in vms:
                try:
                    request = compute_v1.GetInstanceRequest(
                        project=self.project_id,
                        zone=zone,
                        instance=vm_name
                    )
                    vm = vm_client.get(request=request)
                    
                    if vm.status != "RUNNING":
                        status["all_running"] = False
                        status["issues"].append(f"VM {vm_name} is not running (status: {vm.status})")
                    else:
                        status["warnings"].append(f"VM {vm_name} is running and ready")
                        
                except Exception as e:
                    if "not found" in str(e).lower():
                        status["all_running"] = False
                        status["issues"].append(f"VM {vm_name} not found in zone {zone}")
                    else:
                        status["warnings"].append(f"Could not check VM {vm_name}: {e}")
            
            return status
            
        except ImportError:
            # If compute client is not available, return basic status
            return {
                "all_running": True,  # Assume OK if we can't check
                "issues": [],
                "warnings": ["Could not verify VM status (compute client not available)"]
            }
    
    def format_availability_report(self, availability: Dict[str, Any]) -> str:
        """Format availability check results"""
        lines = ["🔍 Resource Availability Check:"]
        lines.append("")
        
        if availability["available"]:
            lines.append("✅ Available backends:")
            for backend_status in availability["available"]:
                backend = backend_status["backend"]
                lines.append(f"   • {backend.vm_name} ({backend.zone})")
                if hasattr(backend, 'vms') and backend.vms:
                    lines.append(f"     VMs: {len(backend.vms)} instances")
                else:
                    lines.append(f"     VM: {backend.vm_name}")
        
        if availability["unavailable"]:
            lines.append("")
            lines.append("⚠️  Backends with issues:")
            for backend_status in availability["unavailable"]:
                backend = backend_status["backend"]
                lines.append(f"   • {backend.vm_name} ({backend.zone})")
                for issue in backend_status["issues"]:
                    lines.append(f"     - {issue}")
        
        if availability["warnings"]:
            lines.append("")
            lines.append("💡 Notes:")
            for warning in availability["warnings"]:
                lines.append(f"   • {warning}")
        
        return "\n".join(lines) 