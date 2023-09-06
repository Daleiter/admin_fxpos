from sqlalchemy import  String, Integer, Column, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy  import fields, auto_field
from rest.init_db import db, ma


class GuacamoleConnection(db.Model):
    __table_args__ = {'schema': 'public'}
    __bind_key__ = 'guac_db'
    __tablename__ = 'guacamole_connection'
    connection_id = Column(Integer(), nullable=False, primary_key=True)
    connection_name = Column(String(), nullable=False)
    parent_id = Column(Integer())
    protocol = Column(String(), nullable=False)
    max_connections = Column(Integer())
    max_connections_per_user = Column(Integer())
    failover_only = Column(Boolean(), nullable=False, default=False)

   
    def __repr__(self) -> str:
        return "<GuacamoleConnection(connection_id='%s', connection_name='%s')>" % (
                            self.connection_id, self.connection_name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GuacamoleConnectionParameter(db.Model):
    __table_args__ = {'schema': 'public'}
    __bind_key__ = 'guac_db'
    __tablename__ = 'guacamole_connection_parameter'
    connection_id = Column(Integer(),ForeignKey(GuacamoleConnection.connection_id), nullable=False, primary_key=True)
    parameter_name = Column(String())
    parameter_value = Column(String())

   
    def __repr__(self) -> str:
        return "<GuacamoleConnection(connection_id='%s', connection_name='%s')>" % (
                            self.connection_id, self.connection_name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GuacamoleConnection_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GuacamoleConnection
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    connection_id = auto_field()
    connection_name = auto_field()
    parent_id = auto_field()
    protocol = auto_field()
    max_connections = auto_field()
    max_connections_per_user = auto_field()
    failover_only = auto_field()


class GuacamoleConnectionParameter_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GuacamoleConnectionParameter
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = db.session
    
    connection_id = auto_field()
    parameter_name = auto_field()
    parameter_value = auto_field()