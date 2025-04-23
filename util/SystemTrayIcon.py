import logging
from pystray import Icon as PystrayIcon, Menu as PystrayMenu, MenuItem as PystrayMenuItem
from PIL import Image
from util.Util import run_in_thread
from util.settingGUI import settingsGUI


class SystemTrayIcon:
    def __init__(self, settingsGUI: settingsGUI, start_webuiFunc, stop_webuiFunc, image_path='./icon.png'):
        self.icon_image = Image.open(image_path)
        self.settingsGUI = settingsGUI
        self.start_webuiFunc = start_webuiFunc
        self.stop_webuiFunc = stop_webuiFunc
        self.icon = PystrayIcon('keyboardControlMouse', self.icon_image,
                                'keyboardControlMouse', self.create_menu('start webui'))

    def create_menu(self, action):
        if action == 'start webui':
            return PystrayMenu(
                PystrayMenuItem('settings', action=self.settingsGUI.open_settings_gui),
                PystrayMenuItem('start webui', action=self.on_start_webui),
                PystrayMenuItem('exit', action=self.on_exit),
            )
        elif action == 'stop webui':
            return PystrayMenu(
                PystrayMenuItem('settings', action=self.settingsGUI.open_settings_gui),
                PystrayMenuItem('stop webui', action=self.on_stop_webui),
                PystrayMenuItem('exit', action=self.on_exit),
            )

    @run_in_thread
    def start(self, extra_execution_function=[]):
        self.icon.run()
        for func in extra_execution_function:
            func()

    def on_start_webui(self):
        self.start_webuiFunc()
        self.icon.menu = self.create_menu('stop webui')

    def on_stop_webui(self):
        self.stop_webuiFunc()
        self.icon.menu = self.create_menu('start webui')

    def on_exit(self):
        logging.debug('exit触发')
        self.icon.stop()

    def change_icon(self, image):
        """
        改变任务栏图标
        """
        self.icon.icon = image