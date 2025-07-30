from sanic.request import Request
from typing import List, Dict
from co6co.utils import log
from .authonCache import AuthonCacheManage


class apiPermissionCheck:
    request: Request = None
    currentUserMenus: List[Dict] = None
    inited: bool = False

    def __init__(self, request: Request) -> None:
        self.request = request
        pass
    # 协调函数

    async def init(self):
        """
        初始化
        """
        cacheManage = AuthonCacheManage(self.request)
        allMenuData = await cacheManage.menuData
        currentUserRoles = await cacheManage.currentRoles
        self.currentUserMenus = []
        [self.currentUserMenus.append(m) for m in allMenuData if m.get("roleId") in currentUserRoles and m.get("id") not in map(lambda m: m['id'], self.currentUserMenus)]
        self.inited = True
    # def __await__(self):
        # 需要生成器对对象
        # allMenuData= yield from  cacheManage.menuData

    def check(self) -> bool:
        if not self.inited:
            log.err("未初始化.")
            return False
        for menu in self.currentUserMenus:
            if self._check(menu):
                return True
        return False

    def _check(self, menu: Dict):
        url: str = menu["url"]
        path = self.request.path
        method = self.request.method
        methods: str = menu["methods"]
        methods: list = methods.split(",")
        if method not in methods and "ALL" not in methods:
            return False
        pathArr = path.split("/")
        if "**" in url:
            url = url[0:url.index("**")]
            urlArr = url.split("/")
            # log.warn(pathArr,urlArr)
            if len(pathArr) >= len(urlArr)-1 and pathArr[0:len(urlArr)-1] == urlArr[0: len(urlArr)-1]:
                return True
        if "*" in url:
            url = url[0:url.index("*")]
            urlArr = url.split("/")
            log.warn(pathArr, urlArr)
            if (len(pathArr) == len(urlArr) or len(pathArr) == len(urlArr)-1) and pathArr[0:len(urlArr)-1] == urlArr[0: len(urlArr)-1]:
                return True
        if url == path:
            return True
        return False
