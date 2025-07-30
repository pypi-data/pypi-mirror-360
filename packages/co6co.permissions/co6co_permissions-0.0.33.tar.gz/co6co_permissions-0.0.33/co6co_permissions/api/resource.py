from sanic import Sanic, Blueprint, Request
from co6co_sanic_ext .api import add_routes
from ..view_model.resource.path_view import Video_View, Image_View, Poster_View, thumbnail_View
from ..view_model.resource.resource_view import Res_Image_View, Res_Video_View, Res_thumbnail_View, Res_Poster_View
from ..view_model.resource.upload_view import Upload_View, Image_View as upLoad_img_View, Video_View as upload_video_view

# 查看
_api = Blueprint("resource_API")
add_routes(_api, Res_Image_View, Res_Video_View, Res_thumbnail_View, Res_Poster_View)
add_routes(_api, Video_View, Image_View, Poster_View, thumbnail_View)

# 上传
_upload_api = Blueprint("resource_upload_API", url_prefix="/upload")
add_routes(_upload_api, Upload_View, upLoad_img_View, upload_video_view)

res_api = Blueprint.group(_api, _upload_api, url_prefix="/res")
