
from sanic import Request
from sanic.response import file
from . import resource_baseView


class Image_View(resource_baseView):
    routePath = "/img"

    async def get(self, request: Request):
        """
        显示图片
        """
        fullPath = await self.getLocalPath(request)
        return await file(fullPath, mime_type="image/jpeg")


class Video_View(resource_baseView):
    routePath = "/video"

    async def get(self, request: Request):
        """
        显示视频文件
        """
        fullPath = await self.getLocalPath(request)
        return await file(fullPath, mime_type="image/jpeg")


class thumbnail_View(resource_baseView):
    routePath = "/thumbnail/<w:int>/<h:int>"

    async def get(self, request: Request, w: int = 208, h: int = 117):
        """
        略缩图
        """
        fullPath = await self.getLocalPath(request)
        return await self.screenshot_image(fullPath, w, h)


class Poster_View(resource_baseView):
    routePath = "/poster/<w:int>/<h:int>"

    async def get(self, request: Request, w: int = 208, h: int = 117):
        """
        视频截图
        视频第一帧作为 poster
        未使用可能需要
        """
        fullPath = await self.getLocalPath(request)
        return await self.screenshot(fullPath, w, h)
