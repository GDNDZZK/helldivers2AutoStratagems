import os

from util.globalHotKeyManager import GlobalHotKeyManager, vk_to_key_str
from util.loadSetting import saveConfigDict
from util.imageProcessing import capture_screenshot, crop_image, resize_image

from PyQt6.QtWidgets import QApplication, QWidget, QDoubleSpinBox, QLabel, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtGui import QKeyEvent, QColor, QPainter, QBrush, QPen, QDesktopServices
from PyQt6.QtCore import Qt, QPoint, QUrl


class resizePanel(QWidget):

    border_color = QColor(0, 120, 215, 255)
    border_width = 4
    corner_radius = 10
    min_w, min_h = 100, 60

    resizing = False
    resize_corner = False
    drag_position = None

    def __init__(self, parent, x, y, w, h):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(max(self.min_w, w), max(self.min_h, h))
        self.move(x, y)

        self.drag_position = QPoint()

        self.save_button = QPushButton("保存", self)
        self.save_button.setFixedSize(80, 40)
        self.save_button.clicked.connect(parent.onResizeSaved)
        self.save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3399FF;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007ACC;
            }
            """
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 120, 215, 60)))
        painter.setPen(QPen(self.border_color, self.border_width))

        rect = self.rect().adjusted(
            self.border_width, self.border_width,
            -self.border_width, -self.border_width
        )
        painter.drawRoundedRect(rect, self.corner_radius, self.corner_radius)

    def resizeEvent(self, event):
        padding = 10
        self.save_button.move(
            self.width() - self.save_button.width() - padding,
            self.height() - self.save_button.height() - padding
        )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.resizing = True
        pos = event.position().toPoint()
        half_w = self.width() // 2
        half_h = self.height() // 2

        if pos.x() > half_w and pos.y() > half_h:
            self.resize_corner = True
        else:
            self.window().windowHandle().startSystemMove()

        self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.resizing:
            return

        current_pos = event.globalPosition().toPoint()
        delta = current_pos - self.drag_position

        new_w = self.geometry().width()
        new_h = self.geometry().height()
        if self.resize_corner:
            new_w += delta.x()
            new_h += delta.y()


        self.resize(max(self.min_w, new_w), max(self.min_h, new_h))
        self.drag_position = current_pos

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None


class settingPanel(QWidget):

    qApp = None
    config = None
    keyMgr = None

    save_button = None

    delay_min_spinbox = None
    delay_max_spinbox = None

    keybind_button = None
    keybind_label = None
    onGettingKeys = False
    #TODO: for multi key support
    #onHoldKeys = []

    resize_button = None
    resize_test_button = None
    overlay = None
    size_x_spinbox = None
    size_y_spinbox = None
    size_w_spinbox = None
    size_h_spinbox = None

    def __init__(self, qApp, config: dict, hotkeyManager: GlobalHotKeyManager):
        super().__init__()

        self.qApp = qApp
        self.config = config
        self.keyMgr = hotkeyManager

        self.setFixedSize(200, 300)

        # save button #

        self.save_button = QPushButton("保存", self)
        self.save_button.setGeometry(10, 260, 180, 30)

        self.save_button.clicked.connect(self.onSaveButtonCliecked)

        # save button end #

        # spinbox #

        def createSpinbox_delay(label, h):
            delay_label = QLabel(label, self)
            delay_label.setGeometry(10, h, 100, 30)

            delay_spinbox = QDoubleSpinBox(self)
            delay_spinbox.setGeometry(110, h, 80, 30)

            delay_spinbox.setRange(0.0, 100.0)
            delay_spinbox.setDecimals(2)
            delay_spinbox.setSingleStep(0.01)

            return delay_spinbox

        # DELAY_MIN #

        self.delay_min_spinbox = createSpinbox_delay("最小延迟 (秒):", 10)
        self.delay_min_spinbox.setValue(float(self.config.get("DELAY_MIN", "0.05")))

        # DELAY_MAX

        self.delay_max_spinbox = createSpinbox_delay("最大延迟 (秒):", 40)
        self.delay_max_spinbox.setValue(float(self.config.get("DELAY_MAX", "0.1")))

        # spinbox end #

        # keybind #

        self.keybind_button = QPushButton("更改按键", self)
        self.keybind_button.setGeometry(110, 80, 80, 30)
        self.keybind_button.clicked.connect(self.onKeybindButtonCliecked)

        self.keybind_label = QTextEdit(self)
        self.keybind_label.setGeometry(10, 80, 90, 30)
        self.keybind_label.setReadOnly(True)
        self.keybind_label.setPlainText(self.config.get("ACTIVATION", "<ctrl>"))

        # keybind end #

        # resize panel #

        def createSpinbox_resizePanel(label, h, first):
            delay_label = QLabel(label, self)
            if first:
                delay_label.setGeometry(10, h, 20, 30)
            else:
                delay_label.setGeometry(105, h, 20, 30)

            delay_spinbox = QDoubleSpinBox(self)
            if first:
                delay_spinbox.setGeometry(40, h, 55, 30)
            else:
                delay_spinbox.setGeometry(135, h, 55, 30)

            delay_spinbox.setRange(0.0, 99999.0)
            delay_spinbox.setDecimals(0)
            delay_spinbox.setSingleStep(1)

            return delay_spinbox

        resize_label = QLabel("========  识别区域设置  ========", self)
        resize_label.setGeometry(10, 120, 180, 30)
        resize_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.size_x_spinbox = createSpinbox_resizePanel( "左:", 150, True )
        self.size_x_spinbox.setValue(float(self.config.get("LEFT", "30")))

        self.size_y_spinbox = createSpinbox_resizePanel( "上:", 185, True )
        self.size_y_spinbox.setValue(float(self.config.get("TOP", "20")))

        self.size_w_spinbox = createSpinbox_resizePanel( "右:", 150, False )
        self.size_w_spinbox.setValue(float(self.config.get("RIGHT", "220")))

        self.size_h_spinbox = createSpinbox_resizePanel( "下:", 185, False )
        self.size_h_spinbox.setValue(float(self.config.get("BOTTOM", "400")))

        self.resize_button = QPushButton("交互式更改", self)
        self.resize_button.setGeometry(10, 220, 85, 30)
        self.resize_button.clicked.connect(self.onResizeButtonCliecked)

        self.resize_test_button = QPushButton("截图测试", self)
        self.resize_test_button.setGeometry(105, 220, 85, 30)
        self.resize_test_button.clicked.connect(self.onResizeTestButtonCliecked)

        # resize panel end #


    # save button #
    def onSaveButtonCliecked(self):

        newConfig = {
            "DELAY_MIN": self.delay_min_spinbox.value(),
            "DELAY_MAX": self.delay_max_spinbox.value(),
            "ACTIVATION": self.keybind_label.toPlainText(),

            "LEFT": self.size_x_spinbox.value(),
            "TOP": self.size_y_spinbox.value(),
            "RIGHT": self.size_w_spinbox.value(),
            "BOTTOM": self.size_h_spinbox.value()
        }

        saveConfigDict(newConfig)
        self.close()
    # save button end #

    # keybind #
    def onKeybindButtonCliecked(self):
        #TODO: for multi key support
        # defensive fix
        #self.onHoldKeys = []
        self.grabKeyboard()
        self.onGettingKeys = True

    def keyPressEvent(self, event: QKeyEvent):
        if(not self.onGettingKeys):
            super().keyPressEvent(event)
            return

        key = event.nativeVirtualKey()
        self.keybind_label.setPlainText(vk_to_key_str(key))

        #TODO: for multi key support
        #self.onHoldKeys.append(key)
        #self.keybind_label.setPlainText(vks_to_key_str(self.onHoldKeys))
    def keyReleaseEvent(self, event: QKeyEvent):
        if(not self.onGettingKeys):
            super().keyReleaseEvent(event)
            return

        #TODO: for multi key support
        #self.onHoldKeys = []
        self.releaseKeyboard()
        self.onGettingKeys = False
    # keybind end #

    # resize panel #
    def onResizeTestButtonCliecked(self):
        path = './temp/gui_resize_test_screenshot.png'
        config = {
            "LEFT": self.size_x_spinbox.value(),
            "TOP": self.size_y_spinbox.value(),
            "RIGHT": self.size_w_spinbox.value(),
            "BOTTOM": self.size_h_spinbox.value()
        }

        capture_screenshot(path)
        resize_image(path,path)
        crop_image(path,path,config=config)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def onResizeButtonCliecked(self):

        # EDIT: well we just find out that this software can not even run on wayland, and this tips is useless now
        # can not get overlayWindow`s position at wayland environment, so this feat is fucked on wayland
        #if os.environ.get('WAYLAND_DISPLAY') is not None:
        #    QMessageBox.critical(self, 'Error', 'Wayland环境下无法使用此功能', QMessageBox.StandardButton.Ok)
        #    return

        self.hide()


        x, y, w, h = int(self.size_x_spinbox.value()), int(self.size_y_spinbox.value()), int(self.size_w_spinbox.value()), int(self.size_h_spinbox.value())

        screen_size = self.qApp.primaryScreen().size()
        sw, sh = screen_size.width(), screen_size.height()
        # reverse imageProcessing format
        x, y = self.reverse_scale_coordinate((sw, sh), (x, y))
        w, h = self.reverse_scale_coordinate((sw, sh), (w, h))
        # make absolute position to window size
        w, h = w - x, h - y

        self.overlay = resizePanel(self, int(x), int(y), int(w), int(h))
        self.overlay.show()

    def onResizeSaved(self):
        x, y, w, h = self.overlay.geometry().getRect()
        # change window size to absolute position
        w, h = x + w, y + h # type: ignore

        # EDIT: haha i cant fix that, no help at all
        # linux wayland desktop defensive fix, fucking wayland destroy everything
        #if x == 0 and y == 0:
        #    point = self.overlay.windowHandle().screen().geometry().topLeft()
        #    x = point.x()
        #    y = point.y()
        #    print("wayland defensive fix, x value:"+ str(x) +" y value:"+ str(y))

        screen_size = self.qApp.primaryScreen().size()
        sw, sh = screen_size.width(), screen_size.height()
        # scale the to same format with imageProcessing
        x, y = self.scale_coordinate((sw, sh), (x, y))
        w, h = self.scale_coordinate((sw, sh), (w, h))

        self.size_x_spinbox.setValue(x)
        self.size_y_spinbox.setValue(y)
        self.size_w_spinbox.setValue(w)
        self.size_h_spinbox.setValue(h)

        self.overlay.close()
        self.show()

    # scale the to same format with imageProcessing
    def scale_coordinate(self, original_resolution, original_point):
        original_width, original_height = original_resolution
        if original_height == 0:
            raise ValueError("Original height cannot be zero")
        scale = 720 / original_height
        new_x = original_point[0] * scale
        new_y = original_point[1] * scale
        return (new_x, new_y)

    # reverse imageProcessing format
    def reverse_scale_coordinate(self, original_resolution, scaled_point):
        original_width, original_height = original_resolution
        if original_height == 0:
            raise ValueError("Original height cannot be zero")
        scale = 720 / original_height
        original_x = scaled_point[0] / scale
        original_y = scaled_point[1] / scale
        return (original_x, original_y)
    # resize panel end #

# class from old tkGui(early nuked), im too lazy so i didnt change the api format #

class settingsGUI:

    app = None
    window = None

    def __init__(self, config: dict, hotkeyManager: GlobalHotKeyManager):
        app = QApplication([])
        self.app = app

        window = settingPanel(app, config, hotkeyManager)
        self.window = window

    def open_settings_gui(self):
        self.window.show()

        if os.environ.get('WAYLAND_DISPLAY') is not None:
            QMessageBox.critical(self.window, 'Error', '此软件无法在Wayland环境下使用\n详见：\nhttps://github.com/BoboTiG/python-mss/issues/155', QMessageBox.StandardButton.Ok)

        self.app.exec()
