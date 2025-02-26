#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交错战线 Assets 工具主程序
"""
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from pathlib import Path

# 导入自定义模块
from src.config import ConfigManager
from src.ui import CryptoTab, ImageTab, SettingsTab


class MainApp:
    """主应用程序类"""
    
    def __init__(self, root):
        """
        初始化主应用程序
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("交错战线 Assets 工具 V0.7")

        # 确保缓存目录存在
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        
        # 确保输出目录存在
        output_dir = Path("output_预乘透明")
        output_dir.mkdir(exist_ok=True)
        output_dir = Path("output_直通透明")
        output_dir.mkdir(exist_ok=True)

        # 加载配置并应用主题
        self.config = ConfigManager.load_config()
        self.style = Style(theme=self.config.get('theme', 'minty'))

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

        # 创建设置标签页
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='设置')
        self.settings_tab = SettingsTab(self.settings_frame, self.style)

        # 设置主窗口最小大小
        self.root.minsize(600, 400)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # 如果图标不存在，忽略错误

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """关闭应用程序时的处理"""
        # 获取当前配置并保存
        config = {
            'decrypt_path': self.crypto_tab.decrypt_entry.get(),
            'encrypt_path': self.crypto_tab.encrypt_entry.get(),
            'cache_file': self.crypto_tab.cache_entry.get(),
            'theme': self.settings_tab.config['theme']
        }
        ConfigManager.save_config(config)
        self.root.destroy()


def main():
    """主函数"""
    # 创建并运行应用程序
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
