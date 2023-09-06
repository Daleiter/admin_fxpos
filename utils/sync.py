from models.db_model import Shops


class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("Это будет выведено в консоль Flask")
        # shops = Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all()
        # for shop in shops:
        #     print(shop.shop_number)