from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "customer"

class UserOut(UserBase):
    id: int
    role: str
    loyalty_points: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    category_id: int

class ProductCreate(ProductBase):
    vendor_id: int

class ProductResponse(ProductBase):
    id: int
    vendor_id: int
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: str
    math_breakdown: Optional[dict] = None
    class Config:
        from_attributes = True
