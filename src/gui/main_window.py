import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QFileDialog, QMessageBox, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from .control_panel import ControlPanel
from .preview_panel import PreviewPanel
from ..core.config_manager import ConfigManager
from ..core.history_manager import HistoryManager

class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化配置和历史记录管理器
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager()
        
        self.setWindowTitle("本地剧集重命名工具")
        
        # 设置窗口大小
        window_size = self.config_manager.get('window_size', [900, 600])
        self.resize(window_size[0], window_size[1])
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建控制面板和预览面板
        self.control_panel = ControlPanel()
        self.preview_panel = PreviewPanel()
        
        # 设置面板之间的通信
        self.control_panel.rename_settings_changed.connect(self.preview_panel.update_preview)
        self.control_panel.directory_changed.connect(self.preview_panel.load_files)
        self.control_panel.execute_rename.connect(self.preview_panel.execute_rename)
        
        # 添加面板到分割器
        self.splitter.addWidget(self.control_panel)
        self.splitter.addWidget(self.preview_panel)
        
        # 设置初始分割比例
        splitter_position = self.config_manager.get('splitter_position', [300, 600])
        self.splitter.setSizes(splitter_position)
        
        # 添加分割器到主布局
        main_layout.addWidget(self.splitter)
        
        # 设置菜单栏
        self._setup_menu()
        
    def _setup_menu(self):
        """设置菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 打开文件夹动作
        open_action = QAction("打开文件夹", self)
        open_action.triggered.connect(self._open_directory)
        file_menu.addAction(open_action)
        
        # 最近打开的文件夹
        self.recent_menu = QMenu("最近打开", self)
        file_menu.addMenu(self.recent_menu)
        self._update_recent_menu()
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        
        # 撤销动作
        undo_action = QAction("撤销上次操作", self)
        undo_action.triggered.connect(self._undo_last_operation)
        edit_menu.addAction(undo_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _update_recent_menu(self):
        """更新最近打开的文件夹菜单"""
        self.recent_menu.clear()
        
        recent_dirs = self.config_manager.get('recent_directories', [])
        
        if not recent_dirs:
            no_recent_action = QAction("无最近记录", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
            return
        
        for directory in recent_dirs:
            action = QAction(directory, self)
            action.triggered.connect(lambda checked=False, dir=directory: self._open_recent_directory(dir))
            self.recent_menu.addAction(action)
        
        self.recent_menu.addSeparator()
        clear_action = QAction("清除记录", self)
        clear_action.triggered.connect(self._clear_recent_directories)
        self.recent_menu.addAction(clear_action)
        
    def _open_directory(self):
        """打开文件夹对话框"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择文件夹", os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.control_panel.set_directory(directory)
            self.config_manager.add_recent_directory(directory)
            self._update_recent_menu()
            
    def _open_recent_directory(self, directory):
        """打开最近使用的目录"""
        if os.path.exists(directory):
            self.control_panel.set_directory(directory)
            self.config_manager.add_recent_directory(directory)
        else:
            QMessageBox.warning(self, "目录不存在", f"目录 {directory} 不存在或无法访问。")
            
            # 从最近列表中移除
            recent_dirs = self.config_manager.get('recent_directories', [])
            if directory in recent_dirs:
                recent_dirs.remove(directory)
                self.config_manager.set('recent_directories', recent_dirs)
                self._update_recent_menu()
                
    def _clear_recent_directories(self):
        """清除最近打开的目录记录"""
        self.config_manager.set('recent_directories', [])
        self._update_recent_menu()
        
    def _undo_last_operation(self):
        """撤销上次操作"""
        if self.history_manager.undo_last_operation():
            QMessageBox.information(self, "撤销成功", "已成功撤销上次重命名操作。")
            
            # 重新加载当前目录
            if self.control_panel.current_directory:
                self.preview_panel.load_files(self.control_panel.current_directory)
        else:
            QMessageBox.warning(self, "撤销失败", "无法撤销操作或没有可撤销的操作。")
            
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于本地剧集重命名工具",
            "本地剧集重命名工具 v1.0\n\n"
            "一个用于批量重命名本地磁盘上剧集文件的Python工具。\n\n"
            "基于drive-rename项目改造。"
        )
        
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 保存窗口大小
        self.config_manager.set('window_size', [self.width(), self.height()])
        
        # 保存分割器位置
        splitter_sizes = self.splitter.sizes()
        self.config_manager.set('splitter_position', splitter_sizes)
        
        event.accept() 