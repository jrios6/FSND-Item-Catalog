from flask import Blueprint, render_template, request, redirect ,url_for, flash

## For Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

## For Authentication and authorization
from flask import session as login_session, make_response
import random, string

from oauth2client import client
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2, json
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


simple_page = Blueprint('simple_page', __name__, template_folder='templates')

@simple_page.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
            string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@simple_page.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['credentials']
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['access_token']

        del login_session['user_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['provider']

        flash('You have been successfully logged out')
        return redirect(url_for('home'))
    else:
        flash('You were not logged in')
        return redirect(url_for('home'))


@simple_page.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


@simple_page.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    credentials_json = login_session.get('credentials')
    if credentials_json is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    credentials = client.OAuth2Credentials.from_json(credentials_json)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials.access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@simple_page.route('/fbconnect', methods = ['POST'])
def fbconnect():
    # Validate State Token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    authorization_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    h = httplib2.Http()
    exchange_url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, authorization_token)
    access_token = json.loads(h.request(exchange_url, 'GET')[1])["access_token"]

    debug_url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (authorization_token, access_token)
    fb_id = json.loads(h.request(debug_url, 'GET')[1])['data']['user_id']

    user_info_url = 'https://graph.facebook.com/v2.9/%s?fields=name,id,email&access_token=%s' % (fb_id, access_token)
    data = json.loads(h.request(user_info_url, 'GET')[1])

    print data
    if login_session.get('username') is not None and data['id'] == login_session.get('facebook_id'):
        response = make_response(json.dumps("Current user is already connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token in session for later user in JSON
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['facebook_id'] = data['id']
    login_session['email'] = data['email']

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    login_session['access_token'] = access_token

    user_picture_url = 'https://graph.facebook.com/v2.9/%s/picture?redirect=0&height=200&width=200' % fb_id
    data = json.loads(h.request(user_picture_url, 'GET')[1])['data']
    login_session['picture'] = data['url']

    # Checks if user is already in database
    user_id = getUserIDWithEmail(login_session['email'])
    if user_id is not None:
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@simple_page.route('/gconnect', methods = ['POST'])
def gconnect():
    # Validate State Token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade authorization code to credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If error in access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that access token is for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's user ID doesn't match app ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if login_session.get('credentials') is not None and gplus_id == login_session.get('gplus_id'):
        response = make_response(json.dumps("Current user is already connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token in session for later user in JSON
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    params = {'access_token': credentials.access_token, 'alt': 'json'}

    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Checks if user is already in database
    user_id = getUserIDWithEmail(login_session['email'])
    if user_id is not None:
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


## User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id


def getUserIDWithEmail(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserWithID(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user
