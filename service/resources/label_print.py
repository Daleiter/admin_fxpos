from flask_restful import Resource
from flask import  request, send_file
from flask_restful import reqparse, inputs
from io import BytesIO
from utils.label_pdf_gen import LablelPdfGen
from utils.ware_gold_info import Labelinfo
import os 

arg_parser = reqparse.RequestParser(bundle_errors=True)
arg_parser.add_argument('date', type=inputs.date, location='args')

class LabelPrint(Resource):
    """Api"""

    def get(self, article):
        """ Create a BytesIO object with PDF contents"""
        args = arg_parser.parse_args(strict=True)
        context = Labelinfo().get_info(article)
        print(len(context['ingredients']))
        #context = {'header': "Продукція кулінарна.Багет Мисливський.",
        #   'mass': "Маса нетто : 242 г (g)",
        #   'dstu': "Граничнодопустиме від'ємне відхилення від номінальної маси нетто 9 г (g). ТУ У 10.8-38213643-006:2015 ",
        #   'sklad': "Склад: багет 52 %, (борошно пшеничне в\г, молоко коров’яче незбиране, цукор, дріжджі, кефір, олія соняшникова рафінована, сіль кухонна), мисливські ковбаск 21 % (м’ясна сировина 100 %, сіль нітритна (консервант, фіксатор кольору), перець духмяний молотий, перець чорний мелений, цукор, часник свіжий очищений подрібнений), огірок консервований (огірки, сіль кухонна, лимонна кислота, кріп, зелень петрушки, листя хрону, часник свіжий), соус [майонез (олія соняшникова рафінована, цукор, сіль кухонна, яєчний порошок, емульгатор – крохмаль модифікований кукурудзяний, регулятор кислотності оцтова кислота, молочна кислота), гірчиця Діжонська (вода питна, зерна гірчиці білої та чорної, цукор, регулятор кислотності киислота оцтова, сіль кухонна, олія соняшникова рафінована, куркума, кмин)].",
        #   'made_by': "ТзОВ ТВК “Львівхолод”, Цех з виробництва швидкого харчування r-UA-13-21-4731 від 16.08.2019 р вул Луганська, 6, м.Львів, 79000, Україна, 095-18-00-337",
        #   'energy': "енергетична цінність-327,7 ккал (kcal) / 1368 кДж (kJ), жири- 19,93 г (g) з них насичені – 10,46 г (g), вуглеводи -28,77 г (g) з них цукри-7,8 г (g), білки-8,3 г (g), сіль-1,3 г (g).",
        #   'date_to': "31 тра 2023",
        #   'barcode': '2000002614500',
        #   'barcode_base64': None}
        label_g = LablelPdfGen(context, 1, date_to=args['date'])
        path = label_g._gen_pdf(60, 58)
        print(path)

        #os.remove(path)

        return send_file(path, as_attachment=True, attachment_filename=path, mimetype='application/pdf', cache_timeout=0)

    
    def post(self):
        """Get"""        

        return '', 200
