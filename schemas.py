"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    image: Optional[str] = Field(None, description="Image URL")
    featured: bool = Field(False, description="Whether featured on homepage")
    in_stock: bool = Field(True, description="Whether product is in stock")

# CustomPrint Studio specific schema
class Enquiry(BaseModel):
    """
    Enquiries collection schema
    Collection name: "enquiry"
    """
    name: str = Field(..., description="Full name of the requester")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    company: Optional[str] = Field(None, description="Company or organisation")
    product_type: Literal['2D Laser-cut','3D Trophy','3D Mockup','Other'] = Field(..., description="Requested product type")
    quantity: Optional[int] = Field(None, ge=1, description="Estimated quantity")
    budget_range: Optional[str] = Field(None, description="Approximate budget range")
    message: str = Field(..., description="Project details / brief")
    reference_url: Optional[str] = Field(None, description="Link to reference/inspiration")
