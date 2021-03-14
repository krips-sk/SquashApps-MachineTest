from flask_restplus import Namespace, fields


class DropdownDto:
    api = Namespace('dropdown', description='dropdown related operations')

    dropdown_save = api.model('dropdown', {
        'id': fields.String(required=False, description='Dropdown id'),
        'key_value_en': fields.String(required=True, description='Dropdown value in Eng'),
        'key_value_ma': fields.String(required=True, description='Dropdown value in Malay'),
        'type': fields.String(required=True, description='Dropdown type'),
        'user_id':fields.String(required=True, description='user_id'),
    })

    delete_dropdown = api.model('delete_from_department', {
        'id': fields.Integer(required=True, description='id'),
    })

    dropdownlist = api.model('dropdown_list', {
        'id': fields.Integer(required=False, description='Dropdown id'),
        'key_id': fields.String(required=False, description='Dropdown key id'),
        'key_value_en': fields.String(required=True, description='Dropdown value in Eng'),
        'key_value_ma': fields.String(required=True, description='Dropdown value in Malay'),
        'type': fields.String(required=True, description='Dropdown type')
    })


class ProductDto:
    api = Namespace('product', description='product related operations')

    product_save = api.model('product', {
        'product_id': fields.Integer(required=False, description='Product id'),
        'product_name': fields.String(required=True, description='Product name'),
        'product_value': fields.String(required=True, description='Product value'),
        'type': fields.String(required=True, description='Product type'),
    })

    delete_product = api.model('delete_from_department', {
        'product_id': fields.Integer(required=True, description='product_id'),
    })

    productlist = api.model('product_list', {
        'product_id': fields.Integer(required=False, description='Product id'),
        'product_name': fields.String(required=False, description='Product Name'),
        'product_value': fields.String(required=True, description='Product Value'),
        'type': fields.String(required=True, description='Product type')
    })