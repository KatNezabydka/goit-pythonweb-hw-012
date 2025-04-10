import pytest
from unittest.mock import AsyncMock, MagicMock

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserCreate


@pytest.fixture
def session_mock():
    return AsyncMock()


@pytest.fixture
def repository(session_mock):
    return UserRepository(session_mock)


@pytest.fixture
def fake_user():
    return User(id=1, username="testuser", email="test@example.com", avatar=None, confirmed=False)


@pytest.mark.asyncio
async def test_get_user_by_id(repository, session_mock, fake_user):
    session_mock.execute.return_value.scalar_one_or_none.return_value = fake_user
    result = await repository.get_user_by_id(1)
    assert result == fake_user
    session_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_username(repository, session_mock, fake_user):
    session_mock.execute.return_value.scalar_one_or_none.return_value = fake_user
    result = await repository.get_user_by_username("testuser")
    assert result == fake_user
    session_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_email(repository, session_mock, fake_user):
    session_mock.execute.return_value.scalar_one_or_none.return_value = fake_user
    result = await repository.get_user_by_email("test@example.com")
    assert result == fake_user
    session_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_user(repository, session_mock):
    user_create = UserCreate(username="testuser", email="test@example.com", password="hashed_pass")
    # Мокаємо refresh, щоб не падало
    session_mock.refresh = AsyncMock()
    # Мокаємо get_user_by_id всередині метода
    repository.get_user_by_id = AsyncMock(return_value=User(id=1, username="testuser", email="test@example.com"))

    result = await repository.create_user(user_create, avatar="http://avatar.url")
    assert result.username == user_create.username
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called()
    session_mock.refresh.assert_called()


@pytest.mark.asyncio
async def test_confirmed_email(repository, session_mock, fake_user):
    repository.get_user_by_email = AsyncMock(return_value=fake_user)
    await repository.confirmed_email("test@example.com")
    assert fake_user.confirmed is True
    session_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_avatar_url(repository, session_mock, fake_user):
    repository.get_user_by_email = AsyncMock(return_value=fake_user)
    session_mock.refresh = AsyncMock()
    updated_user = await repository.update_avatar_url("test@example.com", "http://new.avatar")
    assert updated_user.avatar == "http://new.avatar"
    session_mock.commit.assert_called_once()
    session_mock.refresh.assert_called_once()