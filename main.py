from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -------------------- CONFIG --------------------

app = FastAPI()

# CORS: allow frontend (Netlify) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://soft-kelpie-3f3e73.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database (Railway PostgreSQL)
DATABASE_URL = "postgresql://postgres:nxcSPNhdeobiAcAWjqwihSdhZYIBVGoQ@centerbeam.proxy.rlwy.net:46423/railway"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------- MODELS --------------------

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    price = Column(Float)
    image_url = Column(String)

Base.metadata.create_all(bind=engine)

# -------------------- SCHEMAS --------------------

class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    price: float
    image_url: str

class ProductUpdate(ProductCreate):
    id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    image_url: str
    class Config:
        orm_mode = True

# -------------------- ROUTES --------------------

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Product API!"}

@app.post("/add_product")
def add_product(product: ProductCreate):
    db = SessionLocal()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()
    return {"message": "✅ Product added successfully", "product_id": new_product.id}

@app.get("/list_products", response_model=list[ProductResponse])
def list_products():
    db = SessionLocal()
    items = db.query(Product).all()
    db.close()
    return items

@app.put("/update_product")
def update_product(product: ProductUpdate):
    db = SessionLocal()
    db_item = db.query(Product).filter(Product.id == product.id).first()
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in product.dict().items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    db.close()
    return {"message": "✅ Product updated successfully"}

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_item = db.query(Product).filter(Product.id == product_id).first()
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_item)
    db.commit()
    db.close()
    return {"message": "🗑️ Product deleted successfully"}

# -------------------- EXTRA: show routes on startup --------------------

from fastapi.routing import APIRoute

@app.on_event("startup")
def show_routes():
    print("Registered API routes:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Path: {route.path} | Methods: {route.methods}")
