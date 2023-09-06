import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash


PORT=os.environ.get('REST_SRV_PORT')
pos_dashboard = Blueprint('pos_dashboard', __name__)

@pos_dashboard.route('/dashboard', methods=['GET'])
def get_dashboard():
    promql_res = requests.get('http://192.168.1.200:9090/api/v1/query?query=probe_success{job="pos"}').json()
    #print(promql_res)
    data_for_template = {"metric" : [], "value" : []}
    #http://192.168.1.200:9090/api/v1/query?query=probe_success{job="pos"}
    for i in promql_res["data"]["result"]:
        data_for_template["metric"].append(i["metric"])
        data_for_template["value"].append(i["value"][1])
    print(data_for_template)
    return render_template('pos_dashboard.html', data_for_template=data_for_template, zip=zip)