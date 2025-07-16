"""
Workflow Automation Supporting Classes
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json


class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class EscalationLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationRule:
    channel: NotificationChannel
    recipient: str
    template: str
    delay_minutes: int = 0


@dataclass
class EscalationRule:
    level: EscalationLevel
    threshold_hours: int
    escalate_to: List[str]
    notification_rules: List[NotificationRule]


class NotificationManager:
    def __init__(self):
        self.rules: Dict[str, List[NotificationRule]] = {}
        self.escalation_rules: Dict[str, List[EscalationRule]] = {}
        self.notification_history: List[Dict] = []

    async def send_notification(self, event_type: str, recipient: str, 
                              data: Dict[str, Any]) -> bool:
        """Send notification based on event type"""
        try:
            # In a real system, this would integrate with email/SMS services
            notification = {
                "id": f"notif_{len(self.notification_history) + 1}",
                "event_type": event_type,
                "recipient": recipient,
                "data": data,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            self.notification_history.append(notification)
            print(f"Notification sent: {event_type} to {recipient}")
            return True
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def add_rule(self, event_type: str, rule: NotificationRule):
        """Add notification rule for event type"""
        if event_type not in self.rules:
            self.rules[event_type] = []
        self.rules[event_type].append(rule)

    def add_escalation_rule(self, request_type: str, rule: EscalationRule):
        """Add escalation rule for request type"""
        if request_type not in self.escalation_rules:
            self.escalation_rules[request_type] = []
        self.escalation_rules[request_type].append(rule)


class DocumentManager:
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self.documents: Dict[str, Dict] = {}

    def create_document(self, template_name: str, data: Dict[str, Any]) -> str:
        """Create document from template"""
        doc_id = f"doc_{len(self.documents) + 1}"
        
        if template_name in self.templates:
            content = self.templates[template_name].format(**data)
        else:
            content = json.dumps(data, indent=2)
        
        document = {
            "id": doc_id,
            "template": template_name,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "data": data
        }
        
        self.documents[doc_id] = document
        return doc_id

    def add_template(self, name: str, template: str):
        """Add document template"""
        self.templates[name] = template

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID"""
        return self.documents.get(doc_id)


class SupplierIntegrationManager:
    def __init__(self):
        self.integrations: Dict[str, Dict] = {}
        self.api_configurations: Dict[str, Dict] = {}

    async def sync_catalog(self, supplier_id: str) -> List[Dict[str, Any]]:
        """Sync catalog from supplier API"""
        # Mock catalog data - in real system would call supplier API
        mock_catalog = [
            {
                "item_id": "SUP_ITEM_001",
                "name": "Medical Gloves",
                "price": 15.99,
                "stock": 1000,
                "lead_time_days": 3
            },
            {
                "item_id": "SUP_ITEM_002", 
                "name": "Surgical Masks",
                "price": 8.50,
                "stock": 500,
                "lead_time_days": 5
            }
        ]
        
        integration_record = {
            "supplier_id": supplier_id,
            "last_sync": datetime.now().isoformat(),
            "items_synced": len(mock_catalog),
            "status": "success"
        }
        
        self.integrations[supplier_id] = integration_record
        return mock_catalog

    async def submit_purchase_order(self, supplier_id: str, po_data: Dict) -> bool:
        """Submit PO to supplier system"""
        try:
            # Mock API call - in real system would submit to supplier
            print(f"Submitting PO {po_data.get('po_number')} to supplier {supplier_id}")
            return True
        except Exception as e:
            print(f"Failed to submit PO to supplier: {e}")
            return False

    def configure_api(self, supplier_id: str, config: Dict[str, str]):
        """Configure API settings for supplier"""
        self.api_configurations[supplier_id] = config


class WorkflowAnalytics:
    def __init__(self):
        self.metrics_cache: Dict[str, Any] = {}
        self.last_calculation: Optional[datetime] = None

    def calculate_cycle_times(self, approval_requests: List) -> Dict[str, float]:
        """Calculate average cycle times for approval processes"""
        cycle_times = {}
        
        for request in approval_requests:
            if hasattr(request, 'status') and request.status.value == 'approved':
                # Calculate time from creation to approval
                if hasattr(request, 'approvals') and request.approvals:
                    start_time = request.created_at
                    end_time = datetime.fromisoformat(request.approvals[-1]['timestamp'])
                    cycle_time = (end_time - start_time).total_seconds() / 3600  # hours
                    
                    request_type = request.request_type
                    if request_type not in cycle_times:
                        cycle_times[request_type] = []
                    cycle_times[request_type].append(cycle_time)
        
        # Calculate averages
        avg_cycle_times = {}
        for req_type, times in cycle_times.items():
            avg_cycle_times[req_type] = sum(times) / len(times) if times else 0
        
        return avg_cycle_times

    def calculate_bottlenecks(self, approval_requests: List) -> List[Dict[str, Any]]:
        """Identify bottlenecks in approval process"""
        approver_times = {}
        
        for request in approval_requests:
            if hasattr(request, 'approvals'):
                for i, approval in enumerate(request.approvals):
                    approver = approval['approver_id']
                    if approver not in approver_times:
                        approver_times[approver] = []
                    
                    # Calculate time this approver took
                    if i == 0:
                        start_time = request.created_at
                    else:
                        start_time = datetime.fromisoformat(request.approvals[i-1]['timestamp'])
                    
                    end_time = datetime.fromisoformat(approval['timestamp'])
                    approval_time = (end_time - start_time).total_seconds() / 3600
                    approver_times[approver].append(approval_time)
        
        # Find bottlenecks (approvers with high average times)
        bottlenecks = []
        for approver, times in approver_times.items():
            avg_time = sum(times) / len(times) if times else 0
            if avg_time > 24:  # More than 24 hours average
                bottlenecks.append({
                    "approver": approver,
                    "avg_approval_time_hours": avg_time,
                    "requests_processed": len(times)
                })
        
        return sorted(bottlenecks, key=lambda x: x['avg_approval_time_hours'], reverse=True)

    def generate_dashboard_metrics(self, workflow_engine) -> Dict[str, Any]:
        """Generate comprehensive dashboard metrics"""
        approval_metrics = workflow_engine.get_approval_metrics()
        po_metrics = workflow_engine.get_po_metrics()
        supplier_metrics = workflow_engine.get_supplier_metrics()
        
        # Calculate additional metrics
        cycle_times = self.calculate_cycle_times(list(workflow_engine.approval_requests.values()))
        bottlenecks = self.calculate_bottlenecks(list(workflow_engine.approval_requests.values()))
        
        return {
            "approval_metrics": approval_metrics,
            "po_metrics": po_metrics,
            "supplier_metrics": supplier_metrics,
            "cycle_times": cycle_times,
            "bottlenecks": bottlenecks,
            "last_updated": datetime.now().isoformat()
        }


# Initialize supporting managers
notification_manager = NotificationManager()
document_manager = DocumentManager()
supplier_integration_manager = SupplierIntegrationManager()
workflow_analytics = WorkflowAnalytics()

# Setup default templates
document_manager.add_template("purchase_order", """
PURCHASE ORDER: {po_number}
Date: {date}
Supplier: {supplier_name}
Total Amount: ${total_amount}

Items:
{items}

Delivery Date: {delivery_date}
""")

document_manager.add_template("approval_request", """
APPROVAL REQUEST: {request_id}
Type: {request_type}
Requester: {requester}
Amount: ${amount}
Justification: {justification}

Please review and approve/reject.
""")
