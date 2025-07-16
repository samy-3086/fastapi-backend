from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    price = Column(Float)
    image_url = Column(String)

Base.metadata.create_all(bind=engine)

# Get all products
@app.get("/products")
def read_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return [p.__dict__ for p in products]

# Add new product
@app.post("/products")
def create_product(name: str, brand: str, category: str, price: float, image_url: str):
    db = SessionLocal()
    new = Product(name=name, brand=brand, category=category, price=price, image_url=image_url)
    db.add(new)
    db.commit()
    db.refresh(new)
    db.close()
    return new.__dict__
