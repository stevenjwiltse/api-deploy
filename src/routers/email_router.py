from fastapi import FastAPI, APIRouter, Depends, HTTPException
from operations.email_operations import email_operations
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules.user.email_schema import EmailSchema
from modules.user.error_response_schema import ErrorResponse

# Initialize the HTTPBearer scheme for authentication
bearer_scheme = HTTPBearer()

email_router = APIRouter(
    prefix="/api/v1/email",
    tags=["email"],
)


# Endpoint to send emails with error handling
@email_router.post("/send",
    responses={
        200: {"description": "Email has been sent successfully."},
        500: {"model": ErrorResponse, "description": "An error occurred while sending the email."}
    }
)
async def send_email(
    email_data: EmailSchema,  
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    try:
        # Send the email
        await email_operations.send_email(
            email_data.email,
            email_data.subject,
            email_data.body
        )

        # Successful response
        return {"message": "Email has been sent successfully."}

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")