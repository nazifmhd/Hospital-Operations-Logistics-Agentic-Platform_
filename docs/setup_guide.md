# Hospital Supply Inventory Agent - Setup and Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **Python**: Version 3.9 or higher
- **Node.js**: Version 16 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: Minimum 10GB free space

### Required Software
- Git
- Python 3.9+
- Node.js 16+
- npm or yarn
- PostgreSQL (optional for production)
- Redis (optional for production)

## Quick Start Guide

### 1. Clone the Repository
```powershell
git clone https://github.com/your-org/Hospital-Operations-Logistics-Agentic-Platform_.git
cd Hospital-Operations-Logistics-Agentic-Platform_
```

### 2. Backend Setup

#### Install Python Dependencies
```powershell
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: The requirements.txt has been optimized to avoid conflicts with Python's built-in modules (logging, datetime, asyncio are part of Python standard library).

#### Start the Backend Server
```powershell
# Navigate to the API directory
cd api

# Start the FastAPI server
python main.py
```

The backend server will start on `http://localhost:8000`

### 3. Frontend Setup

#### Install Node.js Dependencies
```powershell
# Open a new terminal window
cd dashboard/supply_dashboard
npm install
```

#### Start the React Development Server
```powershell
npm start
```

The frontend will start on `http://localhost:3000`

## Detailed Setup Instructions

### Backend Configuration

#### Environment Variables
Create a `.env` file in the `backend/api` directory:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Database Configuration (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_supply
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]
```

#### Database Setup (Production)
```powershell
# Install PostgreSQL and Redis
# For development, the agent uses in-memory storage

# Create database
createdb hospital_supply

# Run migrations (when implemented)
# python manage.py migrate
```

### Frontend Configuration

#### Environment Variables
Create a `.env` file in the `dashboard/supply_dashboard` directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_ENVIRONMENT=development
```

#### Build for Production
```powershell
cd dashboard/supply_dashboard
npm run build
```

## Running the Application

### Development Mode
1. Start the backend server:
   ```powershell
   cd backend/api
   python main.py
   ```

2. Start the frontend development server:
   ```powershell
   cd dashboard/supply_dashboard
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

### Production Deployment

#### Using Docker (Recommended)
```powershell
# Build and run with Docker Compose
docker-compose up -d
```

#### Manual Deployment
1. Build the frontend:
   ```powershell
   cd dashboard/supply_dashboard
   npm run build
   ```

2. Deploy the backend with a production WSGI server:
   ```powershell
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

## Testing the Installation

### Backend Health Check
```powershell
# Test API health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-12T10:30:00Z",
  "agent_running": true
}
```

### Frontend Access
1. Open `http://localhost:3000` in your browser
2. You should see the Supply Inventory Dashboard
3. Check that real-time data is loading

### WebSocket Connection
1. Open browser developer tools
2. Check the Network tab for WebSocket connections
3. Verify real-time updates are working

## Configuration Options

### Agent Configuration
Modify `agents/supply_inventory_agent/supply_agent.py`:
```python
# Monitoring frequency (seconds)
MONITORING_INTERVAL = 60

# Alert thresholds
LOW_STOCK_THRESHOLD = 0.2  # 20% of max capacity
EXPIRY_WARNING_DAYS = 30

# Usage pattern analysis
USAGE_HISTORY_DAYS = 30
```

### Dashboard Configuration
Modify `dashboard/supply_dashboard/src/context/SupplyDataContext.js`:
```javascript
// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Update frequency (milliseconds)
const UPDATE_INTERVAL = 5000;

// WebSocket reconnection settings
const WS_RECONNECT_DELAY = 5000;
```

## Troubleshooting

### Common Issues

#### Backend Issues
1. **Import errors**: Ensure all dependencies are installed
   ```powershell
   pip install -r requirements.txt
   ```

2. **Port already in use**: Change the port in `main.py`
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

3. **CORS errors**: Check CORS configuration in `main.py`

#### Frontend Issues
1. **Node modules errors**: Delete and reinstall
   ```powershell
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **API connection issues**: Check the API URL in `.env`

3. **WebSocket connection failed**: Ensure backend is running

#### Performance Issues
1. **Slow loading**: Check network connectivity
2. **High memory usage**: Reduce monitoring frequency
3. **Database errors**: Check database connection settings

### Logs and Debugging

#### Backend Logs
- Logs are output to console by default
- Check for agent initialization messages
- Monitor WebSocket connection logs

#### Frontend Debugging
- Open browser developer tools
- Check Console for JavaScript errors
- Monitor Network tab for API calls

### Getting Help
1. Check the [documentation](./docs/)
2. Review [common issues](./docs/troubleshooting.md)
3. Contact the development team
4. Submit issues on GitHub

## Next Steps

### Initial Configuration
1. **Review sample data**: Check the inventory items in the agent
2. **Configure alerts**: Adjust thresholds for your needs
3. **Set up users**: Configure role-based access
4. **Integrate systems**: Connect to existing hospital systems

### Training
1. **Admin training**: System configuration and management
2. **User training**: Daily operations and workflows
3. **Support training**: Troubleshooting and maintenance

### Production Readiness
1. **Security review**: Implement authentication and authorization
2. **Performance testing**: Load test with expected user volume
3. **Backup strategy**: Set up automated backups
4. **Monitoring**: Configure system monitoring and alerts

## Features Overview

### Current Features
- ✅ Real-time inventory monitoring
- ✅ Automated alert generation
- ✅ Procurement recommendations
- ✅ Interactive dashboard
- ✅ Usage analytics
- ✅ WebSocket real-time updates

### Planned Features
- 🔄 User authentication
- 🔄 Database persistence
- 🔄 Email notifications
- 🔄 Advanced analytics
- 🔄 Mobile responsiveness
- 🔄 Integration APIs

## Support

For technical support or questions:
- **Documentation**: Check the docs folder
- **Issues**: Submit GitHub issues
- **Email**: support@hospital-supply-platform.com
- **Training**: Schedule training sessions
