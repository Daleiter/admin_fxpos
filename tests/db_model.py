from sqlalchemy import MetaData, String, Integer, Column, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import fields
from rest.init_db import db, ma

metadata = MetaData(schema='inventory')
Base = declarative_base(metadata=metadata)
class Shops(db.Model):
    __tablename__ = 'shops'
    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False)
    base_ip = Column(String(),  nullable=False)
    active = Column(Boolean(), default=False)
    shop_number = Column(Integer(), nullable=False)
    items = db.relationship('Items', backref='shops')

    def __repr__(self) -> str:
        return "<Shop(id='%s', name='%s', base_ip='%s', active='%s', shop_number='%s')>" % (
                            self.id, self.name, self.base_ip, self.active, self.shop_number)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    


class Items(db.Model):
    __tablename__ = 'items'
    id = Column(Integer(), primary_key=True)
    id_shop = Column(Integer(), ForeignKey(Shops.id), nullable=False)
    host = Column(String(),  nullable=False)
    id_type = Column(Integer(), nullable=False)
    active = Column(Boolean(), default=False)
    shop = db.relationship("Shops", back_populates="items")
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


class Items_schema(ma.Schema):
    class Meta:
        model = Items
    
    id = fields.Integer(load=True, partial=True)
    #shop = fields.Nested(shop_structure)
    host = fields.String(require=True)
    id_type = fields.Integer(require=True)
    active = fields.Boolean(require=True)
    attributes = fields.Nested('Items_attributes_schema', many=False, load=True)

class Items_attributes_schema(ma.Schema):
    class Meta:
        model = Items_attributes
    
    id_item = fields.Integer(load=True, partial=True)
    #shop = fields.Nested(shop_structure)
    id_attribute = fields.Integer(require=True)
    attribute_type = fields.Nested('Attribute_types_schema', many=False, load=True)
    value = fields.String(require=True)

class Attribute_types_schema(ma.Schema):
    class Meta:
        model = Attribute_types
    
    id_attribute = fields.Integer(load=True, partial=True)
    attribute_type = fields.Integer(require=True)
    attribute_name = fields.String(require=True)
    

