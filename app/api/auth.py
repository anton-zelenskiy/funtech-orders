from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import create_access_token
from app.db.base import get_db_session
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register/", response_model=UserResponse)
@limiter.limit(settings.rate_limit_default)
async def register(
    request: Request,
    body: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    repository = UserRepository(session)
    existing = await repository.get_by_email(body.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await register_user(repository, body.email, body.password)
    return UserResponse.model_validate(user)


@router.post("/token/", response_model=Token)
@limiter.limit(settings.rate_limit_default)
async def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    repository = UserRepository(session)
    user = await authenticate_user(repository, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
