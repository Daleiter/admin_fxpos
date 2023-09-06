from flask_restful import fields


"""Testing object sturcture"""
shop_structure = {
    'id': fields.Integer,
    'name': fields.String,
    'base_ip': fields.String, 
    'active': fields.Boolean,
    'shop_number': fields.Integer
}

attribute_types = {
    #'id_attribute': fields.Integer,
    #'id_type': fields.Integer,
    'attribute_name': fields.String  
}

item_attribute_structure = {
    'id_item': fields.Integer,
    #id_item': fields.Nested(item_structure),
    'id_attribute': fields.Integer,
    'attribute_type': fields.Nested(attribute_types),
    #'attribute_type': attribute_types['attribute_name'],
    'value': fields.String
}

item_structure = {
    'id': fields.Integer,
    'shop': fields.Nested(shop_structure),
    'id_shop':fields.Integer,
    'host': fields.String,
    'id_type': fields.Integer,
    'active': fields.Boolean,
    'attributes': fields.Nested(item_attribute_structure)
}

pos_targets_structure = {
    'labels': fields.Nested({
    'id_pos': fields.String,
    'id_shop': fields.String,
    'is_prro': fields.String,
    'shop_name': fields.String
}),
    'targets': fields.List(fields.String)
}
printer_targets_structure = {
    'labels': fields.Nested({
    'id_shop': fields.String,
    'shop_name': fields.String
}),
    'targets': fields.List(fields.String)
}

router_targets_structure = {
    'labels': fields.Nested({
    'id_shop': fields.String,
    'shop_name': fields.String,
    'provider': fields.String
}),
    'targets': fields.List(fields.String)
}

raspberry_targets_structure = {
    'labels': fields.Nested({
    'id_shop': fields.String,
    'shop_name': fields.String
}),
    'targets': fields.List(fields.String)
}

addressbook_structure = {
    "items": fields.List(fields.Nested(
        {
            "number": fields.String,
            "name": fields.String
        })
), 
"refresh": fields.Integer
    
}