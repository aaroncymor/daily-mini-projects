Project Title
FastAPI Crash Course: Production-Grade CRUD & Core Fundamentals

Overview & Objective
Master essential FastAPI concepts in under 2 hours to prep for your interview today. You'll build a clean, production-structured REST API (a lightweight Anime & Manga Collection Manager) focusing on type safety with Pydantic v2, dependency injection, explicit status codes, route grouping, and automatic OpenAPI documentation.

Tech Stack
Framework: FastAPI + Uvicorn

Data Validation / Schemas: Pydantic v2

Language / Typing: Python 3.11+ (Type Hints & Annotations)

Testing / Docs: Swagger UI (/docs) & Redoc (/redoc)

Core Concepts Covered
Pydantic v2 Schemas: Request validation vs. Response serialization (BaseModel, Field, optional types).

Dependency Injection (Depends): Reusable query parameters, mock DB access, and request context.

Path & Query Parameters: Strict typing, default values, and path validation (Path, Query).

HTTP Status Codes & Exceptions: Returning 201 Created, 204 No Content, and throwing HTTPException.

Step-by-Step Crash Course Implementation
Step 1: Environment & Project Structure (10 mins)
Create a clean directory layout mimicking a production FastAPI app:

Plaintext
fastapi-crashcourse/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── models.py
│   └── database.py
└── requirements.txt
Install requirements:

Bash
pip install "fastapi[standard]" pydantic
Step 2: Define Pydantic Schemas (app/schemas.py) (15 mins)
Separate request creation schemas from response payload schemas.

Python
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MediaType(str, Enum):
    ANIME = "anime"
    MANGA = "manga"


# Base properties shared across schemas
class MediaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="Frieren")
    media_type: MediaType = Field(..., example=MediaType.ANIME)
    rating: float = Field(..., ge=0.0, le=10.0, example=9.2)


# Schema for CREATING an item (no ID required from user)
class MediaCreate(MediaBase):
    pass


# Schema for UPDATING an item (all fields optional)
class MediaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    media_type: Optional[MediaType] = None
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)


# Schema for RESPONSES (includes DB-assigned fields)
class MediaResponse(MediaBase):
    id: int

    class Config:
        from_attributes = True  # Allows ORM model conversion (Pydantic v2 replacement for orm_mode)
Step 3: In-Memory Database & Dependency (app/database.py) (15 mins)
Create a simple in-memory repository with a FastAPI dependency for DB access.

Python
from typing import Dict
from app.schemas import MediaCreate, MediaResponse, MediaType

# In-memory database dictionary
fake_db: Dict[int, dict] = {
    1: {"id": 1, "title": "Frieren: Beyond Journey's End", "media_type": MediaType.ANIME, "rating": 9.3},
    2: {"id": 2, "title": "Dungeon Meshi", "media_type": MediaType.MANGA, "rating": 8.8},
}


# Dependency function to get DB context
def get_db():
    return fake_db
Step 4: Complete CRUD Endpoints (app/main.py) (45 mins)
Build the full REST lifecycle with explicit response models, status codes, and HTTP exception handling.

Python
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from app.schemas import MediaCreate, MediaUpdate, MediaResponse, MediaType
from app.database import get_db

app = FastAPI(
    title="FastAPI Interview Crash Course API",
    description="Full CRUD with Pydantic v2, Dependency Injection, and Type Hints",
    version="1.0.0",
)


# --- 1. CREATE (POST) ---
@app.post(
    "/api/v1/media/",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new anime/manga entry",
)
def create_media(payload: MediaCreate, db: dict = Depends(get_db)):
    new_id = max(db.keys(), default=0) + 1
    item_data = payload.model_dump()  # Pydantic v2 dictionary extraction
    item_data["id"] = new_id
    db[new_id] = item_data
    return item_data


# --- 2. READ ALL / LIST (GET with Query Params) ---
@app.get(
    "/api/v1/media/",
    response_model=List[MediaResponse],
    status_code=status.HTTP_200_OK,
    summary="List media with optional filtering",
)
def list_media(
    media_type: Optional[MediaType] = Query(None, description="Filter by anime or manga"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum rating cutoff"),
    db: dict = Depends(get_db),
):
    results = list(db.values())
    if media_type:
        results = [item for item in results if item["media_type"] == media_type]
    if min_rating is not None:
        results = [item for item in results if item["rating"] >= min_rating]
    return results


# --- 3. READ SINGLE (GET by ID) ---
@app.get(
    "/api/v1/media/{media_id}/",
    response_model=MediaResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single media entry by ID",
)
def get_media(
    media_id: int = Path(..., ge=1, description="The ID of the item to retrieve"),
    db: dict = Depends(get_db),
):
    if media_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media entry with ID {media_id} not found",
        )
    return d[118;1:3ub[media_id]


# --- 4. UPDATE (PATCH) ---
@app.patch(
    "/api/v1/media/{media_id}/",
    response_model=MediaResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a media entry",
)
def update_media(
    media_id: int,
    payload: MediaUpdate,
    db: dict = Depends(get_db),
):
    if media_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media entry with ID {media_id} not found",
        )

    # Exclude unset fields so we only update provided values
    update_data = payload.model_dump(exclude_unset=True)
    db[media_id].update(update_data)
    return db[media_id]


# --- 5. DELETE (DELETE) ---
@app.delete(
    "/api/v1/media/{media_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a media entry",
)
def delete_media(media_id: int, db: dict = Depends(get_db)):
    if media_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media entry with ID {media_id} not found",
        )
    del db[media_id]
    return None  # 204 No Content expects empty response
How to Run & Test (Interactive Docs)
Run the server using Uvicorn:

Bash
uvicorn app.main:app --reload
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

Test every CRUD endpoint directly through the auto-generated Swagger UI.

Observe how Pydantic automatically rejects invalid payloads (e.g., passing a rating of 12.0 or invalid media type) with explicit 422 Unprocessable Entity responses.

Top Interview Talking Points to Remember
Pydantic v2 vs v1: Use .model_dump() instead of .dict(), and from_attributes = True instead of orm_mode = True.

Depends(): FastAPI's built-in dependency injection system used for database sessions, auth, and query validation.

response_model: Defines response serialization and automatically filters out unauthorized/unwanted fields before returning JSON to the client.

ASGI Performance: Built on Starlette and Pydantic, running natively on top of uvicorn / gunicorn for asynchronous Python concurrency.
