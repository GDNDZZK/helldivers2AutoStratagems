import threading
import tkinter as tk
from tkinter import ttk

from util.globalHotKeyManager import GlobalHotKeyManager
from util.loadSetting import saveConfigDict, getConfigDict

class settingsGUI:

    def __init__(self, config, hotkeyManager: GlobalHotKeyManager):
        """
        初始化设置 GUI
        """
        self.window = None
        self.config = config
        self.hotkeyManager = hotkeyManager
        self.lock = threading.Lock()

    def open_settings_gui(self):
        """
        打开设置 GUI 的逻辑
        """
        def save_settings():
            with self.lock:
                # 获取用户输入的值
                delay_min = delay_min_var.get()
                delay_max = delay_max_var.get()
                activation_key = activation_key_var.get()

                # 保存设置逻辑（可以写入配置文件或全局变量）
                print(f"保存设置: DELAY_MIN={delay_min}, DELAY_MAX={delay_max}, ACTIVATION={activation_key}")
                new_config = {
                    "DELAY_MIN": delay_min,
                    "DELAY_MAX": delay_max,
                    "ACTIVATION": activation_key,
                }
                saveConfigDict(new_config)
                self.config = new_config
                self.hotkeyManager.stop()
                self.hotkeyManager.auto_register(new_config)
                self.hotkeyManager.start()

                # 关闭窗口
                settings_window.destroy()

        def restore_defaults():
            # 还原默认设置
            delay_min_var.set("0.05")
            delay_max_var.set("0.1")
            activation_key_var.set("<ctrl>")

        # 创建主窗口
        settings_window = tk.Tk()
        settings_window.title("设置菜单")
        settings_window.geometry("300x250")

        # 延迟设置
        tk.Label(settings_window, text="最小延迟 (秒):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        delay_min_var = tk.StringVar(value=self.config.get("DELAY_MIN", ""))
        tk.Entry(settings_window, textvariable=delay_min_var).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="最大延迟 (秒):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        delay_max_var = tk.StringVar(value=self.config.get("DELAY_MAX", ""))
        tk.Entry(settings_window, textvariable=delay_max_var).grid(row=1, column=1, padx=10, pady=5)

        # 激活键设置
        tk.Label(settings_window, text="激活键:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        activation_key_var = tk.StringVar(value=self.config.get("ACTIVATION", ""))
        ttk.Combobox(settings_window, textvariable=activation_key_var, values=["<ctrl>", "<alt>", "<shift>"]).grid(row=2, column=1, padx=10, pady=5)

        # 保存按钮
        tk.Button(settings_window, text="保存", command=save_settings).grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # 还原默认按钮
        tk.Button(settings_window, text="默认", command=restore_defaults).grid(row=3, column=1, padx=10, pady=10, sticky="e")

        # 运行窗口
        settings_window.mainloop()