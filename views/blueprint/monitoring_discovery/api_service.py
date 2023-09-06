import os
import requests
import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, json, jsonify


PORT=os.environ.get('REST_SRV_PORT')
monitoring_api_service = Blueprint('monitoring_api_service', __name__)

@monitoring_api_service.route('/api/discovery/monitoring/<taget_type>', methods=['GET'])
def get_sd_config_by_type(taget_type):
    return jsonify(_get_targets_by_type(taget_type))


def _get_targets_by_type(taget_type):
    sql_request = f"""
SELECT
	inventory.items."id", 
	inventory.items."host", 
	inventory.shops.shop_number, 
	inventory.shops."name"
FROM
	inventory.items
	INNER JOIN
	inventory.item_types
	ON 
		inventory.items.id_type = inventory.item_types.id_type
	INNER JOIN
	inventory.shops
	ON 
		inventory.items.id_shop = inventory.shops."id"
WHERE
	inventory.items.active = TRUE AND
	inventory.item_types.id_type = {taget_type};
    """

    connect = psycopg2.connect(database="db_inventory", user="postgres", password="inventory_atadgp", host='192.168.1.15', port="5432")
    cursor = connect.cursor()
    cursor.execute(sql_request)
    result_query = cursor.fetchall()
    result = []
    for id_item in result_query:
        sql_request_0 = f"""
SELECT
    inventory.items.id,
	inventory.attibute_types.attribute_name, 
	inventory.item_attributes."value"
FROM
	inventory.items
	INNER JOIN
	inventory.item_attributes
	ON 
		inventory.items."id" = inventory.item_attributes.id_item
	INNER JOIN
	inventory.attibute_types
	ON 
		inventory.item_attributes.id_attribute = inventory.attibute_types.id_attiribute
		
	WHERE inventory.items."id" = {id_item[0]} and inventory.item_attributes.id_attribute in (3,4);
    """
        cursor.execute(sql_request_0)
        result_query = cursor.fetchall()
        if result_query[1][2] == '1':
            is_prro = True
        else:
            is_prro = False
        target = {
            "targets": [id_item[1]],
            "labels": {
                "id_pos": result_query[0][2],
                "id_shop": str(id_item[2]),
                "is_prro": str(is_prro).lower(),
                "shop_name": id_item[3]
                }
        }
        result.append(target)      
    connect.close()
    return result
