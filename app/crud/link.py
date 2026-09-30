import string
import random
import json

from sqlalchemy import select

from app.db.redis_client import redis_client
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.link import Link
from app.schemas.link import LinkCreate


CACHE_PREFIX = "urlshortener:link"
CACHE_TTL = 300  # 5 хвилин

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def _cache_key(short_code: str) -> str:
    return f"{CACHE_PREFIX}:{short_code}"


async def create_short_link(db: AsyncSession, link_in: LinkCreate, user_id: int) -> Link:
    # Генеруємо унікальний код (в реальності тут потрібен цикл перевірки на колізії)
    short_code = generate_short_code()

    db_link = Link(
        original_url=str(link_in.original_url),
        short_code=short_code,
        user_id=user_id
    )
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link


CACHE_TTL = 300  # 5 хвилин


async def get_link_by_code(db: AsyncSession, short_code: str) -> Link | None:
    """Чистий запит до БД."""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    return result.scalar_one_or_none()


async def get_link_by_code_cached(db, short_code: str):
    # Спробувати кеш, але не падати при помилці
    try:
        cached = await redis_client.get(_cache_key(short_code))
        if cached:
            return json.loads(cached), "HIT"
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}, falling back to DB")

    link = await get_link_by_code(db, short_code)
    try:
        if link:
            await redis_client.setex(...)
    except Exception:
        pass  # Кеш недоступний — просто не кешуємо
    return link, "MISS"



async def increment_click_counter(link_id: int) -> int:
    """Атомарний лічильник у Redis (shared, не in-memory)."""
    counter_key = f"clicks:{link_id}"
    return await redis_client.incr(counter_key)


async def get_click_count(link_id: int) -> int:
    """Читає кількість кліків з Redis."""
    counter_key = f"clicks:{link_id}"
    value = await redis_client.get(counter_key)
    return int(value) if value else 0