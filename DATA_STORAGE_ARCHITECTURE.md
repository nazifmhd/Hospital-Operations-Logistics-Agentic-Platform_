# 📊 Data Storage Architecture - Hospital Supply Platform

## 🗄️ **Where Your Approval Workflow Data is Stored**

### **1. Memory-Based Storage (Current Implementation)**

#### **ConversationMemory Class - In-Memory Storage**
```python
# Location: ai_ml/comprehensive_ai_agent.py (lines 88-106)
@dataclass
class ConversationMemory:
    user_id: str
    session_id: str
    context_type: ConversationContext
    entities_mentioned: List[str]
    actions_performed: List[AgentAction]
    preferences: Dict[str, Any]
    last_updated: datetime
    conversation_history: List[Dict[str, str]] = None
    pending_approvals: Dict[str, Any] = None      # ← APPROVAL WORKFLOW DATA
    pending_orders: List[Dict[str, Any]] = None   # ← PENDING ORDERS DATA
```

#### **Agent Memory Storage**
```python
# Location: ai_ml/comprehensive_ai_agent.py (line 127)
class ComprehensiveAIAgent:
    def __init__(self):
        self.conversation_memory = {}  # ← SESSION-BASED MEMORY STORAGE
        self.active_sessions = {}
```

#### **What's Stored in Memory:**
1. **Pending Approvals** (`pending_approvals`):
   ```json
   {
     "suggestions": [
       {
         "type": "inter_transfer",
         "from_location": "ER-01",
         "to_location": "ICU-01",
         "item_name": "medical supplies",
         "suggested_quantity": 15,
         "available_quantity": 30,
         "urgency": "high"
       },
       {
         "type": "automatic_reorder",
         "item_name": "medical supplies",
         "location": "ICU-01",
         "suggested_quantity": 80,
         "urgency": "medium",
         "estimated_delivery": "2-3 business days"
       }
     ],
     "item_context": {
       "item_name": "medical supplies",
       "location": "ICU-01",
       "current_stock": 66,
       "modification_timestamp": "2025-07-29T22:47:05"
     },
     "created_at": "2025-07-29T22:47:05"
   }
   ```

2. **Pending Orders** (`pending_orders`):
   ```json
   [
     {
       "order_id": "PENDING-E5F6G7H8",
       "item_name": "medical supplies",
       "quantity": 80,
       "location": "ICU-01",
       "status": "pending",
       "rejection_timestamp": "2025-07-29T22:47:05",
       "reason": "User rejected via chat",
       "requires_manager_approval": true
     }
   ]
   ```

---

### **2. Database Storage (Persistent Storage)**

#### **PostgreSQL Database Structure**
```
📁 backend/database/
├── config.py              # Database configuration
├── database.py            # Database connection setup
├── models.py              # SQLAlchemy models
├── repositories.py        # Data access layer
└── init_db.py             # Database initialization
```

#### **Current Inventory Data Storage**
```python
# Location: backend/fixed_database_integration.py
class FixedDatabaseIntegration:
    """Handles PostgreSQL connection with inventory data"""
    
    async def get_inventory_data(self):
        """Retrieves inventory from PostgreSQL database"""
        # Current: 124 inventory items stored in PostgreSQL
        # Database tables: inventory_items, departments, etc.
```

#### **Database Tables for Approval Workflow**
```sql
-- Suggested tables for persistent approval workflow storage:

-- 1. Pending Approvals Table
CREATE TABLE pending_approvals (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL,  -- 'inter_transfer' or 'automatic_reorder'
    item_name VARCHAR(255) NOT NULL,
    from_location VARCHAR(100),
    to_location VARCHAR(100),
    suggested_quantity INTEGER NOT NULL,
    urgency VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'  -- 'pending', 'approved', 'rejected'
);

-- 2. Pending Orders Table
CREATE TABLE pending_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    location VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requires_manager_approval BOOLEAN DEFAULT TRUE
);

-- 3. Transfer History Table
CREATE TABLE transfer_history (
    id SERIAL PRIMARY KEY,
    transfer_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    from_location VARCHAR(100) NOT NULL,
    to_location VARCHAR(100) NOT NULL,
    quantity_transferred INTEGER NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed'
);
```

