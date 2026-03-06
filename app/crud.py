from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def get_products(db: Session, min_price: float = None, max_price: float = None, category_name: str = None, in_stock: bool = None):
    query = db.query(models.Product)

    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)

    if category_name:
        query = query.join(models.Product.category).filter(models.Category.name == category_name)

    if in_stock is True:
        query = query.filter(models.Product.stock_quantity > 0)

    products = query.all()

    for product in products:
        product.low_stock_warning = product.stock_quantity < 5

    return products

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_category(db: Session, category: schemas.CategoryBase):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
from fastapi import HTTPException

def create_order(db: Session, order_data: schemas.OrderCreate):
    subtotal = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail="Product unavailable or out of stock")
        subtotal += product.price * item.quantity

    total_with_tax = subtotal * 1.16

    db_order = models.Order(user_id=1, total_price=total_with_tax, status="PENDING")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        product.stock_quantity -= item.quantity
        
        log = models.InventoryLog(product_id=product.id, change_amount=-item.quantity, reason="Sale")
        db.add(log)
    
    db.commit()
    return db_order

def create_order(db: Session, order_data: schemas.OrderCreate):
    subtotal = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail="Product unavailable or insufficient stock")
        subtotal += product.price * item.quantity

    total_with_tax = subtotal * 1.16

    db_order = models.Order(user_id=1, total_price=total_with_tax, status="PENDING")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        product.stock_quantity -= item.quantity

        inventory_log = models.InventoryLog(product_id=product.id, change_amount=-item.quantity, reason="Sale")
        db.add(inventory_log)
    
    db.commit()
    return db_order
