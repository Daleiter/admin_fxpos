""" Main app for CRUD operations"""
import os
from flask import Flask
from flask_restful import Api

#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

from rest.init_db import db

from service.resources.shops import ShopList
from service.resources.shops import Shop
from service.resources.items import ItemsList
from service.resources.items import Item
from service.resources.discovery import Pos_targets

#basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)


#with app.app_context():
#    db.create_all()

#migrate.init_app(app, db, directory=os.path.join('../migration'))



#api = Api(app)
app.config['SECRET_KEY'] = 'secret_key'
app.config['JSON_AS_ASCII'] = False
app.config['RESTFUL_JSON'] = {
            'ensure_ascii': False
        }
DATABASE_URI = 'postgres+psycopg2://postgres:inventory_atadgp@192.168.1.15:5432/db_inventory'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
api = Api(app)
db.init_app(app)
api.add_resource(ShopList, '/api/shops', '/api/shops')
api.add_resource(Shop, '/api/shops', '/api/shops/<id_shop>')
api.add_resource(ItemsList, '/api/items', '/api/items')
api.add_resource(Item, '/api/items', '/api/items/<id_item>')
api.add_resource(Pos_targets, '/api/postargets', '/api/postargets')

#api.add_resource(DepartmentList, '/api/departments', '/api/departments')
#api.add_resource(Department, '/api/departments', '/api/departments/<id_department>')