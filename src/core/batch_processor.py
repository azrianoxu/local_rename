import os
import time
from typing import List, Dict, Callable

class BatchProcessor:
    """批量处理器，用于处理大量文件的重命名操作"""
    
    def __init__(self, callback: Callable[[str, int, int], None] = None):
        """
        初始化批处理器
        
        Args:
            callback: 进度回调函数，参数为(状态消息, 当前进度, 总数)
        """
        self.callback = callback
        
    def process(self, files: List[Dict], new_names: Dict[str, str]) -> Dict[str, bool]:
        """
        批量处理文件重命名
        
        Args:
            files: 文件列表
            new_names: 新文件名映射 {file_id: new_name}
            
        Returns:
            处理结果 {file_id: success}
        """
        results = {}
        total = len(new_names)
        processed = 0
        
        # 检查冲突
        if self._check_conflicts(files, new_names):
            if self.callback:
                self.callback("检测到文件名冲突，操作已取消", 0, total)
            return {}
        
        # 执行重命名
        for file in files:
            file_id = file['file_id']
            if file_id in new_names:
                processed += 1
                
                if self.callback:
                    self.callback(f"正在处理 ({processed}/{total}): {file['name']}", processed, total)
                
                # 添加延迟以避免系统过载
                time.sleep(0.05)
                
                try:
                    directory = os.path.dirname(file_id)
                    new_path = os.path.join(directory, new_names[file_id])
                    
                    os.rename(file_id, new_path)
                    results[file_id] = True
                except Exception as e:
                    print(f"重命名失败 {file_id}: {e}")
                    results[file_id] = False
        
        if self.callback:
            self.callback("处理完成", total, total)
            
        return results
    
    def _check_conflicts(self, files: List[Dict], new_names: Dict[str, str]) -> bool:
        """检查是否有文件名冲突"""
        # 按目录分组
        by_dir = {}
        for file in files:
            file_id = file['file_id']
            if file_id in new_names:
                directory = os.path.dirname(file_id)
                if directory not in by_dir:
                    by_dir[directory] = []
                by_dir[directory].append((file_id, new_names[file_id]))
        
        # 检查每个目录中的冲突
        for directory, file_pairs in by_dir.items():
            new_name_set = set()
            for _, new_name in file_pairs:
                if new_name in new_name_set:
                    return True
                new_name_set.add(new_name)
                
                # 检查是否与现有文件冲突（排除自身）
                full_path = os.path.join(directory, new_name)
                if os.path.exists(full_path) and not any(file_id == full_path for file_id, _ in file_pairs):
                    return True
        
        return False 