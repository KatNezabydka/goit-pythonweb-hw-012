from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas import ContactModel, ContactUpdate


def _handle_integrity_error(e: IntegrityError):
    """
    Handles IntegrityError exceptions related to unique constraints on email or phone fields.

    Args:
        e (IntegrityError): The exception raised due to a violation of integrity constraints.

    Raises:
        HTTPException: With a conflict status code if the error relates to an existing email or phone number.
        HTTPException: With a bad request status code for other integrity errors.
    """
    error_message = str(e.orig).lower()
    if "email" in error_message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A contact with this email already exists."
        )
    if "phone" in error_message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A contact with this phone number already exists."
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Data integrity error."
    )


class ContactService:
    """
    Service class for handling contact-related business logic.

    Provides methods to create, read, update, delete, and search contacts.
    Handles validation and integrity errors during these operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a database session.

        Args:
            db (AsyncSession): The database session to interact with the repository.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """
        Creates a new contact.

        Args:
            body (ContactModel): The contact information to be created.
            user (User): The user creating the contact.

        Returns:
            ContactModel: The created contact.

        Raises:
            HTTPException: If there is an integrity error (e.g., duplicate email or phone number).
        """
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieves a list of contacts for the specified user, with pagination.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to retrieve.

        Returns:
            List[ContactModel]: A list of contacts.
        """
        return await self.repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a single contact by its ID for the specified user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user requesting the contact.

        Returns:
            ContactModel: The requested contact, if found.

        Raises:
            HTTPException: If the contact does not belong to the user or is not found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
        Updates the details of an existing contact.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The updated contact information.
            user (User): The user updating the contact.

        Returns:
            ContactModel: The updated contact.

        Raises:
            HTTPException: If there is an integrity error (e.g., duplicate email or phone number).
        """
        try:
            return await self.repository.update_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Deletes a contact.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user requesting the deletion.

        Returns:
            ContactModel: The deleted contact.

        Raises:
            HTTPException: If the contact does not belong to the user or is not found.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def search_contacts(self, user: User, first_name: str = None, last_name: str = None, email: str = None):
        """
        Searches for contacts based on provided filters.

        Args:
            user (User): The user performing the search.
            first_name (str, optional): The first name to search for.
            last_name (str, optional): The last name to search for.
            email (str, optional): The email to search for.

        Returns:
            List[ContactModel]: A list of contacts that match the search criteria.
        """
        return await self.repository.search_contacts(user, first_name, last_name, email)

    async def get_contacts_upcoming_birthday(self, user: User):
        """
        Retrieves a list of contacts with upcoming birthdays for the specified user.

        Args:
            user (User): The user requesting the list of contacts.

        Returns:
            List[ContactModel]: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_contacts_upcoming_birthday(user)