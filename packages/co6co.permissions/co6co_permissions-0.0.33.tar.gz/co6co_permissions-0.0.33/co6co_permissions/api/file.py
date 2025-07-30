from sanic import Sanic, Blueprint, Request
from co6co_sanic_ext .api import add_routes
from ..view_model.file import FileViews, FolderView
from ..view_model.file.upload import UploadView, UploadQueryView
from ..view_model.file.batch import batchDelView
from ..view_model.file.simple import RenameView, NewFolderView, FileContentView


# 文件管理
file_api = Blueprint("files_manage", url_prefix="/files")
add_routes(file_api, FileViews, FolderView, UploadView, UploadQueryView, batchDelView, RenameView, NewFolderView, FileContentView)
