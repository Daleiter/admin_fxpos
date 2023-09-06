import json
from flask_restful import Resource, marshal_with
from flask_restful import reqparse, request
from models.db_model import Shops, Items, Items_attributes, Phones, Phones_schema
from sqlalchemy.orm.exc import NoResultFound
from rest.init_db import db
from rest.init_cache import cache
from service.resources.models_stucture import shop_structure
from sqlalchemy.orm.exc import NoResultFound
from webargs import fields
from webargs.flaskparser import use_args
from utils.ldap_util import LdapUtils


args_schema = {
        'active': fields.Bool(required=False)
    }

class ShopList(Resource):
    """Api for CRUD operations for colection of shops"""
    @use_args(args_schema, location="query")
    #@cache.cached(timeout=60)
    @marshal_with(shop_structure)
    def get(self, args):
        """Get list shops"""
        if 'active' in args:
            if args['active'] == True:
                return Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all(), 200
        
        return Shops.query.order_by(Shops.base_ip.asc()).all(), 200
    
    def post(self):

        with LdapUtils() as ldap_utils:
            for shop_ad in ldap_utils.get_shops_ad():
                print(shop_ad)
                try:
                    shop = Shops.query.filter(Shops.shop_number==shop_ad['id_shop']).one()
                    shop.email = shop_ad['email']
                    db.session.add(shop)
                    db.session.commit()

                except NoResultFound:
                    print(shop_ad, "not found")
                print(shop)


class ShopPhonesList(Resource):
    """Api for CRUD operations for colection of shop phones"""
    @cache.cached(timeout=60)
    def get(self):
        phones = Phones.query.all()
        res = Phones_schema(many=True, only=('id_shop', 'numbers_list')).dump(phones)
        return res, 200

    def post(self):
        json_data = request.get_json(force=True)
        res = Phones_schema().load(json_data)
        db.session.add(res)
        db.session.commit()
        db.session.refresh(res)
        print(res)
        #print(json_data)
        return 200

class ShopPhones(Resource):
    """Api for CRUD operations for colection of shop phones"""
    @cache.cached(timeout=60, key_prefix='shop_number_{shop_number}')
    def get(self, shop_number):
        try:
            shop = Shops.query.filter(Shops.shop_number==shop_number).one()
            phones = Phones.query.filter(Phones.shop == shop).one()
        except NoResultFound:
            phones = Phones()
        res = Phones_schema(only=('id_shop', 'numbers_list')).dump(phones)
        return res, 200
    
    def post(self, shop_number):
        data = request.get_json()

        try:
            shop = Shops.query.filter(Shops.id==shop_number).one()
            phones_all = Phones.query.filter(Shops.id!=shop_number).all()
            for phones_shop in phones_all:
                if data['number'] in phones_shop.numbers_list:
                    phones_shop.numbers_list.remove(data['number'])
            phones = Phones.query.filter(Phones.shop == shop).one()
            if data['number'] in phones.numbers_list:
                return {"error": "Phone duplicate."}, 409
            phones.numbers_list.append(data['number'])
            db.session.add(phones)
            db.session.commit()
            db.session.refresh(phones)
            db.session.close()
        except NoResultFound:
            phones = Phones()
        
        res = Phones_schema(only=('id_shop', 'numbers_list')).dump(phones)
        return res, 200


class Shop(Resource):
    """Api for CRUD opertioms by id shop"""

    @marshal_with(shop_structure)
    def get(self, id_shop):
        """Get shop by id"""
        return Shops.query.filter(Shops.id==id_shop).one(), 200

    @marshal_with(shop_structure)
    def post(self):
        """Create new shop"""
        json_data = request.get_json(force=True)
        shop = Shops()
        shop.name = json_data['shopAddress']
        shop.shop_number = json_data['idShop']
        shop.base_ip = json_data['ipAddress']
        shop.active = True
        db.session.add(shop)
        db.session.commit()
        db.session.refresh(shop)
        for pos_number in range(1,int(json_data['posCount']) + 1):
            item = Items()
            item.host = f"192.168.{json_data['ipAddress']}.{pos_number}"
            item.active = True
            item.id_type = 1
            item.id_shop = shop.id
            #item.attributes.append
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            items_attributes = Items_attributes()
            items_attributes.id_item = item.id
            items_attributes.id_attribute = 1
            items_attributes.value = 'Ubuntu'
            db.session.add(items_attributes)
    
            items_attributes = Items_attributes()
            items_attributes.id_item = item.id
            items_attributes.id_attribute = 2
            items_attributes.value = f"pos-{shop.shop_number}-{pos_number}"
            db.session.add(items_attributes)
    
            items_attributes = Items_attributes()
            items_attributes.id_item = item.id
            items_attributes.id_attribute = 3
            items_attributes.value = str(pos_number)
            db.session.add(items_attributes)
            db.session.commit()
        
        # Add router
        router = Items()
        router.host = f"192.168.{json_data['ipAddress']}.100"
        router.active = True
        router.id_type = 6
        router.id_shop = shop.id
        db.session.add(router)
        db.session.commit()
        db.session.refresh(router)

        # Add a4_printer
        a4_printer = Items()
        a4_printer.host = f"192.168.{json_data['ipAddress']}.31"
        a4_printer.active = True
        a4_printer.id_type = 13
        a4_printer.id_shop = shop.id
        db.session.add(a4_printer)
        db.session.commit()

        # Add price_printer
        price_printer = Items()
        price_printer.host = f"192.168.{json_data['ipAddress']}.30"
        price_printer.active = True
        price_printer.id_type = 13
        price_printer.id_shop = shop.id
        db.session.add(price_printer)
        db.session.commit()

        # Add raspberry
        raspberry = Items()
        raspberry.host = f"192.168.{json_data['ipAddress']}.49"
        raspberry.active = True
        raspberry.id_type = 12
        raspberry.id_shop = shop.id
        db.session.add(raspberry)
        db.session.commit()

        # Add director_pc
        director_pc = Items()
        director_pc.host = f"192.168.{json_data['ipAddress']}.6"
        director_pc.active = True
        director_pc.id_type = 4
        director_pc.id_shop = shop.id
        db.session.add(director_pc)
        db.session.commit()
        db.session.refresh(director_pc)
        director_pc_attributes = Items_attributes()
        director_pc_attributes.id_item = director_pc.id
        director_pc_attributes.id_attribute = 25
        director_pc_attributes.value = 'XXXXXXXXXXXXXXXXXXXXXXXXX=='
        db.session.add(director_pc_attributes)
        db.session.commit()
        # Add switch
        switch = Items()
        switch.host = f"192.168.{json_data['ipAddress']}.254"
        switch.active = True
        switch.id_type = 5
        switch.id_shop = shop.id
        db.session.add(switch)
        db.session.commit()    

        # Add router provider
        router_prov = Items()
        router_prov.host = f"10.129.{json_data['ipAddress']}.2"
        router_prov.active = True
        router_prov.id_type = 9
        router_prov.id_shop = shop.id
        db.session.add(router_prov)
        db.session.commit()
        db.session.refresh(router_prov)
        router_prov_attributes = Items_attributes()
        router_prov_attributes.id_item = router_prov.id
        router_prov_attributes.id_attribute = 20
        router_prov_attributes.value = json_data['provider']
        db.session.add(router_prov_attributes)
        db.session.commit()

        return shop
