# Name: supplier_controller.py
# Description: This is used to save the supplier and related operations
# Author: Thirumurthy
# Created: 2020.12.31
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2020.12.31 save supplier added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import SupplierDto
from app.ems.supplier.sevice.supplier_service import save_supplier, get_supplier_list, delete_supplier_data, \
    get_supplier_details, get_all_supplier_list

api = SupplierDto.api
supplier_save = SupplierDto.supplier_save
delete_supplier = SupplierDto.delete_supplier
supplier_list_resp = SupplierDto.supplier_list_resp
supplier_info_rsp = SupplierDto.supplier_info


#
#   feat  Used to save the supplier.
#
@api.route('/add')
class AddSupplier(Resource):
    @api.response(201, 'supplier added successfully.')
    @api.expect(supplier_save, validate=True)
    #@token_required
    @api.doc('supplier added successfully.')
    def post(self):
        """Add item to supplier """
        data = request.json
        return save_supplier(data=data)


#
#   feat  get the list of Company supplier.
#
@api.route('/get_supplier_list/<user_id>/<page>/<row>/<searchterm>')
class GetAllSupplier(Resource):
    @api.doc('Get supplier list')
    #@token_required
    @marshal_with(supplier_list_resp)
    def get(self, user_id, page, row, searchterm):
        try:
            """get supplier list"""
            doc_list = get_supplier_list(user_id, page, row, searchterm)
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  get the list of Company suppliers.
#
@api.route('/get_all_supplier')
class GetAllSupplierList(Resource):
    @api.doc('Get supplier list')
    #@token_required
    @marshal_with(supplier_list_resp)
    def get(self):
        try:
            """get supplier list"""
            doc_list = get_all_supplier_list()
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  delete the supplier information by using id
#
@api.route('/delete')
class DeleteSupplier(Resource):
    @api.response(201, 'supplier deleted from  Company.')
    #@token_required
    @api.expect(delete_supplier, validate=True)
    @api.doc('delete supplier from Company.')
    def post(self):
        """Delete supplier"""
        data = request.json
        return delete_supplier_data(data)


#
#   feat  Used to get the supplier details.
#
@api.route('/get_details/<public_id>')
class GetSupplierDetails(Resource):
    @api.response(201, 'Used to get the company details.')
    @api.doc('Used to get the company details.')
    @marshal_with(supplier_info_rsp)
    def get(self, public_id):
        """Used to get the supplier details."""
        return get_supplier_details(public_id)
