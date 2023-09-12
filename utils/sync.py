from models.db_model import Shops
from models.db_model_cashdesk_shop import ShopsCD

class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("----------------------RELOAD----------------------")
        rk =[]
        rkcd =[]
        shops = Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all()
        for shop in shops:
            rk.append(shop.shop_number)
        shopscd = ShopsCD.query.filter(ShopsCD.sign_activity==1).all()
        for shopcd in shopscd:
           rkcd.append(shopcd.code_shop)
           
        set1 = set(rk)
        set2 = set(rkcd)
        elements_not_in_list2 = set2 - set1
        result_list = list(elements_not_in_list2)
        print(result_list)