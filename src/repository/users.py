from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        Args:
            body (UserCreate): The data model containing user information (excluding password).
            avatar (str, optional): The avatar URL for the user. Defaults to None.

        Returns:
            User: The created user object with all fields populated.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm a user's email address.

        Args:
            email (str): The email address of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL for an existing user.

        Args:
            email (str): The email address of the user whose avatar URL is being updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object with the new avatar URL.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
        return user