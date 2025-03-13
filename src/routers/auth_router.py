from fastapi import APIRouter, Form
from auth.controller import AuthController
from auth.models import TokenResponse

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

# Define the login endpoint
@auth_router.post("/login", response_model=TokenResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Login endpoint to authenticate the user and return an access token.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The password of the user.

    Returns:
        TokenResponse: Contains the access token upon successful authentication.
    """
    return AuthController.login(username, password)
