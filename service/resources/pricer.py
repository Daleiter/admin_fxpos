import json
import requests
from flask import request
from flask_restful import Resource
from requests.auth import HTTPBasicAuth
from models.db_model import Shops


class Pricer(Resource):
    def get(self, code_shop, barcode):
        basic = HTTPBasicAuth('test', '123456')
        base_ip = str(request.remote_addr).split('.')[2]
        shop = Shops.query.filter(Shops.base_ip==base_ip).one()
        price = requests.post(f'http://192.168.1.172:5658/cds/wares/price', json={
                             "request": {"barcode": barcode, "code_shop": shop.shop_number}}, auth=basic).json()
        print(price, request.remote_addr)
        return price, 200
