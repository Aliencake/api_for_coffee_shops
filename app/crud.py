from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy.orm import Session
from app import db_models, schemas
from secrets import token_urlsafe
from fastapi import HTTPException


def revoke_token(db: Session, db_client: db_models.Client, input_password: str):
    if checkpw(input_password.encode('utf-8'), db_client.hashed_password.encode('utf-8')):
        token = token_urlsafe(40)
        setattr(db_client, 'token', token)
        db.commit()
        db.refresh(db_client)
        return {"Ваш новий токен": token}
    else:
        return False


def change_password(db: Session, client: schemas.ClientChangePassword, db_client: db_models.Client):
    if client.token == db_client.token:
        hashed_password = hashpw(client.new_password.encode('utf-8'), gensalt())
        setattr(db_client, 'hashed_password', hashed_password)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return f"Ваш пароль змінено на: {client.new_password}"
    return False


def delete_client(db: Session, client: schemas.ClientDelete, db_client: db_models.Client):
    if not checkpw(client.password.encode('utf-8'), db_client.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Не вірний пароль")
    if not client.token == db_client.token:
        raise HTTPException(status_code=400, detail="Не вірний токен")
    products: db_models.Product | [] = db.query(db_models.Product).filter(db_models.Product.owner_id == db_client.id).all()
    for product in products:
        db.delete(product)
    db.delete(db_client)
    db.commit()
    return f"Кав'ярню {db_client.coffee_shop} успішно видалено"


def get_client(db: Session, user_id: int):
    return db.query(db_models.Client).filter(db_models.Client.id == user_id).first()


def get_client_by_email(db: Session, email: str):
    return db.query(db_models.Client).filter(db_models.Client.email == email).first()


def get_client_by_coffee_shop(db: Session, coffee_shop: str):
    return db.query(db_models.Client).filter(db_models.Client.coffee_shop == coffee_shop).first()


def get_clients(db: Session):
    return db.query(db_models.Client).all()


def create_client(db: Session, client: schemas.ClientCreate, coffee_shop: str):
    hashed_password = hashpw(client.password.encode('utf-8'), gensalt())
    token = token_urlsafe(40)
    db_client = db_models.Client(email=client.email, hashed_password=hashed_password, token=token,
                                 coffee_shop=coffee_shop)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return token


def get_client_id_by_token(db: Session, token: str):
    return db.query(db_models.Client.id).filter(db_models.Client.token == token).first()[0]


def get_products(db: Session, client_id: int):
    return db.query(db_models.Product).filter(db_models.Product.owner_id == client_id).all()


def get_products_by_category(db: Session, client_id: int, category: str):
    return db.query(db_models.Product).filter(db_models.Product.owner_id == client_id).\
        filter(db_models.Product.category == category).all()


def update_product(db: Session, product_id: int, client_id: int, item: schemas.ProductCreate):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == product_id).first()
    if not db_product:
        return False
    elif not db_product.owner_id == client_id:
        return False
    for key, value in item:
        setattr(db_product, key, value)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_product(db: Session, item: schemas.ProductCreate, client_id: int):
    db_product = db_models.Product(**item.dict(), owner_id=client_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int, token: str):

    client_id: int = get_client_id_by_token(db, token)
    db_product: db_models.Product | None = db.query(db_models.Product)\
        .filter(db_models.Product.owner_id == client_id).filter(db_models.Product.id == product_id).first()
    db.delete(db_product)
    db.commit()
    return f"Продукт №{db_product.id} успішно видалено"
