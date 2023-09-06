#from models.db_model import Shops
from models.db_model_cashdesk_shop import ShopsCD

class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("Это будет выведено в консоль Flask")
        # shops = Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all()
        # for shop in shops:
        #     print(shop.shop_number)
        shops = ShopsCD.query.all()
        for shop in shops:
            print(shop)