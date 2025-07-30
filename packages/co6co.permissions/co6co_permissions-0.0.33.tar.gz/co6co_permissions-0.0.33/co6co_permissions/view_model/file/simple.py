from sanic import Request
from co6co_sanic_ext.model.res.result import Result
from ..base_view import AuthMethodView
import os
from sanic.response import file_stream, json
from co6co.utils import log 
import mimetypes

class RenameView(AuthMethodView):
    routePath = "/rename"

    async def post(self, request: Request):
        """
        重命名 文件或者目录
        @param {path:D:\\abcc\\xxx.xx,name:xxx.txt}
        """
        path_param = request.json.get("path", None)
        name = request.json.get("name", None)
        if path_param is None or name is None:
            return self.response_json(Result.fail(message="path和name参数是必须的"))
        try:
            os.renames(path_param, os.path.join(os.path.dirname(path_param), name))
            return self.response_json(Result.success(message="重命名完成！"))
        except Exception as e:
            return self.response_json(Result.fail(message="重命名失败{}".format(e)))


class NewFolderView(AuthMethodView):
    routePath = "/new"

    async def post(self, request: Request):
        """
        新建文件夹
        @param {path:D:\\abcc\\xxx.xx,name:xxx.txt}
        """
        path_param = request.json.get("path", None)
        name = request.json.get("name", None)
        if path_param is None or name is None:
            return self.response_json(Result.fail(message="path和name参数是必须的"))
        try:
            os.makedirs(os.path.join(path_param, name))
            return self.response_json(Result.success())
        except Exception as e:
            return self.response_json(Result.fail(message="新建文件夹'{}'失败:{}".format(name, e)))


class FileContentView(AuthMethodView):
    routePath = "/file"

    async def post(self, request: Request):
        """
        获取文件内容
        @param {path:D:\\abcc\\xxx.xx }
        """
        try: 
            path_param=None
            log.warn(request.json)
            path_param = request.json.get("path", None)
            if path_param is None:
                return self.response_json(Result.fail(message="path参数是必须的"))
            if os.path.exists(path_param) and os.path.isfile(path_param):
                return await file_stream(path_param,mime_type=mimetypes.guess_type(path_param)[0] or 'application/octet-stream')
            else:
                return json({}, 404)
        except Exception as e: 
            return self.response_json(Result.fail(message="获取文件内容'{}'失败:{}".format(path_param, e)))
