from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy  import fields, auto_field
from rest.init_db import db, ma

#metadata = MetaData(schema='inventory')
#Base = declarative_base(metadata=metadata)

class Shops(db.Model):
    __tablename__ = 'shops'
    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False)
    base_ip = Column(String(),  nullable=False)
    active = Column(Boolean(), default=False)
    email = Column(String(),  nullable=True)
    shop_number = Column(Integer(), nullable=False)
    #items = db.relationship('Items', backref='shops')

    def __repr__(self) -> str:
        return "<Shop(id='%s', name='%s', base_ip='%s', active='%s', shop_number='%s')>" % (
                            self.id, self.name, self.base_ip, self.active, self.shop_number)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Phones(db.Model):
    ___tablename__ = 'phones'
    id_shop = Column(Integer(), ForeignKey(Shops.id), nullable=False, primary_key=True)
    numbers_list = Column(MutableList.as_mutable(ARRAY(String)))
    shop = db.relationship("Shops")

    def __repr__(self) -> str:
        return "<Phones(id_shop='%s', numbers_list='%s')>" % (
                            self.id_shop, self.numbers_list)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Items(db.Model):
    __tablename__ = 'items'
    id = Column(Integer(), primary_key=True)
    id_shop = Column(Integer(), ForeignKey(Shops.id), nullable=False)
    host = Column(String(),  nullable=False)
    id_type = Column(Integer(), nullable=False)
    active = Column(Boolean(), default=False)
    shop = db.relationship("Shops") #, back_populates="items"
    attributes = db.relationship("Items_attributes")

    def __repr__(self) -> str:
        return "<Item(id='%s', id_shop='%s', host='%s', id_type='%s', active='%s')>" % (
                            self.id, self.id_shop, self.host, self.id_type, self.active)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Items_attributes(db.Model):
    __tablename__ = 'item_attributes'
    id_item = Column(Integer(), ForeignKey(Items.id), primary_key=True, nullable=False)
    id_attribute = Column(Integer(), primary_key=True)
    value = Column(String(),  nullable=False)
    attribute_type = db.relationship("Attribute_types")


    def __repr__(self) -> str:
        return "<Item(id_item='%s', id_attribute='%s', value='%s')>" % (
                            self.id_item, self.id_attribute, self.value)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Attribute_types(db.Model):
    __tablename__ = 'attibute_types'
    id_attiribute = Column(Integer(), ForeignKey(Items_attributes.id_attribute), primary_key=True, nullable=False)
    id_type = Column(Integer())
    attribute_name = Column(String(),  nullable=False)
    

    def __repr__(self) -> str:
        return "<Item(id_attribute='%s', id_type='%s', attribute_name='%s')>" % (
                            self.id_attribute, self.id_type, self.attribute_name)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Item_types(db.Model):
    __tablename__ = 'item_types'
    id_type = Column(Integer(), ForeignKey(Items_attributes.id_attribute), primary_key=True, nullable=False)
    name = Column(String(), nullable=False)
    type = Column(String(), nullable=False)
    

    def __repr__(self) -> str:
        return "<Item(id_type='%s', name='%s', type='%s')>" % (
                            self.id_type, self.name, self.type)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ListItemsView(db.Model):
    __tablename__ = 'pos_all_info'
    host = Column(String(), primary_key=True)
    vnc_guac = Column(String())
    ssh_guac = Column(String())
    url_guac = Column(String())
    is_prro = Column(Boolean())
    is_router = Column(Boolean())
    is_pc = Column(Boolean())
    id_workplace = Column(String())
    shop_number = Column(Integer())
    active = Column(Boolean())

    def __repr__(self) -> str:
        return "<ListItemsView(host='%s', vnc_guac='%s')>" % (
                            self.host, self.vnc_guac)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Incedent(db.Model):
    __tablename__ = 'incedents'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    time_start = Column(DateTime())
    time_finish = Column(DateTime())
    id_shop = Column(Integer())
    id_item = Column(Integer())
    user = Column(String())
    id_problem = Column(Integer())
    result = Column(String())
    type = Column(Integer())
    active = Column(Boolean())
    add_info = Column(MutableDict.as_mutable(JSON))
    def __repr__(self) -> str:
        return "<Item(id='%s', id_problem='%s', type='%s', add_info='%s')>" % (
                            self.id, self.id_problem, self.type, self.add_info)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Problem(db.Model):
    __tablename__ = 'problems'
    id = Column(Integer(),primary_key=True, nullable=False)
    name = Column(String(), nullable=False)
    id_parent = Column(Integer())
    

    def __repr__(self) -> str:
        return "<Problem(id='%s', name='%s', id_parent='%s')>" % (
                            self.id, self.name, self.id_parent)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Attribute_types_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attribute_types
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session

    attribute_name = auto_field() 

class Shops_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Shops
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id = auto_field()
    name = auto_field()
    base_ip = auto_field()
    active = auto_field()
    email = auto_field()
    shop_number = auto_field()
    #items = fields.Nested(Items_schema, many=True)


class Items_attributes_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Items_attributes
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id_item = auto_field()
    id_attribute = auto_field()
    value = auto_field()
    attribute_type = fields.Nested(Attribute_types_schema, many=True)

class Items_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Items
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id = auto_field()
    shop = fields.Nested(Shops_schema, many=False)
    host = auto_field()
    id_type = auto_field()
    active = auto_field()
    attributes = fields.Nested(Items_attributes_schema, many=True)


class Phones_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Phones
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id_shop = auto_field()
    numbers_list = auto_field()
    shop = fields.Nested(Shops_schema, many=True)

class ListItemsView_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ListItemsView
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    host = auto_field()
    vnc_guac = auto_field()
    ssh_guac = auto_field()
    url_guac = auto_field()
    is_prro = auto_field()
    is_pc = auto_field()
    is_router = auto_field()
    id_workplace = auto_field()
    shop_number = auto_field()
    active = auto_field()
     
class Incedent_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Incedent
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id = auto_field()
    time_start = auto_field()
    time_finish = auto_field()
    id_shop = auto_field()
    id_item = auto_field()
    user = auto_field()
    id_problem = auto_field()
    result = auto_field()
    type = auto_field()
    active = auto_field()
    add_info = auto_field()


class Problem_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Problem
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id = auto_field()
    name = auto_field()
    id_parent = auto_field()
