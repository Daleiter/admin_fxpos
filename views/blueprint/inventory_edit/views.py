from keyword import kwlist
import os
import re
from unittest import result
import requests
import psycopg2
from views.cache import cache
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify


PORT=os.environ.get('REST_SRV_PORT')
inventory_edit = Blueprint('inventory_edit', __name__)

@inventory_edit.route('/directory', methods=['GET'])
def get_directory():
    shops = requests.get(f'http://localhost:8888/api/shops').json()
    return render_template('shop_directory.html', shops=shops)

@inventory_edit.route('/directory/item', methods=['GET'])
def get_item_modal():
    #shops = requests.get(f'http://localhost:8888/api/items/{id}').json()
    return render_template('modal_form_item_pos.html')

@inventory_edit.route('/directory/shop/<id>', methods=['GET'])
def get_shop(id):
    json_data = requests.get(f'http://localhost:8888/api/items?shop_number={id}').json()
    return render_template('shop.html', shop_data=json_data)
