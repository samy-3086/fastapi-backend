from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://soft-kelpie-3f3e73.netlify.app/"],  # better: ["https://soft-kelpie-3f3e73.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup (using SQLite; replace with PostgreSQL if needed)
DATABASE_URL = "sqlite:///./test.db"  # For cloud, use something like: postgresql://user:password@host/db
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Product model (SQLAlchemy)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String)
    category = Column(String)
    price = Column(Float)
    image_url = Column(String)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Pydantic model for adding product
class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    price: float
    image_url: str

# Pydantic model for response
class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    image_url: str

    class Config:
        orm_mode = True

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Product API!"}

# Add product endpoint
@app.post("/add_product")
def add_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(
        name=product.name,
        brand=product.brand,
        category=product.category,
        price=product.price,
        image_url=product.image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return {"message": "Product added successfully", "product_id": db_product.id}

# List all products endpoint
@app.get("/list_products", response_model=list[ProductResponse])
def list_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

# Print available routes at startup (helpful for Render logs)
from fastapi.routing import APIRoute

@app.on_event("startup")
def show_routes():
    print("Registered API routes:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Path: {route.path} | Methods: {route.methods}")
