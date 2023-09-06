import sys
import os
import psycopg2
from psycopg2 import OperationalError
from threading import Thread


class Get_sum:

    def __init__(self, report_date):
        self.report_date = report_date
   
    def run(self):
        pos_info = self.get_ips()
        ips = [r[2] for r in pos_info]
        threads = [None] * len(ips)
        results = [None] * len(ips)

        for i in range(len(threads)):
            threads[i] = Thread(target=self.get_sum, args=(self.report_date ,ips, results, i))
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

        non_count = 0
        all_result = 0
        not_sync = 0
        sum_none = 0
        dpos_sums = self.get_dpos_pos_sum(self.report_date)
        p_ip = ''
        json_result = []
        for i in range(len(ips)):
            if (pos_info[i][0], pos_info[i][1]) in dpos_sums:
                dpos_sum = dpos_sums[(pos_info[i][0], pos_info[i][1])]
            else:
                dpos_sum = 0

            
            if float(results[i]) < 0:
                connected = False
                results[i] = 0
            else:
                connected = True

            if float(results[i]) != dpos_sum:
                equals = False
            else:
                equals = True

            json_result.append({"address" : ips[i],
            "id_shop" : pos_info[i][0],
            "sum" : float(results[i]),
            "sum_dpos" : dpos_sum,
            "equals" : equals,
            "connected": connected}
            )

        return json_result
        print(json_result)

    def get_ips(self):
      connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host='127.0.0.1', port="5432")
      cursor = connect.cursor()
      sql_requset = f"SELECT trade_point, cash_box, ip from  t_kassa;"
      cursor.execute(sql_requset)
      result = cursor.fetchall()
      return result

    def get_dpos_pos_sum(self, date):
      connect = psycopg2.connect(database="db_server", user="postgres", password="", host='192.168.1.139', port="5432", connect_timeout=5)
      cursor = connect.cursor()
      sql_requset = f"SELECT id_shop, id_workplace, sum(sum) from  pos.t_check WHERE date_operation = '{date}' and dtype = 0 GROUP BY id_shop, id_workplace;"
      cursor.execute(sql_requset)
      tuples_sum = cursor.fetchall()
      sum_dict = dict(((shop, pos), float(sum)) for shop, pos, sum in tuples_sum)
      return sum_dict


    def get_sum_dpos(self, date):
      connect = psycopg2.connect(database="db_server", user="postgres", password="", host='192.168.1.139', port="5432", connect_timeout=5)
      cursor = connect.cursor()
      sql_requset = f"SELECT sum(sum) FROM pos.t_check WHERE date_operation = '{date}' and dtype = 0;"
      cursor.execute(sql_requset)
      result = cursor.fetchone()
      return float(result[0])
       

    def get_sum(self, date, ip, result_all, index):
      try:
        connect = psycopg2.connect(database="db_client", user="postgres", password="", host=str(ip[index]), port="5432", connect_timeout=5)
        cursor = connect.cursor()
        sql_requset = f"SELECT sum(sum) FROM pos.t_check WHERE date_operation = '{date}' and dtype = 0;"
        cursor.execute(sql_requset)
        result = cursor.fetchone()
        if result[0] == None:
          result_all[index] = 0
        else:
          result_all[index] = result[0]
      except OperationalError as err:
        print(f"Cant connect to {str(ip[index])}")
        result_all[index] = -99999999
    
       


