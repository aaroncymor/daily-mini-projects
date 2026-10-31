import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Optional
import jwt
from fastapi import FastAPI, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel, Field

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"


# Simulated Global Database Pool Connection
class DatabasePool:
    def __init__(self):
        self.is_connected = False

    async def connect(self):
        await asyncio.sleep(0.1)
        self.is_connected = True
        print("[DB] Connected to database pool.")

    async def disconnect(self):
        self.is_connected = False
        print("[DB] Disconnected from database pool.")


db_pool = DatabasePool()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_pool.connect()
    yield
    await db_pool.disconnect()


# --- Models ---
class UserProfile(BaseModel):
    user_id: int
    role: str


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


# --- Dependencies ---
async def get_current_user(authorization: str = Header(...)) -> UserProfile:
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return UserProfile(user_id=payload["sub"], role=payload["role"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token"
        )


# --- ASGI Middleware ---
class CustomHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Correct ASGI specification: tuple of bytes
            scope["headers"].append((b"x-gateway-processed", b"true"))
        await self.app(scope, receive, send)


app = FastAPI(title="Gateway Service", lifespan=lifespan)
app.add_middleware(CustomHeaderMiddleware)


# --- Endpoints ---
@app.get("/v1/items")
async def list_items(
    pagination: Annotated[PaginationParams, Depends()],
    user: Annotated[UserProfile, Depends(get_current_user)]
):
    if not db_pool.is_connected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection offline"
        )

    return {
        "user_id": user.user_id,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "items": [f"Item_{i}" for i in range(pagination.page_size)]
    }
