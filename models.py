from operator import index

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):
    __tablename__= 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))#foreignkey demek aynı id den bir başka tabloda da veri olabilir bu şekilde kullanıcın diğer tablolardaki verilerini de inceleyebiliyoruz.


class User(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True )
    email = Column(String, unique=True) #unique : bu mailden birden başka hesap olamaz anlamına gelir
    username = Column(String, unique=True)
    first_name = Column(String)
    hashed_password = Column(String) #hashed yazmamızın sebebi şifrelerin veritabanında direk gözükmesini engeller . kanunen de böyle olmalı
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)
