#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交错战线 Assets 工具主程序 - PyQt6重构版
"""
import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon, isDarkTheme
from qfluentwidgets import setTheme, Theme, SplashScreen

# 导入自定义模块
from src.config import ConfigManager
from src.ui import CryptoTab, ImageTab, SettingsTab


class MainWindow(FluentWindow):
    """主应用程序窗口"""
    
    def __init__(self):
        """初始化主应用程序"""
        super().__init__()
        self.setWindowTitle("交错战线 Assets 工具 V1.0.0")
        
        # 设置应用图标
        app_icon = QIcon("resources/icons/app_icon.png")
        self.setWindowIcon(app_icon)
        
        # 确保目录存在
        self._ensure_directories()
        
        # 加载配置
        self.config = ConfigManager.load_config()
        
        # 应用主题
        theme_name = self.config.get('theme', 'light')
        setTheme(Theme.LIGHT if theme_name == 'light' else Theme.DARK)
        
        # 设置窗口大小和位置
        self.resize(900, 650)
        self.center_window()
        
        # 启用亚克力效果
        # 检查配置中是否启用了亚克力效果，默认为True
        enable_acrylic = self.config.get('enable_acrylic', True)
        if enable_acrylic:
            # 尝试使用Mica效果作为替代
            self.setMicaEffectEnabled(True)
        
        # 创建UI组件
        self.init_ui()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 创建缓存和输出目录
        directories = [
            Path("cache"),
            Path("output_预乘透明"),
            Path("output_直通透明"),
            Path("resources/icons"),
            Path("resources/logs")
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
    
    def center_window(self):
        """使窗口居中显示"""
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def init_ui(self):
        """初始化UI界面"""
        # 创建标签页
        self.crypto_tab = CryptoTab(self)
        self.crypto_tab.setObjectName("cryptoTab")
        
        self.image_tab = ImageTab(self)
        self.image_tab.setObjectName("imageTab")
        
        self.settings_tab = SettingsTab(self)
        self.settings_tab.setObjectName("settingsTab")
        
        # 添加到导航栏
        self.addSubInterface(self.crypto_tab, 
                            FluentIcon.CERTIFICATE, 
                            "加密/解密", 
                            NavigationItemPosition.TOP)
        
        self.addSubInterface(self.image_tab, 
                            FluentIcon.PHOTO, 
                            "图片处理", 
                            NavigationItemPosition.TOP)
        
        self.addSubInterface(self.settings_tab, 
                            FluentIcon.SETTING, 
                            "设置", 
                            NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 保存配置
        self.settings_tab.save_config()
        super().closeEvent(event)


def show_splash_screen():
    """显示启动页"""
    # 创建启动页
    splash_pix = QPixmap("resources/icons/splash.png")
    
    # 如果图片不存在，创建简单的启动页
    if splash_pix.isNull():
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.GlobalColor.white)
    
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    
    return splash


def main():
    """主函数"""
    # 在创建应用程序前设置高DPI缩放策略
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # 创建并运行应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("交错战线Assets工具")
    
    # 设置默认图标
    app_icon = QIcon("resources/icons/app_icon.png")
    app.setWindowIcon(app_icon)
    
    # 显示启动页
    splash = show_splash_screen()
    
    # 创建主窗口
    window = MainWindow()
    
    # 延迟关闭启动页并显示主窗口
    QTimer.singleShot(1500, lambda: (splash.close(), window.show()))
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
