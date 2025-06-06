import os
import time

import re

from util.globalHotKeyManager import GlobalHotKeyManager, KeyboardListener, vk_to_key_str
from util.loadSetting import getConfigFilePath, saveConfigDict, getConfigDict, getDefaultConfigDict
from util.imageProcessing import capture_screenshot, crop_image, resize_image

from PyQt6.QtWidgets import QApplication, QWidget, QDoubleSpinBox, QLabel, QPushButton, QTextEdit, QMessageBox, QCheckBox, QDialog, QVBoxLayout, QLineEdit
from PyQt6.QtGui import QKeyEvent, QColor, QPainter, QBrush, QPen, QDesktopServices, QIcon
from PyQt6.QtCore import Qt, QPoint, QUrl, QTimer, QObject, pyqtSignal

keys = set()
update_flag = False
keys_record_flag = False
def keyCallBack(callbak_keys):
    global keys,update_flag,keys_record_flag
    if not keys_record_flag:
        return
    if len(keys)<len(callbak_keys):
        keys = callbak_keys
    update_flag = True

kbl = None

class keyBindingDialog(QDialog):

    def __init__(self, parent):
        global keys_record_flag, kbl
        super().__init__(parent)

        self.pressed_keys = []

        self.setWindowTitle("按键输入")
        self.setWindowIcon(QIcon("./icon.png"))
        self.setFixedSize(200, 100)

        self.label = QLabel("等待输入...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.label.setGeometry(0, 40, 200, 20)
        keys_record_flag = True
        if kbl is None:
            kbl = KeyboardListener(keyCallBack)
            kbl.start()

    def keyPressEvent(self, event):
        global update_flag,keys
        for _ in range(30):
            if update_flag:
                break
            time.sleep(0.01)
            pass
        if len(self.pressed_keys) < len(keys):
            self.pressed_keys = list(keys)
        update_flag = False
        # self.pressed_keys.append(event.nativeVirtualKey())
        self.label.setText('+'.join(vk_to_key_str(key) for key in self.pressed_keys))

    def keyReleaseEvent(self, event):
        global keys,keys_record_flag, kbl, update_flag
        if not kbl is None:
            kbl.stop()
            kbl = None
        keys = set()
        update_flag = False
        keys_record_flag = False
        self.accept()

class keyBindingPanel(QWidget):

    def __init__(self, parent, config: dict):
        super().__init__()

        self.parent = parent
        self.config = config
        self.textEdits = {}

        self.UTIL_KEYBINDS = {
            "OCRKEY": ["识别按键", self.config.get("OCRKEY", "")],
            "SETTINGKEY": ["打开设置", self.config.get("SETTINGKEY", "")]
        }

        self.GROUP1_KEYBINDS = {
            "SKEY1": ["战备1", self.config.get("SKEY1", "")],
            "SKEY2": ["战备2", self.config.get("SKEY2", "")],
            "SKEY3": ["战备3", self.config.get("SKEY3", "")],
            "SKEY4": ["战备4", self.config.get("SKEY4", "")],
            "SKEY5": ["战备5", self.config.get("SKEY5", "")],
            "SKEY6": ["战备6", self.config.get("SKEY6", "")],
            "SKEY7": ["战备7", self.config.get("SKEY7", "")],
            "SKEY8": ["战备8", self.config.get("SKEY8", "")],
            "SKEY9": ["战备9", self.config.get("SKEY9", "")],
            "SKEY10": ["战备10", self.config.get("SKEY10", "")]
        }

        self.GROUP2_KEYBINDS = {
            "SKEYANDOCR1": ["战备1", self.config.get("SKEYANDOCR1", "")],
            "SKEYANDOCR2": ["战备2", self.config.get("SKEYANDOCR2", "")],
            "SKEYANDOCR3": ["战备3", self.config.get("SKEYANDOCR3", "")],
            "SKEYANDOCR4": ["战备4", self.config.get("SKEYANDOCR4", "")],
            "SKEYANDOCR5": ["战备5", self.config.get("SKEYANDOCR5", "")],
            "SKEYANDOCR6": ["战备6", self.config.get("SKEYANDOCR6", "")],
            "SKEYANDOCR7": ["战备7", self.config.get("SKEYANDOCR7", "")],
            "SKEYANDOCR8": ["战备8", self.config.get("SKEYANDOCR8", "")],
            "SKEYANDOCR9": ["战备9", self.config.get("SKEYANDOCR9", "")],
            "SKEYANDOCR10": ["战备10", self.config.get("SKEYANDOCR10", "")]
        }

        self.KEYMAP_KEYBINDS = {
            "W": ["上", self.config.get("W", "")],
            "A": ["左", self.config.get("A", "")],
            "S": ["下", self.config.get("S", "")],
            "D": ["右", self.config.get("D", "")]
        }

        self.ACTIVATION = {
            "ACTIVATION": ["战备面板", self.config.get("ACTIVATION", "")]
        }

        self.setWindowTitle("HD2AS 按键设置")
        # 设置图标
        self.setWindowIcon(QIcon("./icon.png"))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.initWidgets()

    def initWidgets(self):

        def createKeybindingWidget(label, key_name, keybind_name, h, first):
            button = QPushButton(label, self)
            if first:
                button.setGeometry(10, h + 1, 60, 28)
            else:
                button.setGeometry(205, h + 1, 60, 28)

            button.clicked.connect(lambda _, k=key_name: self.change_key(k))


            textEdit = QTextEdit(self)
            textEdit.setPlainText(keybind_name)
            if first:
                textEdit.setGeometry(72, h + 1, 123, 28)
            else:
                textEdit.setGeometry(267, h + 1, 123, 28)

            return textEdit

        def createKeybindingWidget_groups(keybinds, h):
            isFirst = True
            for k, v in keybinds.items():
                textEdit = createKeybindingWidget(v[0], k, v[1], h, isFirst)
                if isFirst:
                    isFirst = False
                else:
                    h += 30
                    isFirst = True
                self.textEdits[k] = textEdit
            if not isFirst:
                h += 30
            return h
        def createKeyBindingLabel(text, h):
            h = h + 10
            label = QLabel(text, self)
            label.setGeometry(10, h, 380, 30)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return h + 30


        h = 10
        h = createKeybindingWidget_groups(self.UTIL_KEYBINDS, h)
        h = createKeyBindingLabel("标准呼叫战备按键", h)
        h = createKeybindingWidget_groups(self.GROUP1_KEYBINDS, h)
        h = createKeyBindingLabel("干扰器优化呼叫战备按键", h)
        h = createKeybindingWidget_groups(self.GROUP2_KEYBINDS, h)
        h = createKeyBindingLabel("战略配备键位", h)
        h = createKeybindingWidget_groups(self.KEYMAP_KEYBINDS, h)

        self.ok_button = QPushButton("完成", self)
        h += 20
        createKeybindingWidget_groups(self.ACTIVATION, h)
        self.ok_button.setGeometry(205, h, 190, 30)
        h += 30
        self.ok_button.clicked.connect(self.parent.onKeybindingOk)

        self.setFixedSize(400, h + 10)

    def change_key(self, key_name):
        dialog = keyBindingDialog(self)
        dialog.exec()

        if not dialog.pressed_keys:
            return

        self.textEdits[key_name].setPlainText('+'.join(vk_to_key_str(key) for key in dialog.pressed_keys))
        dialog.deleteLater()

class resizePanel(QWidget):

    BORDER_COLOR = QColor(0, 120, 215, 255)
    BORDER_WIDTH = 4
    CORNER_RADIUS = 10
    MIN_W, MIN_H = 100, 60

    def __init__(self, parent, x, y, w, h):
        super().__init__()

        self.resize_corner = False
        self.resizing = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setWindowTitle("区域选择框")

        self.resize(max(self.MIN_W, w), max(self.MIN_H, h))
        self.move(x, y)

        self.drag_position = QPoint()

        self.save_button = QPushButton("完成", self)
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
        painter.setPen(QPen(self.BORDER_COLOR, self.BORDER_WIDTH))

        rect = self.rect().adjusted(
            self.BORDER_WIDTH, self.BORDER_WIDTH,
            -self.BORDER_WIDTH, -self.BORDER_WIDTH
        )
        painter.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

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

        self.resize(max(self.MIN_W, new_w), max(self.MIN_H, new_h))
        self.drag_position = current_pos

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None


class ipInputer(QLineEdit):
    def __init__(self, parent, defalutText):
        super().__init__(parent)

        self.setPlaceholderText("Host [ipv4 / ipv6]")
        self.setText(defalutText)

        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self):
        if self.isValidIpAddress(self.text()):
            self.setStyleSheet("background-color: white;")
        else:
            self.setStyleSheet("background-color: #ffaaaa;")

    def isValidIpAddress(self, text):
        ipv4 = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        ipv6 = r'^([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4})$|^([0-9a-fA-F]{1,4}:){1,7}:$|^::([0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,6}:([0-9a-fA-F]{1,4})$|^([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}$|^([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}$|^([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}$|^([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}$|^([0-9a-fA-F]{1,4}:){1}(:[0-9a-fA-F]{1,4}){1,6}$|^:((:[0-9a-fA-F]{1,4}){1,7}|:)$'

        pattern = re.compile(rf'^{ipv4}|{ipv6}|all$')
        return pattern.fullmatch(text)

