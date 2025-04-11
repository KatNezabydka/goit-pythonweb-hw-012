import json
from pathlib import Path

from fastapi import APIRouter, Request, BackgroundTasks, Depends, HTTPException, status, Form
from fastapi import Body
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.conf.config import settings
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token, create_email_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email, send_reset_email
from src.database.redis import redis_client

router = APIRouter(prefix="/auth", tags=["auth"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserCreate,
        background_tasks: BackgroundTasks,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    This endpoint registers a new user and sends a verification email.
    If the email or username is already taken, it returns a 409 Conflict response.

    Args:
        user_data (UserCreate): The data required to create a new user (email, username, password).
        background_tasks (BackgroundTasks): Allows running background tasks like sending an email.
        request (Request): The HTTP request object.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        User: The newly created user object.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    """
    Log in a user and generate an access token.

    This endpoint validates the user's credentials and returns an access token
    that can be used for authentication in subsequent requests.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        Token: The access token that can be used for authorization.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address not verified",
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db), ):
    """
    Confirm the user's email address using the verification token.

    This endpoint verifies the email address of the user using a token.
    If the email is already confirmed, it returns a message indicating that.

    Args:
        token (str): The email verification token.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        dict: A message indicating whether the email was successfully confirmed or already confirmed.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email Verified"}


@router.post("/request_email")
async def request_email(
        body: RequestEmail,
        background_tasks: BackgroundTasks,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Request a new email verification link.

    This endpoint sends a new email verification link to the user if their email is not yet confirmed.

    Args:
        body (RequestEmail): The email of the user requesting the verification.
        background_tasks (BackgroundTasks): Allows sending a background task for email sending.
        request (Request): The HTTP request object.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        dict: A message indicating whether an email was sent or not.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User with this email does not exist"
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Please check your email for verification"}


@router.post("/forgot-password")
async def forgot_password(
        email: str,
        background_tasks: BackgroundTasks,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Send a password reset link to the user's email.

    This endpoint sends a password reset link to the user's email if they exist in the database.

    Args:
        email (EmailStr): The email address of the user requesting a password reset.
        background_tasks (BackgroundTasks): Allows sending a background task for email sending.
        request (Request): The HTTP request object.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        dict: A message indicating that the reset email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    token_data = {"sub": user.email}
    token = create_email_token(token_data)

    user_schema = User.model_validate(user)
    await redis_client.set(token, json.dumps(user_schema.model_dump()), ex=settings.REDIS_EXPIRE_SECONDS)

    reset_link = f"{request.base_url}api/auth/reset-password?token={token}"

    background_tasks.add_task(send_reset_email, user.email, reset_link, user.username, request.base_url)

    return {"msg": "Password reset email sent"}


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    """
    Show the password reset form.

    This endpoint renders the password reset form for the user with the provided token.

    Args:
        request (Request): The HTTP request object.
        token (str): The password reset token.

    Returns:
        HTMLResponse: The rendered reset form.
    """
    return templates.TemplateResponse(request, "reset_form.html", {"token": token})


@router.post("/reset-password")
async def reset_password(
        token: str = Form(...),
        new_password: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Reset the user's password using the reset token.

    This endpoint resets the user's password if the token is valid and not expired.

    Args:
        token (str): The password reset token.
        new_password (str): The new password for the user.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        dict: A message indicating whether the password was successfully reset.
    """
    try:
        await get_email_from_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    cached_user_data = await redis_client.get(token)
    if not cached_user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is invalid or expired"
        )

    user_data = User.model_validate(json.loads(cached_user_data))

    user_service = UserService(db)
    user = await user_service.get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed_password = Hash().get_password_hash(new_password)
    user.hashed_password = hashed_password

    await db.commit()

    await redis_client.delete(token)

    return {"msg": "Password successfully reset"}
