from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud, database, auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Marco E-commerce Engine V2")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(
    min_price: float = None,
    max_price: float = None,
    category_name: str = None,
    in_stock: bool = None,
    db: Session = Depends(database.get_db)
):
    return crud.get_products(db, min_price=min_price, max_price=max_price, category_name=category_name, in_stock=in_stock)

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can add products")
    return crud.create_product(db=db, product=product)

@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryBase, db: Session = Depends(database.get_db)):
    return crud.create_category(db=db, category=category)

@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_order = crud.create_order(db=db, order_data=order, current_user_id=current_user.id)
    if not db_order:
        raise HTTPException(status_code=400, detail="Stock not enough or product not found")
    return db_order

@app.post("/orders/{order_id}/return")
def return_order(
    order_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = crud.return_order(db=db, order_id=order_id, current_user_id=current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
