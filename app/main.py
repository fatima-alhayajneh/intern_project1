import time
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud, database, auth

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Marco E-commerce Engine V2")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    print(f"INFO: {request.method} {request.url.path} took {process_time:.2f}ms")
    return response

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

@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(limit: int = 10, offset: int = 0, db: Session = Depends(database.get_db)):
    return crud.get_products(db, limit=limit, offset=offset)

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in ["vendor", "admin"]:
        raise HTTPException(status_code=403, detail="Only vendors or admins can add products")
    return crud.create_product(db=db, product=product)

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in ["vendor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete")
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.put("/products/{product_id}/restock")
def restock_product(product_id: int, new_stock: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    result = crud.update_product_safe(db, product_id, current_user.id, new_stock)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result

@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_order = crud.create_order(db=db, order_data=order, current_user_id=current_user.id)
    if not db_order:
        raise HTTPException(status_code=400, detail="Stock not enough or product not found")
    return db_order

@app.post("/orders/{order_id}/return")
def return_order(order_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    result = crud.return_order(db=db, order_id=order_id, current_user_id=current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
@app.get("/admin/dashboard")
def get_dashboard(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return crud.get_admin_dashboard(db)
