from typing import Optional
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
    item_data = payload.model_dump()  # pydantic v2 dictionary extraction
    item_data["id"] = new_id
    db[new_id] = item_data
    return item_data


# --- 2. READ ALL / LIST (GET with Query Params) ---
@app.get(
    "/api/v1/media/",
    response_model=list[MediaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listmedia with optional filtering",
)
def list_media(
    media_type: Optional[MediaType] = Query(None, description="Filter by anime or manga"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum rating cutoff"),
    db: dict = Depends(get_db)
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
    summary="Get single media entry by ID"
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
    return db[media_id]


# --- 4. UPDATE (PATCH)) ---
@app.patch(
    "/api/v1/media/{media_id}/",
    response_model=MediaResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a media entry",
)
def update_media(
    media_id: int,
    payload: MediaUpdate,
    db: dict = Depends(get_db)
):
    if media_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media entry with ID {media_id} not found"
        )

    # Exclude unset fields so we only update provided values
    update_data = payload.model_dump(exclude_unset=True)
    db[media_id].update(update_data)
    return db[media_id]


# --- 5. DELETE (DELETE) ---
@app.delete(
    "/api/v1/media/{media_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a media entry"
)
def delete_media(media_id: int, db:dict = Depends(get_db)):
    if media_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media entry with ID {media_id} not found",
        )
    del db[media_id]
    return None  # 204 No content expects empty response

