"""
配置管理模块，负责应用程序配置的加载和保存 - PyQt6版本
"""
import json
import os
from pathlib import Path

# 配置文件路径
CONFIG_FILE = 'app_config.json'

class ConfigManager:
    """配置管理类，处理应用程序配置的加载和保存"""
    
    @staticmethod
    def get_default_config():
        """获取默认配置"""
        return {
            'theme': 'light',  # 改为light/dark主题
            'decrypt_path': '',
            'encrypt_path': '',
            'cache_file': '',
            'last_image_dir': ''
        }
    
    @staticmethod
    def load_config():
        """加载配置文件，如果不存在则返回默认配置"""
        default_config = ConfigManager.get_default_config()
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 兼容旧版配置(ttkbootstrap主题到light/dark主题的转换)
                if 'theme' in config and config['theme'] not in ['light', 'dark']:
                    config['theme'] = 'light'  # 默认使用浅色主题
                    
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
    
    @staticmethod
    def save_config(config):
        """保存配置到文件"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def update_config(key, value):
        """更新单个配置项"""
        config = ConfigManager.load_config()
        config[key] = value
        ConfigManager.save_config(config) 