from flask import request
from flask_restplus import Resource
import logging

from app.cura.user.util.decorator import admin_token_required
from ..util.dto import RoleDto
from ..service.role_service import add_Role  , delete_Role ,generate_token, get_a_role,get_all_roles
from app.cura.util.constants import constant

api = RoleDto.api
_role = RoleDto.role
role_update = RoleDto.role_update
role_delete = RoleDto.role_delete



@api.route('/add')
class RoleAdd(Resource):
    @api.expect(_role, validate=True)
    @api.response(201, 'Role successfully created.')
    @api.doc('create a new Role')
    def post(self):
        """Creates a new Role """
        data = request.json
        print(data);
        return add_Role(data)

@api.route('/id/<role_id>')
class RoleGet(Resource):
    @api.doc('get a user')
    @api.marshal_with(_role)
    def get(self, role_id):
        """get a user given its identifier"""
        role = get_a_role(role_id)
        if not role:
            api.abort(404)
        else:
            return role

@api.route('/<searchterm>')
class RoleList(Resource):
    @api.doc('list_of_registered_role')
    @api.marshal_list_with(_role, envelope='data')
    def get(self, searchterm):
        logging.info("This is a test log")
        logging.info(constant("INVALID_USER"))

        """List all registered users"""
        return get_all_roles(searchterm)

@api.route('/delete')
class RoleDelete(Resource):
    @api.expect(role_delete, validate=True)
    @api.response(201, 'Role deleted.')
    @api.doc('Delete user')
    def post(self):
        """Delete User """
        data = request.json
        return delete_Role(data=data)
