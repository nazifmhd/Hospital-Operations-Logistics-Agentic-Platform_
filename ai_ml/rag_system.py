"""
Retrieval-Augmented Generation (RAG) System for Hospital Supply Chain Platform
Enhances LLM responses with contextual hospital data and documentation
"""

import os
import json
import asyncio
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pickle
import sqlite3
from pathlib import Path

# Vector database and embedding imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available - using fallback vector storage")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - using basic text matching")

# OpenAI for embeddings
try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here':
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
    else:
        OPENAI_AVAILABLE = False
except ImportError:
    OPENAI_AVAILABLE = False

class DocumentType(Enum):
    INVENTORY_DATA = "inventory_data"
    PROCEDURE_GUIDE = "procedure_guide"
    POLICY_DOCUMENT = "policy_document"
    SUPPLIER_INFO = "supplier_info"
    HISTORICAL_DATA = "historical_data"
    ALERT_CONTEXT = "alert_context"
    USER_MANUAL = "user_manual"
    COMPLIANCE_DOC = "compliance_doc"

@dataclass
class Document:
    """Represents a document in the RAG system"""
    id: str
    content: str
    doc_type: DocumentType
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: str = ""
    relevance_score: float = 0.0

@dataclass
class RAGContext:
    """Context retrieved for RAG enhancement"""
    query: str
    relevant_documents: List[Document]
    context_summary: str
    confidence_score: float
    retrieved_at: datetime = field(default_factory=datetime.now)

