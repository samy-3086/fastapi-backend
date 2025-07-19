from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil
import os
import uuid

app = FastAPI()

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS: allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://soft-kelpie-3f3e73.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = "postgresql://postgres:nxcSPNhdeobiAcAWjqwihSdhZYIBVGoQ@centerbeam.proxy.rlwy.net:46423/railway"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Model
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    price = Column(Float)
    image_url = Column(String)

Base.metadata.create_all(bind=engine)

# Schemas
class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    image_url: str
    class Config:
        orm_mode = True

# Routes
@app.post("/add_product")
async def add_product(
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...)
):
    # Save file
    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = f"/uploads/{filename}"

    db = SessionLocal()
    new_product = Product(name=name, brand=brand, category=category, price=price, image_url=image_url)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()
    return {"message": "✅ Product added", "product_id": new_product.id}

@app.get("/list_products", response_model=list[ProductResponse])
def list_products():
    db = SessionLocal()
    items = db.query(Product).all()
    db.close()
    return items

@app.put("/update_product/{product_id}")
async def update_product(
    product_id: int,
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None)  # optional new image
):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = name
    product.brand = brand
    product.category = category
    product.price = price

    if image:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        filepath = os.path.join("uploads", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)
    db.close()
    return {"message": "✅ Product updated"}

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    db.close()
    return {"message": "🗑️ Product deleted"}

@app.get("/")
def root():
    return {"message": "FastAPI file upload CRUD ready"}
