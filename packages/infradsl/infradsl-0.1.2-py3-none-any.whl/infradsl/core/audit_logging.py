"""
Comprehensive Audit Logging System for InfraDSL
Enterprise-grade logging for compliance, security, and governance
"""

import json
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
from pathlib import Path
from abc import ABC, abstractmethod
import queue
import gzip
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AuditEventType(Enum):
    """Types of auditable events"""
    # Resource operations
    RESOURCE_CREATE = "resource_create"
    RESOURCE_READ = "resource_read"
    RESOURCE_UPDATE = "resource_update"
    RESOURCE_DELETE = "resource_delete"
    RESOURCE_IMPORT = "resource_import"
    RESOURCE_EXPORT = "resource_export"
    
    # Authentication and authorization
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGE = "permission_change"
    ROLE_ASSIGNMENT = "role_assignment"
    ROLE_REVOCATION = "role_revocation"
    
    # Administrative operations
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    ROLE_CREATE = "role_create"
    ROLE_UPDATE = "role_update"
    ROLE_DELETE = "role_delete"
    POLICY_CREATE = "policy_create"
    POLICY_UPDATE = "policy_update"
    POLICY_DELETE = "policy_delete"
    
    # Infrastructure operations
    WORKSPACE_CREATE = "workspace_create"
    WORKSPACE_UPDATE = "workspace_update"
    WORKSPACE_DELETE = "workspace_delete"
    DEPLOYMENT_START = "deployment_start"
    DEPLOYMENT_COMPLETE = "deployment_complete"
    DEPLOYMENT_FAILED = "deployment_failed"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_VIOLATION = "security_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIGURATION_CHANGE = "configuration_change"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    FEDRAMP = "fedramp"
    NIST = "nist"


@dataclass
class AuditEvent:
    """Represents a single audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    
    # Actor information
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    service_account: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    # Resource information
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    workspace: Optional[str] = None
    provider: Optional[str] = None
    
    # Event details
    action: str = ""
    outcome: str = ""  # success, failure, pending
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Request context
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    
    # Compliance and security
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    sensitivity_level: str = "normal"  # normal, sensitive, confidential, restricted
    retention_period: Optional[int] = None  # days
    
    # Data classification
    contains_pii: bool = False
    contains_phi: bool = False
    contains_financial_data: bool = False
    
    # Integrity and authenticity
    checksum: Optional[str] = None
    digital_signature: Optional[str] = None


@dataclass
class AuditQuery:
    """Query parameters for audit log searches"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: List[AuditEventType] = field(default_factory=list)
    user_ids: List[str] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)
    workspaces: List[str] = field(default_factory=list)
    severity_levels: List[AuditSeverity] = field(default_factory=list)
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    contains_pii: Optional[bool] = None
    outcome: Optional[str] = None
    limit: int = 1000
    offset: int = 0


