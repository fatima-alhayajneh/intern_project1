from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from . import models, schemas, auth

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pass = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pass,
        role=user.role,
        loyalty_points=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_order(db: Session, order_data: schemas.OrderCreate, current_user_id: int):
    product = db.query(models.Product).filter(models.Product.id == order_data.product_id).first()
    if not product or product.stock_quantity < order_data.quantity:
        return None

    current_price = product.price
    if 1 < product.stock_quantity <= 10:
        current_price = round(product.price * 1.15, 2)
    elif product.stock_quantity == 1:
        current_price = round(product.price * 1.50, 2)

    subtotal = current_price * order_data.quantity

    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    total_spent = db.query(func.sum(models.Order.total_price)).filter(models.Order.user_id == current_user_id).scalar() or 0
    
    vip_discount = 0
    if total_spent > 500:
        vip_discount = subtotal * 0.02

    final_price_before_tax = subtotal - vip_discount
    total_with_tax = round(final_price_before_tax * 1.16, 2)

    new_order = models.Order(
        user_id=current_user_id,
        total_price=total_with_tax,
        status="PAID"
    )
    db.add(new_order)
    db.flush()

    product.stock_quantity -= order_data.quantity
    user.loyalty_points += int(total_with_tax)

    order_item = models.OrderItem(
        order_id=new_order.id,
        product_id=product.id,
        quantity=order_data.quantity,
        price_at_purchase=current_price
    )
    db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    return new_order

def return_order(db: Session, order_id: int, current_user_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user_id).first()
    if not order:
        return {"error": "Order not found or not yours"}
    
    time_limit = order.created_at + timedelta(hours=24)
    if datetime.utcnow() > time_limit:
        return {"error": "Return period expired (24h rule)"}
    
    order.status = "RETURNED"
    db.commit()
    return {"message": "Order returned successfully"}

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        vendor_id=product.vendor_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, min_price: float = None, max_price: float = None, category_name: str = None, in_stock: bool = None):
    query = db.query(models.Product)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if category_name:
        query = query.join(models.Category).filter(models.Category.name == category_name)
    if in_stock is True:
        query = query.filter(models.Product.stock_quantity > 0)
    
    products = query.all()
    for product in products:
        if 1 < product.stock_quantity <= 10:
            product.price = round(product.price * 1.15, 2)
        elif product.stock_quantity == 1:
            product.price = round(product.price * 1.50, 2)
    return products

def create_category(db: Session, category: schemas.CategoryBase):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
