import os

from util.globalHotKeyManager import GlobalHotKeyManager, vk_to_key_str
from util.loadSetting import saveConfigDict, getConfigDict, getDefaultConfigDict
from util.imageProcessing import capture_screenshot, crop_image, resize_image

from PyQt6.QtWidgets import QApplication, QWidget, QDoubleSpinBox, QLabel, QPushButton, QTextEdit, QMessageBox, QCheckBox
from PyQt6.QtGui import QKeyEvent, QColor, QPainter, QBrush, QPen, QDesktopServices
from PyQt6.QtCore import Qt, QPoint, QUrl, QTimer


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
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMouseTracking(True)

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

        # cursor shape change
        pos = event.position().toPoint()
        half_w = self.width() // 2
        half_h = self.height() // 2

        shouldSetCursor = True
        # cursor not on resize place
        if pos.x() <= half_w or pos.y() <= half_h:
            shouldSetCursor = False
        # cursor on the save button
        if self.save_button.geometry().contains(pos):
            shouldSetCursor = False
        # should always keep resize cursor shape when resizing
        if self.resizing:
            shouldSetCursor = True

        if shouldSetCursor:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # window resize
        if not self.resizing or not self.resize_corner:
            return

        current_pos = event.globalPosition().toPoint()
        delta = current_pos - self.drag_position

        new_w = self.width() + delta.x()
        new_h = self.height() + delta.y()

        self.resize(max(self.min_w, new_w), max(self.min_h, new_h))
        self.drag_position = current_pos

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None


