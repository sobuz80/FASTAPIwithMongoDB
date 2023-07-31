from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List
from models import Category, Product
from bson import ObjectId
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


# Get Category Posts
@app.get("/categories/", response_model=List[dict])
def get_categories():
    categories = list(categories_collection.find({}))
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    categories_with_id_name = []
    for category in categories:
        category_id = str(category["_id"]) 
        category_name = category["name"]
        category_data = {"id": category_id, "name": category_name}
        categories_with_id_name.append(category_data)

    return categories_with_id_name

# Category Post add
@app.post("/categories/", response_model=Category)
def create_category(category: Category):
    existing_category = find_category_by_name(category.name)
    if existing_category:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists")

    category_dict = category.dict()
    inserted_category = categories_collection.insert_one(category_dict)
    category.id = str(inserted_category.inserted_id)

    # Add a success message to the response
    return {"message": "Category created successfully", "category": category}

#Delete
@app.delete("/categories/{category_id}")
def delete_category(category_id: str):
    category_id_obj = ObjectId(category_id)
    result = categories_collection.delete_one({"_id": category_id_obj})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Get Single Categories  by ID
@app.get("/categories/{category_id}", response_model=Category)
def get_single_category(category_id: str):
    category_id_obj = ObjectId(category_id)
    category = categories_collection.find_one(
        {"_id": category_id_obj}, {"name": 1})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Construct the JSON response with only the name and _id fields
    response_data = {
        "_id": str(category["_id"]),
        "name": category["name"]
    }
    return JSONResponse(content=response_data)

#Update
@app.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: str, updated_category: Category):
    category_id_obj = ObjectId(category_id)
    existing_category = categories_collection.find_one(
        {"_id": category_id_obj})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = updated_category.dict(exclude_unset=True)
    categories_collection.update_one(
        {"_id": category_id_obj}, {"$set": update_data})
    updated_category = categories_collection.find_one({"_id": category_id_obj})
    return updated_category

#Grt
@app.get("/products/", response_model=List[Product])
def get_products():
    return list(products_collection.find({}))
#Add 
@app.post("/products/", response_model=Product)
def create_product(product: Product):
    existing_product = find_product_by_name(product.name)
    if existing_product:
        raise HTTPException(
            status_code=400, detail="Product with this name already exists")
    product_dict = product.dict()
    inserted_product = products_collection.insert_one(product_dict)
    product.id = str(inserted_product.inserted_id)
    return product

#Delete
def find_and_delete_product_by_id(product_id: str):
    try:
        product_obj_id = ObjectId(product_id)
        product = products_collection.find_one({'_id': product_obj_id})
        if product:
            products_collection.delete_one({'_id': product_obj_id})
            return product
        return None  # Product with the given ID not found.
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: str):
    # Assuming you have a function to find and delete the product by its ID
    deleted_product = find_and_delete_product_by_id(product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product

#Edit
@app.get("/products/{product_id}/", response_model=Product)
def get_single_product(product_id: str):
    # Convert the provided product_id to an ObjectId
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product_id")
    product = products_collection.find_one({"_id": obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

#updating
@app.put("/products/{product_id}/", response_model=Product)
def update_product(product_id: str, updated_product: Product):
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product_id")
    product = products_collection.find_one({"_id": obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = updated_product.dict(exclude_unset=True)
    products_collection.update_one({"_id": obj_id}, {"$set": update_data})
    #return updated_product
    return {
        "message": "Product updated successfully",
        "updated_product": updated_product
    }