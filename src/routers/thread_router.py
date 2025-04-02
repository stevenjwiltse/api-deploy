from fastapi import APIRouter, HTTPException, Query
from modules.thread_schema import ThreadCreate, ThreadResponse
from modules.user.error_response_schema import ErrorResponse
from core.dependencies import DBSessionDep
from operations.thread_operations import ThreadOperations
from typing import List

thread_router = APIRouter(
    prefix="/api/v1/threads",
    tags=["threads"]
)

# POST endpoint to create a new thread
@thread_router.post("", response_model=ThreadResponse, responses = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_thread(thread: ThreadCreate, db_session: DBSessionDep) -> ThreadResponse:
    thread_ops = ThreadOperations(db_session)
    return await thread_ops.create_thread(thread)

# GET endpoint to retrieve threads for a particular logged in user and the user they are conversing with
# This will return threads were the user is both 'sendingUser' and 'recievingUser'
# in order to properly display both sides of the conversation 
@thread_router.get("/{logged_user_id}/and/{other_user_id}", response_model=List[ThreadResponse], responses = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_threads_by_user_id(
    logged_user_id: int, 
    other_user_id: int, 
    db_session: DBSessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100)
) -> List[ThreadResponse]:
    thread_ops = ThreadOperations(db_session)
    response = await thread_ops.get_threads_by_user_id(logged_user_id, other_user_id, page, limit)
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"No threads found between users with IDs: {logged_user_id} and {other_user_id}"
        )
    return response

# GET endpoint to retrieve ALL threads for a particular user, where the user is both 'sendingUser'
# and 'receivingUser' (for displaying all of a user's conversations)
@thread_router.get("/{user_id}", response_model=List[ThreadResponse], responses = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_all_threads_by_user_id(
    user_id: int,
    db_session: DBSessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100)
) -> List[ThreadResponse]:
    
    thread_ops = ThreadOperations(db_session)
    response = await thread_ops.get_all_threads_by_user_id(user_id, page, limit)
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"No threads found for user with ID: {user_id}"
        )
    return response