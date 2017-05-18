from flask import Flask, render_template, request, redirect ,url_for, flash
from flask import session as login_session
from login_management import simple_page
from api_management import api_blueprint

## For Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

app = Flask(__name__)
app.register_blueprint(simple_page)
app.register_blueprint(api_blueprint)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def home():
    categories = session.query(Category).all()
    catalogItems = session.query(CatalogItem).all()

    return render_template("main.html", categories=categories,
                            catalogItems=catalogItems)


@app.route('/catalog/<int:category_id>')
def showCatalog(category_id):
    categories = session.query(Category).all()
    catalogItems = session.query(CatalogItem).filter_by(category_id = category_id).all()

    return render_template("category_catalog.html",
                            categories=categories,
                            category_id=category_id,
                            catalogItems=catalogItems)


@app.route('/catalog/item/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))

        name = request.form['name']
        description = request.form['description']
        category_id= request.form['category_id']

        newItem = CatalogItem(name = name,
                                description = description,
                                category_id = category_id,
                                user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('home'))

    else:
        categories = session.query(Category).all()
        return render_template("add_item.html",
                                categories=categories)


@app.route('/catalog/<int:category_id>/item/<int:item_id>')
def showItem(category_id, item_id):
    category = session.query(Category).filter_by(id = category_id).one()
    item = session.query(CatalogItem).filter_by(id = item_id).one()

    return render_template("item_details.html",
                            category=category,
                            item=item)


@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
            methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    item = session.query(CatalogItem).filter_by(id = item_id).one()

    if login_session['user_id'] != item.user_id:
        return redirect(url_for('showItem', category_id = category_id,
                                            item_id = item_id))

    if request.method == 'POST':
        if item != []:
            item.name = request.form['name']
            item.description = request.form['description']
            item.category_id = request.form['category_id']
            session.add(item)
            session.commit()
            flash("item edited!")
        return redirect(url_for('showCatalog', category_id=category_id))

    else:
        categories = session.query(Category).all()
        return render_template("edit_item.html",
                                categories=categories,
                                item=item)


@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
            methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    item = session.query(CatalogItem).filter_by(id = item_id).one()

    if login_session['user_id'] != item.user_id:
        return redirect(url_for('showItem', category_id = category_id,
                                            item_id = item_id))

    if request.method == 'POST':
        if item != []:
            session.delete(item)
            session.commit()
            flash("item deleted!")
        return redirect(url_for('showCatalog', category_id=category_id))

    return render_template("delete_item.html",
                            item=item)


if __name__ == '__main__':
    app.secret_key = 'abcd'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)