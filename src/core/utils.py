import os
import random
from typing import List, Dict, Any, Optional

def get_file_size_str(size_bytes: int) -> str:
    """
    将文件大小转换为人类可读的字符串
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化后的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息字典
    """
    try:
        stat = os.stat(file_path)
        name = os.path.basename(file_path)
        _, ext = os.path.splitext(name)
        
        return {
            'name': name,
            'path': file_path,
            'size': stat.st_size,
            'size_str': get_file_size_str(stat.st_size),
            'modified': stat.st_mtime,
            'extension': ext[1:] if ext else '',
            'is_dir': os.path.isdir(file_path)
        }
    except Exception as e:
        print(f"获取文件信息失败: {e}")
        return {}

def is_video_file(file_path: str, extensions: List[str] = None) -> bool:
    """
    检查文件是否为视频文件
    
    Args:
        file_path: 文件路径
        extensions: 视频文件扩展名列表
        
    Returns:
        是否为视频文件
    """
    if extensions is None:
        extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
        
    _, ext = os.path.splitext(file_path)
    return ext.lower() in extensions

def random_color() -> str:
    """
    生成随机颜色（十六进制格式）
    
    Returns:
        颜色字符串，如 "#FF0000"
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def ensure_dir(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功创建或已存在
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    return True 