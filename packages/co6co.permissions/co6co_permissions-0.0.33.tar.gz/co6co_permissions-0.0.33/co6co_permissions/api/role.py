from sanic import Sanic, Blueprint,Request
from co6co_sanic_ext .api import add_routes
from ..view_model.role_view import role_view,roles_view,roles_ass_view

role_api = Blueprint("roles_API",url_prefix="/role") 
add_routes(role_api,role_view,roles_view,roles_ass_view)

'''
userGroup_api.add_route(roles_view.as_view(),"/",name=roles_view.__name__)  
userGroup_api.add_route(role_view.as_view(),"/<pk:int>",name=role_view.__name__) 
'''