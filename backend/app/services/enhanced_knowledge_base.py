import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
from sentence_transformers import SentenceTransformer

from app.models.schemas import (
    SearchResult, EnrichmentSuggestion, DocumentMetadata,
    SearchQuery, SearchResponse, CompletenessCheck
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class EnhancedKnowledgeBase:
    """Enhanced knowledge base with completeness checking and enrichment suggestions"""
    
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize collections
        self.documents_collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embeddings_collection = self.chroma_client.get_or_create_collection(
            name="embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize OpenAI client for advanced analysis
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Could not load sentence transformer: {e}")
            self.embedding_model = None
    
    async def upload_document(self, file_path: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Upload and process a document"""
        try:
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate embeddings
            embeddings = await self._generate_embeddings(content)
            
            # Store in ChromaDB
            document_id = f"doc_{datetime.now().timestamp()}"
            
            self.documents_collection.add(
                documents=[content],
                metadatas=[metadata.dict()],
                ids=[document_id],
                embeddings=[embeddings]
            )
            
            # Store in embeddings collection for similarity search
            self.embeddings_collection.add(
                documents=[content],
                metadatas=[metadata.dict()],
                ids=[document_id],
                embeddings=[embeddings]
            )
            
            return {
                "success": True,
                "document_id": document_id,
                "content_length": len(content),
                "embeddings_generated": len(embeddings)
            }
            
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[SearchResult]:
        """Search knowledge base with enhanced relevance scoring"""
        try:
            # Generate query embeddings
            query_embeddings = await self._generate_embeddings(query)
            
            # Search in embeddings collection
            results = self.embeddings_collection.query(
                query_embeddings=[query_embeddings],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            
            for i, (doc_id, document, metadata, distance) in enumerate(
                zip(results["ids"][0], results["documents"][0], 
                    results["metadatas"][0], results["distances"][0])
            ):
                # Convert distance to similarity score (0-1)
                similarity_score = 1 - distance
                
                # Only include results above threshold
                if similarity_score >= threshold:
                    # Calculate confidence based on similarity and metadata quality
                    confidence = self._calculate_confidence(similarity_score, metadata)
                    
                    search_results.append(SearchResult(
                        document_id=doc_id,
                        content=document,
                        metadata=metadata,
                        relevance_score=similarity_score,
                        confidence=confidence,
                        search_timestamp=datetime.now()
                    ))
            
            # Sort by confidence
            search_results.sort(key=lambda x: x.confidence, reverse=True)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def get_ai_answer(self, query: str, context: List[SearchResult]) -> Dict[str, Any]:
        """Generate AI answer with completeness checking"""
        try:
            if not context:
                return {
                    "answer": "I don't have enough information to answer your question.",
                    "confidence": 0.0,
                    "completeness": "incomplete",
                    "missing_info": "No relevant documents found in the knowledge base.",
                    "suggestions": ["Upload relevant documents", "Refine your search query"]
                }
            
            # Prepare context for AI
            context_text = "\n\n".join([
                f"Document {i+1}:\n{result.content[:500]}..."
                for i, result in enumerate(context[:3])  # Use top 3 results
            ])
            
            # Generate answer with completeness checking
            prompt = f"""
            Based on the following context, answer the question. If you cannot provide a complete answer, explain what information is missing.
            
            Question: {query}
            
            Context:
            {context_text}
            
            Provide your response in the following JSON format:
            {{
                "answer": "Your answer here",
                "confidence": 0.0-1.0,
                "completeness": "complete|partial|incomplete",
                "missing_info": "What information is missing (if any)",
                "sources_used": ["list of document IDs used"],
                "suggestions": ["suggestions for getting more information"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "answer": response.choices[0].message.content,
                    "confidence": 0.7,
                    "completeness": "partial",
                    "missing_info": "Could not parse structured response",
                    "suggestions": ["Check the generated answer manually"]
                }
            
        except Exception as e:
            logger.error(f"AI answer generation failed: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "confidence": 0.0,
                "completeness": "error",
                "missing_info": "System error occurred",
                "suggestions": ["Try again later", "Contact support"]
            }
    
    async def check_completeness(self, query: str, answer: str, context: List[SearchResult]) -> CompletenessCheck:
        """Check if the answer is complete based on available information"""
        try:
            # Use AI to analyze completeness
            prompt = f"""
            Analyze the completeness of this answer for the given question:
            
            Question: {query}
            Answer: {answer}
            
            Available Context: {len(context)} documents
            
            Rate the completeness and identify gaps:
            1. Completeness Level: complete|partial|incomplete
            2. Confidence: 0.0-1.0
            3. Missing Information: List what's missing
            4. Quality Score: 0.0-1.0
            5. Recommendations: How to improve
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.2
            )
            
            # Extract completeness information
            content = response.choices[0].message.content
            
            # Simple parsing (in production, use structured output)
            completeness = "partial"
            if "complete" in content.lower():
                completeness = "complete"
            elif "incomplete" in content.lower():
                completeness = "incomplete"
            
            # Extract confidence from text
            confidence = 0.7  # Default
            if "confidence:" in content.lower():
                try:
                    conf_text = content.lower().split("confidence:")[1].split("\n")[0]
                    confidence = float(conf_text.strip())
                except:
                    pass
            
            return CompletenessCheck(
                completeness_level=completeness,
                confidence=confidence,
                missing_information=content,
                quality_score=confidence,
                recommendations=content
            )
            
        except Exception as e:
            logger.error(f"Completeness check failed: {str(e)}")
            return CompletenessCheck(
                completeness_level="unknown",
                confidence=0.0,
                missing_information="Error occurred during analysis",
                quality_score=0.0,
                recommendations="Try again later"
            )
    
    async def suggest_enrichment(self, query: str, current_results: List[SearchResult], 
                                completeness_check: CompletenessCheck) -> List[EnrichmentSuggestion]:
        """Suggest ways to enrich the knowledge base"""
        try:
            suggestions = []
            
            # Analyze current gaps
            if completeness_check.completeness_level == "incomplete":
                    suggestions.append(EnrichmentSuggestion(
                    type="document_upload",
                    description="Upload additional documents related to your query",
                    priority="high",
                    expected_impact="high"
                ))
            
            if completeness_check.confidence < 0.7:
                suggestions.append(EnrichmentSuggestion(
                    type="additional_sources",
                    description="Include more diverse sources for better coverage",
                    priority="medium",
                    expected_impact="medium"
                ))
            
            # Check for document variety
            if current_results:
                doc_types = set(result.metadata.get("document_type", "unknown") for result in current_results)
                if len(doc_types) < 2:
                    suggestions.append(EnrichmentSuggestion(
                        type="document_diversity",
                        description="Add different types of documents (reports, data, articles)",
                        priority="medium",
                        expected_impact="medium"
                    ))
            
            # Suggest external data sources
            suggestions.append(EnrichmentSuggestion(
                type="external_integration",
                description="Integrate with external APIs for real-time data",
                priority="low",
                expected_impact="high"
            ))
            
            # Suggest user feedback collection
            suggestions.append(EnrichmentSuggestion(
                type="user_feedback",
                description="Collect user ratings to improve answer quality",
                priority="low",
                expected_impact="medium"
            ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Enrichment suggestion failed: {str(e)}")
            return []

    async def _generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            if self.embedding_model:
                embeddings = self.embedding_model.encode(text)
                return embeddings.tolist()
            else:
                # Fallback to simple TF-IDF like approach
                words = text.lower().split()
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Simple vector representation (not as good as proper embeddings)
                return list(word_freq.values())[:384]  # Pad to 384 dimensions
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return [0.0] * 384  # Return zero vector
    
    def _calculate_confidence(self, similarity_score: float, metadata: Dict[str, Any]) -> float:
        """Calculate confidence score based on similarity and metadata quality"""
        base_confidence = similarity_score
        
        # Boost confidence based on metadata quality
        quality_boost = 0.0
        
        # Document recency
        if "upload_date" in metadata:
            try:
                upload_date = datetime.fromisoformat(metadata["upload_date"])
                days_old = (datetime.now() - upload_date).days
                if days_old < 30:
                    quality_boost += 0.1
                elif days_old < 90:
                    quality_boost += 0.05
            except:
                pass
        
        # Document type preference
        if metadata.get("document_type") in ["report", "research", "official"]:
            quality_boost += 0.1
        
        # Source reliability
        if metadata.get("source_reliability") == "high":
            quality_boost += 0.15
        
        # Calculate final confidence
        final_confidence = min(1.0, base_confidence + quality_boost)
        return round(final_confidence, 3)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            doc_count = self.documents_collection.count()
            embedding_count = self.embeddings_collection.count()
            
            return {
                "total_documents": doc_count,
                "total_embeddings": embedding_count,
                "last_updated": datetime.now().isoformat(),
                "status": "healthy" if doc_count > 0 else "empty"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
