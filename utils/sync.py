from models.db_model import Shops, Items, Item_types, Items_attributes
from models.db_model_cashdesk_shop import ShopsCD, WorkplaceCD
from models.db_model import Items
from rest.init_db import db

class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("----------------------RELOAD----------------------")
# __________SHOP__________
        # rk =[]
        # rkcd =[]
        # shops = Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all()
        # for shop in shops:
        #     rk.append(shop.shop_number)
        # shopscd = ShopsCD.query.filter(ShopsCD.sign_activity==1).all()
        # for shopcd in shopscd:
        #    rkcd.append(shopcd.code_shop)
           
        # set1 = set(rk)
        # set2 = set(rkcd)
        # elements_not_in_list2 = set2 - set1
        # result_list = list(elements_not_in_list2)
        # print(result_list)
        # shop = Shops()
        # shop.name = json_data['shopAddress']
        # shop.shop_number = json_data['idShop']
        # shop.base_ip = json_data['ipAddress']
        # shop.active = True
        # db.session.add(shop)
        # db.session.commit()
        # db.session.refresh(shop)
# __________POS__________

        posescd = WorkplaceCD.query.filter(WorkplaceCD.sign_activity==1).all()
        id_type = Item_types.query.filter(Item_types.type=='pos').one()
        poses = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
        poscd = []
        pos = []
        for i in posescd:
            poscd.append(i)
            for j in poses:
                id_workplace = None
                for att in j.attributes:
                    if att.id_attribute == 3:
                        id_workplace = att.value
                if i.code_shop == j.shop.shop_number and str(i.id_workplace) == id_workplace:
                    pos.append(i)
        set1 = set(pos)
        set2 = set(poscd)
        elements_not_in_poscd = set2 - set1
        nemapos = list(elements_not_in_poscd)
        for posi in nemapos:
            print(posi.shop.name_shop, posi.id_workplace)