# models.py
from pydantic import BaseModel

class Category(BaseModel):
    name: str

class Product(BaseModel):
    name: str
    price: float
    category_id: str
