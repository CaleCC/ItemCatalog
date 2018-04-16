from models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Item, Category

engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


category = Category(name='Snowboarding')
session.add(category)

category = Category(name='Fruits')
session.add(category)


item = Item(name='Goggles',
            description='close-fitting eyeglasses with side shields, for' +
            'proecting the eyes from glare, dust, water',
            category_id='1')
session.add(item)


item = Item(name='Apple',
            description='Sweet fruit',
            category_id='2')
session.add(item)

item = Item(name='Cherry',
            description='The cherry fruits of commerce usually are obtained from\
             cultivars of a limited number of species such as \
             the sweet cherry and the sour cherry.',
            category_id='2')
session.add(item)

session.add(item)
session.commit()
