from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

metadata = MetaData(schema='inventory')
db = SQLAlchemy(metadata=metadata,engine_options={'isolation_level': 'AUTOCOMMIT'})
ma = Marshmallow()