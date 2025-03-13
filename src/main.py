from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from core.db import sessionmanager
from core.config import settings
from routers.user_router import user_router
from auth.controller import AuthController
from routers.barber_router import barber_router
from routers.service_router import service_router
from routers.schedule_router import schedule_router
from routers.auth_router import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)

# Initialize the HTTPBearer scheme for authentication
bearer_scheme = HTTPBearer()

# Middleware configuration for Frontend-Backend communication
app.add_middleware(
    CORSMiddleware,

    allow_origins=[settings.get_config()["backend_cors_origins"]],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect auth_router
app.include_router(auth_router)

# Connect user_router
app.include_router(user_router)

# Connect barber_router
app.include_router(barber_router)

# Connect service_router
app.include_router(service_router)

# Connect schedule_router
app.include_router(schedule_router)

# Define the root endpoint
@app.get("/")
async def root():
    return {"Barbershop App"}

@app.get("/healthz")
async def root():
    return {"healthy": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)