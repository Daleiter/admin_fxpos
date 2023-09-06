from flask_restful import Resource, marshal_with
from flask_restful import reqparse
from flask import jsonify, request 
from models.db_model import Items, Item_types, Items_schema, Shops, ListItemsView, ListItemsView_schema
from rest.init_db import db
from rest.init_cache import cache
from sqlalchemy.orm import exc
from service.resources.models_stucture import item_structure
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
import urllib

def cache_key():
   args = request.args
   key = request.path + '?' + urllib.parse.urlencode([
     (k, v) for k in sorted(args) for v in sorted(args.getlist(k))
   ])
   return key

item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('itemtype', type=str, location='args')
item_parser.add_argument('shop_number', type=str, location='args')

class ItemsList(Resource):
    args_schema = {
        'itemtype': fields.Str(required=False),
        'shop_number': fields.Str(required=False)
    }
    """Api for CRUD operations for colection of shops"""
    @cache.cached(timeout=60, key_prefix=cache_key)
    @use_args(args_schema, location="query")
    @marshal_with(item_structure)
    def get(self, args):
        """Get list shops"""
        if args['shop_number']:
            print(args['shop_number'])

            shop = Shops.query.filter(Shops.shop_number==args['shop_number']).one()

            q = Items.query.filter(Items.shop == shop, Items.active==True).order_by(Items.host.asc()).all()
            return q, 200
        elif args['itemtype']:
            id_type = Item_types.query.filter(Item_types.type==args['itemtype']).one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            return q, 200
        else:
            q = Items.query.all()
            return q, 200

class Item(Resource):
    """Api for CRUD opertioms by id shop"""

    @cache.cached(timeout=60, key_prefix='user_{id_item}')
    def get(self, id_item):
        """Get shop by id"""
        item = Items.query.filter(Items.id==id_item).one()
        res = Items_schema().dump(item)
        return res, 200


    def post(self):
        json_data = request.get_json(force=True)
        res = Items_schema().load(json_data)
        db.session.add(res)
        db.session.commit()
        db.session.refresh(res)
        item_json = Items_schema().dump(res)
        return item_json,200
    
class ListItemsViewR(Resource):

    @cache.cached(timeout=60)
    def get(self):
        """Get shop by id"""
        item = ListItemsView.query.filter(ListItemsView.active==True).all()
        res = ListItemsView_schema().dump(item, many=True)
        return res, 200
