# app/ui/main_window.py
"""
UI展现层：主窗口 (GitHubManager)
负责组装UI视图、连接信号与槽，作为UI层的控制器。
"""
import os
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
    QFileDialog, QProgressBar, QInputDialog
)
from PyQt6.QtCore import QTimer

from app.config import settings
from app.core.git_worker import GitWorker
from app.services.config_service import ConfigService
from app.ui.views.title_view import TitleView
from app.ui.views.config_view import ConfigView
from app.ui.views.status_view import StatusView
from app.ui.views.operations_view import OperationsView
from app.ui.views.log_view import LogView

class MainWindow(QMainWindow):
    """
    GitHub仓库智能管理器 - 主窗口
    """
    def __init__(self):
        super().__init__()
        self.worker = None
        self.config = {}

        self._init_ui()
        self.load_config()
        self._connect_signals()

        QTimer.singleShot(500, self.auto_check_status)

    def _init_ui(self):
        """初始化并组装UI视图"""
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setGeometry(100, 100, settings.WINDOW_DEFAULT_WIDTH, settings.WINDOW_DEFAULT_HEIGHT)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- 左侧主控制区 ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 实例化所有视图
        self.title_view = TitleView()
        self.config_view = ConfigView()
        self.status_view = StatusView()
        self.operations_view = OperationsView()
        self.log_view = LogView()

        left_layout.addWidget(self.title_view)
        left_layout.addWidget(self.config_view)
        left_layout.addWidget(self.status_view)
        left_layout.addWidget(self.operations_view)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        # 样式可以后续移到 styling.py 中
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {settings.Colors.BORDER_FOCUS};
                border-radius: 8px; text-align: center; height: 30px;
                background-color: {settings.Colors.PROGRESS_BAR_BACKGROUND};
                color: white; font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {settings.Colors.BRAND_PRIMARY_START},
                    stop:1 {settings.Colors.BRAND_PRIMARY_END});
                border-radius: 6px;
            }}
        """)
        left_layout.addWidget(self.progress_bar)
        left_layout.addStretch()

        # 将左右两个区域添加到主布局
        left_container.setMinimumWidth(settings.WINDOW_MIN_WIDTH_LEFT_PANEL)
        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(self.log_view, 3)

        # 状态栏
        self.statusBar().showMessage(settings.STATUS_BAR_READY)
        self.statusBar().setStyleSheet(f"color: {settings.Colors.STATUS_BAR_TEXT}; font-weight: bold;")

    def _connect_signals(self):
        """连接所有UI组件的信号到主窗口的槽函数"""
        # 配置视图
        self.config_view.browse_btn.clicked.connect(self.browse_folder)
        self.config_view.save_btn.clicked.connect(self.save_config)
        self.config_view.refresh_btn.clicked.connect(self.auto_check_status)

        # 操作视图
        for op_id, button in self.operations_view.buttons.items():
            handler = getattr(self, f"handle_{op_id}", None)
            if handler:
                button.clicked.connect(handler)

        # 日志视图
        self.log_view.clear_btn.clicked.connect(self.log_view.log_text.clear)

    # --- 槽函数 (事件处理器) ---

    def load_config(self):
        """从服务加载配置并更新UI"""
        self.config = ConfigService.load_config()
        self.config_view.set_config_data(self.config)
        self.log("✓ 配置已从本地加载", "success")

    def save_config(self):
        """从UI获取数据并通过服务保存配置"""
        current_config = self.config_view.get_config_data()

        if not current_config['local_path']:
            QMessageBox.warning(self, settings.MSG_CONFIG_WARN_TITLE, settings.MSG_CONFIG_WARN_NO_LOCAL_PATH)
            return
        if not current_config['remote_url']:
            QMessageBox.warning(self, settings.MSG_CONFIG_WARN_TITLE, settings.MSG_CONFIG_WARN_NO_REMOTE_URL)
            return

        success, message = ConfigService.save_config(current_config)
        if success:
            self.config = current_config
            self.log(f"✓ {message}", "success")
            QMessageBox.information(self, "成功", message)
            self.auto_check_status()
        else:
            self.log(f"✗ {message}", "error")
            QMessageBox.critical(self, "错误", message)

    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择本地仓库路径",
            self.config.get('local_path') or str(settings.CONFIG_FILE_PATH.parent)
        )
        if folder:
            self.config_view.local_path_input.setText(folder)

    def auto_check_status(self):
        """自动检查仓库状态并更新UI"""
        local_path = self.config_view.local_path_input.text()
        if not local_path or not os.path.exists(local_path):
            self.status_view.update_status({
                "sync": settings.STATUS_STATE_UNCONFIGURED
            })
            return

        try:
            os.chdir(local_path)
            if not os.path.exists('.git'):
                self.status_view.update_status({
                    "sync": settings.STATUS_STATE_UNINITIALIZED
                })
                return

            branch = self._run_git_command("git branch --show-current") or "main"
            status = self._run_git_command("git status --porcelain")
            uncommitted = len(status.strip().split('\\n')) if status.strip() else 0

            try:
                unpushed = self._run_git_command("git rev-list @{u}..HEAD --count") or "0"
                sync_status = settings.STATUS_STATE_CONNECTED
            except subprocess.CalledProcessError:
                unpushed = "--"
                sync_status = settings.STATUS_STATE_LOCAL

            self.status_view.update_status({
                "branch": branch,
                "uncommitted": uncommitted,
                "unpushed": unpushed,
                "sync": sync_status
            })

        except Exception as e:
            self.log(f"⚠ 状态检查失败: {str(e)}", "warning")
            self.status_view.update_status({"sync": settings.STATUS_STATE_ERROR})

    def _run_git_command(self, command):
        """辅助函数，用于运行git命令并返回输出"""
        return subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8'
        ).stdout.strip()

    # --- GitWorker 控制 ---

    def execute_operation(self, operation, confirm_title=None, confirm_text=None):
        """执行Git操作的通用入口"""
        config_data = self.config_view.get_config_data()
        if not config_data['local_path']:
            QMessageBox.warning(self, settings.MSG_CONFIG_WARN_TITLE, settings.MSG_CONFIG_WARN_NO_LOCAL_PATH)
            return
        if not config_data['remote_url'] and operation != "status":
            QMessageBox.warning(self, settings.MSG_CONFIG_WARN_TITLE, settings.MSG_CONFIG_WARN_NO_REMOTE_URL)
            return

        if confirm_title and confirm_text:
            reply = QMessageBox.question(self, confirm_title, confirm_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._set_ui_enabled(False)
        self.worker = GitWorker(operation, config_data['local_path'], config_data['remote_url'], config_data)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def on_operation_finished(self, success, message):
        """操作完成的回调"""
        self._set_ui_enabled(True)
        self.log(message, "success" if success else "error")

        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)

        QTimer.singleShot(500, self.auto_check_status)

    def _set_ui_enabled(self, enabled):
        """启用或禁用UI控件"""
        self.config_view.setEnabled(enabled)
        self.operations_view.setEnabled(enabled)
        self.progress_bar.setVisible(not enabled)
        if not enabled:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
        self.statusBar().showMessage("正在执行..." if not enabled else settings.STATUS_BAR_READY)

    def log(self, message, msg_type="info"):
        """向日志视图添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = settings.LOG_COLORS.get(msg_type, settings.Colors.PRIMARY_TEXT)

        html = (f'<span style="color: {settings.Colors.LOG_TIMESTAMP_TEXT};">[{timestamp}]</span> '
                f'<span style="color: {color}; font-weight: bold;">{message}</span>')
        self.log_view.log_text.append(html)

        scrollbar = self.log_view.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # --- 具体操作的处理函数 ---

    def handle_upload(self):
        self.execute_operation("upload")

    def handle_download(self):
        self.execute_operation("download")

    def handle_sync(self):
        self.execute_operation("sync", settings.CONFIRM_SYNC_TITLE, settings.CONFIRM_SYNC_TEXT)

    def handle_overwrite(self):
        self.execute_operation("overwrite", settings.CONFIRM_OVERWRITE_TITLE, settings.CONFIRM_OVERWRITE_TEXT)

    def handle_delete(self):
        reply = QMessageBox.critical(self, settings.CONFIRM_DELETE_TITLE, settings.CONFIRM_DELETE_TEXT,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)

        if reply == QMessageBox.StandardButton.Ok:
            text, ok = QInputDialog.getText(self, settings.CONFIRM_DELETE_TITLE, settings.CONFIRM_DELETE_INPUT_PROMPT)
            if ok and text == settings.CONFIRM_DELETE_INPUT_KEYWORD:
                self.execute_operation("delete")

    def handle_init(self):
        self.execute_operation("init")
