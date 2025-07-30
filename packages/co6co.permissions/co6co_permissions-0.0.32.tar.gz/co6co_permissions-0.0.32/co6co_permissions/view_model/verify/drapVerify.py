
from co6co_web_db.view_model import BaseMethodView
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
import uuid
import datetime


class drap_verify_view(BaseMethodView):

    async def post(self, request: Request):
        """
        拖动验证
        """
        json: dict = request.json
        start = json.get("start", 0)
        end = json.get("end", 0)
        data = json.get("data", [])
        start = datetime.datetime.fromtimestamp(start/1000)
        end = datetime.datetime.fromtimestamp(end/1000)
        dif = end-start
        min = datetime.timedelta(milliseconds=60)
        max = datetime.timedelta(seconds=15)
        if dif > min and dif < max:
            s = str(uuid.uuid4())
            _, sDict = self.get_Session(request)
            sDict["verifyCode"] = s
            return JSON_util.response(Result.success(data=s, message=f"验证成功,用时：{dif.total_seconds()}s"))
        else:
            return JSON_util.response(Result.fail(message="验证失败"))
