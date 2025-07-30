"""
LLM Integration Module for Hospital Supply Chain Platform
Enhances system intelligence with natural language processing capabilities
Real-time integration with OpenAI API
"""

import asyncio
import logging
import os
import time
import hashlib
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

# Production LLM Integration - OpenAI support
from dotenv import load_dotenv

# Try OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("⚠️ OpenAI not available, install with: pip install openai")

# Load environment variables - try multiple locations
load_dotenv()  # Try current directory first
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))  # Try parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))  # Try root directory

# Configure LLM APIs based on provider
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI
if OPENAI_API_KEY and OPENAI_AVAILABLE and LLM_PROVIDER == 'openai':
    openai.api_key = OPENAI_API_KEY
    OPENAI_CONFIGURED = True
    logging.info("✅ OpenAI API configured successfully")
else:
    OPENAI_CONFIGURED = False

# LLM Configuration status
LLM_CONFIGURED = OPENAI_CONFIGURED
logging.info(f"🤖 LLM Provider: {LLM_PROVIDER}, OpenAI: {OPENAI_CONFIGURED}")

# Import RAG and MCP systems
try:
    from rag_system import get_rag_system, enhance_with_rag, RAGContext
    from mcp_server import get_mcp_server, handle_mcp_request, MCPContext
    RAG_MCP_AVAILABLE = True
    logging.info("✅ RAG and MCP systems available")
except ImportError as e:
    RAG_MCP_AVAILABLE = False
    logging.warning(f"⚠️ RAG/MCP systems not available: {e}")

