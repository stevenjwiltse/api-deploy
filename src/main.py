from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import user_router

app = FastAPI()

# Middleware configuration for Frontend-Backend communication
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Only localhost for now
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect user_router
app.include_route(user_router)


@app.get("/")
async def root():
    return {"root": "test"}


