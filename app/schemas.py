from pydantic import BaseModel, EmailStr


class ProductBase(BaseModel):
    name: str
    composition: str | None = None
    allergens: str | None = None
    count: int = 0
    category: str | None = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    email: EmailStr
    coffee_shop: str


class ClientCreate(ClientBase):
    password: str


class ClientLogIn(BaseModel):
    email: EmailStr
    password: str


class ClientChangePassword(BaseModel):
    token: str
    new_password: str
    email: EmailStr


class ClientDelete(BaseModel):
    password: str
    token: str
    email: EmailStr


class Client(ClientBase):
    id: int
    products: list[Product] = []

    class Config:
        orm_mode = True

