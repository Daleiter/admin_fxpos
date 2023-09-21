import os
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from utils.speedtest import Speedtest
from utils.sync import DBSync
from views.blueprint.pos_dashboard.views import pos_dashboard
from views.blueprint.edit_config.views import edit_config
from views.blueprint.silences.views import silences_blueprint
from views.blueprint.get_lost_check.views import pos_get_lost_check
from views.blueprint.quickcodes_dpos.views import quickcodes_dpos
from views.blueprint.inventory_shops.views import inventory_shop
from views.blueprint.inventory_edit.views import inventory_edit
from views.blueprint.monitoring_discovery.api_service import monitoring_api_service
from views.blueprint.check_item.views import b_check_item
from views.blueprint.check_sales_shop.views import check_sales_shop
from views.get_sum import Get_sum
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# imports for api
from flask_restful import Api
from rest.init_db import db, ma
from rest.init_rq import init_redis_components
from rest.init_cache import cache
from service.resources.shops import ShopList
from service.resources.shops import Shop, ShopPhones, ShopPhonesList
from service.resources.items import ItemsList
from service.resources.items import Item, ListItemsViewR
from service.resources.discovery import Pos_targets
from service.resources.workplace_props import WorkplaceOptionsList
from service.resources.incedent import IncedentList, ProblemsList, IncedentAnnouncer, AsteriskIncedents
from service.resources.incident_handler import IncidentHandler
from service.resources.label_print import LabelPrint
from service.resources.login import LoginResource
from service.resources.address_book import AddressBook
from service.resources.guac import GuacamoleConnectionList
from service.resources.pricer import Pricer
from utils.report_util import RepotUtil
from utils.db_query_runner import QueryRunner
from views.logger import setup_logging


app = Flask(__name__, template_folder='../templates', static_url_path='', static_folder='../static')
setup_logging()
environment = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(f'config.{environment.capitalize()}Config')
jwt = JWTManager(app)
api = Api(app)
init_redis_components(app)
db.init_app(app)
#db_C.init_app(app)
ma.init_app(app)
#ma_C.init_app(app)
cache.init_app(app)
CORS(app)

def get_aler():
    with app.app_context():
        handler = IncidentHandler()
        handler.get_incedents()


def send_exice_reoprt():
    print("Run task.... [send_exice_reoprt]")
    q = QueryRunner()
    RepotUtil(q.run_query('exice'), ["ter_dyr@lvivkholod.com", "reg_dir@lvivkholod.com"])
    
def run_dbsync():
    with app.app_context():
        DBSync().run()

sched = BackgroundScheduler(daemon=True)
#sched.add_job(get_aler,'interval',seconds=120)
sched.add_job(run_dbsync,'interval',seconds=10)
#sched.add_job(send_exice_reoprt, 'cron' , year="*", month="*", day="*", hour="8", minute="28", second="5")
sched.start()
# api resourses
api.add_resource(ShopList, '/api/shops', '/api/shops')
api.add_resource(Shop, '/api/shops', '/api/shops/<id_shop>')
api.add_resource(ItemsList, '/api/items', '/api/items')
api.add_resource(Item, '/api/items', '/api/items/<id_item>')
api.add_resource(LabelPrint, '/api/labelprint', '/api/labelprint/<article>')
api.add_resource(Pos_targets, '/api/targets', '/api/targets/<string:type>')
api.add_resource(ShopPhonesList, '/api/shops/phones', '/api/shops/phones')
api.add_resource(ShopPhones, '/api/shops/phones', '/api/shops/phones/<shop_number>')
api.add_resource(WorkplaceOptionsList, '/api/workplace-options', '/api/workplace-options/<id_shop>/<id_worplace>') #ListItemsViewR
api.add_resource(ListItemsViewR, '/api/all-items', '/api/all-items')
api.add_resource(IncedentList, '/api/incedents', '/api/incedents')
api.add_resource(ProblemsList, '/api/problems', '/api/problems')
api.add_resource(IncedentAnnouncer, '/api/sse', '/api/sse')
api.add_resource(LoginResource, '/api/login', '/api/login')
api.add_resource(GuacamoleConnectionList, '/api/conguac', '/api/conguac')
api.add_resource(AddressBook, '/api/addressbook', '/api/addressbook')
api.add_resource(AsteriskIncedents, '/api/incedents/', '/api/incedents/<string:type>')
api.add_resource(Pricer, '/api/pricer', '/api/pricer/<string:barcode>/<int:code_shop>')

# blueprints
app.register_blueprint(pos_dashboard)
app.register_blueprint(edit_config)
app.register_blueprint(silences_blueprint)
app.register_blueprint(pos_get_lost_check)
app.register_blueprint(inventory_shop)
app.register_blueprint(inventory_edit)
app.register_blueprint(monitoring_api_service)
app.register_blueprint(b_check_item)
app.register_blueprint(check_sales_shop)
app.register_blueprint(quickcodes_dpos)

@app.route('/api/dbsync', methods=['GET'])
def db_sync():
    
    """Run db synchronization"""
    s = DBSync()
    s.run()
    return '200'


@app.route('/', methods=['GET'])
def get_home():
    """Show home page"""
    return render_template('index.html')

@app.route('/api/sum/byday/<date>', methods=['GET'])
def get_sum(date):
    """Show home page"""
    res = Get_sum(date).run()
    return jsonify(res)

@app.route('/api/getalerts', methods=['GET'])
def getalerts():
    """Show home page"""
    handler = IncidentHandler()
    handler.get_incedents()
    
    return '200'

@app.route('/api/report', methods=['GET'])
def report():
    """Show home page"""
    send_exice_reoprt()
    return '200'

@app.route('/api/sseclient', methods=['GET'])
def sse_client():
    js = """
    <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Page Title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

</head>
<body>
    
</body>
        <script>
const eventSource = new EventSource('localhost:8888/api/sse');
console.log('okkk')
eventSource.onmessage = function(event) {
  const eventData = JSON.parse(event.data);
  // Handle the received event data
  console.log('Received event:', eventData);
};

eventSource.onerror = function(error) {
  console.error('SSE Error:', error);
};
</script>
</html>

"""
    return js


@app.route('/api/speedtest/<shop_number>', methods=['GET'])
def speedtest(shop_number):
    s = Speedtest(shop_number=shop_number)
    res = s.run_speedtest()
    return jsonify(res)

@app.route('/labelprintdev', methods=['GET'])
def labelprint1():

    return render_template('label_print.html')


# User authentication endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Perform user authentication here (e.g., check username and password against the database)
    if username == 'admin' and password == 'admin123':
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}! This is a protected route.'})