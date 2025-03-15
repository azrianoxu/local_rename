from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QCheckBox,
                            QHeaderView, QPushButton, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor

from ..core.file_scanner import FileScanner
from ..core.rename_engine import RenameEngine

class PreviewPanel(QWidget):
    """预览面板，显示文件列表和重命名预览"""
    
    def __init__(self):
        super().__init__()
        
        self.file_scanner = FileScanner()
        self.rename_engine = RenameEngine()
        
        self.files = []
        self.new_names = {}
        self.checked_files = set()
        self.settings = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("全选")
        self.deselect_all_btn = QPushButton("全不选")
        self.video_only_checkbox = QCheckBox("仅显示视频文件")
        self.video_only_checkbox.setChecked(True)
        
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.deselect_all_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.video_only_checkbox)
        
        # 文件表格
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["选择", "原文件名", "新文件名"])
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # 状态信息
        self.status_label = QLabel()
        
        # 添加所有组件到主布局
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.file_table)
        main_layout.addWidget(self.status_label)
        
        # 连接信号
        self.select_all_btn.clicked.connect(self._select_all)
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        self.video_only_checkbox.stateChanged.connect(self._on_video_only_changed)
        
    @pyqtSlot(str)
    def load_files(self, directory):
        """加载指定目录的文件"""
        self.files = self.file_scanner.scan_directory(
            directory, 
            video_only=self.video_only_checkbox.isChecked()
        )
        
        # 猜测剧集名和季数
        if self.files:
            prefix = self.rename_engine.guess_prefix(self.files)
            season = self.rename_engine.guess_season(self.files)
            
            # 更新控制面板
            parent = self.parent()
            while parent and not hasattr(parent, 'control_panel'):
                parent = parent.parent()
                
            if parent and hasattr(parent, 'control_panel'):
                parent.control_panel.prefix_input.setText(prefix)
                parent.control_panel.season_input.setText(season)
        
        self._update_file_table()
        
    @pyqtSlot(dict)
    def update_preview(self, settings):
        """更新重命名预览"""
        self.settings = settings
        self.new_names = {}
        
        if not self.files:
            return
            
        # 生成新文件名预览
        for file in self.files:
            if settings['mode'] == 'extract':
                new_name = self.rename_engine.rename_by_extract(
                    file['name'],
                    settings['prefix'],
                    settings['season'],
                    {
                        'pre': settings['ep_helper_pre'],
                        'post': settings['ep_helper_post']
                    }
                )
            else:
                new_name = self.rename_engine.rename_by_regexp(
                    file['name'],
                    settings['from'],
                    settings['to']
                )
                
            if new_name and new_name != file['name']:
                self.new_names[file['file_id']] = new_name
                
        self._update_file_table()
        
        # 检查冲突
        self._check_conflicts()
        
    @pyqtSlot()
    def execute_rename(self):
        """执行重命名操作"""
        success_count = 0
        error_count = 0
        
        for file_id in self.checked_files:
            if file_id in self.new_names:
                file_info = next((f for f in self.files if f['file_id'] == file_id), None)
                if file_info:
                    success = self.rename_engine.execute_rename(
                        file_id,
                        self.new_names[file_id]
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
        
        # 重新加载文件列表
        if self.file_scanner.current_dir:
            self.load_files(self.file_scanner.current_dir)
            
        # 更新状态
        self.status_label.setText(f"重命名完成: 成功 {success_count}, 失败 {error_count}")
        
    def _update_file_table(self):
        """更新文件表格"""
        self.file_table.setRowCount(0)
        self.file_table.setRowCount(len(self.files))
        
        for row, file in enumerate(self.files):
            # 选择框
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            checkbox = QCheckBox()
            checkbox.setChecked(file['file_id'] in self.checked_files)
            checkbox.stateChanged.connect(lambda state, file_id=file['file_id']: self._on_checkbox_changed(state, file_id))
            
            checkbox_layout.addWidget(checkbox)
            self.file_table.setCellWidget(row, 0, checkbox_widget)
            
            # 原文件名
            name_item = QTableWidgetItem(file['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.file_table.setItem(row, 1, name_item)
            
            # 新文件名
            new_name = self.new_names.get(file['file_id'], '')
            new_name_item = QTableWidgetItem(new_name)
            new_name_item.setFlags(new_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # 设置颜色
            if new_name:
                new_name_item.setBackground(QColor(200, 255, 200))  # 浅绿色
                
            self.file_table.setItem(row, 2, new_name_item)
            
    def _on_checkbox_changed(self, state, file_id):
        """处理复选框状态变更"""
        if state == Qt.CheckState.Checked:
            self.checked_files.add(file_id)
        else:
            self.checked_files.discard(file_id)
            
        # 检查冲突
        self._check_conflicts()
            
    def _select_all(self):
        """全选"""
        for file in self.files:
            self.checked_files.add(file['file_id'])
        self._update_file_table()
        self._check_conflicts()
        
    def _deselect_all(self):
        """全不选"""
        self.checked_files.clear()
        self._update_file_table()
        self._check_conflicts()
        
    def _on_video_only_changed(self):
        """处理仅显示视频文件选项变更"""
        if self.file_scanner.current_dir:
            self.load_files(self.file_scanner.current_dir)
            
    def _check_conflicts(self):
        """检查文件名冲突"""
        new_names_list = [self.new_names.get(file_id) for file_id in self.checked_files if file_id in self.new_names]
        duplicates = set([name for name in new_names_list if new_names_list.count(name) > 1])
        
        if duplicates:
            self.status_label.setText(f"警告：检测到{len(duplicates)}个文件名冲突！")
            
            # 在表格中标记冲突项
            for row in range(self.file_table.rowCount()):
                file_id = self.files[row]['file_id']
                if file_id in self.checked_files and file_id in self.new_names:
                    new_name = self.new_names[file_id]
                    if new_name in duplicates:
                        self.file_table.item(row, 2).setBackground(QColor(255, 200, 200))  # 浅红色
                        
            # 禁用执行按钮
            parent = self.parent()
            while parent and not hasattr(parent, 'control_panel'):
                parent = parent.parent()
                
            if parent and hasattr(parent, 'control_panel'):
                parent.control_panel.run_button.setEnabled(False)
        else:
            # 如果没有冲突，启用执行按钮
            if self.checked_files and any(file_id in self.new_names for file_id in self.checked_files):
                parent = self.parent()
                while parent and not hasattr(parent, 'control_panel'):
                    parent = parent.parent()
                    
                if parent and hasattr(parent, 'control_panel'):
                    parent.control_panel.run_button.setEnabled(True)