# Simple in-memory cache to reduce API calls
class LLMCache:
    """Simple cache to reduce repeated API calls"""
    
    def __init__(self, ttl_minutes: int = 30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[tuple]:
        """Get cached response if available and not expired"""
        key = self._get_cache_key(prompt)
        if key in self.cache:
            response, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logging.info("🎯 Using cached response")
                return response
            else:
                del self.cache[key]  # Remove expired entry
        return None
    
    def set(self, prompt: str, response: tuple):
        """Cache response"""
        key = self._get_cache_key(prompt)
        self.cache[key] = (response, datetime.now())
        
        # Simple cleanup - keep only last 100 entries
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

# Global cache instance
llm_cache = LLMCache(ttl_minutes=30)

class LLMProvider(Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    LOCAL_LLM = "local_llm"

@dataclass
class LLMResponse:
    content: str
    confidence: float
    reasoning: str
    suggestions: List[str]
    generated_at: datetime
    model_used: str = "gpt-3.5-turbo"
    tokens_used: Optional[int] = None

class HospitalContextManager:
    """
    Manages hospital-specific context and terminology for LLM interactions
    """
    
    def __init__(self):
        self.hospital_context = {
            "name": os.getenv('HOSPITAL_NAME', 'General Hospital'),
            "type": os.getenv('HOSPITAL_TYPE', 'General Acute Care'),
            "location": os.getenv('HOSPITAL_LOCATION', 'City, State'),
            "compliance_standards": os.getenv('COMPLIANCE_STANDARDS', '').split(','),
            "departments": [
                "Emergency Department (ED)", "Intensive Care Unit (ICU)", 
                "Operating Room (OR)", "Medical/Surgical Units", "Pharmacy",
                "Laboratory", "Radiology", "Physical Therapy", "Central Supply"
            ],
            "critical_supplies": [
                "N95 Respirators", "Surgical Masks", "Sterile Gloves", 
                "IV Fluids", "Syringes", "Oxygen", "Medications",
                "Blood Products", "Surgical Instruments", "PPE"
            ]
        }
    
    def get_system_prompt(self) -> str:
        """Generate hospital-specific system prompt"""
        return f"""
        You are an expert AI assistant specializing in hospital supply chain management for {self.hospital_context['name']}.
        
        HOSPITAL CONTEXT:
        - Type: {self.hospital_context['type']}
        - Location: {self.hospital_context['location']}
        - Compliance: {', '.join(self.hospital_context['compliance_standards'])}
        
        EXPERTISE AREAS:
        - Medical supply inventory management
        - Healthcare procurement processes
        - Patient safety and care continuity
        - Regulatory compliance (Joint Commission, CMS, OSHA)
        - Cost optimization in healthcare settings
        - Emergency preparedness and supply resilience
        
        COMMUNICATION STYLE:
        - Professional and precise
        - Patient safety-focused
        - Compliance-aware
        - Actionable recommendations
        - Clear urgency indicators
        
        Always consider patient care impact, regulatory requirements, and cost-effectiveness in your responses.
        """

class IntelligentSupplyAssistant:
    """
    LLM-powered assistant for intelligent supply chain decisions
    Supports OpenAI GPT API
    """
    
    def __init__(self, provider: str = None):
        self.provider = provider or LLM_PROVIDER
        self.conversation_history = []
        self.context_memory = {}
        self.context_manager = HospitalContextManager()
        self.model_config = {
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.3')),
            'max_output_tokens': int(os.getenv('LLM_MAX_TOKENS', '4096')),
        }
        
        # Initialize OpenAI
        if self.provider == 'openai' and OPENAI_CONFIGURED:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self.model_name = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
            self.model = None  # OpenAI uses client pattern
            logging.info(f"✅ Intelligent Supply Assistant initialized with OpenAI ({self.model_name})")
        else:
            self.model = None
            self.client = None
            logging.warning(f"⚠️ No LLM configured (Provider: {self.provider}, OpenAI: {OPENAI_CONFIGURED})")
    
    def _is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return (self.provider == 'openai' and self.client is not None)
    
    def _optimize_prompt_for_speed(self, prompt: str) -> str:
        """Optimize prompt for faster processing while maintaining quality"""
        # If prompt is too long, truncate intelligently
        if len(prompt) > 2000:
            # Keep system instructions and user query, truncate context
            lines = prompt.split('\n')
            user_query_start = -1
            context_start = -1
            
            for i, line in enumerate(lines):
                if 'User Query:' in line:
                    user_query_start = i
                elif 'Relevant Context:' in line:
                    context_start = i
                    break
            
            if context_start > 0 and user_query_start > 0:
                # Keep everything up to context, then limit context
                optimized_lines = lines[:context_start + 1]
                context_lines = lines[context_start + 1:]
                
                # Keep only first 10 lines of context
                optimized_lines.extend(context_lines[:10])
                if len(context_lines) > 10:
                    optimized_lines.append("... (context truncated for faster processing)")
                
                return '\n'.join(optimized_lines)
        
        return prompt

    async def _call_llm_api(self, prompt: str) -> tuple[str, float]:
        """
        Make API call to configured LLM (OpenAI) with error handling
        """
        if not self._is_configured():
            logging.warning("🔄 No LLM configured - using intelligent fallback")
            return self._get_fallback_response(prompt)

        try:
            # Optimize prompt for faster processing
            optimized_prompt = self._optimize_prompt_for_speed(prompt)
            
            if self.provider == 'openai' and self.client:
                return await self._call_openai_api(optimized_prompt)
            else:
                logging.warning("🔄 LLM not properly configured - using fallback")
                return self._get_fallback_response(prompt)
                
        except Exception as e:
            logging.error(f"❌ LLM API call failed: {e}")
            return self._get_fallback_response(prompt)

    async def _call_openai_api(self, prompt: str) -> tuple[str, float]:
        """Call OpenAI API with error handling"""
        try:
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.2)
            
            # Prepare messages
            messages = [
                {"role": "system", "content": self.context_manager.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            # Make API call with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=messages,
                    temperature=self.model_config['temperature'],
                    max_tokens=min(self.model_config['max_output_tokens'], 1024),
                    top_p=0.9
                ),
                timeout=15.0  # 15 second timeout for OpenAI
            )
            
            response_text = response.choices[0].message.content
            confidence = 0.95  # High confidence for successful API calls
            
            logging.info(f"✅ OpenAI API response received ({len(response_text)} chars)")
            return response_text, confidence
            
        except asyncio.TimeoutError:
            logging.error("⏱️ OpenAI API timeout - using fallback response")
            return self._get_fallback_response(prompt)
        except Exception as e:
            logging.error(f"❌ OpenAI API error: {e}")
            return self._get_fallback_response(prompt)

    def _estimate_confidence(self, response: str, prompt: str) -> float:
        """
        Estimate confidence based on response characteristics
        """
        confidence = 0.8  # Base confidence
        
        # Increase confidence for detailed responses
        if len(response) > 200:
            confidence += 0.1
        
        # Increase confidence for structured responses
        if any(marker in response.lower() for marker in ['•', '1.', '2.', 'recommendation:', 'analysis:']):
            confidence += 0.05
        
        # Decrease confidence for uncertain language
        uncertainty_words = ['might', 'could', 'possibly', 'perhaps', 'maybe']
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        confidence -= uncertainty_count * 0.02
        
        # Ensure confidence is within bounds
        return max(0.1, min(0.99, confidence))
    
    def _get_fallback_response(self, prompt: str) -> tuple[str, float]:
        """
        Provide intelligent fallback response when OpenAI API is unavailable
        """
        prompt_lower = prompt.lower()
        
        # Inventory status queries
        if any(word in prompt_lower for word in ['inventory', 'stock', 'supplies', 'levels']):
            return (
                "🏥 **INVENTORY STATUS OVERVIEW** (Offline Mode)\n\n"
                "🔴 **CRITICAL ALERTS:**\n"
                "• Monitor PPE supplies (N95 masks, surgical gloves)\n"
                "• Check medication expiration dates\n"
                "• Verify emergency equipment availability\n\n"
                "📊 **RECOMMENDATIONS:**\n"
                "• Review low-stock items in critical departments\n"
                "• Schedule procurement for high-usage items\n"
                "• Implement automated reorder points\n\n"
                "ℹ️ *AI assistant is currently in offline mode. For real-time analysis, please check your network connection.*",
                0.75
            )
        
        # Critical alerts queries
        elif any(word in prompt_lower for word in ['alert', 'critical', 'urgent', 'emergency']):
            return (
                "🚨 **CRITICAL ALERTS SUMMARY** (Offline Mode)\n\n"
                "⚠️ **HIGH PRIORITY:**\n"
                "• ICU supplies below safety threshold\n"
                "• Emergency medications need restocking\n"
                "• Surgical equipment maintenance due\n\n"
                "📋 **ACTION ITEMS:**\n"
                "• Contact suppliers for expedited delivery\n"
                "• Review safety stock levels\n"
                "• Update procurement schedules\n\n"
                "ℹ️ *Operating in offline mode. Connect to network for live alerts.*",
                0.70
            )
        
        # Purchase order queries
        elif any(word in prompt_lower for word in ['purchase', 'order', 'procurement', 'buying']):
            return (
                "📦 **PROCUREMENT GUIDANCE** (Offline Mode)\n\n"
                "💡 **BEST PRACTICES:**\n"
                "• Prioritize patient-critical items\n"
                "• Consider bulk purchasing for cost savings\n"
                "• Verify supplier certifications and compliance\n\n"
                "🔍 **APPROVAL WORKFLOW:**\n"
                "• Department head approval required\n"
                "• Budget verification needed\n"
                "• Quality assurance check mandatory\n\n"
                "ℹ️ *AI analysis unavailable offline. Please check network connectivity.*",
                0.65
            )
        
        # Department queries
        elif any(word in prompt_lower for word in ['department', 'icu', 'er', 'surgery', 'pharmacy']):
            return (
                "🏥 **DEPARTMENT ANALYSIS** (Offline Mode)\n\n"
                "📋 **DEPARTMENT PRIORITIES:**\n"
                "• ICU: Ventilator supplies, medications\n"
                "• ER: Trauma kits, diagnostic equipment\n"
                "• Surgery: Surgical instruments, anesthetics\n"
                "• Pharmacy: Controlled substances, antibiotics\n\n"
                "🎯 **FOCUS AREAS:**\n"
                "• Maintain 72-hour emergency stock\n"
                "• Monitor high-turnover items\n"
                "• Ensure regulatory compliance\n\n"
                "ℹ️ *Limited offline analysis. Full insights available when connected.*",
                0.68
            )
        
        # Cost/efficiency queries
        elif any(word in prompt_lower for word in ['cost', 'budget', 'efficiency', 'optimization']):
            return (
                "💰 **COST OPTIMIZATION TIPS** (Offline Mode)\n\n"
                "📈 **SAVINGS OPPORTUNITIES:**\n"
                "• Negotiate bulk purchase agreements\n"
                "• Implement just-in-time inventory\n"
                "• Reduce waste through better forecasting\n\n"
                "🎯 **EFFICIENCY MEASURES:**\n"
                "• Automate reorder processes\n"
                "• Track usage patterns\n"
                "• Standardize supplier relationships\n\n"
                "ℹ️ *Operating offline. Connect for detailed cost analysis.*",
                0.72
            )
        
        # General help or unknown queries
        else:
            return (
                "🤖 **HOSPITAL SUPPLY ASSISTANT** (Offline Mode)\n\n"
                "✅ **AVAILABLE SERVICES:**\n"
                "• Inventory status monitoring\n"
                "• Critical alerts management\n"
                "• Purchase order recommendations\n"
                "• Department-specific guidance\n"
                "• Cost optimization strategies\n\n"
                "💡 **HOW TO USE:**\n"
                "Try asking about:\n"
                "• 'What supplies are running low?'\n"
                "• 'Show me critical alerts'\n"
                "• 'Help with purchase orders'\n"
                "• 'Department inventory status'\n\n"
                "🔗 **CONNECTIVITY:** Currently operating in offline mode. "
                "Please check your internet connection for full AI capabilities.",
                0.60
            )
    
    async def analyze_inventory_situation(self, inventory_data: Dict, context: Dict) -> LLMResponse:
        """
        Provide intelligent analysis of inventory situation with recommendations
        """
        
        prompt = f"""
        HOSPITAL SUPPLY CHAIN ANALYSIS REQUEST
        
        INVENTORY DATA:
        {json.dumps(inventory_data, indent=2)}
        
        HOSPITAL CONTEXT:
        - Hospital Type: {context.get('hospital_type', self.context_manager.hospital_context['type'])}
        - Current Season: {context.get('season', 'Current')}
        - Patient Load: {context.get('patient_load', 'Normal')}
        - Budget Status: {context.get('budget_status', 'Normal')}
        - Emergency Preparedness Level: {context.get('emergency_level', 'Standard')}
        
        REQUIRED ANALYSIS:
        1. **CRITICAL INVENTORY ASSESSMENT**: Identify items requiring immediate action
        2. **PATIENT CARE IMPACT**: Assess potential impact on patient safety and care quality
        3. **COMPLIANCE CONSIDERATIONS**: Address regulatory requirements and standards
        4. **PROCUREMENT STRATEGY**: Recommend optimal ordering approach and timing
        5. **COST OPTIMIZATION**: Identify opportunities for cost savings and efficiency
        6. **RISK MITIGATION**: Provide contingency planning for critical shortages
        
        FORMAT RESPONSE AS:
        🔴 CRITICAL ALERTS: [Items requiring immediate action]
        🟡 ATTENTION NEEDED: [Items to monitor closely]
        ✅ OPTIMAL LEVELS: [Well-stocked items]
        💡 RECOMMENDATIONS: [Specific, actionable steps]
        ⚠️ RISK FACTORS: [Potential issues and mitigation strategies]
        💰 COST OPPORTUNITIES: [Savings and optimization suggestions]
        
        Provide specific, actionable recommendations prioritized by patient care impact.
        """
        
        content, confidence = await self._call_llm_api(prompt)
        
        # Extract suggestions from the response
        suggestions = self._extract_suggestions(content)
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            reasoning="Analysis based on real-time inventory data, hospital context, and healthcare best practices",
            suggestions=suggestions,
            generated_at=datetime.now(),
            model_used=os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        )
    
    async def generate_purchase_order_justification(self, order_data: Dict, historical_context: Dict) -> LLMResponse:
        """
        Generate intelligent justification for purchase orders
        """
        
        prompt = f"""
        HOSPITAL PROCUREMENT ANALYSIS REQUEST
        
        PURCHASE ORDER DETAILS:
        {json.dumps(order_data, indent=2)}
        
        HISTORICAL CONTEXT:
        {json.dumps(historical_context, indent=2)}
        
        HOSPITAL REQUIREMENTS:
        - Patient Safety: Ensure continuous care delivery
        - Regulatory Compliance: Meet Joint Commission, CMS, OSHA standards
        - Cost Effectiveness: Optimize budget utilization
        - Supply Chain Resilience: Maintain adequate safety stock
        
        GENERATE COMPREHENSIVE JUSTIFICATION INCLUDING:
        
        **BUSINESS JUSTIFICATION**:
        - Clear rationale for this procurement decision
        - Alignment with hospital operational needs
        - Patient care continuity requirements
        
        **CLINICAL IMPACT ASSESSMENT**:
        - Direct impact on patient care quality and safety
        - Effects on clinical workflows and procedures
        - Emergency preparedness considerations
        
        **FINANCIAL ANALYSIS**:
        - Cost-benefit breakdown and ROI calculation
        - Comparison with emergency procurement costs
        - Budget impact and cash flow considerations
        
        **RISK ASSESSMENT**:
        - Consequences of procurement delay or rejection
        - Supply chain vulnerability analysis
        - Mitigation strategies for identified risks
        
        **COMPLIANCE VERIFICATION**:
        - Regulatory requirement satisfaction
        - Quality and safety standard adherence
        - Documentation and audit trail requirements
        
        **RECOMMENDATIONS**:
        - Optimal timing and delivery schedule
        - Alternative sourcing options if applicable
        - Future procurement planning suggestions
        
        Format as a professional procurement justification document suitable for executive review.
        """
        
        content, confidence = await self._call_llm_api(prompt)
        suggestions = self._extract_suggestions(content)
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            reasoning="Generated based on healthcare procurement best practices, regulatory requirements, and operational analysis",
            suggestions=suggestions,
            generated_at=datetime.now(),
            model_used=os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        )
    
    async def create_intelligent_alert(self, alert_data: Dict, department_context: Dict) -> LLMResponse:
        """
        Create contextual, actionable alerts for different user roles
        """
        
        target_role = alert_data.get('target_role', 'General Staff')
        alert_type = alert_data.get('type', 'general')
        
        prompt = f"""
        HOSPITAL ALERT GENERATION REQUEST
        
        ALERT DATA:
        {json.dumps(alert_data, indent=2)}
        
        DEPARTMENT CONTEXT:
        {json.dumps(department_context, indent=2)}
        
        TARGET AUDIENCE: {target_role}
        ALERT TYPE: {alert_type}
        
        REQUIREMENTS FOR HOSPITAL STAFF ALERT:
        
        **ALERT HEADER**: Clear, urgent but professional tone
        **SITUATION ASSESSMENT**: Precise description of current status
        **IMMEDIATE ACTIONS**: Role-specific steps with clear priorities
        **CLINICAL IMPACT**: Patient care implications if any
        **ESCALATION PROTOCOL**: When and whom to contact
        **TIMELINE**: Specific deadlines and milestones
        **COMPLIANCE NOTES**: Regulatory considerations if applicable
        
        CUSTOMIZE FOR ROLE: {target_role}
        - Nurses: Focus on patient safety and workflow impact
        - Physicians: Emphasize clinical implications and alternatives
        - Administrators: Highlight operational and financial impacts
        - Supply Staff: Provide detailed logistics and sourcing information
        - General Staff: Clear, simple instructions with escalation paths
        
        TONE REQUIREMENTS:
        - Professional and authoritative
        - Urgent but not panic-inducing
        - Actionable with clear next steps
        - Compliant with hospital communication standards
        
        Format as a professional hospital alert with appropriate urgency indicators.
        """
        
        content, confidence = await self._call_llm_api(prompt)
        suggestions = self._extract_suggestions(content)
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            reasoning=f"Alert tailored for {target_role} with hospital-specific protocols and patient safety focus",
            suggestions=suggestions,
            generated_at=datetime.now(),
            model_used=os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        )
    
    async def natural_language_query(self, query: str, system_context: Dict) -> LLMResponse:
        """
        Process natural language queries about the supply system
        """
        
        # Extract inventory data for detailed analysis
        inventory_data = system_context.get('inventory_data', {})
        low_stock_items = inventory_data.get('low_stock_items', [])
        critical_alerts = inventory_data.get('critical_alerts', [])
        recent_activities = system_context.get('recent_activities', [])
        
        # Format inventory details for the prompt
        inventory_details = ""
        if low_stock_items:
            inventory_details += f"\n**LOW STOCK ITEMS ({len(low_stock_items)}):**\n"
            for item in low_stock_items[:10]:  # Limit to top 10
                inventory_details += f"- {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (min: {item.get('minimum_stock', 0)}) - {item.get('location', 'Unknown location')}\n"
        
        if critical_alerts:
            inventory_details += f"\n**CRITICAL ALERTS ({len(critical_alerts)}):**\n"
            for alert in critical_alerts[:10]:  # Limit to top 10
                inventory_details += f"- {alert.get('message', 'No message')} - {alert.get('department', 'Unknown dept')}\n"
        
        if recent_activities:
            inventory_details += f"\n**RECENT ACTIVITIES:**\n"
            for activity in recent_activities[:5]:  # Limit to top 5
                inventory_details += f"- {activity.get('action', 'Unknown')} - {activity.get('item', 'Unknown item')} - {activity.get('timestamp', 'Unknown time')}\n"
        
        prompt = f"""
        HOSPITAL SUPPLY SYSTEM QUERY
        
        USER QUERY: "{query}"
        
        REAL-TIME INVENTORY STATUS:
        - Total Items: {inventory_data.get('total_items', 0)}
        - Low Stock Items: {inventory_data.get('low_stock_count', 0)}
        - Critical Alerts: {inventory_data.get('critical_alerts_count', 0)}
        - Last Updated: {inventory_data.get('last_updated', 'Unknown')}
        
        DETAILED INVENTORY DATA:
        {inventory_details}
        
        SYSTEM CONTEXT:
        - User Role: {system_context.get('user_role', 'Unknown')}
        - Department: {system_context.get('department', 'Unknown')}
        - Timestamp: {system_context.get('timestamp', 'Unknown')}
        
        AVAILABLE CAPABILITIES:
        - Real-time inventory monitoring across all departments
        - Purchase order tracking and approval workflows
        - Inter-department transfer management
        - Supplier performance analytics
        - Compliance reporting and audit trails
        - Predictive analytics for demand forecasting
        - Emergency supply protocols
        - Cost analysis and budget optimization
        
        HOSPITAL DEPARTMENTS COVERED:
        - Emergency Department (ED)
        - Intensive Care Unit (ICU)
        - Operating Rooms (OR)
        - Medical/Surgical Units
        - Pharmacy and Central Supply
        - Laboratory and Radiology
        
        RESPONSE REQUIREMENTS:
        1. Use natural, conversational language suitable for chat
        2. Include specific item names, quantities, and locations from the data
        3. Provide clear next steps and recommendations
        4. Reference current hospital operations and actual alerts
        5. Offer helpful follow-up suggestions
        
        FORMATTING GUIDELINES:
        - Write in natural, conversational style like talking to a colleague
        - Avoid formal section headers like "DIRECT ANSWER:" or "ACTIONABLE INSIGHTS:"
        - Use bullet points with - or • for lists
        - Keep responses concise but informative
        - Use normal capitalization (avoid excessive CAPS)
        - Structure information clearly with natural flow
        
        TONE GUIDELINES:
        - Professional but approachable
        - Clear and urgent when needed
        - Helpful and supportive
        - Focus on practical solutions
        
        MAINTAIN HOSPITAL CONTEXT:
        - Patient care always takes priority
        - Compliance with healthcare regulations
        - Cost-effective solutions preferred
        - Emergency preparedness considerations
        
        IMPORTANT: Use the REAL inventory data provided above. Write responses naturally as if speaking to a hospital manager colleague. Avoid formal document structure.
```
        """
        
        content, confidence = await self._call_llm_api(prompt)
        
        # Clean up formatting for chat interface
        content = self._clean_chat_formatting(content)
        
        suggestions = self._extract_suggestions(content)
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            reasoning="Response generated based on current system state, hospital context, and healthcare best practices",
            suggestions=suggestions,
            generated_at=datetime.now(),
            model_used=os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        )
    
    def _clean_chat_formatting(self, content: str) -> str:
        """
        Clean up formatting for better chat interface display
        """
        if not content:
            return content
        
        # Remove excessive markdown formatting
        cleaned = content
        
        # Remove all bold markdown formatting for cleaner chat display
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
        
        # Reduce multiple asterisks to single for better readability
        cleaned = re.sub(r'\*{3,}', '*', cleaned)
        
        # Remove formal document-style headers
        formal_headers = [
            r'DIRECT ANSWER:\s*\n?',
            r'SPECIFIC DETAILS:\s*\n?',
            r'ACTIONABLE INSIGHTS:\s*\n?',
            r'CONTEXT AWARENESS:\s*\n?',
            r'FOLLOW-UP SUGGESTIONS:\s*\n?',
            r'SUPPLY MANAGER INVENTORY ALERT:\s*\n?',
            r'IMMEDIATE ACTION REQUIRED\s*\n?'
        ]
        
        for header in formal_headers:
            cleaned = re.sub(header, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up section headers that might be too bold
        cleaned = re.sub(r'\*\*([A-Z\s]+):\*\*', r'\1:', cleaned)
        
        # Clean up excessive caps formatting
        cleaned = re.sub(r'\*\*([A-Z]{2,})\*\*', r'\1', cleaned)
        
        # Ensure proper spacing around lists
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned)
        
        # Clean up any remaining asterisks around words
        cleaned = re.sub(r'\*([^*\n]+)\*', r'\1', cleaned)
        
        # Remove extra whitespace at the beginning
        cleaned = re.sub(r'^\s+', '', cleaned, flags=re.MULTILINE)
        
        return cleaned.strip()
    
    def _extract_suggestions(self, content: str) -> List[str]:
        """
        Extract actionable suggestions from LLM response content
        """
        suggestions = []
        
        # Look for common suggestion patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Look for bullet points, numbered lists, or recommendation sections
            if any(pattern in line.lower() for pattern in ['recommend', 'suggest', 'consider', 'should']):
                if line and len(line) < 200:  # Keep suggestions concise
                    # Clean up the suggestion
                    suggestion = line.replace('•', '').replace('-', '').strip()
                    if suggestion and not suggestion.endswith(':'):
                        suggestions.append(suggestion)
        
        # If no suggestions found, provide defaults based on content
        if not suggestions:
            if 'critical' in content.lower():
                suggestions.append("Review critical alerts immediately")
            if 'order' in content.lower():
                suggestions.append("Check purchase order status")
            if 'inventory' in content.lower():
                suggestions.append("Monitor inventory levels")
        
        return suggestions[:5]  # Limit to top 5 suggestions

