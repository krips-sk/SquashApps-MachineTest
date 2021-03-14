# Name: product_list_controller.py
# Description: This is used to save the Product list values and related operations
# Author: Kumaresan A
# Created: 2021.01.25
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.01.25 save department added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import ProductDto
from app.ems.dropdown_list.sevice.product_service import save_Product, get_product_list

api = ProductDto.api
_product_save = ProductDto.product_save
productlist = ProductDto.productlist

#
#   Save product item
#
@api.route('/save_product')
class SaveProduct(Resource):
    @api.expect(_product_save, validate=True)
    @api.response(201, 'Product item added')
    @api.doc('Product item added')
    def post(self):
        data = request.json
        return save_Product(data=data)

#
#   feat  get the list of product list.
#
@api.route('/get_product_list/<type>')
class GetAllProductList(Resource):
    @api.doc('Get product list')
    #@token_required
    # @marshal_with(productlist)
    def get(self, type):
        try:
            """get department list"""
            return get_product_list(type)
        except Exception as e:
            logging.exception(e)
            return ""
