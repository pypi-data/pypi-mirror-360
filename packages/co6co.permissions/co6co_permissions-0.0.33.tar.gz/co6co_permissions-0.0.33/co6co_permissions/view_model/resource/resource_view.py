
from sanic import Request
from sanic.response import file
from . import resource_baseView


class Res_Image_View(resource_baseView):
    routePath = "/img/<pk:int>"

    async def get(self, request: Request, pk: int):
        """
        显示图片
        """
        fullPath = await self.getLocalPathById(request, pk)
        return await file(fullPath, mime_type="image/jpeg")


class Res_Video_View(resource_baseView):
    routePath = "/video/<pk:int>"

    async def get(self, request: Request, pk: int):
        """
        显示视频文件
        """
        fullPath = await self.getLocalPathById(request, pk)
        return await file(fullPath, mime_type="image/jpeg")


class Res_thumbnail_View(resource_baseView):
    routePath = "/img/thumbnail/<pk:int>/<w:int>/<h:int>"

    async def get(self, request: Request, pk: int, w: int = 208, h: int = 117):
        """
        略缩图
        """
        fullPath = await self.getLocalPathById(request, pk)
        return await self.screenshot_image(fullPath, w, h)


class Res_Poster_View(resource_baseView):
    routePath = "/video/poster/<pk:int>/<w:int>/<h:int>"

    async def get(self, request: Request, pk: int, w: int = 208, h: int = 117):
        """
        视频截图
        视频第一帧作为 poster
        未使用可能需要
        """
        fullPath = await self.getLocalPathById(request, pk)
        return await self.screenshot(fullPath, w, h)
