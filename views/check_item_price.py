import psycopg2

class Item_price:

    def __init__(self, id_shop, article='', barcode=''):
        self.id_shop = id_shop
        self.article = article
        self.barcode = barcode
        self.info_db = '192.168.1.14'

    def get_ip_pos(self, tradepoint, cash_box):
        connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host=self.info_db, port="5432")
        cursor = connect.cursor()
        sql_requset = f"select ip from t_kassa where trade_point = {tradepoint} and cash_box = {cash_box};"
        cursor.execute(sql_requset)
        result = cursor.fetchone()
        return result[0]

    def get_ips_of_trade_point(self, tradepoint):
        connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host=self.info_db, port="5432")
        cursor = connect.cursor()
        sql_requset = f"select ip from t_kassa where trade_point = {tradepoint};"
        cursor.execute(sql_requset)
        result = cursor.fetchall()
        return result

    def _get_ids_worklace_of_tradepoint(self):
        connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host=self.info_db, port="5432")
        cursor = connect.cursor()
        sql_requset = f"select cash_box from t_kassa where trade_point = {self.id_shop};"
        cursor.execute(sql_requset)
        result = cursor.fetchall()
        return result

    def get_name_tarade_point(self, trade_point):
        connect = psycopg2.connect(database="db_admin", user="postgres", password="1", host=self.info_db, port="5432")
        cursor = connect.cursor()
        sql_requset = f"select name from t_trade_point where trade_point = {trade_point};"
        cursor.execute(sql_requset)
        result = cursor.fetchone()
        return result[0]

    def get_price_of_item(self, article, barcode, id_shop, id_workplace, dpos):
        query_article = f"""
            SELECT
    	t_barcode.price[1], 
    	t_article.name, 
    	t_article.article, 
    	t_barcode.barcode, 
    	t_barcode.id_article, 
    	t_barcode.id_barcode, 
    	t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		t_article.id_article = t_barcode.id_article AND
    		t_article.id_shop = t_barcode.id_shop
    WHERE
    	t_article.article = '{article}' and
        t_article.id_shop = '{id_shop}';
            """

        query_barcode = f"""
            SELECT
    	t_barcode.price[1], 
    	t_article.name, 
    	t_article.article, 
    	t_barcode.barcode, 
    	t_barcode.id_article, 
    	t_barcode.id_barcode, 
    	t_article.id_shop
    FROM
    	pos.t_article
    	INNER JOIN
    	pos.t_barcode
    	ON 
    		t_article.id_article = t_barcode.id_article AND
    		t_article.id_shop = t_barcode.id_shop
    WHERE
    	t_barcode.barcode = '{barcode}' and
        t_barcode.id_shop = '{id_shop}';
            """

        if not dpos:
            ip = self.get_ip_pos(id_shop, id_workplace)
            try:
                connect_pos = psycopg2.connect(database="db_client", user="postgres", host=str(ip), port="5432")
                cursor = connect_pos.cursor()
                if article:
                    cursor.execute(query_article)
                if barcode:
                    cursor.execute(query_barcode)

                result = cursor.fetchall()
            except psycopg2.OperationalError:
                print(f"Oops!  Can not connect to {ip} Try again...")
                return None
            if result:
                item = {
                    "price": float(result[0][0]),
                    "item_name":  result[0][1],
                    "article":  result[0][2],
                    "barcode":  result[0][3],
                    "id_article":  result[0][4],
                    "id_barcode":  result[0][5],
                    "id_shop":  result[0][6],
                    "id_workplace":  id_workplace
                }
                return item
            print(f"[ERROR] (article={article}, barcode={barcode}, id_shop={id_shop}, id_workplace={id_workplace}): За данними параметрами в базі нічого не знайдено :(")
        else:
            ip = '192.168.1.139'
            try:
                connect_dpos = psycopg2.connect(database="db_server", user="postgres", host='192.168.1.139', port="5432")
                cursor = connect_dpos.cursor()
                if article:
                    cursor.execute(query_article)
                if barcode:
                    cursor.execute(query_barcode)

                result = cursor.fetchall()
            except psycopg2.OperationalError:
                print(f"Oops!  Can not connect to {ip} ")
                return None
            if result:
                item = {
                    "price": float(result[0][0]),
                    "item_name":  result[0][1],
                    "article":  result[0][2],
                    "barcode":  result[0][3],
                    "id_article":  result[0][4],
                    "id_barcode":  result[0][5],
                    "id_shop":  result[0][6],
                    "id_workplace":  "dpos"
                }
                return item
                #return result[0]
            print(f"[ERROR]  (article={article}, barcode={barcode}): За данними параметрами в базі цDPOS нічого не знайдено :(")

    def get_price_pos(self):
        print(self.id_shop)
        info_list = []
        for workplace in self._get_ids_worklace_of_tradepoint():
            pos_info = self.get_price_of_item(self.article, self.barcode, self.id_shop, workplace[0], dpos=False)
            info_list.append(pos_info)
        
        print(info_list)
        print(self.get_price_of_item(self.article, self.barcode, self.id_shop, workplace[0], dpos=True))


if __name__ == "__main__":
    price = Item_price(515, article='1301050700')
    price.get_price_pos()

#    article, barcode, id_shop = main(sys.argv[1:])
#    t = PrettyTable(['Ціна', 'Назва', 'Артикул', 'Штрих-код', 'Ід артикулу', 'Ід Штрихкоду', 'Ід магазину', 'Номер каси'])
#    for workplace in get_ids_worklace_of_tradepoint(id_shop):
#        row = get_price_of_item(article, barcode, id_shop, workplace[0], dpos=False)
#        if row:
#            price = [float(row[0][0])]
#            price.extend(list(row[1:]))
#            price.append(workplace[0])
#            t.add_row(price)
#
#    print(t)
#    t.clear_rows()
#
#    row = get_price_of_item(article, barcode, id_shop, workplace[0], dpos=True)
#    if row:
#        price = [float(row[0][0])]
#        price.extend(list(row[1:]))
#        price.append('цDPOS')
#        t.add_row(price)
#    print(t)
#