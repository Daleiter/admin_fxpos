from models.db_model import Shops, Items, Item_types, Items_attributes
from models.db_model_cashdesk_shop import ShopsCD, WorkplaceCD
from models.db_model_cashdesk import WorkplaceOptions
from models.db_model import Items
from rest.init_db import db
from views.logger import get_logger

class DBSync:
    def __init__(self):
        self.logger = get_logger(__name__)
        pass
    
    

    def run(self):
        tokens = WorkplaceOptions.query.filter(WorkplaceOptions.code_option==55).all()
        shops = Shops.query.all()
        shopscd = ShopsCD.query.all()
        posescd = WorkplaceCD.query.all()
        id_type = Item_types.query.filter(Item_types.type=='pos').one()
        poses = Items.query.filter(Items.id_type==id_type.id_type).all()


        def is_workpace_prro(shop,workplace=0, tokens=tokens):
            shop =str(shop)
            workplace = str(workplace)
            for token in tokens:
                if str(token.code_shop)==shop and str(token.id_workplace)==workplace and token.code_option==55:
                    if 'url' in token.value_option:
                        return str(1)
            return str(0)
        
        def difference_set(set1=None, set2=None):
            set1 = set(set1)
            set2 = set(set2)
            elements_not_in_shop = set2 - set1
            elements_not_in_shop = (list(elements_not_in_shop))
            return(elements_not_in_shop)

        def add_item(host, activity, id_type, shopid):
            item = Items()
            item.host = host
            item.active = activity
            item.id_type = id_type
            item.id_shop = shopid
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            self.logger.debug(f"Add {item}")
            return item

        def add_atributes(itemid, id_attribute, value):
            items_attributes = Items_attributes()
            items_attributes.id_item = itemid
            items_attributes.id_attribute = id_attribute
            items_attributes.value = value
            db.session.add(items_attributes)
        
        def update_active(cd_value, db_value):
            if db_value.active != cd_value.sign_activity:
                self.logger.debug(f"{db_value} --> {cd_value}")
                db_value.active = cd_value.sign_activity
                db.session.commit()
                db.session.refresh(db_value)
        def update_prro_status(index_poscd, index_pos):
            prro = is_workpace_prro(index_poscd.code_shop, index_poscd.id_workplace)
            for attribute in index_pos.attributes:
                if attribute.id_attribute==4:
                    if attribute.value != prro:
                        self.logger.debug(f"{prro} --> {attribute}")
                        attribute.value = prro
                        db.session.commit()
                        db.session.refresh(attribute)



        self.logger.debug("Sync pos and shop")
# __________SHOP__________
        rk =[]
        rkcd =[]
        for shopcd in shopscd:
            rkcd.append(shopcd)
            for shop in shops:            
                if shop.shop_number == shopcd.code_shop:
                    rk.append(shopcd)
                    #Update shop active in our DB
                    update_active(shopcd, shop)
        nemashop = difference_set(rk, rkcd)
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
            self.logger.debug(f"Add {shop}")
            # add items
            router = add_item(f"192.168.{shopi.address}.100", shopi.sign_activity, 6, shop.id)
            router_prov = add_item(f"10.129.{shopi.address}.2", shopi.sign_activity, 9, shop.id)
            add_atributes(router_prov.id, 20, 'Gigatrans')
            printer = add_item(f"192.168.{shopi.address}.31", shopi.sign_activity, 13, shop.id)
            price_printer = add_item(f"192.168.{shopi.address}.30", shopi.sign_activity, 13, shop.id)
            raspberry = add_item(f"192.168.{shopi.address}.49", shopi.sign_activity, 12, shop.id)
            director_pc = add_item(f"192.168.{shopi.address}.6", shopi.sign_activity, 4, shop.id)
            add_atributes(director_pc.id, 25, 'XXXXXXXXXXXXXXXXXXXXXXXXX==')
            switch = add_item(f"192.168.{shopi.address}.254", shopi.sign_activity, 5, shop.id)



# # __________POS__________

        shops = Shops.query.all()
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
                    update_prro_status(index_poscd, index_pos)
                    # Update pos active in our DB
                    update_active(index_poscd, index_pos)
        nemapos = difference_set(pos, poscd)
        for posi in nemapos:
            for shop in shops:
                if posi.code_shop == shop.shop_number:
                    #print(shop.shop_number, posi.id_workplace, is_workpace_prro(shop.shop_number, posi.id_workplace))
                    item = add_item(f"192.168.{shop.base_ip}.{posi.id_workplace}", posi.sign_activity, 1, shop.id)
                    add_atributes(item.id, 1, 'Ubuntu')
                    add_atributes(item.id, 2, f"pos-{shop.shop_number}-{posi.id_workplace}")
                    add_atributes(item.id, 3, str(posi.id_workplace))
                    add_atributes(item.id, 4, str(is_workpace_prro(shop.shop_number, posi.id_workplace)))
                    db.session.commit()
