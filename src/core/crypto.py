"""
加密解密核心功能模块
"""
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from binascii import hexlify, unhexlify
import ujson
from datetime import datetime

# 创建线程池，优化线程数
CPU_COUNT = os.cpu_count() or 4
DECRYPT_EXECUTOR = ThreadPoolExecutor(max_workers=CPU_COUNT*2, thread_name_prefix="DecryptThread")
ENCRYPT_EXECUTOR = ThreadPoolExecutor(max_workers=CPU_COUNT*2, thread_name_prefix="EncryptThread")


def find_next_unityFS_index(file_data: bytes):
    """
    查找UnityFS索引位置
    
    Args:
        file_data: 文件二进制数据
        
    Returns:
        int: UnityFS索引位置，如果未找到则返回-1
    """
    openFileHex = hexlify(file_data)
    unityFS_len = len(re.findall(b"556e6974794653000000000", openFileHex))
    if unityFS_len < 2:
        return -1
    else:
        unityFS_index = openFileHex.find(b"556e6974794653000000000")
        return unityFS_index


def decrypt_file(file_path: Path, log_callback):
    """
    解密单个文件
    
    Args:
        file_path: 文件路径
        log_callback: 日志回调函数
    
    Returns:
        bool: 解密是否成功
    """
    try:
        # 读取文件
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        # 查找索引
        unityFS_index = find_next_unityFS_index(file_data)
        if unityFS_index == -1:
            return False
        
        # 保存解密后的文件
        with open(file_path, "wb") as f:
            f.write(file_data[unityFS_index//2:])
        
        return True
    except Exception as e:
        log_callback(f"解密文件 {file_path.name} 时出错: {str(e)}")
        return False


def decrypt(game_bundles_path: Path, log_callback=None):
    """
    解密目录下的所有资源文件
    
    Args:
        game_bundles_path: 游戏资源目录
        log_callback: 日志回调函数
    """
    if log_callback is None:
        log_callback = print
    
    # 确保路径存在
    if not game_bundles_path.exists():
        log_callback(f"错误: 路径 {game_bundles_path} 不存在\n")
        return
    
    log_callback(f"正在扫描目录: {game_bundles_path}\n")
    start_time = time.time()
    
    # 收集所有文件
    all_files = list(game_bundles_path.glob("**/*"))
    bundle_files = [f for f in all_files if f.is_file() and not f.name.endswith((".meta", ".manifest", ".json"))]
    
    if not bundle_files:
        log_callback("未找到需要解密的文件\n")
        return
    
    log_callback(f"找到 {len(bundle_files)} 个可能需要解密的文件\n")
    log_callback("开始解密资源文件...\n")
    
    # 计数器
    successful = 0
    failed = 0
    skipped = 0
    total = len(bundle_files)
    last_progress = 0
    
    # 提交所有任务
    futures = {DECRYPT_EXECUTOR.submit(decrypt_file, file, log_callback): file for file in bundle_files}
    
    # 处理结果
    for i, future in enumerate(as_completed(futures), 1):
        file = futures[future]
        try:
            result = future.result()
            if result:
                successful += 1
                # 仅在完成重要进度时输出日志，减少日志刷屏
                progress = int(i / total * 100)
                if progress >= last_progress + 10 or i == total:
                    log_callback(f"进度: {progress}% ({i}/{total})")
                    last_progress = progress
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            log_callback(f"处理 {file.name} 时出错: {str(e)}")
    
    # 生成index_cache文件（存储目录信息）
    try:
        # 提取目录结构
        directory_structure = {}
        for file in bundle_files:
            rel_path = str(file.relative_to(game_bundles_path))
            directory_structure[rel_path] = str(rel_path)
        
        # 保存为JSON文件
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        
        cache_file = cache_dir / f"index_cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            ujson.dump(directory_structure, f, ensure_ascii=False, indent=2)
        
        log_callback(f"\n目录索引已保存至: {cache_file}\n")
    except Exception as e:
        log_callback(f"\n保存目录索引时出错: {str(e)}\n")
    
    # 打印统计信息
    elapsed = time.time() - start_time
    log_callback(f"\n解密完成! 耗时: {elapsed:.2f}秒")
    log_callback(f"成功: {successful}, 跳过: {skipped}, 失败: {failed}\n")


def encode_file(file_path: Path, header_len, log_callback):
    """
    加密单个文件
    
    Args:
        file_path: 文件路径
        header_len: 文件头长度
        log_callback: 日志回调函数
    
    Returns:
        bool: 加密是否成功
    """
    try:
        file_content = b""
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        encoded = file_content[header_len:]
        
        with open(file_path, "wb") as f:
            f.write(encoded)
        
        return True
    except Exception as e:
        log_callback(f"加密文件 {file_path.name} 时出错: {str(e)}")
        return False


def encode(game_bundles_path: Path, cache_file, log_callback):
    """
    加密目录下的所有资源文件
    
    Args:
        game_bundles_path: 游戏资源目录
        cache_file: 目录索引缓存文件
        log_callback: 日志回调函数
    """
    if log_callback is None:
        log_callback = print
    
    # 确保路径存在
    if not game_bundles_path.exists():
        log_callback(f"错误: 路径 {game_bundles_path} 不存在\n")
        return
    
    # 读取index_cache文件
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cache_data = ujson.load(f)
    except Exception as e:
        log_callback(f"加载index_cache文件时出错: {str(e)}\n")
        return
    
    log_callback(f"正在扫描目录: {game_bundles_path}\n")
    log_callback(f"使用索引文件: {cache_file}\n")
    start_time = time.time()
    
    # 收集要加密的文件
    bundle_files = []
    for rel_path in cache_data.keys():
        file_path = game_bundles_path / rel_path
        if file_path.exists() and file_path.is_file():
            bundle_files.append(file_path)
    
    if not bundle_files:
        log_callback("未找到需要加密的文件\n")
        return
    
    log_callback(f"找到 {len(bundle_files)} 个文件需要加密\n")
    log_callback("开始加密资源文件...\n")
    
    # 加载标准Header
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "header.txt"), "r") as f:
        header = f.read().strip()
    header_binary = unhexlify(header)
    header_len = 336
    
    # 计数器
    successful = 0
    failed = 0
    total = len(bundle_files)
    last_progress = 0
    
    # 提交所有任务
    futures = {ENCRYPT_EXECUTOR.submit(encode_file, file, header_len, log_callback): file for file in bundle_files}
    
    # 处理结果
    for i, future in enumerate(as_completed(futures), 1):
        file = futures[future]
        try:
            result = future.result()
            if result:
                successful += 1
                # 仅在完成重要进度时输出日志
                progress = int(i / total * 100)
                if progress >= last_progress + 10 or i == total:
                    log_callback(f"进度: {progress}% ({i}/{total})")
                    last_progress = progress
        except Exception as e:
            failed += 1
            log_callback(f"处理 {file.name} 时出错: {str(e)}")
    
    # 打印统计信息
    elapsed = time.time() - start_time
    log_callback(f"\n加密完成! 耗时: {elapsed:.2f}秒")
    log_callback(f"成功: {successful}, 失败: {failed}\n") 