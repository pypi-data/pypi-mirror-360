

from co6co_sanic_ext.model.res.result import Result
from co6co_sanic_ext.utils import JSON_util
from ..model.enum import menu_type, menu_state, user_state
from ..view_model.aop.api_auth import authorized
from sanic import Sanic, Blueprint, Request
from ..view_model.menu_view import menu_tree_view, menu_view, menus_view, menu_batch_view

from co6co_sanic_ext.api import add_routes

menu_api = Blueprint("menu_API", url_prefix="/menu")
add_routes(menu_api, menus_view, menu_tree_view, menu_view, menu_batch_view)
'''
menu_api.add_route(menus_view.as_view(),"/",name=menus_view.__name__) 
menu_api.add_route(menu_tree_view.as_view(),"/tree",name=menu_tree_view.__name__) 
menu_api.add_route(menu_view.as_view(),"/<pk:int>",name=menu_view.__name__) 
'''
'''
代码放置在 view_model 可能会出现循环引用问题
'''


@menu_api.route("/status", methods=["GET", "POST"])
@authorized
async def getMenuStatus(request: Request):
    """
    菜单状态
    """
    states = menu_state.to_dict_list()
    return JSON_util.response(Result.success(data=states))


@menu_api.route("/category", methods=["GET", "POST"])
@authorized
async def getMenuCategory(request: Request):
    """
    菜单类别
    """
    states = menu_type.to_dict_list()
    return JSON_util.response(Result.success(data=states))
