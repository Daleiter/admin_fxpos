from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy  import fields, auto_field
from rest.init_db import db, ma


class WorkplaceOptions(db.Model):
    __table_args__ = {'schema': 'pos'}
    __bind_key__ = 'cashdesk_db'
    __tablename__ = 'workplace_options'
    id_workplace = Column(Integer(), nullable=False, primary_key=True)
    value_option = Column(String())
    code_shop = Column(Integer(),  nullable=False, primary_key=True)
    code_module = Column(Integer(), default=False, primary_key=True)
    code_option = Column(Integer(), nullable=False, primary_key=True)
   
    def __repr__(self) -> str:
        return "<WorkplaceOptions(id_workplace='%s', value_option='%s', code_shop='%s', code_module='%s', code_option='%s')>" % (
                            self.id_workplace, self.value_option, self.code_shop, self.code_module, self.code_option)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WorkplaceOptions_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkplaceOptions
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    id_workplace = auto_field()
    value_option = auto_field()
    code_shop = auto_field()
    code_module = auto_field()
    code_option = auto_field()

