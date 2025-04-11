import pytest
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.models import User
from src.services.users import UserService
from src.schemas import UserCreate


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)


@pytest.mark.asyncio
@patch("src.services.users.UserRepository")
@patch("libgravatar.Gravatar")
async def test_create_user(mock_gravatar, MockUserRepository, db):
    mock_repo = MockUserRepository.return_value
    mock_repo.create_user = AsyncMock(
        return_value=User(id=1, username="testuser", email="test@example.com", avatar="http://avatar.com")
    )

    user_service = UserService(db=db)
    mock_gravatar_instance = mock_gravatar.return_value
    fake_avatar_url = "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0"
    mock_gravatar_instance.get_image = AsyncMock(return_value=fake_avatar_url)
    user_data = UserCreate(username="testuser", email="test@example.com", password="securepassword")
    created_user = await user_service.create_user(user_data)
    mock_repo.create_user.assert_called_once_with(user_data, fake_avatar_url)

    assert created_user.email == "test@example.com"
    assert created_user.username == "testuser"


@pytest.mark.asyncio
@patch("src.services.users.UserRepository")
async def test_get_user_by_id(MockUserRepository, db):
    mock_repo = MockUserRepository.return_value
    mock_repo.get_user_by_id = AsyncMock(return_value=User(id=1, username="testuser", email="test@example.com"))
    user_service = UserService(db=db)
    user = await user_service.get_user_by_id(1)
    mock_repo.get_user_by_id.assert_called_once_with(1)

    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
@patch("src.services.users.UserRepository")
async def test_get_user_by_username(MockUserRepository, db):
    mock_repo = MockUserRepository.return_value
    mock_repo.get_user_by_username = AsyncMock(return_value=User(id=1, username="testuser", email="test@example.com"))
    user_service = UserService(db=db)
    user = await user_service.get_user_by_username("testuser")
    mock_repo.get_user_by_username.assert_called_once_with("testuser")

    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
@patch("src.services.users.UserRepository")
async def test_update_avatar(MockUserRepository, db):
    mock_repo = MockUserRepository.return_value
    mock_repo.update_avatar_url = AsyncMock(
        return_value=User(id=1, username="testuser", email="test@example.com", avatar="http://new-avatar.com"))

    user_service = UserService(db=db)
    user = await user_service.update_avatar_url("test@example.com", "http://new-avatar.com")
    mock_repo.update_avatar_url.assert_called_once_with("test@example.com", "http://new-avatar.com")

    assert user.avatar == "http://new-avatar.com"
