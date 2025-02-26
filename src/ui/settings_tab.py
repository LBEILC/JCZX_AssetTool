"""
设置标签页UI模块
"""
import tkinter as tk
from tkinter import ttk

from src.config import ConfigManager


class SettingsTab:
    """设置标签页类"""

    def __init__(self, parent, style):
        """
        初始化设置标签页
        
        Args:
            parent: 父级窗口
            style: ttkbootstrap样式对象
        """
        self.parent = parent
        self.style = style
        self.config = ConfigManager.load_config()
        self.create_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 创建一个框架来包含所有设置
        self.settings_frame = ttk.LabelFrame(self.parent, text="应用程序设置")
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 主题选择下拉框
        self.theme_label = ttk.Label(self.settings_frame, text="主题:")
        self.theme_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.theme_combobox = ttk.Combobox(self.settings_frame, values=self.style.theme_names(), state='readonly')
        self.theme_combobox.set(self.config.get('theme', 'default'))
        self.theme_combobox.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.theme_combobox.bind('<<ComboboxSelected>>', self.change_theme)

        # 缓存目录设置
        self.cache_frame = ttk.LabelFrame(self.settings_frame, text="缓存设置")
        self.cache_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)

        # 清除缓存按钮
        self.clear_cache_button = ttk.Button(self.cache_frame, text="清除缓存文件", command=self.clear_cache)
        self.clear_cache_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 关于信息
        self.about_frame = ttk.LabelFrame(self.settings_frame, text="关于")
        self.about_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)

        # 版本信息
        self.version_label = ttk.Label(self.about_frame, text="交错战线 Assets 工具 V1.0.0")
        self.version_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 作者信息
        self.author_label = ttk.Label(self.about_frame, text="作者: 路北路陈")
        self.author_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    def change_theme(self, event):
        """
        更改应用程序主题
        
        Args:
            event: 事件对象
        """
        new_theme = self.theme_combobox.get()
        self.style.theme_use(new_theme)
        self.config['theme'] = new_theme
        ConfigManager.save_config(self.config)

    def clear_cache(self):
        """清除缓存文件"""
        from pathlib import Path
        import shutil

        cache_dir = Path("cache")
        if cache_dir.exists():
            try:
                # 删除缓存目录中的所有文件
                for file in cache_dir.glob("*"):
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        shutil.rmtree(file)

                # 显示成功消息
                self.show_message("缓存已清除")
            except Exception as e:
                # 显示错误消息
                self.show_message(f"清除缓存时出错: {str(e)}")
        else:
            # 显示信息消息
            self.show_message("缓存目录不存在")

    def show_message(self, message):
        """
        显示消息对话框
        
        Args:
            message: 消息内容
        """
        from tkinter import messagebox
        messagebox.showinfo("信息", message)
