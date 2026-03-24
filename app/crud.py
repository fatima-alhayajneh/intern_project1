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
    new_order = models.Order(user_id=current_user_id, status="PAID", created_at=datetime.utcnow())
    db.add(new_order)
    db.flush()

    subtotal = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id,
            models.Product.is_deleted == False
        ).first()
        if not product or product.stock_quantity < item.quantity:
            return None

        price_at_purchase = product.price
        if 1 < product.stock_quantity <= 10:
            price_at_purchase = round(product.price * 1.15, 2)
        elif product.stock_quantity == 1:
            price_at_purchase = round(product.price * 1.50, 2)

        subtotal += price_at_purchase * item.quantity
        product.stock_quantity -= item.quantity
        db.add(models.OrderItem(order_id=new_order.id, product_id=product.id, quantity=item.quantity, price_at_purchase=price_at_purchase))

    bundle_discount = round(subtotal * 0.10, 2) if len(order_data.items) >= 2 else 0
    past_spent = db.query(func.sum(models.Order.total_price)).filter(models.Order.user_id == current_user_id).scalar() or 0
    vip_discount = round((subtotal - bundle_discount) * 0.02, 2) if past_spent > 500 else 0

    final_before_tax = subtotal - bundle_discount - vip_discount
    tax = round(final_before_tax * 0.16, 2)
    total_with_tax = round(final_before_tax + tax, 2)

    new_order.total_price = total_with_tax
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    user.loyalty_points += int(total_with_tax)

    db.commit()
    db.refresh(new_order)

    new_order.math_breakdown = {
        "initial_subtotal": subtotal,
        "bundle_discount_10": bundle_discount,
        "vip_discount_2": vip_discount,
        "tax_16_percent": tax,
        "final_total": total_with_tax
    }
    return new_order

def return_order(db: Session, order_id: int, current_user_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user_id).first()
    if not order:
        return {"error": "Order not found"}
    if datetime.utcnow() > (order.created_at + timedelta(hours=24)):
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
        vendor_id=product.vendor_id,
        is_deleted=False
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, min_price=None, max_price=None, category_name=None, in_stock=None, limit: int = 10, offset: int = 0):
    query = db.query(models.Product).filter(models.Product.is_deleted == False)
    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)
    if category_name:
        query = query.join(models.Category).filter(models.Category.name == category_name)
    if in_stock:
        query = query.filter(models.Product.stock_quantity > 0)
    
    products = query.offset(offset).limit(limit).all()
    for p in products:
        if 1 < p.stock_quantity <= 10:
            p.price = round(p.price * 1.15, 2)
        elif p.stock_quantity == 1:
            p.price = round(p.price * 1.50, 2)
    return products

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.is_deleted = True
        db.commit()
        return True
    return False

def create_category(db: Session, category: schemas.CategoryBase):
    db_cat = models.Category(name=category.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def get_admin_dashboard(db: Session):
    top_products_raw = db.query(
        models.Product.name,
        func.sum(models.OrderItem.quantity).label("total_sold")
    ).join(models.OrderItem)\
     .group_by(models.Product.id)\
     .order_by(func.sum(models.OrderItem.quantity).desc())\
     .limit(3).all()

    top_products = [{"name": p[0], "total_sold": p[1]} for p in top_products_raw]

    current_month = datetime.utcnow().month
    total_revenue = db.query(func.sum(models.Order.total_price)).filter(
        func.extract('month', models.Order.created_at) == current_month
    ).scalar() or 0

    low_stock_count = db.query(func.count(models.Product.id)).filter(
        models.Product.stock_quantity < 5,
        models.Product.is_deleted == False
    ).scalar()

    return {
        "top_selling_products": top_products,
        "monthly_revenue": total_revenue,
        "low_stock_items": low_stock_count
    }