class VectorStore:
    """Vector storage interface with multiple backends"""
    
    def __init__(self, storage_path: str = "rag_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        if CHROMADB_AVAILABLE:
            self._init_chromadb()
        elif SKLEARN_AVAILABLE:
            self._init_sklearn_backend()
        else:
            self._init_fallback_backend()
    
    def _init_chromadb(self):
        """Initialize ChromaDB vector store"""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path / "chromadb"),
                settings=Settings(allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection(
                name="hospital_supply_docs",
                metadata={"description": "Hospital supply chain documents"}
            )
            self.backend = "chromadb"
            logging.info("✅ ChromaDB vector store initialized")
        except Exception as e:
            logging.error(f"ChromaDB initialization failed: {e}")
            if SKLEARN_AVAILABLE:
                self._init_sklearn_backend()
            else:
                self._init_fallback_backend()
    
    def _init_sklearn_backend(self):
        """Initialize scikit-learn TF-IDF backend"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.documents_db = sqlite3.connect(
            str(self.storage_path / "documents.db"),
            check_same_thread=False
        )
        self._create_tables()
        self.backend = "sklearn"
        logging.info("✅ Scikit-learn TF-IDF backend initialized")
    
    def _init_fallback_backend(self):
        """Initialize simple text matching fallback"""
        self.documents_db = sqlite3.connect(
            str(self.storage_path / "documents.db"),
            check_same_thread=False
        )
        self._create_tables()
        self.backend = "fallback"
        logging.info("✅ Fallback text matching backend initialized")
    
    def _create_tables(self):
        """Create SQLite tables for document storage"""
        cursor = self.documents_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT,
                doc_type TEXT,
                metadata TEXT,
                embedding BLOB,
                created_at TEXT,
                updated_at TEXT,
                source TEXT
            )
        ''')
        self.documents_db.commit()
    
    async def add_document(self, document: Document) -> bool:
        """Add document to vector store"""
        try:
            if self.backend == "chromadb":
                return await self._add_to_chromadb(document)
            else:
                return await self._add_to_sqlite(document)
        except Exception as e:
            logging.error(f"Failed to add document {document.id}: {e}")
            return False
    
    async def _add_to_chromadb(self, document: Document) -> bool:
        """Add document to ChromaDB"""
        try:
            self.collection.add(
                documents=[document.content],
                metadatas=[{
                    "doc_type": document.doc_type.value,
                    "source": document.source,
                    "created_at": document.created_at.isoformat(),
                    **document.metadata
                }],
                ids=[document.id]
            )
            return True
        except Exception as e:
            logging.error(f"ChromaDB add failed: {e}")
            return False
    
    async def _add_to_sqlite(self, document: Document) -> bool:
        """Add document to SQLite backend"""
        try:
            cursor = self.documents_db.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (id, content, doc_type, metadata, embedding, created_at, updated_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.id,
                document.content,
                document.doc_type.value,
                json.dumps(document.metadata),
                pickle.dumps(document.embedding) if document.embedding else None,
                document.created_at.isoformat(),
                document.updated_at.isoformat(),
                document.source
            ))
            self.documents_db.commit()
            return True
        except Exception as e:
            logging.error(f"SQLite add failed: {e}")
            return False
    
    async def search(self, query: str, limit: int = 5) -> List[Document]:
        """Search for relevant documents"""
        try:
            if self.backend == "chromadb":
                return await self._search_chromadb(query, limit)
            elif self.backend == "sklearn":
                return await self._search_sklearn(query, limit)
            else:
                return await self._search_fallback(query, limit)
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []
    
    async def _search_chromadb(self, query: str, limit: int) -> List[Document]:
        """Search using ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            documents = []
            for i, doc_id in enumerate(results['ids'][0]):
                content = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results else 0.0
                
                document = Document(
                    id=doc_id,
                    content=content,
                    doc_type=DocumentType(metadata.get('doc_type', 'inventory_data')),
                    metadata=metadata,
                    source=metadata.get('source', ''),
                    relevance_score=1.0 - distance  # Convert distance to similarity
                )
                documents.append(document)
            
            return documents
        except Exception as e:
            logging.error(f"ChromaDB search failed: {e}")
            return []
    
    async def _search_sklearn(self, query: str, limit: int) -> List[Document]:
        """Search using scikit-learn TF-IDF"""
        try:
            cursor = self.documents_db.cursor()
            cursor.execute('SELECT * FROM documents')
            rows = cursor.fetchall()
            
            if not rows:
                return []
            
            contents = [row[1] for row in rows]  # content column
            
            # Fit vectorizer if not already fitted or if empty
            try:
                tfidf_matrix = self.vectorizer.transform(contents + [query])
            except:
                tfidf_matrix = self.vectorizer.fit_transform(contents + [query])
            
            # Calculate similarities
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # Get top results
            top_indices = similarities.argsort()[-limit:][::-1]
            
            documents = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    row = rows[idx]
                    document = Document(
                        id=row[0],
                        content=row[1],
                        doc_type=DocumentType(row[2]),
                        metadata=json.loads(row[3]),
                        source=row[7],
                        relevance_score=float(similarities[idx])
                    )
                    documents.append(document)
            
            return documents
        except Exception as e:
            logging.error(f"Sklearn search failed: {e}")
            return []
    
    async def _search_fallback(self, query: str, limit: int) -> List[Document]:
        """Fallback text search"""
        try:
            cursor = self.documents_db.cursor()
            cursor.execute('''
                SELECT * FROM documents 
                WHERE content LIKE ? OR metadata LIKE ?
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            documents = []
            
            for row in rows:
                document = Document(
                    id=row[0],
                    content=row[1],
                    doc_type=DocumentType(row[2]),
                    metadata=json.loads(row[3]),
                    source=row[7],
                    relevance_score=0.5  # Default relevance for fallback
                )
                documents.append(document)
            
            return documents
        except Exception as e:
            logging.error(f"Fallback search failed: {e}")
            return []

class RAGSystem:
    """Main RAG system for hospital supply chain platform"""
    
    def __init__(self, storage_path: str = "rag_data"):
        self.vector_store = VectorStore(storage_path)
        self.context_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        
    async def initialize(self):
        """Initialize RAG system with hospital data"""
        logging.info("🔍 Initializing RAG system...")
        
        # Add initial hospital knowledge base
        await self._load_initial_knowledge()
        
        logging.info("✅ RAG system initialized successfully")
    
    async def _load_initial_knowledge(self):
        """Load initial hospital supply chain knowledge"""
        
        # Inventory management procedures
        procedures_doc = Document(
            id="inventory_procedures_001",
            content="""
            Hospital Inventory Management Procedures:
            
            1. Stock Level Monitoring:
            - Check minimum stock levels daily
            - Set reorder points at 20% of maximum capacity
            - Monitor expiration dates weekly
            - Conduct physical counts monthly
            
            2. Reorder Process:
            - Automated reorders trigger at reorder point
            - Manual override available for urgent needs
            - Purchase orders require approval for amounts >$1000
            - Emergency orders can bypass approval for critical items
            
            3. Inter-facility Transfers:
            - Transfer requests require department head approval
            - Transfers completed within 24 hours for critical items
            - Transfer documentation required for audit trail
            
            4. Quality Control:
            - All incoming supplies inspected upon receipt
            - Temperature-sensitive items verified immediately
            - Damaged or expired items quarantined
            - Recall procedures implemented within 4 hours
            """,
            doc_type=DocumentType.PROCEDURE_GUIDE,
            metadata={
                "category": "inventory_management",
                "version": "2.1",
                "last_updated": "2024-07-15"
            },
            source="hospital_policy_manual"
        )
        
        # Compliance requirements
        compliance_doc = Document(
            id="compliance_requirements_001",
            content="""
            Healthcare Supply Chain Compliance Requirements:
            
            1. HIPAA Compliance:
            - All inventory data must be encrypted
            - Access logs maintained for auditing
            - PHI protection in all documentation
            
            2. FDA Regulations:
            - Medical device tracking required
            - Lot number documentation mandatory
            - Adverse event reporting within 24 hours
            
            3. Joint Commission Standards:
            - Medication storage requirements
            - Temperature monitoring protocols
            - Emergency supply maintenance
            
            4. State Regulations:
            - Controlled substance tracking
            - Pharmacy inventory audits
            - License verification for vendors
            
            5. Internal Policies:
            - Budget approval processes
            - Vendor qualification criteria
            - Risk management protocols
            """,
            doc_type=DocumentType.COMPLIANCE_DOC,
            metadata={
                "category": "compliance",
                "regulatory_body": "multiple",
                "criticality": "high"
            },
            source="compliance_manual"
        )
        
        # Common supply categories
        supply_categories_doc = Document(
            id="supply_categories_001",
            content="""
            Hospital Supply Categories and Management:
            
            1. Medical Supplies:
            - Syringes, needles, catheters
            - Bandages, gauze, tape
            - Diagnostic supplies
            - Minimum stock: 7-day supply
            
            2. Pharmaceuticals:
            - Prescription medications
            - Over-the-counter drugs
            - Controlled substances (special handling)
            - Refrigerated medications
            
            3. Personal Protective Equipment (PPE):
            - Gloves, masks, gowns
            - Face shields, respirators
            - Emergency stockpile required
            
            4. Surgical Supplies:
            - Sutures, surgical instruments
            - Implants and devices
            - Operating room consumables
            
            5. Laboratory Supplies:
            - Reagents and test kits
            - Collection containers
            - Quality control materials
            
            6. Emergency Supplies:
            - Disaster response items
            - Emergency medications
            - Backup equipment
            """,
            doc_type=DocumentType.INVENTORY_DATA,
            metadata={
                "category": "supply_classification",
                "department": "all",
                "priority": "reference"
            },
            source="supply_management_guide"
        )
        
        # Add documents to vector store
        await self.vector_store.add_document(procedures_doc)
        await self.vector_store.add_document(compliance_doc)
        await self.vector_store.add_document(supply_categories_doc)
        
        logging.info("📚 Initial knowledge base loaded successfully")
    
    async def get_context(self, query: str, context_type: str = "general") -> RAGContext:
        """Retrieve relevant context for a query"""
        
        # Check cache first
        cache_key = hashlib.md5(f"{query}_{context_type}".encode()).hexdigest()
        if cache_key in self.context_cache:
            cached_context, timestamp = self.context_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logging.info("🎯 Using cached RAG context")
                return cached_context
        
        try:
            # Search for relevant documents
            relevant_docs = await self.vector_store.search(query, limit=5)
            
            # Create context summary
            context_summary = self._create_context_summary(query, relevant_docs)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(relevant_docs)
            
            rag_context = RAGContext(
                query=query,
                relevant_documents=relevant_docs,
                context_summary=context_summary,
                confidence_score=confidence
            )
            
            # Cache the result
            self.context_cache[cache_key] = (rag_context, datetime.now())
            
            # Clean old cache entries
            self._clean_cache()
            
            return rag_context
            
        except Exception as e:
            logging.error(f"Failed to get RAG context: {e}")
            return RAGContext(
                query=query,
                relevant_documents=[],
                context_summary="No relevant context found.",
                confidence_score=0.0
            )
    
    def _create_context_summary(self, query: str, documents: List[Document]) -> str:
        """Create a summary of retrieved context"""
        if not documents:
            return "No relevant information found in the knowledge base."
        
        # Group documents by type
        doc_groups = {}
        for doc in documents:
            doc_type = doc.doc_type.value
            if doc_type not in doc_groups:
                doc_groups[doc_type] = []
            doc_groups[doc_type].append(doc)
        
        summary_parts = [f"Based on the query '{query}', here's the relevant information:"]
        
        for doc_type, docs in doc_groups.items():
            summary_parts.append(f"\n{doc_type.replace('_', ' ').title()}:")
            for doc in docs:
                # Extract relevant snippets
                snippet = self._extract_relevant_snippet(query, doc.content)
                summary_parts.append(f"- {snippet}")
        
        return "\n".join(summary_parts)
    
    def _extract_relevant_snippet(self, query: str, content: str, max_length: int = 200) -> str:
        """Extract the most relevant snippet from content"""
        sentences = content.split('. ')
        query_words = query.lower().split()
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for word in query_words if word in sentence_lower)
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        if best_sentence and len(best_sentence) <= max_length:
            return best_sentence
        elif best_sentence:
            return best_sentence[:max_length] + "..."
        else:
            return content[:max_length] + "..."
    
    def _calculate_confidence(self, documents: List[Document]) -> float:
        """Calculate confidence score for retrieved context"""
        if not documents:
            return 0.0
        
        # Average relevance score weighted by document count
        total_score = sum(doc.relevance_score for doc in documents)
        avg_score = total_score / len(documents)
        
        # Boost confidence if we have multiple relevant documents
        document_boost = min(len(documents) / 5.0, 1.0)
        
        return min(avg_score * (1 + document_boost * 0.2), 1.0)
    
    def _clean_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.context_cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.context_cache[key]
    
    async def add_dynamic_context(self, content: str, doc_type: DocumentType, 
                                metadata: Dict[str, Any], source: str = "dynamic"):
        """Add dynamic context from real-time data"""
        doc_id = f"dynamic_{datetime.now().isoformat()}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        document = Document(
            id=doc_id,
            content=content,
            doc_type=doc_type,
            metadata=metadata,
            source=source
        )
        
        await self.vector_store.add_document(document)
        logging.info(f"📝 Added dynamic context: {doc_id}")

# Global RAG system instance
rag_system = None

async def get_rag_system() -> RAGSystem:
    """Get or create global RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
        await rag_system.initialize()
    return rag_system

async def enhance_with_rag(query: str, context_type: str = "general") -> RAGContext:
    """Enhance query with RAG context"""
    system = await get_rag_system()
    return await system.get_context(query, context_type)
