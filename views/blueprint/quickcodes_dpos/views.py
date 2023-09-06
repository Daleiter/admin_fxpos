import os
import json
import psycopg2
from xml.dom.minidom import *
from io import StringIO
from datetime import datetime
from werkzeug.wrappers import Response
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sshtunnel import SSHTunnelForwarder
from sshtunnel import open_tunnel


PORT = os.environ.get('REST_SRV_PORT')
quickcodes_dpos = Blueprint('quickcodes_dpos', __name__)


@quickcodes_dpos.route('/goods-dpos/<id_shop>/xml', methods=['GET'])
def get_form_search_check_csv(id_shop):
    response = Response(make_xml(id_shop).toxml(), mimetype='text/xml')
    response.headers.set("Content-Disposition", "attachment",
                         filename=f"goods.xml")
    return response

#def _generate_report(input_data):
#    data = StringIO()
#    w = csv.writer(data, delimiter=';')
#    w.writerow(('РК', 'Каса', 'Касир', 'Дія', 'Артикул', 'Товар', 'Кількість', 'Вартість',
#               'Ціна', 'Номер чеку', 'Час пробивання', 'Знижка', 'Оплата готівкою', 'Оплата картою'))
#    yield data.getvalue()
#    data.seek(0)
#    data.truncate(0)
#
#    for item in input_data:
#        w.writerow([item["id_shop"], item["id_workplace"], item["id_user"], item["id_action"], item["article"], item["name"], item["quantity"],
#                   item["price_sale"], item["price"], item["check_number"], item["date"], item["discount"], item["pay_cash"], item["pay_card"]])
#        yield data.getvalue()
#        data.seek(0)
#        data.truncate(0)

def get_quickcodes(id_shop):
    query = f"""
    SELECT
	pos.t_quickcodes.val, 
	pos.t_quickcodes.description, 
	pos.t_articles_group."name"
FROM
	pos.t_barcode
	INNER JOIN
	pos.t_article
	ON 
		pos.t_barcode.id_article = pos.t_article.id_article AND
		pos.t_barcode.id_shop = pos.t_article.id_shop
	INNER JOIN
	pos.t_articles_group
	ON 
		pos.t_article.id_articles_group = pos.t_articles_group.id_articles_group AND
		pos.t_article.id_shop = pos.t_articles_group.id_shop
	INNER JOIN
	pos.t_quickcodes
	ON 
		pos.t_barcode.barcode = pos.t_quickcodes.val AND
		pos.t_barcode.id_shop = pos.t_quickcodes.id_shop
WHERE
	pos.t_quickcodes.id_shop = {id_shop}  AND "val" NOT LIKE '22%'
ORDER BY "name";
    """

    connect = psycopg2.connect(database="db_server", user="postgres", host='192.168.1.139', port="5432")
    cursor = connect.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connect.close()
    return result

def make_xml(id_shop):
    quickcodes = get_quickcodes(id_shop)

    #get distinct groups
    groups = set()
    for q in quickcodes:
        groups.add(q[2])
    groups = list(groups)

    doc = Document()
    node = doc.createElement('root')
    #doc.createTextNode('bar')
    for g in groups:
        group = doc.createElement('group')
        group.setAttribute("text", g)
        for q in quickcodes:
            if q[2] == g:
                good = doc.createElement("good")
                name = doc.createElement("name")
                name.appendChild(doc.createTextNode(q[1]))
                barcode = doc.createElement("barcode")
                barcode.appendChild(doc.createTextNode(q[0]))
                good.appendChild(name)
                good.appendChild(barcode)
                group.appendChild(good)
        node.appendChild(group)

    doc.appendChild(node)
    return doc