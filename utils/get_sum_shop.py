import sys
import os
import psycopg2
from psycopg2 import OperationalError
from threading import Thread


class Get_sum_pos:

    def __init__(self, ip_pos, id_shop, id_workplace, date):
        self.DPOS_IP = '192.168.1.139'
        self.ip_pos = ip_pos
        self.id_shop = id_shop
        self.id_workplace = id_workplace
        self.date = date
        self.query_report = f"""
SELECT SUM
	( sum_ready_money + sum_ready_credit ) 
FROM
	pos.t_cash_register_report 
WHERE
	id_shop = '{self.id_shop}' 
	AND id_workplace = '{self.id_workplace}' 
	AND report_time > '{self.date} 00:00:00' 
	AND report_time < '{self.date} 23:59:59';
"""
        self.query_cheks = f"""
        SELECT SUM
	( SUM ) 
FROM
	pos.t_check 
WHERE
	date_operation = '{self.date}' 
	AND id_workplace = '{self.id_workplace}' 
	AND id_shop = '{self.id_shop}' 
	AND dtype = 0;
        """
        self.query_cheks_articles = f"""
        SELECT SUM
	( SUM ) 
FROM
	pos.t_check_articles 
WHERE
	id_check IN ( SELECT id_check FROM pos.t_check WHERE date_operation = '{self.date}' AND id_workplace = '{self.id_workplace}' AND id_shop = '{self.id_shop}' AND dtype = 0 ) 
	AND id_shop = '{self.id_shop}' 
	AND id_workplace = '{self.id_workplace}';
        """

    def get_sum(self):
        result = {
            'info': {
                'id_shop': self.id_shop,
                'id_workplace': self.id_workplace,
                'date': self.date
            },
            'dpos': { 
                'sum_report': self._get_sum_dpos(self.query_report),
                'sum_cheks': self._get_sum_dpos(self.query_cheks),
                'sum_cheks_articles': self._get_sum_dpos(self.query_cheks_articles)
            },
            'pos':{
                'sum_report': self._get_sum_pos(self.query_report),
                'sum_cheks': self._get_sum_pos(self.query_cheks),
                'sum_cheks_articles': self._get_sum_pos(self.query_cheks_articles)
            }
        }

        return result

    def _get_sum_pos(self, sql_requset):
        result = None
        try:
            connect = psycopg2.connect(database="db_client", user="postgres", password="", host=self.ip_pos , port="5432", connect_timeout=5)
            cursor = connect.cursor()
            cursor.execute(sql_requset)
            result = cursor.fetchone()
            connect.close()
        except OperationalError as err:
            print(f"Cant connect to {self.ip_pos}")
            #connect.close()
        if result:
            return result[0]
        return result

    def _get_sum_dpos(self, sql_requset):
        result = None
        try:
            connect = psycopg2.connect(database="db_server", user="postgres", password="", host=self.DPOS_IP , port="5432", connect_timeout=5)
            cursor = connect.cursor()
            cursor.execute(sql_requset)
            result = cursor.fetchone()
            connect.close()
        except OperationalError as err:
            print(f"Cant connect to {self.DPOS_IP}")
            #connect.close()
        if result:
            return result[0]
        return result
           
   