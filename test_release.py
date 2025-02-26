#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试版本更新脚本 - 用于测试版本更新流程，不会实际提交到Git
"""
import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_files():
    """备份将要修改的文件"""
    files_to_backup = [
        "src/__init__.py",
        "main.py",
        "src/ui/settings_tab.py",
        "CHANGELOG.md"
    ]
    
    for file_path in files_to_backup:
        path = Path(file_path)
        if path.exists():
            backup_path = Path(f"{file_path}.bak")
            shutil.copy2(path, backup_path)
            print(f"已备份 {file_path} 到 {backup_path}")

def restore_files():
    """恢复备份的文件"""
    backup_files = list(Path(".").glob("**/*.bak"))
    
    for backup_path in backup_files:
        original_path = Path(str(backup_path)[:-4])  # 移除.bak后缀
        shutil.copy2(backup_path, original_path)
        backup_path.unlink()  # 删除备份文件
        print(f"已恢复 {original_path}")

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

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_release.py <版本号> [发布说明]")
        print("示例: python test_release.py 1.0.0 '修复了一些bug'")
        return
    
    version = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else f"版本 {version} 发布"
    
    try:
        # 备份文件
        backup_files()
        
        # 更新版本号
        update_version(version)
        
        # 更新更新日志
        update_changelog(version, message)
        
        print("\n测试完成！这些更改没有提交到Git。")
        print("请检查文件更改是否符合预期。")
        
        # 询问是否恢复文件
        response = input("\n是否恢复文件到原始状态？(y/n): ")
        if response.lower() == 'y':
            restore_files()
            print("所有文件已恢复到原始状态。")
        else:
            print("文件保持更改状态。如需恢复，请手动运行 'python test_release.py restore'")
    
    except Exception as e:
        print(f"发生错误: {e}")
        restore_files()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_files()
    else:
        main() 