import uuid
import logging

from app.cura import db
from app.cura.user.model.menu import Menuitem
from app.cura.user.model.rolemenu import RoleMenu
from app.cura.user.model.role import Role
from app.cura.user.model.user import User
from sqlalchemy import asc, and_, desc
import datetime


def get_Menuitem(parentid, role_Id, islogin=0, sheet_menu=[], company_menu=[], mgr_menu=[]):
    try:
        menu_item_query = db.session.query(Menuitem, RoleMenu).outerjoin(RoleMenu, and_(Menuitem.id == RoleMenu.menu_id,
                                                                                        RoleMenu.role_id == role_Id,
                                                                                        RoleMenu.isActive == 1))
        menu = menu_item_query.filter(Menuitem.isActive == 1, Menuitem.parent_id == parentid) \
            .order_by(asc(Menuitem.parent_id), asc(Menuitem.order_no)).all()
        menulist = []
        for data in menu:
            data1 = {}
            data1["id"] = data[0].id
            data1["menu_name"] = data[0].menu_name
            data1["display_name"] = data[0].display_name
            data1["menu_code"] = data[0].menu_code
            data1['parent_id'] = data[0].parent_id
            data1['order_no'] = data[0].order_no
            data1['submenu_type'] = data[0].submenu_type
            data1["is_view"] = data[1].is_view if data[1] else 0
            data1["is_add"] = data[1].is_add if data[1] else 0
            data1["is_edit"] = data[1].is_edit if data[1] else 0
            data1["is_delete"] = data[1].is_delete if data[1] else 0
            if islogin == 1:
                if data1["is_view"] == 1:
                    menulist.append(data1)
            else:
                menulist.append(data1)

            if data[0].submenu_type == 2:
                data1["sub_menu"] = sheet_menu
            elif data[0].submenu_type == 3:
                data1["sub_menu"] = company_menu
            elif data[0].submenu_type == 4:
                data1["sub_menu"] = mgr_menu
            else:
                # check the parent exists then call
                parent_count = Menuitem.query.filter_by(parent_id=data[0].id, isActive=1).count()
                if parent_count > 0:
                    data1["sub_menu"], tmp = get_Menuitem(data[0].id, role_Id, islogin)

        response_object = {
            'menulist': menulist,
            'TotalCount': len(menulist),
            'ErrorCode': '9999'
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)
        response_object = {
            'menulist': [],
            'TotalCount': 0,
            'ErrorCode': '9997'
        }
        return response_object, 201


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def add_RoleMenu(data):
    try:
        role = Role.query.filter_by(role_Id=data['role_id']).filter_by(
            isActive=1).first()
        if role:
            menu = Menuitem.query.filter_by(id=data['menu_id']).filter_by(
                isActive=1).first()
            if menu:
                menurole = RoleMenu.query.filter_by(role_id=data['role_id'], menu_id=data['menu_id']).filter_by(
                    isActive=1).first()
                if menurole:
                    menurole.is_view = 1 if (data['is_add'] == 1 or data['is_edit'] == 1 or data['is_delete'] == 1) else \
                        data[
                            'is_view']
                    menurole.is_add = data['is_add']
                    menurole.is_edit = data['is_edit']
                    menurole.is_delete = data['is_delete']
                    menurole.updated_by = data['created_by']
                    menurole.updated_date = datetime.datetime.utcnow()
                    save_changes(menurole)
                    response_object = {
                        'status': 'success',
                        'message': 'Menu Role Added',
                        'ErrorCode': '9999'
                    }
                    return response_object, 200
                else:
                    new_menu_role = RoleMenu(
                        role_id=data['role_id'],
                        menu_id=data['menu_id'],
                        is_view=1 if (data['is_add'] == 1 or data['is_edit'] == 1 or data['is_delete'] == 1) else data[
                            'is_view'],
                        is_add=data['is_add'],
                        is_edit=data['is_edit'],
                        is_delete=data['is_delete'],
                        created_by=data['created_by'],
                        created_date=datetime.datetime.utcnow())
                    new_menu_role.isActive = 1
                    save_changes(new_menu_role)
                    # need to send email to the user.
                    response_object = {
                        'status': 'success',
                        'message': 'Menu Role Added',
                        'ErrorCode': '9999'
                    }
                    return response_object, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Menu does not exits',
                    'ErrorCode': '9997'
                }
                return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Role does not exits',
                'ErrorCode': '9996'
            }
            return response_object, 200
    except Exception as e:
        print(e)
        print('Handling run-time error:')




