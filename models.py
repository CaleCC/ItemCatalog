from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import os
import sys
import datetime
import sqlalchemy
import sqlalchemy.types
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature,
    SignatureExpired)
import random
import string

Base = declarative_base()
secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    """
    User entity
    This entity is not used because we do not use local authentication
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verity_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user_id = data['id']
        return user_id


class Category(Base):
    """
    category is the parent of item
    """
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    item = relationship('Item', cascade="all, delete-orphan")


class Item(Base):
    """
    item is the child of parent
    it has has category_id to identify the category it belongs to
    ower field idenfity the creater of this item
    """
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String)
    category_id = Column(String(80), ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    owner = Column(String(80), ForeignKey('user.username'))
    user = relationship(User)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category_id': self.category_id,
            'createdTime': self.created_time
        }


engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.create_all(engine)
