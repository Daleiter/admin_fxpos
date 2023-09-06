#from rest.app import app as rest_app
import os
from views.app_all import app as web_app

use_reloader = True
if os.environ['PROD'] == 'yes':
    use_reloader = False

web_app.run(debug=True, host='0.0.0.0', port='8888', use_reloader=use_reloader) #, use_reloader=False