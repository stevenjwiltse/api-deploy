from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.modules.user.models import User
from pydantic import EmailStr
from src.modules.user.user_schema import UserCreate, UserBase
from typing import List, Optional

'''
CRUD operations for interacting with users database table
'''
class UserOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Create a user
    async def create_user(self, user_data: UserCreate) -> User:
        new_user = User(**user_data.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    # Get all users
    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    # Get a specific user by their ID
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.user_id == user_id))
        return result.scalars().first()

    # Update user by their ID
    async def update_user(self, user_id: int, user_data: UserBase) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            return None
        for key, value in user_data.model_dump().items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # Delete a user by their ID
    async def delete_user(self, user_id: int) -> bool:
        result = await self.db.execute(select(User).filter(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True