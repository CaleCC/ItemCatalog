from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   jsonify,
                   abort,
                   flash)
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Item, Category
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)
engine = create_engine('sqlite:///catalogwithusers.db')


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


DBSession = sessionmaker(bind=engine)
session = DBSession()


# display all the categories and latest items
@app.route('/')
@app.route('/catalog/')
def getCatalog():
    print login_session
    catalog = session.query(Category).all()
    latestItems = session.query(Item).order_by(desc(Item.created_time))
    return render_template(
        "catalog.html",
        catalogs=catalog,
        latestItems=latestItems
    )


@app.route('/catalog/<int:category_id>/items')
def getCategory(category_id):
    """
    show a list of items that belong to the same category
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template("items.html", category=category, items=items)
    # return 'this is the page to display items of a category %d' % category_id


@app.route('/item/<int:item_id>')
def getItem(item_id):
    """
    display the detailed information of an item
    """
    item = session.query(Item).filter_by(id=item_id).one()
    catalog = session.query(Category).filter_by(id=item.category_id).one()
    return render_template("item.html", catalog=catalog, item=item)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def addCatalog():
    """
    add a new category
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalog = Category(name=request.form['name'])
        session.add(newCatalog)
        session.commit()
        flash('new category added!')
        return redirect(url_for('getCatalog'))
    else:
        return render_template('newCategory.html')


@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """
   delete a category
    """
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('getCatalog'))
    else:
        return render_template('deleteCategory.html', category=category)


@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', "POST"])
def newItem(category_id):
    """
     create a new Item
    """
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category_id,
                       owner=login_session['gplus_id'])
        session.add(newItem)
        session.commit()
        flash('New item added!')
        return redirect(url_for('getCategory', category_id=category_id))
    else:
        return render_template('newItem.html', category=category)


@app.route(
    '/catalog/<int:category_id>/item/<int:item_id>/edit/',
    methods=['GET', 'POST'])
def editItem(item_id, category_id):
    """
    edit an item
    """
    # check if user is logged in, if not redirect to login page
    if 'username' not in login_session:
        flash('Only authorized user can editItem. Please log in.')
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    # only allow owner to edit the item
    if login_session['gplus_id'] != editedItem.owner:
        flash('You are not the owner of the item. Please create a new\
         item of your own to edit')
        return redirect(url_for('newItem', category_id=category_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('getItem', item_id=item_id))
    else:
        return render_template(
            'editItem.html', item=editedItem)
    # return 'edit item %d here' % item_id


@app.route('/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    """
    delete an item
    """
    if 'username' not in login_session:
        flash('Only authorized user can edit the item')
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    # only allow owner to edit the item
    if login_session['gplus_id'] != itemToDelete.owner:
        flash('Only owner of the item can delete it.')
        return redirect(url_for(
            'getCategory', category_id=itemToDelete.category_id))
    if request.method == 'POST':
        category_id = itemToDelete.category_id
        session.delete(itemToDelete)
        session.commit()
        flash('Item deleted.')
        return redirect(url_for('getCategory', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)
    # return 'delete item %d here' %item_id


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    this method followed the idea of udacity course about how to create
    anti forgery Oauth Signin
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
        connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    print 'accsee token = ' + login_session['access_token']
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-we\
    bkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/login', methods=['GET'])
def login():
    """
    render the login page
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    create a new user
    this part of code is not called because the project
    requires google sign in, not local authentication.
    """
    if request.method == 'POST':
        print 'method is post'
        name = request.form['name']
        password = request.form['password']
        print name
        print password
        if name is None or password is None:
            abort(400)
        if session.query(User).filter_by(username=name).first() is not None:
            print 'user ' + name + ' already exist'
            abort(400)
        user = User(username=name)
        user.hash_password(password)
        session.add(user)
        session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("signup.html")


@app.route('/gdisconnect')
def gdisconnect():
    print login_session
    access_token = login_session.get('access_token')

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/\
    revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('getCatalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/item/<int:item_id>/json')
def getCatalogJson(item_id):
    """
    The end point that returns a Json object
    """
    item = session.query(Item).filter_by(id=item_id).one()
    print jsonify(item=item.serialize)
    return jsonify(item=item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'tsc%weTD32w3G$'
    app.run(host='0.0.0.0', port=8000)
