from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Appointment, User, Barber, Schedule
from typing import List, Optional
from fastapi import HTTPException
from modules.appointment_schema import AppointmentCreate, AppointmentResponse


'''
CRUD operations for interacting with the appointment database table
'''

class AppointmentOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    #create a new appointment
    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentResponse:
        try:

            #check if user_id exists in user table
            user_result = await self.db.execute(select(User).filter(User.user_id == appointment_data.user_id))
            user = user_result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid user_id: User does not exist"
                )
            
            #check if barber_id exists in the Barber table
            barber_result = await self.db.execute(select(Barber).filter(Barber.barber_id == appointment_data.barber_id))
            barber = barber_result.scalars().first()

            if not barber:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid barber_id: Barber does not exist"
                )
            
            #check if schedule_id exists in the Schedule table
            schedule_result = await self.db.execute(select(Schedule).filter(Schedule.schedule_id == appointment_data.schedule_id))
            schedule = schedule_result.scalars().first()

            if not schedule:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid schedule_id: Schedule block does not exist"
                )

            #create new appointment if both exist
            new_appointment = Appointment(
                user_id=appointment_data.user_id,
                barber_id=appointment_data.barber_id,
                status=appointment_data.status
            )
            self.db.add(new_appointment)
            await self.db.commit()
            await self.db.refresh(new_appointment)

            #Update the schedule block with the newly created appointment_id
            schedule.appointment_id = new_appointment.appointment_id
            await self.db.commit()

            # Refresh appointment again to ensure the session is aware of its latest state
            await self.db.refresh(new_appointment)

            # Return the appointment response
            return AppointmentResponse(
                appointment_id=new_appointment.appointment_id,
                user_id=new_appointment.user_id,
                barber_id=new_appointment.barber_id,
                status=new_appointment.status
            )
        
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during appointment creation"
            )
        
    #Get all appointments
    async def get_all_appointments(self, page: int, limit: int) -> List[Appointment]:
        try:
            # Calculate offset for SQL query
            offset = (page - 1) * limit

            result = await self.db.execute(select(Appointment).limit(limit).offset(offset))
            return result.scalars().all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching appointments"
            )
        
    #Get a specific appointment by its id
    async def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        try:
            result = await self.db.execute(select(Appointment).filter(Appointment.appointment_id == appointment_id))
            return result.scalars().first()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching the appointment"
            )
        
    #Update an existing appointment
    async def update_appointment(self, appointment_id: int, appointment_data) -> Optional[Appointment]:
        try:
            result = await self.db.execute(select(Appointment).filter(Appointment.appointment_id == appointment_id))
            appointment = result.scalars().first()
            if not appointment:
                return None
            
            for key, value in appointment_data.dict(exclude_unset=True).items():
                setattr(appointment, key, value)

            await self.db.commit()
            await self.db.refresh(appointment)
            return appointment
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while updating the desired appointment"
            )
        
    #Delete an appointment
    async def delete_appointment(self, appointment_id: int) -> bool:
        try:
            result = await self.db.execute(select(Appointment).filter(Appointment.appointment_id == appointment_id))
            appointment = result.scalars().first()
            if not appointment:
                return False
            await self.db.delete(appointment)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while deleting the desired appointment"
            )