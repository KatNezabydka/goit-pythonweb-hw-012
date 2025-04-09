from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate

class UserService:
    """
    Service layer for handling user-related operations such as user creation,
    fetching users by different attributes (ID, username, email), and updating
    the user's avatar URL.

    Attributes:
        repository (UserRepository): The repository used for database operations related to users.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.

        Args:
            db (AsyncSession): The database session used for interacting with the database.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user with the provided user data and attempts to fetch a Gravatar
        image using the user's email.

        If Gravatar fetch fails, the avatar is set to `None`.

        Args:
            body (UserCreate): The user data used for creating the new user.

        Returns:
            User: The created user object with the associated avatar URL (if available).
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Fetches a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user object, if found, else None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Fetches a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object, if found, else None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Fetches a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User: The user object, if found, else None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Marks the email address as confirmed in the database.

        Args:
            email (str): The email address to confirm.

        Returns:
            User: The user object with the updated confirmation status.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL of a user identified by their email.

        Args:
            email (str): The email of the user whose avatar needs to be updated.
            url (str): The new avatar URL to associate with the user.

        Returns:
            User: The user object with the updated avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)