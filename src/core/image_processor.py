"""
图像处理核心功能模块
"""
import os
from pathlib import Path
import threading
from PIL import Image
import numpy as np


def premultiply_alpha(img):
    """
    将直通透明转换为预乘透明
    
    Args:
        img: PIL图像对象
        
    Returns:
        PIL.Image: 处理后的图像
    """
    matrix = np.array(img, dtype=int)
    for row in matrix:
        for pixel in row:
            if pixel[3] == 255:
                continue
            elif pixel[3] == 0:
                pixel[0] = pixel[1] = pixel[2] = 0
            else:
                for i in range(3):
                    pixel[i] = pixel[i] * pixel[3] // 255
    matrix = matrix.astype("uint8")
    return Image.fromarray(matrix)


def straight_alpha(img):
    """
    将预乘透明转换为直通透明
    
    Args:
        img: PIL图像对象
        
    Returns:
        PIL.Image: 处理后的图像
    """
    matrix = np.array(img)
    for row in matrix:
        for pixel in row:
            rgb = pixel[:-1]
            alpha = pixel[-1]
            if alpha != 0 and alpha != 255:
                maxrgb = max(rgb)
                if maxrgb > alpha:
                    for i in range(3):
                        pixel[i] = rgb[i] * 255 // maxrgb
                else:
                    for i in range(3):
                        pixel[i] = rgb[i] * 255 // alpha
    return Image.fromarray(matrix)


def process_image_file(file_path, output_dir, conversion_function, log_callback=None):
    """
    处理单个图像文件
    
    Args:
        file_path: 图像文件路径
        output_dir: 输出目录
        conversion_function: 转换函数
        log_callback: 日志回调函数
        
    Returns:
        bool: 处理是否成功
    """
    if log_callback is None:
        log_callback = print
        
    try:
        # 打开图像
        img = Image.open(file_path)
        
        # 检查是否有Alpha通道
        if img.mode != 'RGBA':
            if img.mode == 'RGB':
                # 转换为RGBA模式
                img = img.convert('RGBA')
            else:
                log_callback(f"跳过 {file_path.name} - 不支持的图像模式: {img.mode}\n")
                return False
        
        # 应用转换
        processed_img = conversion_function(img)
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存处理后的图像
        output_path = output_dir / file_path.name
        processed_img.save(output_path)
        
        log_callback(f"已处理: {file_path.name}\n")
        return True
    except Exception as e:
        log_callback(f"处理 {file_path.name} 时出错: {str(e)}\n")
        return False


def batch_process_images(file_paths, conversion_function, log_callback=None):
    """
    批量处理图像文件
    
    Args:
        file_paths: 图像文件路径列表
        conversion_function: 转换函数
        log_callback: 日志回调函数
        
    Returns:
        int: 成功处理的文件数量
    """
    if log_callback is None:
        log_callback = print
    
    # 创建输出目录
    conversion_name = "预乘透明" if conversion_function == premultiply_alpha else "直通透明"
    output_dir = Path(f"output_{conversion_name}")
    output_dir.mkdir(exist_ok=True)
    
    log_callback(f"开始处理 {len(file_paths)} 个文件，转换为{conversion_name}...\n")
    
    # 创建线程列表
    threads = []
    success_count = 0
    
    # 创建线程锁，用于同步计数
    lock = threading.Lock()
    
    def process_file(file_path):
        nonlocal success_count
        result = process_image_file(file_path, output_dir, conversion_function, log_callback)
        if result:
            with lock:
                success_count += 1
    
    # 创建并启动线程
    for file_path in file_paths:
        thread = threading.Thread(target=process_file, args=(file_path,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    log_callback(f"处理完成，成功转换 {success_count}/{len(file_paths)} 个文件\n")
    log_callback(f"输出目录: {output_dir.absolute()}\n")
    
    return success_count 