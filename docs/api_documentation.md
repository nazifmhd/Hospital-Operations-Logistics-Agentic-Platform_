# Hospital Operations & Logistics Platform - API Documentation

## Overview
This document provides comprehensive API documentation for the Hospital Operations & Logistics Platform backend services.

## Base URLs
- **Development**: `http://localhost:8001`
- **Production**: `https://api.hospital-ops.com`

## Authentication
Currently using development mode. Production deployment will implement:
- JWT token-based authentication
- Role-based access control (RBAC)
- HIPAA-compliant security measures

## API Endpoints

### Health Check
```http
GET /health
```
**Description**: Check API health status
**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2025-07-13T10:30:00Z",
    "version": "1.0.0"
}
```

### Supply Inventory Management

#### Get All Inventory Items
```http
GET /inventory
```
**Description**: Retrieve all inventory items with current stock levels
**Response**:
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "Surgical Gloves",
            "category": "Medical Supplies",
            "current_stock": 45,
            "minimum_threshold": 50,
            "location": "Storage Room A",
            "expiry_date": "2025-12-15",
            "unit_cost": 12.50,
            "supplier": "MedSupply Corp",
            "last_updated": "2025-07-13T10:25:00Z"
        }
    ],
    "total_items": 18,
    "total_value": 15420.75
}
```

#### Update Inventory Item
```http
PUT /inventory/{item_id}
```
**Description**: Update inventory item details
**Parameters**:
- `item_id` (path): Integer - Item identifier
**Request Body**:
```json
{
    "current_stock": 75,
    "location": "Storage Room B",
    "notes": "Restocked after delivery"
}
```

#### Get Low Stock Alerts
```http
GET /alerts/low-stock
```
**Description**: Retrieve items below minimum threshold
**Response**:
```json
{
    "status": "success",
    "alerts": [
        {
            "item_id": 1,
            "item_name": "Surgical Gloves",
            "current_stock": 45,
            "minimum_threshold": 50,
            "priority": "Medium",
            "days_until_critical": 12,
            "recommended_order_quantity": 100
        }
    ],
    "total_alerts": 4
}
```

### Analytics Endpoints

#### Get Inventory Analytics
```http
GET /analytics/inventory
```
**Description**: Retrieve inventory analytics and insights
**Query Parameters**:
- `period` (optional): string - Time period (7d, 30d, 90d, 1y)
- `category` (optional): string - Filter by category
**Response**:
```json
{
    "status": "success",
    "period": "30d",
    "data": {
        "total_value": 15420.75,
        "consumption_rate": {
            "daily_average": 125.5,
            "weekly_trend": "+5.2%"
        },
        "category_breakdown": {
            "Medical Supplies": 8245.30,
            "Personal Protective Equipment": 3180.45,
            "Medications": 2995.00,
            "Cleaning Supplies": 1000.00
        },
        "cost_savings": {
            "bulk_purchase_opportunities": 2340.00,
            "expiry_prevention": 156.75
        }
    }
}
```

#### Get Usage Patterns
```http
GET /analytics/usage-patterns
```
**Description**: Analyze consumption patterns for forecasting

### Professional Dashboard Endpoints

#### Get Professional Overview
```http
GET /professional/overview
```
**Description**: Get comprehensive professional dashboard data
**Response**:
```json
{
    "status": "success",
    "data": {
        "critical_metrics": {
            "items_below_threshold": 4,
            "expiring_soon": 2,
            "total_inventory_value": 15420.75,
            "monthly_consumption": 12500.00
        },
        "recent_activities": [
            {
                "type": "stock_update",
                "item": "Surgical Masks",
                "action": "Restocked",
                "quantity": 200,
                "timestamp": "2025-07-13T09:15:00Z",
                "user": "John Smith"
            }
        ],
        "quick_actions": {
            "pending_orders": 3,
            "approval_required": 1,
            "emergency_requests": 0
        }
    }
}
```

### Multi-Location Management

#### Get All Locations
```http
GET /locations
```
**Description**: Retrieve all hospital locations and their inventory
**Response**:
```json
{
    "status": "success",
    "locations": [
        {
            "id": "main-hospital",
            "name": "Main Hospital",
            "type": "Primary Care",
            "total_items": 18,
            "total_value": 15420.75,
            "critical_alerts": 2,
            "status": "Operational"
        },
        {
            "id": "emergency-wing",
            "name": "Emergency Wing",
            "type": "Emergency Care",
            "total_items": 12,
            "total_value": 8750.25,
            "critical_alerts": 1,
            "status": "Operational"
        }
    ]
}
```

#### Transfer Items Between Locations
```http
POST /locations/transfer
```
**Description**: Transfer inventory between locations
**Request Body**:
```json
{
    "item_id": 1,
    "from_location": "main-hospital",
    "to_location": "emergency-wing",
    "quantity": 25,
    "reason": "Emergency restocking",
    "requested_by": "Jane Doe"
}
```

### Batch Management

#### Get Batch Information
```http
GET /batches
```
**Description**: Retrieve batch tracking information
**Response**:
```json
{
    "status": "success",
    "batches": [
        {
            "batch_id": "BATCH001",
            "item_name": "Surgical Gloves",
            "quantity": 500,
            "expiry_date": "2025-12-15",
            "supplier": "MedSupply Corp",
            "received_date": "2025-06-15",
            "status": "Active",
            "remaining_quantity": 455
        }
    ]
}
```

### User Management

#### Get Users
```http
GET /users
```
**Description**: Retrieve system users (Admin access required)
**Response**:
```json
{
    "status": "success",
    "users": [
        {
            "id": 1,
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@hospital.com",
            "role": "Admin",
            "department": "Administration",
            "status": "Active",
            "last_login": "2025-07-13T08:30:00Z"
        }
    ]
}
```

## Error Handling

### Error Response Format
```json
{
    "status": "error",
    "error_code": "ITEM_NOT_FOUND",
    "message": "The requested inventory item was not found",
    "timestamp": "2025-07-13T10:30:00Z",
    "request_id": "req_abc123"
}
```

### Common Error Codes
- `ITEM_NOT_FOUND` (404): Inventory item not found
- `INSUFFICIENT_STOCK` (400): Not enough stock for operation
- `VALIDATION_ERROR` (400): Invalid request data
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting
- **Development**: No limits
- **Production**: 1000 requests per hour per API key

## WebSocket Events
Real-time updates are available via WebSocket connection at `/ws`:

### Event Types
- `inventory_update`: Stock level changes
- `new_alert`: New alert generated
- `alert_resolved`: Alert resolution
- `batch_expiry_warning`: Batch expiration notifications

### Example WebSocket Message
```json
{
    "event": "inventory_update",
    "data": {
        "item_id": 1,
        "name": "Surgical Gloves",
        "previous_stock": 50,
        "current_stock": 45,
        "timestamp": "2025-07-13T10:30:00Z"
    }
}
```

## Development Notes
- All timestamps are in ISO 8601 format (UTC)
- Monetary values are in USD with 2 decimal places
- Stock quantities are integers
- All API responses include status field for consistency
