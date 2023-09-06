from cProfile import label
from nis import match
import requests
from flask_restful import Resource, marshal_with, marshal
from flask_restful import reqparse
from sqlalchemy import case
from models.db_model import Items, Item_types, Items_schema
from rest.init_db import db
from service.resources.models_stucture import pos_targets_structure, printer_targets_structure, router_targets_structure, raspberry_targets_structure


class Pos_targets(Resource):
    """Api for CRUD operations for colection of targets"""

    def get(self, type):
        """Get list targets"""

        if type == 'printer':
            id_type = Item_types.query.filter(Item_types.type=='printer').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_pos(res)
            return marshal(result, printer_targets_structure), 200

        elif type == 'pos':
            id_type = Item_types.query.filter(Item_types.type=='pos').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_pos(res)
            return marshal(result, pos_targets_structure), 200

        elif type == 'rro':
            id_type = Item_types.query.filter(Item_types.type=='pos').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_rro(res)
            return marshal(result, pos_targets_structure), 200
        
        elif type == 'dmvchasno':
            id_type = Item_types.query.filter(Item_types.type=='pos').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_dm_vchasno(res)
            return marshal(result, pos_targets_structure), 200
        
        elif type == 'routers':
            id_type = Item_types.query.filter(Item_types.type=='provider-router').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_router(res)
            return marshal(result, router_targets_structure), 200

        elif type == 'routers-provider':
            id_type = Item_types.query.filter(Item_types.type=='provider-router').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_provider(res)
            return marshal(result, router_targets_structure), 200
        
        elif type == 'raspberry':
            id_type = Item_types.query.filter(Item_types.type=='music-box').one()
            q = Items.query.filter(Items.id_type==id_type.id_type, Items.active==True).all()
            res = Items_schema().dump(q, many=True)
            result = _get_json_pos(res)
            return marshal(result, raspberry_targets_structure), 200

        return 404

def _get_json_pos(json_response):
        q = []
        for item in json_response:
            id_pos = "None"
            is_prro = "None"
            for att in item['attributes']:
                if att['id_attribute'] == 3:
                    id_pos = att['value']
                if att['id_attribute'] == 4:
                    if att['value'] == '0':
                        is_prro = 'false'
                    else:
                        is_prro = 'true'

            labels = {
                'id_pos': id_pos,
                'id_shop': item['shop']['shop_number'],
                'is_prro': is_prro,
                'shop_name': item['shop']['name']
            }
            targets = [item['host']]
            q.append({'labels': labels, 'targets': targets})
        return q

def _get_json_dm_vchasno(json_response):
        q = []
        for item in json_response:
            id_pos = "None"
            is_prro = "None"
            for att in item['attributes']:
                if att['id_attribute'] == 3:
                    id_pos = att['value']
                if att['id_attribute'] == 4:
                    if att['value'] == '0':
                        is_prro = 'false'
                    else:
                        is_prro = 'true'
            if is_prro == 'true':
                labels = {
                    'id_pos': id_pos,
                    'id_shop': item['shop']['shop_number'],
                    'is_prro': is_prro,
                    'shop_name': item['shop']['name']
                }
                targets = [f"http://{item['host']}:3939/dm/vchasno-kasa/api/v1/dashboard"]
                q.append({'labels': labels, 'targets': targets})
        return q

def _get_json_rro(json_response):
        q = []
        for item in json_response:
            id_pos = "None"
            is_prro = "None"
            for att in item['attributes']:
                if att['id_attribute'] == 3:
                    id_pos = att['value']
                if att['id_attribute'] == 4:
                    if att['value'] == '0':
                        is_prro = 'false'
                    else:
                        is_prro = 'true'

            labels = {
                'id_pos': id_pos,
                'id_shop': item['shop']['shop_number'],
                'is_prro': is_prro,
                'shop_name': item['shop']['name']
            }
            targets = [ f"192.168.{item['shop']['base_ip']}.20{id_pos}"]
            #if not labels['is_prro']:
            q.append({'labels': labels, 'targets': targets})
        return q

def _get_json_router(json_response):
    q = []
    for item in json_response:
        provider = None
        for att in item['attributes']:
                    if att['id_attribute'] == 20:
                        provider = att['value']
        labels = {
                    'id_shop': item['shop']['shop_number'],
                    'shop_name': item['shop']['name'],
                    "provider": provider
        }
        targets = [ f"192.168.{item['shop']['base_ip']}.100"]
        if item['shop']['active']:
           q.append({'labels': labels, 'targets': targets})
    return q


def _get_json_raspberry(json_response):
    q = []
    for item in json_response:

        labels = {
                    'id_shop': item['shop']['shop_number'],
                    'shop_name': item['shop']['name']
        }
        targets = [ f"192.168.{item['shop']['base_ip']}.49"]
        if item['shop']['active']:
           q.append({'labels': labels, 'targets': targets})
    return q

def _get_json_provider(json_response):
    q = []
    for item in json_response:
        provider = None
        for att in item['attributes']:
                    if att['id_attribute'] == 20:
                        provider = att['value']
        labels = {
                    'id_shop': item['shop']['shop_number'],
                    'shop_name': item['shop']['name'],
                    "provider": provider
        }
        targets = [ item["host"] ]
        if item['shop']['active']:
           q.append({'labels': labels, 'targets': targets})
    return q