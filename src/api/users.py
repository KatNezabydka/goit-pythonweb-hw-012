from fastapi import APIRouter, Request, UploadFile, Depends
from fastapi.params import File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas import User
from src.services.auth import get_current_user, check_admin
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.

    This endpoint allows the user to retrieve their own profile data. It is rate-limited to 10 requests per minute.

    Args:
        request (Request): The HTTP request object.
        user (User): The current authenticated user, injected via dependency.

    Returns:
        User: The authenticated user's profile.

    Rate Limiting:
        - No more than 10 requests per minute.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
        file: UploadFile = File(),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        admin_user: User = Depends(check_admin)
):
    """
    Update the profile avatar for the authenticated user.

    This endpoint allows the authenticated user (or an admin) to upload and update their avatar image.

    Args:
        file (UploadFile): The avatar image file to upload.
        user (User): The current authenticated user, injected via dependency.
        db (AsyncSession): The database session.
        admin_user (User): The admin user dependency to check if the request is made by an admin.

    Returns:
        User: The updated user profile with the new avatar URL.

    Raises:
        HTTPException: If the user is not an admin and tries to access the route (if admin_user is used inappropriately).
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user