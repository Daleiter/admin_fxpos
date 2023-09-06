import os
import json
import psycopg2
import csv
from io import StringIO
from datetime import datetime
from werkzeug.wrappers import Response
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sshtunnel import SSHTunnelForwarder
from sshtunnel import open_tunnel


PORT = os.environ.get('REST_SRV_PORT')
pos_get_lost_check = Blueprint('get_lost_check', __name__)


@pos_get_lost_check.route('/getlostcheck', methods=['POST'])
def get_lost_check():
    id_shop = request.form.get('idshop')
    id_workplace = request.form.get('idworkplace')
    id_check = request.form.get('idcheck')
    print(id_shop, id_workplace, id_check)
    host = get_ip_pos(tradepoint=id_shop, cash_box=id_workplace)
    data = get_check_from_db(host=host, id_shop=id_shop,
                             id_workplace=id_workplace, id_check=id_check)

    return render_template('get_lost_check.html', json=json, data=data, id_shop=id_shop, id_workplace=id_workplace, id_check=id_check)


@pos_get_lost_check.route('/getlostcheck', methods=['GET'])
def get_form_search_check():
    return render_template('get_lost_check.html')


@pos_get_lost_check.route('/getlostcheck/csv', methods=['GET'])
def get_form_search_check_csv():
    id_shop = request.args.get('idshop')
    id_workplace = request.args.get('idworkplace')
    id_check = request.args.get('idcheck')
    print(id_shop, id_workplace, id_check)
    host = get_ip_pos(tradepoint=id_shop, cash_box=id_workplace)
    data = get_check_from_db(host=host, id_shop=id_shop,
                             id_workplace=id_workplace, id_check=id_check)
    response = Response(_generate_report(data), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment",
                         filename=f"check-{id_shop}-{id_workplace}-{id_check}.csv")
    return response


def get_check_from_db(host, id_shop, id_workplace, id_check):

    # connect to db via ssh tunnel
    server = SSHTunnelForwarder(
        host,
        ssh_username="root",
        ssh_password="toor",
        remote_bind_address=('localhost', 5432)
    )
    server.start()
    #connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host='192.168.1.14', port="5432")

    connect = psycopg2.connect(database="db_client", user="postgres",
                               password="", host='localhost', port=server.local_bind_port)
    sql_requset = f"""
  SELECT
  DISTINCT on (pos.t_audit_action.id_article)
  pos.t_audit_action.id_shop AS "РК",
	pos.t_audit_action.id_workplace AS "Каса",
	pos.t_audit_action.id_user AS "Касир",
	pos.t_audit_action.id_event AS "Дія",
	pos.t_article.article AS "Артикул",
	pos.t_article."name" AS "Товар",
	pos.t_audit_action.quantity AS "Кількість",
	pos.t_audit_action.price_sale AS "Вартість",
	pos.t_audit_action.check_number AS "Номер чеку",
	pos.t_audit_action.date_event AS "Час пробивання",
	pos.t_audit_action.memo AS "full" 
FROM
	pos.t_audit_action
	INNER JOIN pos.t_article ON pos.t_audit_action.id_article = pos.t_article.id_article 
WHERE
	pos.t_audit_action.check_number = {id_check} AND
	pos.t_audit_action.id_shop = {id_shop} AND
	pos.t_audit_action.id_workplace = {id_workplace}
    ORDER BY pos.t_audit_action.id_article, pos.t_audit_action.date_event desc;
  """

    sql_requset_close = f"""
  SELECT
	pos.t_audit_action.id_shop AS "РК",
  pos.t_audit_action.id_workplace AS "Каса",
	pos.t_audit_action.id_user AS "Касир",
	pos.t_audit_action.id_event AS "Дія",
    'none' AS "Артикул",
	'none' AS "Товар",
    'none' AS "Кількість",
	pos.t_audit_action.price_sale AS "Вартість",
	pos.t_audit_action.check_number AS "Номер чеку",
	pos.t_audit_action.date_event AS "Час пробивання",
	pos.t_audit_action.memo AS "full" 
FROM
	pos.t_audit_action 
WHERE
	pos.t_audit_action.id_event = 21 AND
	pos.t_audit_action.check_number = {id_check} AND
	pos.t_audit_action.id_shop = {id_shop} AND
	pos.t_audit_action.id_workplace = {id_workplace};
  """
    #connect = psycopg2.connect(database="db_client", user="postgres", password="", host=host, port="5432")
    cursor = connect.cursor()
    cursor.execute(sql_requset)
    result_items = cursor.fetchall()
    result = []
    for item in result_items:
        memo = json.loads(item[10])
        memo_json = json.dumps(memo, ensure_ascii=False)
        #item_list = list(item)
        memo_json = json.loads(item[10])
        item_list = {
            "id_shop": item[0],
            "id_workplace": item[1],
            "id_user": item[2],
            "id_action": item[3],
            "article": item[4],
            "name": item[5],
            "quantity": item[6],
            "price_sale": item[7],
            "price": memo_json['sum'],
            "check_number": item[8],
            "date": item[9],
            # "memo": memo_json,
            "discount": memo_json['discount'],
            "pay_cash": '',
            "pay_card": ''

        }
        #item_list[9] = memo_json
        result.append(item_list)

    cursor.execute(sql_requset_close)
    result_close = list(cursor.fetchone())
    close_check = json.loads(result_close[10])
    type_pay = ''
    if close_check["CashSum"] != 0:
        type_pay = 'close_cash'
    else:
        type_pay = 'close_card'
    res_dict = {
        "id_shop": result_close[0],
        "id_workplace": result_close[1],
        "id_user": result_close[2],
        "id_action": result_close[3],
        "article": '',
        "name": '',
        "quantity": '',
        "price_sale": result_close[7],
        "price": '',
        "check_number": result_close[8],
        "date": result_close[9],
        # "memo": type_pay
        "discount": close_check['DiscountSum'],
        "pay_cash": close_check['CashSum'],
        "pay_card": close_check['CardSum']
    }

    result.append(res_dict)

    server.stop()
    return result


def get_ip_pos(tradepoint, cash_box):

    # connect to db via ssh tunnel
    server = SSHTunnelForwarder(
        '192.168.1.14',
        ssh_username="root",
        ssh_password="vldh_adm",
        remote_bind_address=('localhost', 5432)
    )
    server.start()
    #connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host='192.168.1.14', port="5432")

    connect = psycopg2.connect(database="db_admin", user="postgres",
                               password="1", host='localhost', port=server.local_bind_port)
    cursor = connect.cursor()
    sql_requset = f"select ip from t_kassa where trade_point = {tradepoint} and cash_box = {cash_box};"
    cursor.execute(sql_requset)
    result = cursor.fetchone()

    server.stop()

    return result[0]


def _generate_report(input_data):
    data = StringIO()
    w = csv.writer(data, delimiter=';')
    w.writerow(('РК', 'Каса', 'Касир', 'Дія', 'Артикул', 'Товар', 'Кількість', 'Вартість',
               'Ціна', 'Номер чеку', 'Час пробивання', 'Знижка', 'Оплата готівкою', 'Оплата картою'))
    yield data.getvalue()
    data.seek(0)
    data.truncate(0)

    for item in input_data:
        w.writerow([item["id_shop"], item["id_workplace"], item["id_user"], item["id_action"], item["article"], item["name"], item["quantity"],
                   item["price_sale"], item["price"], item["check_number"], item["date"], item["discount"], item["pay_cash"], item["pay_card"]])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
