#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
版本更新脚本 - 用于更新版本号并创建Git标签
"""
import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def update_version(version):
    """更新版本号"""
    # 更新src/__init__.py中的版本号
    init_file = Path("src/__init__.py")
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        new_content = re.sub(r"__version__ = '[^']+'", f"__version__ = '{version}'", content)
        init_file.write_text(new_content, encoding="utf-8")
        print(f"已更新 src/__init__.py 中的版本号为 {version}")
    
    # 更新main.py中的版本号
    main_file = Path("main.py")
    if main_file.exists():
        content = main_file.read_text(encoding="utf-8")
        new_content = re.sub(r'self\.root\.title\("交错战线 Assets 工具 V[^"]+"\)', 
                            f'self.root.title("交错战线 Assets 工具 V{version}")', content)
        main_file.write_text(new_content, encoding="utf-8")
        print(f"已更新 main.py 中的版本号为 {version}")
    
    # 更新settings_tab.py中的版本号
    settings_file = Path("src/ui/settings_tab.py")
    if settings_file.exists():
        content = settings_file.read_text(encoding="utf-8")
        new_content = re.sub(r'self\.version_label = ttk\.Label\(self\.about_frame, text="交错战线 Assets 工具 V[^"]+"\)', 
                            f'self.version_label = ttk.Label(self.about_frame, text="交错战线 Assets 工具 V{version}")', content)
        settings_file.write_text(new_content, encoding="utf-8")
        print(f"已更新 src/ui/settings_tab.py 中的版本号为 {version}")

def update_changelog(version, message):
    """更新CHANGELOG.md文件"""
    changelog_file = Path("CHANGELOG.md")
    if not changelog_file.exists():
        print("错误: CHANGELOG.md文件不存在")
        return False
    
    content = changelog_file.read_text(encoding="utf-8")
    
    # 获取当前日期
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查是否有未发布的更改
    unreleased_match = re.search(r"## \[未发布\]\n\n(.*?)(?=\n## \[)", content, re.DOTALL)
    if not unreleased_match:
        print("警告: 在CHANGELOG.md中未找到未发布的更改")
        return False
    
    unreleased_content = unreleased_match.group(1)
    
    # 创建新版本的更新日志
    new_version_entry = f"## [{version}] - {today}\n\n{unreleased_content}"
    
    # 重置未发布的更改
    reset_unreleased = """## [未发布]

### 新增
- 

### 变更
- 

### 修复
- 

"""
    
    # 替换内容
    new_content = content.replace(f"## [未发布]\n\n{unreleased_content}", f"{reset_unreleased}{new_version_entry}")
    
    # 写入文件
    changelog_file.write_text(new_content, encoding="utf-8")
    print(f"已更新 CHANGELOG.md，添加了版本 {version} 的更新日志")
    
    return True

def create_git_tag(version, message):
    """创建Git标签并推送"""
    try:
        # 添加所有更改
        subprocess.run(["git", "add", "."], check=True)
        
        # 提交更改
        subprocess.run(["git", "commit", "-m", f"版本更新: v{version}"], check=True)
        
        # 创建标签
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", message], check=True)
        
        # 推送提交
        subprocess.run(["git", "push"], check=True)
        
        # 推送标签
        subprocess.run(["git", "push", "origin", f"v{version}"], check=True)
        
        print(f"已创建标签 v{version} 并推送到远程仓库")
        print("GitHub Actions将自动构建并发布此版本")
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python create_release.py <版本号> [发布说明]")
        print("示例: python create_release.py 1.0.0 '修复了一些bug'")
        return
    
    version = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else f"版本 {version} 发布"
    
    # 更新版本号
    update_version(version)
    
    # 更新更新日志
    update_changelog(version, message)
    
    # 创建Git标签
    create_git_tag(version, message)

if __name__ == "__main__":
    main() 