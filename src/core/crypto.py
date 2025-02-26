"""
加密解密核心功能模块
"""
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from binascii import hexlify, unhexlify
import ujson
from datetime import datetime

# 创建线程池
DECRYPT_EXECUTOR = ThreadPoolExecutor(max_workers=50, thread_name_prefix="DecryptThread")
ENCRYPT_EXECUTOR = ThreadPoolExecutor(max_workers=50, thread_name_prefix="EncryptThread")


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
        find_index = len(re.search(b".+556e6974794653000000000", openFileHex).group()) - 23
        return len(unhexlify(openFileHex[:find_index]))


def decrypt_file(file_path: Path, log_callback):
    """
    解密单个文件
    
    Args:
        file_path: 文件路径
        log_callback: 日志回调函数
        
    Returns:
        tuple: (文件名, 头部长度)
    """
    with file_path.open("rb") as f:
        data = f.read()

    header_len = find_next_unityFS_index(data)
    if header_len == -1:
        log_callback(f"文件 {file_path.name} 不包含有效的 UnityFS 头，跳过解密。\n")
        return file_path.name, header_len

    with file_path.open("wb") as f:
        f.write(data[header_len:])

    log_callback(f"正在解密文件: {file_path.name}\n")
    return file_path.name, header_len


def decrypt(game_bundles_path: Path, log_callback=None):
    """
    解密指定目录下的所有文件
    
    Args:
        game_bundles_path: 游戏资源目录路径
        log_callback: 日志回调函数
        
    Returns:
        dict: 包含文件名和头部长度的字典
    """
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    if log_callback is None:
        log_callback = print

    log_callback(f"开始解密 {game_bundles_path} 目录中的文件...\n")

    # 创建缓存目录
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    # 创建缓存文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    cache_file = cache_dir / f"index_cache_{timestamp}.json"

    # 获取所有文件
    files = [f for f in game_bundles_path.glob("**/*") if f.is_file()]
    log_callback(f"找到 {len(files)} 个文件\n")

    # 使用线程池处理文件
    results = {}
    futures = {DECRYPT_EXECUTOR.submit(decrypt_file, file_path, log_callback): file_path for file_path in files}
    
    for future in as_completed(futures):
        file_name, header_len = future.result()
        if header_len != -1:
            results[str(futures[future].relative_to(game_bundles_path))] = header_len

    # 保存缓存
    with cache_file.open("w", encoding="utf-8") as f:
        ujson.dump(results, f, ensure_ascii=False, indent=2)

    log_callback(f"解密完成，共处理 {len(results)} 个文件\n")
    log_callback(f"索引缓存已保存到 {cache_file}\n")
    
    return results


def encode_file(file_path: Path, header_len, log_callback):
    """
    加密单个文件
    
    Args:
        file_path: 文件路径
        header_len: 头部长度
        log_callback: 日志回调函数
    """
    with file_path.open("rb") as f:
        data = f.read()

    enc_data = data[:header_len]
    with file_path.open("wb") as f:
        f.write(enc_data + data)

    log_callback(f"正在加密文件: {file_path.name}\n")


def encode(game_bundles_path: Path, cache_file, log_callback):
    """
    加密指定目录下的所有文件
    
    Args:
        game_bundles_path: 游戏资源目录路径
        cache_file: 缓存文件路径
        log_callback: 日志回调函数
    """
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    if not cache_file:
        raise FileNotFoundError("未指定index_cache文件")

    with open(cache_file, "r", encoding="utf-8") as f:
        cache_file_index = ujson.load(f)

    log_callback(f"开始加密 {game_bundles_path} 目录中的文件...\n")

    # 使用线程池处理文件
    futures = []
    for rel_path, header_len in cache_file_index.items():
        file_path = game_bundles_path / rel_path
        if file_path.exists():
            futures.append(ENCRYPT_EXECUTOR.submit(encode_file, file_path, header_len, log_callback))

    # 等待所有任务完成
    for future in as_completed(futures):
        future.result()

    log_callback(f"加密完成，共处理 {len(futures)} 个文件\n") 