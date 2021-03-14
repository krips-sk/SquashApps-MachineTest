from flask import request
from flask_restplus import Resource
import logging
from ..util.dto import MenuItemDto
from ..service.menuitem_service import get_Menuitem, add_RoleMenu, save_all_role_menu_permission
from app.cura.util.constants import constant

api = MenuItemDto.api
_menu = MenuItemDto.menuitem
_rolemenu = MenuItemDto.rolemenu
_all_permission_save = MenuItemDto.all_permission_save


@api.route('/getmenu/<parentid>/<roleid>')
class MenuGet(Resource):
    @api.doc('get a menuitem')
    # @api.marshal_with(_enquiry)
    def get(self, parentid, roleid):
        """get a Enquiry given its identifier"""
        return get_Menuitem(parentid, roleid)


@api.route('/role/update')
class RoleMenuUpdate(Resource):
    @api.expect(_all_permission_save, validate=True)
    @api.response(201, 'Role Menu successfully updated.')
    @api.doc('create a new Role')
    def post(self):
        """Creates or update Role menu"""
        data = request.json
        print(data);
        return save_all_role_menu_permission(data)


@api.route('/role/single_update')
class RoleMenuSingleUpdate(Resource):
    @api.expect(_rolemenu, validate=True)
    @api.response(201, 'Role Menu successfully updated.')
    @api.doc('create a new Role')
    def post(self):
        """Creates or update Role menu"""
        data = request.json
        print(data);
        return add_RoleMenu(data)
