import base64
from flask_restful import Resource
from models.db_model import Items, Item_types, Items_attributes
from models.db_model_guac import db, GuacamoleConnection, GuacamoleConnection_schema, GuacamoleConnectionParameter
from sqlalchemy import exc
from views.logger import get_logger

class GuacamoleConnectionList(Resource):
    """Api for CRUD operations for colection of shops"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def get(self):
        """Get list shops"""
        self.create_connections('pc')
        workplaceOptions = GuacamoleConnection.query.all()
        res = GuacamoleConnection_schema().dump(workplaceOptions, many=True)
        db.session.close()
        return res, 200

    def create_connections(self, type):
        id_type = Item_types.query.filter(Item_types.type==type).one()
        q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all() 
        for i in q:
            con = GuacamoleConnection()
            id_pos = "None"
            if type == 'pos':
                for att in i.attributes:
                    if att.id_attribute == 3:
                        id_pos = att.value
            if type == 'pc':
                for att in i.attributes:
                    if att.id_attribute == 31:
                        id_pos = att.value

            con.connection_id = i.id
            #self.logger.info(self.generate_guacamole_url(i.id))
            con.connection_name = f"{type}-{i.shop.shop_number}-{id_pos}"
            con.parent_id = 2
            con.protocol = 'vnc'
            con.max_connections = 3
            con.max_connections_per_user = 3
            db.session.add(con)
            
            try:
                db.session.commit()
                db.session.refresh(con)
            except exc.IntegrityError as e:
                #self.logger.debug("Alredy exist", con)
                db.session.rollback()
            
            try:
                if type == 'pos':
                    self.createConnParams(i.id, i.host, 'Cthdbc@0')
                elif  type == 'pc':
                     self.createConnParams(i.id, i.host, 'vldh_rem')
            except exc.IntegrityError as e:
                #self.logger.debug("Alredy exist", con)
                db.session.rollback()

            try:
                if type == 'pos':
                    item_attributes = Items_attributes(id_item=i.id, id_attribute=29, value=self.generate_guacamole_url(i.id))
                elif  type == 'pc':
                     item_attributes = Items_attributes(id_item=i.id, id_attribute=30, value=self.generate_guacamole_url(i.id))
                db.session.add(item_attributes)
                db.session.commit()
            except exc.IntegrityError as e:
                #self.logger.debug("Alredy exist", con)
                db.session.rollback()


    def generate_guacamole_url(self, id):
        # Convert the input string to bytes
        input_string = f'{id}\0c\0postgresql'
        input_bytes = input_string.encode('utf-8')
    
        # Encode the bytes using base64
        base64_param = base64.b64encode(input_bytes).decode('utf-8')
    
        # Generate the URL
        url = f"http://automate-it.lvivkholod.int:18088/guacamole/#/client/{base64_param}"
        return url
    

    def createConnParams(self, id, ip, password):
        p = GuacamoleConnectionParameter()
        p.connection_id = id
        p.parameter_name = 'password'
        p.parameter_value = password
        db.session.add(p)
        db.session.commit()

        p = GuacamoleConnectionParameter()
        p.connection_id = id
        p.parameter_name = 'hostname'
        p.parameter_value = ip
        db.session.add(p)
        db.session.commit()

        p = GuacamoleConnectionParameter()
        p.connection_id = id
        p.parameter_name = 'port'
        p.parameter_value = '5900'
        db.session.add(p)
        db.session.commit()

        p = GuacamoleConnectionParameter()
        p.connection_id = id
        p.parameter_name = 'username'
        p.parameter_value = 'root'
        db.session.add(p)
        db.session.commit()