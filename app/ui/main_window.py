"""
主窗口 UI
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QProgressBar, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from app.utils.stylesheet import get_main_stylesheet, darken_color

class GitHubManager(QMainWindow):
    """GitHub仓库智能管理器 - 主窗口 (纯UI)"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub 仓库智能管理器 v2.0 Professional")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet(get_main_stylesheet())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title_widget = self._create_title_widget()
        layout.addWidget(title_widget)

        config_group = self._create_config_group()
        layout.addWidget(config_group)

        self.status_group = self._create_status_group()
        layout.addWidget(self.status_group)

        operations_group = self._create_operations_group()
        layout.addWidget(operations_group)

        log_group = self._create_log_group()
        layout.addWidget(log_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #6366f1;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                background-color: #1f2937;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("color: #10b981; font-weight: bold;")

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

        title = QLabel("🚀 GitHub 仓库智能管理器")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        layout.addStretch()

        version = QLabel("v2.0 Professional")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: rgba(255,255,255,0.8);")
        layout.addWidget(version)

        return widget

    def _create_config_group(self):
        """创建配置组"""
        group = QGroupBox("⚙ 仓库配置")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 10, 8, 8)

        layout.addWidget(QLabel("📁 本地路径:"), 0, 0)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("例如: G:\\PYthon\\GitHub 仓库管理")
        layout.addWidget(self.local_path_input, 0, 1)

        self.browse_btn = QPushButton("📂 浏览")
        self.browse_btn.setFixedWidth(100)
        layout.addWidget(self.browse_btn, 0, 2)

        layout.addWidget(QLabel("🌐 远程仓库:"), 1, 0)
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText("https://github.com/username/repo.git")
        layout.addWidget(self.remote_url_input, 1, 1, 1, 2)

        layout.addWidget(QLabel("👤 用户名:"), 2, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Git用户名 (可选)")
        layout.addWidget(self.username_input, 2, 1, 1, 2)

        layout.addWidget(QLabel("📧 邮箱:"), 3, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Git邮箱 (可选)")
        layout.addWidget(self.email_input, 3, 1, 1, 2)

        button_layout = QHBoxLayout()

        self.load_config_btn = QPushButton("📂 加载配置")
        self.load_config_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #22c55e, stop:1 #16a34a);
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16a34a, stop:1 #15803d);
            }
        """)
        button_layout.addWidget(self.load_config_btn)

        self.save_config_btn = QPushButton("💾 保存配置为...")
        self.save_config_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        button_layout.addWidget(self.save_config_btn)

        self.refresh_btn = QPushButton("🔄 刷新状态")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #4f46e5);
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #4338ca);
            }
        """)
        button_layout.addWidget(self.refresh_btn)

        layout.addLayout(button_layout, 4, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_status_group(self):
        """创建状态组"""
        group = QGroupBox("📊 仓库状态")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(8, 12, 8, 8)

        self.branch_label = self._create_status_label("🌿 分支", "--", "#10b981")
        self.uncommitted_label = self._create_status_label("📝 未提交", "--", "#f59e0b")
        self.unpushed_label = self._create_status_label("📤 未推送", "--", "#3b82f6")
        self.sync_label = self._create_status_label("🔗 状态", "--", "#8b5cf6")

        layout.addWidget(self.branch_label, 0, 0)
        layout.addWidget(self.uncommitted_label, 0, 1)
        layout.addWidget(self.unpushed_label, 0, 2)
        layout.addWidget(self.sync_label, 0, 3)

        group.setLayout(layout)
        return group

    def _create_status_label(self, title, value, color):
        """创建状态标签"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: #1f2937;
                border-left: 3px solid {color};
                border-radius: 5px;
                padding: 6px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))
        title_label.setStyleSheet("color: #9ca3af;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("value")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        widget.value_label = value_label
        return widget

    def _create_operations_group(self):
        """创建操作按钮组"""
        group = QGroupBox("🎯 智能操作")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 12, 8, 8)

        operations = [
            ("upload", "📤 智能上传", "自动检测并上传更改", "#10b981"),
            ("download", "📥 智能下载", "拉取远程最新更新", "#3b82f6"),
            ("sync", "🔄 智能同步", "双向同步本地与远程", "#8b5cf6"),
            ("overwrite", "⚡ 强制覆盖", "用本地强制覆盖远程", "#f59e0b"),
            ("delete", "🗑 清理远程", "删除远程所有文件", "#ef4444"),
            ("init", "🔧 初始化", "初始化Git仓库", "#06b6d4"),
        ]

        self.operation_buttons = {}
        for i, (op_name, text, tooltip, color) in enumerate(operations):
            btn = self._create_operation_button(text, tooltip, color)
            layout.addWidget(btn, i // 3, i % 3)
            self.operation_buttons[op_name] = btn

        group.setLayout(layout)
        return group

    def _create_operation_button(self, text, tooltip, color):
        """创建操作按钮"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {darken_color(color)});
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {darken_color(color)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {darken_color(color, 40)};
            }}
            QPushButton:disabled {{
                background: #4b5563;
                color: #9ca3af;
            }}
        """)
        return btn

    def _create_log_group(self):
        """创建日志组"""
        group = QGroupBox("📋 操作日志")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 12, 8, 8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(130)
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 2px solid #1e293b;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.log_text)

        self.clear_log_btn = QPushButton("🧹 清空日志")
        layout.addWidget(self.clear_log_btn)

        group.setLayout(layout)
        return group

    def get_config_data(self):
        """获取当前界面的配置数据"""
        return {
            'local_path': self.local_path_input.text(),
            'remote_url': self.remote_url_input.text(),
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

    def set_config_data(self, config):
        """将配置数据设置到界面上"""
        self.local_path_input.setText(config.get('local_path', ''))
        self.remote_url_input.setText(config.get('remote_url', ''))
        self.username_input.setText(config.get('username', ''))
        self.email_input.setText(config.get('email', ''))

    def log(self, message, msg_type="info"):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")

        colors = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }

        color = colors.get(msg_type, "#cbd5e1")

        html = f'<span style="color: #64748b;">[{timestamp}]</span> '
        html += f'<span style="color: {color}; font-weight: bold;">{message}</span>'

        self.log_text.append(html)

        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_status_display(self, branch, uncommitted, unpushed, sync_status):
        """更新状态显示"""
        self.branch_label.value_label.setText(branch)
        self.uncommitted_label.value_label.setText(uncommitted)
        self.unpushed_label.value_label.setText(unpushed)
        self.sync_label.value_label.setText(sync_status)

    def get_delete_confirmation(self):
        """获取删除操作的最终确认"""
        text, ok = QInputDialog.getText(
            self,
            "确认删除",
            "请输入 'DELETE' 确认删除:"
        )
        return ok and text == "DELETE"
