from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask import session as login_session
app = Flask(__name__)


from sqlalchemy import create_engine,desc
engine = create_engine('sqlite:///catalogwithusers.db')

from sqlalchemy.orm import sessionmaker
from models import Base, User, Item, Category
import random, string


DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def getCatalog():
    catalog = session.query(Category).all()
    latestItems = session.query(Item).order_by(desc(Item.created_time))
    return render_template("catalog.html", catalogs = catalog, latestItems = latestItems)
    #return 'this is the page for display all catalog'


@app.route('/catalog/<int:category_id>/items')
def getCategory(category_id):
    #catalog = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template("items.html", category_id = category_id, items = items)
    #return 'this is the page to display items of a category %d' % category_id


@app.route('/item/<int:item_id>')
def getItem(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    catalog = session.query(Category).filter_by(id = item.category_id).one()
    return render_template("item.html", catalog = catalog, item = item)
    #return 'show description of an item %d that belong to category %d' % item_id, category_id

#add a new category
@app.route('/catalog/new/', methods=['GET','POST'])
def addCatalog():
    if request.method == 'POST':
        newCatalog = Category(name=request.form['name'])
        session.add(newCatalog)
        session.commit()
        return redirect(url_for('getCatalog'))
    else:
        return render_template('newCategory.html')

#should allow delete of a category?
@app.route('/catalog/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('getCatalog'))
    else:
        return render_template('deleteCategory.html',category = category)


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            return redirect(url_for('getCatalog'))
    else:
        return render_template(
            'editCategory.html', category=editedCategory
        )


@app.route('/catalog/<int:category_id>/item/new/', methods=['GET',"POST"])
def newItem(category_id):
        category =  session.query(
            Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            newItem = Item(name=request.form['name'],
                                   description=request.form['description'],
                                   category_id=category_id)
            session.add(newItem)
            session.commit()
            return redirect(url_for('getCategory', category_id=category_id))
        else:
            return render_template('newItem.html', category=category)


@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id, category_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('getItem', item_id = item_id))
    else:
        return render_template(
            'editItem.html', item = editedItem)
    #return 'edit item %d here' % item_id


@app.route('/item/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        category_id = itemToDelete.category_id
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('getCategory',category_id=category_id ))
    else:
        return render_template('deleteItem.html', item=itemToDelete)
    #return 'delete item %d here' %item_id



@app.route('/login', methods=['GET','POST'])
def login():
    print request.method
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = session.query(User).filter_by(username=name).one()
        if user.verify_password(password):
            state = ''.join(random.choice(string.ascii_uppercase+string.digits) for x in xrange(32))
            login_session['state'] = state
            login_session['username'] = name
            print name + ' login successful'
            return redirect('/catalog/')
        else:
            return 400
    else:
        return render_template('login.html')
    

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        print 'method is post'
        name = request.form['name']
        password = request.form['password']
        print name 
        print password
        if name is None or password is None:
            abort(400)
        if session.query(User).filter_by(username = name).first() is not None:
            print 'user ' + name+ ' already exist'
            abort(400)
        user = User(username = name)
        user.hash_password(password)
        session.add(user)
        session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("signup.html")






if __name__ == '__main__':
    app.debug = True
    app.secret_key='tsc%weTD32w3G$'
    app.run(host = '0.0.0.0', port = 8000)
