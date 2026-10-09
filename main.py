from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Models (Pydantic) define the shape of data and validate it automatically.

# Data the client SENDS when creating a product (no id, the server generates it)
class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True  # default value if client doesn't send it


# Data the client sends when partially updating (PATCH): every field is optional
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None


# Data the server RETURNS: same fields as ProductCreate + an id.
# Used as response_model so responses always have this exact shape.
class Product(ProductCreate):
    id: int


# Mock data
products: list[dict] = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": False},
    {"id": 2, "name": "Headphones", "price": 59.5, "category": "Electronics", "in_stock": False},
    {"id": 3, "name": "Coffee Mug", "price": 12.0, "category": "Kitchen", "in_stock": True},
    {"id": 4, "name": "Desk Chair", "price": 149.0, "category": "Furniture", "in_stock": True},
]


# Helper: look up a product by id, or return a 404 error if it doesn't exist
def find_product(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/")
def home():
    return "Welcome to the home page bilal"


# READ all: GET /products (optionally filter: ?category=Kitchen&in_stock=true)
@app.get("/products", response_model=list[Product])
def list_products(category: Optional[str] = None, in_stock: Optional[bool] = None):
    # No filters given: return everything
    if category is None and in_stock is None:
        return products

    result = []  # start empty, each filter ADDS its matches

    if category is not None:
        for p in products:
            if p["category"].lower() == category.lower():
                result.append(p)

    if in_stock is not None:
        for p in products:
            # add only if it matches and wasn't already added by the category filter
            if p["in_stock"] == in_stock and p not in result:
                result.append(p)

    return result


# READ one: GET /products/1
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    return find_product(product_id)


# CREATE: POST /products (new id = highest existing id + 1)
@app.post("/products", response_model=Product, status_code=201)
def create_product(data: ProductCreate):
    new_id = max((p["id"] for p in products), default=0) + 1
    product = {"id": new_id, **data.model_dump()}
    products.append(product)
    return product


# UPDATE (full): PUT /products/1 (must send all fields)
@app.put("/products/{product_id}", response_model=Product)
def replace_product(product_id: int, data: ProductCreate):
    product = find_product(product_id)
    product.update(data.model_dump())
    return product


# UPDATE (partial): PATCH /products/1 (send only the fields you want to change)
@app.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: int, data: ProductUpdate):
    product = find_product(product_id)
    product.update(data.model_dump(exclude_unset=True))
    return product


# DELETE: DELETE /products/1 (returns nothing on success)
@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    products.remove(find_product(product_id))
