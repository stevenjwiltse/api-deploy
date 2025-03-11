from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Appointment, User, Barber
from typing import List, Optional
from fastapi import HTTPException


'''
CRUD operations for interacting with the appointment database table
'''

class AppointmentOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    #create a new appointment
    async def create_appointment(self, appointment_data) -> Appointment:
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

            #create new appointment if both exist
            new_appointment = Appointment(**appointment_data.dict())
            self.db.add(new_appointment)
            await self.db.commit()
            await self.db.refresh(new_appointment)
            return new_appointment
        
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during appointment creation"
            )
        
    #Get all appointments
    async def get_all_appointments(self) -> List[Appointment]:
        try:
            result = await self.db.execute(select(Appointment))
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