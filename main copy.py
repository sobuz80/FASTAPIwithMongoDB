from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List
from models import Category, Product

app = FastAPI()

mongo_connection_string = "mongodb+srv://11335220:11335220@cluster0.ojobzbu.mongodb.net/Todo?retryWrites=true&w=majority"
client = MongoClient(mongo_connection_string)

# Specify the default database name here
db = client.get_database("Todo")

categories_collection: Collection = db["categories"]
products_collection: Collection = db["products"]

def find_category_by_name(name: str):
    return categories_collection.find_one({"name": name})


def find_product_by_name(name: str):
    return products_collection.find_one({"name": name})


@app.post("/categories/", response_model=Category)
def create_category(category: Category):
    existing_category = find_category_by_name(category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    category_dict = category.dict()
    inserted_category = categories_collection.insert_one(category_dict)
    category.id = str(inserted_category.inserted_id)

    # Add a success message to the response
    return {"message": "Category created successfully", "category": category}



@app.delete("/categories/{category_id}", response_model=Category)
def delete_category(category_id: str):
    category = categories_collection.find_one({"_id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Delete the category from the database
    deleted_category = categories_collection.find_one_and_delete({"_id": category_id})

    if not deleted_category:
        raise HTTPException(status_code=500, detail="Failed to delete category")

    # Return the deleted category and a custom response message
    return {"message": "Category deleted successfully", "category": deleted_category}





@app.post("/products/", response_model=Product)
def create_product(product: Product):
    existing_product = find_product_by_name(product.name)
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    product_dict = product.dict()
    inserted_product = products_collection.insert_one(product_dict)
    product.id = str(inserted_product.inserted_id)
    return product


@app.get("/categories/", response_model=List[Category])
def get_categories():
    return list(categories_collection.find({}))


@app.get("/products/", response_model=List[Product])
def get_products():
    return list(products_collection.find({}))


@app.get("/products/{category_id}", response_model=List[Product])
def get_products_by_category(category_id: str):
    return list(products_collection.find({"category_id": category_id}))
