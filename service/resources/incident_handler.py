import requests
from sqlalchemy import  String
from models.db_model import Incedent, Shops, Phones
from rest.init_db import db
from datetime import datetime
from dateutil import tz
from views.logger import get_logger

class IncidentHandler():
    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger(__name__)

    def get_incedents(self):
        alerts = requests.get('http://192.168.1.200:9093/api/v2/alerts?filter=job=~%22routers%22').json()
        active_alerts = Incedent.query.filter(Incedent.type == 1, Incedent.active == True).all()
        fingerprints = []
        fingerprints_maneger = []
        for tmp_alert in active_alerts:
            if tmp_alert.add_info != None:
                #print(tmp_alert)
                fingerprints.append(tmp_alert.add_info["fingerprint"])
        for alert in alerts:
            self.logger.debug(alert)
            incedent = Incedent()
            id_shop = Shops.query.filter(Shops.shop_number==alert["labels"]["id_shop"]).one()
            phones = Phones.query.filter(Phones.shop == id_shop).first()
            datetime_object = datetime.strptime(alert["startsAt"], '%Y-%m-%dT%H:%M:%S.%fZ')
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('Europe/Kiev')
            utc = datetime_object.replace(tzinfo=from_zone)
            ok_zone = utc.astimezone(to_zone)
            incedent.add_info = {"fingerprint": alert["fingerprint"], "summary": alert["annotations"]["summary"], "phones": phones.numbers_list, "CallInProgress": '', "CallStatus": 0, "LastCallDateTime": ""}
            incedent.id_shop = id_shop.id
            incedent.type = 1
            incedent.active = True
            incedent.time_start = ok_zone
            incedent.user = 'admin@lvivkholod.com'
            incedent.id_problem = 2
            incedent.result = ''
            if alert["fingerprint"] not in fingerprints:
                db.session.add(incedent)
                db.session.commit()
            fingerprints_maneger.append(alert["fingerprint"])
        #print(fingerprints)
        for fingerp in fingerprints:
            if fingerp not in fingerprints_maneger:
                set_not_active = Incedent.query.filter(Incedent.add_info["fingerprint"].astext.cast(String)==str(fingerp)).order_by(Incedent.id.desc()).first()
                set_not_active.active = False
                set_not_active.time_finish = datetime.now()
                print("Wait commit state false", set_not_active)
                db.session.commit()
    