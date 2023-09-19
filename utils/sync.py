from models.db_model import Shops, Items, Item_types, Items_attributes
from models.db_model_cashdesk_shop import ShopsCD, WorkplaceCD
from models.db_model_cashdesk import WorkplaceOptions
from flask_restful import reqparse, request
from models.db_model import Items
from rest.init_db import db
import json

class DBSync:
    def __init__(self):
        pass
    
    

    def run(self):
        tokens = WorkplaceOptions.query.filter(WorkplaceOptions.code_option==55).all()
        shops = Shops.query.all()
        shopscd = ShopsCD.query.all()
        posescd = WorkplaceCD.query.all()#.filter(WorkplaceCD.sign_activity==1).all()
        id_type = Item_types.query.filter(Item_types.type=='pos').one()
        poses = Items.query.filter(Items.id_type==id_type.id_type).all()#, Items.active==True).all()


        def is_workpace_prro(shop,workplace=0, tokens=tokens):
            for token in tokens:
                if token.code_shop==shop and token.id_workplace==workplace and token.code_option==55:
                    if 'url' in token.value_option:
                        return 1
            return 0
        
        def get_shop_atributes(rk=-1,id=-1,ip=-1,shops=shops):
            for shop in shops:
                if rk != -1:
                    if shop.shop_number == rk:
                        return shop
                if id != -1:
                    if shop.id == id:
                        return shop
                if ip != -1:
                    if shop.base_ip == ip:
                        return shop
        
        def add_item(host, activity, id_type, shopid):
            item = Items()
            item.host = host
            item.active = activity
            item.id_type = id_type
            item.id_shop = shopid
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            return item

        def add_atributes(itemid, id_attribute, value):
            items_attributes = Items_attributes()
            items_attributes.id_item = itemid
            items_attributes.id_attribute = id_attribute
            items_attributes.value = value
            db.session.add(items_attributes)


        print("----------------------RELOAD----------------------")
# __________SHOP__________
        rk =[]
        rkcd =[]
        for shopcd in shopscd:
            rkcd.append(shopcd)
            for shop in shops:            
                if shop.shop_number == shopcd.code_shop:
                    rk.append(shopcd)
                    if shop.active != shopcd.sign_activity:
                        shop.active = shopcd.sign_activity
                        db.session.commit()
                        db.session.refresh(shop)

        set1 = set(rk)
        set2 = set(rkcd)
        elements_not_in_shop = set2 - set1
        nemashop = (list(elements_not_in_shop))
        #print(nemashop)
        for shopi in nemashop:
            shop = Shops()
            shop.name = shopi.name_shop
            shop.shop_number = shopi.code_shop
            shop.base_ip = shopi.address
            shop.active = shopi.sign_activity
            db.session.add(shop)
            db.session.commit()
            db.session.refresh(shop)
            # add router
            router = add_item(f"192.168.{shopi.address}.100", True, 6, shop.id)
            # router = Items()
            # router.host = f"192.168.{shopi.address}.100"
            # router.active = True
            # router.id_type = 6
            # router.id_shop = shop.id
            # db.session.add(router)
            # db.session.commit()
            # db.session.refresh(router)
            # Add router provider
            router_prov = add_item(f"10.129.{shopi.address}.2", True, 9, shop.id)
            add_atributes(router_prov.id, 20, 'Gigatrans')
            # router_prov = Items()
            # router_prov.host = f"10.129.{shopi.address}.2"
            # router_prov.active = True
            # router_prov.id_type = 9
            # router_prov.id_shop = shop.id
            # db.session.add(router_prov)
            # db.session.commit()
            # db.session.refresh(router_prov)
            
            db.session.commit()



# # __________POS__________


        poscd = []
        pos = []
        for index_poscd in posescd:
            poscd.append(index_poscd)
            for index_pos in poses:
                id_workplace = None
                for att in index_pos.attributes:
                    if att.id_attribute == 3:
                        id_workplace = att.value
                if index_poscd.code_shop == index_pos.shop.shop_number and str(index_poscd.id_workplace) == id_workplace:
                    pos.append(index_poscd)
                    #Update pos active in our DB
                    if index_poscd.sign_activity != index_pos.active:
                        index_pos.active = index_poscd.sign_activity
                        db.session.commit()
                        db.session.refresh(index_pos)
                        #print(i.sign_activity, j.active, j.shop.shop_number, id_workplace)
        set1 = set(pos)
        set2 = set(poscd)
        elements_not_in_poscd = set2 - set1
        nemapos = list(elements_not_in_poscd)
        #print(nemapos)
        for posi in nemapos:
            for shop in shops:
                if posi.code_shop == shop.shop_number:
                    #print(shop.shop_number, posi.id_workplace, is_workpace_prro(shop.shop_number, posi.id_workplace))
                    item = add_item(f"192.168.{shop.base_ip}.{posi.id_workplace}", posi.sign_activity, 1, shop.id)
                    # item = Items()
                    # item.host = f"192.168.{shop.base_ip}.{posi.id_workplace}"
                    # item.active = posi.sign_activity
                    # item.id_type = 1
                    # item.id_shop = shop.id
                    # db.session.add(item)
                    # db.session.commit()
                    # db.session.refresh(item)
                    add_atributes(item.id, 1, 'Ubuntu')
                    add_atributes(item.id, 2, f"pos-{shop.shop_number}-{posi.id_workplace}")
                    add_atributes(item.id, 3, str(posi.id_workplace))
                    add_atributes(item.id, 4, str(is_workpace_prro(shop.shop_number, posi.id_workplace)))
                    db.session.commit()
