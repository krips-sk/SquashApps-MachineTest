import uuid
from app.cura import db
from app.cura.user.model.role import Role
from sqlalchemy import and_,func, asc


def add_Role(data):
    try:
        if data['id']==0:
            role= Role.query.filter(func.lower(Role.role_Name)==func.lower(data['role_Name']),Role.isActive==1).first()
            if not role:
                new_role = Role(
                    role_Name=data['role_Name'],
                    role_Id=data['role_Id'],
                    created_by=data['created_by'],
                    isActive=1
                )
                save_changes(new_role)
                return generate_token(new_role)
            else:
                response_object = {
                    'ErrorCode': 9997,
                    'status': 'fail',
                    'message': 'Role name already exist.'
                }
                return response_object
        else:
            role = Role.query.filter_by(id=data['id']).first()
            if role:
                role.role_Name = data['role_Name']
                role.updated_by = data['created_by']

                save_changes(role)
                return generate_token(role)
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_all_roles(searchterm):
    try:
        if searchterm != '\"\"':
            return Role.query.filter(
                                    and_(
                                            Role.role_Name.ilike('%'+searchterm+'%'),
                                            Role.isActive == 1
                                        )
                                    ).order_by(asc(Role.role_Name)).all()
        else:
            return Role.query.filter_by(isActive=1).order_by(asc(Role.role_Name)).all()
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def get_a_role(id):
    try:
        return Role.query.filter_by(id=id).first()
    except Exception as e:
        print(e)
        print('Handling run-time error:')



def delete_Role(data):
    try:
        role = Role.query.filter_by(id=data['id']).first()
        if role:
            role.isActive = 0

            save_changes(role)
            response_object = {
                'status': 'success',
                'message': 'Role deleted successfully',
            }
            return generate_token(role)
        else:
            response_object = {
                'status': 'fail',
                'message': 'User not exists.',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')




def generate_token(role):
    try:
        # generate the auth token
        # auth_token = User.encode_auth_token(user.id)
        response_object = {
            'ErrorCode': 9999,
            'status': 'success',
            'message': 'Role added successfully',
            'Role id': role.id,
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 201


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def save_changefid(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')