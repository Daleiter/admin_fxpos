from models.db_model import Shops, Items, Item_types, Items_attributes
from models.db_model_cashdesk_shop import ShopsCD, WorkplaceCD
from flask_restful import reqparse, request
from models.db_model import Items
from rest.init_db import db

class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("----------------------RELOAD----------------------")
# __________SHOP__________
        rk =[]
        rkcd =[]
        shops = Shops.query.all()
        shopscd = ShopsCD.query.all()
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
        print(nemashop)
        for shopi in nemashop:
            shop = Shops()
            shop.name = shopi.name_shop
            shop.shop_number = shopi.code_shop
            shop.base_ip = shopi.address
            shop.active = shopi.sign_activity
            db.session.add(shop)
            db.session.commit()
            db.session.refresh(shop)


# __________POS__________



        posescd = WorkplaceCD.query.all()#.filter(WorkplaceCD.sign_activity==1).all()
        id_type = Item_types.query.filter(Item_types.type=='pos').one()
        poses = Items.query.filter(Items.id_type==id_type.id_type).all()#, Items.active==True).all()
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
                    if index_poscd.sign_activity != index_pos.active:
                        index_pos.active = index_poscd.sign_activity
                        db.session.commit()
                        # db.session.refresh(index_pos)
                        #print(i.sign_activity, j.active, j.shop.shop_number, id_workplace)
        set1 = set(pos)
        set2 = set(poscd)
        elements_not_in_poscd = set2 - set1
        nemapos = list(elements_not_in_poscd)
        print(nemapos)
        # for posi in nemapos:
        #     for shop in shops:
        #         if posi.code_shop == shop.shop_number:
        #             item.host = f"192.168.{shop.base_ip}.{posi.id_workplace}"
        #             item.active = posi.sign_activity
        #             item.id_type = 1
        #             item.id_shop = shop.id
        #             db.session.add(item)
        #             db.session.commit()
        #             db.session.refresh(item)