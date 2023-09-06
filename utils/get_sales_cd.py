import requests
import psycopg2
from datetime import datetime

conn_cashdesk = psycopg2.connect(
    dbname='dbmain',
    user='sysdba',
    host='192.168.1.172',
    password='masterkey'
)
query = """
WITH checks as (
selecT o.code_shop as "Код магазину", s.name_shop "Торговий майданчик", o.id_workplace "Номер каси",o.date_receipt "Дата чека",
o.code_order "Код чека",  
  o.code_shop||':'||o.id_workplace||'.'||o.code_z_report||'.'||o.code_order_shift "Номер чека",
       o.number_receipt "Фиск. номер чека",    
       o.sum_order  "Сума чека до сплат",        
       (select array_to_string(array_agg(p.name_pay||' '|| op.sum_pay), ', ') descr_pay from pos.order_pay op join pos.pay p on p.type_pay=op.type_pay where op.code_order = o.code_order and op.id_workplace = o.id_workplace and op.code_shop = o.code_shop and op.method_pay_rro!=0) "Оплати бонус/серт.",       
       o.sum_order - (select coalesce(sum(op.sum_pay),0) from pos.order_pay op where op.code_order = o.code_order and op.id_workplace = o.id_workplace and op.code_shop = o.code_shop and op.method_pay_rro!=0) "Сума чека РРО",        
       ( SELECT sum(op.sum_pay) as descr_pay  from pos.order_pay op join pos.pay p on p.type_pay=op.type_pay where op.code_order = o.code_order and op.id_workplace = o.id_workplace and op.code_shop = o.code_shop and op.method_pay_rro=0) "Оплати РРО",       
       case o.type_order when 0 then 'Продаж' when 1 then 'Повернення' else '~' end "Тип",
       
       o.date_receipt "Дата чека" ,   u.user_name "Касир", o.number_cash_register"Серійний номер РРО" ,
       add_info::json->>'barcodeClient' "Штрихкод клиієнта",
       o.date_open "Дата відкриття чека",         
       o.code_order, o.id_workplace, o.code_shop, o.code_shop||':'||o.id_workplace||'.'||o.code_z_report||'.'||o.code_order_shift number_novus
       
from pos.order_client o 
 left join pos.shops s on s.code_shop = o.code_shop
 left join pos.user_pos u  on u.code_user = o.code_user     
where

o.code_shop <> 1 
and o.type_order  = 0
and o.date_open >= date_trunc('day', to_date('%s','YYYY-MM-DD') )
and o.date_open <= date_trunc('day', to_date('%s','YYYY-MM-DD') )
and o.date_receipt is not null

order by o.id_workplace, o.code_order
),

resul as ( 
SELECT "Код магазину", 
"Торговий майданчик" as "Назва магазину",
sum ( "Оплати РРО" ) as "ТО загалом",
"count"("Номер чека") as "Кількість чеків",
NULLIF (sum( case WHEN "Штрихкод клиієнта" is not NULL THEN "Оплати РРО" else 0 end) :: DECIMAL, 0 ) as "ТО Родина",
NULLIF (COUNT( case WHEN "Штрихкод клиієнта" is not NULL THEN "Штрихкод клиієнта" else NULL end) :: DECIMAL, 0 ) as "Кількість чеків родина"
from checks
GROUP BY "Код магазину", "Торговий майданчик"
)

SELECT
    "Код магазину",
    "Назва магазину",
    "ТО загалом",
    "Кількість чеків",
    ( "ТО загалом" / "Кількість чеків" ) :: "numeric" ( 10, 2 ) AS "сер.чек  Загалом"
FROM
    resul;
"""


def send_data():
    data_to_powerbi = [] #%Y-%m-%dT%H:%M:%SZ
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    db_date_string = now.strftime("%Y-%m-%d")
    url = "https://api.powerbi.com/beta/9d1a8c34-83a4-43c7-9693-bbcea5566381/datasets/ad7ca338-aedd-428a-a34b-477a6e3e27b9/rows?key=HmuEyiSCzPjOyCN4byHT0GYaJKDzvZreiLa%2BGa5u0zm14pAEgeSs%2FzZw0YXpD408%2B8i7%2FPwOEVsWbvOAI%2BfrTA%3D%3D"
    cursor = conn_cashdesk.cursor()
    cursor.execute(query % ('2023-03-26', '2023-03-27'))
    res = cursor.fetchall()
    for row in res:
        data_to_powerbi.append(
            {
                "shop": row[0],
                "shop_name": row[1],
                "sales": float(row[2]),
                "count_orders": float(row[3]),
                "avg_order": float(row[4]),
                "date_time": dt_string
            }
        )
    requests.post(url, json=data_to_powerbi)

send_data()
