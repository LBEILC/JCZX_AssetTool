import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import ujson

Executor = ThreadPoolExecutor(max_workers=50, thread_name_prefix="EncryptThread")


def encode_file(file_path: Path, header_len, log_callback):
    with file_path.open("rb") as f:
        data = f.read()

    enc_data = data[:header_len]
    with file_path.open("wb") as f:
        f.write(enc_data + data)

    log_callback(f"正在加密文件: {file_path.name}\n")


def encode(game_bundles_path: Path, cache_file, log_callback):
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    if not cache_file:
        raise FileNotFoundError("未指定index_cache文件")

    with open(cache_file, "r", encoding="utf-8") as f:
        cache_file_index = ujson.load(f)

    log_callback(f"开始加密 {game_bundles_path} 目录中的文件...\n")

    futures = []

    for AssetFile in game_bundles_path.iterdir():
        header_len = cache_file_index.get(AssetFile.name)
        if header_len is None:
            log_callback(f"{AssetFile.name} 加密失败, 未找到索引, 请重新解密后再加密\n")
            continue
        futures.append(Executor.submit(encode_file, AssetFile, header_len, log_callback))

    for future in as_completed(futures):
        future.result()  # 我们不需要结果，但这会确保任务完成

    log_callback("加密操作完成。\n")
