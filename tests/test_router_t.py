from traceback import print_tb
import requests

params = {"itemtype": "provider-router"}
json_response = requests.get(f'http://192.168.1.14:8888/api/items', params=params).json()  
q = []
#print(res)
for item in json_response:
    provider = None
    for att in item['attributes']:
                if att['id_attribute'] == 20:
                    provider = att['value']
    labels = {
                'id_shop': item['shop']['shop_number'],
                'shop_name': item['shop']['name'],
                #"target": f"192.168.{item['shop']['base_ip']}.100",
                "provider": provider
    }
    targets = [ f"192.168.{item['shop']['base_ip']}.100"]
    q.append({'labels': labels, 'targets': targets})
    #q.append({'labels': labels})

print(q)