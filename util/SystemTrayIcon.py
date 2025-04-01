from pystray import Icon as PystrayIcon, Menu as PystrayMenu, MenuItem as PystrayMenuItem
from PIL import Image


class SystemTrayIcon:
    def __init__(self, image_path='./icon.png'):
        self.icon_image = Image.open(image_path)
        self.menu = PystrayMenu(
            PystrayMenuItem('exit', action=self.on_exit),
        )

    def start(self):
        self.icon = PystrayIcon('keyboardControlMouse', self.icon_image,
                                'keyboardControlMouse', self.menu)
        self.icon.run()

    def on_exit(self):
        print('exit触发')
        self.icon.stop()

    def change_icon(self, image):
        """
        改变任务栏图标
        """
        self.icon.icon = image