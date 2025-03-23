import os

from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

required_environment_variables = [
    "SECRET_KEY",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DB",
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_ECHO",
    "DEBUG",
    "BACKEND_CORS_ORIGINS",
    "FRONTEND_HOST",
    "KEYCLOAK_SERVER_URL",
    "KEYCLOAK_REALM",
    "KEYCLOAK_API_CLIENT_ID",
    "KEYCLOAK_FRONT_END_CLIENT_ID",
    "KEYCLOAK_API_SECRET",
    "KEYCLOAK_FRONT_END_SECRET",
    "KEYCLOAK_ADMIN_USERNAME",
    "KEYCLOAK_ADMIN_PASSWORD",
]

class BaseSettings(TypedDict):
    secret_key: str
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_host: str
    mysql_port: str
    mysql_echo: bool
    debug: bool
    backend_cors_origins: list[str]
    frontend_host: str
    keycloak_server_url: str
    keycloak_realm: str
    keycloak_api_client_id: str
    keycloak_frontend_client_id: str
    keycloak_api_secret: str
    keycloak_front_end_secret: str
    keycloak_admin_username: str
    keycloak_admin_password: str

class Settings:
    def __init__(self):
        self.check_environment_variables()

    def check_environment_variables(self):
        for env_var in required_environment_variables:
            if env_var not in os.environ:
                raise EnvironmentError(f"Missing environment variable: {env_var}")
            
    def get_config(self) -> BaseSettings:
        return {
            "secret_key": os.getenv("SECRET_KEY"),
            "mysql_user": os.getenv("MYSQL_USER"),
            "mysql_password": os.getenv("MYSQL_PASSWORD"),
            "mysql_db": os.getenv("MYSQL_DB"),
            "mysql_host": os.getenv("MYSQL_HOST"),
            "mysql_port": os.getenv("MYSQL_PORT"),
            "mysql_echo": self.check_boolean(os.getenv("MYSQL_ECHO")),
            "debug": self.check_boolean(os.getenv("DEBUG")),
            "backend_cors_origins": os.getenv("BACKEND_CORS_ORIGINS").split(","),
            "frontend_host": os.getenv("FRONTEND_HOST"),
            "keycloak_server_url": os.getenv("KEYCLOAK_SERVER_URL"),
            "keycloak_realm": os.getenv("KEYCLOAK_REALM"),
            "keycloak_api_client_id": os.getenv("KEYCLOAK_API_CLIENT_ID"),
            "keycloak_front_end_client_id": os.getenv("KEYCLOAK_FRONT_END_CLIENT_ID"),
            "keycloak_api_secret": os.getenv("KEYCLOAK_API_SECRET"),
            "keycloak_front_end_secret": os.getenv("KEYCLOAK_FRONT_END_SECRET"),
            "keycloak_admin_username": os.getenv("KEYCLOAK_ADMIN_USERNAME"),
            "keycloak_admin_password": os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
        }
    
    def check_boolean(self, value: str) -> bool:
        return value.lower() == "true"
    
    def get_database_url(self) -> str:
        return f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    

settings = Settings()

