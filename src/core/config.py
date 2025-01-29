import os

from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

required_environment_variables = [
    "SECRET_KEY",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "DEBUG",
    "BACKEND_CORS_ORIGINS",
    "FRONTEND_HOST",
]

class BaseSettings(TypedDict):
    secret_key: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    debug: bool
    backend_cors_origins: list[str]
    frontend_host: str


class Settings:
    def __init__(self):
        self.check_environment_variables()

    def check_environment_variables(self):
        for env_var in required_environment_variables:
            if env_var not in os.environ:
                raise EnvironmentError(f"Missing environment variable: {env_var}")
            
    def get_config() -> BaseSettings:
        return {
            "secret_key": os.getenv("SECRET_KEY"),
            "postgres_user": os.getenv("POSTGRES_USER"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD"),
            "postgres_db": os.getenv("POSTGRES_DB"),
            "postgres_host": os.getenv("POSTGRES_HOST"),
            "postgres_port": os.getenv("POSTGRES_PORT"),
            "debug": os.getenv("DEBUG"),
            "backend_cors_origins": os.getenv("BACKEND_CORS_ORIGINS").split(","),
            "frontend_host": os.getenv("FRONTEND_HOST"),
        }
    
    def get_database_url() -> str:
        return f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    

settings = Settings()