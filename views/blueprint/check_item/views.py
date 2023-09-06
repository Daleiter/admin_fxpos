import os
import psycopg2
from utils.get_item_from_pos import Get_item_pos
from psycopg2 import OperationalError
from threading import Thread
from flask import Blueprint, render_template, request, redirect, url_for, flash

DPOS_IP = '192.168.1.139'
PORT=os.environ.get('REST_SRV_PORT')
b_check_item = Blueprint('check_item', __name__)

@b_check_item.route('/check_item/', methods=['GET'])
def check_item():
    print(request.remote_addr)
    return render_template('check_item.html')

@b_check_item.route('/check_item/get', methods=['POST'])
def get_item():
    id_shop = request.form.get('shop')
    barcode = request.form.get('barcode')
    article = request.form.get('article')
    is_barcode = False
    is_article = False
    
    item = None
    if barcode:
        id_barcode = _get_barcode(id_shop, barcode)
        if id_barcode:
            is_barcode = True
            item = _get_item_by_id_barcode(id_shop, id_barcode)
            if item:
                is_article = True

    else:
        id_barcode = None

    if article:
        id_article = _get_article(id_shop, article )
        if id_article:
            item = _get_item_by_id_article(id_shop, id_article)
            is_article = True
            if item:
                is_barcode = True
    else:
        id_article = None
    
    print(id_shop, barcode, article, item)
    data = []
    data.append(item)

    if barcode and is_barcode:
        get_item_pos = Get_item_pos(id_shop, barcode=id_barcode)
        data.extend(get_item_pos.run())

    if article and is_article:
        get_item_pos = Get_item_pos(id_shop, article=id_article)
        data.extend(get_item_pos.run())

   
    return render_template('check_item.html', data=data, is_barcode=is_barcode, is_article=is_article)


def _get_barcode(id_shop, barcode):
    result = None
    query_barcode = f"select t_barcode.id_barcode from pos.t_barcode where id_shop={id_shop} and barcode = '{barcode}';"
    try:
        connect_dpos = psycopg2.connect(database="db_server", user="postgres", host=DPOS_IP, port="5432")
        cursor = connect_dpos.cursor()
        cursor.execute(query_barcode)
        result = cursor.fetchone()
        connect_dpos.close()
    except psycopg2.OperationalError:
        print(f"Oops!  Can not connect to 192.168.1.139")
        return None
    if result:
        return result[0]

def _get_article(id_shop, article):
    result = None
    query_article = f"select t_article.id_article from pos.t_article where id_shop={id_shop} and article = '{article}';"
    try:
        connect_dpos = psycopg2.connect(database="db_server", user="postgres", host=DPOS_IP, port="5432")
        cursor = connect_dpos.cursor()
        cursor.execute(query_article)
        result = cursor.fetchone()
        connect_dpos.close()
    except psycopg2.OperationalError:
        print(f"Oops!  Can not connect to 192.168.1.139")
        return None
    if result:
        return result[0]


def _get_item_by_id_article(id_shop, id_article):
    query_barcode = f"""
            SELECT
    	t_barcode.price[1], 
    	t_article.name, 
    	t_article.article, 
    	t_barcode.barcode, 
    	t_barcode.id_article, 
    	t_barcode.id_barcode, 
    	t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		t_article.id_article = t_barcode.id_article AND
    		t_article.id_shop = t_barcode.id_shop
    WHERE
    	t_article.id_article = '{id_article}' and
        t_article.id_shop = '{id_shop}';
            """
    result = None
    try:
        connect_dpos = psycopg2.connect(database="db_server", user="postgres", host=DPOS_IP, port="5432")
        cursor = connect_dpos.cursor()
        cursor.execute(query_barcode)
        result = cursor.fetchall()
        connect_dpos.close()

    except psycopg2.OperationalError:
            print(f"Oops!  Can not connect to DPOS Server ")
            return None
    if result:
            item = {
                "price": float(result[0][0]),
                "item_name":  result[0][1],
                "article":  result[0][2],
                "barcode":  result[0][3],
                "id_article":  result[0][4],
                "id_barcode":  result[0][5],
                "id_shop":  result[0][6],
                "id_workplace":  "dpos"
            }
    else:
        item = None
    return item

def _get_item_by_id_barcode(id_shop, id_barcode):
    query_barcode = f"""
            SELECT
    	t_barcode.price[1], 
    	t_article.name, 
    	t_article.article, 
    	t_barcode.barcode, 
    	t_barcode.id_article, 
    	t_barcode.id_barcode, 
    	t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		t_article.id_article = t_barcode.id_article AND
    		t_article.id_shop = t_barcode.id_shop
    WHERE
    	t_barcode.id_barcode = '{id_barcode}' and
        t_barcode.id_shop = '{id_shop}';
            """
    result = None
    try:
        connect_dpos = psycopg2.connect(database="db_server", user="postgres", host=DPOS_IP, port="5432")
        cursor = connect_dpos.cursor()
        cursor.execute(query_barcode)
        result = cursor.fetchall()
        connect_dpos.close()

    except psycopg2.OperationalError:
            print(f"Oops!  Can not connect to DPOS Server ")
            return None
    if result:
            item = {
                "price": float(result[0][0]),
                "item_name":  result[0][1],
                "article":  result[0][2],
                "barcode":  result[0][3],
                "id_article":  result[0][4],
                "id_barcode":  result[0][5],
                "id_shop":  result[0][6],
                "id_workplace":  "dpos"
            }
    return item