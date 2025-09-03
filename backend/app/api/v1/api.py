from fastapi import APIRouter
from app.api.v1.endpoints import documents, search, tasks, enhanced_tasks, enhanced_search, enhanced_dashboard

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)
api_router.include_router(
    enhanced_tasks.router,
    prefix="/enhanced-tasks",
    tags=["enhanced-tasks"]
)
api_router.include_router(
    enhanced_search.router,
    prefix="/enhanced-search",
    tags=["enhanced-search"]
)
api_router.include_router(
    enhanced_dashboard.router,
    prefix="/enhanced-dashboard",
    tags=["enhanced-dashboard"]
)
