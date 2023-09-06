import os
import requests
import psycopg2
from utils.get_item_from_pos import Get_item_pos
from psycopg2 import OperationalError
from threading import Thread
from utils.get_sum_shop import Get_sum_pos
from flask import Blueprint, render_template, request, redirect, url_for, flash

DPOS_IP = '192.168.1.139'
PORT=os.environ.get('REST_SRV_PORT')
PORT=8888
check_sales_shop = Blueprint('check_sales_shop', __name__)

@check_sales_shop.route('/sales/', methods=['GET'])
def check_item():
    print(request.remote_addr)
    return render_template('check_sales.html')

@check_sales_shop.route('/sales/get', methods=['get'])
def get_item():
    id_shop = request.args.get('shop')
    data = f'{{"shop_number": {id_shop}}}'
    data_of_shop = requests.get(f'http://localhost:8888/api/items', data=data,
                        headers={'Content-Type': 'application/json'}).json()
    
    for data in data_of_shop:
        id_pos = list(filter(lambda x: x["id_attribute"] == 3, data['attributes']))
        sum = Get_sum_pos(data['host'], data['shop']['shop_number'], id_pos[0]['value'], '2022-05-30').get_sum()
        print(data['host'], sum)
    #sum = Get_sum_pos(l[0], id_shop, )
    print()
    return 'ok 299'
