from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import sessionmanager
from auth.auth import auth_router
from routers.user_router import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)

# Middleware configuration for Frontend-Backend communication
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Only localhost for now
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect user_router
app.include_router(user_router)
# Connect auth_router
app.include_router(auth_router)


@app.get("/healthz")
async def root():
    return {"healthy": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)