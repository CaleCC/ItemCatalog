from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/catalog')
def getCatalog():
    return 'this is the page for display all catalog'


@app.route('/catalog/<int:category_id>/items')
def getItemsOfCatalog(category_id):
    return 'this is the page to display items of a category %d' % category_id


@app.route('/catalog/<int:category_id>/<int:item_id>')
def getItemInformation(category_id):
    return 'show description of an item %d that belong to category %d' % item_id, category_id


@app.route('/catalog/new')
def addCatalog():
    return 'add a new catalog'


@app.route('/catalog/<int:category_id>/delete')
def deleteCatalog(catefory_id):
    return 'delete category ' + category_id


@app.route('/catalog/<int:category_id>/edit')
def editCatalog(category_id):
    return 'edit category %d' % category_id


@app.route('/login')
def login():
    return 'this is page for login'


@app.route('/item/<int:item_id>/edit')
def editItem(item_id):
    return 'edit item %d here' % item_id


@app.route('/item/<int:item_id>/delete')
def deleteItem(item_id):
    return 'delete item %d here' %item_id

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
