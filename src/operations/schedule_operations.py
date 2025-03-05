from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Schedule
from typing import List, Optional
from fastapi import HTTPException
from datetime import time

'''
CRUD operations for interacting with the schedule database table
'''

class ScheduleOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    #Create a new schedule block
    async def create_schedule(self, schedule_data) -> Schedule:
        try:
            new_schedule = Schedule(**schedule_data.dict())
            self.db.add(new_schedule)
            await self.db.commit()
            await self.db.refresh(new_schedule)
            return new_schedule
        except SQLAlchemyError:
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred during schedule block creation"
            )
        
    #Get all schedule blocks
    async def get_all_schedules(self) -> List[Schedule]:
        try:
            result = await self.db.execute(select(Schedule))
            return result.scalars().all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred while fetching schedule blocks"
            )
        
    #Get a specific schedule block by its id
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        try:
            result = await self.db.execute(select(Schedule).filter(Schedule.schedule_id == schedule_id))
            return result.scalars().first()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred while fetching the schedule block"
            )
        
    #Update an existing schedule block
    async def update_schedule(self, schedule_id: int, schedule_data) -> Optional[Schedule]:
        try:
            result = await self.db.execute(select(Schedule).filter(Schedule.schedule_id == schedule_id))
            schedule = result.scalars().first()
            if not schedule:
                return None
            
            for key, value in schedule_data.dict(exclude_unset=True).items():
                setattr(schedule, key, value)

            await self.db.commit()
            await self.db.refresh(schedule)
            return schedule
        except SQLAlchemyError:
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred while updating the desired schedule block"
            )
        
    #Delete a schedule block by id
    async def delete_schedule(self, schedule_id: int) -> bool:
        try:
            result = await self.db.execute(select(Schedule).filter(Schedule.schedule_id == schedule_id))
            schedule = result.scalars().first()
            if not schedule:
                return False
            await self.db.delete(schedule)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred while deleting the desired schedule block"
            )