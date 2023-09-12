from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy  import fields, auto_field
from rest.init_db import db, ma


class ShopsCD(db.Model):
    __table_args__ = {'schema': 'pos'}
    __bind_key__ = 'cashdesk_db'
    __tablename__ = 'shops'
    code_shop = Column(Integer(),  nullable=False, primary_key=True)
    name_shop = Column(Integer())
    sign_activity = Column(Integer())
   
    def __repr__(self) -> str:
        return "<shops(code_shop='%s', name_shop='%s')>" % (
                            self.code_shop, self.name_shop, self.sign_activity)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WorkplaceCD(db.Model):
    __table_args__ = {'schema': 'pos'}
    __bind_key__ = 'cashdesk_db'
    __tablename__ = 'workplace'
    version_row_r  = Column(Integer(), primary_key=True)
    code_shop = Column(Integer(), ForeignKey(ShopsCD.code_shop),  nullable=False)
    id_workplace = Column(Integer())
    sign_activity = Column(Integer())
    shop = db.relationship("ShopsCD") #, back_populates="items"

    def __repr__(self) -> str:
        return "<workplace(version_row_r='%s', code_shop='%s', id_workplace='%s', sign_activity='%s')>" % (
                            self.version_row_r, self.code_shop, self.id_workplace, self.sign_activity)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class shops_shema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ShopsCD
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    code_shop = auto_field()
    name_shop = auto_field()
    sign_activity = auto_field()

class workplacecd_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkplaceCD
        load_instance = True
        #include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    version_row_r = auto_field()
    code_shop = auto_field()
    id_workplace = auto_field()
    sign_activity = auto_field()
    shop = fields.Nested(shops_shema, many=False)