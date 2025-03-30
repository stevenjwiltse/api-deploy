from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_db_session
from core.dependencies import DBSessionDep
from operations.schedule_operations import ScheduleOperations
from modules.schedule_schema import ScheduleResponse, ScheduleCreate, ScheduleUpdate, TimeSlotChildResponse
from auth.controller import AuthController
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from modules.user.error_response_schema import ErrorResponse

'''
Endpoints for interactions with schedule table
'''

schedule_router = APIRouter(
    prefix="/api/v1/schedules",
    tags=["schedules"],
)
# Initialize the HTTPBearer scheme for authentication
bearer_scheme = HTTPBearer()

# POST endpoint to create a new schedule block in the database
@schedule_router.post("", response_model=ScheduleResponse, responses = {
    500: {"model": ErrorResponse}
})
async def create_schedule(schedule: ScheduleCreate, db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    AuthController.protected_endpoint(credentials, required_role="barber")
    # try:
    schedule_ops = ScheduleOperations(db_session)
    created_schedule = await schedule_ops.create_schedule(schedule)
    if not created_schedule:
        raise HTTPException(status_code=500, detail="Schedule creation failed")
    
    return created_schedule.to_response_schema()
    # except Exception as e:
    #     logging.error(e)
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred during schedule block creation")

# GET endpoint to get all schedule blocks from the database
@schedule_router.get("", response_model=List[ScheduleResponse], responses = {
    500: {"model": ErrorResponse}
})
async def get_schedules(db_session: DBSessionDep):

    schedule_ops = ScheduleOperations(db_session)
    results = await schedule_ops.get_all_schedules()
    return [schedule.to_response_schema() for schedule in results]

# GET endpoint to retrieve a specific schedule block from the database by the schedule_id
@schedule_router.get("/{schedule_id}", response_model=ScheduleResponse, responses = {
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_schedule(schedule_id: int, db_session: DBSessionDep):
    
    schedule_ops = ScheduleOperations(db_session)
    schedule = await schedule_ops.get_schedule_by_id(schedule_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule block with ID provided not found")
    return schedule.to_response_schema()

# PUT endpoint to update a specific schedule block in the database by the schedule_id
@schedule_router.put("/{schedule_id}", response_model=ScheduleResponse, responses = {
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_schedule(schedule_id: int, schedule: ScheduleUpdate, db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    
    schedule_ops = ScheduleOperations(db_session)
    updated_schedule = await schedule_ops.update_schedule(schedule_id, schedule)
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Schedule block with ID provided not found")
    return updated_schedule.to_response_schema()

# DELETE endpoint to delete a schedule block from the database by the schedule_id
@schedule_router.delete("/{schedule_id}", response_model=dict, responses = {
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_schedule(schedule_id: int, db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    
    schedule_ops = ScheduleOperations(db_session)
    success = await schedule_ops.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule with ID provided not found")
    return {"message": "Schedule block deleted successfully"}

