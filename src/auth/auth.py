from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from keycloak import KeycloakAdmin, KeycloakOpenID, KeycloakOpenIDConnection
from pydantic import BaseModel

import os
from dotenv import load_dotenv
load_dotenv()
# Create a FastAPI router for authentication
auth_router = APIRouter()


# Keycloak Credentials
KEYCLOAK_SERVER_URL=os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM=os.getenv("KEYCLOAK_REALM")
KEYCLOAK_API_CLIENT_ID =os.getenv("KEYCLOAK_API_CLIENT_ID")
KEYCLOAK_ADMIN_USERNAME=os.getenv("KEYCLOAK_ADMIN_USERNAME")
KEYCLOAK_ADMIN_PASSWORD=os.getenv("KEYCLOAK_ADMIN_PASSWORD")
KEYCLOAK_API_SECRET=os.getenv("KEYCLOAK_API_SECRET")

# Keycloak OpenID Config
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_API_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_API_SECRET
)

# Credentials Admin Config
keycloak_connection = KeycloakOpenIDConnection(
    server_url=KEYCLOAK_SERVER_URL,
    username=KEYCLOAK_ADMIN_USERNAME,
    password=KEYCLOAK_ADMIN_PASSWORD,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_API_CLIENT_ID,
    client_secret_key=KEYCLOAK_API_SECRET,
    verify=True
)
print("URL",KEYCLOAK_SERVER_URL)
print("REALM",KEYCLOAK_REALM)
print("CLIENT",KEYCLOAK_API_CLIENT_ID)
print("USERNAME",KEYCLOAK_ADMIN_USERNAME)
print("PW",KEYCLOAK_ADMIN_PASSWORD)
print("SECRET",KEYCLOAK_API_SECRET)
keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

# User Model
class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

# Create User Function
def create_kc_user(user: UserCreate):
    user_representation = {
        "username": user.username,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "enabled": True,
        "credentials": [{"type": "password", "value": user.password, "temporary": False}]
    }
    try:
        keycloak_admin.create_user(user_representation)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

# User Registration Route
@auth_router.post("/auth/users/")
def register_user(user: UserCreate):
    return create_kc_user(user)

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Token Endpoint (Login)
@auth_router.post("/auth/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = keycloak_openid.token(form_data.username, form_data.password)
        return {"access_token": token["access_token"], "token_type": "bearer"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Get User Info
@auth_router.get("/auth/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        userinfo = keycloak_openid.userinfo(token)
        return userinfo
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

