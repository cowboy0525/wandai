import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2
from fastapi import UploadFile
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import openai
from dotenv import load_dotenv

from app.models.schemas import DocumentMetadata, SearchResult, EnrichmentSuggestion

load_dotenv()

class KnowledgeBase:
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        self.chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.chroma_path, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # OpenAI client for summarization and enrichment
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # In-memory document metadata (in production, use a proper database)
        self.documents: Dict[str, DocumentMetadata] = {}
    
    async def add_document(self, file: UploadFile) -> str:
        """Add a document to the knowledge base"""
        try:
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Save file
            file_path = os.path.join(self.upload_dir, f"{doc_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Extract text content
            text_content = await self._extract_text(file_path, file.filename)
            
            # Generate summary
            summary = await self._generate_summary(text_content)
            
            # Create embeddings and store in ChromaDB
            chunks = self._chunk_text(text_content)
            embeddings = self.embedding_model.encode(chunks)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=[{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))],
                ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
            )
            
            # Store metadata
            self.documents[doc_id] = DocumentMetadata(
                filename=file.filename,
                document_type="OTHER",
                upload_date=datetime.now(),
                file_size=len(content),
                description=summary
            )
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")
    
    async def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from different file types"""
        try:
            if filename.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            elif filename.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif filename.lower().endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                raise ValueError(f"Unsupported file type: {filename}")
        except Exception as e:
            raise Exception(f"Failed to extract text: {str(e)}")
    
    async def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document using OpenAI"""
        try:
            if not openai.api_key:
                return "Summary not available (OpenAI API key not configured)"
            
            # Truncate text if too long
            max_tokens = 4000
            truncated_text = text[:max_tokens] if len(text) > max_tokens else text
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes documents concisely."},
                    {"role": "user", "content": f"Please provide a brief summary of this document:\n\n{truncated_text}"}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for embedding"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search the knowledge base using RAG"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k
            )
            
            # Format results
            search_results = []
            for i, (doc_id_chunk, content, metadata, distance) in enumerate(zip(
                results['ids'][0], results['documents'][0], 
                results['metadatas'][0], results['distances'][0]
            )):
                doc_id = metadata['doc_id']
                if doc_id in self.documents:
                    search_results.append(SearchResult(
                        document_id=doc_id,
                        filename=self.documents[doc_id].filename,
                        content=content,
                        relevance_score=1.0 - distance,  # Convert distance to similarity
                        page_number=metadata.get('chunk_index', 0)
                    ))
            
            return search_results
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_enrichment_suggestions(self, query: str) -> List[EnrichmentSuggestion]:
        """Generate suggestions for enriching the knowledge base"""
        suggestions = []
        
        # Analyze query for potential gaps
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['financial', 'revenue', 'profit', 'cost']):
            suggestions.append(EnrichmentSuggestion(
                type="document",
                description="Financial reports and quarterly statements",
                priority="high",
                source="Finance department"
            ))
        
        if any(word in query_lower for word in ['customer', 'user', 'feedback', 'survey']):
            suggestions.append(EnrichmentSuggestion(
                type="data",
                description="Customer feedback and survey results",
                priority="medium",
                source="Customer success team"
            ))
        
        if any(word in query_lower for word in ['trend', 'analysis', 'forecast', 'prediction']):
            suggestions.append(EnrichmentSuggestion(
                type="action",
                description="Conduct market research and trend analysis",
                priority="high",
                source="Strategy team"
            ))
        
        return suggestions
    
    def list_documents(self) -> List[DocumentMetadata]:
        """List all documents in the knowledge base"""
        return list(self.documents.values())
    
    def get_document(self, doc_id: str) -> DocumentMetadata:
        """Get a specific document by ID"""
        return self.documents.get(doc_id)
