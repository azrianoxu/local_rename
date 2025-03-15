import os
from pathlib import Path
from typing import List, Dict, Optional

class FileScanner:
    """扫描本地文件夹并获取文件列表"""
    
    VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    
    def __init__(self):
        self.current_dir = None
        
    def scan_directory(self, directory_path: str, video_only: bool = True) -> List[Dict]:
        """扫描指定目录并返回文件列表"""
        self.current_dir = directory_path
        files = []
        
        try:
            for item in os.listdir(directory_path):
                full_path = os.path.join(directory_path, item)
                
                if os.path.isfile(full_path):
                    _, ext = os.path.splitext(item)
                    
                    if video_only and ext.lower() not in self.VIDEO_EXTENSIONS:
                        continue
                        
                    files.append({
                        'file_id': full_path,  # 使用完整路径作为唯一ID
                        'name': item,
                        'type': 'file',
                        'file_extension': ext[1:] if ext else '',
                        'parent_path': directory_path
                    })
            
            return sorted(files, key=lambda x: x['name'])
        except Exception as e:
            print(f"扫描目录时出错: {e}")
            return [] 