from flask_restful import Resource
from flask import request, Response, current_app
from flask_restful import reqparse, inputs
from rest.init_db import db
from models.tiket_model import create_help_desk_tiket
from models.db_model import Incedent, Incedent_schema, Problem, Problem_schema, Phones, Shops, Shops_schema
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
from sqlalchemy.sql.expression import any_
from sqlalchemy.orm.exc import NoResultFound
from utils.ldap_util import LdapUtils
import time
import json
from flask_sse import sse
from datetime import datetime, timedelta
from utils.tasks import my_background_task


class IncedentList(Resource):
    """Api for CRUD operations for colection of shops"""
    args_schema = {
        'active': fields.Bool(required=False),
        'support': fields.Bool(required=False),
        'id_shop': fields.Int(required=False)
    }

    @use_args(args_schema, location="query")
    def get(self, args):
        """Get list shops"""
        #args = arg_parser.parse_args(strict=True)
        #args = request.args
        if 'support' in args and 'id_shop' in args:
            incedent = Incedent.query.filter(
                Incedent.type == 0, Incedent.id_shop == args['id_shop']).order_by(Incedent.id.desc()).all()
        else:
            incedent = Incedent.query.filter(
                Incedent.type == 0).order_by(Incedent.id.desc()).all()
        res = Incedent_schema().dump(incedent, many=True)
        return res, 200

    def post(self):
        """Get list shops"""
        json_data = request.get_json(force=True)
        res = Incedent_schema().load(json_data)
        db.session.add(res)
        db.session.commit()
        db.session.refresh(res)
        if res.active == False:
            print(res, "send to hd")
            job = current_app.queue.enqueue(my_background_task, incedent=res)
            #create_help_desk_tiket(res)
        item_json = Incedent_schema().dump(res)
        return item_json, 200


    def patch(self):
    
        json_data = request.get_json(force=True)
        #print(json_data)
        
        if 'add_info' in json_data:
            add_info = json_data['add_info']
            json_data.pop('add_info')
            res = Incedent_schema().load(json_data)
            db.session.add(res)
            db.session.commit()
            db.session.refresh(res)
            existing_json_data = res.add_info or {}
            existing_json_data.update(add_info)
            res.add_info = existing_json_data
        else:
            res = Incedent_schema().load(json_data)

        db.session.add(res)
        db.session.commit()
        db.session.refresh(res)
        item_json = Incedent_schema().dump(res)
        return item_json, 200


class AsteriskIncedents(Resource):
    def get(self, type):
        """Get list shops"""
        if type == 'all':
            incedent = Incedent.query.filter(Incedent.type == 1, Incedent.active == True, Incedent.id_problem != 1000, Incedent.id_problem != 1001, Incedent.id_problem != -1).order_by(Incedent.id.desc()).all()
        if type == 'electric':
            incedent = Incedent.query.filter(Incedent.type == 1, Incedent.active == True, Incedent.id_problem == 1000, Incedent.id_problem != -1, (datetime.now() - Incedent.time_start) >= timedelta(hours=3)).order_by(Incedent.id.desc()).all()
        if type == 'regulatory':
            incedent = Incedent.query.filter(Incedent.type == 1, Incedent.active == True, Incedent.id_problem == 1001, Incedent.id_problem != -1, (datetime.now() - Incedent.time_start) >= timedelta(hours=3)).order_by(Incedent.id.desc()).all()
        for i in incedent:
            print((datetime.now() - i.time_start))
        res = Incedent_schema().dump(incedent, many=True)
        return res, 200


class ProblemsList(Resource):
    """Api for CRUD operations for colection of shops"""

    def get(self):
        """Get list shops"""
        problems = Problem.query.all()
        res = Problem_schema().dump(problems, many=True)
        return res, 200

    def post(self):
        """Get list shops"""
        json_data = request.get_json(force=True)
        res = Problem_schema().load(json_data)
        print(res)
        db.session.add(res)
        db.session.commit()
        db.session.refresh(res)
        item_json = Problem_schema().dump(res)
        problems = Problem.query.all()
        res = Problem_schema().dump(problems, many=True)
        return res, 200


class IncedentAnnouncer(Resource):
    def get(self):
        return sse.stream()

    def post(self):
        type_incedents = {
            '11': "каси",
            '12': "мережа",
            '13': "ваги",
            '14': "інша"
        }
        # Process the POST request
        data = request.get_json()
        print(data)
        mock_ldap = LdapUtils()
        user = mock_ldap.get_email_by_sip(data['sipid'])
        print("_______" + user + "_______")
        incedent = Incedent()

        try:
            phone = Phones.query.filter(
                Phones.numbers_list.any(data['callerid'])).one()
            incedent.id_shop = phone.shop.id
        except NoResultFound:
            incedent.id_shop = 0

        incedent.user = user
        if data['dst'] in type_incedents:
            incedent.add_info = {
                "type_incedent_from_line": type_incedents[data['dst']], "callerid": data['callerid']}
        else:
             incedent.add_info = {
                "type_incedent_from_line": 'інша (не вибрали проблему)', "callerid": data['callerid']}
        incedent.time_start = datetime.now()
        incedent.type = 0
        incedent.id_problem = 0
        incedent.result = ''
        incedent.active = True
        db.session.add(incedent)
        db.session.commit()
        db.session.refresh(incedent)
        # Emit SSE event
        sse.publish({"callerid": data['callerid'], "user": user,
                    "dst": data['dst'], "id_incedent": incedent.id})

        # Return the response
        # ...

        return {"message": "POST request processed"}
