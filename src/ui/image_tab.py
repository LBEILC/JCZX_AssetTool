"""
图像处理标签页UI模块 - PyQt6版本
"""
import threading
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QGridLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from qfluentwidgets import (
    PushButton, TextEdit, CardWidget, FluentIcon, 
    InfoBar, InfoBarPosition, ImageLabel, TitleLabel,
    StrongBodyLabel, BodyLabel, ScrollArea,
    IconWidget, TransparentToolButton, ToggleButton,
    isDarkTheme
)

from src.config import ConfigManager
from src.core.image_processor import premultiply_alpha, straight_alpha, batch_process_images


class ImageTab(QWidget):
    """图像处理标签页类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        初始化图像处理标签页
        
        Args:
            parent: 父级窗口
        """
        super().__init__(parent)
        self.config = ConfigManager.load_config()
        self.last_processed_images = []
        self.setup_ui()
        
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
        title_label = TitleLabel("图像透明度处理")
        description_label = BodyLabel("用于转换图像透明度格式，支持预乘透明和直通透明互转")
        description_label.setTextColor("gray")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        main_layout.addSpacing(10)
        
        # 创建转换选项卡片
        conversion_card = CardWidget(self)
        conversion_layout = QVBoxLayout(conversion_card)
        conversion_layout.setContentsMargins(15, 15, 15, 15)
        conversion_layout.setSpacing(10)
        
        # 标题
        card_title = StrongBodyLabel("转换选项")
        conversion_layout.addWidget(card_title)
        
        # 创建按钮区
        button_grid = QGridLayout()
        button_grid.setContentsMargins(10, 10, 10, 10)
        button_grid.setSpacing(15)
        
        # 直通转预乘按钮
        self.straight_to_premul_card = CardWidget(self)
        self.straight_to_premul_card.setCursor(Qt.CursorShape.PointingHandCursor)
        straight_to_premul_layout = QVBoxLayout(self.straight_to_premul_card)
        
        straight_to_premul_icon = IconWidget(FluentIcon.DOWNLOAD)
        straight_to_premul_icon.setFixedSize(48, 48)
        
        straight_to_premul_title = StrongBodyLabel("直通透明转预乘透明")
        straight_to_premul_desc = BodyLabel("适用于需要在游戏引擎中使用的图像")
        straight_to_premul_desc.setTextColor("gray")
        
        straight_to_premul_layout.addWidget(straight_to_premul_icon, 0, Qt.AlignmentFlag.AlignCenter)
        straight_to_premul_layout.addWidget(straight_to_premul_title, 0, Qt.AlignmentFlag.AlignCenter)
        straight_to_premul_layout.addWidget(straight_to_premul_desc, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 预乘转直通按钮
        self.premul_to_straight_card = CardWidget(self)
        self.premul_to_straight_card.setCursor(Qt.CursorShape.PointingHandCursor)
        premul_to_straight_layout = QVBoxLayout(self.premul_to_straight_card)
        
        premul_to_straight_icon = IconWidget(FluentIcon.FONT_INCREASE)
        premul_to_straight_icon.setFixedSize(48, 48)
        
        premul_to_straight_title = StrongBodyLabel("预乘透明转直通透明")
        premul_to_straight_desc = BodyLabel("适用于图像编辑软件中使用的图像")
        premul_to_straight_desc.setTextColor("gray")
        
        premul_to_straight_layout.addWidget(premul_to_straight_icon, 0, Qt.AlignmentFlag.AlignCenter)
        premul_to_straight_layout.addWidget(premul_to_straight_title, 0, Qt.AlignmentFlag.AlignCenter)
        premul_to_straight_layout.addWidget(premul_to_straight_desc, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 添加到网格
        button_grid.addWidget(self.straight_to_premul_card, 0, 0)
        button_grid.addWidget(self.premul_to_straight_card, 0, 1)
        
        # 添加提示文本
        hint_label = BodyLabel("点击上方选项选择要处理的图像文件")
        hint_label.setTextColor("gray")
        
        conversion_layout.addLayout(button_grid)
        conversion_layout.addWidget(hint_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(conversion_card)
        
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
        self.log_text.setMinimumHeight(150)
        
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
        
        # 按钮连接
        self.straight_to_premul_card.mousePressEvent = lambda e: self.select_images(False)
        self.premul_to_straight_card.mousePressEvent = lambda e: self.select_images(True)

    def select_images(self, premultiplied_to_straight):
        """
        选择图像文件并处理
        
        Args:
            premultiplied_to_straight: 是否为预乘转直通
        """
        # 获取上次使用的目录
        initial_dir = self.config.get('last_image_dir', '')
        
        # 选择文件
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图像文件",
            initial_dir,
            "PNG文件 (*.png);;所有图像文件 (*.png *.jpg *.jpeg *.tga *.bmp);;所有文件 (*)"
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
        self.last_processed_images = file_paths
        
        # 选择转换函数
        conversion_function = straight_alpha if premultiplied_to_straight else premultiply_alpha
        conversion_type = "预乘转直通" if premultiplied_to_straight else "直通转预乘"
        
        # 显示处理信息
        self.log(f"开始处理图像 ({conversion_type})...\n")
        self.log(f"选择了 {len(files)} 个文件\n")
        
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
            
            # 完成后显示成功信息
            InfoBar.success(
                title="处理完成",
                content=f"已成功处理 {len(file_paths)} 个图像文件",
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            
        except Exception as e:
            self.log(f"处理图像时出错: {str(e)}\n")
            
            # 显示错误信息
            InfoBar.error(
                title="处理失败",
                content=f"处理图像时出错: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            
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
        """禁用转换按钮"""
        self.straight_to_premul_card.setEnabled(False)
        self.premul_to_straight_card.setEnabled(False)
        
    def enable_buttons(self):
        """启用转换按钮"""
        self.straight_to_premul_card.setEnabled(True)
        self.premul_to_straight_card.setEnabled(True)
        
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