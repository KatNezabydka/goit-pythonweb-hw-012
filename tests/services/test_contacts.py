import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from src.services.contacts import ContactService, _handle_integrity_error
from src.schemas import ContactModel, ContactUpdate
from src.database.models import User


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def contact_service(mock_db):
    return ContactService(db=mock_db)


@pytest.fixture
def fake_user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.fixture
def contact_data():
    return ContactModel(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday="1990-01-01"
    )


@pytest.fixture
def update_data():
    return ContactUpdate(
        first_name="Johnny"
    )


def test_handle_integrity_error_email():
    with pytest.raises(Exception) as exc:
        _handle_integrity_error(IntegrityError(
            statement=None, params=None, orig=Exception("email already exists")
        ))
    assert "email" in str(exc.value.detail).lower()


def test_handle_integrity_error_phone():
    with pytest.raises(Exception) as exc:
        _handle_integrity_error(IntegrityError(
            statement=None, params=None, orig=Exception("phone already exists")
        ))
    assert "phone" in str(exc.value.detail).lower()


def test_handle_integrity_error_other():
    with pytest.raises(Exception) as exc:
        _handle_integrity_error(IntegrityError(
            statement=None, params=None, orig=Exception("something else")
        ))
    assert "data integrity error" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_create_contact(contact_service, contact_data, fake_user):
    contact_service.repository.create_contact = AsyncMock(return_value=contact_data)
    result = await contact_service.create_contact(contact_data, fake_user)
    assert result == contact_data


@pytest.mark.asyncio
async def test_create_contact_integrity_error(contact_service, contact_data, fake_user):
    contact_service.repository.create_contact = AsyncMock(side_effect=IntegrityError(
        statement=None, params=None, orig=Exception("email")
    ))
    contact_service.repository.db.rollback = AsyncMock()

    with pytest.raises(Exception) as exc:
        await contact_service.create_contact(contact_data, fake_user)
    assert "email" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_contacts(contact_service, fake_user):
    contact_service.repository.get_contacts = AsyncMock(return_value=[1, 2])
    result = await contact_service.get_contacts(0, 10, fake_user)
    assert result == [1, 2]


@pytest.mark.asyncio
async def test_get_contact(contact_service, fake_user):
    contact_service.repository.get_contact_by_id = AsyncMock(return_value=123)
    result = await contact_service.get_contact(1, fake_user)
    assert result == 123


@pytest.mark.asyncio
async def test_update_contact(contact_service, update_data, fake_user):
    contact_service.repository.update_contact = AsyncMock(return_value="updated")
    result = await contact_service.update_contact(1, update_data, fake_user)
    assert result == "updated"


@pytest.mark.asyncio
async def test_update_contact_integrity_error(contact_service, update_data, fake_user):
    contact_service.repository.update_contact = AsyncMock(side_effect=IntegrityError(
        statement=None, params=None, orig=Exception("phone")
    ))
    contact_service.repository.db.rollback = AsyncMock()

    with pytest.raises(Exception) as exc:
        await contact_service.update_contact(1, update_data, fake_user)
    assert "phone" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_remove_contact(contact_service, fake_user):
    contact_service.repository.remove_contact = AsyncMock(return_value="deleted")
    result = await contact_service.remove_contact(1, fake_user)
    assert result == "deleted"


@pytest.mark.asyncio
async def test_search_contacts(contact_service, fake_user):
    contact_service.repository.search_contacts = AsyncMock(return_value=["match1", "match2"])
    result = await contact_service.search_contacts(fake_user, first_name="John")
    assert result == ["match1", "match2"]


@pytest.mark.asyncio
async def test_get_contacts_upcoming_birthday(contact_service, fake_user):
    contact_service.repository.get_contacts_upcoming_birthday = AsyncMock(return_value=["bday1", "bday2"])
    result = await contact_service.get_contacts_upcoming_birthday(fake_user)
    assert result == ["bday1", "bday2"]
