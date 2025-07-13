# Hospital Operations Platform - Contributing Guide

## Welcome Contributors! 🎉

Thank you for your interest in contributing to the Hospital Operations & Logistics Platform. This guide will help you get started with contributing to this important healthcare technology project.

## 📋 Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Workflow](#contribution-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Issue Guidelines](#issue-guidelines)
10. [Security Considerations](#security-considerations)

## Code of Conduct

### Our Pledge
We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
**Examples of behavior that contributes to creating a positive environment include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior include:**
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Getting Started

### Prerequisites
Before contributing, ensure you have:
- **Git** installed and configured
- **Node.js** 16+ for frontend development
- **Python** 3.9+ for backend development
- **Docker** for containerized development
- Basic understanding of React.js and FastAPI
- Familiarity with healthcare data privacy (HIPAA compliance)

### Project Overview
This platform manages critical hospital operations including:
- Supply inventory tracking and management
- Multi-location resource coordination
- Professional analytics and reporting
- Real-time alert systems
- Batch tracking and compliance

### First Time Contributors
1. **Star** the repository ⭐
2. **Fork** the repository to your GitHub account
3. **Clone** your fork locally
4. **Set up** the development environment
5. **Pick** a "good first issue" to work on

## Development Setup

### Local Environment Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Hospital-Operations-Logistics-Agentic-Platform_.git
cd Hospital-Operations-Logistics-Agentic-Platform_

# Add upstream remote
git remote add upstream https://github.com/nazifmhd/Hospital-Operations-Logistics-Agentic-Platform_.git
```

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
cd api
python main.py
```

### Frontend Setup
```bash
cd dashboard

# Install dependencies
npm install

# Start development server
npm start
```

### Docker Development
```bash
# Build and run entire stack
docker-compose up --build

# Run specific services
docker-compose up frontend backend
```

### Environment Variables
Create `.env` files for local development:

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:8001
REACT_APP_WS_URL=ws://localhost:8001/ws
REACT_APP_ENV=development
```

**Backend (.env)**
```env
DEBUG=true
API_HOST=localhost
API_PORT=8001
CORS_ORIGINS=["http://localhost:3000"]
```

## Contribution Workflow

### 1. Planning Your Contribution
Before starting work:
- **Check existing issues** for similar work
- **Create or comment** on relevant issues
- **Discuss** major changes with maintainers
- **Fork** the repository if you haven't already

### 2. Creating a Feature Branch
```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Making Changes
- **Write clear commit messages**
- **Keep commits atomic** (one logical change per commit)
- **Test your changes** thoroughly
- **Update documentation** as needed

### 4. Commit Guidelines
```bash
# Good commit message format
git commit -m "feat: add inventory batch tracking functionality

- Implement batch number tracking for medical supplies
- Add expiry date monitoring with alerts
- Update UI components for batch display
- Add unit tests for batch management

Closes #123"
```

**Commit Message Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 5. Pushing Changes
```bash
# Push to your fork
git push origin feature/your-feature-name
```

## Coding Standards

### JavaScript/React Standards
```javascript
// Use functional components with hooks
const InventoryItem = ({ item, onUpdate }) => {
    const [isEditing, setIsEditing] = useState(false);
    
    // Clear function names
    const handleStockUpdate = async (newStock) => {
        try {
            await onUpdate(item.id, newStock);
            setIsEditing(false);
        } catch (error) {
            console.error('Failed to update stock:', error);
        }
    };
    
    return (
        <div className="inventory-item">
            {/* JSX content */}
        </div>
    );
};

// PropTypes for type checking
InventoryItem.propTypes = {
    item: PropTypes.object.isRequired,
    onUpdate: PropTypes.func.isRequired
};
```

### Python/FastAPI Standards
```python
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

# Type hints for all functions
async def get_inventory_items(
    category: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
) -> List[InventoryItem]:
    """
    Retrieve inventory items with optional filtering.
    
    Args:
        category: Filter by item category
        location: Filter by storage location
        limit: Maximum number of items to return
        
    Returns:
        List of inventory items matching criteria
        
    Raises:
        HTTPException: If database query fails
    """
    try:
        return await inventory_service.get_items(
            category=category,
            location=location,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve inventory: {str(e)}"
        )

# Pydantic models for data validation
class InventoryItemCreate(BaseModel):
    name: str
    category: str
    initial_stock: int = 0
    minimum_threshold: int = 0
    location: str
    unit_cost: float
    supplier: str
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Surgical Gloves",
                "category": "Medical Supplies",
                "initial_stock": 100,
                "minimum_threshold": 20,
                "location": "Storage Room A",
                "unit_cost": 12.50,
                "supplier": "MedSupply Corp"
            }
        }
```

### CSS/Styling Standards
```css
/* Use Tailwind CSS utility classes */
.inventory-table {
    @apply w-full bg-white shadow-md rounded-lg overflow-hidden;
}

.alert-critical {
    @apply bg-red-100 border-red-500 text-red-700 px-4 py-3 rounded;
}

/* Custom components when utilities aren't sufficient */
.loading-spinner {
    @apply inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600;
}
```

### Database Standards
```sql
-- Use descriptive table and column names
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    minimum_threshold INTEGER NOT NULL DEFAULT 0,
    location VARCHAR(100) NOT NULL,
    expiry_date DATE,
    unit_cost DECIMAL(10,2) NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add proper indexes
CREATE INDEX idx_inventory_category ON inventory_items(category);
CREATE INDEX idx_inventory_location ON inventory_items(location);
CREATE INDEX idx_inventory_expiry ON inventory_items(expiry_date);
```

## Testing Guidelines

### Frontend Testing
```javascript
// Component testing with React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InventoryTable from '../InventoryTable';

describe('InventoryTable', () => {
    const mockItems = [
        {
            id: 1,
            name: 'Surgical Gloves',
            current_stock: 45,
            minimum_threshold: 50,
            location: 'Storage Room A'
        }
    ];
    
    test('displays inventory items correctly', () => {
        render(<InventoryTable items={mockItems} />);
        
        expect(screen.getByText('Surgical Gloves')).toBeInTheDocument();
        expect(screen.getByText('45')).toBeInTheDocument();
        expect(screen.getByText('Storage Room A')).toBeInTheDocument();
    });
    
    test('handles stock update', async () => {
        const mockOnUpdate = jest.fn();
        render(
            <InventoryTable 
                items={mockItems} 
                onUpdateStock={mockOnUpdate} 
            />
        );
        
        const updateButton = screen.getByText('Update');
        fireEvent.click(updateButton);
        
        await waitFor(() => {
            expect(mockOnUpdate).toHaveBeenCalledWith(1, expect.any(Number));
        });
    });
});
```

### Backend Testing
```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestInventoryAPI:
    def test_get_inventory_items(self):
        """Test retrieving inventory items."""
        response = client.get("/api/v1/inventory")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_create_inventory_item(self):
        """Test creating new inventory item."""
        item_data = {
            "name": "Test Item",
            "category": "Test Category",
            "initial_stock": 100,
            "minimum_threshold": 20,
            "location": "Test Location",
            "unit_cost": 10.0,
            "supplier": "Test Supplier"
        }
        
        response = client.post("/api/v1/inventory", json=item_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["current_stock"] == 100
    
    def test_update_nonexistent_item(self):
        """Test updating non-existent item returns 404."""
        response = client.put(
            "/api/v1/inventory/99999",
            json={"current_stock": 50}
        )
        
        assert response.status_code == 404
```

### Running Tests
```bash
# Frontend tests
cd dashboard
npm test                    # Run all tests
npm test -- --coverage     # Run with coverage
npm test -- --watch        # Run in watch mode

# Backend tests
cd backend
python -m pytest                           # Run all tests
python -m pytest --cov=api                # Run with coverage
python -m pytest tests/test_inventory.py  # Run specific test file
```

## Documentation

### Code Documentation
```python
def calculate_reorder_quantity(
    current_stock: int,
    minimum_threshold: int,
    average_daily_usage: float,
    lead_time_days: int,
    safety_factor: float = 1.2
) -> int:
    """
    Calculate optimal reorder quantity for inventory item.
    
    Uses a modified EOQ (Economic Order Quantity) model adapted for
    hospital supply management with safety stock considerations.
    
    Args:
        current_stock: Current quantity in inventory
        minimum_threshold: Minimum stock level before reordering
        average_daily_usage: Average daily consumption rate
        lead_time_days: Supplier lead time in days
        safety_factor: Safety multiplier for uncertainty (default 1.2)
        
    Returns:
        Recommended order quantity
        
    Example:
        >>> calculate_reorder_quantity(20, 50, 5.5, 7, 1.3)
        85
    """
    # Calculate safety stock
    safety_stock = average_daily_usage * lead_time_days * safety_factor
    
    # Calculate optimal order quantity
    optimal_stock = minimum_threshold + safety_stock
    reorder_quantity = max(0, optimal_stock - current_stock)
    
    return int(reorder_quantity)
```

### API Documentation
Use OpenAPI/Swagger documentation:
```python
@router.post(
    "/inventory",
    response_model=InventoryItem,
    status_code=201,
    summary="Create new inventory item",
    description="Add a new item to the hospital inventory system",
    responses={
        201: {"description": "Item created successfully"},
        400: {"description": "Invalid item data"},
        409: {"description": "Item already exists"}
    }
)
async def create_inventory_item(item: InventoryItemCreate):
    """
    Create a new inventory item with the following information:
    
    - **name**: Item name (required)
    - **category**: Supply category (required)  
    - **initial_stock**: Starting quantity (default: 0)
    - **minimum_threshold**: Reorder threshold (default: 0)
    - **location**: Storage location (required)
    - **unit_cost**: Cost per unit (required)
    - **supplier**: Supplier information (required)
    """
    pass
```

## Pull Request Process

### Before Submitting
1. **Sync with upstream** to avoid conflicts
2. **Run all tests** and ensure they pass
3. **Update documentation** if needed
4. **Check code style** with linters
5. **Verify HIPAA compliance** for any health data changes

### Pull Request Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Cross-browser testing (if UI changes)

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Security Considerations
- [ ] No sensitive data is exposed
- [ ] HIPAA compliance maintained
- [ ] Input validation implemented
- [ ] Authorization checks in place
```

### Review Process
1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Security review** for sensitive changes
4. **Manual testing** by reviewer
5. **Approval and merge** by maintainer

## Issue Guidelines

### Creating Issues

#### Bug Reports
```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, macOS Big Sur]
 - Browser [e.g. chrome, safari]
 - Version [e.g. 22]

