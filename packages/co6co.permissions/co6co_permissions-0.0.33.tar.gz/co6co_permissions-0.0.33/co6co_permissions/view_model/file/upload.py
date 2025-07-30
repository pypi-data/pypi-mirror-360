
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from ..base_view import AuthMethodView
from ...model.filters.file_param import FileParam
import os
from co6co.utils import log
import tempfile
from sanic.request.form import File
from co6co.utils.hash import str_md5


def getTempFileName(folder: str, fileName: str):
    """
    获取临时文件名
    """
    fullPath = os.path.join(folder, fileName)
    return str_md5(fullPath)


def merge_chunks(savePath: str, file_name: str, total_chunks: int):
    """
    合并文件块
    """
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    output_file_path = os.path.join(savePath, file_name)
    tempFileName = getTempFileName(savePath, file_name)
    with open(output_file_path, 'wb') as output_file:
        for i in range(1, total_chunks + 1):
            temp_file_path = os.path.join(tempfile.gettempdir(), f'{tempFileName}_part{i}')
            with open(temp_file_path, 'rb') as temp_file:
                output_file.write(temp_file.read())
            os.remove(temp_file_path)  # 删除临时文件


class UploadQueryView(AuthMethodView):
    routePath = "/upload/query"

    async def post(self, request: Request):
        """
        查询已上传的文件块
        {fileName:xxx.xx,totalChunks:1000}
        """
        params: dict = request.json
        fileName: str = params.get("fileName", None)
        totalChunks = params.get("totalChunks", None)
        uploadPath = params.get("uploadPath", None)
        if not fileName:
            return self.response_json(Result.fail(message="缺少文件名"))
        if not totalChunks:
            return self.response_json(Result.fail(message="缺少totalChunks"))
        totalChunks = int(totalChunks)
        uploaded_chunks = []
        tempFileName = getTempFileName(uploadPath, fileName)
        for i in range(1, totalChunks+1):
            temp_file_path = os.path.join(tempfile.gettempdir(), f'{tempFileName}_part{i}')
            if os.path.exists(temp_file_path):
                uploaded_chunks.append(i)
            else:
                break
        finshed = len(uploaded_chunks) == totalChunks
        if finshed:
            merge_chunks(uploadPath, fileName, totalChunks)
        return self.response_json(Result.success({'uploadedChunks': uploaded_chunks, "finshed": finshed}))


class UploadView(AuthMethodView):
    routePath = "/upload"

    async def put(self, request: Request):
        """
        上传 chunk
        index: 从1开始
        """
        try:
            file: File = request.files.get('file')
            index = int(request.form.get('index'))
            total_chunks = int(request.form.get('totalChunks'))
            file_name = request.form.get('fileName')
            uploadPath = request.form.get('uploadPath')
            if not file or not file_name:
                return self.response_json(Result.fail(message="缺少文件名"))
            tempFileName = getTempFileName(uploadPath, file_name)
            # 保存文件块到临时目录
            temp_file_path = os.path.join(tempfile.gettempdir(), f'{tempFileName}_part{index}')
            await self.save_file(file, temp_file_path)

            # 检查是否所有块都已上传
            if index == total_chunks:
                merge_chunks(uploadPath, file_name, total_chunks)

            return self.response_json(Result.success(message="文件块上传成功"))
        except Exception as e:
            return self.response_json(Result.fail(message="文件块上传失败{}".format(e)))
