import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class GitWorker(QThread):
    """Git 操作工作线程 - 非阻塞式执行"""
    progress = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, operation, local_path, remote_url, config):
        super().__init__()
        self.operation = operation
        self.local_path = local_path
        self.remote_url = remote_url
        self.config = config

    def run(self):
        """执行Git操作"""
        try:
            if not os.path.exists(self.local_path):
                os.makedirs(self.local_path, exist_ok=True)

            # 切换工作目录至本地仓库
            # 这是关键一步，所有git命令都需要在此路径下执行
            os.chdir(self.local_path)

            if self.config.get('username') and self.config.get('email'):
                self._run_cmd(f'git config user.name "{self.config["username"]}"', "配置用户名", silent=True)
                self._run_cmd(f'git config user.email "{self.config["email"]}"', "配置邮箱", silent=True)

            operations = {
                "upload": self._smart_upload,
                "download": self._smart_download,
                "sync": self._smart_sync,
                "overwrite": self._smart_overwrite,
                "delete": self._smart_delete,
                "init": self._init_repo,
                "status": self._check_status
            }

            if self.operation in operations:
                operations[self.operation]()
            else:
                raise Exception(f"未知操作: {self.operation}")

        except Exception as e:
            self.finished.emit(False, f"操作失败: {str(e)}")

    def _run_cmd(self, cmd, description, silent=False):
        """执行命令并发送进度"""
        if not silent:
            self.progress.emit(f"▶ {description}", "info")

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            encoding='utf-8', errors='ignore'
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            if not silent or not error_msg:
                 raise Exception(f"{description} 失败: {error_msg}")

        return result.stdout.strip()

    def _init_repo(self):
        """初始化仓库"""
        self.progress.emit("🔧 正在初始化Git仓库...", "info")
        if not os.path.exists('.git'):
            self._run_cmd("git init", "初始化Git仓库")
            self._run_cmd(f'git remote add origin "{self.remote_url}"', "添加远程仓库")
            self._run_cmd("git branch -M main", "创建main分支")
        else:
            try:
                current_remote = self._run_cmd("git remote get-url origin", "获取远程URL", silent=True)
                if current_remote != self.remote_url:
                    self._run_cmd(f'git remote set-url origin "{self.remote_url}"', "更新远程仓库URL")
            except Exception:
                self._run_cmd(f'git remote add origin "{self.remote_url}"', "添加远程仓库")
        self.finished.emit(True, "✓ 仓库初始化/验证完成")

    def _check_status(self):
        """检查仓库状态"""
        # ... (此处省略具体实现, 因为状态检查现在由UI层通过直接调用git命令完成)
        # 为了保持接口一致性，我们依然保留这个方法
        pass

    def _smart_upload(self):
        self.progress.emit("📊 正在分析本地文件变化...", "info")
        if not os.path.exists('.git'): self._init_repo()

        status = self._run_cmd("git status --porcelain", "检查文件状态", silent=True)
        if not status:
            self.finished.emit(True, "✓ 工作区干净,没有需要上传的更改")
            return

        changes = status.split('\n')
        self.progress.emit(f"检测到 {len(changes)} 个文件变化", "info")
        self._run_cmd("git add .", "添加文件到暂存区")
        commit_msg = f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._run_cmd(f'git commit -m "{commit_msg}"', "提交更改")
        self._run_cmd("git push origin main", "推送到远程仓库")
        self.finished.emit(True, f"✓ 上传成功! {len(changes)} 个文件已同步")

    def _smart_download(self):
        self.progress.emit("🔍 正在检查远程仓库更新...", "info")
        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化,请先初始化")
            return

        self._run_cmd("git fetch origin", "获取远程更新信息")
        behind = self._run_cmd("git rev-list HEAD..origin/main --count", "检查远程更新", silent=True)

        if behind and behind != "0":
            self.progress.emit(f"发现 {behind} 个远程提交", "info")
            self._run_cmd("git pull origin main", "拉取远程更新")
            self.finished.emit(True, f"✓ 下载成功! 已更新 {behind} 个提交")
        else:
            self.finished.emit(True, "✓ 本地已是最新版本")

    def _smart_sync(self):
        self.progress.emit("🔄 正在执行双向智能同步...", "info")
        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化,请先初始化")
            return

        has_local_changes = bool(self._run_cmd("git status --porcelain", "检查状态", silent=True))
        if has_local_changes:
            self.progress.emit("保存本地更改...", "info")
            self._run_cmd("git add .", "添加本地更改")
            commit_msg = f"Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self._run_cmd(f'git commit -m "{commit_msg}"', "提交本地更改")

        self.progress.emit("拉取远程更新...", "info")
        self._run_cmd("git pull origin main --rebase", "合并远程更改")

        self.progress.emit("推送到远程仓库...", "info")
        self._run_cmd("git push origin main", "推送更新")
        self.finished.emit(True, "✓ 同步完成!")

    def _smart_overwrite(self):
        self.progress.emit("⚠ 正在强制覆盖远程仓库...", "warning")
        if not os.path.exists('.git'): self._init_repo()

        self._run_cmd("git add .", "添加所有文件")
        commit_msg = f"Force overwrite: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            self._run_cmd(f'git commit -m "{commit_msg}"', "提交更改")
        except Exception:
             # 如果没有本地更改，提交会失败，这很正常
            pass
        self._run_cmd("git push -f origin main", "强制推送")
        self.finished.emit(True, "✓ 覆盖完成! 远程仓库已被本地版本替换")

    def _smart_delete(self):
        self.progress.emit("🗑 正在清理远程仓库...", "warning")
        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化")
            return

        self._run_cmd("git rm -rf .", "删除所有文件")
        self._run_cmd('git commit --allow-empty -m "Clean repository"', "提交删除")
        self._run_cmd("git push origin main", "推送删除")
        self.finished.emit(True, "✓ 删除完成! 远程文件已清理")
