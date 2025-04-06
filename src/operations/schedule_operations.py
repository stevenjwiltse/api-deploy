from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Schedule, TimeSlot
from modules.schedule_schema import ScheduleCreate, ScheduleUpdate
from modules.time_slot_schema import TimeSlotUpdate
from typing import List, Optional
from fastapi import HTTPException
from datetime import time

"""
CRUD operations for interacting with the schedule database table
"""


class ScheduleOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Create a new schedule block
    async def create_schedule(self, schedule_data: ScheduleCreate) -> Schedule:
        # try:
        new_schedule = Schedule(**schedule_data.model_dump(exclude={"time_slots"}))
        self.db.add(new_schedule)
        await self.db.commit()
        await self.db.refresh(new_schedule)

        # Create time slots for the schedule, each 30 minutes
        # starting from 9:00 AM to 5:00 PM
        for time_slot in schedule_data.time_slots:
            self.db.add(
                TimeSlot(
                    schedule_id=new_schedule.schedule_id,
                    start_time=time_slot.start_time,
                    end_time=time_slot.end_time,
                    is_available=time_slot.is_available,
                )
            )
        await self.db.commit()
        await self.db.refresh(new_schedule)

        return new_schedule
        # except SQLAlchemyError:
        #     raise HTTPException(
        #         status_code=500,
        #         detail="An unexpected error occurred during schedule block creation",
        #     )

    # Get all schedule blocks
    async def get_all_schedules(self, page: int, limit: int) -> List[Schedule]:
        try:
            # Calculate offset for SQL query
            offset = (page - 1) * limit

            result = await self.db.execute(select(Schedule).limit(limit).offset(offset))
            return result.scalars().all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching schedule blocks",
            )

    # Get a specific schedule block by its id
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        try:
            result = await self.db.execute(
                select(Schedule)
                .join(TimeSlot)
                .filter(Schedule.schedule_id == schedule_id)
            )
            return result.scalars().first()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching the schedule block",
            )

    # Update an existing schedule block
    async def update_schedule(
        self, schedule_id: int, schedule_data: ScheduleUpdate
    ) -> Optional[Schedule]:
        try:
            result = await self.db.execute(
                select(Schedule).filter(Schedule.schedule_id == schedule_id)
            )
            schedule = result.scalars().first()
            if not schedule:
                return None

            for key, value in schedule_data.model_dump(exclude_unset=True).items():
                if key == "time_slots":
                    # Update time slots if provided
                    for time_slot in value:
                        time_slot = TimeSlotUpdate(**time_slot)
                        existing_time_slot = (
                            await self.db.execute(
                                select(TimeSlot)
                                .filter(
                                    TimeSlot.slot_id == time_slot.slot_id,
                                    TimeSlot.schedule_id == schedule_id,
                                )
                            )
                        ).scalars().first()
                        if existing_time_slot:
                            existing_time_slot.start_time = time_slot.start_time
                            existing_time_slot.end_time = time_slot.end_time
                            existing_time_slot.is_available = time_slot.is_available
                        else:
                            new_time_slot = TimeSlot(
                                schedule_id=schedule.schedule_id,
                                start_time=time_slot.start_time,
                                end_time=time_slot.end_time,
                                is_available=time_slot.is_available,
                            )
                            self.db.add(new_time_slot)
                else:
                    setattr(schedule, key, value)

            await self.db.commit()
            await self.db.refresh(schedule)
            return schedule
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while updating the desired schedule block",
            )

    # Delete a schedule block by id
    async def delete_schedule(self, schedule_id: int) -> bool:
        try:
            result = await self.db.execute(
                select(Schedule).filter(Schedule.schedule_id == schedule_id)
            )
            schedule = result.scalars().first()
            if not schedule:
                return False
            await self.db.delete(schedule)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while deleting the desired schedule block",
            )
