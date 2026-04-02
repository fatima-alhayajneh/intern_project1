import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, auth
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.is_deleted == False).offset(skip).limit(limit).all()

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.create_product(db=db, product=product)

@app.delete("/products/{product_id}")
def soft_delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_deleted = True
    db.commit()
    return {"message": "Product deleted successfully"}

@app.get("/admin/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    top_selling = crud.get_top_selling_products(db)
    monthly_rev = crud.get_monthly_revenue(db)
    low_stock = crud.get_low_stock_items(db)
    formatted_top_products = [{"name": str(item[0].name), "sold": int(item[1])} for item in top_selling] if top_selling else []
    return {
        "top_selling_products": formatted_top_products,
        "monthly_revenue": float(monthly_rev) if monthly_rev else 0.0,
        "low_stock_items_count": len(low_stock) if low_stock else 0
    }

@app.patch("/products/{product_id}/restock")
def restock_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock_quantity += 10
    db.commit()
    return {"message": "Stock updated", "new_stock": product.stock_quantity}

@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_order(db=db, order=order, user_id=current_user.id)
