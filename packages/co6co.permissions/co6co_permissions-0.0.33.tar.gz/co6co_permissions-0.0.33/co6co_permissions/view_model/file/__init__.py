
from sanic.response import text
from sanic import Request
from sanic.response import file, file_stream, json, raw
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from ..base_view import AuthMethodView
from ...model.filters.file_param import FileParam
from ...services import fileService
import os
import datetime
from co6co.utils import log
import tempfile
import shutil


class File:
    isFile: bool
    name: str
    path: str
    right: str
    date: datetime.datetime
    size: int

    def __init__(self):
        self.isFile = None
        self.name = None
        self.path = None
        self.right = None
        self.updateTime = None
        self.size = None
        pass

    def __init__(self, root, name):
        self.name = name
        self.path = os.path.join(root,   name)
        self.path = os.path.abspath(self.path)
        self.isFile = os.path.isfile(self.path)
        if self.isFile:
            self.size = os.path.getsize(self.path)
        self.right = None
        self.updateTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.path))
        pass


class FolderView(AuthMethodView):
    routePath = "/zip"

    async def head(self, request: Request):
        """
        文件夹打包
        """
        try:
            args = self.usable_args(request)
            filePath = args.get("path")
            if os.path.isfile(filePath):
                raise Exception("该方法不支持文件")
            timeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            fileName = "{}_{}.zip".format(os.path.basename(filePath), timeStr)
            # cache:Cache= request.app.ctx.Cache
            # uid=uuid.uuid4()
            # cache.add(uid,fileName)
            zipFilePath = os.path.join('.', fileName)
            await self.zip_directory(filePath, zipFilePath)
            id = request.headers.get("session")
            request.app.ctx.data = {id: {filePath: zipFilePath}}
            return await self.response_size(zipFilePath)
        except Exception as e:
            return self.response_json(Result.fail("压缩文件出错:{}".format(e)))

    async def get(self, request: Request):
        try:
            args = self.usable_args(request)
            key = args.get("path")
            sessionId = request.headers.get("session")
            filePath = request.app.ctx.data[sessionId].get(key)
            _, end, file_size = self.parseRange(request, filePath=filePath)
            return await self.get_file_partial(request, filePath)
        finally:
            if filePath != None and os.path.exists(filePath) and file_size-1 == end:
                # log.warn("删除文件.", filePath)
                os.remove(filePath)
                # os.unlink(zipFilePath)
                cache: dict = request.app.ctx.data[sessionId]
                log.warn(cache, key, cache.keys)
                if key in cache:
                    cache.pop(key)
                if {} == cache:
                    cache: dict = request.app.ctx.data
                    if sessionId in cache:
                        cache.pop(sessionId)


class FileViews(AuthMethodView):

    async def head(self, request: Request):
        """
        文件或目录大小
        """
        args = self.usable_args(request)
        filePath = args.get("path")
        return await self.response_size(filePath)

    async def get(self, request: Request):
        """
        下载文件
        """
        args = self.usable_args(request)
        filePath = args.get("path")
        if os.path.isdir(filePath):
            raise ValueError("该方法不支持文件夹下载")
        return await self.get_file_partial(request, filePath)

    async def post(self, request: Request):
        """
        列表
        """
        param = FileParam()
        param.__dict__.update(request.json)
        if param.root == None:
            param.root = "/"
        if param.root.endswith(":"):
            param.root = param.root+os.sep

        def filter(x): return param.name == None or param.name in x
        list = os.listdir(param.root)
        result = []
        for s in list:
            if filter(s):
                folder = File(param.root, s)
                result.append(folder)
        return self.response_json(Result.success({"root": param.root, "res": result}))

    async def delete(self, request: Request):
        args = self.usable_args(request)
        filePath = args.get("path")
        if not os.path.exists(filePath):
            return self.response_json(Result.success(message=f"路径：{filePath},不存在！"))
        fileService.delFileOrFolder(filePath)
        return self.response_json(Result.success(message=f"删除'{filePath}'完成！"))

    async def put(self, request: Request):
        # 创建一个临时文件用于保存上传的数据
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # 定义一个异步生成器来处理文件流
            async def process_data(stream):
                async for data in stream:
                    temp_file.write(data)

            # 调用 request.stream 并传入生成器
            await request.stream(process_data)
            # 这里可以添加更多处理逻辑，比如保存文件到永久位置等
            return self.response_json(Result.success())

        finally:
            # 确保无论如何都会执行的清理代码
            temp_file.close()
            # 如果需要，在这里删除临时文件
            os.unlink(temp_file.name)  # 删除临时文件
