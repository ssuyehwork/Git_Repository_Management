"""
应用程序逻辑控制器
"""
import os
import subprocess
import time
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QTimer

from app.logic.git_worker import GitWorker
from app.config.config_manager import ConfigManager
from app.config.storage import JsonStorage
from app.utils.file_manager import FileManager
from app.logic.workers.monitor_worker import MonitorThread
from app.logic.workers.extract_worker import ExtractThread
from app.logic.workers.launcher_worker import LauncherThread


class AppLogic:
    """负责连接UI和后台业务逻辑"""

    def __init__(self, ui):
        self.ui = ui
        self.git_config_manager = ConfigManager(self.ui)

        # Git worker
        self.git_worker = None

        # Sync workers
        self.monitor_thread = None
        self.extract_thread = None
        self.launcher_thread = None

        # Sync state
        self.sync_groups = {}

        self._connect_signals()
        self._init_sync_tab()

        # 启动时自动检查Git状态
        QTimer.singleShot(500, self.auto_check_git_status)

    def _connect_signals(self):
        """连接所有UI信号到逻辑处理函数"""
        # --- Git Tab ---
        self.ui.git_load_config_btn.clicked.connect(self.load_git_config)
        self.ui.git_save_config_btn.clicked.connect(self.save_git_config)
        self.ui.git_browse_btn.clicked.connect(self.browse_git_local_path)
        self.ui.git_refresh_btn.clicked.connect(self.auto_check_git_status)

        self.ui.operation_buttons["upload"].clicked.connect(self.smart_upload)
        self.ui.operation_buttons["download"].clicked.connect(self.smart_download)
        self.ui.operation_buttons["sync"].clicked.connect(self.smart_sync)
        self.ui.operation_buttons["overwrite"].clicked.connect(self.smart_overwrite)
        self.ui.operation_buttons["delete"].clicked.connect(self.smart_delete)
        self.ui.operation_buttons["init"].clicked.connect(self.init_repo)

        # --- Sync Tab ---
        self.ui.path_buttons['browse_extract'].clicked.connect(self.select_extract_path)
        self.ui.path_buttons['browse_source'].clicked.connect(self.select_source_path)
        self.ui.path_buttons['browse_target'].clicked.connect(self.select_target_path)
        self.ui.path_buttons['browse_main'].clicked.connect(self.select_main_program_path)
        self.ui.path_buttons['prev_version'].clicked.connect(lambda: self.switch_source_version('prev'))
        self.ui.path_buttons['next_version'].clicked.connect(lambda: self.switch_source_version('next'))

        self.ui.sync_save_group_btn.clicked.connect(self.save_sync_group)
        self.ui.sync_load_group_btn.clicked.connect(self.load_sync_group)
        self.ui.sync_del_group_btn.clicked.connect(self.delete_sync_group)

        self.ui.sync_start_btn.clicked.connect(self.start_copy)

        # --- Common ---
        self.ui.clear_log_btn.clicked.connect(self.ui.log_text.clear)

    # ========================================
    #         Git Tab Logic
    # ========================================
    def load_git_config(self):
        config, filename = self.git_config_manager.load_config()
        if config:
            self.ui.set_git_config_data(config)
            self.ui.log(f"✓ Git配置已从 {filename} 加载")
            self.auto_check_git_status()

    def save_git_config(self):
        config_data = self.ui.get_git_config_data()
        success, filename = self.git_config_manager.save_config(config_data)
        if success:
            self.ui.log(f"✓ Git配置已保存到 {filename}")

    def browse_git_local_path(self):
        folder = QFileDialog.getExistingDirectory(self.ui, "选择本地仓库路径")
        if folder:
            self.ui.git_local_path_input.setText(folder)

    def auto_check_git_status(self):
        local_path = self.ui.git_local_path_input.text()
        if not local_path or not os.path.exists(local_path):
            self.ui.update_status_display("--", "--", "--", "未配置")
            return

        try:
            os.chdir(local_path)
            if not os.path.exists('.git'):
                self.ui.update_status_display("--", "--", "--", "未初始化")
                return

            branch = self._run_shell_command("git branch --show-current") or "main"
            status = self._run_shell_command("git status --porcelain")
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0

            try:
                unpushed = self._run_shell_command("git rev-list @{u}..HEAD --count")
            except Exception:
                unpushed = "--"

            self.ui.update_status_display(branch, str(uncommitted), str(unpushed), "✓ 已连接" if unpushed != "--" else "本地仓库")

        except Exception as e:
            self.ui.log(f"⚠ Git状态检查失败: {str(e)}", True)
            self.ui.update_status_display("--", "--", "--", "检查失败")

    def execute_git_operation(self, operation, confirm_msg=None):
        config_data = self.ui.get_git_config_data()
        local_path = config_data.get('local_path')
        remote_url = config_data.get('remote_url')

        if not local_path or not remote_url:
            QMessageBox.warning(self.ui, "警告", "请先配置本地和远程路径!")
            return

        if confirm_msg and QMessageBox.question(self.ui, "确认操作", confirm_msg) != QMessageBox.StandardButton.Yes:
            return

        self._start_git_worker(operation, local_path, remote_url, config_data)

    def _start_git_worker(self, operation, local_path, remote_url, config):
        self.ui.setEnabled(False)
        self.ui.progress_bar.setVisible(True)
        self.ui.progress_bar.setRange(0, 0)
        self.ui.statusBar().showMessage(f"Git操作: {operation}")

        self.git_worker = GitWorker(operation, local_path, remote_url, config)
        self.git_worker.progress.connect(lambda msg, type: self.ui.log(msg, type=="error"))
        self.git_worker.finished.connect(self.on_git_operation_finished)
        self.git_worker.start()

    def on_git_operation_finished(self, success, message):
        self.ui.setEnabled(True)
        self.ui.progress_bar.setVisible(False)
        self.ui.statusBar().showMessage("就绪")

        self.ui.log(message, not success)

        if success:
            QMessageBox.information(self.ui, "成功", message)
        else:
            QMessageBox.critical(self.ui, "错误", message)

        QTimer.singleShot(500, self.auto_check_git_status)

    def smart_upload(self): self.execute_git_operation("upload")
    def smart_download(self): self.execute_git_operation("download")
    def init_repo(self): self.execute_git_operation("init")
    def smart_sync(self): self.execute_git_operation("sync", "确认双向同步吗?")
    def smart_overwrite(self): self.execute_git_operation("overwrite", "警告: 这将强制覆盖远程! 确定吗?")
    def smart_delete(self):
        if self.ui.get_delete_confirmation():
            self.execute_git_operation("delete")

    # ========================================
    #         Sync Tab Logic
    # ========================================
    def _init_sync_tab(self):
        """初始化文件同步标签页的状态"""
        self.ui.sync_edit_extract.setText(JsonStorage.load_last_extract_path())
        self.ui.sync_edit_src.setText(JsonStorage.load_last_source_folder())
        self.ui.sync_edit_main.setText(JsonStorage.load_main_program_path())

        self.sync_groups = JsonStorage.load_groups()
        last_group = JsonStorage.load_last_selected_group()
        self.refresh_sync_group_list(last_group)
        self.load_sync_group()

        self.auto_process_on_startup()
        self.start_monitoring()

    def select_extract_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择解压目标文件夹")
        if path:
            self.ui.sync_edit_extract.setText(path)
            JsonStorage.save_last_extract_path(path)

    def select_source_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择来源文件夹")
        if path:
            self.ui.sync_edit_src.setText(path)
            JsonStorage.save_last_source_folder(path)

    def select_target_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择目标文件夹")
        if path:
            self.ui.sync_edit_dst.setText(path)

    def select_main_program_path(self):
        path, _ = QFileDialog.getOpenFileName(self.ui, "选择主程序")
        if path:
            self.ui.sync_edit_main.setText(path)
            JsonStorage.save_main_program_path(path)

    def switch_source_version(self, direction):
        current = self.ui.sync_edit_src.text().strip()
        new_path = FileManager.get_adjacent_folder(current, direction)

        if new_path:
            self.ui.sync_edit_src.setText(new_path)
            JsonStorage.save_last_source_folder(new_path)
            self.ui.log(f"已切换版本至: {os.path.basename(new_path)}")
        else:
            self.ui.log("无法切换 (无更多版本或路径无效)", True)

    def save_sync_group(self):
        name = self.ui.sync_edit_grp_name.text().strip()
        if not name:
            QMessageBox.warning(self.ui, "提示", "请输入分组名称")
            return

        self.sync_groups[name] = {
            "target": self.ui.sync_edit_dst.text().strip(),
            "main_program": self.ui.sync_edit_main.text().strip()
        }
        JsonStorage.save_groups(self.sync_groups)
        self.refresh_sync_group_list(name)
        self.ui.log(f"已保存分组: {name}")
        JsonStorage.save_last_selected_group(name)

    def load_sync_group(self):
        name = self.ui.sync_combo_grp.currentText()
        if not name or name not in self.sync_groups:
            return
        data = self.sync_groups[name]
        self.ui.sync_edit_dst.setText(data.get("target", ""))
        self.ui.sync_edit_main.setText(data.get("main_program", ""))
        self.ui.log(f"已加载分组: {name}")
        JsonStorage.save_last_selected_group(name)

    def delete_sync_group(self):
        name = self.ui.sync_combo_grp.currentText()
        if not name or name not in self.sync_groups: return

        if QMessageBox.question(self.ui, "确认", f"确定删除分组 '{name}'?") == QMessageBox.StandardButton.Yes:
            del self.sync_groups[name]
            JsonStorage.save_groups(self.sync_groups)
            self.refresh_sync_group_list()
            self.ui.log(f"已删除分组: {name}")
            new_selection = self.ui.sync_combo_grp.currentText()
            JsonStorage.save_last_selected_group(new_selection)

    def refresh_sync_group_list(self, select_item=None):
        self.ui.refresh_sync_group_list(self.sync_groups, select_item)

    def start_copy(self):
        src = self.ui.sync_edit_src.text().strip()
        dst = self.ui.sync_edit_dst.text().strip()

        if not os.path.isdir(src) or not os.path.isdir(dst):
            QMessageBox.critical(self.ui, "错误", "来源或目标路径无效!")
            return

        self.ui.sync_start_btn.setEnabled(False)
        self.ui.sync_start_btn.setText("执行中...")

        if self.launcher_thread and self.launcher_thread.isRunning():
            self.ui.log("检测到程序正在运行，正在强制终止...")
            self.launcher_thread.stop()
            self.launcher_thread.wait()
            time.sleep(0.2)
            self.ui.log("旧程序已终止")

        self.ui.log("开始覆盖文件...")
        count, errors = FileManager.copy_files_recursive(src, dst)

        for rel_path, err in errors:
            self.ui.log(f"错误: {rel_path} - {err}", True)

        self.ui.log(f"任务完成，成功: {count}，失败: {len(errors)}")

        self.launch_program()

        self.ui.sync_start_btn.setEnabled(True)
        self.ui.sync_start_btn.setText("开始覆盖")

    def launch_program(self):
        path = self.ui.sync_edit_main.text().strip()
        if not path or not os.path.exists(path):
            self.ui.log("主程序路径无效或未设置", True)
            return

        if self.launcher_thread and self.launcher_thread.isRunning():
            self.launcher_thread.stop()
            self.launcher_thread.wait()

        self.ui.log(f"🚀 启动主程序: {path}")
        self.launcher_thread = LauncherThread(path)
        self.launcher_thread.output_signal.connect(lambda msg: self.ui.log(msg))
        self.launcher_thread.start()

    # ========================================
    #      Worker Signal Handlers
    # ========================================
    def auto_process_on_startup(self):
        self.ui.log("="*60)
        self.ui.log("程序启动 - 自动处理现有压缩文件")
        history = JsonStorage.load_history()

        # 清理无效历史记录
        valid_hist = [p for p in history if os.path.exists(p)]
        if len(history) != len(valid_hist):
            JsonStorage.save_history(valid_hist)
            history = valid_hist

        self.ui.log("历史记录已加载和验证")
        self.ui.log("="*60)

    def start_monitoring(self):
        self.monitor_thread = MonitorThread()
        self.monitor_thread.log_signal.connect(self.ui.log)
        self.monitor_thread.new_file_detected.connect(self.on_new_file)
        self.monitor_thread.start()

    def on_new_file(self, new_files):
        extract_path = self.ui.sync_edit_extract.text().strip()
        if not extract_path or not os.path.isdir(extract_path):
            QMessageBox.critical(self.ui, "错误", "请先设置有效的解压目标文件夹!")
            return

        self.extract_thread = ExtractThread(new_files, extract_path)
        self.extract_thread.log_signal.connect(self.ui.log)
        self.extract_thread.finished_signal.connect(self.on_extract_finished)
        self.extract_thread.start()

    def on_extract_finished(self, path):
        if path:
            self.ui.sync_edit_src.setText(path)
            JsonStorage.save_last_source_folder(path)
            self.ui.log(f"✅ 来源路径已自动填充: {path}")
        self.ui.log("="*60)

    def close_threads(self):
        if self.monitor_thread: self.monitor_thread.stop()
        if self.launcher_thread: self.launcher_thread.stop()

    def _run_shell_command(self, command):
        """通用shell命令执行函数"""
        return subprocess.run(
            command, shell=True, capture_output=True, text=True,
            encoding='utf-8', errors='ignore'
        ).stdout.strip()
