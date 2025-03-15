from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QRadioButton, QButtonGroup, 
                            QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QWidget):
    """控制面板，用于设置重命名规则"""
    
    # 信号定义
    rename_settings_changed = pyqtSignal(dict)  # 重命名设置变更信号
    directory_changed = pyqtSignal(str)  # 目录变更信号
    execute_rename = pyqtSignal()  # 执行重命名信号
    
    def __init__(self):
        super().__init__()
        
        self.current_directory = None
        self.active_mode = "extract"  # 默认为剧集模式
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 模式选择
        mode_group = QGroupBox("重命名模式")
        mode_layout = QHBoxLayout()
        
        self.extract_mode = QRadioButton("剧集模式")
        self.regexp_mode = QRadioButton("正则模式")
        self.extract_mode.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.extract_mode, 1)
        self.mode_group.addButton(self.regexp_mode, 2)
        
        mode_layout.addWidget(self.extract_mode)
        mode_layout.addWidget(self.regexp_mode)
        mode_group.setLayout(mode_layout)
        
        # 剧集模式设置
        self.extract_group = QGroupBox("剧集设置")
        extract_layout = QFormLayout()
        
        self.prefix_input = QLineEdit()
        self.season_input = QLineEdit()
        self.ep_helper_pre = QLineEdit()
        self.ep_helper_post = QLineEdit()
        
        extract_layout.addRow("剧名:", self.prefix_input)
        extract_layout.addRow("季数:", self.season_input)
        
        helper_layout = QHBoxLayout()
        helper_layout.addWidget(QLabel("辅助定位集数:"))
        helper_layout.addWidget(self.ep_helper_pre)
        helper_layout.addWidget(QLabel("[集数]"))
        helper_layout.addWidget(self.ep_helper_post)
        
        extract_layout.addRow(helper_layout)
        self.extract_group.setLayout(extract_layout)
        
        # 正则模式设置
        self.regexp_group = QGroupBox("正则设置")
        regexp_layout = QFormLayout()
        
        self.from_input = QLineEdit()
        self.to_input = QLineEdit()
        
        regexp_layout.addRow("匹配模式:", self.from_input)
        regexp_layout.addRow("替换为:", self.to_input)
        self.regexp_group.setLayout(regexp_layout)
        self.regexp_group.setVisible(False)
        
        # 执行按钮
        self.run_button = QPushButton("执行重命名")
        self.run_button.setEnabled(False)
        
        # 状态信息
        self.status_label = QLabel()
        
        # 添加所有组件到主布局
        main_layout.addWidget(mode_group)
        main_layout.addWidget(self.extract_group)
        main_layout.addWidget(self.regexp_group)
        main_layout.addStretch()
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.run_button)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 模式切换
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        
        # 输入变更
        self.prefix_input.textChanged.connect(self._on_settings_changed)
        self.season_input.textChanged.connect(self._on_settings_changed)
        self.ep_helper_pre.textChanged.connect(self._on_settings_changed)
        self.ep_helper_post.textChanged.connect(self._on_settings_changed)
        self.from_input.textChanged.connect(self._on_settings_changed)
        self.to_input.textChanged.connect(self._on_settings_changed)
        
        # 执行按钮
        self.run_button.clicked.connect(self.execute_rename)
        
    def _on_mode_changed(self, button):
        """处理模式变更"""
        if button == self.extract_mode:
            self.active_mode = "extract"
            self.extract_group.setVisible(True)
            self.regexp_group.setVisible(False)
        else:
            self.active_mode = "regexp"
            self.extract_group.setVisible(False)
            self.regexp_group.setVisible(True)
            
        self._on_settings_changed()
        
    def _on_settings_changed(self):
        """处理设置变更"""
        settings = {
            'mode': self.active_mode,
            'prefix': self.prefix_input.text(),
            'season': self.season_input.text(),
            'ep_helper_pre': self.ep_helper_pre.text(),
            'ep_helper_post': self.ep_helper_post.text(),
            'from': self.from_input.text(),
            'to': self.to_input.text()
        }
        
        # 检查是否可以启用执行按钮
        can_run = False
        if self.active_mode == "extract":
            can_run = bool(settings['prefix'] and settings['season'])
        else:
            can_run = bool(settings['from'] and settings['to'])
            
        self.run_button.setEnabled(can_run and self.current_directory is not None)
        
        # 发送设置变更信号
        self.rename_settings_changed.emit(settings)
        
    def set_directory(self, directory):
        """设置当前目录"""
        self.current_directory = directory
        self.directory_changed.emit(directory)
        self._on_settings_changed()  # 重新检查按钮状态
        
    def set_status(self, message):
        """设置状态信息"""
        self.status_label.setText(message) 