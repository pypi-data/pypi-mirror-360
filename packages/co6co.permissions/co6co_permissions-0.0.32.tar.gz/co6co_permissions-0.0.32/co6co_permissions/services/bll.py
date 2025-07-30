import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from co6co_db_ext.db_session import db_service
import asyncio
from sanic import Sanic
from co6co.task.thread import ThreadEvent
from co6co.utils import log
from sqlalchemy import text


class baseBll:
    session: AsyncSession = None
 
    def __init__(self, db_settings: dict) -> None:
        _service: db_service = db_service(db_settings)
        self.session: AsyncSession = _service.async_session_factory() 
        self.service=_service
        self.isClose=False
        '''
        service:db_service=app.ctx.service
        self.session:AsyncSession=service.async_session_factory()
        '''
        # log.warn(f"..创建session。。")
        pass
    async def close(self):
        #log.log("等待关闭。。。",type(self.session))
        self.isClose=True 
        await self.session.close() 
        await self.service.engine.dispose()
        #log.log("关闭ed")
        pass
    def __del__(self) -> None: 
        if not self.isClose :
            loop= asyncio.get_running_loop() 
            loop.create_task(self.close())  
            #log.succ(f"会在close之前执行 {self}...关闭session",'done->',task.done(),"canceled->",task.cancelled())
             

    def __repr__(self) -> str:
        return f'{self.__class__}'


class BaseBll(baseBll): 
    def __init__(self,*,  db_settings: dict={},app:Sanic=None) -> None: 
        self.t = ThreadEvent() 
        if not db_settings:
            app =app or Sanic.get_app()
            db_settings=app.config.db_settings 
        super().__init__(db_settings)

    def run(self, task, *args, **argkv):
        data = self.t.runTask(task, *args, **argkv)
        return data
    def __str__(self):
        return f'{self.__class__}'

    def __del__(self) -> None:
        try: 
            if not self.isClose: 
                self.t.runTask(self.close) 
            self.t.close()  
        except Exception as e:
            log.warn("__del___ error",e)
            pass