class portInputer(QLineEdit):
    def __init__(self, parent, defalutText):
        super().__init__(parent)

        self.setPlaceholderText("Port")
        self.setText(defalutText)

        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self):
        if self.isValidPort(self.text()):
            self.setStyleSheet("background-color: white;")
        else:
            self.setStyleSheet("background-color: #ffaaaa;")

    def isValidPort(self, text):
        port = r'^(0|[1-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|65535)$'

        pattern = re.compile(port)
        return pattern.fullmatch(text)


class settingPanel(QWidget):

    def __init__(self, qApp, config: dict, hotkeyManager: GlobalHotKeyManager):
        super().__init__()

        self.qApp = qApp
        self.config = config
        self.hotkeyMgr = hotkeyManager
        self.keybinds = {}
        self.is_closed = True

        self.setWindowTitle("HD2AS 设置面板")
        self.setWindowIcon(QIcon("./icon.png"))
        self.setFixedSize(200, 410)

        self.initWidgets()

    def initWidgets(self):

        # reset button #

        self.reset_button = QPushButton("重置所有设置", self)
        self.reset_button.setGeometry(10, 370, 85, 30)
        self.reset_button.setStyleSheet("color: red;")

        self.reset_button.clicked.connect(self.onResetButtonCliecked)

        # reset button end #

        # save button #

        self.save_button = QPushButton("保存所有设置", self)
        self.save_button.setGeometry(105, 370, 85, 30)

        self.save_button.clicked.connect(self.onSaveButtonCliecked)

        # save button end #

        # start with program #

        self.start_with_program_checkbox = QCheckBox("允许设置面板随程序开启", self)
        self.start_with_program_checkbox.setGeometry(10, 310, 180, 20)
        self.start_with_program_checkbox.setChecked(self.config.get("START_GUI_WITH_PROGRAM", "True").upper() == "TRUE")
        # this checkbox state will be saved when save button cliecked

        # start with program end #

        # manual edit button #

        self.manual_edit_button = QPushButton("(高级)手动编辑配置文件", self)
        self.manual_edit_button.setGeometry(10, 335, 180, 30)

        self.manual_edit_button.clicked.connect(self.onManualEditButtonCliecked)

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

        # webui #

        webui_label = QLabel("========  WebUI 设置  ========", self)
        webui_label.setGeometry(10, 235, 180, 25)
        webui_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.host_lineedit = ipInputer(self, self.config.get("WEB_GUI_HOST", ""))
        self.host_lineedit.setGeometry(10, 260, 110, 30)

        colon_label = QLabel(":", self)
        colon_label.setGeometry(120, 260, 10, 30)
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.port_lineedit = portInputer(self, str(self.config.get("WEB_GUI_PORT", "")))
        self.port_lineedit.setGeometry(130, 260, 60, 30)


        # webui end #

        widgets = [
            self.delay_min_spinbox,
            self.delay_max_spinbox,
            self.keybind_button,
            self.size_x_spinbox,
            self.size_w_spinbox,
            self.size_y_spinbox,
            self.size_h_spinbox,
            self.resize_button,
            self.resize_test_button,
            self.start_with_program_checkbox,
            self.manual_edit_button,
            self.reset_button,
            self.save_button
        ]
        for i in range(len(widgets) - 1):
            self.setTabOrder(widgets[i], widgets[i + 1])

    # reset button #
    def onResetButtonCliecked(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("警告")
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

        # delete all widgets and reinit them, so i dont need to change the value one by one
        self.hide()

        for child in self.findChildren(QWidget):
            child.deleteLater()
        self.initWidgets()

        self.show()
    # reset button end #

    # save button #
    def onSaveButtonCliecked(self):

        newConfig = dict(self.keybinds)

        try:
            newConfig .update({
                "DELAY_MIN": self.delay_min_spinbox.value(),
                "DELAY_MAX": self.delay_max_spinbox.value(),
                #"ACTIVATION": self.keybind_label.toPlainText(),

                "LEFT": int(self.size_x_spinbox.value()),
                "TOP": int(self.size_y_spinbox.value()),
                "RIGHT": int(self.size_w_spinbox.value()),
                "BOTTOM": int(self.size_h_spinbox.value()),

                "START_GUI_WITH_PROGRAM": "True" if self.start_with_program_checkbox.isChecked() else "False",

                "WEB_GUI_PORT": int(self.port_lineedit.text()),
                "WEB_GUI_HOST": self.host_lineedit.text()
            })
        except Exception as e:
            QMessageBox.critical(self, 'QMessageBox', '保存时发生错误！目前没有执行任何操作\n' + str(e), QMessageBox.StandardButton.Ok)
            return


        saveConfigDict(newConfig)
        self.config = getConfigDict()
        self.hotkeyMgr.auto_register(self.config)

        self.close()
    # save button end #

    # manual edit button #
    def onManualEditButtonCliecked(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("警告")
        message_box.setText("<font color='red'>这会放弃所有未保存的改动</font><br/>要继续吗？")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        message_box.button(QMessageBox.StandardButton.Yes).setText("确认")
        message_box.button(QMessageBox.StandardButton.No).setText("取消")
        message_box.setIcon(QMessageBox.Icon.Warning)

        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.No:
            return


        QDesktopServices.openUrl(QUrl.fromLocalFile(getConfigFilePath()))
        # wait for a while to let QDesktopServices finish his job
        QTimer.singleShot(1000, self.close)
    # manual edit button end #

    # keybind #
    def onKeybindButtonCliecked(self):
        self.hide()

        keybinds_dict = self.keybinds
        if not keybinds_dict:
            keybinds_dict = self.config

        self.overlay_keybinding = keyBindingPanel(self, keybinds_dict)
        self.overlay_keybinding.destroyed.connect(self.onOverlayKeybindingPanelDestroyed)
        self.overlay_keybinding.show()

    def onKeybindingOk(self):
        keybinds_dict = {}
        for k, v in self.overlay_keybinding.textEdits.items():
            keybinds_dict[k] = v.toPlainText()
        self.keybinds = keybinds_dict

        self.overlay_keybinding.close()

    def onOverlayKeybindingPanelDestroyed(self):
        if self.isVisible():
            return
        self.show()
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
        # make absolute position to window size
        w, h = w - x, h - y

        self.overlay_resize = resizePanel(self, int(x), int(y), int(w), int(h))
        self.overlay_resize.destroyed.connect(self.onOverlayResizePanelDestroyed)
        self.overlay_resize.show()

    def onResizeSaved(self):
        x, y, w, h = self.overlay_resize.geometry().getRect()
        # defensive fix
        if w is None or h is None or x is None or y is None:
            QMessageBox.critical(self, 'QMessageBox', '无法从交互式面板获取框选区域？！\n当前未进行任何改动', QMessageBox.StandardButton.Ok)
            return
        # change window size to absolute position
        w, h = x + w, y + h

        # EDIT: haha i cant fix that, no help at all
        # linux wayland desktop defensive fix, fucking wayland destroy everything
        #if x == 0 and y == 0:
        #    point = self.overlay_resize.windowHandle().screen().geometry().topLeft()
        #    x = point.x()
        #    y = point.y()
        #    print("wayland defensive fix, x value:"+ str(x) +" y value:"+ str(y))

        self.size_x_spinbox.setValue(x)
        self.size_y_spinbox.setValue(y)
        self.size_w_spinbox.setValue(w)
        self.size_h_spinbox.setValue(h)

        self.overlay_resize.close()

    def onOverlayResizePanelDestroyed(self):
        if self.isVisible():
            return
        self.show()
    # resize panel end #


    def showEvent(self, event):
        self.is_closed = False

    def closeEvent(self, event):
        self.is_closed = True
        self.hotkeyMgr.start()
        super().closeEvent(event)

# class from old tkGui(early nuked), im too lazy so i didnt change the api format #
class settingsGUI(QObject):

    exit_signal = pyqtSignal()

    def __init__(self, config: dict, hotkeyManager: GlobalHotKeyManager):
        super().__init__()

        self.config = config
        self.hotkeyMgr = hotkeyManager

        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.exit_signal.connect(self.app.quit)

        self.window = settingPanel(self.app, self.config, self.hotkeyMgr)

    def execute(self):
        self.app.exec()

    def start_qt_widget(self):

        if not self.window.is_closed:
            return

        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

        # will restart it when window closed, see settingPanel.closeEvent()
        self.hotkeyMgr.stop()

        if os.environ.get('WAYLAND_DISPLAY') is not None:
            QMessageBox.critical(self.window, 'QMessageBox', '此软件无法在Wayland环境下使用\n详见：\nhttps://github.com/BoboTiG/python-mss/issues/155', QMessageBox.StandardButton.Ok)

    def open_settings_gui(self):
        # make sure is running on main thread
        QTimer.singleShot(0, self.start_qt_widget)

    def startWithProgram(self):
        if self.config.get("START_GUI_WITH_PROGRAM", "True").upper() == "TRUE":
            self.open_settings_gui()

    def quit(self):
        global kbl

        self.exit_signal.emit()

        if not kbl is None:
            kbl.stop()