class settingPanel(QWidget):

    qApp = None
    config = None

    reset_button = None

    save_button = None

    start_with_program_checkbox = None

    manual_edit_button = None

    delay_min_spinbox = None
    delay_max_spinbox = None

    keybind_button = None
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

        self.setFixedSize(200, 350)

        self.initWidgets()

    def initWidgets(self):

        # reset button #

        self.save_button = QPushButton("重置所有设置", self)
        self.save_button.setGeometry(10, 310, 85, 30)
        self.save_button.setStyleSheet("color: red;")

        self.save_button.clicked.connect(self.onResetButtonCliecked)

        # reset button end #

        # save button #

        self.save_button = QPushButton("保存所有设置", self)
        self.save_button.setGeometry(105, 310, 85, 30)

        self.save_button.clicked.connect(self.onSaveButtonCliecked)

        # save button end #

        # start with program #

        self.start_with_program_checkbox = QCheckBox("允许设置面板随程序开启", self)
        self.start_with_program_checkbox.setGeometry(10, 250, 180, 20)
        self.start_with_program_checkbox.setChecked(bool(int(self.config.get("START_GUI_WITH_PROGRAM", ""))))
        # this checkbox state will be saved when save button cliecked

        # start with program end #

        # manual edit button #

        self.manual_edit_button = QPushButton("（高级）手动编辑配置文件", self)
        self.manual_edit_button.setGeometry(10, 275, 180, 30)

        # manual edit button end #

        # spinbox #

        def createSpinbox_delay(label, h):
            delay_label = QLabel(label, self)
            delay_label.setGeometry(10, h, 120, 30)

            delay_spinbox = QDoubleSpinBox(self)
            delay_spinbox.setGeometry(130, h, 60, 30)

            delay_spinbox.setRange(0.0, 100.0)
            delay_spinbox.setDecimals(3)
            delay_spinbox.setSingleStep(0.001)

            return delay_spinbox

        # DELAY_MIN #

        self.delay_min_spinbox = createSpinbox_delay("按键随机最小延迟(s):", 10)
        self.delay_min_spinbox.setValue(float(self.config.get("DELAY_MIN", "")))

        # DELAY_MAX #

        self.delay_max_spinbox = createSpinbox_delay("按键随机最大延迟(s):", 40)
        self.delay_max_spinbox.setValue(float(self.config.get("DELAY_MAX", "")))

        # spinbox end #

        # keybind #

        self.keybind_button = QPushButton("配置键盘快捷键", self)
        self.keybind_button.setGeometry(10, 75, 180, 30)
        self.keybind_button.clicked.connect(self.onKeybindButtonCliecked)

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
                delay_spinbox.setGeometry(35, h, 60, 30)
            else:
                delay_spinbox.setGeometry(130, h, 60, 30)

            delay_spinbox.setRange(0.0, 99999.0)
            delay_spinbox.setDecimals(0)
            delay_spinbox.setSingleStep(1)

            return delay_spinbox

        resize_label = QLabel("========  识别区域设置  ========", self)
        resize_label.setGeometry(10, 110, 180, 25)
        resize_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.size_x_spinbox = createSpinbox_resizePanel( "左:", 135, True )
        self.size_x_spinbox.setValue(float(self.config.get("LEFT", "")))

        self.size_y_spinbox = createSpinbox_resizePanel( "上:", 165, True )
        self.size_y_spinbox.setValue(float(self.config.get("TOP", "")))

        self.size_w_spinbox = createSpinbox_resizePanel( "右:", 135, False )
        self.size_w_spinbox.setValue(float(self.config.get("RIGHT", "")))

        self.size_h_spinbox = createSpinbox_resizePanel( "下:", 165, False )
        self.size_h_spinbox.setValue(float(self.config.get("BOTTOM", "")))

        self.resize_button = QPushButton("交互式更改", self)
        self.resize_button.setGeometry(10, 200, 85, 30)
        self.resize_button.clicked.connect(self.onResizeButtonCliecked)

        self.resize_test_button = QPushButton("截图测试", self)
        self.resize_test_button.setGeometry(105, 200, 85, 30)
        self.resize_test_button.clicked.connect(self.onResizeTestButtonCliecked)

        # resize panel end #


    # reset button #
    def onResetButtonCliecked(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("二次确认")
        message_box.setText("你正在执行的操作：重置所有设置<br/><font color='red'>警告：此操作不可逆</font>")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        message_box.button(QMessageBox.StandardButton.Yes).setText("确认")
        message_box.button(QMessageBox.StandardButton.No).setText("取消")
        message_box.setIcon(QMessageBox.Icon.Warning)

        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.No:
            return


        saveConfigDict(getDefaultConfigDict())
        self.config = getConfigDict()

        # delete all Widgets and reinit them, so i dont need to change the widgets value one by one
        self.hide()

        for child in self.findChildren(QWidget):
            child.deleteLater()
        self.initWidgets()

        self.show()
    # reset button end #

    # save button #
    def onSaveButtonCliecked(self):

        newConfig = {
            "DELAY_MIN": self.delay_min_spinbox.value(),
            "DELAY_MAX": self.delay_max_spinbox.value(),
            #"ACTIVATION": self.keybind_label.toPlainText(),

            "LEFT": self.size_x_spinbox.value(),
            "TOP": self.size_y_spinbox.value(),
            "RIGHT": self.size_w_spinbox.value(),
            "BOTTOM": self.size_h_spinbox.value(),

            "START_GUI_WITH_PROGRAM": "1" if self.start_with_program_checkbox.isChecked() else "0"
        }

        saveConfigDict(newConfig)
        self.config = getConfigDict()

        self.close()
    # save button end #

    # manual edit button #
    def onManualEditButtonCliecked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile('./config.ini'))
        # wait for a while to let QDesktopServices finish his job
        QTimer.singleShot(1000, self.close)
    # manual edit button end #

    # keybind #
    def onKeybindButtonCliecked(self):
        return

    """
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
    """
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
        # can not get overlayWindow position at wayland environment, so this feat is fucked on wayland
        #if os.environ.get('WAYLAND_DISPLAY') is not None:
        #    QMessageBox.critical(self, 'Error', 'Wayland环境下无法使用此功能', QMessageBox.StandardButton.Ok)
        #    return

        self.hide()


        x, y, w, h = int(self.size_x_spinbox.value()), int(self.size_y_spinbox.value()), int(self.size_w_spinbox.value()), int(self.size_h_spinbox.value())

        screen_size = self.qApp.primaryScreen().size()
        sw, sh = screen_size.width(), screen_size.height()
        # convert imageProcessing format to absolute position
        x, y = self.reverse_scale_coordinate((sw, sh), (x, y))
        w, h = self.reverse_scale_coordinate((sw, sh), (w, h))
        # make absolute position to window size
        w, h = w - x, h - y

        self.overlay = resizePanel(self, int(x), int(y), int(w), int(h))
        self.overlay.destroyed.connect(self.onOverlayWindowDestroyed)
        self.overlay.show()

    def onResizeSaved(self):
        x, y, w, h = self.overlay.geometry().getRect()
        # change window size to absolute position
        w, h = x + w, y + h

        # EDIT: haha i cant fix that, no help at all
        # linux wayland desktop defensive fix, fucking wayland destroy everything
        #if x == 0 and y == 0:
        #    point = self.overlay.windowHandle().screen().geometry().topLeft()
        #    x = point.x()
        #    y = point.y()
        #    print("wayland defensive fix, x value:"+ str(x) +" y value:"+ str(y))

        screen_size = self.qApp.primaryScreen().size()
        sw, sh = screen_size.width(), screen_size.height()
        # scale to same format with imageProcessing
        x, y = self.scale_coordinate((sw, sh), (x, y))
        w, h = self.scale_coordinate((sw, sh), (w, h))

        self.size_x_spinbox.setValue(x)
        self.size_y_spinbox.setValue(y)
        self.size_w_spinbox.setValue(w)
        self.size_h_spinbox.setValue(h)

        self.overlay.close()

    def onOverlayWindowDestroyed(self):
        if self.isVisible():
            return
        self.show()

    # scale to same format with imageProcessing
    def scale_coordinate(self, original_resolution, original_point):
        original_width, original_height = original_resolution
        if original_height == 0:
            raise ValueError("Original height cannot be zero")
        scale = 720 / original_height
        new_x = original_point[0] * scale
        new_y = original_point[1] * scale
        return (new_x, new_y)

    # convert imageProcessing format to absolute position
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
    config = None

    def __init__(self, config: dict, hotkeyManager: GlobalHotKeyManager):
        self.config = config

        app = QApplication([])
        self.app = app

        window = settingPanel(app, config, hotkeyManager)
        self.window = window

    def open_settings_gui(self):
        if self.window.isVisible():
            return

        self.window.show()

        if os.environ.get('WAYLAND_DISPLAY') is not None:
            QMessageBox.critical(self.window, 'Error', '此软件无法在Wayland环境下使用\n详见：\nhttps://github.com/BoboTiG/python-mss/issues/155', QMessageBox.StandardButton.Ok)

        self.app.exec()

    def startWithProgram(self):
        if bool(int(self.config.get("START_GUI_WITH_PROGRAM", ""))):
            self.open_settings_gui()
