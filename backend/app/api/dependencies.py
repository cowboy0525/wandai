from typing import Generator
from fastapi import Depends
from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
from app.services.enhanced_agent_orchestrator import EnhancedAgentOrchestrator
from app.services.knowledge_base import KnowledgeBase

# Service instances (in production, these would be managed by a dependency container)
_enhanced_knowledge_base = None
_enhanced_agent_orchestrator = None
_knowledge_base = None

def get_enhanced_knowledge_base() -> EnhancedKnowledgeBase:
    """Get EnhancedKnowledgeBase service instance"""
    global _enhanced_knowledge_base
    if _enhanced_knowledge_base is None:
        _enhanced_knowledge_base = EnhancedKnowledgeBase()
    return _enhanced_knowledge_base

def get_enhanced_agent_orchestrator() -> EnhancedAgentOrchestrator:
    """Get EnhancedAgentOrchestrator service instance"""
    global _enhanced_agent_orchestrator
    if _enhanced_agent_orchestrator is None:
        _enhanced_agent_orchestrator = EnhancedAgentOrchestrator(get_enhanced_knowledge_base())
    return _enhanced_agent_orchestrator

def get_knowledge_base() -> KnowledgeBase:
    """Get KnowledgeBase service instance (legacy)"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base

# Dependency functions for use in endpoints
def enhanced_knowledge_base_dependency() -> Generator[EnhancedKnowledgeBase, None, None]:
    """Dependency for EnhancedKnowledgeBase service"""
    yield get_enhanced_knowledge_base()

def enhanced_agent_orchestrator_dependency() -> Generator[EnhancedAgentOrchestrator, None, None]:
    """Dependency for EnhancedAgentOrchestrator service"""
    yield get_enhanced_agent_orchestrator()

# Legacy dependencies for backward compatibility
def knowledge_base_dependency() -> Generator[KnowledgeBase, None, None]:
    """Legacy dependency for KnowledgeBase service"""
    yield get_knowledge_base()

def agent_orchestrator_dependency() -> Generator[EnhancedAgentOrchestrator, None, None]:
    """Legacy dependency for AgentOrchestrator service (now returns EnhancedAgentOrchestrator)"""
    yield get_enhanced_agent_orchestrator()
