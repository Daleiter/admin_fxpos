from keyword import kwlist
import os
import re
from unittest import result
import requests
import psycopg2
#from views.cache import cache
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify


PORT=os.environ.get('REST_SRV_PORT')
inventory_shop = Blueprint('inventory_shop', __name__)

@inventory_shop.route('/inventory', methods=['GET'])
def get_inventory():
    data_for_template = _get_inventory_from_db()
    print(data_for_template)        
    return render_template('inventory_shops.html', data_for_template=data_for_template)

@inventory_shop.route('/inventory/shop/<id>', methods=['GET'])
def get_item(id):
    return jsonify(_get_item_from_db(id))

@inventory_shop.route('/inventory/shop', methods=['GET'])
def get_shop():
    return render_template('form_shop.html')

@inventory_shop.route('/inventory/item/<id>', methods=['POST'])
def update_item(id):
    request_data = request.get_json()
    _update_item(id, request_data)
    return jsonify(_get_item_from_db(id))


@inventory_shop.route('/inventory/wiki-list', methods=['GET'])
#@cache.cached(timeout=43200)
def get_wiki_list_shops():
    prro = request.args.get('prro')
    shops = requests.get(f'http://localhost:8888/api/shops').json()
    #shops = [
    #    {"shop_number": 515},
    #    {"shop_number": 597},
    #    {"shop_number": 712},
    #    {"shop_number": 466}
    #]
    data = []
    remote_con_len = 0
    for i_shop in shops:
        res = requests.get(f'http://localhost:8888/api/items', params=f'shop_number={i_shop["shop_number"]}').json()
        phones = requests.get(f'http://localhost:8888/api/shops/phones/{i_shop["shop_number"]}').json()
       
        shop = {
            "shop_number": res[0]["shop"]["shop_number"],
            "is_have_prro": False,
            "is_cashdesk": False,
            "shop_name": res[0]["shop"]["name"],
            "ip": res[0]["shop"]["base_ip"],
            "pos": [],
            "pc": [],
            "phones": phones["numbers_list"],
            "router": "",
            "provider": {
                "name": "",
                "host": ""
            }
        }
        pos_json = list(filter(lambda x: x["id_type"] == 1, res))
        pc_json = list(filter(lambda x: x["id_type"] == 4, res))
        router_json = list(filter(lambda x: x["id_type"] == 6, res))
        provider_json = list(filter(lambda x: x["id_type"] == 9, res))
        for i in pos_json:

            link_ssh = list(filter(lambda x: x["id_attribute"] == 21, i["attributes"]))
            link_vnc = list(filter(lambda x: x["id_attribute"] == 22, i["attributes"]))
            is_prro = list(filter(lambda x: x["id_attribute"] == 4, i["attributes"]))
            is_cashdesk = list(filter(lambda x: x["id_attribute"] == 26, i["attributes"]))
            if link_ssh:
                link_ssh = link_ssh[0]["value"]
            else:
                link_ssh = "Poshel_na_hyi"
            if link_vnc:
                link_vnc = link_vnc[0]["value"]
            else:
                link_vnc = "Poshel_na_hyi"

            if is_prro:
                is_prro = bool(int(is_prro[0]["value"]))
                if not shop["is_have_prro"]:
                    shop["is_have_prro"] = is_prro
            else:
                is_prro = False
            if is_cashdesk:
                is_cashdesk = bool(int(is_cashdesk[0]["value"]))
                if not shop["is_cashdesk"]:
                    shop["is_cashdesk"] = is_cashdesk
            else:
                is_prro = False
            tmp = {
                "host": i["host"],
                "vnc_code": link_vnc,
                "ssh_code": link_ssh,
                "is_prro": is_prro
            }
            shop["pos"].append(tmp)
        
        for i in pc_json:
            link_vnc = list(filter(lambda x: x["id_attribute"] == 25, i["attributes"]))
            if link_vnc:
                link_vnc = link_vnc[0]["value"]
            tmp = {
                "host": i["host"],
                "vnc_code": link_vnc
            }
            shop["pc"].append(tmp)
        if len(shop["pc"]) + len(shop["pos"]) > remote_con_len:
            remote_con_len = len(shop["pc"]) + len(shop["pos"])
        if router_json:
            shop["router"] = router_json[0]["host"]
        else:
            shop["router"] = "Stas chort ;)"
        print(provider_json)
        print(shop["is_cashdesk"], shop["shop_name"])
        if provider_json:
            provider_name = list(filter(lambda x: x["id_attribute"] == 20, provider_json[0]["attributes"]))
            print(provider_name)
            if provider_name:
                provider_name = provider_name[0]["value"]
            else:
                provider_name = ""
            shop["provider"]["name"] = provider_name
            shop["provider"]["host"] = provider_json[0]["host"]
        else:
            shop["provider"]["name"] = "Stas chort ;)"
            shop["provider"]["host"] = "Stas chort ;)"
        data.append(shop)
    if prro == "yes":
        prro = True
    else:
        prro = False
    return render_template('wiki-shops.html', data=data, remote_con_len=remote_con_len, prro=prro)

