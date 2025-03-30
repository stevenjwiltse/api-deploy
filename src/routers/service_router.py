from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query

from core.dependencies import DBSessionDep
from modules.user.service_schema import ServiceBase, ServiceResponse, ServiceUpdate
from operations.service_operations import ServiceOperations
from modules.user.error_response_schema import ErrorResponse
from auth.controller import AuthController
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

service_router = APIRouter(
    prefix="/api/v1/services",
    tags=["services"],
)
# Initialize the HTTPBearer scheme for authentication
bearer_scheme = HTTPBearer()

# POST endpoint to create a service
@service_router.post("", response_model=ServiceResponse, responses = {
    500: {"model": ErrorResponse}
})
async def create_service(service: ServiceBase, db_session: DBSessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Checks for barber role
    AuthController.protected_endpoint(credentials, required_role="barber")
    
    service_ops = ServiceOperations(db_session)
    response = await service_ops.create_service(service)

    return response


# GET endpoint to get all available services
@service_router.get("", response_model=List[ServiceResponse], responses = {
    500: {"model": ErrorResponse}
})
async def get_all_services(
    db_session: DBSessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100)
):
    service_ops = ServiceOperations(db_session)
    response = await service_ops.get_all_services(page, limit)
    
    return response

# PUT endpoint to update a service
@service_router.put("/{service_id}", response_model=ServiceResponse, responses = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_service(db_session: DBSessionDep, service_id: int, service_details: ServiceUpdate, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Checks for barber role
    AuthController.protected_endpoint(credentials, required_role="barber")
    
    service_ops = ServiceOperations(db_session)
    response = await service_ops.update_service(service_id, service_details)

    return response

# DELETE endpoint to delete a service
@service_router.delete("/{service_id}", response_model=dict, responses = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_service(db_session: DBSessionDep, service_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Checks for barber role
    AuthController.protected_endpoint(credentials, required_role="barber")
    
    
    service_ops = ServiceOperations(db_session)
    response = await service_ops.delete_service(service_id)

    if not response:
        raise HTTPException(
            status_code=400,
            detail="Service not found with provided ID"
        )
    
    return {"message": "Service deleted successfully"}
