#!/usr/bin/env python

'''
Example custom dynamic inventory script for Ansible, in Python.
'''
import yaml
import requests
import os
import sys
import argparse
import json
from yaml import SafeDumper


class ExampleInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()
        #self.get_json()
        self.get_json_router("admin", "vldh_mikrotik")
        # Called with `--list`.
        if self.args.list:
            self.inventory = self.example_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        # print(json.dumps(self.inventory))

    # Example inventory for testing.
    def example_inventory(self):
        return {
            'group': {
                'hosts': ['192.168.28.71', '192.168.28.72'],
                'vars': {
                    'ansible_ssh_user': 'vagrant',
                    'ansible_ssh_private_key_file':
                        '~/.vagrant.d/insecure_private_key',
                    'example_variable': 'value'
                }
            },
            '_meta': {
                'hostvars': {
                    '192.168.28.71': {
                        'host_specific_var': 'foo'
                    },
                    '192.168.28.72': {
                        'host_specific_var': 'bar'
                    }
                }
            }
        }

    def get_json_pos(self):
        SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
        )
        params = {"itemtype": "pos"}
        json_response = requests.get(
            f'http://192.168.1.14:8888/api/items', params=params).json()
        list_shops = []
        list_shop_dict = {}
        for item in json_response:
            shop = item['shop']['shop_number']
            list_shops.append(shop)
        list_shop_dict["all_shops"] = {"children":{}}
        list_shop_dict["is_prro"] = {"hosts":{}}
        for shop in set(list_shops):
            poss_json = list(filter(lambda x: x['shop']['shop_number'] == shop, json_response))
            list_shop_dict[f"shop_{shop}"] = {"hosts":{}}
            list_shop_dict["all_shops"]["children"][f"shop_{shop}"] = None
            for item in poss_json:
                id_workplace = None
                host = item['host']
                ssh_pass = None
                ssh_user = None
                item_res = {}
                is_prro = None
                for att in item['attributes']:
                    if att['id_attribute'] == 3:
                        id_workplace = att['value']
                    if att['id_attribute'] == 8:
                        ssh_pass = att['value']
                    if att['id_attribute'] == 9:
                        ssh_user = att['value']
                    if att['id_attribute'] == 4:
                        if att['value'] == '1':
                            is_prro = True
                        else: 
                            is_prro = False
                if is_prro:
                    list_shop_dict["is_prro"]["hosts"][f"pos{shop}_{id_workplace}"] = None
                list_shop_dict[f"shop_{shop}"]["hosts"][f"pos{shop}_{id_workplace}"] = {
                    "ansible_host": host,
                    "ansible_user": "rootadmin",
                    "ansible_ssh_pass": "Gfhfcjkmrf@0",
                    "ansible_become_pass": "Gfhfcjkmrf@0"
                }
        print(yaml.safe_dump(list_shop_dict, default_flow_style=False))

    def get_json_router(self, login, passw):
        SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
        )
        params = {"itemtype": "router"}
        json_response = requests.get(
            f'http://192.168.1.14:8888/api/items', params=params).json()
        list_shops = []
        list_shop_dict = {}
        for item in json_response:
            shop = item['shop']['shop_number']
            list_shops.append(shop)
        list_shop_dict["all_shops"] = {"children":{}}
        #list_shop_dict["is_prro"] = {"hosts":{}}
        for shop in set(list_shops):
            poss_json = list(filter(lambda x: x['shop']['shop_number'] == shop, json_response))
            list_shop_dict[f"shop_{shop}"] = {"hosts":{}}
            list_shop_dict["all_shops"]["children"][f"shop_{shop}"] = None
            for item in poss_json:
                host = item['host']
                for att in item['attributes']:
                    if att['id_attribute'] == 3:
                        id_workplace = att['value']
                    if att['id_attribute'] == 8:
                        ssh_pass = att['value']
                    if att['id_attribute'] == 9:
                        ssh_user = att['value']
                    if att['id_attribute'] == 4:
                        if att['value'] == '1':
                            is_prro = True
                        else: 
                            is_prro = False
                list_shop_dict[f"shop_{shop}"]["hosts"][f"router_{shop}"] = {
                    "ansible_host": host,
                    "ansible_user": login,
                    "ansible_ssh_pass": passw,
                    "ansible_become_pass": passw
                }
        print(yaml.safe_dump(list_shop_dict, default_flow_style=False))


    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()


# Get the inventory.
ExampleInventory()
