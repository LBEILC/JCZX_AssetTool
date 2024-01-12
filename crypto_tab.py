# crypto_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import json

# 假设 decrypt.py 和 encrypt.py 是您的加密解密模块
from decrypt import decrypt
from encrypt import encode

CONFIG_FILE = 'app_config.json'

def load_config():
    default_config = {
        'theme': 'minty',
        'decrypt_path': '',
        'encrypt_path': '',
        'cache_file': ''
    }
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return {**default_config, **config}
    except FileNotFoundError:
        return default_config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

class CryptoTab:
    def __init__(self, parent):
        self.parent = parent
        self.config = load_config()
        self.create_widgets()
        self.load_config_to_widgets()

    def create_widgets(self):
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

        # 选择index_cache文件按钮和显示所选文件的标签
        self.select_cache_button = ttk.Button(self.parent, text="选择index_cache文件", command=self.select_cache_file)
        self.select_cache_button.grid(row=2, column=0, padx=5, pady=5)
        self.cache_file_label = ttk.Label(self.parent, text="未选择index_cache文件")
        self.cache_file_label.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # 日志显示区域
        log_label = ttk.Label(self.parent, text="日志")
        log_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.log_text = scrolledtext.ScrolledText(self.parent, height=10, width=80)
        self.log_text.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # 配置 grid 布局的权重
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(4, weight=1)

    def load_config_to_widgets(self):
        # 从配置加载路径到输入框
        self.decrypt_entry.insert(0, self.config['decrypt_path'])
        self.encrypt_entry.insert(0, self.config['encrypt_path'])
        if self.config['cache_file']:
            self.cache_file_label['text'] = Path(self.config['cache_file']).name

    def select_decrypt_folder(self):
        # 选择解密目录
        directory = filedialog.askdirectory()
        if directory:
            self.decrypt_entry.delete(0, tk.END)
            self.decrypt_entry.insert(0, directory)
            self.config['decrypt_path'] = directory
            save_config(self.config)

    def select_encrypt_folder(self):
        # 选择加密目录
        directory = filedialog.askdirectory()
        if directory:
            self.encrypt_entry.delete(0, tk.END)
            self.encrypt_entry.insert(0, directory)
            self.config['encrypt_path'] = directory
            save_config(self.config)

    def select_cache_file(self):
        # 选择index_cache文件
        file_path = filedialog.askopenfilename(
            initialdir=".",
            title="选择index_cache文件",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.cache_file_label['text'] = Path(file_path).name
            self.config['cache_file'] = file_path
            save_config(self.config)

    def start_process(self, process_func):
        # 启动解密或加密进程
        directory = self.decrypt_entry.get() if process_func == decrypt else self.encrypt_entry.get()
        if not directory:
            messagebox.showwarning("警告", "请选择一个有效的目录")
            return
        if process_func == encode and not self.config['cache_file']:
            messagebox.showwarning("警告", "请先选择一个index_cache文件")
            return
        self.disable_buttons()
        threading.Thread(target=self.run_process, args=(process_func, directory), daemon=True).start()

    def run_process(self, process_func, directory):
        # 运行解密或加密进程
        try:
            path = Path(directory)
            if process_func == encode:
                process_func(path, self.config['cache_file'], self.log)
            elif process_func == decrypt:
                process_func(path, self.log)
            self.log("操作完成\n")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            self.log(f"错误: {e}\n")
        finally:
            self.enable_buttons()

    def log(self, message):
        # 日志记录
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def disable_buttons(self):
        # 禁用按钮
        self.decrypt_button['state'] = 'disabled'
        self.encrypt_button['state'] = 'disabled'
        self.select_cache_button['state'] = 'disabled'

    def enable_buttons(self):
        # 启用按钮
        self.decrypt_button['state'] = 'normal'
        self.encrypt_button['state'] = 'normal'
        self.select_cache_button['state'] = 'normal'
