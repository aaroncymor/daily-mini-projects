from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MediaType(str, Enum):
    ANIME = "anime"
    MANGA = "manga"


# Base properties shared accross schemas
class MediaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="Frieren")
    media_type: MediaType = Field(..., example=MediaType.ANIME)
    rating: float = Field(..., ge=0.0, le=10.0, example=9.2)


class MediaCreate(MediaBase):
    pass


class MediaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    media_type: Optional[MediaType] = None
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)


class MediaResponse(MediaBase):
    id: int

    class Config:
        from_attributes = True  # Allows ORM model conversion (Pydantic v2 replacement form orm_mode)
