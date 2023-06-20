from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    coffee_shop = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    token = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    products = relationship("Product", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    composition = Column(String(255), index=True)
    allergens = Column(String(255), index=True)
    count = Column(Integer, index=True)
    owner_id = Column(Integer, ForeignKey("clients.id"))

    owner = relationship("Client", back_populates="products")
