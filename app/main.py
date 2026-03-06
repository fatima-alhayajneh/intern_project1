from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Marco E-commerce Engine")

@app.get("/products/", response_model=list[schemas.ProductResponse])
def read_products(
    min_price: float = None,
    max_price: float = None,
    category_name: str = None,
    in_stock: bool = None,
    db: Session = Depends(database.get_db)
):
    products = crud.get_products(db, min_price=min_price, max_price=max_price, category_name=category_name, in_stock=in_stock)
    return products

@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryBase, db: Session = Depends(database.get_db)):
    return crud.create_category(db=db, category=category)

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    return crud.create_product(db=db, product=product)
@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    return crud.create_order(db=db, order_data=order)
