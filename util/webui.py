import os
import threading
import time

from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI

from util.loadSetting import getConfigDict

class FastAPIServer:
    def __init__(self):
        # 创建 FastAPI 应用
        self.app = FastAPI()
        self.app.mount("/static/", StaticFiles(directory="./static"), name="static")

        @self.app.get("/test")
        async def test():
            return "OK"

        # 定义 / 路由，返回 index.html
        @self.app.get("/")
        async def index():
            return RedirectResponse(url="index.html")

        @self.app.get("/index.html")
        async def index_html():
            return RedirectResponse(url="static/index.html")

        @self.app.get("/favicon.ico")
        async def favicon():
            return RedirectResponse("static/favicon.ico")

        # 服务器实例和线程引用
        self._server = None
        self._thread = None

    def start(self):
        """
        启动服务
        如果已经启动,则不重复启动
        """
        config_dict = getConfigDict()
        if self._server is not None and self._thread is not None and self._thread.is_alive():
            print(
                f"Server is already running on port {self._server.config.port}")
            return

        # 配置 uvicorn
        config = uvicorn.Config(
            app=self.app,
            host=config_dict['WEB_GUI_HOST'],
            port=int(float(config_dict['WEB_GUI_PORT'])),
            log_level="info",
            lifespan="on",
        )
        self._server = uvicorn.Server(config)

        # 在独立线程中运行
        def _run():
            self._server.run()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

        # 等待服务器启动
        while not self._server.started:
            time.sleep(0.01)
        print(f"Server started on {config_dict['WEB_GUI_HOST']}:{int(float(config_dict['WEB_GUI_PORT']))}")

    def stop(self):
        """
        关闭服务，释放资源
        关闭后可再次 start
        """
        if self._server is None:
            print("Server is not running.")
            return

        # 通知服务器退出
        self._server.should_exit = True
        # 等待线程结束
        if self._thread is not None:
            self._thread.join()

        print("Server stopped.")

        # 重置引用，允许再次启动
        self._server = None
        self._thread = None
