from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy  import fields, auto_field
from rest.init_db import db, ma


class ShopsCD(db.Model):
    __table_args__ = {'schema': 'pos'}
    __bind_key__ = 'cashdesk_db'
    __tablename__ = 'shops'
    code_shop = Column(Integer(),  nullable=False, primary_key=True)
    name_shop = Column(Integer(), default=False, primary_key=True)
   
    def __repr__(self) -> str:
        return "<shops(code_shop='%s', name_shop='%s')>" % (
                            self.code_shop, self.name_shop)

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

