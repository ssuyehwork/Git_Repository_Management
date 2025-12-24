import os
import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QMessageBox, QFileDialog, QProgressBar,
    QInputDialog, QSplashScreen
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from app.core.git_worker import GitWorker
from app.core.config_manager import ConfigManager
from app.utils.dependency_manager import DependencyManager
from .styles import get_stylesheet, darken_color # 从同级目录的styles模块导入
from datetime import datetime

# ================================
# 主窗口类
# ================================
class GitHubManager(QMainWindow):
    """GitHub仓库智能管理器 - 主窗口"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.worker = None

        # 检查Git
        if not DependencyManager.check_git():
            QMessageBox.critical(
                None,
                "Git未安装",
                "未检测到Git!\n\n请先安装Git:\nhttps://git-scm.com/downloads"
            )
            sys.exit(1)

        self.init_ui()
        self.load_config_to_ui()
        QTimer.singleShot(500, self.auto_check_status)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub 仓库智能管理器 v2.0 Professional")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet(get_stylesheet()) # 应用全局样式

        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题区域
        title_widget = self._create_title_widget()
        layout.addWidget(title_widget)

        # 配置区域
        config_group = self._create_config_group()
        layout.addWidget(config_group)

        # 仓库状态区域
        self.status_group = self._create_status_group()
        layout.addWidget(self.status_group)

        # 操作按钮区域
        operations_group = self._create_operations_group()
        layout.addWidget(operations_group)

        # 日志区域
        log_group = self._create_log_group()
        layout.addWidget(log_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        # 样式已通过全局QSS设置
        layout.addWidget(self.progress_bar)

        # 状态栏
        self.statusBar().showMessage("就绪")
        # 样式已通过全局QSS设置

    def _create_title_widget(self):
        """创建标题区域"""
        widget = QWidget()
        # 样式已通过全局QSS设置

        layout = QHBoxLayout(widget)

        title = QLabel("🚀 GitHub 仓库智能管理器")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(title)

        layout.addStretch()

        version = QLabel("v2.0 Professional")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        layout.addWidget(version)

        return widget

    def _create_config_group(self):
        """创建配置组"""
        group = QGroupBox("⚙ 仓库配置")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 10, 8, 8)

        # 本地路径
        layout.addWidget(QLabel("📁 本地路径:"), 0, 0)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("例如: G:\\PYthon\\GitHub 仓库管理")
        layout.addWidget(self.local_path_input, 0, 1)

        browse_btn = QPushButton("📂 浏览")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(browse_btn, 0, 2)

        # 远程URL
        layout.addWidget(QLabel("🌐 远程仓库:"), 1, 0)
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText("https://github.com/username/repo.git")
        layout.addWidget(self.remote_url_input, 1, 1, 1, 2)

        # Git用户名
        layout.addWidget(QLabel("👤 用户名:"), 2, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Git用户名 (可选)")
        layout.addWidget(self.username_input, 2, 1, 1, 2)

        # Git邮箱
        layout.addWidget(QLabel("📧 邮箱:"), 3, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Git邮箱 (可选)")
        layout.addWidget(self.email_input, 3, 1, 1, 2)

        # 按钮行
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 保存配置")
        save_btn.setObjectName("saveButton") # 设置对象名以应用特定样式
        save_btn.clicked.connect(self.save_config_from_ui)
        button_layout.addWidget(save_btn)

        refresh_btn = QPushButton("🔄 刷新状态")
        refresh_btn.setObjectName("refreshButton") # 设置对象名
        refresh_btn.clicked.connect(self.auto_check_status)
        button_layout.addWidget(refresh_btn)

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

        # 创建状态标签
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
        widget.setObjectName("statusLabelWidget")
        widget.setStyleSheet(f"border-left: 3px solid {color};")

        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; background: transparent;")
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
            ("📤 智能上传", "自动检测并上传更改", "#10b981", self.smart_upload),
            ("📥 智能下载", "拉取远程最新更新", "#3b82f6", self.smart_download),
            ("🔄 智能同步", "双向同步本地与远程", "#8b5cf6", self.smart_sync),
            ("⚡ 强制覆盖", "用本地强制覆盖远程", "#f59e0b", self.smart_overwrite),
            ("🗑 清理远程", "删除远程所有文件", "#ef4444", self.smart_delete),
            ("🔧 初始化", "初始化Git仓库", "#06b6d4", self.init_repo),
        ]

        for i, (text, tooltip, color, func) in enumerate(operations):
            btn = self._create_operation_button(text, tooltip, color, func)
            layout.addWidget(btn, i // 3, i % 3)

        group.setLayout(layout)
        return group

    def _create_operation_button(self, text, tooltip, color, callback):
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
            }}
            QPushButton:pressed {{
                background: {darken_color(color, 40)};
            }}
            QPushButton:disabled {{
                background: #4b5563;
                color: #9ca3af;
            }}
        """)
        btn.clicked.connect(callback)
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

        layout.addWidget(self.log_text)

        clear_btn = QPushButton("🧹 清空日志")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(clear_btn)

        group.setLayout(layout)
        return group

    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择本地仓库路径",
            self.local_path_input.text() or str(Path.home())
        )
        if folder:
            self.local_path_input.setText(folder)

    def load_config_to_ui(self):
        """加载配置并更新UI"""
        config = self.config_manager.load_config()
        self.local_path_input.setText(config.get('local_path', ''))
        self.remote_url_input.setText(config.get('remote_url', ''))
        self.username_input.setText(config.get('username', ''))
        self.email_input.setText(config.get('email', ''))
        self.log("✓ 配置已加载", "success")

    def save_config_from_ui(self):
        """从UI获取数据并保存配置"""
        config = {
            'local_path': self.local_path_input.text(),
            'remote_url': self.remote_url_input.text(),
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

        if not config['local_path']:
            QMessageBox.warning(self, "警告", "请填写本地路径!")
            return

        if not config['remote_url']:
            QMessageBox.warning(self, "警告", "请填写远程仓库URL!")
            return

        success, message = self.config_manager.save_config(config)

        if success:
            self.log(message, "success")
            QMessageBox.information(self, "成功", message)
            self.auto_check_status()
        else:
            self.log(message, "error")
            QMessageBox.critical(self, "错误", message)

    def log(self, message, msg_type="info"):
        """添加日志"""
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
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def auto_check_status(self):
        """自动检查仓库状态"""
        local_path = self.local_path_input.text()
        if not local_path or not os.path.exists(local_path):
            self.update_status_display("--", "--", "--", "未配置")
            return

        try:
            os.chdir(local_path)

            if not os.path.exists('.git'):
                self.update_status_display("--", "--", "--", "未初始化")
                return

            branch = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True, encoding='utf-8').stdout.strip() or "main"
            status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0

            try:
                unpushed_result = subprocess.run("git rev-list @{u}..HEAD --count", shell=True, capture_output=True, text=True, check=True)
                unpushed = unpushed_result.stdout.strip()
                sync_status = "✓ 已连接"
            except subprocess.CalledProcessError:
                unpushed = "N/A" # 可能是新仓库，还没有上游分支
                sync_status = "本地仓库"

            self.update_status_display(branch, str(uncommitted), unpushed, sync_status)

        except Exception as e:
            self.log(f"⚠ 状态检查失败: {str(e)}", "warning")
            self.update_status_display("--", "--", "--", "检查失败")

    def update_status_display(self, branch, uncommitted, unpushed, sync_status):
        """更新状态显示"""
        self.branch_label.value_label.setText(branch)
        self.uncommitted_label.value_label.setText(uncommitted)
        self.unpushed_label.value_label.setText(unpushed)
        self.sync_label.value_label.setText(sync_status)

    def execute_operation(self, operation, confirm_msg=None):
        """执行Git操作"""
        local_path = self.local_path_input.text()
        remote_url = self.remote_url_input.text()

        if not local_path:
            QMessageBox.warning(self, "警告", "请先配置本地路径!")
            return

        if not remote_url and operation != "status":
            QMessageBox.warning(self, "警告", "请先配置远程仓库!")
            return

        if confirm_msg:
            reply = QMessageBox.question(self, "确认操作", confirm_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.set_ui_enabled(False)
        self.statusBar().showMessage(f"正在执行: {operation}")

        config = {
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

        self.worker = GitWorker(operation, local_path, remote_url, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.execute_script.connect(self.execute_downloaded_script)
        self.worker.start()

    def set_ui_enabled(self, enabled):
        """启用或禁用UI"""
        self.setEnabled(enabled)
        self.progress_bar.setVisible(not enabled)
        if not enabled:
            self.progress_bar.setRange(0, 0) # 不确定模式
        else:
            self.progress_bar.setRange(0, 100) # 重置

    def on_progress(self, message, msg_type):
        """进度回调"""
        self.log(message, msg_type)

    def on_operation_finished(self, success, message):
        """操作完成回调"""
        self.set_ui_enabled(True)
        self.statusBar().showMessage("就绪")

        self.log(message, "success" if success else "error")

        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)

        QTimer.singleShot(500, self.auto_check_status)

    def execute_downloaded_script(self, script_path):
        """执行下载后的脚本"""
        try:
            self.log(f"🚀 正在启动: {Path(script_path).name}", "info")

            if sys.platform == "win32":
                subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=str(Path(script_path).parent))
            else:
                subprocess.Popen([sys.executable, script_path], cwd=str(Path(script_path).parent))

            self.log(f"✓ 程序已在新窗口启动", "success")

        except Exception as e:
            self.log(f"✗ 启动程序失败: {str(e)}", "error")
            QMessageBox.warning(self, "启动失败", f"自动启动程序失败:\n{str(e)}\n\n请手动运行: {script_path}")

    def smart_upload(self): self.execute_operation("upload")
    def smart_download(self): self.execute_operation("download")
    def init_repo(self): self.execute_operation("init")

    def smart_sync(self):
        self.execute_operation("sync", "将执行双向同步操作:\n\n1. 保存本地更改\n2. 拉取远程更新\n3. 推送到远程\n\n确定继续吗?")

    def smart_overwrite(self):
        self.execute_operation("overwrite", "⚠ 警告: 强制覆盖操作\n\n这将用本地版本强制覆盖远程仓库!\n远程的更改将永久丢失!\n\n确定要继续吗?")

    def smart_delete(self):
        reply = QMessageBox.critical(self, "⚠ 危险操作", "这将删除远程仓库的所有文件!\n此操作不可恢复!", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Ok:
            text, ok = QInputDialog.getText(self, "确认删除", "请输入 'DELETE' 确认删除:")
            if ok and text == "DELETE":
                self.execute_operation("delete")
