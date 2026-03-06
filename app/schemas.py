from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    low_stock_warning: bool = False

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: str
    created_at: datetime

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
    created_at: datetime

    class Config:
        from_attributes = True
