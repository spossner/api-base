from fastapi import APIRouter

from app.api.v1.endpoints import items, users, jobs

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, tags=["jobs"])
