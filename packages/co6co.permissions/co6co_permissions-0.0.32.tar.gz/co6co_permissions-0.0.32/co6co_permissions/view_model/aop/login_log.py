
from functools import wraps
from sanic.request import Request
from ...model.pos.right import LoginLogPO


from datetime import datetime
from sanic.response import JSONResponse

from co6co.utils import log
from co6co_sanic_ext.model.res.result import Result
from co6co_db_ext.db_utils import db_tools, InsertCallable
from ...services import getCurrentUserId
import json


async def _loginLog(response: JSONResponse, request: Request):
    try:
        po = LoginLogPO()
        po.ipAddress = request.client_ip  # p.ip=self.forwarded['for']
        po.createTime = datetime.now()
        res = json.loads(str(response.body, encoding='utf-8'))
        result = Result.success()
        result.__dict__.update(res)
        po.name = request.json.get("userName")
        if result.code == 0:
            po.createUser = getCurrentUserId(request)
            po.state = "成功"
        else:
            po.state = "失败"
        # log.warn(po.__dict__)
        insert = InsertCallable(request.ctx.session)
        await insert(po)
    except Exception as e:
        log.err("写登录日志失败")


def loginLog(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        request: Request = None
        for a in args:
            if type(a) == Request:
                request = a
            # log.warn("第一个参数",type(a))
        '''
        for a,v in kwargs:
            log.warn("第er个参数",type(a),type(v))
        '''

        response = await f(*args, **kwargs)
        await _loginLog(response, request)
        return response
    return decorated_function
