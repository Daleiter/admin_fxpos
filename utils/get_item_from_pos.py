import sys
import os
import psycopg2
from psycopg2 import OperationalError
from threading import Thread


class Get_item_pos:

    def __init__(self, id_shop, barcode=None, article=None):
        self.id_shop = id_shop
        self.barcode = barcode
        self.article = article
   
    def run(self):
        pos_info = self.get_ips(self.id_shop)
        ips = [r[2] for r in pos_info]
        threads = [None] * len(ips)
        results = [None] * len(ips)

        for i in range(len(threads)):
            if self.barcode:
              threads[i] = Thread(target=self.get_by_barcode, args=(self.barcode, ips, results, i))
            if self.article:
              threads[i] = Thread(target=self.get_by_article, args=(self.article, ips, results, i))

            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()
        json_result = []
        for i in range(len(ips)):
          if results[i]:
            item = {
                  "price": float(results[i][0]),
                  "item_name":  results[i][1],
                  "article":  results[i][2],
                  "barcode":  results[i][3],
                  "id_article":  results[i][4],
                  "id_barcode":  results[i][5],
                  "id_shop":  results[i][6],
                  "id_workplace":  pos_info[i][1]
              }
            json_result.append(item)
          else:
            json_result.append({"id_shop": self.id_shop, "id_workplace":  pos_info[i][1], "false": True})
        return json_result

    def get_ips(self, id_shop):
      connect = psycopg2.connect(database="db_inventory", user="postgres", password="inventory_atadgp", host='192.168.1.15', port="5432")
      cursor = connect.cursor()
      sql_requset = f"""
SELECT
	inventory.shops.shop_number,
	inventory.item_attributes."value",
	inventory.items."host" 
FROM
	inventory.items
	INNER JOIN inventory.item_types ON inventory.items.id_type = inventory.item_types.id_type
	INNER JOIN inventory.shops ON inventory.items.id_shop = inventory.shops."id"
	INNER JOIN inventory.item_attributes ON inventory.items."id" = inventory.item_attributes.id_item 
WHERE
	inventory.shops.shop_number = {id_shop} 
	AND inventory.item_types.id_type = 1 
	AND inventory.items.active = TRUE 
	AND inventory.item_attributes.id_attribute = 3
  ORDER BY inventory.item_attributes."value" ASC;"""
      cursor.execute(sql_requset)
      result = cursor.fetchall()
      print(result)
      return result

    def get_by_barcode(self, id_barcode, ip, result_all, index):
      try:
        connect = psycopg2.connect(database="db_client", user="postgres", password="", host=str(ip[index]), port="5432", connect_timeout=5)
        cursor = connect.cursor()
        sql_requset = f"""
            SELECT
    	pos.t_barcode.price[1], 
    	pos.t_article.name, 
    	pos.t_article.article, 
    	pos.t_barcode.barcode, 
    	pos.t_barcode.id_article, 
    	pos.t_barcode.id_barcode, 
    	pos.t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		pos.t_article.id_article = pos.t_barcode.id_article AND
    		pos.t_article.id_shop = pos.t_barcode.id_shop
    WHERE
    	pos.t_barcode.id_barcode = '{id_barcode}';
            """
        cursor.execute(sql_requset)
        result = cursor.fetchone()
        if result == None:
          result_all[index] = 0
        else:
          result_all[index] = result
        connect.close()
      except OperationalError as err:
        print(f"Cant connect to {str(ip[index])}")
        connect.close()
        result_all[index] = None
    
    def get_by_article(self, id_article, ip, result_all, index):
      try:
        connect = psycopg2.connect(database="db_client", user="postgres", password="", host=str(ip[index]), port="5432", connect_timeout=5)
        cursor = connect.cursor()
        sql_requset =  f"""
            SELECT
    	pos.t_barcode.price[1], 
    	pos.t_article.name, 
    	pos.t_article.article, 
    	pos.t_barcode.barcode, 
    	pos.t_barcode.id_article, 
    	pos.t_barcode.id_barcode, 
    	pos.t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		pos.t_article.id_article = pos.t_barcode.id_article AND
    		pos.t_article.id_shop = pos.t_barcode.id_shop
    WHERE
    	pos.t_article.id_article = '{id_article}';
            """
        cursor.execute(sql_requset)
        result = cursor.fetchone()
        if result == None:
          result_all[index] = 0
        else:
          result_all[index] = result
      except OperationalError as err:
        print(f"Cant connect to {str(ip[index])}")
        result_all[index] = None
       
    
       
if __name__ == "__main__":
    price = Get_item_pos(515, barcode='28061')
    print(price.run())