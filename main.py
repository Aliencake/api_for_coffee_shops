from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from app import crud, db_models, schemas
from app.database import local_session, engine

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = crud.get_client_by_email(db, email=client.email)

    if not crud.get_client_by_coffee_shop(db, coffee_shop=client.coffee_shop):
        pass
    else:
        raise HTTPException(status_code=400, detail="Назва кав'ярні вже існує")

    if 7 > int(len(client.password)):
        raise HTTPException(status_code=400, detail="Пароль має містити більше 6 символів")
    if db_client:
        raise HTTPException(status_code=400, detail="Ця пошта вже зареєстрована")
    token = crud.create_client(db=db, client=client, coffee_shop=client.coffee_shop)
    return {"Ви успішно зареєстровані, ваш токен": token}
# Dependency


@app.post("/revoke_token")
def revoke_token(client: schemas.ClientLogIn, db: Session = Depends(get_db)):
    db_client: db_models.Client = crud.get_client_by_email(db, email=client.email)
    if db_client:
        response = crud.revoke_token(db=db, db_client=db_client, input_password=client.password)
        if response:
            return response
        else:
            raise HTTPException(status_code=400, detail="Не правильний пароль")
    else:
        raise HTTPException(status_code=400, detail="Користувача не знайдено")


@app.post("/change_password")
def change_password(client: schemas.ClientChangePassword, db: Session = Depends(get_db)):
    if 7 > int(len(client.new_password)):
        raise HTTPException(status_code=400, detail="Пароль має містити більше 6 символів")
    db_client: db_models.Client = crud.get_client_by_email(db, email=client.email)
    if db_client:
        response = crud.change_password(db=db, db_client=db_client, client=client)
        if response:
            return response
        else:
            raise HTTPException(status_code=400, detail="Немає сумісності токену з поштою")
    else:
        raise HTTPException(status_code=400, detail="Користувача не знайдено")


@app.post("/delete_account")
def delete_account(client: schemas.ClientDelete, db: Session = Depends(get_db)):
    db_client: db_models.Client = crud.get_client_by_email(db, email=client.email)
    if db_client:
        return crud.delete_client(db=db, db_client=db_client, client=client)
    else:
        raise HTTPException(status_code=400, detail="Користувача не знайдено")

@app.get("/get_all_shops/")
def all_shops(db: Session = Depends(get_db)):
    clients = crud.get_clients(db)
    return {client.coffee_shop for client in clients}


@app.get("/{coffee_shop}/products/")
def get_products(coffee_shop: str, db: Session = Depends(get_db)):
    client: schemas.Client = crud.get_client_by_coffee_shop(db=db, coffee_shop=coffee_shop)
    if not client:
        raise HTTPException(status_code=400, detail="Кав'ярню не знайдено")
    products = crud.get_products(db, client.id)
    return products


@app.get("/{coffee_shop}/products/{category}")
def get_products_by_category(coffee_shop: str, category: str, db: Session = Depends(get_db)):
    client: schemas.Client = crud.get_client_by_coffee_shop(db=db, coffee_shop=coffee_shop)
    if not client:
        raise HTTPException(status_code=400, detail="Кав'ярню не знайдено")
    products = crud.get_products_by_category(db, client.id, category)
    return products


@app.post("/{client_token}/products/", response_model=schemas.Product)
def create_item_for_client(client_token: str, item: schemas.ProductCreate, db: Session = Depends(get_db)):
    client_id = crud.get_client_id_by_token(db=db, token=client_token)
    return crud.create_product(db=db, item=item, client_id=client_id)


@app.post("/{client_token}/products/{product_id}")
def update_product(client_token: str, product_id: int, item: schemas.ProductCreate, db: Session = Depends(get_db)):
    client_id = crud.get_client_id_by_token(db=db, token=client_token)
    response = crud.update_product(db=db, product_id=product_id, client_id=client_id, item=item)
    if response:
        return response
    else:
        raise HTTPException(status_code=400, detail="Це не ваш продукт")


@app.post("/{client_token}/delete_product/{product_id}")
def delete_product(client_token: str, product_id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db=db, product_id=product_id, token=client_token)