def get_login_menu(role_id, user_id):
    try:
        menu_item_query = db.session.query(Menuitem, RoleMenu).outerjoin(RoleMenu, and_(Menuitem.id == RoleMenu.menu_id,
                                                                                        RoleMenu.role_id == role_id,
                                                                                        RoleMenu.isActive == 1))
        menu = menu_item_query.filter(Menuitem.isActive == 1, Menuitem.parent_id == -1) \
            .order_by(asc(Menuitem.parent_id), asc(Menuitem.order_no)).all()
        menu_list = []
        sheet_menu, tmp = [],0
        company_menu = [],0
        mgr_menu = [],0
        for data in menu:
            data1 = {}
            data1["is_view"] = data[1].is_view if data[1] else 0
            if data1["is_view"] == 1:
                data1["id"] = data[0].id
                data1["menu_name"] = data[0].menu_name
                data1["display_name"] = data[0].display_name
                data1["menu_code"] = data[0].menu_code
                data1['parent_id'] = data[0].parent_id
                data1['order_no'] = data[0].order_no
                data1['submenu_type'] = data[0].submenu_type

                data1["is_add"] = data[1].is_add if data[1] else 0
                data1["is_edit"] = data[1].is_edit if data[1] else 0
                data1["is_delete"] = data[1].is_delete if data[1] else 0
                # check the menu is entry then need to display sheets
                # to display the sheet list require to check the current user has view permission
                if data[0].submenu_type == 2:
                    data1["sub_menu"] = sheet_menu
                elif data[0].submenu_type == 3:
                    data1["sub_menu"] = company_menu
                elif data[0].submenu_type == 4:
                    data1["sub_menu"] = mgr_menu
                else:
                    data1["sub_menu"], tmp = get_Menuitem(data[0].id, role_id, 0, sheet_menu, company_menu, mgr_menu)

                menu_list.append(data1)

        response_object = {
            'main_menu_list': menu_list,
            'TotalCount': len(menu_list),
            'ErrorCode': '9999'
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            'main_menu_list': [],
            'TotalCount': 0,
            'ErrorCode': '9997',
            'components': ''
        }
        return response_object


def save_all_role_menu_permission(full_data):
    try:
        role = Role.query.filter_by(role_Id=full_data['role_id']).filter_by(
            isActive=1).first()
        if role:
            for data in full_data['role_permission']:
                menu = Menuitem.query.filter_by(id=data['id']).filter_by(
                    isActive=1).first()
                if menu:
                    menurole = RoleMenu.query.filter_by(role_id=full_data['role_id'], menu_id=data['id']).filter_by(
                        isActive=1).first()
                    if menurole:
                        menurole.is_view = 1 if (
                                data['is_add'] or data['is_edit'] or data['is_delete']) else \
                            1 if data[
                                     'is_view'] == True else -1
                        menurole.is_add = 1 if data['is_add'] else -1
                        menurole.is_edit = 1 if data['is_edit'] else -1
                        menurole.is_delete = 1 if data['is_delete'] else -1
                        menurole.updated_by = full_data['created_by']
                        menurole.updated_date = datetime.datetime.utcnow()
                        save_changes(menurole)
                        response_object = {
                            'status': 'success',
                            'message': 'Menu Role Added',
                            'ErrorCode': '9999'
                        }
                    else:
                        new_menu_role = RoleMenu(
                            role_id=full_data['role_id'],
                            menu_id=data['id'],
                            is_view=1 if (data['is_add'] or data['is_edit'] or data['is_delete']) else
                            1 if data['is_view'] else -1,
                            is_add=1 if data['is_add'] else -1,
                            is_edit=1 if data['is_edit'] else -1,
                            is_delete=1 if data['is_delete'] else -1,
                            created_by=full_data['created_by'],
                            created_date=datetime.datetime.utcnow())
                        new_menu_role.isActive = 1
                        save_changes(new_menu_role)
                        response_object = {
                            'status': 'success',
                            'message': 'Menu Role Added',
                            'ErrorCode': '9999'
                        }
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Menu does not exits',
                        'ErrorCode': '9997'
                    }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Role does not exits',
                'ErrorCode': '9996'
            }
            return response_object, 200
    except Exception as e:
        print(e)
        print('Handling run-time error:')
