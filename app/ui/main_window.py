"""
主窗口 UI
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QProgressBar, QInputDialog, QTabWidget,
    QFileDialog, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont, QColor, QTextCursor

from app.utils.stylesheet import get_main_stylesheet, darken_color

class GitHubManager(QMainWindow):
    """GitHub仓库智能管理器 - 主窗口 (纯UI)"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("智能开发工具套件 v3.0")
        self.setGeometry(100, 100, 1100, 800)
        self.setStyleSheet(get_main_stylesheet())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title_widget = self._create_title_widget()
        layout.addWidget(title_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 创建各个功能页
        git_tab = QWidget()
        sync_tab = QWidget()

        tab_widget.addTab(git_tab, "🚀 Git 仓库管理")
        tab_widget.addTab(sync_tab, "📦 文件同步覆盖")

        # 填充每个标签页的内容
        self._create_git_tab_ui(git_tab)
        self._create_sync_tab_ui(sync_tab)

        # 公共日志和进度条区域
        log_group = self._create_log_group()
        layout.addWidget(log_group)

        self.progress_bar = self._create_progress_bar()
        layout.addWidget(self.progress_bar)

        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("color: #10b981; font-weight: bold;")

    # --- Git 管理标签页 UI ---
    def _create_git_tab_ui(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 10, 5, 5)

        config_group = self._create_git_config_group()
        layout.addWidget(config_group)

        self.status_group = self._create_status_group()
        layout.addWidget(self.status_group)

        operations_group = self._create_operations_group()
        layout.addWidget(operations_group)

        layout.addStretch() # 添加弹性空间

    # --- 文件同步标签页 UI ---
    def _create_sync_tab_ui(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 10, 5, 5)

        path_panel = self._create_sync_path_panel()
        layout.addWidget(path_panel)

        group_panel = self._create_sync_group_panel()
        layout.addWidget(group_panel)

        act_layout = QHBoxLayout()
        act_layout.addStretch()
        self.sync_start_btn = QPushButton("开始覆盖")
        self.sync_start_btn.setProperty("role", "primary")
        self.sync_start_btn.setMinimumHeight(36)
        self.sync_start_btn.setFixedWidth(140)
        act_layout.addWidget(self.sync_start_btn)
        layout.addLayout(act_layout)

        layout.addStretch()

    def _create_title_widget(self):
        """创建标题区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 10px;
                padding: 12px;
            }
        """)

        layout = QHBoxLayout(widget)

        title = QLabel("🚀 智能开发工具套件")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        layout.addStretch()

        version = QLabel("v3.0 Integrated")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: rgba(255,255,255,0.8);")
        layout.addWidget(version)

        return widget

    def _create_git_config_group(self):
        group = QGroupBox("⚙ 仓库配置")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout(group)
        layout.setSpacing(8)

        layout.addWidget(QLabel("📁 本地路径:"), 0, 0)
        self.git_local_path_input = QLineEdit()
        layout.addWidget(self.git_local_path_input, 0, 1)

        self.git_browse_btn = QPushButton("📂 浏览")
        layout.addWidget(self.git_browse_btn, 0, 2)

        layout.addWidget(QLabel("🌐 远程仓库:"), 1, 0)
        self.git_remote_url_input = QLineEdit()
        layout.addWidget(self.git_remote_url_input, 1, 1, 1, 2)

        layout.addWidget(QLabel("👤 用户名:"), 2, 0)
        self.git_username_input = QLineEdit()
        layout.addWidget(self.git_username_input, 2, 1, 1, 2)

        layout.addWidget(QLabel("📧 邮箱:"), 3, 0)
        self.git_email_input = QLineEdit()
        layout.addWidget(self.git_email_input, 3, 1, 1, 2)

        button_layout = QHBoxLayout()
        self.git_load_config_btn = QPushButton("📂 加载配置")
        self.git_save_config_btn = QPushButton("💾 保存配置为...")
        self.git_refresh_btn = QPushButton("🔄 刷新状态")
        button_layout.addWidget(self.git_load_config_btn)
        button_layout.addWidget(self.git_save_config_btn)
        button_layout.addWidget(self.git_refresh_btn)
        layout.addLayout(button_layout, 4, 0, 1, 3)

        return group

    def _create_status_group(self):
        group = QGroupBox("📊 仓库状态")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout(group)

        self.branch_label = self._create_status_label("🌿 分支", "--", "#10b981")
        self.uncommitted_label = self._create_status_label("📝 未提交", "--", "#f59e0b")
        self.unpushed_label = self._create_status_label("📤 未推送", "--", "#3b82f6")
        self.sync_label = self._create_status_label("🔗 状态", "--", "#8b5cf6")

        layout.addWidget(self.branch_label, 0, 0)
        layout.addWidget(self.uncommitted_label, 0, 1)
        layout.addWidget(self.unpushed_label, 0, 2)
        layout.addWidget(self.sync_label, 0, 3)

        return group

    def _create_operations_group(self):
        group = QGroupBox("🎯 智能操作")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout(group)

        operations = [
            ("upload", "📤 智能上传", "#10b981"),
            ("download", "📥 智能下载", "#3b82f6"),
            ("sync", "🔄 智能同步", "#8b5cf6"),
            ("overwrite", "⚡ 强制覆盖", "#f59e0b"),
            ("delete", "🗑 清理远程", "#ef4444"),
            ("init", "🔧 初始化", "#06b6d4"),
        ]

        self.operation_buttons = {}
        for i, (op_name, text, color) in enumerate(operations):
            btn = self._create_operation_button(text, color)
            layout.addWidget(btn, i // 3, i % 3)
            self.operation_buttons[op_name] = btn

        return group

    def _create_sync_path_panel(self):
        panel = QGroupBox("路径设置")
        panel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout(panel)
        layout.setColumnStretch(1, 1)

        self.sync_edit_extract = QLineEdit()
        self.sync_edit_src = QLineEdit()
        self.sync_edit_dst = QLineEdit()
        self.sync_edit_main = QLineEdit()

        self._add_path_row(layout, 1, "解压目标文件夹", self.sync_edit_extract, "browse_extract")
        self._add_path_row(layout, 2, "来源文件夹", self.sync_edit_src, "browse_source", is_source=True)
        self._add_path_row(layout, 3, "目标文件夹", self.sync_edit_dst, "browse_target")
        self._add_path_row(layout, 4, "主程序路径", self.sync_edit_main, "browse_main")

        return panel

    def _create_sync_group_panel(self):
        panel = QGroupBox("路径分组")
        panel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout(panel)
        layout.setColumnStretch(1, 1)

        self.sync_edit_grp_name = QLineEdit()
        self.sync_save_group_btn = QPushButton("保存分组")

        self.sync_combo_grp = QComboBox()
        self.sync_load_group_btn = QPushButton("加载")
        self.sync_del_group_btn = QPushButton("×")
        self.sync_del_group_btn.setProperty("role", "danger")
        self.sync_del_group_btn.setFixedWidth(30)

        layout.addWidget(QLabel("分组名称"), 1, 0)
        layout.addWidget(self.sync_edit_grp_name, 1, 1)
        layout.addWidget(self.sync_save_group_btn, 1, 2)

        btn_container = QHBoxLayout()
        btn_container.addWidget(self.sync_load_group_btn)
        btn_container.addWidget(self.sync_del_group_btn)

        layout.addWidget(QLabel("选择分组"), 2, 0)
        layout.addWidget(self.sync_combo_grp, 2, 1)
        layout.addLayout(btn_container, 2, 2)

        return panel

    def _add_path_row(self, layout, row, label, edit_widget, btn_key, is_source=False):
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        if not hasattr(self, 'path_buttons'):
            self.path_buttons = {}

        if is_source:
            src_btn_container = QHBoxLayout()
            btn_prev = QPushButton("－")
            btn_next = QPushButton("＋")
            btn_browse = QPushButton("浏览")
            src_btn_container.addWidget(btn_prev)
            src_btn_container.addWidget(btn_next)
            src_btn_container.addWidget(btn_browse)
            layout.addWidget(lbl, row, 0)
            layout.addWidget(edit_widget, row, 1)
            layout.addLayout(src_btn_container, row, 2)
            self.path_buttons['prev_version'] = btn_prev
            self.path_buttons['next_version'] = btn_next
            self.path_buttons[btn_key] = btn_browse
        else:
            btn = QPushButton("浏览")
            layout.addWidget(lbl, row, 0)
            layout.addWidget(edit_widget, row, 1)
            layout.addWidget(btn, row, 2)
            self.path_buttons[btn_key] = btn

    # --- 公共/辅助 UI 创建函数 ---
    def _create_status_label(self, title, value, color):
        widget = QWidget()
        widget.setStyleSheet(f"background-color: #1f2937; border-left: 3px solid {color}; border-radius: 5px; padding: 6px;")
        layout = QVBoxLayout(widget)
        title_label = QLabel(title)
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none; background: transparent;")
        widget.value_label = value_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return widget

    def _create_operation_button(self, text, color):
        btn = QPushButton(text)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {darken_color(color)}); color: white; border-radius: 7px; }}
            QPushButton:hover {{ background: {darken_color(color)}; }}
        """)
        return btn

    def _create_log_group(self):
        group = QGroupBox("📋 操作日志")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.clear_log_btn = QPushButton("🧹 清空日志")
        layout.addWidget(self.log_text)
        layout.addWidget(self.clear_log_btn)
        return group

    def _create_progress_bar(self):
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #6366f1; border-radius: 8px; text-align: center; height: 30px; background-color: #1f2937; color: white; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6); border-radius: 6px; }
        """)
        return progress_bar

    # --- UI 更新和交互方法 ---
    def get_git_config_data(self):
        return {
            'local_path': self.git_local_path_input.text(),
            'remote_url': self.git_remote_url_input.text(),
            'username': self.git_username_input.text(),
            'email': self.git_email_input.text()
        }

    def set_git_config_data(self, config):
        self.git_local_path_input.setText(config.get('local_path', ''))
        self.git_remote_url_input.setText(config.get('remote_url', ''))
        self.git_username_input.setText(config.get('username', ''))
        self.git_email_input.setText(config.get('email', ''))

    def log(self, message, is_error=False):
        timestamp = QColor("#64748b")
        msg_color = QColor("#ef4444") if is_error else QColor("#e2e8f0")

        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        time_format = cursor.charFormat()
        time_format.setForeground(timestamp)
        cursor.setCharFormat(time_format)
        cursor.insertText(f"[{QTime.currentTime().toString('HH:mm:ss')}] ")

        msg_format = cursor.charFormat()
        msg_format.setForeground(msg_color)
        cursor.setCharFormat(msg_format)
        cursor.insertText(message + "\n")

        self.log_text.ensureCursorVisible()

    def update_status_display(self, branch, uncommitted, unpushed, sync_status):
        self.branch_label.value_label.setText(branch)
        self.uncommitted_label.value_label.setText(uncommitted)
        self.unpushed_label.value_label.setText(unpushed)
        self.sync_label.value_label.setText(sync_status)

    def get_delete_confirmation(self):
        text, ok = QInputDialog.getText(self, "确认删除", "请输入 'DELETE' 确认删除:")
        return ok and text == "DELETE"

    def refresh_sync_group_list(self, groups, select_item=None):
        self.sync_combo_grp.blockSignals(True)
        self.sync_combo_grp.clear()
        self.sync_combo_grp.addItems(list(groups.keys()))

        idx = self.sync_combo_grp.findText(select_item)
        if idx >= 0:
            self.sync_combo_grp.setCurrentIndex(idx)
        elif self.sync_combo_grp.count() > 0:
            self.sync_combo_grp.setCurrentIndex(0)
        self.sync_combo_grp.blockSignals(False)
