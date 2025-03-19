"""
加密解密标签页UI模块 - PyQt6版本
"""
import threading
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from qfluentwidgets import (
    PushButton, LineEdit, TextEdit, 
    FluentIcon, ComboBox, InfoBar, InfoBarPosition,
    CardWidget, TitleLabel, StrongBodyLabel, BodyLabel, 
    MessageBox, SmoothScrollArea, IconWidget, TransparentToolButton, ScrollArea,
    isDarkTheme
)

from src.config import ConfigManager
from src.core.crypto import decrypt, encode


class CryptoTab(QWidget):
    """加密解密标签页类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        初始化加密解密标签页
        
        Args:
            parent: 父级窗口
        """
        super().__init__(parent)
        self.config = ConfigManager.load_config()
        self.setup_ui()
        self.load_config_to_widgets()
        
        # 连接信号
        self.log_signal.connect(self.append_log)
        
        # 监听主题变化
        from qfluentwidgets import qconfig
        qconfig.themeChanged.connect(self.on_theme_changed)

    def setup_ui(self):
        """创建UI组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)
        
        # 添加标题
        title_label = TitleLabel("资源文件加密/解密")
        description_label = BodyLabel("用于处理游戏资源文件的加密和解密操作")
        description_label.setTextColor("gray")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        main_layout.addSpacing(10)
        
        # 创建文件操作卡片
        operation_card = CardWidget(self)
        operation_layout = QVBoxLayout(operation_card)
        operation_layout.setContentsMargins(15, 15, 15, 15)
        operation_layout.setSpacing(15)
        
        # 解密文件目录
        decrypt_title = StrongBodyLabel("资源解密")
        operation_layout.addWidget(decrypt_title)
        
        decrypt_layout = QHBoxLayout()
        decrypt_label = BodyLabel("解密assets文件目录:")
        self.decrypt_entry = LineEdit()
        self.decrypt_entry.setPlaceholderText("选择包含加密资源文件的目录")
        self.decrypt_entry.setMinimumWidth(300)
        self.decrypt_select_button = PushButton("选择", self, FluentIcon.FOLDER)
        self.decrypt_button = PushButton("解密", self, FluentIcon.DOWNLOAD)
        self.decrypt_button.setIcon(FluentIcon.DOWNLOAD)
        
        decrypt_layout.addWidget(decrypt_label)
        decrypt_layout.addWidget(self.decrypt_entry, 1)
        decrypt_layout.addWidget(self.decrypt_select_button)
        decrypt_layout.addWidget(self.decrypt_button)
        
        operation_layout.addLayout(decrypt_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        operation_layout.addWidget(separator)
        
        # 加密文件目录
        encrypt_title = StrongBodyLabel("资源加密")
        operation_layout.addWidget(encrypt_title)
        
        encrypt_layout = QHBoxLayout()
        encrypt_label = BodyLabel("加密assets文件目录:")
        self.encrypt_entry = LineEdit()
        self.encrypt_entry.setPlaceholderText("选择包含解密资源文件的目录")
        self.encrypt_entry.setMinimumWidth(300)
        self.encrypt_select_button = PushButton("选择", self, FluentIcon.FOLDER)
        self.encrypt_button = PushButton("加密", self, FluentIcon.FONT_INCREASE)
        
        encrypt_layout.addWidget(encrypt_label)
        encrypt_layout.addWidget(self.encrypt_entry, 1)
        encrypt_layout.addWidget(self.encrypt_select_button)
        encrypt_layout.addWidget(self.encrypt_button)
        
        # index_cache文件选择
        cache_layout = QHBoxLayout()
        cache_label = BodyLabel("index_cache文件:")
        self.cache_entry = LineEdit()
        self.cache_entry.setPlaceholderText("选择index_cache文件")
        self.cache_entry.setMinimumWidth(300)
        self.cache_select_button = PushButton("选择", self, FluentIcon.DOCUMENT)
        
        cache_layout.addWidget(cache_label)
        cache_layout.addWidget(self.cache_entry, 1)
        cache_layout.addWidget(self.cache_select_button)
        
        operation_layout.addLayout(encrypt_layout)
        operation_layout.addLayout(cache_layout)
        
        main_layout.addWidget(operation_card)
        
        # 日志卡片
        log_card = CardWidget(self)
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        # 日志标题区域带图标
        log_header = QHBoxLayout()
        log_title = StrongBodyLabel("操作日志")
        log_icon = IconWidget(FluentIcon.HISTORY, self)
        log_icon.setFixedSize(20, 20)
        
        log_header.addWidget(log_icon)
        log_header.addWidget(log_title)
        log_header.addStretch(1)
        
        # 清除日志按钮
        clear_log_button = TransparentToolButton(FluentIcon.DELETE, self)
        clear_log_button.setFixedSize(32, 32)
        clear_log_button.setToolTip("清除日志")
        clear_log_button.clicked.connect(self.clear_log)
        log_header.addWidget(clear_log_button)
        
        log_layout.addLayout(log_header)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: rgba(200, 200, 200, 100); margin: 5px 0;")
        log_layout.addWidget(separator)
        
        # 使用ScrollArea包装日志文本框
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 设置根据主题自适应的样式
        if isDarkTheme():
            scroll_area.setStyleSheet("""
                ScrollArea {
                    background-color: rgba(50, 50, 50, 120);
                    border-radius: 5px;
                    border: 1px solid rgba(80, 80, 80, 150);
                }
            """)
        else:
            scroll_area.setStyleSheet("""
                ScrollArea {
                    background-color: rgba(255, 255, 255, 40);
                    border-radius: 5px;
                    border: 1px solid rgba(200, 200, 200, 100);
                }
            """)
        
        # 日志文本框
        self.log_text = TextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(180)
        
        # 禁用TextEdit自身的滚动条
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 根据主题设置文本框样式
        if isDarkTheme():
            self.log_text.setStyleSheet("""
                TextEdit {
                    border: none;
                    background-color: transparent;
                    color: #e0e0e0;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    font-size: 9pt;
                }
            """)
        else:
            self.log_text.setStyleSheet("""
                TextEdit {
                    border: none;
                    background-color: transparent;
                    color: #333333;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    font-size: 9pt;
                }
            """)
        
        scroll_area.setWidget(self.log_text)
        log_layout.addWidget(scroll_area)
        
        main_layout.addWidget(log_card)
        
        # 连接按钮信号
        self.decrypt_select_button.clicked.connect(self.select_decrypt_folder)
        self.encrypt_select_button.clicked.connect(self.select_encrypt_folder)
        self.cache_select_button.clicked.connect(self.select_cache_file)
        self.decrypt_button.clicked.connect(lambda: self.start_process(decrypt))
        self.encrypt_button.clicked.connect(lambda: self.start_process(encode))

    def load_config_to_widgets(self):
        """从配置加载路径到输入框"""
        self.decrypt_entry.setText(self.config.get('decrypt_path', ''))
        self.encrypt_entry.setText(self.config.get('encrypt_path', ''))
        self.cache_entry.setText(self.config.get('cache_file', ''))

    def select_decrypt_folder(self):
        """选择解密目录"""
        folder = QFileDialog.getExistingDirectory(self, "选择解密assets文件目录")
        if folder:
            self.decrypt_entry.setText(folder)
            self.config['decrypt_path'] = folder
            ConfigManager.save_config(self.config)

    def select_encrypt_folder(self):
        """选择加密目录"""
        folder = QFileDialog.getExistingDirectory(self, "选择加密assets文件目录")
        if folder:
            self.encrypt_entry.setText(folder)
            self.config['encrypt_path'] = folder
            ConfigManager.save_config(self.config)

    def select_cache_file(self):
        """选择index_cache文件"""
        cache_dir = str(Path("cache").absolute()) if Path("cache").exists() else None
        file, _ = QFileDialog.getOpenFileName(
            self, 
            "选择index_cache文件",
            cache_dir,
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file:
            self.cache_entry.setText(file)
            self.config['cache_file'] = file
            ConfigManager.save_config(self.config)

    def start_process(self, process_func):
        """
        启动解密或加密进程
        
        Args:
            process_func: 处理函数（decrypt或encode）
        """
        if process_func == decrypt:
            directory = self.decrypt_entry.text()
            if not directory:
                MessageBox("错误", "请选择解密目录", self).exec()
                return
        else:  # encode
            directory = self.encrypt_entry.text()
            if not directory:
                MessageBox("错误", "请选择加密目录", self).exec()
                return
                
            cache_file = self.cache_entry.text()
            if not cache_file:
                MessageBox("错误", "请选择index_cache文件", self).exec()
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
                cache_file = self.cache_entry.text()
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
        self.log_signal.emit(message)
        
    def append_log(self, message):
        """将消息添加到日志文本框"""
        self.log_text.append(message)
        # 滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def disable_buttons(self):
        """禁用按钮"""
        self.decrypt_button.setEnabled(False)
        self.encrypt_button.setEnabled(False)
        self.decrypt_select_button.setEnabled(False)
        self.encrypt_select_button.setEnabled(False)
        self.cache_select_button.setEnabled(False)

    def enable_buttons(self):
        """启用按钮"""
        self.decrypt_button.setEnabled(True)
        self.encrypt_button.setEnabled(True)
        self.decrypt_select_button.setEnabled(True)
        self.encrypt_select_button.setEnabled(True)
        self.cache_select_button.setEnabled(True)

    def clear_log(self):
        """清除日志内容"""
        self.log_text.clear()
        self.log("日志已清除\n")

    def on_theme_changed(self):
        """主题变化时更新操作日志样式"""
        # 更新滚动区域样式
        scroll_area = self.findChild(ScrollArea)
        if scroll_area:
            if isDarkTheme():
                scroll_area.setStyleSheet("""
                    ScrollArea {
                        background-color: rgba(50, 50, 50, 120);
                        border-radius: 5px;
                        border: 1px solid rgba(80, 80, 80, 150);
                    }
                """)
            else:
                scroll_area.setStyleSheet("""
                    ScrollArea {
                        background-color: rgba(255, 255, 255, 40);
                        border-radius: 5px;
                        border: 1px solid rgba(200, 200, 200, 100);
                    }
                """)
        
        # 更新文本框样式
        if self.log_text:
            if isDarkTheme():
                self.log_text.setStyleSheet("""
                    TextEdit {
                        border: none;
                        background-color: transparent;
                        color: #e0e0e0;
                        font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                        font-size: 9pt;
                    }
                """)
            else:
                self.log_text.setStyleSheet("""
                    TextEdit {
                        border: none;
                        background-color: transparent;
                        color: #333333;
                        font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                        font-size: 9pt;
                    }
                """) 