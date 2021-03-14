from flask_restplus import Api
from flask import Blueprint

from .cura.user.controller.user_controller import api as user_ns
from .cura.user.controller.auth_controller import api as auth_ns
from .cura.email.controller.email_conroller import api as email_ns
from .cura.user.controller.role_controller import api as  role_ns
from .cura.user.controller.rkp_disciplinary_controller import api as  rkp_discipline_ns
from .cura.user.controller.menuitem_controller import api as menuitem_ns
from .ems.schedule.controller.schedule_controller import api as schedule_ns
from .ems.leave_management.controller.leave_management_controller import api as leave_management_ns
from .ems.legal_documents.controller.legal_document_controller import api as legal_document_ns
from .ems.vehicle.controller.vehicle_controller import api as vehicle_ns
from .ems.predeparture.controller.pdc_registration_controller import api as pdc_ns
from .ems.audit_log.controller.audit_log_controller import api as audit_log_ns
from .ems.workshop.controller.workshop_controller import api as workshop_ns
from .ems.branch.controller.branch_controller import api as branch_ns
from .ems.supplier.controller.supplier_controller import api as supplier_ns
from .ems.notification.controller.notification_controller import api as notification_ns
from .ems.department.controller.department_controller import api as department_ns
from .ems.report.controller.report_controller import api as report_ns

from .ems.dropdown_list.controller.dropdown_controller import api as dropdown_ns
from .ems.claim.controller.claim_controller import api as claim_ns
from .ems.dropdown_list.controller.product_controller import api as product_ns

blueprint = Blueprint('api', __name__)

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(blueprint,
          title='CURA API WITH JWT',
          version='1.0',
          description='A CURA rest web service',
          doc='/',
          security='Bearer Auth',
          authorizations=authorizations
          )

api.add_namespace(auth_ns)
api.add_namespace(user_ns, path='/user')
api.add_namespace(role_ns, path='/role')
api.add_namespace(menuitem_ns, path='/menuitems')
api.add_namespace(schedule_ns, path='/schedule')
api.add_namespace(leave_management_ns, path='/leavemanagement')
api.add_namespace(legal_document_ns, path='/legaldocument')
api.add_namespace(pdc_ns, path='/pdc')
api.add_namespace(email_ns)
api.add_namespace(vehicle_ns, path='/vehicle')
api.add_namespace(audit_log_ns, path='/audit_log')
api.add_namespace(workshop_ns, path='/workshop')
api.add_namespace(branch_ns, path="/branch")
api.add_namespace(supplier_ns, path='/supplier')
api.add_namespace(notification_ns, path='/notification')
api.add_namespace(department_ns, path='/department')
api.add_namespace(rkp_discipline_ns, path='/rkp_discipline')
api.add_namespace(dropdown_ns, path='/dropdown')
api.add_namespace(report_ns, path='/report')
api.add_namespace(claim_ns, path='/claim')
api.add_namespace(product_ns, path='/product')
