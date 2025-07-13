# Hospital Operations Platform - Architecture Documentation

## System Architecture Overview

The Hospital Operations & Logistics Platform is built using a modern, scalable architecture that supports real-time operations, high availability, and HIPAA compliance requirements.

## 🏗️ High-Level Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│   Frontend (React)  │◄──►│  Backend (FastAPI)  │◄──►│   Database Layer    │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
          │                           │                           │
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  WebSocket Layer    │    │   Agent Framework   │    │   External APIs     │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📱 Frontend Architecture

### Technology Stack
- **Framework**: React 18.2+
- **Language**: JavaScript (ES6+)
- **Styling**: Tailwind CSS
- **State Management**: React Hooks + Context API
- **Routing**: React Router v6
- **HTTP Client**: Fetch API
- **Real-time**: WebSocket

### Component Architecture
```
src/
├── components/
│   ├── Dashboard/           # Main dashboard components
│   ├── Analytics/          # Analytics and reporting
│   ├── Inventory/          # Inventory management
│   ├── Alerts/             # Alert system
│   ├── Professional/       # Professional dashboard
│   ├── MultiLocation/      # Multi-location management
│   ├── Batch/              # Batch tracking
│   ├── User/               # User management
│   ├── Settings/           # System settings
│   └── Common/             # Shared components
├── utils/
│   ├── api.js              # API utilities
│   ├── websocket.js        # WebSocket client
│   ├── helpers.js          # Helper functions
│   └── constants.js        # Application constants
├── styles/
│   └── globals.css         # Global styles
└── App.js                  # Main application component
```

### Component Design Patterns

#### Container/Presentational Pattern
```javascript
// Container Component (Logic)
const InventoryContainer = () => {
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchInventory();
    }, []);
    
    return <InventoryTable data={inventory} loading={loading} />;
};

// Presentational Component (UI)
const InventoryTable = ({ data, loading }) => {
    if (loading) return <LoadingSpinner />;
    return <Table data={data} />;
};
```

#### Custom Hooks for State Management
```javascript
// useInventory Hook
const useInventory = () => {
    const [inventory, setInventory] = useState([]);
    const [alerts, setAlerts] = useState([]);
    
    const updateStock = async (itemId, quantity) => {
        // Update logic
    };
    
    return { inventory, alerts, updateStock };
};
```

### Real-time Data Flow
```
Component → useEffect → API Call → State Update → Re-render
    ↑                                                   ↓
WebSocket ← Event Handler ← WebSocket Message ← Server Push
```

## 🔧 Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.9+
- **ASGI Server**: Uvicorn
- **WebSocket**: FastAPI WebSocket support
- **Validation**: Pydantic models
- **CORS**: FastAPI CORS middleware

### API Architecture
```
backend/
├── api/
│   ├── main.py                 # FastAPI application
│   ├── professional_main.py    # Professional endpoints
│   ├── models/
│   │   ├── inventory.py        # Data models
│   │   ├── alerts.py          # Alert models
│   │   └── users.py           # User models
│   ├── services/
│   │   ├── inventory_service.py    # Business logic
│   │   ├── alert_service.py       # Alert processing
│   │   └── analytics_service.py   # Analytics engine
│   └── utils/
│       ├── database.py        # Database utilities
│       ├── auth.py           # Authentication
│       └── websocket.py      # WebSocket manager
└── requirements.txt          # Python dependencies
```

### API Endpoint Design
```python
# RESTful Endpoint Structure
@app.get("/api/v1/inventory")           # GET all items
@app.get("/api/v1/inventory/{id}")      # GET specific item
@app.post("/api/v1/inventory")          # CREATE new item
@app.put("/api/v1/inventory/{id}")      # UPDATE existing item
@app.delete("/api/v1/inventory/{id}")   # DELETE item

# Professional Dashboard Endpoints
@app.get("/api/v1/professional/overview")     # Executive metrics
@app.get("/api/v1/professional/analytics")    # Advanced analytics
@app.post("/api/v1/professional/reports")     # Generate reports
```

### Data Models (Pydantic)
```python
class InventoryItem(BaseModel):
    id: int
    name: str
    category: str
    current_stock: int
    minimum_threshold: int
    location: str
    expiry_date: Optional[date]
    unit_cost: float
    supplier: str
    last_updated: datetime

class Alert(BaseModel):
    id: int
    type: AlertType
    priority: Priority
    item_id: int
    message: str
    created_at: datetime
    resolved: bool = False
```

## 🤖 Agent Framework

### Supply Inventory Agent
```python
class SupplyInventoryAgent:
    def __init__(self):
        self.monitor = InventoryMonitor()
        self.analyzer = UsageAnalyzer()
        self.forecaster = DemandForecaster()
        self.alerter = AlertManager()
    
    async def run_monitoring_cycle(self):
        """Main agent execution loop"""
        while True:
            await self.monitor.check_inventory()
            await self.analyzer.analyze_usage_patterns()
            await self.forecaster.predict_demand()
            await self.alerter.generate_alerts()
            await asyncio.sleep(30)  # 30-second cycle
```