@inventory_shop.route('/inventory/wiki-list/prro', methods=['GET'])
#@cache.cached(timeout=600)
def get_wiki_list_shops_prro():
    shops = requests.get(f'http://localhost:8888/api/shops').json()
    #shops = [
    #    {"shop_number": 515},
    #    {"shop_number": 597},
    #    {"shop_number": 466},
    #    {"shop_number": 712},
    #]
    data = []
    remote_con_len = 0
    for i_shop in shops:
        res = requests.get(f'http://localhost:8888/api/items', params=f'shop_number={i_shop["shop_number"]}').json()
        phones = requests.get(f'http://localhost:8888/api/shops/phones/{i_shop["shop_number"]}').json()
       
        shop = {
            "shop_number": res[0]["shop"]["shop_number"],
            "is_have_prro": False,
            "shop_name": res[0]["shop"]["name"],
            "ip": res[0]["shop"]["base_ip"],
            "pos": [],
            "pc": [],
            "phones": phones["numbers_list"],
            "router": "",
            "provider": {
                "name": "",
                "host": ""
            }
        }
        pos_json = list(filter(lambda x: x["id_type"] == 1, res))
        pc_json = list(filter(lambda x: x["id_type"] == 4, res))
        router_json = list(filter(lambda x: x["id_type"] == 6, res))
        provider_json = list(filter(lambda x: x["id_type"] == 9, res))
        for i in pos_json:

            link_ssh = list(filter(lambda x: x["id_attribute"] == 21, i["attributes"]))
            link_vnc = list(filter(lambda x: x["id_attribute"] == 22, i["attributes"]))
            is_prro = list(filter(lambda x: x["id_attribute"] == 4, i["attributes"]))
            if link_ssh:
                link_ssh = link_ssh[0]["value"]
            else:
                link_ssh = "Poshel_na_hyi"
            if link_vnc:
                link_vnc = link_vnc[0]["value"]
            else:
                link_vnc = "Poshel_na_hyi"

            if is_prro:
                is_prro = bool(int(is_prro[0]["value"]))
                if not shop["is_have_prro"]:
                    shop["is_have_prro"] = is_prro
            else:
                is_prro = False
            tmp = {
                "host": i["host"],
                "vnc_code": link_vnc,
                "ssh_code": link_ssh,
                "is_prro": is_prro
            }
            shop["pos"].append(tmp)
        
        for i in pc_json:
            link_vnc = list(filter(lambda x: x["id_attribute"] == 25, i["attributes"]))
            if link_vnc:
                link_vnc = link_vnc[0]["value"]
            tmp = {
                "host": i["host"],
                "vnc_code": link_vnc
            }
            shop["pc"].append(tmp)
        if len(shop["pc"]) + len(shop["pos"]) > remote_con_len:
            remote_con_len = len(shop["pc"]) + len(shop["pos"])
        if router_json:
            shop["router"] = router_json[0]["host"]
        else:
            shop["router"] = "Stas chort ;)"

        if provider_json:
            provider_name = list(filter(lambda x: x["id_attribute"] == 20, provider_json[0]["attributes"]))

            if provider_name:
                provider_name = provider_name[0]["value"]
            else:
                provider_name = ""
            shop["provider"]["name"] = provider_name
            shop["provider"]["host"] = provider_json[0]["host"]
        else:
            shop["provider"]["name"] = "Stas chort ;)"
            shop["provider"]["host"] = "Stas chort ;)"
        data.append(shop)
    
    prro = True
    return render_template('wiki-shop-prro-pusk.html', data=data, remote_con_len=remote_con_len, prro=prro)

def _update_item(id, data):
    for key in data:
        if key == "active":
            print(id, data['active'])
            sql_request = f"UPDATE inventory.items SET active = {data['active']} WHERE id = {id}"
            connect = psycopg2.connect(database="db_inventory", user="postgres", password="inventory_atadgp", host='192.168.1.15', port="5432")
            cursor = connect.cursor()
            cursor.execute(sql_request)
            connect.commit()
            cursor.close()



def _get_inventory_from_db():
    sql_request = """
SELECT
	inventory.shops.base_ip, 
	inventory.shops.shop_number, 
	inventory.shops."name", 
	inventory.shops."id"
FROM
	inventory.shops
WHERE
	inventory.shops.active = true
ORDER BY
	base_ip ASC;
    """
    connect = psycopg2.connect(database="db_inventory", user="postgres", password="inventory_atadgp", host='192.168.1.15', port="5432")
    cursor = connect.cursor()
    cursor.execute(sql_request)
    result_query = cursor.fetchall()
    result = []
    for shop in result_query:
        shop_dict = {
            "base_ip": shop[0],
            "shop_number": shop[1],
            "name": shop[2],
            "id": shop[3]
        }
        result.append(shop_dict)
    connect.close()
    return result

def _get_item_from_db(id_item):
    sql_request = f"""
SELECT
    inventory.items."id",
	inventory.shops.shop_number, 
	inventory.items."host", 
	inventory.shops."name", 
	inventory.item_attributes."value" as "id_workplace", 
	inventory.item_types."name" as "type",
	inventory.items.active
FROM
	inventory.items
	INNER JOIN
	inventory.shops
	ON 
		inventory.items.id_shop = inventory.shops."id"
	INNER JOIN
	inventory.item_types
	ON 
		inventory.items.id_type = inventory.item_types.id_type
	INNER JOIN
	inventory.item_attributes
	ON 
		inventory.items."id" = inventory.item_attributes.id_item
WHERE
	inventory.shops."id" = {id_item} AND
	inventory.item_attributes.id_attribute = 3
ORDER BY
	inventory.item_attributes."value" ASC
    """
    connect = psycopg2.connect(database="db_inventory", user="postgres", password="inventory_atadgp", host='192.168.1.15', port="5432")
    cursor = connect.cursor()
    cursor.execute(sql_request)
    db_result = cursor.fetchall()
    result = []
    for item in db_result:
        item_dict = {
            "id_item": item[0],
            "id_shop": item[1],
            "host": item[2],
            "shop_name": item[3],
            "id_workplace": item[4],
            "type_name": item[5],
            "active": item[6]
        }
        result.append(item_dict)
    connect.close()
    return result