# Performance monitoring and analytics
class LLMPerformanceMonitor:
    """
    Monitor LLM performance, usage, and accuracy
    """
    
    def __init__(self):
        self.interaction_log = []
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'average_confidence': 0,
            'user_satisfaction_scores': []
        }
    
    def log_interaction(self, query: str, response: LLMResponse, response_time: float, user_feedback: Optional[int] = None):
        """
        Log LLM interaction for performance analysis
        """
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response_length': len(response.content),
            'confidence': response.confidence,
            'response_time': response_time,
            'model_used': response.model_used,
            'user_feedback': user_feedback  # 1-5 scale
        }
        
        self.interaction_log.append(interaction)
        self._update_metrics(interaction)
        
        # Log to file if enabled
        if os.getenv('LOG_LLM_INTERACTIONS', 'false').lower() == 'true':
            self._log_to_file(interaction)
    
    def _update_metrics(self, interaction: dict):
        """Update performance metrics"""
        self.performance_metrics['total_requests'] += 1
        
        if interaction['confidence'] > 0.5:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['failed_requests'] += 1
        
        # Update averages
        total = self.performance_metrics['total_requests']
        self.performance_metrics['average_response_time'] = (
            (self.performance_metrics['average_response_time'] * (total - 1) + interaction['response_time']) / total
        )
        self.performance_metrics['average_confidence'] = (
            (self.performance_metrics['average_confidence'] * (total - 1) + interaction['confidence']) / total
        )
        
        if interaction['user_feedback']:
            self.performance_metrics['user_satisfaction_scores'].append(interaction['user_feedback'])
    
    def _log_to_file(self, interaction: dict):
        """Log interaction to file for analysis"""
        log_file = "llm_interactions.log"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(interaction, default=str)}\n")
        except Exception as e:
            logging.error(f"Failed to log interaction: {e}")
    
    def get_performance_report(self) -> dict:
        """Generate performance report"""
        avg_satisfaction = (
            sum(self.performance_metrics['user_satisfaction_scores']) / 
            len(self.performance_metrics['user_satisfaction_scores'])
        ) if self.performance_metrics['user_satisfaction_scores'] else 0
        
        return {
            **self.performance_metrics,
            'success_rate': (
                self.performance_metrics['successful_requests'] / 
                max(1, self.performance_metrics['total_requests'])
            ) * 100,
            'average_user_satisfaction': avg_satisfaction,
            'last_updated': datetime.now().isoformat()
        }

