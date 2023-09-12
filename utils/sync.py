from models.db_model import Shops, Items, Item_types, Items_attributes
from models.db_model_cashdesk_shop import ShopsCD, WorkplaceCD
from models.db_model import Items

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
        
# __________POS__________

        posescd = WorkplaceCD.query.filter(WorkplaceCD.sign_activity==1).all()
        # id_type = Item_types.query.filter(Item_types.type=='pos').one()
        poses = Items.query.filter(Items.id_type==1, Items.active==True).all()
        nemapos = []
        pos = []
        for i in posescd:
            for j in poses:
                id_workplace = None
                for att in j.attributes:
                    if att.id_attribute == 3:
                        id_workplace = att.value
                            # print('i',i.code_shop)
                            # print('j',j.shop.shop_number)
                            # print('i id',i.id_workplace)
                            # print('id',id_workplace)

                if i.code_shop == j.shop.shop_number and str(i.id_workplace) == id_workplace:
                    pass
                else:
                    print(i)
            #print(i.code_shop)
        # for i in q:
        #     if i.shop.id == 2:
        #             print(i)
        # for i in q:
        #         for att in i.attributes:
        #             if att.id_attribute == 3:
        #                 print(att)


        #     con = GuacamoleConnection()
        #     id_pos = "None"
        #     if type == 'pos':
        #         for att in i.attributes:
        #             if att.id_attribute == 3:
        #                 id_pos = att.value