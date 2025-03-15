import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器，用于保存和加载用户配置"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            'recent_directories': [],
            'default_mode': 'extract',
            'video_extensions': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'max_recent_dirs': 10,
            'window_size': [900, 600],
            'splitter_position': [300, 600]
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置和加载的配置
                    for key, value in loaded_config.items():
                        default_config[key] = value
            except:
                pass
                
        return default_config
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项值
        """
        self.config[key] = value
        self._save_config()
    
    def add_recent_directory(self, directory: str):
        """
        添加最近使用的目录
        
        Args:
            directory: 目录路径
        """
        recent_dirs = self.get('recent_directories', [])
        
        # 如果已存在，先移除
        if directory in recent_dirs:
            recent_dirs.remove(directory)
            
        # 添加到列表开头
        recent_dirs.insert(0, directory)
        
        # 限制列表长度
        max_dirs = self.get('max_recent_dirs', 10)
        if len(recent_dirs) > max_dirs:
            recent_dirs = recent_dirs[:max_dirs]
            
        self.set('recent_directories', recent_dirs) 