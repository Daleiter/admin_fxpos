from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey

metadata = MetaData(schema='inventory')

Shops = Table('shops', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('name', String(), nullable=False),
    Column('base_ip', String(),  nullable=False),
    Column('active', Boolean(), default=False),
    Column('shop_number', Integer(), nullable=False)
    
)

Items = Table('items', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('id_shop', Integer(), ForeignKey(Shops.c.id), nullable=False),
    Column('host', String(),  nullable=False),
    Column('id_type', Integer(), nullable=False),
    Column('active', Boolean(), default=False)
)