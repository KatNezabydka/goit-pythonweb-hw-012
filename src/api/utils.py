from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for database connection and FastAPI status.

    This endpoint checks the database connection by executing a simple SQL query (`SELECT 1`) to ensure the database is properly configured.
    If the database is connected and properly configured, it returns a welcome message.
    Otherwise, it raises an error indicating the database is not correctly set up or there is an issue connecting.

    Args:
        db (AsyncSession): The database session, injected via dependency.

    Returns:
        dict: A success message if the database is connected correctly.

    Raises:
        HTTPException: If there is an issue connecting to the database or the database is not configured properly, a `500 Internal Server Error` is raised.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )