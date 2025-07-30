from sanic import Request
from co6co_sanic_ext.model.res.result import Result
from ..base_view import AuthMethodView
from ...services import fileService


class batchDelView(AuthMethodView):
    routePath = "/batch/del"

    async def post(self, request: Request):
        paths = request.json.get("paths", [])
        try:
            flag = 0
            for path in paths:
                fileService.delFileOrFolder(path)
                flag += 1
            return self.response_json(Result.success(message="删除完成！"))
        except Exception as e:
            if flag > 0:
                return self.response_json(Result.fail(message="部分删除，因{}后面执行删除".format(e)))
            return self.response_json(Result.fail(message="删除失败：{}".format(e)))
