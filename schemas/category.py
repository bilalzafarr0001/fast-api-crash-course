from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Data the client sends to create a category
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


# Data the client sends to update a category (all optional)
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


# Data the server RETURNS
class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
