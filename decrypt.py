import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from binascii import hexlify, unhexlify
import ujson
from datetime import datetime

Executor = ThreadPoolExecutor(max_workers=50, thread_name_prefix="DecryptThread")


def find_next_unityFS_index(file_data: bytes):
    openFileHex = hexlify(file_data)
    unityFS_len = len(re.findall(b"556e6974794653000000000", openFileHex))
    if unityFS_len < 2:
        return -1
    else:
        find_index = len(re.search(b".+556e6974794653000000000", openFileHex).group()) - 23
        return len(unhexlify(openFileHex[:find_index]))


def decrypt_file(file_path: Path, log_callback):
    with file_path.open("rb") as f:
        data = f.read()

    header_len = find_next_unityFS_index(data)
    if header_len == -1:
        log_callback(f"文件 {file_path.name} 不包含有效的 UnityFS 头，跳过解密。\n")
        return file_path.name, header_len

    with file_path.open("wb") as f:
        f.write(data[header_len:])

    log_callback(f"文件 {file_path.name} 解密成功。\n")
    return file_path.name, header_len


def decrypt(game_bundles_path: Path, log_callback=None):
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    log_callback(f"开始解密 {game_bundles_path} 目录中的文件...\n")

    futures = []
    decrypt_result = {}

    for AssetFile in game_bundles_path.iterdir():
        futures.append(Executor.submit(decrypt_file, AssetFile, log_callback))

    for future in as_completed(futures):
        file_name, header_len = future.result()
        if header_len != -1:
            decrypt_result[file_name] = header_len

    # 创建 index_cache 文件夹和 index_cache_日期.json 文件
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_folder = Path("index_cache")
    cache_folder.mkdir(exist_ok=True)
    cache_file_path = cache_folder / f"index_cache_{date_str}.json"

    # 将解密结果写入新的 index_cache_日期.json 文件
    with cache_file_path.open("w", encoding="utf-8") as f:
        ujson.dump(decrypt_result, f)

    log_callback(f"解密操作完成。索引已保存到 {cache_file_path}\n")
