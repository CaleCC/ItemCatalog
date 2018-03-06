from models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Item, Category

engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(username = 'Eddie')
user.hash_password('12345')
session.add(user)

user2 = User(username = 'Eason')
user2.hash_password('12345')
session.add(user2)
category = Category(name = 'Snowboarding')
session.add(category)

item = Item(name = 'Goggles',
            description = 'close-fitting eyeglasses with side shields, for' +
            'proecting the eyes from glare, dust, water',
            category_id = '1',
            owner_id = '1')

session.add(item)
session.commit()
