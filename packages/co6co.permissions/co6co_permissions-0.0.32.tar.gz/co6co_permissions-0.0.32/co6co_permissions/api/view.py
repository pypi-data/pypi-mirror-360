

from sanic import Sanic, Blueprint, Request
from ..view_model.ui.menu_view import ui_tree_view
from ..view_model.ui.session_view import Session_View
from co6co_sanic_ext.api import add_routes

view_api = Blueprint("view_API", url_prefix="/view")
add_routes(view_api, ui_tree_view, Session_View)
'''
menu_api.add_route(menus_view.as_view(),"/",name=menus_view.__name__) 
menu_api.add_route(menu_tree_view.as_view(),"/tree",name=menu_tree_view.__name__) 
menu_api.add_route(menu_view.as_view(),"/<pk:int>",name=menu_view.__name__) 
'''