class AuditLogStorage(ABC):
    """Abstract interface for audit log storage backends"""
    
    @abstractmethod
    def store_event(self, event: AuditEvent) -> bool:
        """Store a single audit event"""
        pass
    
    @abstractmethod
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query audit events based on criteria"""
        pass
    
    @abstractmethod
    def get_event_count(self, query: AuditQuery) -> int:
        """Get count of events matching query"""
        pass
    
    @abstractmethod
    def archive_events(self, before_date: datetime) -> int:
        """Archive events older than specified date"""
        pass


class FileAuditLogStorage(AuditLogStorage):
    """File-based audit log storage with encryption and compression"""
    
    def __init__(self, storage_path: str, encryption_key: Optional[bytes] = None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Encryption setup
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            self.cipher = None
        
        # Create index for fast queries
        self.index_file = self.storage_path / "audit_index.json"
        self.index = self._load_index()
        
        # Thread safety
        self.lock = threading.Lock()
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store event to file with optional encryption"""
        try:
            with self.lock:
                # Serialize event
                event_data = asdict(event)
                event_data['timestamp'] = event.timestamp.isoformat()
                
                # Determine file path
                date_str = event.timestamp.strftime('%Y-%m-%d')
                file_path = self.storage_path / f"audit_{date_str}.jsonl"
                
                # Encrypt if enabled
                if self.cipher:
                    event_json = json.dumps(event_data)
                    encrypted_data = self.cipher.encrypt(event_json.encode())
                    event_line = base64.b64encode(encrypted_data).decode() + '\n'
                else:
                    event_line = json.dumps(event_data) + '\n'
                
                # Write to file
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(event_line)
                
                # Update index
                self._update_index(event)
                
                return True
                
        except Exception as e:
            logging.error(f"Failed to store audit event: {e}")
            return False
    
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query events from files"""
        events = []
        
        try:
            with self.lock:
                # Determine date range for file scanning
                files_to_scan = self._get_files_for_query(query)
                
                for file_path in files_to_scan:
                    events.extend(self._scan_file(file_path, query))
                
                # Apply limit and offset
                start_idx = query.offset
                end_idx = start_idx + query.limit
                return events[start_idx:end_idx]
                
        except Exception as e:
            logging.error(f"Failed to query audit events: {e}")
            return []
    
    def get_event_count(self, query: AuditQuery) -> int:
        """Get count of matching events"""
        return len(self.query_events(AuditQuery(
            start_time=query.start_time,
            end_time=query.end_time,
            event_types=query.event_types,
            user_ids=query.user_ids,
            resource_types=query.resource_types,
            workspaces=query.workspaces,
            severity_levels=query.severity_levels,
            compliance_frameworks=query.compliance_frameworks,
            contains_pii=query.contains_pii,
            outcome=query.outcome,
            limit=999999  # Large limit for counting
        )))
    
    def archive_events(self, before_date: datetime) -> int:
        """Archive old events to compressed files"""
        archived_count = 0
        
        try:
            with self.lock:
                # Find files to archive
                for file_path in self.storage_path.glob("audit_*.jsonl"):
                    file_date_str = file_path.stem.replace("audit_", "")
                    file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                    
                    if file_date < before_date:
                        # Compress and archive
                        archive_path = file_path.with_suffix('.jsonl.gz')
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(archive_path, 'wb') as f_out:
                                f_out.writelines(f_in)
                        
                        # Count archived events
                        with open(file_path, 'r') as f:
                            archived_count += sum(1 for _ in f)
                        
                        # Remove original file
                        file_path.unlink()
                
                return archived_count
                
        except Exception as e:
            logging.error(f"Failed to archive audit events: {e}")
            return 0
    
    def _load_index(self) -> Dict[str, Any]:
        """Load or create audit index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "files": {},
            "users": set(),
            "resource_types": set(),
            "workspaces": set(),
            "event_types": set()
        }
    
    def _update_index(self, event: AuditEvent):
        """Update search index with new event"""
        date_str = event.timestamp.strftime('%Y-%m-%d')
        
        if date_str not in self.index["files"]:
            self.index["files"][date_str] = {
                "event_count": 0,
                "first_event": event.timestamp.isoformat(),
                "last_event": event.timestamp.isoformat()
            }
        
        file_info = self.index["files"][date_str]
        file_info["event_count"] += 1
        file_info["last_event"] = event.timestamp.isoformat()
        
        # Update categorical indexes
        if event.user_id:
            self.index["users"].add(event.user_id)
        if event.resource_type:
            self.index["resource_types"].add(event.resource_type)
        if event.workspace:
            self.index["workspaces"].add(event.workspace)
        self.index["event_types"].add(event.event_type.value)
        
        # Convert sets to lists for JSON serialization
        index_to_save = self.index.copy()
        for key in ["users", "resource_types", "workspaces", "event_types"]:
            index_to_save[key] = list(self.index[key])
        
        # Save updated index
        with open(self.index_file, 'w') as f:
            json.dump(index_to_save, f, indent=2)
    
    def _get_files_for_query(self, query: AuditQuery) -> List[Path]:
        """Get list of files to scan for query"""
        files = []
        
        if query.start_time and query.end_time:
            # Scan only files in date range
            current_date = query.start_time.date()
            end_date = query.end_time.date()
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                file_path = self.storage_path / f"audit_{date_str}.jsonl"
                archive_path = self.storage_path / f"audit_{date_str}.jsonl.gz"
                
                if file_path.exists():
                    files.append(file_path)
                elif archive_path.exists():
                    files.append(archive_path)
                
                current_date += timedelta(days=1)
        else:
            # Scan all files
            files.extend(self.storage_path.glob("audit_*.jsonl"))
            files.extend(self.storage_path.glob("audit_*.jsonl.gz"))
        
        return sorted(files)
    
    def _scan_file(self, file_path: Path, query: AuditQuery) -> List[AuditEvent]:
        """Scan a single file for matching events"""
        events = []
        
        try:
            # Handle compressed files
            if file_path.suffix == '.gz':
                file_obj = gzip.open(file_path, 'rt', encoding='utf-8')
            else:
                file_obj = open(file_path, 'r', encoding='utf-8')
            
            with file_obj:
                for line in file_obj:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Decrypt if necessary
                        if self.cipher and not file_path.suffix == '.gz':
                            encrypted_data = base64.b64decode(line.encode())
                            decrypted_data = self.cipher.decrypt(encrypted_data)
                            event_data = json.loads(decrypted_data.decode())
                        else:
                            event_data = json.loads(line)
                        
                        # Convert back to AuditEvent
                        event = self._dict_to_audit_event(event_data)
                        
                        # Apply query filters
                        if self._event_matches_query(event, query):
                            events.append(event)
                            
                    except Exception as e:
                        logging.warning(f"Failed to parse audit event: {e}")
                        continue
            
            return events
            
        except Exception as e:
            logging.error(f"Failed to scan file {file_path}: {e}")
            return []
    
    def _dict_to_audit_event(self, data: Dict[str, Any]) -> AuditEvent:
        """Convert dictionary back to AuditEvent object"""
        # Convert timestamp back to datetime
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert enums back
        data['event_type'] = AuditEventType(data['event_type'])
        data['severity'] = AuditSeverity(data['severity'])
        
        if data.get('compliance_frameworks'):
            data['compliance_frameworks'] = [
                ComplianceFramework(f) for f in data['compliance_frameworks']
            ]
        
        return AuditEvent(**data)
    
    def _event_matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Check if event matches query criteria"""
        
        # Time range filter
        if query.start_time and event.timestamp < query.start_time:
            return False
        if query.end_time and event.timestamp > query.end_time:
            return False
        
        # Event type filter
        if query.event_types and event.event_type not in query.event_types:
            return False
        
        # User filter
        if query.user_ids and event.user_id not in query.user_ids:
            return False
        
        # Resource type filter
        if query.resource_types and event.resource_type not in query.resource_types:
            return False
        
        # Workspace filter
        if query.workspaces and event.workspace not in query.workspaces:
            return False
        
        # Severity filter
        if query.severity_levels and event.severity not in query.severity_levels:
            return False
        
        # Compliance framework filter
        if query.compliance_frameworks:
            if not any(cf in event.compliance_frameworks for cf in query.compliance_frameworks):
                return False
        
        # PII filter
        if query.contains_pii is not None and event.contains_pii != query.contains_pii:
            return False
        
        # Outcome filter
        if query.outcome and event.outcome != query.outcome:
            return False
        
        return True


class AuditLogger:
    """
    Comprehensive audit logging system for InfraDSL
    
    Features:
    - Multiple storage backends
    - Real-time event streaming
    - Compliance framework support
    - Data encryption and integrity
    - Advanced querying and reporting
    - Automated archival and retention
    - Integration with SIEM systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage backend
        self.storage = self._initialize_storage()
        
        # Event queue for asynchronous processing
        self.event_queue = queue.Queue(maxsize=10000)
        self.processing_thread = None
        self.running = False
        
        # Event listeners for real-time processing
        self.event_listeners: List[Callable[[AuditEvent], None]] = []
        
        # Compliance configuration
        self.compliance_config = self._load_compliance_config()
        
        # Metrics tracking
        self.metrics = {
            "events_logged": 0,
            "events_failed": 0,
            "last_event_time": None
        }
        
        # Start processing thread
        self.start()
    
    def log_event(self, event_type: AuditEventType, **kwargs) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event being logged
            **kwargs: Event details
            
        Returns:
            Event ID of the logged event
        """
        
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=kwargs.get('severity', AuditSeverity.INFO),
            **{k: v for k, v in kwargs.items() if k != 'severity'}
        )
        
        # Apply compliance requirements
        event = self._apply_compliance_requirements(event)
        
        # Calculate integrity checksum
        event.checksum = self._calculate_checksum(event)
        
        # Queue for processing
        try:
            self.event_queue.put_nowait(event)
            self.metrics["events_logged"] += 1
            self.metrics["last_event_time"] = datetime.utcnow()
        except queue.Full:
            self.logger.error("Audit event queue is full, dropping event")
            self.metrics["events_failed"] += 1
        
        return event_id
    
    def query_events(self, **kwargs) -> List[AuditEvent]:
        """
        Query audit events
        
        Args:
            **kwargs: Query parameters
            
        Returns:
            List of matching audit events
        """
        
        query = AuditQuery(**kwargs)
        return self.storage.query_events(query)
    
    def add_event_listener(self, listener: Callable[[AuditEvent], None]):
        """Add real-time event listener"""
        self.event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[AuditEvent], None]):
        """Remove event listener"""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
    
    def generate_compliance_report(self, framework: ComplianceFramework,
                                 start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Generate compliance report for specific framework
        
        Args:
            framework: Compliance framework
            start_time: Report start time
            end_time: Report end time
            
        Returns:
            Compliance report
        """
        
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            compliance_frameworks=[framework],
            limit=999999
        )
        
        events = self.storage.query_events(query)
        
        # Generate report based on framework requirements
        if framework == ComplianceFramework.SOX:
            return self._generate_sox_report(events, start_time, end_time)
        elif framework == ComplianceFramework.GDPR:
            return self._generate_gdpr_report(events, start_time, end_time)
        elif framework == ComplianceFramework.HIPAA:
            return self._generate_hipaa_report(events, start_time, end_time)
        else:
            return self._generate_generic_report(events, start_time, end_time, framework)
    
    def archive_old_events(self, retention_days: int = 2555) -> int:
        """Archive events older than retention period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        return self.storage.archive_events(cutoff_date)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get audit logging metrics"""
        
        return {
            **self.metrics,
            "queue_size": self.event_queue.qsize(),
            "storage_backend": type(self.storage).__name__,
            "listeners_count": len(self.event_listeners)
        }
    
    def start(self):
        """Start audit logging processing"""
        
        if not self.running:
            self.running = True
            self.processing_thread = threading.Thread(target=self._process_events)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            self.logger.info("Audit logging started")
    
    def stop(self):
        """Stop audit logging processing"""
        
        if self.running:
            self.running = False
            if self.processing_thread:
                self.processing_thread.join(timeout=5)
            self.logger.info("Audit logging stopped")
    
    def _process_events(self):
        """Process events from queue"""
        
        while self.running:
            try:
                # Get event from queue (with timeout)
                event = self.event_queue.get(timeout=1)
                
                # Store event
                success = self.storage.store_event(event)
                
                if success:
                    # Notify listeners
                    for listener in self.event_listeners:
                        try:
                            listener(event)
                        except Exception as e:
                            self.logger.error(f"Event listener failed: {e}")
                else:
                    self.metrics["events_failed"] += 1
                
                # Mark task as done
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audit event: {e}")
                self.metrics["events_failed"] += 1
    
    def _initialize_storage(self) -> AuditLogStorage:
        """Initialize storage backend"""
        
        storage_type = self.config.get("storage_type", "file")
        
        if storage_type == "file":
            storage_path = self.config.get("storage_path", "./audit_logs")
            encryption_key = self.config.get("encryption_key")
            return FileAuditLogStorage(storage_path, encryption_key)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    def _apply_compliance_requirements(self, event: AuditEvent) -> AuditEvent:
        """Apply compliance framework requirements to event"""
        
        # Determine applicable compliance frameworks
        frameworks = []
        
        # Check for financial data (SOX)
        if event.contains_financial_data or "financial" in event.message.lower():
            frameworks.append(ComplianceFramework.SOX)
        
        # Check for PII/PHI (GDPR/HIPAA)
        if event.contains_pii:
            frameworks.append(ComplianceFramework.GDPR)
        if event.contains_phi:
            frameworks.append(ComplianceFramework.HIPAA)
        
        # Default compliance requirements
        if event.event_type in [AuditEventType.ACCESS_GRANTED, AuditEventType.ACCESS_DENIED]:
            frameworks.append(ComplianceFramework.SOC2)
        
        event.compliance_frameworks = frameworks
        
        # Set retention period based on frameworks
        if ComplianceFramework.SOX in frameworks:
            event.retention_period = 2555  # 7 years
        elif ComplianceFramework.GDPR in frameworks:
            event.retention_period = 2190  # 6 years
        elif ComplianceFramework.HIPAA in frameworks:
            event.retention_period = 2190  # 6 years
        else:
            event.retention_period = 1095  # 3 years default
        
        return event
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate integrity checksum for event"""
        
        # Create deterministic string representation
        event_str = f"{event.event_id}|{event.timestamp.isoformat()}|{event.event_type.value}|{event.user_id}|{event.action}|{event.outcome}"
        
        # Calculate SHA-256 hash
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def _load_compliance_config(self) -> Dict[str, Any]:
        """Load compliance configuration"""
        
        return {
            "sox_enabled": True,
            "gdpr_enabled": True,
            "hipaa_enabled": True,
            "pci_dss_enabled": False,
            "default_retention_days": 1095
        }
    
    def _generate_sox_report(self, events: List[AuditEvent], 
                           start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate SOX compliance report"""
        
        # Analyze events for SOX requirements
        financial_access_events = [e for e in events if e.contains_financial_data]
        privileged_access_events = [e for e in events if e.event_type in [
            AuditEventType.ACCESS_GRANTED, AuditEventType.ROLE_ASSIGNMENT
        ]]
        
        return {
            "framework": "SOX",
            "period": f"{start_time.date()} to {end_time.date()}",
            "total_events": len(events),
            "financial_access_events": len(financial_access_events),
            "privileged_access_events": len(privileged_access_events),
            "compliance_status": "COMPLIANT" if len(financial_access_events) == 0 else "REVIEW_REQUIRED",
            "recommendations": [
                "Review all financial data access events",
                "Ensure separation of duties for financial operations",
                "Implement additional controls for privileged access"
            ]
        }
    
    def _generate_gdpr_report(self, events: List[AuditEvent],
                            start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        
        # Analyze events for GDPR requirements
        pii_events = [e for e in events if e.contains_pii]
        data_subject_requests = [e for e in events if "data_subject" in e.message.lower()]
        
        return {
            "framework": "GDPR",
            "period": f"{start_time.date()} to {end_time.date()}",
            "total_events": len(events),
            "pii_access_events": len(pii_events),
            "data_subject_requests": len(data_subject_requests),
            "compliance_status": "COMPLIANT",
            "recommendations": [
                "Regularly review PII access patterns",
                "Ensure data subject rights are respected",
                "Implement data minimization principles"
            ]
        }
    
    def _generate_hipaa_report(self, events: List[AuditEvent],
                             start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate HIPAA compliance report"""
        
        # Analyze events for HIPAA requirements
        phi_events = [e for e in events if e.contains_phi]
        healthcare_access = [e for e in events if "health" in e.message.lower()]
        
        return {
            "framework": "HIPAA",
            "period": f"{start_time.date()} to {end_time.date()}",
            "total_events": len(events),
            "phi_access_events": len(phi_events),
            "healthcare_access_events": len(healthcare_access),
            "compliance_status": "COMPLIANT",
            "recommendations": [
                "Monitor PHI access closely",
                "Ensure minimum necessary access principle",
                "Regular workforce training on HIPAA requirements"
            ]
        }
    
    def _generate_generic_report(self, events: List[AuditEvent],
                               start_time: datetime, end_time: datetime,
                               framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate generic compliance report"""
        
        return {
            "framework": framework.value.upper(),
            "period": f"{start_time.date()} to {end_time.date()}",
            "total_events": len(events),
            "compliance_status": "REVIEW_REQUIRED",
            "recommendations": [
                f"Review events for {framework.value.upper()} compliance",
                "Implement framework-specific controls",
                "Regular compliance assessments"
            ]
        }


# Pre-configured event logging functions for common operations
def log_resource_operation(audit_logger: AuditLogger, operation: str, **kwargs):
    """Log resource operation with standardized format"""
    
    event_type_map = {
        "create": AuditEventType.RESOURCE_CREATE,
        "read": AuditEventType.RESOURCE_READ,
        "update": AuditEventType.RESOURCE_UPDATE,
        "delete": AuditEventType.RESOURCE_DELETE,
        "import": AuditEventType.RESOURCE_IMPORT,
        "export": AuditEventType.RESOURCE_EXPORT
    }
    
    event_type = event_type_map.get(operation.lower(), AuditEventType.RESOURCE_UPDATE)
    
    return audit_logger.log_event(
        event_type=event_type,
        action=f"Resource {operation}",
        **kwargs
    )


def log_access_event(audit_logger: AuditLogger, granted: bool, **kwargs):
    """Log access control event"""
    
    event_type = AuditEventType.ACCESS_GRANTED if granted else AuditEventType.ACCESS_DENIED
    severity = AuditSeverity.INFO if granted else AuditSeverity.WARNING
    
    return audit_logger.log_event(
        event_type=event_type,
        severity=severity,
        outcome="success" if granted else "failure",
        **kwargs
    )


def log_security_event(audit_logger: AuditLogger, event_type: str, **kwargs):
    """Log security-related event"""
    
    security_event_map = {
        "suspicious_activity": AuditEventType.SUSPICIOUS_ACTIVITY,
        "security_violation": AuditEventType.SECURITY_VIOLATION,
        "unauthorized_access": AuditEventType.UNAUTHORIZED_ACCESS,
        "data_breach": AuditEventType.DATA_BREACH
    }
    
    event_type_enum = security_event_map.get(event_type, AuditEventType.SECURITY_VIOLATION)
    
    return audit_logger.log_event(
        event_type=event_type_enum,
        severity=AuditSeverity.CRITICAL,
        **kwargs
    )