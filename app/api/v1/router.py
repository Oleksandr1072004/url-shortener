from fastapi import APIRouter
from app.api.v1.endpoints import users, links

api_router = APIRouter()
api_router.include_router(users.router, prefix="/auth", tags=["auth"])
api_router.include_router(links.router, prefix="/links", tags=["links"])