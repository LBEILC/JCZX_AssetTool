"""
图像处理标签页UI模块
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from pathlib import Path

from src.config import ConfigManager
from src.core.image_processor import premultiply_alpha, straight_alpha, batch_process_images


class ImageTab:
    """图像处理标签页类"""
    
    def __init__(self, parent):
        """
        初始化图像处理标签页
        
        Args:
            parent: 父级窗口
        """
        self.parent = parent
        self.config = ConfigManager.load_config()
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # 设置网格权重，使组件可以随窗口调整大小
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        """创建UI组件"""
        # 直通转预乘按钮
        self.straight_to_premul_button = ttk.Button(
            self.frame, 
            text="直通透明转预乘透明", 
            command=lambda: self.select_images(False)
        )
        self.straight_to_premul_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # 预乘转直通按钮
        self.premul_to_straight_button = ttk.Button(
            self.frame, 
            text="预乘透明转直通透明", 
            command=lambda: self.select_images(True)
        )
        self.premul_to_straight_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.log_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # 设置网格权重，使组件可以随窗口调整大小
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def select_images(self, premultiplied_to_straight):
        """
        选择图像文件并处理
        
        Args:
            premultiplied_to_straight: 是否为预乘转直通
        """
        # 获取上次使用的目录
        initial_dir = self.config.get('last_image_dir', '')
        
        # 选择文件
        files = filedialog.askopenfilenames(
            title="选择图像文件",
            filetypes=[
                ("PNG文件", "*.png"),
                ("所有图像文件", "*.png *.jpg *.jpeg *.tga *.bmp"),
                ("所有文件", "*.*")
            ],
            initialdir=initial_dir if initial_dir else None
        )
        
        if not files:
            return
            
        # 保存最后使用的目录
        if files:
            last_dir = str(Path(files[0]).parent)
            self.config['last_image_dir'] = last_dir
            ConfigManager.save_config(self.config)
        
        # 禁用按钮
        self.disable_buttons()
        
        # 转换为Path对象
        file_paths = [Path(f) for f in files]
        
        # 选择转换函数
        conversion_function = straight_alpha if premultiplied_to_straight else premultiply_alpha
        
        # 在新线程中处理图像
        thread = threading.Thread(
            target=self.process_images,
            args=(file_paths, conversion_function)
        )
        thread.daemon = True
        thread.start()

    def process_images(self, file_paths, conversion_function):
        """
        处理图像文件
        
        Args:
            file_paths: 图像文件路径列表
            conversion_function: 转换函数
        """
        try:
            batch_process_images(file_paths, conversion_function, self.log)
        except Exception as e:
            self.log(f"处理图像时出错: {str(e)}\n")
        finally:
            # 恢复按钮状态
            self.enable_buttons()

    def log(self, message):
        """
        日志记录
        
        Args:
            message: 日志消息
        """
        def append_message():
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
            
        # 在主线程中更新UI
        if threading.current_thread() is not threading.main_thread():
            self.frame.after(0, append_message)
        else:
            append_message()

    def disable_buttons(self):
        """禁用按钮"""
        self.straight_to_premul_button.configure(state='disabled')
        self.premul_to_straight_button.configure(state='disabled')

    def enable_buttons(self):
        """启用按钮"""
        self.straight_to_premul_button.configure(state='normal')
        self.premul_to_straight_button.configure(state='normal')

    def pack(self, **kwargs):
        """
        包装组件
        
        Args:
            **kwargs: 包装参数
        """
        self.frame.pack(**kwargs) 