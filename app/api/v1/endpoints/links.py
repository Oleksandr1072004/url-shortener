from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud import link as crud_link
from app.schemas.link import LinkCreate, LinkResponse

router = APIRouter()


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
        link_in: LinkCreate,
        db: AsyncSession = Depends(deps.get_db),
        current_user=Depends(deps.get_current_user)
):
    """Створити коротке посилання."""
    return await crud_link.create_short_link(db, link_in, current_user.id)


@router.get("/{short_code}")
async def redirect_to_original(
        short_code: str,
        db: AsyncSession = Depends(deps.get_db)
):
    """Редірект на оригінальний URL (Пікове навантаження!)."""
    link = await crud_link.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Тут можна асинхронно записати клік у чергу або БД
    # await crud_link.log_click(db, link.id)

    return RedirectResponse(url=link.original_url)


@router.get("/", response_model=list[LinkResponse])
async def read_links(
        db: AsyncSession = Depends(deps.get_db),
        current_user=Depends(deps.get_current_user)
):
    """Отримати всі посилання користувача."""
    return await crud_link.get_user_links(db, current_user.id)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
        link_id: int,
        db: AsyncSession = Depends(deps.get_db),
        current_user=Depends(deps.get_current_user)
):
    """Видалити посилання."""
    await crud_link.delete_link(db, link_id, current_user.id)
    return None


@router.get("/{link_id}/stats")
async def get_link_stats(
        link_id: int,
        db: AsyncSession = Depends(deps.get_db),
        current_user=Depends(deps.get_current_user)
):
    """Отримати статистику кліків."""
    return await crud_link.get_stats(db, link_id)


@router.get("/{short_code}")
async def redirect(short_code: str, response: Response, db=Depends(deps.get_db)):
    link, cache_status = await crud_link.get_link_by_code_cached(db, short_code)
    if not link:
        raise HTTPException(404, "Not found")
    response.headers["X-Cache"] = cache_status  # HIT / MISS
    return RedirectResponse(url=link.original_url)