---

### **3. Data Flow Architecture**

#### **Current Data Storage Flow:**
```
User Input → AI Agent → ConversationMemory (RAM) → Response
                    ↓
              PostgreSQL Database
              (Inventory Data)
```

#### **Enhanced Data Storage Flow (For Production):**
```
User Input → AI Agent → ConversationMemory (RAM) → Response
                    ↓                    ↓
              PostgreSQL Database    Redis Cache
              (Persistent Storage)   (Session Storage)
                    ↓
              Backup & Analytics
```

---

### **4. Storage Locations Summary**

#### **🔴 Currently Active Storage:**

1. **In-Memory (Temporary)**:
   - **Location**: `self.conversation_memory` in `ComprehensiveAIAgent`
   - **Data**: Pending approvals, pending orders, conversation history
   - **Persistence**: Session-based (lost when server restarts)
   - **File**: `ai_ml/comprehensive_ai_agent.py`

2. **PostgreSQL Database (Persistent)**:
   - **Location**: Database server (configured in `backend/database/`)
   - **Data**: Inventory items (124 items), departments, stock levels
   - **Persistence**: Permanent
   - **File**: `backend/fixed_database_integration.py`

#### **🟢 Recommended for Production:**

1. **PostgreSQL Tables** (Add approval workflow tables):
   ```sql
   -- Add these tables to your existing database:
   - pending_approvals
   - pending_orders  
   - transfer_history
   - approval_audit_log
   ```

2. **Redis Cache** (Session management):
   ```
   - Session-based approval states
   - Quick access to pending approvals
   - Real-time conversation context
   ```

---

### **5. How to Make Storage Persistent**

#### **Option 1: Extend PostgreSQL (Recommended)**
```python
# Add to backend/database/models.py
class PendingApproval(Base):
    __tablename__ = 'pending_approvals'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    suggestion_type = Column(String(50), nullable=False)
    item_name = Column(String(255), nullable=False)
    # ... other fields

class PendingOrder(Base):
    __tablename__ = 'pending_orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, nullable=False)
    # ... other fields
```

#### **Option 2: Add Redis for Session Storage**
```python
# Add to requirements.txt
redis==4.5.4

# Add session storage
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Store approval data
redis_client.setex(
    f"approvals:{session_id}", 
    3600,  # 1 hour expiry
    json.dumps(pending_approvals)
)
```

---

### **6. Current Working Directory Structure**

```
📁 e:\Rise Ai\Updated\Hospital-Operations-Logistics-Agentic-Platform_\
├── 📁 ai_ml/
│   ├── comprehensive_ai_agent.py     ← APPROVAL WORKFLOW CODE (Memory Storage)
│   ├── rag_system.py                ← RAG Data Storage
│   └── rag_data/chromadb/           ← Vector Database
├── 📁 backend/
│   ├── fixed_database_integration.py ← INVENTORY DATA (PostgreSQL)
│   └── database/                     ← Database Models & Config
├── 📁 dashboard/supply_dashboard/    ← Frontend (React)
└── 📄 approval_workflow_demo.py     ← Working Demo
```

---

## 🎯 **Summary: Where Your Data Lives**

### **✅ Current Storage (Working Now)**:
- **Approval Workflow Data**: In-memory (`ConversationMemory` class)
- **Inventory Data**: PostgreSQL database (124 items)
- **Conversation History**: In-memory (per session)

### **🚀 For Production (Recommended)**:
- **Add PostgreSQL tables** for persistent approval/pending order storage
- **Keep in-memory storage** for fast access during active sessions
- **Optional: Add Redis** for session management across server restarts

**Your approval workflow is currently working with in-memory storage, which is perfect for development and testing. For production, you'd add database tables to make approvals and pending orders persistent.** 📊
