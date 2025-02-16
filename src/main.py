from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.user_router import user_router
from auth.auth import auth_router

app = FastAPI()

# Middleware configuration for Frontend-Backend communication
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Only localhost for now
        "http://localhost:8000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect user_router
app.include_router(user_router)
# Connect auth_router
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"root": "test"}

