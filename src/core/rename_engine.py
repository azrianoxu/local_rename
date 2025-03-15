import os
import re
from typing import List, Dict, Optional, Tuple

class RenameEngine:
    """处理文件重命名逻辑"""
    
    def __init__(self):
        self.season_episode_pattern = re.compile(r'S(?:eason)?[._\- ]?(\d{1,3})(?:[._\- ]?E|[._\- ])(\d{1,3})(?!\d)', re.IGNORECASE)
        self.episode_pattern1 = re.compile(r'EP?(\d{1,3})(?!\d)', re.IGNORECASE)
        self.episode_pattern2 = re.compile(r'(?<![0-9h\u4E00-\u9FA5])(\d{1,3})(?!\d)(?![PK季])')
        self.episode_pattern3 = re.compile(r'(?<![0-9h])(\d{1,3})(?!\d)(?![PK季])')
        self.chinese_pattern = re.compile(r'([\u4E00-\u9FA5]+)')
    
    def rename_by_regexp(self, old_name: str, pattern: str, replacement: str) -> str:
        """使用正则表达式重命名"""
        try:
            return re.sub(pattern, replacement, old_name)
        except:
            return ''
    
    def rename_by_extract(self, old_name: str, prefix: str, season: str, 
                          ep_helpers: Dict[str, str] = None, ref_name: str = None) -> str:
        """提取季集信息重命名"""
        if ep_helpers is None:
            ep_helpers = {'pre': '', 'post': ''}
            
        # 提取集数
        episode = None
        
        if ep_helpers['pre'] or ep_helpers['post']:
            episode = self._get_episode_by_helpers(old_name, ep_helpers)
            
        if not episode and ref_name:
            episode = self._get_episode_by_compare(old_name, ref_name)
            
        if not episode:
            episode = self._get_episode(old_name)
            
        # 标准化季数
        season = season or '1'
        try:
            season_number = int(season)
            if 0 <= season_number < 100:
                season = str(season_number).zfill(2)
            else:
                season = '01'
        except:
            season = '01'
            
        if not episode:
            return ''
            
        # 保留扩展名
        name, ext = os.path.splitext(old_name)
        return f"{prefix} S{season}E{episode}{ext}"
    
    def _get_episode(self, name: str) -> str:
        """从文件名中提取集数"""
        # 移除扩展名
        name = os.path.splitext(name)[0]
        
        # 尝试各种模式匹配
        match = self.season_episode_pattern.search(name)
        if match:
            return self._normalize_episode(match.group(2))
            
        match = self.episode_pattern1.search(name)
        if match:
            return self._normalize_episode(match.group(1))
            
        match = self.episode_pattern2.search(name)
        if match:
            return self._normalize_episode(match.group(1))
            
        match = self.episode_pattern3.search(name)
        if match:
            return self._normalize_episode(match.group(1))
            
        return '001'  # 默认值
    
    def _normalize_episode(self, episode: str) -> str:
        """标准化集数格式"""
        try:
            return str(int(episode)).zfill(3)
        except:
            return '001'
    
    def _get_episode_by_helpers(self, name: str, helpers: Dict[str, str]) -> Optional[str]:
        """使用辅助标记提取集数"""
        pre, post = helpers.get('pre', ''), helpers.get('post', '')
        
        if not pre and not post:
            return None
            
        pre_index = name.find(pre) if pre else 0
        post_index = name.rfind(post) if post else len(name)
        
        if pre_index == -1 and post_index == -1:
            return None
            
        shorted = name[pre_index + len(pre):post_index]
        episode = self._get_episode(shorted)
        
        try:
            return self._normalize_episode(episode)
        except:
            return None
    
    def _get_episode_by_compare(self, name: str, ref_name: str) -> Optional[str]:
        """通过比较两个文件名提取集数"""
        matches_old = [m.group(0) for m in re.finditer(r'\d+', name)]
        matches_ref = [m.group(0) for m in re.finditer(r'\d+', ref_name)]
        
        if not matches_old or len(matches_old) != len(matches_ref):
            return None
            
        diff = []
        for i in range(len(matches_old)):
            if matches_old[i] != matches_ref[i]:
                diff.append(matches_old[i])
                
        filtered = [x for x in diff if 0 < int(x) < 1000]
        
        return self._normalize_episode(filtered[0]) if len(filtered) == 1 else None
    
    def guess_prefix(self, file_list: List[Dict]) -> str:
        """猜测剧集名称"""
        if not file_list:
            return ''
            
        # 尝试提取中文名称
        match = self.chinese_pattern.search(file_list[0]['name'])
        if match:
            return match.group(1)
            
        # 如果只有一个文件
        if len(file_list) < 2:
            name = file_list[0]['name']
            base_name = os.path.splitext(name)[0]
            return re.sub(r'\s*S\d+E\d*|\s*E\d+', '', base_name, flags=re.IGNORECASE).strip()
            
        # 尝试找最长公共子串
        a = os.path.splitext(file_list[-2]['name'])[0]
        b = os.path.splitext(file_list[-1]['name'])[0]
        lcs = self._get_longest_common_substring(a, b)
        
        if lcs:
            return re.sub(r'\s*S\d+E\d*|\s*E\d+', '', lcs, flags=re.IGNORECASE).strip()
            
        return ''
    
    def guess_season(self, file_list: List[Dict]) -> str:
        """猜测季数"""
        current_season = '1'
        
        for file in file_list:
            match = self.season_episode_pattern.search(file['name'])
            if match:
                current_season = match.group(1)
                
        return current_season
    
    def _get_longest_common_substring(self, a: str, b: str) -> str:
        """获取两个字符串的最长公共子串"""
        if not a or not b:
            return ''
            
        len_a, len_b = len(a), len(b)
        cache = [[0 for _ in range(len_b)] for _ in range(2)]
        max_len, max_end = 0, 0
        
        for i in range(len_a):
            for j in range(len_b):
                if i == 0:
                    cache[0][j] = 1 if a[0] == b[j] else 0
                else:
                    cache[1][j] = cache[0][j-1] + 1 if a[i] == b[j] and j > 0 else (1 if a[i] == b[j] else 0)
                    
                    if cache[1][j] > max_len:
                        max_len = cache[1][j]
                        max_end = j
                        
            if i > 0:
                cache[0], cache[1] = cache[1], [0] * len_b
                
        return b[max_end - max_len + 1:max_end + 1] if max_len > 0 else ''
    
    def execute_rename(self, file_path: str, new_name: str) -> bool:
        """执行实际的文件重命名操作"""
        try:
            directory = os.path.dirname(file_path)
            new_path = os.path.join(directory, new_name)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path) and file_path != new_path:
                return False
                
            os.rename(file_path, new_path)
            return True
        except Exception as e:
            print(f"重命名文件时出错: {e}")
            return False 