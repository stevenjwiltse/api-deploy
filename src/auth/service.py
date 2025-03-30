import json

from fastapi import HTTPException, status, Security, Depends
from keycloak.exceptions import KeycloakAuthenticationError
from core.config import settings
from auth.models import UserInfo
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from modules.user.user_schema import UserCreate, UserUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from urllib.request import urlopen
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator

bearer_scheme = HTTPBearer()

class ClientCredsTokenValidator(JWTBearerTokenValidator):
    def __init__(self, issuer):
        jsonurl = urlopen(f"{issuer}/protocol/openid-connect/certs")
        public_key = JsonWebKey.import_key_set(json.loads(jsonurl.read()))
        super(ClientCredsTokenValidator, self).__init__(public_key)
        self.claims_options = {
            "exp": {"essential": True},
            "iss": {"essential": True, "value": issuer},
        }

    def validate_token(self, token, scopes, request):
        super(ClientCredsTokenValidator, self).validate_token(token, scopes, request)


class AuthService():

    # Keycloak connection using credentials from core/config/settings
    keycloak_openid = KeycloakOpenID(
        server_url=settings.get_config()["keycloak_server_url"],
        realm_name=settings.get_config()["keycloak_realm"],
        client_id=settings.get_config()["keycloak_api_client_id"],
        client_secret_key=settings.get_config()["keycloak_api_secret"],
        )
    
    # Keycloak Admin (For User Management)
    keycloak_admin_connection = KeycloakOpenIDConnection(
        server_url=settings.get_config()["keycloak_server_url"],
        username=settings.get_config()["keycloak_admin_username"],
        password=settings.get_config()["keycloak_admin_password"],
        realm_name=settings.get_config()["keycloak_realm"],
        client_id=settings.get_config()["keycloak_api_client_id"],
        client_secret_key=settings.get_config()["keycloak_api_secret"],
        verify=True,
    )
    keycloak_admin = KeycloakAdmin(connection=keycloak_admin_connection)
    KEYCLOAK_ISSUER = settings.get_config()["keycloak_server_url"] + "/realms/" + settings.get_config()["keycloak_realm"]
    validator = ClientCredsTokenValidator(KEYCLOAK_ISSUER)


    # Checks username and password against Keycloak DB and return JWT
    def authenticate_user(username: str, password: str) -> str:
        """
        Authenticate the user using Keycloak and return an access token.
        """
        try:
            token = AuthService.keycloak_openid.token(username, password)
            return token["access_token"]
        except KeycloakAuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

    # Verifies token against Keycloak and UserInfo model and returns user info
    def verify_token(token: str) -> UserInfo:
        """
        Verify the given token and return user information.
        """
        try:
            # Introspects the token to check its validity
            token_info = AuthService.keycloak_openid.introspect(token)
            print(f"Token info: {token_info}")
            return

            is_valid = AuthService.validator.validate_token(token_info, scopes=None, request=None)
            print(f"Token is valid: {is_valid}")
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            

            # Retrives user data from the Keycloak server
            user_info = AuthService.keycloak_openid.userinfo(token)
            user_roles = AuthService.keycloak_admin.get_realm_roles_of_user(user_info["sub"])

            # Parses user roles into list 
            roles = [role['name'] for role in user_roles]

            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            
            this_user = UserInfo(
                username=user_info["preferred_username"],
                email=user_info.get("email"),
                full_name=user_info.get("name"),
                first_name=user_info.get("given_name"),
                last_name=user_info.get("family_name"),
                roles=roles
            )           

            return this_user
        except KeycloakAuthenticationError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
    # Register a new user in Keycloak
    def register_kc_user(user: UserCreate):
        """
        Register a new user in Keycloak.
        """
        
        user_representation = {
            "username": user.email,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "enabled": True,
            "credentials": [{"type": "password", "value": user.password, "temporary": False}],
            "requiredActions": ["VERIFY_EMAIL"]
        }


        try:
            AuthService.keycloak_admin.create_user(user_representation)
            return {"message": "User created successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error creating user: {str(e)}"
            )
        


    def update_kc_user(user: UserUpdate):
        
        user_representation = {
            "username": user.email,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            }
        
        try:
            user_id = AuthService.keycloak_admin.get_user_id(username=user.email)
            AuthService.keycloak_admin.update_user(user_id=user_id,payload=user_representation)
            return {"message": "User updated successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error updating user: {str(e)}"
            )
        


    def delete_kc_user(user_email):
        try:
            user_id = AuthService.keycloak_admin.get_user_id(username=user_email)
            AuthService.keycloak_admin.delete_user(user_id=user_id)
            return {"message": "User deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error deleting user: {str(e)}"
            )
        


    def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> UserInfo:
        """Extract and verify the token to retrieve user info."""
        token = credentials.credentials
        user_info = AuthService.verify_token(token)

        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return user_info


