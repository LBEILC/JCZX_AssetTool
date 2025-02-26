"""
加密解密标签页UI模块
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from pathlib import Path

from src.config import ConfigManager
from src.core.crypto import decrypt, encode


class CryptoTab:
    """加密解密标签页类"""
    
    def __init__(self, parent):
        """
        初始化加密解密标签页
        
        Args:
            parent: 父级窗口
        """
        self.parent = parent
        self.config = ConfigManager.load_config()
        self.create_widgets()
        self.load_config_to_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 解密文件目录输入框和按钮
        ttk.Label(self.parent, text="解密assets文件目录:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.decrypt_entry = ttk.Entry(self.parent, width=50)
        self.decrypt_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.decrypt_select_button = ttk.Button(self.parent, text="选择", command=self.select_decrypt_folder)
        self.decrypt_select_button.grid(row=0, column=2, padx=5, pady=5)
        self.decrypt_button = ttk.Button(self.parent, text="解密", command=lambda: self.start_process(decrypt))
        self.decrypt_button.grid(row=0, column=3, padx=5, pady=5)

        # 加密文件目录输入框和按钮
        ttk.Label(self.parent, text="加密assets文件目录:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.encrypt_entry = ttk.Entry(self.parent, width=50)
        self.encrypt_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.encrypt_select_button = ttk.Button(self.parent, text="选择", command=self.select_encrypt_folder)
        self.encrypt_select_button.grid(row=1, column=2, padx=5, pady=5)
        self.encrypt_button = ttk.Button(self.parent, text="加密", command=lambda: self.start_process(encode))
        self.encrypt_button.grid(row=1, column=3, padx=5, pady=5)

        # index_cache文件选择
        ttk.Label(self.parent, text="index_cache文件:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cache_entry = ttk.Entry(self.parent, width=50)
        self.cache_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.cache_select_button = ttk.Button(self.parent, text="选择", command=self.select_cache_file)
        self.cache_select_button.grid(row=2, column=2, padx=5, pady=5)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.parent, width=80, height=20)
        self.log_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # 设置网格权重，使组件可以随窗口调整大小
        self.parent.grid_rowconfigure(3, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

    def load_config_to_widgets(self):
        """从配置加载路径到输入框"""
        self.decrypt_entry.delete(0, tk.END)
        self.decrypt_entry.insert(0, self.config.get('decrypt_path', ''))
        
        self.encrypt_entry.delete(0, tk.END)
        self.encrypt_entry.insert(0, self.config.get('encrypt_path', ''))
        
        self.cache_entry.delete(0, tk.END)
        self.cache_entry.insert(0, self.config.get('cache_file', ''))

    def select_decrypt_folder(self):
        """选择解密目录"""
        folder = filedialog.askdirectory(title="选择解密assets文件目录")
        if folder:
            self.decrypt_entry.delete(0, tk.END)
            self.decrypt_entry.insert(0, folder)
            self.config['decrypt_path'] = folder
            ConfigManager.save_config(self.config)

    def select_encrypt_folder(self):
        """选择加密目录"""
        folder = filedialog.askdirectory(title="选择加密assets文件目录")
        if folder:
            self.encrypt_entry.delete(0, tk.END)
            self.encrypt_entry.insert(0, folder)
            self.config['encrypt_path'] = folder
            ConfigManager.save_config(self.config)

    def select_cache_file(self):
        """选择index_cache文件"""
        file = filedialog.askopenfilename(
            title="选择index_cache文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialdir=str(Path("cache").absolute()) if Path("cache").exists() else None
        )
        if file:
            self.cache_entry.delete(0, tk.END)
            self.cache_entry.insert(0, file)
            self.config['cache_file'] = file
            ConfigManager.save_config(self.config)

    def start_process(self, process_func):
        """
        启动解密或加密进程
        
        Args:
            process_func: 处理函数（decrypt或encode）
        """
        if process_func == decrypt:
            directory = self.decrypt_entry.get()
        else:  # encode
            directory = self.encrypt_entry.get()
            
        if not directory:
            self.log(f"错误: 请选择{'解密' if process_func == decrypt else '加密'}目录\n")
            return
            
        # 禁用按钮，防止重复操作
        self.disable_buttons()
        
        # 在新线程中运行处理函数
        thread = threading.Thread(target=self.run_process, args=(process_func, directory))
        thread.daemon = True
        thread.start()

    def run_process(self, process_func, directory):
        """
        运行解密或加密进程
        
        Args:
            process_func: 处理函数（decrypt或encode）
            directory: 处理目录
        """
        try:
            if process_func == decrypt:
                process_func(Path(directory), self.log)
            else:  # encode
                cache_file = self.cache_entry.get()
                if not cache_file:
                    self.log("错误: 请选择index_cache文件\n")
                    self.enable_buttons()
                    return
                process_func(Path(directory), cache_file, self.log)
        except Exception as e:
            self.log(f"错误: {str(e)}\n")
        finally:
            # 恢复按钮状态
            self.enable_buttons()

    def log(self, message):
        """
        日志记录
        
        Args:
            message: 日志消息
        """
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def disable_buttons(self):
        """禁用按钮"""
        self.decrypt_button.configure(state='disabled')
        self.encrypt_button.configure(state='disabled')
        self.decrypt_select_button.configure(state='disabled')
        self.encrypt_select_button.configure(state='disabled')
        self.cache_select_button.configure(state='disabled')

    def enable_buttons(self):
        """启用按钮"""
        self.decrypt_button.configure(state='normal')
        self.encrypt_button.configure(state='normal')
        self.decrypt_select_button.configure(state='normal')
        self.encrypt_select_button.configure(state='normal')
        self.cache_select_button.configure(state='normal') 