from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from modules.user.models import Appointment, User, Barber, TimeSlot, Appointment_TimeSlot, AppointmentService, Service
from typing import List, Optional
from fastapi import HTTPException
from modules.appointment_schema import AppointmentCreate, AppointmentResponse
import logging
from operations.email_operations import email_operations

logger = logging.getLogger("appointment_operations")
logger.setLevel(logging.ERROR)

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
            
            #check if slot_id(s) exists in the time_slot table
            for slot_id in appointment_data.time_slot:
                time_slot_result = await self.db.execute(select(TimeSlot).filter(TimeSlot.slot_id == slot_id))
                time_slot = time_slot_result.scalars().first()

                if not time_slot:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid slot_id: Time slot does not exist"
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

            #Update the appointment_time_slot table with the newly associated appointment_id and slot_id(s)
            for slot_id in appointment_data.time_slot:
                new_appointment_time_slot = Appointment_TimeSlot(
                    appointment_id = new_appointment.appointment_id,
                    slot_id = slot_id
                )
                self.db.add(new_appointment_time_slot)
            

            
            # Update the is_available field in TimeSlot table for the selected slot_id(s)
            await self.db.execute(
                TimeSlot.__table__.update()
                .where(TimeSlot.slot_id.in_(appointment_data.time_slot))
                .values(is_available=False)
            )

            #Update the service table with the newly associated appointment_id and service_id(s)
            for service_id in appointment_data.service_id:
                new_appointment_service = AppointmentService(
                    service_id = service_id,
                    appointment_id = new_appointment.appointment_id
                )
                self.db.add(new_appointment_service)
            await self.db.commit()

            # Refresh appointment again to ensure the session is aware of its latest state
            await self.db.refresh(new_appointment)

            # Return the appointment response
            return AppointmentResponse(
                appointment_id=new_appointment.appointment_id,
                user_id=new_appointment.user_id,
                barber_id=new_appointment.barber_id,
                status=new_appointment.status,
                time_slot=appointment_data.time_slot,
                service_id=appointment_data.service_id
            )
        
        except SQLAlchemyError as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during appointment creation",
            )
        
    #Get all appointments
    async def get_all_appointments(self, page: int, limit: int) -> List[AppointmentResponse]:
        try:
            # Calculate offset for SQL query
            offset = (page - 1) * limit

            result = await self.db.execute(select(Appointment).limit(limit).offset(offset))
            appointments = result.scalars().all()

            if not appointments:
                return None

            #Extract appointment_ids
            appointment_ids = [appt.appointment_id for appt in appointments]

            #Get slot_ids and link to appointment_ids
            time_slot_result = await self.db.execute(
                select(Appointment_TimeSlot).where(Appointment_TimeSlot.appointment_id.in_(appointment_ids))
            )

            time_slot_links = time_slot_result.scalars().all()

            #Group slot_ids by appointment_id
            time_slot_dict = {}
            for link in time_slot_links:
                time_slot_dict.setdefault(link.appointment_id, []).append(link.slot_id)

            #Get service_ids and link to appointment_ids
            service_result = await self.db.execute(
                select(AppointmentService).where(AppointmentService.appointment_id.in_(appointment_ids))
            )

            service_links = service_result.scalars().all()

            #Group service_ids by appointment_id
            service_dict = {}
            for link in service_links:
                service_dict.setdefault(link.appointment_id, []).append(link.service_id)

            #combine into response list
            responses = []
            for appt in appointments:
                responses.append(
                    AppointmentResponse(
                        appointment_id=appt.appointment_id,
                        user_id=appt.user_id,
                        barber_id=appt.barber_id,
                        status=appt.status,
                        time_slot=time_slot_dict.get(appt.appointment_id, []),
                        service_id=service_dict.get(appt.appointment_id, [])
                    )
                )
            return responses

        except SQLAlchemyError as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching appointments"
            )
        
    #Get a specific appointment by its id
    async def get_appointment_by_id(self, appointment_id: int) -> Optional[AppointmentResponse]:
        try:
            result = await self.db.execute(select(Appointment).filter(Appointment.appointment_id == appointment_id))
            appt = result.scalars().first()

            if not appt:
                return None

            #Get slot_ids linked to appointment_id
            time_slot_result = await self.db.execute(
                select(Appointment_TimeSlot).where(Appointment_TimeSlot.appointment_id == appointment_id)
            )
            time_slot_links = time_slot_result.scalars().all()
            time_slot_ids = [link.slot_id for link in time_slot_links]

            #Get service_ids linked to appointment_id
            service_result = await self.db.execute(
                select(AppointmentService).where(AppointmentService.appointment_id == appointment_id)
            )
            service_links = service_result.scalars().all()
            service_ids = [link.service_id for link in service_links]

            return AppointmentResponse(
                appointment_id=appt.appointment_id,
                user_id=appt.user_id,
                barber_id=appt.barber_id,
                status=appt.status,
                time_slot=time_slot_ids,
                service_id=service_ids
            )

        except SQLAlchemyError as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching the appointment"
            )
        
    #Update an existing appointment
    async def update_appointment(self, appointment_id: int, appointment_data) -> Optional[AppointmentResponse]:
        try:
            result = await self.db.execute(select(Appointment).filter(Appointment.appointment_id == appointment_id))
            appointment = result.scalars().first()


            if not appointment:
                return None
            
             # Update the appointment's info
            update_data = appointment_data.dict(exclude_unset=True, exclude={"time_slot", "service_id"})
            for key, value in update_data.items():
                setattr(appointment, key, value)

            # update Appointment_TimeSlot table if it has new tim_slot info
            if "time_slot" in appointment_data.dict(exclude_unset=True):
                # Delete current associations for this appointment
                await self.db.execute(
                    delete(Appointment_TimeSlot).where(Appointment_TimeSlot.appointment_id == appointment_id)
                )
                # Add new associations
                for slot_id in appointment_data.time_slot:
                    new_link = Appointment_TimeSlot(
                        appointment_id=appointment_id,
                        slot_id=slot_id
                    )
                    self.db.add(new_link)
            
            # update AppointmentService table if it has new service_id information
            if "service_id" in appointment_data.dict(exclude_unset=True):
                await self.db.execute(
                    delete(AppointmentService).where(AppointmentService.appointment_id == appointment_id)
                )
                for svc_id in appointment_data.service_id:
                    new_service_link = AppointmentService(
                        appointment_id=appointment_id,
                        service_id=svc_id
                    )
                    self.db.add(new_service_link)

            # Commit all changes
            await self.db.commit()
            await self.db.refresh(appointment)

            # Retrieve the updated data for the response
            time_slot_result = await self.db.execute(
                select(Appointment_TimeSlot).where(Appointment_TimeSlot.appointment_id == appointment_id)
            )
            time_slot_links = time_slot_result.scalars().all()
            time_slot_ids = [link.slot_id for link in time_slot_links]

            service_result = await self.db.execute(
                select(AppointmentService).where(AppointmentService.appointment_id == appointment_id)
            )
            service_links = service_result.scalars().all()
            service_ids = [link.service_id for link in service_links]

            # Return with updated data
            return AppointmentResponse(
                appointment_id=appointment.appointment_id,
                user_id=appointment.user_id,
                barber_id=appointment.barber_id,
                status=appointment.status,
                time_slot=time_slot_ids,
                service_id=service_ids
            )

        except SQLAlchemyError as e:
            logger.error(e)
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
            
            # Delete associated appointment_time_slot records
            await self.db.execute(
                delete(Appointment_TimeSlot).where(Appointment_TimeSlot.appointment_id == appointment_id)
            )
            # Delete associated appointment_service records
            await self.db.execute(
                delete(AppointmentService).where(AppointmentService.appointment_id == appointment_id)
            )
            
            await self.db.delete(appointment)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while deleting the desired appointment"
            )