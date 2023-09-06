import os
import requests
import csv
from io import StringIO
from datetime import datetime
from werkzeug.wrappers import Response
from flask import Blueprint, render_template, request, redirect, url_for, flash


PORT=os.environ.get('REST_SRV_PORT')
silences_blueprint = Blueprint('silences_blueprint', __name__)

@silences_blueprint.route('/silences', methods=['GET'])
def get_silences():
    silences = requests.get('http://192.168.1.200:9093/api/v2/silences?silenced=false&inhibited=false&active=true').json()
    data_for_template = {"metric" : [], "value" : []}
    #for a in silences:
    #    print(a["comment"])
    #    for d in a:
    #        print(f"{d['name']}, {d['value']}")
    print(data_for_template)
    #return render_template('pos_dashboard.html', data_for_template=data_for_template, zip=zip)
    return render_template('silences.html', data=silences, datetime=datetime)

@silences_blueprint.route('/silences/report/get', methods=['GET'])
def get_report():
    silences = requests.get('http://192.168.1.200:9093/api/v2/silences?silenced=false&inhibited=false&active=true').json()
    # stream the response as the data is generated
    response = Response(_generate_report(silences), mimetype='text/csv')
    # add a filename
    response.headers.set("Content-Disposition", "attachment", filename="problems-report.csv")
    return response

def _generate_report(input_data):
    data = StringIO()
    w = csv.writer(data)

    # write header
    w.writerow(('Назва магазину', 'Номер магазину', 'Номер каси', 'Адресса каси', 'Коментар', 'Створив', 'Початок проблеми', 'Очікувана дата закінчення', 'Тип проблеми'))
    yield data.getvalue()
    data.seek(0)
    data.truncate(0)

    # write each log item
    for item in input_data:
        shop_name = ''
        id_shop = ''
        id_pos = ''
        instance = ''
        alertname = ''

        for match in item["matchers"]:
            if match["name"] == "shop_name":
                shop_name = match["value"]

            if match["name"] == "id_shop":
                id_shop = match["value"]

            if match["name"] == "id_pos":
                id_pos = match["value"]

            if match["name"] == "instance":
                instance = match["value"]

            if match["name"] == "alertname":
                alertname = match["value"]
   
        w.writerow((
            shop_name,
            id_shop,
            id_pos,
            instance,
            item["comment"],
            item["createdBy"],
            datetime.strptime(item["startsAt"] , '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%m/%d/%Y, %H:%M:%S"),
            datetime.strptime(item["endsAt"] , '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%m/%d/%Y, %H:%M:%S"),
            alertname
            #item[0],
            #item[1].isoformat()  # format datetime as string

        ))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)