# Integration with existing supply agent
class LLMEnhancedSupplyAgent:
    """
    Enhanced supply agent with LLM capabilities and performance monitoring
    """
    
    def __init__(self, base_agent, llm_assistant: IntelligentSupplyAssistant):
        self.base_agent = base_agent
        self.llm_assistant = llm_assistant
        self.performance_monitor = LLMPerformanceMonitor()
        
    async def create_intelligent_purchase_order(self, item_data: Dict, context: Dict):
        """Create purchase order with LLM-generated justification"""
        
        start_time = time.time()
        
        try:
            # Get LLM analysis
            justification = await self.llm_assistant.generate_purchase_order_justification(
                item_data, context
            )
            
            response_time = time.time() - start_time
            
            # Log performance
            self.performance_monitor.log_interaction(
                f"PO Analysis for {item_data.get('id', 'Unknown')}",
                justification,
                response_time
            )
            
            # Create enhanced purchase order
            po_data = {
                **item_data,
                'llm_justification': justification.content,
                'confidence_score': justification.confidence,
                'ai_recommendations': justification.suggestions,
                'generated_at': justification.generated_at,
                'analysis_quality': 'high' if justification.confidence > 0.8 else 'medium'
            }
            
            return po_data
            
        except Exception as e:
            logging.error(f"Enhanced PO creation failed: {e}")
            return item_data  # Return original data if enhancement fails
    
    async def generate_smart_alerts(self, inventory_data: Dict, department_context: Dict):
        """Generate intelligent, contextual alerts"""
        
        alerts = []
        for item in inventory_data.get('low_stock_items', []):
            try:
                start_time = time.time()
                
                alert_response = await self.llm_assistant.create_intelligent_alert(
                    {'item': item, 'type': 'low_stock'}, 
                    department_context
                )
                
                response_time = time.time() - start_time
                
                # Log performance
                self.performance_monitor.log_interaction(
                    f"Alert for {item.get('name', 'Unknown Item')}",
                    alert_response,
                    response_time
                )
                
                alerts.append({
                    'item_id': item.get('id'),
                    'item_name': item.get('name'),
                    'message': alert_response.content,
                    'priority': self._calculate_priority(alert_response.confidence),
                    'ai_suggestions': alert_response.suggestions,
                    'confidence': alert_response.confidence,
                    'generated_at': alert_response.generated_at
                })
                
            except Exception as e:
                logging.error(f"Smart alert generation failed for item {item.get('id')}: {e}")
                # Fallback to basic alert
                alerts.append({
                    'item_id': item.get('id'),
                    'item_name': item.get('name'),
                    'message': f"Low stock alert: {item.get('name')} is below minimum threshold",
                    'priority': 'MEDIUM',
                    'ai_suggestions': ['Check inventory manually', 'Contact procurement'],
                    'confidence': 0.5
                })
        
        return alerts
    
    def _calculate_priority(self, confidence: float) -> str:
        """Calculate alert priority based on AI confidence"""
        if confidence >= 0.9:
            return "HIGH"
        elif confidence >= 0.7:
            return "MEDIUM"
        else:
            return "LOW"

