# Hospital Operations & Logistics Platform - Setup and Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **Python**: Version 3.9 or higher
- **Node.js**: Version 16 or higher
- **RAM**: Minimum 8GB (16GB recommended for production)
- **Storage**: Minimum 20GB free space
- **Network**: Stable internet connection

### Required Software
- **Git**: For version control
- **Python 3.9+**: Backend development
- **Node.js 16+**: Frontend development
- **npm or yarn**: Package management
- **Docker** (optional): Containerized deployment
- **PostgreSQL** (optional): Production database
- **Redis** (optional): Caching and real-time features

## 🚀 Quick Start Guide

### Method 1: Docker Deployment (Recommended)

#### 1. Clone the Repository
```powershell
git clone https://github.com/nazifmhd/Hospital-Operations-Logistics-Agentic-Platform_.git
cd Hospital-Operations-Logistics-Agentic-Platform_
```

#### 2. Start with Docker Compose
```powershell
# Build and start all services
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d
```

#### 3. Access the Application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

### Method 2: Manual Installation

#### 1. Clone the Repository
```powershell
git clone https://github.com/nazifmhd/Hospital-Operations-Logistics-Agentic-Platform_.git
cd Hospital-Operations-Logistics-Agentic-Platform_
```

#### 2. Backend Setup

##### Install Python Dependencies
```powershell
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

##### Start the Backend Server
```powershell
# Navigate to the API directory
cd api

# Start the FastAPI server
python main.py
```

The backend server will start on `http://localhost:8001`

#### 3. Frontend Setup

```powershell
cd dashboard

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🔧 Development Environment Setup

### Environment Variables

#### Frontend Environment (.env)
Create a `.env` file in the `dashboard/` directory:
```env
REACT_APP_API_URL=http://localhost:8001
REACT_APP_WS_URL=ws://localhost:8001/ws
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
```

#### Backend Environment (.env)
Create a `.env` file in the `backend/` directory:
```env
# API Configuration
DEBUG=true
API_HOST=localhost
API_PORT=8001
CORS_ORIGINS=["http://localhost:3000"]

# Database (optional for development)
DATABASE_URL=sqlite:///./hospital_ops.db

# Security
SECRET_KEY=your-development-secret-key
JWT_ALGORITHM=HS256

# Agent Configuration
AGENT_UPDATE_INTERVAL=30
ENABLE_REAL_TIME_UPDATES=true
```

## 🧪 Testing the Installation

### Health Checks
After installation, verify the setup:

1. **Backend Health Check**:
   ```
   GET http://localhost:8001/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-07-13T10:30:00Z",
     "version": "1.0.0"
   }
   ```

2. **Frontend Access**: Navigate to http://localhost:3000
   - Should display the main dashboard
   - All navigation links should work
   - Real-time updates should be functional

3. **API Documentation**: Visit http://localhost:8001/docs
   - Interactive Swagger UI should load
   - All endpoints should be documented

### Feature Testing

#### Dashboard Pages Verification
Test all 9 pages of the platform:

1. **Main Dashboard** (`/`): 
   - Real-time metrics display
   - Navigation links functional
   - Recent activity updates

2. **Analytics** (`/analytics`):
   - Inventory overview charts
   - Consumption trends
   - Cost analysis data

3. **Alerts** (`/alerts`):
   - Alert list with priorities
   - Resolution functionality
   - Filter capabilities

4. **Inventory** (`/inventory`):
   - Item listing and search
   - Stock level updates
   - Category filtering

5. **Professional Dashboard** (`/professional`):
   - Executive metrics
   - Quick actions modal
   - Management insights

6. **Multi-Location** (`/multi-location`):
   - 6 location display
   - Transfer functionality
   - Location-specific metrics

7. **Batch Management** (`/batch-management`):
   - Batch tracking information
   - Expiry monitoring
   - Compliance data

8. **User Management** (`/user-management`):
   - User accounts display
   - Role management
   - Activity tracking

9. **Settings** (`/settings`):
   - Configuration options
   - System preferences
   - Notification settings

## 🛠️ Troubleshooting

### Common Issues

#### Backend Won't Start
```
Error: Address already in use
```
**Solution**: Change port or kill existing process:
```powershell
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

#### Frontend Build Errors
```
Module not found: Can't resolve 'module-name'
```
**Solution**: Clear cache and reinstall:
```powershell
rm -rf node_modules package-lock.json
npm install
```

#### CORS Errors
```
Access blocked by CORS policy
```
**Solution**: Verify CORS settings in backend `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Docker Issues
```
Error: Cannot connect to the Docker daemon
```
**Solution**: Ensure Docker is running:
```powershell
# Windows: Start Docker Desktop
# Linux: sudo systemctl start docker
```

## 🚀 Production Deployment

### Using Docker (Recommended)

#### Production Docker Compose
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=https://api.yourhospital.com
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://user:pass@db:5432/hospital_ops
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=hospital_ops
      - POSTGRES_USER=hospital_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Manual Production Setup

#### Production Backend
```bash
cd backend

# Create production virtual environment
python3.9 -m venv prod_venv
source prod_venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

# Run with Gunicorn
cd api
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

#### Production Frontend
```bash
cd dashboard

# Install dependencies
npm ci --only=production

# Build for production
npm run build

# Serve with nginx
sudo cp -r build/* /var/www/html/
```

## 🔒 Security Configuration

### Development Security
- Use environment variables for sensitive data
- Enable CORS only for development domains
- Implement proper authentication
- Use HTTPS in production

### Production Security Checklist
- [ ] SSL/TLS certificates configured
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] CORS origins restricted
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] Error handling without information disclosure

## 📊 Performance Optimization

### Backend Optimization
```python
# Use async/await for I/O operations
# Implement connection pooling for databases
# Use caching for frequent queries
# Enable compression middleware
```

### Frontend Optimization
```javascript
// Use React.memo for expensive components
// Implement lazy loading for routes
// Optimize bundle size with code splitting
// Use React.useMemo for expensive calculations
```

## 🎯 Next Steps

After successful installation:

1. **Explore the Platform**: Navigate through all 9 dashboard pages
2. **Review Documentation**: Check out the [User Guide](./user_guide.md) and [API Documentation](./api_documentation.md)
3. **Customize Configuration**: Adjust settings for your hospital's needs
4. **Set Up Monitoring**: Implement logging and alerting
5. **Plan Deployment**: Prepare for production deployment using the [Deployment Guide](./deployment_guide.md)
6. **Train Users**: Educate staff on platform features

### Additional Resources
- [User Guide](./user_guide.md) - Detailed feature documentation
- [API Documentation](./api_documentation.md) - Complete API reference
- [Architecture Guide](./architecture.md) - Technical details
- [Contributing Guide](./contributing.md) - Development guidelines
- [Project Structure](./project_structure.md) - Codebase organization

---

*Last updated: July 13, 2025*

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
