"""
应用程序逻辑控制器
"""
import os
import subprocess
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QTimer

from app.logic.git_worker import GitWorker
from app.config.config_manager import ConfigManager

class AppLogic:
    """负责连接UI和后台业务逻辑"""

    def __init__(self, ui):
        self.ui = ui
        self.config_manager = ConfigManager(self.ui)
        self.worker = None

        self._connect_signals()

        # 启动时自动检查状态
        QTimer.singleShot(500, self.auto_check_status)

    def _connect_signals(self):
        """连接所有UI信号到逻辑处理函数"""
        # 配置按钮
        self.ui.load_config_btn.clicked.connect(self.load_config)
        self.ui.save_config_btn.clicked.connect(self.save_config)
        self.ui.browse_btn.clicked.connect(self.browse_folder)
        self.ui.refresh_btn.clicked.connect(self.auto_check_status)

        # 操作按钮
        self.ui.operation_buttons["upload"].clicked.connect(self.smart_upload)
        self.ui.operation_buttons["download"].clicked.connect(self.smart_download)
        self.ui.operation_buttons["sync"].clicked.connect(self.smart_sync)
        self.ui.operation_buttons["overwrite"].clicked.connect(self.smart_overwrite)
        self.ui.operation_buttons["delete"].clicked.connect(self.smart_delete)
        self.ui.operation_buttons["init"].clicked.connect(self.init_repo)

        # 日志按钮
        self.ui.clear_log_btn.clicked.connect(self.ui.log_text.clear)

    def load_config(self):
        """处理加载配置逻辑"""
        config, filename = self.config_manager.load_config()
        if config:
            self.ui.set_config_data(config)
            self.ui.log(f"✓ 配置已从 {filename} 加载", "success")
            self.auto_check_status()

    def save_config(self):
        """处理保存配置逻辑"""
        config_data = self.ui.get_config_data()
        success, filename = self.config_manager.save_config(config_data)
        if success:
            self.ui.log(f"✓ 配置已保存到 {filename}", "success")

    def browse_folder(self):
        """处理浏览文件夹逻辑"""
        folder = QFileDialog.getExistingDirectory(
            self.ui,
            "选择本地仓库路径",
            self.ui.local_path_input.text()
        )
        if folder:
            self.ui.local_path_input.setText(folder)

    def auto_check_status(self):
        """自动检查仓库状态"""
        local_path = self.ui.local_path_input.text()
        if not local_path or not os.path.exists(local_path):
            self.ui.update_status_display("--", "--", "--", "未配置")
            return

        try:
            os.chdir(local_path)

            if not os.path.exists('.git'):
                self.ui.update_status_display("--", "--", "--", "未初始化")
                return

            branch = self._run_git_command("git branch --show-current") or "main"
            status = self._run_git_command("git status --porcelain")
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0

            try:
                unpushed = self._run_git_command("git rev-list @{u}..HEAD --count")
            except Exception:
                unpushed = "--"

            self.ui.update_status_display(
                branch,
                str(uncommitted),
                str(unpushed),
                "✓ 已连接" if unpushed != "--" else "本地仓库"
            )

        except Exception as e:
            self.ui.log(f"⚠ 状态检查失败: {str(e)}", "warning")
            self.ui.update_status_display("--", "--", "--", "检查失败")

    def _run_git_command(self, command):
        """执行一个Git命令并返回结果"""
        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        ).stdout.strip()

    def execute_operation(self, operation, confirm_msg=None):
        """执行Git操作"""
        config_data = self.ui.get_config_data()
        local_path = config_data.get('local_path')
        remote_url = config_data.get('remote_url')

        if not local_path:
            QMessageBox.warning(self.ui, "警告", "请先配置本地路径!")
            return

        if not remote_url and operation != "status":
            QMessageBox.warning(self.ui, "警告", "请先配置远程仓库!")
            return

        if confirm_msg:
            reply = QMessageBox.question(
                self.ui, "确认操作", confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._start_worker(operation, local_path, remote_url, config_data)

    def _start_worker(self, operation, local_path, remote_url, config):
        """启动工作线程"""
        self.ui.setEnabled(False)
        self.ui.progress_bar.setVisible(True)
        self.ui.progress_bar.setRange(0, 0)
        self.ui.statusBar().showMessage(f"正在执行: {operation}")

        self.worker = GitWorker(operation, local_path, remote_url, config)
        self.worker.progress.connect(self.ui.log)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def on_operation_finished(self, success, message):
        """操作完成回调"""
        self.ui.setEnabled(True)
        self.ui.progress_bar.setVisible(False)
        self.ui.statusBar().showMessage("就绪")

        self.ui.log(message, "success" if success else "error")

        if success:
            QMessageBox.information(self.ui, "成功", message)
        else:
            QMessageBox.critical(self.ui, "错误", message)

        QTimer.singleShot(500, self.auto_check_status)

    # --- 操作函数的具体实现 ---
    def smart_upload(self):
        self.execute_operation("upload")

    def smart_download(self):
        self.execute_operation("download")

    def smart_sync(self):
        self.execute_operation(
            "sync",
            "将执行双向同步操作:\n\n"
            "1. 保存本地更改\n"
            "2. 拉取远程更新\n"
            "3. 推送到远程\n\n"
            "确定继续吗?"
        )

    def smart_overwrite(self):
        self.execute_operation(
            "overwrite",
            "⚠ 警告: 强制覆盖操作\n\n"
            "这将用本地版本强制覆盖远程仓库!\n"
            "远程的更改将永久丢失!\n\n"
            "确定要继续吗?"
        )

    def smart_delete(self):
        reply = QMessageBox.critical(
            self.ui,
            "⚠ 危险操作",
            "这将删除远程仓库的所有文件!\n"
            "此操作不可恢复!",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Ok:
            if self.ui.get_delete_confirmation():
                self.execute_operation("delete")

    def init_repo(self):
        self.execute_operation("init")
