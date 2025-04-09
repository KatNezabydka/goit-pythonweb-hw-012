from _operator import or_
from datetime import timedelta, date
from sqlalchemy import func
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> Sequence[Contact]:
        """
        Get a list of contacts owned by `user` with pagination.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            user (User): The owner of the contacts to retrieve.

        Returns:
            Sequence[Contact]: A list of contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a contact by its ID for the specified user.

        Args:
            contact_id (int): The ID of the contact.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The contact if found, or None if not.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contacts = await self.db.execute(stmt)
        return contacts.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for the specified user.

        Args:
            body (ContactModel): The data model for the new contact.
            user (User): The owner of the new contact.

        Returns:
            Contact: The created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
        """
        Update a contact for the specified user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The new data to update the contact.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The updated contact, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict().items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact for the specified user.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The removed contact, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(self, user: User, first_name: str = None, last_name: str = None, email: str = None) -> Sequence[Contact]:
        """
        Search for contacts by first name, last name, or email for the specified user.

        Args:
            user (User): The owner of the contacts.
            first_name (str, optional): The first name to search for.
            last_name (str, optional): The last name to search for.
            email (str, optional): The email to search for.

        Returns:
            Sequence[Contact]: A list of matching contacts.
        """
        stmt = select(Contact).where(Contact.user_id == user.id)

        filters = []

        if first_name:
            filters.append(Contact.first_name == first_name)
        if last_name:
            filters.append(Contact.last_name == last_name)
        if email:
            filters.append(Contact.email == email)

        if filters:
            condition = filters[0]
            for f in filters[1:]:
                condition = or_(condition, f)
            stmt = stmt.where(condition)

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contacts_upcoming_birthday(self, user: User) -> Sequence[Contact]:
        """
        Get contacts of the specified user who have birthdays within the next week.

        Args:
            user (User): The owner of the contacts.

        Returns:
            Sequence[Contact]: A list of contacts with upcoming birthdays.
        """
        today = date.today()

        next_week = today + timedelta(days=7)

        stmt = select(Contact).where(Contact.user_id == user.id).filter(
            func.extract('month', Contact.birthday) == today.month,
            func.extract('day', Contact.birthday) >= today.day,
            (func.extract('month', Contact.birthday) == func.extract('month', next_week)) |
            (func.extract('month', Contact.birthday) == today.month)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()