import json
from flask import jsonify
from flask_restful import Resource, marshal_with, marshal
from flask_restful import reqparse, request
from models.db_model import Shops, Items, Items_attributes, Phones, Phones_schema
from rest.init_db import db
from rest.init_cache import cache
from service.resources.models_stucture import shop_structure, addressbook_structure
from sqlalchemy.orm.exc import NoResultFound


class AddressBook(Resource):
    def get(self):
        result = {
            "refresh": 30, #refresh time of address book in microsip
            "items":[]
        }
        shops_with_phones = Phones.query.all()
        shops = Shops.query.all()
        
        for shop_phones in shops_with_phones:
            for phone in shop_phones.numbers_list:
                result["items"].append(
                    {
                        "number": phone,
                        "name":  next(f"{shop.name} - {shop.shop_number}" for shop in shops if shop.id == shop_phones.id_shop)

                    }
                )
        return marshal(result,addressbook_structure), 200