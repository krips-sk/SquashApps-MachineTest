# Name: dropdown_list_controller.py
# Description: This is used to save the Dropdown list values and related operations
# Author: Kumaresan A
# Created: 2021.01.25
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.01.25 save department added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import DropdownDto
from app.ems.dropdown_list.sevice.dropdown_service import save_dropdown, get_dropdown_list,delete_dropdown_value

api = DropdownDto.api
_dropdown_save = DropdownDto.dropdown_save
dropdownlist = DropdownDto.dropdownlist

#
#   Save dropdown item
#
@api.route('/save_dropdownitem')
class SaveDropDown(Resource):
    @api.expect(_dropdown_save, validate=True)
    @api.response(201, 'Dropdown item added')
    @api.doc('Dropdown item added')
    def post(self):
        data = request.json
        return save_dropdown(data=data)

#
#   feat  get the list of dropdown list.
#
@api.route('/get_dropdown_list/<type>')
class GetAllDropdownList(Resource):
    @api.doc('Get dropdown list')
    def get(self, type):
        try:
            """get department list"""
            return get_dropdown_list(type)
        except Exception as e:
            logging.exception(e)
            return ""

#
#   feat  get the list of dropdown list.
#
@api.route('/delete/<drop_id>/<user_id>')
class DeleteDropDown(Resource):
    @api.doc('delete dropdown value')
    def get(self, drop_id,user_id):
        try:
            """delete dropdown value"""
            return delete_dropdown_value(drop_id,user_id)
        except Exception as e:
            logging.exception(e)
            return ""
