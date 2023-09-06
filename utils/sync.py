from models.db_model import Shops
from models.db_model_cashdesk_shop import ShopsCD

class DBSync:
    def __init__(self):
        pass

    def run(self):
        print("Это будет выведено в консоль Flask")
        test =[]
        test2 =[]
        shops = Shops.query.filter(Shops.active==True).order_by(Shops.base_ip.asc()).all()
        for shop in shops:
            test.append(shop.shop_number)
            # print(type(shops))
            # print(shop.shop_number)
        shopscd = ShopsCD.query.all()
        for shopcd in shopscd:
           test2.append(shopcd.code_shop)
        #     # print(shopcd.code_shop)
        # print(shops[1])
        set1 = set(test)
        set2 = set(test2)

        elements_not_in_list2 = set1 - set2

        result_list = list(elements_not_in_list2)

        print(result_list)