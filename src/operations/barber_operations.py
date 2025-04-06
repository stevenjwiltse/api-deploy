from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Barber
from modules.user.models import User
from modules.user.barber_schema import BarberCreate, BarberResponse
from typing import List

'''
Contains methods for barber creation and retrieval.
Updating a Barber's information should be done using the User ID in the user router.
Barbers should be deleted from the system using the user router as well.
'''
class BarberOperations:

    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Create a Barber
    async def create_barber(self, user: BarberCreate) -> Barber:
        result = await self.db.execute(select(User).filter(User.user_id == user.user_id))
        first_result = result.scalars().first()

        # Check to make sure the User ID provided links to a valid User
        if not first_result:
            raise HTTPException(
                status_code = 400,
                detail="User not found with provided ID"
            )
        
        existing_barber = await self.db.execute(select(Barber).filter(Barber.user_id == user.user_id))
        first_existing_barber = existing_barber.scalars().first()

        # Make sure the user is not already a barber
        if first_existing_barber:
            raise HTTPException(
                status_code=400,
                detail="User is already a barber"
            )
        
        try:
            barber = Barber(user_id=user.user_id)
            self.db.add(barber)
            await self.db.commit()
            await self.db.refresh(barber)

            return barber

        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    # Retrieve all barbers
    async def get_all_barbers(self, page: int, limit: int) -> List[Barber]:
        try: 
            # Calculate offset for SQL query
            offset = (page - 1) * limit

            result = await self.db.execute(select(Barber).limit(limit).offset(offset))
            return result.scalars().all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
        
    # Retrieve a specific barber by their Barber ID
    async def get_barber_by_id(self, barber_id: int):
        try:
            result = await self.db.execute(select(Barber).filter(Barber.barber_id == barber_id))
            first_result = result.scalars().first()
            if not first_result:
                raise HTTPException(status_code = 400, detail="No barber found with provided ID")
            else:
                return first_result
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
