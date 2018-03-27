from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)


from sqlalchemy import create_engine
engine = create_engine('sqlite:///catalogwithusers.db')

from sqlalchemy.orm import sessionmaker
from models import Base, User, Item, Category

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def getCatalog():
    catalog = session.query(Category).all()
    return render_template("catalog.html", catalogs = catalog)
    #return 'this is the page for display all catalog'


@app.route('/catalog/<int:category_id>/items')
def getItemsOfCatalog(category_id):
    catalog = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template("items.html", catalog = catalog.name, items = items)
    #return 'this is the page to display items of a category %d' % category_id


@app.route('/item/<int:item_id>')
def getItemInformation(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    catalog = session.query(Category).filter_by(id = item.category_id).one()
    return render_template("item.html", catalog = catalog, item = item)
    #return 'show description of an item %d that belong to category %d' % item_id, category_id

#add a new catalog
@app.route('/catalog/new', method=['GET','POST'])
def addCatalog():
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for(getCatalog))
    else:
        return render_template('newCatalog.html')
    return 'add a new catalog'

#should allow delete of a category?
@app.route('/catalog/<int:category_id>/delete/' methods=['GET','POST'])
def deleteCatalog(category_id):
    return 'delete category ' + category_id


@app.route('/catalog/<int:category_id>/edit/', method=['GET', 'POST'])
def editCatalog(category_id):
    editedCatalog = session.query(
        Catalog).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            session.add(editedCatalog)
            session.commit()
            return redirect(url_for('getCatalog'))
    else:
        return render_template(
            'editCatlog.html', catalog=editedCatalog
        )

@app.route('/item/<int:item_id>/edit/' method=['GET', 'POST'])
def editItem(item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('getItemInformation'), item_id = item_id)
    else:
        return render_template(
            'editeItem.html', item_id=item_id)
    #return 'edit item %d here' % item_id


@app.route('/item/<int:item_id>/delete/', method=['GET','POST'])
def deleteItem(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        catefory_id = itemToDelete.category_id
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('getItemsOfCatalog'),category_id=category_id )
    else:
        return render_template('deleteItem.html', item=itemToDelete)
    #return 'delete item %d here' %item_id



@app.route('/login')
def login():
    return 'this is page for login'




if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
