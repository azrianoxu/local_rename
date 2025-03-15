import json
import os
import time
from typing import List, Dict, Optional

class HistoryManager:
    """历史记录管理器，用于记录和恢复重命名操作"""
    
    def __init__(self, history_file: str = "rename_history.json"):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = history_file
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_record(self, directory: str, operations: List[Dict]):
        """
        添加历史记录
        
        Args:
            directory: 操作的目录
            operations: 操作列表，每项包含 {old_path, new_path, success}
        """
        record = {
            'timestamp': time.time(),
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S'),
            'directory': directory,
            'operations': operations
        }
        
        self.history.append(record)
        self._save_history()
    
    def get_records(self, count: Optional[int] = None) -> List[Dict]:
        """
        获取历史记录
        
        Args:
            count: 返回的记录数量，None表示全部
            
        Returns:
            历史记录列表
        """
        if count is None:
            return self.history
        return self.history[-count:]
    
    def undo_last_operation(self) -> bool:
        """
        撤销最后一次操作
        
        Returns:
            是否成功撤销
        """
        if not self.history:
            return False
        
        last_record = self.history[-1]
        success = True
        
        for op in reversed(last_record['operations']):
            if op['success']:
                try:
                    os.rename(op['new_path'], op['old_path'])
                except:
                    success = False
        
        if success:
            self.history.pop()
            self._save_history()
            
        return success 