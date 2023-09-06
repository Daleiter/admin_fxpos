from flask_restful import Resource
from flask_restful import reqparse
from models.db_model_cashdesk import WorkplaceOptions, WorkplaceOptions_schema, db


item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('itemtype', type=str, location='args')
item_parser.add_argument('shop_number', type=str, location='args')
#item_parser.add_argument('shop_number', type=str, location='json')

class WorkplaceOptionsList(Resource):
    """Api for CRUD operations for colection of shops"""

    def get(self, id_shop, id_worplace):
        """Get list shops"""        
        workplaceOptions = WorkplaceOptions.query.filter(WorkplaceOptions.code_option.in_([12, 55, 139, 15]), WorkplaceOptions.code_shop==id_shop, WorkplaceOptions.id_workplace==id_worplace).all()
        print(workplaceOptions)
        res = WorkplaceOptions_schema().dump(workplaceOptions, many=True)
        print(res)
        db.session.close()
        return res, 200
