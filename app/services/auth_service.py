from app.core.security import get_password_hash, verify_password
from app.db.repositories.user_repository import UserRepository
from app.db.models import User


async def register_user(
    repository: UserRepository,
    email: str,
    password: str,
) -> User:
    hashed = get_password_hash(password)
    return await repository.create(email=email, password=hashed)


async def authenticate_user(
    repository: UserRepository,
    email: str,
    password: str,
) -> User | None:
    user = await repository.get_by_email(email)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user
