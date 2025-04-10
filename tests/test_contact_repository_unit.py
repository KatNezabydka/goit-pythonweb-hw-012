import pytest
from unittest.mock import AsyncMock, MagicMock
from src.repository.contacts import ContactRepository
from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


@pytest.fixture
def session_mock():
    return AsyncMock()


@pytest.fixture
def contact_repo(session_mock):
    return ContactRepository(session_mock)


@pytest.fixture
def fake_user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.fixture
def fake_contact():
    return Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", user_id=1)


@pytest.mark.asyncio
async def test_get_contacts(contact_repo, session_mock, fake_user, fake_contact):
    # Мокируем execute() для возвращения результата
    mock_scalars = AsyncMock()
    mock_scalars.all = AsyncMock(return_value=[fake_contact])
    session_mock.execute.return_value.scalars = mock_scalars

    result = await contact_repo.get_contacts(skip=0, limit=10, user=fake_user)
    assert result == [fake_contact]


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repo, session_mock, fake_user, fake_contact):
    # Мокируем execute() для возвращения fake_contact
    session_mock.execute.return_value.scalar_one_or_none.return_value = fake_contact
    result = await contact_repo.get_contact_by_id(contact_id=1, user=fake_user)
    assert result == fake_contact


@pytest.mark.asyncio
async def test_create_contact(contact_repo, session_mock, fake_user, fake_contact):
    session_mock.refresh = AsyncMock()
    contact_repo.get_contact_by_id = AsyncMock(return_value=fake_contact)

    contact_data = ContactModel(
        first_name="John", last_name="Doe", email="john@example.com", phone="123", birthday="2000-01-01"
    )
    result = await contact_repo.create_contact(contact_data, user=fake_user)

    session_mock.add.assert_called_once()
    session_mock.commit.assert_called()
    session_mock.refresh.assert_called()
    assert result == fake_contact


@pytest.mark.asyncio
async def test_update_contact(contact_repo, session_mock, fake_user, fake_contact):
    session_mock.refresh = AsyncMock()
    contact_repo.get_contact_by_id = AsyncMock(return_value=fake_contact)

    update_data = ContactUpdate(first_name="Jane")
    result = await contact_repo.update_contact(contact_id=1, body=update_data, user=fake_user)

    assert result.first_name == "Jane"
    session_mock.commit.assert_called()
    session_mock.refresh.assert_called()


@pytest.mark.asyncio
async def test_remove_contact(contact_repo, session_mock, fake_user, fake_contact):
    contact_repo.get_contact_by_id = AsyncMock(return_value=fake_contact)

    result = await contact_repo.remove_contact(contact_id=1, user=fake_user)
    session_mock.delete.assert_called_once_with(fake_contact)
    session_mock.commit.assert_called_once()
    assert result == fake_contact


@pytest.mark.asyncio
async def test_search_contacts(contact_repo, session_mock, fake_user, fake_contact):
    # Мокируем execute() для возвращения результата
    mock_scalars = AsyncMock()
    mock_scalars.all = AsyncMock(return_value=[fake_contact])
    session_mock.execute.return_value.scalars = mock_scalars

    result = await contact_repo.search_contacts(user=fake_user, first_name="John")

    assert isinstance(result, list)
    assert result[0] == fake_contact


@pytest.mark.asyncio
async def test_get_contacts_upcoming_birthday(contact_repo, session_mock, fake_user, fake_contact):
    # Мокируем execute() для возвращения результата
    mock_scalars = AsyncMock()
    mock_scalars.all = AsyncMock(return_value=[fake_contact])
    session_mock.execute.return_value.scalars = mock_scalars

    result = await contact_repo.get_contacts_upcoming_birthday(user=fake_user)

    assert isinstance(result, list)
    assert result[0] == fake_contact