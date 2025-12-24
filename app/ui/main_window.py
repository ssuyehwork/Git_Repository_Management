import sys
import os
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QMessageBox, QFileDialog, QProgressBar,
    QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from app.services.config_service import ConfigService
from app.core.git_worker import GitWorker

class MainWindow(QMainWindow):
    """主窗口 - 只负责UI的展示和用户交互"""

    def __init__(self):
        super().__init__()
        self.config_service = ConfigService()
        self.worker = None

        self.init_ui()
        self.load_profiles_to_ui()
        QTimer.singleShot(500, self.auto_check_status)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub 仓库智能管理器 v3.0 (模块化版)")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet(self._get_stylesheet())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # ... (此处省略了与之前版本几乎完全相同的UI创建代码)
        # 为了简洁，仅展示关键的、有变化的部分
        config_group = self._create_config_group()
        operations_group = self._create_operations_group()
        log_group = self._create_log_group()

        layout.addWidget(config_group)
        layout.addWidget(self._create_status_group())
        layout.addWidget(operations_group)
        layout.addWidget(log_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.statusBar().showMessage("就绪")

    def _create_config_group(self):
        """创建配置组 - UI和事件绑定"""
        group = QGroupBox("⚙ 仓库配置")
        layout = QGridLayout()

        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)

        self.local_path_input = QLineEdit()
        self.remote_url_input = QLineEdit()
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()

        browse_btn = QPushButton("📂 浏览")
        browse_btn.clicked.connect(self.browse_folder)

        new_btn = QPushButton("➕ 新建")
        new_btn.clicked.connect(self.create_new_profile)
        update_btn = QPushButton("💾 更新")
        update_btn.clicked.connect(self.update_current_profile)
        delete_btn = QPushButton("❌ 删除")
        delete_btn.clicked.connect(self.delete_current_profile)

        # ... (布局代码省略)
        layout.addWidget(QLabel("📂 配置方案:"), 0, 0)
        layout.addWidget(self.profile_combo, 0, 1, 1, 2)
        layout.addWidget(QLabel("📁 本地路径:"), 1, 0)
        layout.addWidget(self.local_path_input, 1, 1)
        layout.addWidget(browse_btn, 1, 2)
        # ... (其他输入框布局)
        button_layout = QHBoxLayout()
        button_layout.addWidget(new_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout, 5, 0, 1, 3)

        group.setLayout(layout)
        return group

    def _create_operations_group(self):
        """创建操作按钮组"""
        group = QGroupBox("🎯 智能操作")
        layout = QGridLayout()
        operations = [
            ("📤 智能上传", self.smart_upload),
            ("📥 智能下载", self.smart_download),
            # ... (其他操作)
        ]
        # ... (按钮创建循环)
        return group

    # ================================
    # UI -> Service/Core (逻辑调用)
    # ================================

    def load_profiles_to_ui(self):
        """从配置服务加载方案并更新UI"""
        profiles = self.config_service.get_all_profiles()
        last_profile_name = self.config_service.get_last_profile_name()

        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItems(profiles.keys())

        if last_profile_name:
            self.profile_combo.setCurrentText(last_profile_name)
            self.on_profile_changed(last_profile_name)

        self.profile_combo.blockSignals(False)

    def on_profile_changed(self, profile_name):
        """当用户切换配置方案时，更新输入框"""
        if profile_name:
            profile_data = self.config_service.get_profile(profile_name)
            self.local_path_input.setText(profile_data.get('local_path', ''))
            self.remote_url_input.setText(profile_data.get('remote_url', ''))
            self.username_input.setText(profile_data.get('username', ''))
            self.email_input.setText(profile_data.get('email', ''))
            self.auto_check_status()

    def create_new_profile(self):
        """处理'新建'按钮点击"""
        profile_name, ok = QInputDialog.getText(self, "新建配置方案", "请输入方案名称:")
        if ok and profile_name:
            try:
                current_data = self._get_data_from_inputs()
                self.config_service.save_profile(profile_name, current_data)
                self.load_profiles_to_ui() # 重新加载
                self.log(f"✓ 成功创建方案: {profile_name}", "success")
            except ValueError as e:
                QMessageBox.warning(self, "错误", str(e))

    def update_current_profile(self):
        """处理'更新'按钮点击"""
        current_profile = self.profile_combo.currentText()
        if not current_profile:
            QMessageBox.warning(self, "错误", "没有选中的方案可更新。")
            return
        try:
            current_data = self._get_data_from_inputs()
            self.config_service.save_profile(current_profile, current_data)
            self.log(f"✓ 成功更新方案: {current_profile}", "success")
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))

    def delete_current_profile(self):
        """处理'删除'按钮点击"""
        current_profile = self.profile_combo.currentText()
        try:
            if self.config_service.delete_profile(current_profile):
                self.load_profiles_to_ui()
                self.log(f"✓ 成功删除方案: {current_profile}", "success")
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))

    def execute_operation(self, operation):
        """通用Git操作执行器"""
        local_path = self.local_path_input.text()
        remote_url = self.remote_url_input.text()
        config = self._get_data_from_inputs()

        if not local_path or not remote_url:
            QMessageBox.warning(self, "警告", "请先配置并选择一个有效的方案！")
            return

        self.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.worker = GitWorker(operation, local_path, remote_url, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    # --- 具体操作的简单调用 ---
    def smart_upload(self): self.execute_operation("upload")
    def smart_download(self): self.execute_operation("download")
    def smart_sync(self): self.execute_operation("sync")
    # ... 其他按钮也类似

    def auto_check_status(self):
        """
        直接、快速地检查本地Git状态。
        这部分逻辑很简单，直接调用git命令比启动一个完整线程更高效。
        """
        local_path = self.local_path_input.text()
        if not local_path or not os.path.exists(os.path.join(local_path, '.git')):
            # 更新UI显示为'未初始化'
            return

        try:
            os.chdir(local_path)
            branch = subprocess.check_output("git branch --show-current").strip().decode()
            # ... 其他状态检查命令
            # 更新UI状态标签
        except Exception:
            # 更新UI显示为'检查失败'
            pass

    # ================================
    # 辅助方法
    # ================================
    def _get_data_from_inputs(self):
        """从UI输入框收集数据"""
        return {
            'local_path': self.local_path_input.text(),
            'remote_url': self.remote_url_input.text(),
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

    def on_progress(self, message, msg_type):
        self.log(message, msg_type)

    def on_operation_finished(self, success, message):
        self.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log(message, "success" if success else "error")
        self.auto_check_status()

    def log(self, message, msg_type="info"):
        """添加日志条目到UI"""
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

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择本地仓库路径")
        if folder:
            self.local_path_input.setText(folder)

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

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        widget.value_label = value_label
        return widget

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

        clear_btn = QPushButton("🧹 清空日志")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(clear_btn)

        group.setLayout(layout)
        return group

    def _get_stylesheet(self):
        """获取全局样式表"""
        return """
            QMainWindow {
                background-color: #0f172a;
            }
            QGroupBox {
                color: #f1f5f9;
                border: 2px solid #334155;
                border-radius: 10px;
                margin-top: 8px;
                padding-top: 18px;
                background-color: #1e293b;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px;
                background-color: #1e293b;
            }
            QLabel {
                color: #cbd5e1;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #334155;
                color: #f1f5f9;
                border: 2px solid #475569;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                selection-background-color: #6366f1;
            }
            QLineEdit:focus {
                border: 2px solid #6366f1;
                background-color: #3f4d63;
            }
            QLineEdit::placeholder {
                color: #64748b;
            }
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
            QStatusBar {
                background-color: #1e293b;
                color: #cbd5e1;
            }
        """

    def _darken_color(self, hex_color, amount=20):
        """使颜色变暗"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        color.setHsl(h, s, max(0, l - amount), a)
        return color.name()
