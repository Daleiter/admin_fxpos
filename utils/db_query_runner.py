from sqlalchemy import create_engine
from sqlalchemy import text

class QueryRunner:
    
    def run_query(self, name_query):
        #result = self.db.engine.execute(self.list_query[name_query])
        with self.db.connect() as connection:
            result = connection.execute(text(self.list_query[name_query]))
            connection.close()
        #print(result.keys())
        return result
    def __init__(self):
        self.db = create_engine('postgresql://sysdba:masterkey@192.168.1.172:5432/dbmain')
        self.list_query = {
        "test": "SELECT * FROM pos.user_pos LIMIT 1000;",
        "exice": """WITH checks AS (
	SELECT
		o.code_shop AS "Код магазину",
		s.name_shop "Торговий майданчик",
		o.id_workplace "Номер каси",
		o.date_order "Дата чека1",
		o.code_order "Код чека",
		o.code_shop || ':' || o.id_workplace || '.' || o.code_z_report || '.' || o.code_order_shift "Номер чека",
		o.number_receipt "Фиск. номер чека",
		o.sum_order "Сума чека до сплат",
		(
		SELECT
			array_to_string( ARRAY_AGG ( P.name_pay || ' ' || op.sum_pay ), ', ' ) descr_pay 
		FROM
			pos.order_pay op
			JOIN pos.pay P ON P.type_pay = op.type_pay 
		WHERE
			op.code_order = o.code_order 
			AND op.id_workplace = o.id_workplace 
			AND op.code_shop = o.code_shop 
			AND op.method_pay_rro != 0 
		) "Оплати бонус/серт.",
		o.sum_order - (
		SELECT COALESCE
			( SUM ( op.sum_pay ), 0 ) 
		FROM
			pos.order_pay op 
		WHERE
			op.code_order = o.code_order 
			AND op.id_workplace = o.id_workplace 
			AND op.code_shop = o.code_shop 
			AND op.method_pay_rro != 0 
		) "Сума чека РРО",
		(
		SELECT SUM
			( op.sum_pay ) AS descr_pay 
		FROM
			pos.order_pay op
			JOIN pos.pay P ON P.type_pay = op.type_pay 
		WHERE
			op.code_order = o.code_order 
			AND op.id_workplace = o.id_workplace 
			AND op.code_shop = o.code_shop 
			AND op.method_pay_rro = 0 
		) "Оплати РРО",
	CASE
			o.type_order 
			WHEN 0 THEN
			'Продаж' 
			WHEN 1 THEN
			'Повернення' ELSE'~' 
		END "Тип",
	o.date_receipt "Дата чека",
	u.user_name "Касир",
	o.number_cash_register "Серійний номер РРО",
	add_info :: json ->> 'barcodeClient' "Штрихкод клиієнта",
	o.date_open "Дата відкриття чека",
	o.code_order,
	o.id_workplace,
	o.code_shop,
	o.code_shop || ':' || o.id_workplace || '.' || o.code_z_report || '.' || o.code_order_shift number_novus 
FROM
	pos.order_client o
	LEFT JOIN pos.shops s ON s.code_shop = o.code_shop
	LEFT JOIN pos.user_pos u ON u.code_user = o.code_user 
WHERE
	1 = 1--o.code_shop = { c_shop_all;Торговий майданчик} 
AND o.code_shop <> 1 
AND o.type_order = 0 
AND o.date_order = to_char(  now( ) + INTERVAL '-1 days'  , 'yyyy-mm-dd' )::date
--AND o.date_order > to_char(  now( ) + INTERVAL '-30 days'  , 'yyyy-mm-dd' )::date
AND o.date_receipt IS NOT NULL 
--and  o.code_shop = 597

ORDER BY
	o.id_workplace,
	o.code_order 
	) SELECT
	checks."Код магазину",
	checks."Торговий майданчик",
	checks."Номер каси",
	checks."Касир",
	checks."Код чека",
	checks."Номер чека",
    checks."Дата відкриття чека" AS "Дата чека",
	--to_char( checks."Дата відкриття чека", 'dd/mm/yyyy' ) AS "Дата чека",
	to_char(  wares_order.time_add, 'HH24:MI:SS')::time  as "Час чека",
	wares.article as "Артикул",
	wares.name_wares as "Назава товару",
CASE
		
		WHEN wares_order.add_info :: json ->> 'codeExcise' = '' THEN
		'Проскановано спецкод (OOOO000000)' ELSE wares_order.add_info :: json ->> 'codeExcise' 
	END AS "КодАкцизМарки" 
FROM
	checks
	JOIN pos.wares_order ON checks."Код магазину" = pos.wares_order.code_shop 
	AND checks."Номер каси" = pos.wares_order.id_workplace 
	AND checks."Код чека" = pos.wares_order.code_order
	JOIN pos.wares ON wares_order.code_wares = wares.code_wares 
WHERE
	wares_order.add_info LIKE'%%codeExcise%%' 
	AND checks."Код магазину" <> 1 
	AND wares_order.is_deleted = 'f' 
	AND checks."Дата чека1" = to_char(  now( ) + INTERVAL '-1 days'  , 'yyyy-mm-dd' )::date;"""
    }