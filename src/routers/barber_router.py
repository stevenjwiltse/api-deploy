from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from operations.barber_operations import BarberOperations
from core.dependencies import DBSessionDep
from modules.user.barber_schema import BarberResponse, BarberBase
from typing import List
from auth.controller import AuthController
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules.user.error_response_schema import ErrorResponse

barber_router = APIRouter(
    prefix="/api/v1/barbers",
    tags=["barbers"],
)
# Initialize the HTTPBearer scheme for authentication
bearer_scheme = HTTPBearer()

# POST endpoint to create a barber for an existing user by user_id
@barber_router.post("", response_model=BarberResponse, responses = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_barber(user: BarberBase, db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Checks for barber role
    AuthController.protected_endpoint(credentials, required_role="barber")
    
    barber_ops = BarberOperations(db_session)
    response = await barber_ops.create_barber(user)

    return response

# GET endpoint to retrieve all barbers
@barber_router.get("", response_model=List[BarberResponse], responses = {
    500: {"model": ErrorResponse}
})
async def get_all_barbers(db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):

    barber_ops = BarberOperations(db_session)
    response = await barber_ops.get_all_barbers()

    return response

# GET endpoint to retrieve a specific barber by their ID number
@barber_router.get("/{barber_id}", response_model=BarberResponse, responses = {
    500: {"model": ErrorResponse}
})
async def get_barber_by_id(barber_id: int, db_session: DBSessionDep):
    barber_ops = BarberOperations(db_session)
    response = await barber_ops.get_barber_by_id(barber_id)

    return response



