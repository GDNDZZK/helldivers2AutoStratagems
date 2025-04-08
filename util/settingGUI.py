import tkinter as tk
from tkinter import ttk

class settingsGUI:

    def __init__(self, config, hotkeyManager):
        """
        初始化设置 GUI
        """
        self.window = None

    def open_settings_gui(self):
        """
        打开设置 GUI 的逻辑
        """
        def save_settings():
            # 获取用户输入的值
            delay_min = delay_min_var.get()
            delay_max = delay_max_var.get()
            activation_key = activation_key_var.get()

            # 保存设置逻辑（可以写入配置文件或全局变量）
            print(f"保存设置: DELAY_MIN={delay_min}, DELAY_MAX={delay_max}, ACTIVATION={activation_key}")
            # 在这里实现保存逻辑，例如写入配置文件
            # config['DELAY_MIN'] = delay_min
            # config['DELAY_MAX'] = delay_max
            # config['ACTIVATION'] = activation_key

            # 关闭窗口
            settings_window.destroy()

        # 创建主窗口
        settings_window = tk.Tk()
        settings_window.title("设置菜单")
        settings_window.geometry("300x200")

        # 延迟设置
        tk.Label(settings_window, text="最小延迟 (秒):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        delay_min_var = tk.StringVar(value="0.05")  # 默认值
        tk.Entry(settings_window, textvariable=delay_min_var).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="最大延迟 (秒):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        delay_max_var = tk.StringVar(value="0.1")  # 默认值
        tk.Entry(settings_window, textvariable=delay_max_var).grid(row=1, column=1, padx=10, pady=5)

        # 激活键设置
        tk.Label(settings_window, text="激活键:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        activation_key_var = tk.StringVar(value="Ctrl")  # 默认值
        ttk.Combobox(settings_window, textvariable=activation_key_var, values=["Ctrl", "Alt", "Shift"]).grid(row=2, column=1, padx=10, pady=5)

        # 保存按钮
        tk.Button(settings_window, text="保存", command=save_settings).grid(row=3, column=0, columnspan=2, pady=10)

        # 运行窗口
        settings_window.mainloop()