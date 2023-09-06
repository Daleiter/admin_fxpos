from flask import Flask, render_template, send_from_directory, jsonify

from views.blueprint.pos_dashboard.views import pos_dashboard
from views.blueprint.edit_config.views import edit_config
from views.blueprint.silences.views import silences_blueprint
from views.blueprint.get_lost_check.views import pos_get_lost_check
from views.blueprint.inventory_shops.views import inventory_shop
from views.blueprint.monitoring_discovery.api_service import monitoring_api_service
from views.blueprint.check_item.views import b_check_item
from views.get_sum import Get_sum

app = Flask(__name__, template_folder='../templates', static_url_path='', static_folder='../static')
app.config['SECRET_KEY'] = 'secret_key'
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(pos_dashboard)
app.register_blueprint(edit_config)
app.register_blueprint(silences_blueprint)
app.register_blueprint(pos_get_lost_check)
app.register_blueprint(inventory_shop)
app.register_blueprint(monitoring_api_service)
app.register_blueprint(b_check_item)



@app.route('/', methods=['GET'])
def get_home():
    """Show home page"""
    return render_template('index.html')

@app.route('/api/sum/byday/<date>', methods=['GET'])
def get_sum(date):
    """Show home page"""
    res = Get_sum(date).run()
    return jsonify(res)

@app.route('/api/speedtest/<shop_number>', methods=['GET'])
def speedtest(shop_number):
    res = ''
    return jsonify(res)