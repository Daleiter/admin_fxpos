from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_marshmallow import Marshmallow

metadata = MetaData(schema='pos')
db = SQLAlchemy(metadata=metadata, session_options={'autocommit': True})
ma = Marshmallow()