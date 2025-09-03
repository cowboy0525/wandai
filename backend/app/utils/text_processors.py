import re
from typing import List, Dict, Any
from app.core.config import settings

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better embedding"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings
            sentence_endings = ['.', '!', '?', '\n\n']
            for ending in sentence_endings:
                pos = text.rfind(ending, start, end)
                if pos > start + chunk_size // 2:  # Only break if it's not too early
                    end = pos + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '-')
    
    return text.strip()

def extract_metadata(text: str) -> Dict[str, Any]:
    """Extract basic metadata from text"""
    metadata = {
        'word_count': len(text.split()),
        'char_count': len(text),
        'line_count': text.count('\n') + 1,
        'has_numbers': bool(re.search(r'\d', text)),
        'has_urls': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
    }
    
    # Try to extract title (first non-empty line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        metadata['first_line'] = lines[0][:100]  # First 100 chars
    
    return metadata

def calculate_relevance_score(query: str, text: str) -> float:
    """Calculate a simple relevance score between query and text"""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    
    if not query_words:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(query_words.intersection(text_words))
    union = len(query_words.union(text_words))
    
    if union == 0:
        return 0.0
    
    return intersection / union
