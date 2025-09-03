import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.knowledge_base import KnowledgeBase
from app.services.agent_orchestrator import AgentOrchestrator

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def knowledge_base():
    """KnowledgeBase service instance for testing"""
    return KnowledgeBase()

@pytest.fixture
def agent_orchestrator(knowledge_base):
    """AgentOrchestrator service instance for testing"""
    return AgentOrchestrator(knowledge_base)

@pytest.fixture
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