**Additional Context**
Add any other context about the problem here.
```

#### Feature Requests
```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation Ideas**
If you have ideas about how this could be implemented, please share them.
```

### Issue Labels
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: High priority issue
- `security`: Security-related issue
- `performance`: Performance improvement
- `accessibility`: Accessibility improvement

## Security Considerations

### HIPAA Compliance
When working with healthcare data:
- **No PHI** (Protected Health Information) in code or logs
- **Encrypt** sensitive data at rest and in transit
- **Audit logging** for all data access
- **Access controls** based on user roles
- **Data retention** policies compliance

### Security Best Practices
```python
# Example: Secure data handling
from cryptography.fernet import Fernet
import os

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data before storage."""
    key = os.getenv('ENCRYPTION_KEY').encode()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data for authorized access."""
    key = os.getenv('ENCRYPTION_KEY').encode()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
```

### Security Checklist
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure authentication
- [ ] Proper authorization
- [ ] Sensitive data encryption
- [ ] Secure communication (HTTPS)
- [ ] Error handling without information disclosure

## Recognition

### Contributors
We recognize and appreciate all contributions:
- **Code contributors** are listed in CONTRIBUTORS.md
- **Issue reporters** help improve the platform
- **Documentation writers** make the project accessible
- **Reviewers** ensure code quality

### Hall of Fame
Special recognition for significant contributions:
- Major feature implementations
- Critical bug fixes
- Security improvements
- Documentation overhauls

## Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: security@hospital.com (security issues only)
- **Documentation**: Comprehensive guides in `/docs`

### Resources
- [React Documentation](https://reactjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/index.html)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

Thank you for contributing to the Hospital Operations & Logistics Platform! Your contributions help improve healthcare operations and patient care. 🏥❤️

*Last updated: July 13, 2025*