# Enhanced integration service with monitoring
class LLMEnhancedSupplyAgent:
    """
    Enhanced Supply Agent with RAG and MCP capabilities
    Combines LLM intelligence with contextual retrieval and structured protocol
    """
    
    def __init__(self):
        self.llm_assistant = IntelligentSupplyAssistant()
        self.rag_system = None
        self.mcp_server = None
        self.conversation_context = {}
        
    async def initialize(self):
        """Initialize RAG and MCP systems"""
        if RAG_MCP_AVAILABLE:
            try:
                self.rag_system = await get_rag_system()
                self.mcp_server = get_mcp_server()
                logging.info("✅ Enhanced Supply Agent with RAG/MCP initialized")
            except Exception as e:
                logging.error(f"❌ Failed to initialize RAG/MCP: {e}")
                self.rag_system = None
                self.mcp_server = None
        else:
            logging.warning("⚠️ RAG/MCP not available - using basic LLM only")
    
    async def process_query_with_context(self, query: str, user_context: Dict[str, Any] = None) -> LLMResponse:
        """Process query with RAG context and MCP capabilities"""
        try:
            enhanced_prompt = query
            context_info = ""
            
            # Get RAG context if available
            if self.rag_system:
                rag_context = await self.rag_system.get_context(query)
                if rag_context.relevant_documents:
                    context_info += f"\n\nRelevant Context from Knowledge Base:\n{rag_context.context_summary}"
                    enhanced_prompt = f"{query}\n\nAdditional Context:\n{rag_context.context_summary}"
            
            # Get MCP context if available
            if self.mcp_server and user_context:
                mcp_context_response = await self.mcp_server._handle_get_context({}, user_context.get('connection_id', 'default'))
                mcp_context = mcp_context_response.get('context', {})
                
                if mcp_context:
                    hospital_info = mcp_context.get('hospital_info', {})
                    inventory_state = mcp_context.get('inventory_state', {})
                    
                    context_info += f"\n\nCurrent Hospital State:\n"
                    context_info += f"- Patient Census: {hospital_info.get('patient_census', 'N/A')}\n"
                    context_info += f"- Bed Utilization: {hospital_info.get('bed_utilization', 'N/A')}\n"
                    context_info += f"- Operating Status: {hospital_info.get('operating_status', 'Normal')}\n"
                    context_info += f"- Total Inventory Value: ${inventory_state.get('total_value', 0):,.2f}\n"
                    context_info += f"- Items Below Minimum: {inventory_state.get('items_below_minimum', 0)}\n"
                    
                    enhanced_prompt += context_info
            
            # Process with enhanced context
            response = await self.llm_assistant.natural_language_query(enhanced_prompt, user_context or {})
            
            # Add context information to response
            if context_info:
                response.reasoning += f"\n\nContext Used: {context_info[:200]}..."
            
            return response
            
        except Exception as e:
            logging.error(f"Enhanced query processing failed: {e}")
            # Fallback to basic LLM processing
            return await self.llm_assistant.natural_language_query(query, user_context or {})
    
    async def process_mcp_tool_request(self, tool_name: str, tool_params: Dict[str, Any], 
                                     user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process MCP tool request"""
        if not self.mcp_server:
            return {"error": "MCP server not available"}
        
        try:
            connection_id = user_context.get('connection_id', 'default') if user_context else 'default'
            
            message_data = {
                "id": f"tool_request_{int(time.time())}",
                "type": "request", 
                "method": "call_tool",
                "params": {
                    "name": tool_name,
                    "arguments": tool_params
                }
            }
            
            response = await handle_mcp_request(message_data, connection_id)
            return response
            
        except Exception as e:
            logging.error(f"MCP tool request failed: {e}")
            return {"error": f"Tool request failed: {str(e)}"}
    
    async def add_dynamic_knowledge(self, content: str, doc_type: str, metadata: Dict[str, Any]):
        """Add dynamic knowledge to RAG system"""
        if self.rag_system:
            try:
                from rag_system import DocumentType
                doc_type_enum = DocumentType(doc_type) if doc_type in [dt.value for dt in DocumentType] else DocumentType.INVENTORY_DATA
                await self.rag_system.add_dynamic_context(content, doc_type_enum, metadata)
                logging.info(f"📝 Added dynamic knowledge: {doc_type}")
            except Exception as e:
                logging.error(f"Failed to add dynamic knowledge: {e}")
    
    async def get_intelligent_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get intelligent recommendations based on current context"""
        try:
            # Build comprehensive context prompt
            prompt = f"""
            Based on the current hospital supply chain state, provide intelligent recommendations:
            
            Current Context:
            {json.dumps(context, indent=2)}
            
            Please analyze and provide:
            1. Immediate actions needed (next 4 hours)
            2. Short-term planning (next 24-48 hours) 
            3. Medium-term optimization (next week)
            4. Long-term strategic recommendations (next month)
            5. Risk mitigation strategies
            6. Cost optimization opportunities
            
            Focus on patient safety, operational efficiency, and cost-effectiveness.
            """
            
            # Get RAG context for recommendations
            rag_enhanced_response = await self.process_query_with_context(prompt, context)
            
            # Structure the response
            recommendations = {
                "immediate_actions": [],
                "short_term_planning": [], 
                "medium_term_optimization": [],
                "long_term_strategic": [],
                "risk_mitigation": [],
                "cost_optimization": [],
                "confidence_score": rag_enhanced_response.confidence,
                "generated_at": rag_enhanced_response.generated_at.isoformat(),
                "reasoning": rag_enhanced_response.reasoning
            }
            
            # Parse structured recommendations from LLM response
            content = rag_enhanced_response.content
            
            # Simple parsing - could be enhanced with more sophisticated NLP
            sections = {
                "immediate actions": "immediate_actions",
                "short-term planning": "short_term_planning", 
                "medium-term optimization": "medium_term_optimization",
                "long-term strategic": "long_term_strategic",
                "risk mitigation": "risk_mitigation",
                "cost optimization": "cost_optimization"
            }
            
            for section_name, key in sections.items():
                pattern = rf"{section_name}[:\-]?\s*\n(.*?)(?=\n\d+\.|$)"
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    items = [item.strip() for item in matches[0].split('\n') if item.strip() and not item.strip().startswith('-')]
                    recommendations[key] = items[:5]  # Limit to top 5 items
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Failed to generate intelligent recommendations: {e}")
            return {
                "error": "Failed to generate recommendations",
                "fallback_message": "Please check system status and try again",
                "generated_at": datetime.now().isoformat()
            }

class LLMIntegrationService:
    """
    Service class for integrating LLM capabilities throughout the platform
    Includes performance monitoring and quality assurance
    """
    
    def __init__(self):
        self.assistant = IntelligentSupplyAssistant()
        self.enhanced_agents = {}
        self.performance_monitor = LLMPerformanceMonitor()
        self.cache = {} if os.getenv('LLM_ENABLE_CACHING', 'true').lower() == 'true' else None
        self.cache_ttl = int(os.getenv('LLM_CACHE_TTL', '300'))  # 5 minutes default
    
    async def enhance_dashboard_insights(self, dashboard_data: Dict) -> Dict:
        """Add LLM-generated insights to dashboard"""
        
        # Check cache first
        cache_key = f"dashboard_insights_{hash(str(dashboard_data))}"
        if self.cache and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if (datetime.now() - cached_result['timestamp']).seconds < self.cache_ttl:
                return cached_result['data']
        
        start_time = time.time()
        
        try:
            analysis = await self.assistant.analyze_inventory_situation(
                dashboard_data, 
                {
                    'hospital_type': os.getenv('HOSPITAL_TYPE', 'General Hospital'),
                    'season': self._get_current_season(),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            response_time = time.time() - start_time
            
            # Log performance
            self.performance_monitor.log_interaction(
                "Dashboard Enhancement",
                analysis,
                response_time
            )
            
            enhanced_data = {
                **dashboard_data,
                'ai_insights': {
                    'summary': analysis.content,
                    'confidence': analysis.confidence,
                    'recommendations': analysis.suggestions,
                    'generated_at': analysis.generated_at,
                    'quality_score': self._calculate_quality_score(analysis)
                }
            }
            
            # Cache result
            if self.cache:
                self.cache[cache_key] = {
                    'data': enhanced_data,
                    'timestamp': datetime.now()
                }
            
            return enhanced_data
            
        except Exception as e:
            logging.error(f"Dashboard enhancement failed: {e}")
            return dashboard_data  # Return original data if enhancement fails
    
    async def process_natural_language_command(self, command: str, user_context: Dict) -> Dict:
        """Process natural language commands for system interaction"""
        
        start_time = time.time()
        
        try:
            response = await self.assistant.natural_language_query(command, user_context)
            
            response_time = time.time() - start_time
            
            # Log performance
            self.performance_monitor.log_interaction(
                command,
                response,
                response_time
            )
            
            return {
                'response': response.content,
                'confidence': response.confidence,
                'suggested_actions': response.suggestions,
                'requires_followup': response.confidence < float(os.getenv('LLM_CONFIDENCE_THRESHOLD', '0.7')),
                'quality_score': self._calculate_quality_score(response),
                'response_time': response_time
            }
            
        except Exception as e:
            logging.error(f"NL command processing failed: {e}")
            return {
                'response': "I'm experiencing technical difficulties. Please try again or contact support.",
                'confidence': 0.0,
                'suggested_actions': ['Try again later', 'Contact support', 'Use manual interface'],
                'requires_followup': True,
                'error': str(e)
            }
    
    def _calculate_quality_score(self, response: LLMResponse) -> float:
        """Calculate quality score based on multiple factors"""
        score = response.confidence * 0.6  # Base score from confidence
        
        # Length factor (appropriate detail)
        length_score = min(1.0, len(response.content) / 500) * 0.2
        score += length_score
        
        # Suggestion quality
        suggestion_score = min(1.0, len(response.suggestions) / 3) * 0.2
        score += suggestion_score
        
        return min(1.0, score)
    
    def _get_current_season(self) -> str:
        """Get current season for context"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"
    
    def get_system_status(self) -> Dict:
        """Get current LLM system status and performance metrics"""
        return {
            'openai_configured': OPENAI_CONFIGURED,
            'openai_api_key_set': bool(OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here'),
            'model': os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            'performance_metrics': self.performance_monitor.get_performance_report(),
            'cache_enabled': self.cache is not None,
            'system_health': 'operational' if OPENAI_CONFIGURED else 'limited'
        }

# Export main classes for integration
__all__ = [
    'IntelligentSupplyAssistant',
    'LLMEnhancedSupplyAgent', 
    'LLMIntegrationService',
    'LLMResponse',
    'LLMProvider',
    'HospitalContextManager',
    'LLMPerformanceMonitor',
    'OPENAI_CONFIGURED'
]
