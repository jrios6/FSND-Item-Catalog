from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

api_blueprint = Blueprint('api_blueprint', __name__,)


@api_blueprint.route('/catalog/JSON')
def catagoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@api_blueprint.route('/catalog/<int:category_id>/JSON')
def catalogItemsJSON(category_id):
    catalogItems = session.query(CatalogItem).filter_by(
                   category_id=category_id).all()
    return jsonify(CatalogItems=[i.serialize for i in catalogItems])
