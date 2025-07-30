from sanic import Sanic, Blueprint, Request
from co6co_sanic_ext.api import add_routes
from ..view_model.verify.drapVerify import drap_verify_view
from ..view_model.user_group import user_groups_sub_tree_view


verify_api = Blueprint("verify_api", url_prefix="/verify")
add_routes(verify_api, drap_verify_view)