### Agent Capabilities

#### 1. Inventory Monitoring
- Real-time stock level tracking
- Automated threshold checking
- Expiry date monitoring
- Location-based tracking

#### 2. Intelligent Analytics
- Consumption pattern analysis
- Demand forecasting
- Cost optimization recommendations
- Supplier performance evaluation

#### 3. Alert Generation
- Multi-level priority system
- Contextual alert messages
- Automated resolution suggestions
- Escalation procedures

#### 4. Procurement Optimization
- Optimal order quantity calculation
- Supplier selection assistance
- Cost-benefit analysis
- Lead time optimization

## 🗄️ Data Architecture

### Data Models

#### Inventory Management
```sql
-- Inventory Items Table
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    current_stock INTEGER NOT NULL,
    minimum_threshold INTEGER DEFAULT 0,
    location VARCHAR(100),
    expiry_date DATE,
    unit_cost DECIMAL(10,2),
    supplier VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stock Movements Table
CREATE TABLE stock_movements (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES inventory_items(id),
    movement_type VARCHAR(50), -- 'IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'
    quantity INTEGER NOT NULL,
    from_location VARCHAR(100),
    to_location VARCHAR(100),
    reason VARCHAR(255),
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### Alert System
```sql
-- Alerts Table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    item_id INTEGER REFERENCES inventory_items(id),
    message TEXT NOT NULL,
    details JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by INTEGER,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### User Management
```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    password_hash VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Data Flow Architecture
```
User Action → Frontend → API Gateway → Business Logic → Database
     ↓             ↑                                        ↓
WebSocket ← Real-time Updates ← Agent Processing ← Data Changes
```

## 🔄 Real-time Architecture

### WebSocket Implementation
```python
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
```

### Event Types
- `inventory_update`: Stock level changes
- `new_alert`: Alert generation
- `alert_resolved`: Alert resolution
- `batch_expiry`: Expiry warnings
- `user_activity`: User actions

## 🔒 Security Architecture

### Authentication & Authorization
```python
# JWT Token-based Authentication
class AuthManager:
    def create_access_token(self, user_id: int, role: str):
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
```

### Role-Based Access Control (RBAC)
```python
@require_role(["admin", "manager"])
async def delete_inventory_item(item_id: int):
    # Only admins and managers can delete items
    pass

@require_role(["admin"])
async def manage_users():
    # Only admins can manage users
    pass
```

### HIPAA Compliance Measures
- Data encryption at rest and in transit
- Audit logging for all data access
- User authentication and authorization
- Regular security assessments
- Data retention policies

## 🚀 Deployment Architecture

### Development Environment
```
localhost:3000 (Frontend) ← → localhost:8001 (Backend)
```

### Production Environment (Planned)
```
Load Balancer → Frontend (React) → API Gateway → Backend Services
                      ↓                            ↓
                 Static Assets               Database Cluster
                      ↓                            ↓
                    CDN                      Redis Cache
```

### Docker Configuration
```dockerfile
# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 📊 Performance Considerations

### Frontend Optimization
- Component lazy loading
- React.memo for expensive components
- Virtual scrolling for large lists
- Debounced search inputs
- Image optimization

### Backend Optimization
- Database query optimization
- Connection pooling
- Caching strategies (Redis)
- Async/await for I/O operations
- Background task processing

### Real-time Performance
- WebSocket connection management
- Event batching for high-frequency updates
- Client-side data caching
- Optimistic UI updates

## 🔍 Monitoring & Observability

### Application Monitoring
- Performance metrics collection
- Error tracking and reporting
- User activity analytics
- System health monitoring

### Logging Strategy
```python
import logging

# Structured logging
logger = logging.getLogger(__name__)

def log_inventory_update(item_id: int, old_stock: int, new_stock: int, user_id: int):
    logger.info(
        "Inventory updated",
        extra={
            "event": "inventory_update",
            "item_id": item_id,
            "old_stock": old_stock,
            "new_stock": new_stock,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## 🔧 Development Guidelines

### Code Quality Standards
- Type hints for Python code
- ESLint and Prettier for JavaScript
- Comprehensive unit tests
- Integration tests for APIs
- Code coverage requirements (>80%)

### Git Workflow
```
main branch (production-ready)
  ↑
develop branch (integration)
  ↑
feature branches (development)
```

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Performance tests for scalability
- Security tests for vulnerability assessment

This architecture documentation provides a comprehensive view of the system design, enabling effective development, maintenance, and scaling of the Hospital Operations Platform.
