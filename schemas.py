"""
Database Schemas for Custom Children's Stories

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Tier(BaseModel):
    name: Literal["Spark", "Glow", "Shine", "Supernova"] = Field(..., description="Tier name")
    price: float = Field(..., ge=0, description="Price in USD")
    features: List[str] = Field(default_factory=list, description="Included features")
    delivery_days: int = Field(7, ge=1, description="Estimated delivery time in days")


class Character(BaseModel):
    key: str = Field(..., description="Unique key identifier, kebab-case")
    name: str = Field(..., description="Display name")
    era: Optional[str] = Field(None, description="Folktale/fairytale era or origin")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    thumbnail: Optional[str] = Field(None, description="Optional image url")
    description: Optional[str] = Field(None, description="Short blurb")


class StoryOrder(BaseModel):
    parent_name: str
    parent_email: str
    child_name: str
    child_age: int = Field(..., ge=0, le=14)
    tier: Literal["Spark", "Glow", "Shine", "Supernova"]
    character_key: str
    adventure_theme: str = Field(..., description="Adventure the child will go on")
    lesson_theme: str = Field(..., description="Core lesson to learn")
    word_count: Literal[500, 800, 1200, 2000]
    illustration_style: Literal[
        "storybook-classic",
        "watercolor",
        "comic",
        "paper-cut",
        "digital-paint"
    ] = "storybook-classic"
    color_palette: Literal["pastel", "vibrant", "earthy", "primary"] = "pastel"
    dedication: Optional[str] = None
    languages: List[Literal["en", "es", "fr", "de", "it"]] = ["en"]
    include_child_appearance: bool = True
    child_traits: List[str] = Field(default_factory=list, description="Traits to reflect in the story")
    accessibility: List[Literal["dyslexia-friendly", "high-contrast", "large-text"]] = Field(default_factory=list)
    delivery_format: Literal["pdf", "epub", "web"] = "pdf"
    notes: Optional[str] = None


class OrderStatus(BaseModel):
    order_id: str
    status: Literal["received", "processing", "illustrating", "ready"] = "received"
    download_url: Optional[str] = None
    preview_images: List[str] = Field(default_factory=list)
