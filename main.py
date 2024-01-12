# main.py
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from crypto_tab import CryptoTab
from settings_tab import SettingsTab, load_config, save_config
from image_tab import ImageTab  # 导入 ImageTab

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("交错战线 Assets 工具 V0.6")

        # 加载配置并应用主题
        self.config = load_config()
        self.style = Style(theme=self.config.get('theme', 'default'))

        # 创建 Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # 创建加密解密标签页
        self.crypto_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crypto_frame, text='加密/解密')
        self.crypto_tab = CryptoTab(self.crypto_frame)

        # 创建图片处理标签页
        self.image_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.image_frame, text='图片处理')
        self.image_tab = ImageTab(self.image_frame)
        self.image_tab.pack(expand=True, fill='both')

        # 创建设置标签页
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='设置')
        self.settings_tab = SettingsTab(self.settings_frame, self.style)

        # 设置主窗口最小大小
        self.root.minsize(400, 300)

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # 获取当前配置并保存
        config = {
            'decrypt_path': self.crypto_tab.decrypt_entry.get(),
            'encrypt_path': self.crypto_tab.encrypt_entry.get(),
            'cache_file': self.crypto_tab.config.get('cache_file'),  # 从 CryptoTab 的配置中获取
            'theme': self.settings_tab.config['theme']
        }
        save_config(config)
        self.root.destroy()


# 创建并运行应用程序
root = tk.Tk()
app = MainApp(root)
root.mainloop()
