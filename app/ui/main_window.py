import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

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
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title_widget = self._create_title_widget()
        config_group = self._create_config_group()
        status_group = self._create_status_group()
        operations_group = self._create_operations_group()
        log_group = self._create_log_group()

        layout.addWidget(title_widget)
        layout.addWidget(config_group)
        layout.addWidget(status_group)
        layout.addWidget(operations_group)
        layout.addWidget(log_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #6366f1; border-radius: 8px; text-align: center;
                height: 30px; background-color: #1f2937; color: white; font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 10px; padding: 12px;
            }
        """)
        layout = QHBoxLayout(widget)
        title = QLabel("🚀 GitHub 仓库智能管理器")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        layout.addStretch()
        version = QLabel("v3.0 Modular")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: rgba(255,255,255,0.8);")
        layout.addWidget(version)
        return widget

    def _create_config_group(self):
        """创建配置组 - UI和事件绑定"""
        group = QGroupBox("⚙ 仓库配置")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 10, 8, 8)

        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)

        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("例如: G:\\PYthon\\GitHub 仓库管理")
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText("https://github.com/username/repo.git")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Git用户名 (可选)")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Git邮箱 (可选)")

        browse_btn = QPushButton("📂 浏览")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_folder)

        # 创建按钮
        new_btn = QPushButton("➕ 新建方案")
        update_btn = QPushButton("💾 更新方案")
        delete_btn = QPushButton("❌ 删除方案")
        refresh_btn = QPushButton("🔄 刷新状态")

        # 定义通用样式模板
        btn_style_template = """
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2});
                color: white; font-weight: bold; padding: 8px 15px;
                border-radius: 6px; font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color2}, stop:1 {color3});
            }}
        """

        # 应用不同颜色
        new_btn.setStyleSheet(btn_style_template.format(color1="#10b981", color2="#059669", color3="#047857"))
        update_btn.setStyleSheet(btn_style_template.format(color1="#3b82f6", color2="#2563eb", color3="#1d4ed8"))
        delete_btn.setStyleSheet(btn_style_template.format(color1="#ef4444", color2="#dc2626", color3="#b91c1c"))
        refresh_btn.setStyleSheet(btn_style_template.format(color1="#8b5cf6", color2="#7c3aed", color3="#6d28d9"))

        # 连接信号
        new_btn.clicked.connect(self.create_new_profile)
        update_btn.clicked.connect(self.update_current_profile)
        delete_btn.clicked.connect(self.delete_current_profile)
        refresh_btn.clicked.connect(self.auto_check_status)

        # 布局UI
        layout.addWidget(QLabel("📂 配置方案:"), 0, 0)
        layout.addWidget(self.profile_combo, 0, 1, 1, 2)
        layout.addWidget(QLabel("📁 本地路径:"), 1, 0)
        layout.addWidget(self.local_path_input, 1, 1)
        layout.addWidget(browse_btn, 1, 2)
        layout.addWidget(QLabel("🌐 远程仓库:"), 2, 0)
        layout.addWidget(self.remote_url_input, 2, 1, 1, 2)
        layout.addWidget(QLabel("👤 用户名:"), 3, 0)
        layout.addWidget(self.username_input, 3, 1, 1, 2)
        layout.addWidget(QLabel("📧 邮箱:"), 4, 0)
        layout.addWidget(self.email_input, 4, 1, 1, 2)

        button_layout = QHBoxLayout()
        crud_widget = QWidget()
        crud_layout = QHBoxLayout(crud_widget)
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(8)
        crud_layout.addWidget(new_btn)
        crud_layout.addWidget(update_btn)
        crud_layout.addWidget(delete_btn)

        button_layout.addWidget(crud_widget, 1)
        button_layout.addWidget(refresh_btn, 1)

        layout.addLayout(button_layout, 5, 0, 1, 3)
        group.setLayout(layout)
        return group

    def _create_operations_group(self):
        """创建操作按钮组"""
        group = QGroupBox("🎯 智能操作")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()
        layout.setSpacing(8)

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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {self._darken_color(color)});
                color: white; border: none; border-radius: 7px; padding: 10px;
            }}
            QPushButton:hover {{ background: {self._darken_color(color)}; }}
            QPushButton:pressed {{ background: {self._darken_color(color, 40)}; }}
        """)
        btn.clicked.connect(callback)
        return btn

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
        elif profiles:
            first_profile = list(profiles.keys())[0]
            self.profile_combo.setCurrentText(first_profile)
            self.on_profile_changed(first_profile)

        self.profile_combo.blockSignals(False)

    def on_profile_changed(self, profile_name):
        """当用户切换配置方案时，更新输入框"""
        if profile_name:
            profile_data = self.config_service.get_profile(profile_name)
            if profile_data:
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
                self.load_profiles_to_ui()
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
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除配置方案 '{current_profile}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.config_service.delete_profile(current_profile):
                    self.load_profiles_to_ui()
                    self.log(f"✓ 成功删除方案: {current_profile}", "success")
            except ValueError as e:
                QMessageBox.warning(self, "错误", str(e))

    def execute_operation(self, operation, confirm_msg=None):
        """通用Git操作执行器"""
        local_path = self.local_path_input.text()
        remote_url = self.remote_url_input.text()

        if not local_path or not remote_url and operation != 'init':
            QMessageBox.warning(self, "警告", "请先配置并选择一个有效的方案！")
            return

        if confirm_msg:
            reply = QMessageBox.question(self, "确认操作", confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes: return

        self.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        config = self._get_data_from_inputs()
        self.worker = GitWorker(operation, local_path, remote_url, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def smart_upload(self): self.execute_operation("upload")
    def smart_download(self): self.execute_operation("download")
    def init_repo(self): self.execute_operation("init")

    def smart_sync(self):
        self.execute_operation("sync", "将执行双向同步操作:\n\n1. 保存本地更改\n2. 拉取远程更新\n3. 推送到远程\n\n确定继续吗?")

    def smart_overwrite(self):
        self.execute_operation("overwrite", "⚠ 警告: 这将用本地版本强制覆盖远程仓库！\n远程的更改将永久丢失！确定继续吗？")

    def smart_delete(self):
        text, ok = QInputDialog.getText(self, "⚠ 危险操作确认", "此操作不可恢复！\n请输入 'DELETE' 确认删除远程仓库所有文件:")
        if ok and text == "DELETE":
            self.execute_operation("delete")

    def auto_check_status(self):
        local_path = self.local_path_input.text()
        if not local_path or not os.path.isdir(local_path):
            self.update_status_display("--", "--", "--", "路径无效")
            return

        # 保存当前目录
        original_dir = os.getcwd()
        try:
            os.chdir(local_path)
            if not os.path.exists(".git"):
                self.update_status_display("--", "--", "--", "未初始化")
                return

            branch = subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.STDOUT).strip().decode() or "main"
            status = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.STDOUT).decode()
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0

            try:
                # 检查是否存在远程跟踪分支
                subprocess.check_output(["git", "rev-parse", "@{u}"], stderr=subprocess.STDOUT).strip().decode()
                unpushed_cmd = ["git", "rev-list", "@{u}..HEAD", "--count"]
                unpushed = subprocess.check_output(unpushed_cmd, stderr=subprocess.STDOUT).strip().decode()
                status_text = "✓ 已连接"
            except subprocess.CalledProcessError:
                unpushed = "--"
                status_text = "仅本地"

            self.update_status_display(branch, str(uncommitted), str(unpushed), status_text)
        except Exception as e:
            self.update_status_display("错误", "错误", "错误", "检查失败")
            self.log(f"状态检查失败: {e}", "error")
        finally:
            # 恢复原始目录
            os.chdir(original_dir)

    def update_status_display(self, branch, uncommitted, unpushed, sync_status):
        self.branch_label.value_label.setText(branch)
        self.uncommitted_label.value_label.setText(uncommitted)
        self.unpushed_label.value_label.setText(unpushed)
        self.sync_label.value_label.setText(sync_status)

    # ================================
    # 辅助方法
    # ================================
    def _get_data_from_inputs(self):
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
        self.progress_bar.setRange(0, 100)
        self.log(message, "success" if success else "error")
        QMessageBox.information(self, "操作完成", message)
        self.auto_check_status()

    def log(self, message, msg_type="info"):
        """添加日志条目到UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"info": "#3b82f6", "success": "#10b981", "warning": "#f59e0b", "error": "#ef4444"}
        color = colors.get(msg_type, "#cbd5e1")
        html = f'<span style="color: #64748b;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">{message}</span>'
        self.log_text.append(html)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择本地仓库路径")
        if folder:
            self.local_path_input.setText(folder)

    def _create_status_group(self):
        """创建状态组"""
        group = QGroupBox("📊 仓库状态")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QGridLayout()

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
        widget.setObjectName("status_widget")
        widget.setStyleSheet(f"""
            QWidget {{ background-color: #1f2937; border-left: 3px solid {color}; border-radius: 5px; padding: 6px; }}
        """)
        layout = QVBoxLayout(widget)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        widget.value_label = value_label
        return widget

    def _create_log_group(self):
        """创建日志组"""
        group = QGroupBox("📋 操作日志")
        layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a; color: #e2e8f0; border: 2px solid #1e293b;
                border-radius: 8px; padding: 10px; font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        clear_btn = QPushButton("🧹 清空日志")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(self.log_text)
        layout.addWidget(clear_btn)
        group.setLayout(layout)
        return group

    def _get_stylesheet(self):
        """获取全局样式表"""
        return """
            QMainWindow { background-color: #0f172a; }
            QGroupBox {
                color: #f1f5f9; border: 2px solid #334155; border-radius: 10px;
                margin-top: 8px; padding-top: 18px; background-color: #1e293b;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 20px; padding: 0 8px;
            }
            QLabel { color: #cbd5e1; font-size: 13px; }
            QLineEdit {
                background-color: #334155; color: #f1f5f9; border: 2px solid #475569;
                border-radius: 6px; padding: 8px;
            }
            QLineEdit:focus { border: 2px solid #6366f1; }
            QPushButton {
                background-color: #475569; color: white; border: none;
                border-radius: 6px; padding: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #64748b; }
        """

    def _darken_color(self, hex_color, amount=20):
        """使颜色变暗"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        color.setHsl(h, s, max(0, l - amount), a)
        return color.name()
