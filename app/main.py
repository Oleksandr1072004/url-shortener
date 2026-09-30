from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.middleware.instance_id import InstanceIDMiddleware
from app.db.redis_client import close_redis, redis_client
from app.core.config import settings
from fastapi import Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Тільки перевірка підключень, БЕЗ створення таблиць
    try:
        await redis_client.ping()
        print(f"Instance {settings.INSTANCE_ID} connected to Redis")
    except Exception as e:
        print(f"Redis unavailable: {e}")

    yield

    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
app.add_middleware(InstanceIDMiddleware)


@app.get("/")
async def root():
    return {"message": "Welcome to URL Shortener API"}


@app.on_event("startup")
async def startup():
    await redis_client.ping()
    print(f"Instance {settings.INSTANCE_ID} connected to Redis")

@app.on_event("shutdown")
async def shutdown():
    await close_redis()


# @app.get("/health")
# async def health():
#     redis_ok = False
#     try:
#         await redis_client.ping()
#         redis_ok = True
#     except Exception:
#         pass
#
#     return {
#         "status": "ok" if redis_ok else "degraded",
#         "instance_id": settings.INSTANCE_ID,
#         "redis": redis_ok
#     }

@app.get("/health")
async def health():
    redis_ok = False
    db_ok = False
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    if not db_ok:
        raise HTTPException(status_code=503, detail="DB unavailable")
    return {
        "status": "ok",
        "instance_id": settings.INSTANCE_ID,
        "redis": redis_ok,
        "db": db_ok,
    }