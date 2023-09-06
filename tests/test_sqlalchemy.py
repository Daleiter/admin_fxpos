import os, sys
sys.path.append(os.getcwd())
#from item import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.db_model import Incedent, Shops
from sqlalchemy.orm import Session
engine = create_engine('postgres+psycopg2://postgres:inventory_atadgp@192.168.1.15:5432/db_inventory')
session = Session(engine)

shops = select(Shops)
print(shops)