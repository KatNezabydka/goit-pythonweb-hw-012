from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactModel, ContactUpdate
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts for the authenticated user.

    This endpoint fetches the user's contacts with pagination support.

    Args:
        skip (int): The number of contacts to skip (for pagination). Default is 0.
        limit (int): The maximum number of contacts to return. Default is 100.
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts belonging to the authenticated user.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Search contacts based on provided filters (first name, last name, or email).

    This endpoint allows searching for contacts by their first name, last name, or email.

    Args:
        first_name (str): The first name of the contact (optional).
        last_name (str): The last name of the contact (optional).
        email (str): The email of the contact (optional).
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts matching the search criteria.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(user, first_name, last_name, email)
    return contacts


@router.get("/upcoming_birthday", response_model=List[ContactResponse])
async def get_contacts_upcoming_birthday(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with upcoming birthdays for the authenticated user.

    This endpoint returns contacts whose birthdays are coming up in the near future.

    Args:
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_upcoming_birthday(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Retrieve a specific contact by ID for the authenticated user.

    This endpoint fetches a single contact by its ID for the authenticated user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        ContactResponse: The contact details.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
        body: ContactModel,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Create a new contact for the authenticated user.

    This endpoint allows creating a new contact and storing it in the database.

    Args:
        body (ContactModel): The contact data to be created.
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        ContactResponse: The created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        body: ContactUpdate,
        contact_id: int, db:
        AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Update an existing contact for the authenticated user.

    This endpoint updates the details of a contact.

    Args:
        body (ContactUpdate): The updated contact data.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        ContactResponse: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Remove a contact for the authenticated user.

    This endpoint allows deleting a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session.
        user (User): The current authenticated user.

    Returns:
        ContactResponse: The deleted contact details.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact