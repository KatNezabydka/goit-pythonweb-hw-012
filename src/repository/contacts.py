from operator import or_
from datetime import timedelta, date
from sqlalchemy import func, select
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> Sequence[Contact]:
        stmt = select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict().items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(
        self, user: User, first_name: str = None, last_name: str = None, email: str = None
    ) -> Sequence[Contact]:
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
        today = date.today()
        next_week = today + timedelta(days=7)

        stmt = (
            select(Contact)
            .where(Contact.user_id == user.id)
            .filter(
                func.extract("month", Contact.birthday) == today.month,
                func.extract("day", Contact.birthday) >= today.day,
                (
                    func.extract("month", Contact.birthday)
                    == func.extract("month", next_week)
                )
                | (func.extract("month", Contact.birthday) == today.month),
            )
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()