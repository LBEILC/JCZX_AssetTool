"""
设置标签页UI模块 - PyQt6版本
"""
import os
import shutil
import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea
from PyQt6.QtCore import Qt, QUrl
from qfluentwidgets import (
    PushButton, SettingCardGroup, SwitchSettingCard, SettingCard, OptionsSettingCard,
    PrimaryPushSettingCard, CardWidget, TitleLabel, BodyLabel,
    InfoBar, InfoBarPosition, setTheme, Theme, FluentIcon, ComboBox, ScrollArea
)

from src.config import ConfigManager


class SettingsTab(QWidget):
    """设置标签页类"""

    def __init__(self, parent=None):
        """
        初始化设置标签页
        
        Args:
            parent: 父级窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.config = ConfigManager.load_config()
        self.setup_ui()

    def setup_ui(self):
        """创建UI组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)
        
        # 添加标题
        title_label = TitleLabel("设置")
        description_label = BodyLabel("配置应用程序的外观和行为")
        description_label.setTextColor("gray")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        main_layout.addSpacing(10)
        
        # 创建滚动区域
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 确保滚动区域背景透明
        scroll_area.setStyleSheet("""
            ScrollArea {
                background-color: transparent;
                border: none;
            }
            QWidget {
                background-color: transparent;
            }
        """)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0)  # 右侧留出滚动条的空间
        scroll_layout.setSpacing(15)
        
        # 设置滚动内容背景为透明
        scroll_content.setStyleSheet("background-color: transparent;")
        
        # 禁用滚动区域的自动填充背景
        scroll_area.setAutoFillBackground(False)
        scroll_content.setAutoFillBackground(False)
        
        # 主题设置卡片组
        theme_group = SettingCardGroup("外观", self)
        
        # 主题选择 - 使用SettingCard
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["浅色", "深色"])
        self.theme_combo.setFixedWidth(120)
        
        # 设置当前值
        current_theme = self.config.get('theme', 'light')
        self.theme_combo.setCurrentText("浅色" if current_theme == "light" else "深色")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        # 创建设置卡并添加组合框
        theme_card = SettingCard(
            icon=FluentIcon.BRUSH,
            title="主题",
            content="更改应用程序的主题模式",
            parent=theme_group
        )
        theme_card.hBoxLayout.addWidget(self.theme_combo)
        
        # 亚克力效果开关
        enable_acrylic = self.config.get('enable_acrylic', True)
        acrylic_card = SwitchSettingCard(
            icon=FluentIcon.TRANSPARENT,
            title="亚克力效果",
            content="启用窗口亚克力背景效果（需要重启应用生效）",
            parent=theme_group
        )
        acrylic_card.setChecked(enable_acrylic)
        acrylic_card.checkedChanged.connect(self.toggle_acrylic)
        
        theme_group.addSettingCard(theme_card)
        theme_group.addSettingCard(acrylic_card)
        
        # 文件管理卡片组
        files_group = SettingCardGroup("文件管理", self)
        
        # 清除缓存
        self.clear_cache_card = PrimaryPushSettingCard(
            icon=FluentIcon.DELETE,
            title="清除缓存文件",
            content="删除所有缓存文件以释放磁盘空间",
            text="清除",
            parent=files_group
        )
        self.clear_cache_card.button.clicked.connect(self.clear_cache)
        
        files_group.addSettingCard(self.clear_cache_card)
        
        # 打开输出目录
        output_premul_card = PrimaryPushSettingCard(
            icon=FluentIcon.FOLDER,
            title="打开预乘透明输出目录",
            content="打开存放预乘透明图像的输出目录",
            text="打开",
            parent=files_group
        )
        output_premul_card.button.clicked.connect(lambda: self.open_directory("output_预乘透明"))
        
        output_straight_card = PrimaryPushSettingCard(
            icon=FluentIcon.FOLDER,
            title="打开直通透明输出目录",
            content="打开存放直通透明图像的输出目录",
            text="打开",
            parent=files_group
        )
        output_straight_card.button.clicked.connect(lambda: self.open_directory("output_直通透明"))
        
        files_group.addSettingCard(output_premul_card)
        files_group.addSettingCard(output_straight_card)
        
        # 关于信息卡片组
        about_group = SettingCardGroup("关于", self)
        
        # 版本和作者信息
        version_card = SwitchSettingCard(
            icon=FluentIcon.INFO,
            title="交错战线 Assets 工具 V1.0.0",
            content="作者: 路北路陈",
            parent=about_group
        )
        version_card.switchButton.setEnabled(False)
        
        # 项目仓库链接
        github_card = PrimaryPushSettingCard(
            icon=FluentIcon.GITHUB,
            title="项目源码",
            content="访问GitHub仓库查看源代码",
            text="访问",
            parent=about_group
        )
        github_card.button.clicked.connect(lambda: webbrowser.open("https://github.com/yourusername/jiaocha-assets-tool"))
        
        about_group.addSettingCard(version_card)
        about_group.addSettingCard(github_card)
        
        # 添加到滚动布局
        scroll_layout.addWidget(theme_group)
        scroll_layout.addWidget(files_group)
        scroll_layout.addWidget(about_group)
        scroll_layout.addStretch(1)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)

    def change_theme(self, theme_text):
        """
        更改应用程序主题
        
        Args:
            theme_text: 主题文本
        """
        new_theme = "light" if theme_text == "浅色" else "dark"
        self.config['theme'] = new_theme
        ConfigManager.save_config(self.config)
        
        # 应用主题
        setTheme(Theme.LIGHT if new_theme == "light" else Theme.DARK)
        
        # 显示通知
        InfoBar.success(
            title="成功",
            content=f"主题已设置为{theme_text}",
            orient=Qt.Orientation.Horizontal,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def clear_cache(self):
        """清除缓存文件"""
        cache_dir = Path("cache")
        if cache_dir.exists():
            try:
                # 删除缓存目录中的所有文件
                files_removed = 0
                for file in cache_dir.glob("*"):
                    if file.is_file():
                        file.unlink()
                        files_removed += 1
                    elif file.is_dir():
                        shutil.rmtree(file)
                        files_removed += 1

                # 显示成功消息
                InfoBar.success(
                    title="成功",
                    content=f"缓存文件已清除，共删除 {files_removed} 个文件",
                    orient=Qt.Orientation.Horizontal,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                # 显示错误消息
                InfoBar.error(
                    title="错误",
                    content=f"清除缓存时出错: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=5000,
                    parent=self
                )
        else:
            # 显示信息消息
            InfoBar.warning(
                title="注意",
                content="缓存目录不存在",
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
    
    def open_directory(self, directory):
        """打开指定目录"""
        try:
            path = Path(directory).absolute()
            path.mkdir(exist_ok=True)
            
            # 使用系统默认程序打开目录
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS 和 Linux
                os.system(f'xdg-open "{path}"')
                
            # 显示成功消息
            InfoBar.success(
                title="已打开",
                content=f"已打开目录: {directory}",
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        except Exception as e:
            # 显示错误消息
            InfoBar.error(
                title="错误",
                content=f"打开目录时出错: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            
    def save_config(self):
        """保存当前配置"""
        # 获取父窗口中的其他组件的配置
        try:
            from src.ui import CryptoTab
            crypto_tab = self.parent.findChild(CryptoTab)
            if crypto_tab:
                self.config['decrypt_path'] = crypto_tab.decrypt_entry.text()
                self.config['encrypt_path'] = crypto_tab.encrypt_entry.text()
                self.config['cache_file'] = crypto_tab.cache_entry.text()
        except Exception:
            pass
            
        # 保存配置
        ConfigManager.save_config(self.config)

    def toggle_acrylic(self, checked):
        """切换亚克力效果

        Args:
            checked: 是否启用亚克力效果
        """
        self.config['enable_acrylic'] = checked
        ConfigManager.save_config(self.config)
        
        # 显示提示，需要重启应用
        InfoBar.warning(
            title="需要重启",
            content="亚克力效果设置已更改，重启应用后生效",
            orient=Qt.Orientation.Horizontal,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )
