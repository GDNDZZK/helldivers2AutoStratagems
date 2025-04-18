import logging
from pystray import Icon as PystrayIcon, Menu as PystrayMenu, MenuItem as PystrayMenuItem
from PIL import Image
from util.Util import run_in_thread


class SystemTrayIcon:
    def __init__(self, openSettingFunc, image_path='./icon.png'):
        self.icon_image = Image.open(image_path)
        self.menu = PystrayMenu(
            PystrayMenuItem('settings', action=openSettingFunc),
            PystrayMenuItem('exit', action=self.on_exit),
        )

    @run_in_thread
    def start(self,extra_execution_function=[]):
        self.icon = PystrayIcon('keyboardControlMouse', self.icon_image,
                                'keyboardControlMouse', self.menu)
        self.icon.run()
        for func in extra_execution_function:
            func()

    def on_exit(self):
        logging.debug('exit触发')
        self.icon.stop()

    def change_icon(self, image):
        """
        改变任务栏图标
        """
        self.icon.icon = image