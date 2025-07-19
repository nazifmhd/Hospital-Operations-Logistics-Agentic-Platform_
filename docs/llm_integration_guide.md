# LLM Integration Guide - Hospital Supply Platform

## 🚀 Quick Start with Gemini API

### Prerequisites
1. Google Cloud Account or Google AI Studio access
2. Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Python environment with required packages

### Installation

```bash
# Install required dependencies
pip install google-generativeai python-dotenv

# Install from requirements file
pip install -r ai_ml/requirements.txt
```

### Configuration

1. **Set up environment variables in `.env` file:**
```env
GEMINI_API_KEY=your_actual_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.3
HOSPITAL_NAME=Your Hospital Name
HOSPITAL_TYPE=General Acute Care
```

2. **Run the setup script:**
```bash
python ai_ml/setup_gemini.py
```

3. **Verify integration:**
```bash
# The setup script will automatically test:
# - API connection
# - Hospital context understanding
# - Performance benchmarks
```

## 🎯 Features Enabled

### Natural Language Queries
Users can now ask questions in plain English:
- *"What items are critically low in the ICU?"*
- *"Show me purchase orders that need approval"*
- *"Explain why this alert was triggered"*
- *"What's the cost impact of current shortages?"*

### Intelligent Analysis
- **Purchase Order Justification**: AI-generated business cases
- **Inventory Health Assessment**: Smart priority categorization
- **Risk Analysis**: Predictive impact assessments
- **Cost Optimization**: AI-driven savings recommendations

### Smart Alerts
- **Context-Aware Messages**: Role-specific notifications
- **Actionable Insights**: Clear next steps and escalation paths
- **Impact Assessment**: Patient care and operational implications

## 🔧 API Endpoints

### Chat Interface
```javascript
POST /api/v2/llm/query
{
  "query": "Show me critical inventory alerts",
  "context": { "user_role": "supply_manager" },
  "user_role": "supply_manager"
}
```

### Purchase Order Analysis
```javascript
POST /api/v2/llm/analyze-purchase-order
{
  "data": { "id": "PO-001", "items": [...] },
  "analysis_type": "purchase_order_justification",
  "context": { "department": "ICU", "urgency": "high" }
}
```

### Dashboard Enhancement
```javascript
POST /api/v2/llm/enhance-dashboard
// Returns dashboard data with AI insights
```

### Alert Generation
```javascript
POST /api/v2/llm/generate-alert-narrative
{
  "data": { "item": "N95 Masks", "level": "critical" },
  "context": { "department": "ICU", "patient_load": "high" }
}
```

## 🏥 Hospital-Specific Optimization

### Context Management
The system understands:
- **Hospital departments**: ICU, OR, ED, Pharmacy, etc.
- **Medical supplies**: N95s, IV fluids, medications, etc.
- **Compliance standards**: Joint Commission, CMS, OSHA
- **Clinical workflows**: Patient safety, infection control

### Terminology Training
AI responses use appropriate medical terminology:
- Clinical supply names and specifications
- Healthcare regulatory language
- Professional communication standards
- Department-specific context

## 📊 Performance Monitoring

### Metrics Tracked
- Response time and accuracy
- User satisfaction scores
- Confidence levels
- Usage patterns
- Error rates

### Quality Assurance
- Confidence thresholds for response quality
- Fallback responses for low-confidence scenarios
- Caching for improved performance
- Rate limiting for API protection

## 🔒 Security & Compliance

### Data Protection
- No patient data sent to external APIs
- Inventory and operational data only
- API key encryption and secure storage
- Audit trails for all AI interactions

### Compliance Features
- HIPAA-aware data handling
- Regulatory requirement awareness
- Professional communication standards
- Quality assurance protocols

## 🛠 Troubleshooting

### Common Issues

1. **API Key Not Working**
```bash
# Check API key validity
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('Valid')"
```

2. **Low Response Quality**
```env
# Adjust temperature for more/less creative responses
LLM_TEMPERATURE=0.1  # More focused
LLM_TEMPERATURE=0.5  # More creative
```

3. **Performance Issues**
```env
# Enable caching
LLM_ENABLE_CACHING=true
LLM_CACHE_TTL=300
```

### Debug Mode
```env
DEBUG_LLM=true
LOG_LLM_INTERACTIONS=true
```

## 📈 Advanced Configuration

### Custom Prompts
Modify hospital-specific context in `HospitalContextManager`:
```python
self.hospital_context = {
    "name": "Your Hospital Name",
    "type": "Specialty Hospital",
    "departments": ["Custom", "Department", "List"],
    "critical_supplies": ["Hospital", "Specific", "Items"]
}
```

### Performance Tuning
```env
LLM_MAX_TOKENS=4096          # Response length
LLM_CONFIDENCE_THRESHOLD=0.7  # Quality threshold
LLM_RATE_LIMIT_REQUESTS=60   # API rate limiting
```

## 🔄 Integration Examples

### Frontend Usage
```javascript
// Chat interface
import LLMChatInterface from './components/LLMChatInterface';

// Floating assistant
import FloatingAIAssistant from './components/FloatingAIAssistant';

// Purchase order analysis
import LLMPurchaseOrderAnalysis from './components/LLMPurchaseOrderAnalysis';
```

### Backend Integration
```python
from ai_ml.llm_integration import LLMIntegrationService

service = LLMIntegrationService()
response = await service.process_natural_language_command(
    "Show critical alerts", user_context
)
```

## 🚀 Production Deployment

### Environment Setup
1. Set production API keys
2. Configure hospital-specific context
3. Enable monitoring and logging
4. Set up caching infrastructure
5. Configure rate limiting

### Monitoring Dashboard
- Track API usage and costs
- Monitor response quality
- User satisfaction metrics
- Performance analytics

## 📞 Support

### Getting Help
- Check logs in `llm_interactions.log`
- Review performance metrics via `/api/v2/llm/status`
- Use fallback responses when AI unavailable
- Contact support for API issues

### Best Practices
- Keep prompts hospital-specific
- Monitor confidence scores
- Implement proper error handling
- Regular performance reviews
- User feedback collection

---

**Ready to enhance your hospital supply chain with AI intelligence!** 🧠✨
