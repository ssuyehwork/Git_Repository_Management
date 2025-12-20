"""
Git 操作工作线程
"""
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class GitWorker(QThread):
    """Git 操作工作线程 - 非阻塞式执行"""
    progress = pyqtSignal(str, str)  # (消息, 类型)
    finished = pyqtSignal(bool, str)
    execute_script = pyqtSignal(str)  # 执行脚本信号

    def __init__(self, operation, local_path, remote_url, config):
        super().__init__()
        self.operation = operation
        self.local_path = local_path
        self.remote_url = remote_url
        self.config = config
        self.backup_path = None

    def run(self):
        """执行Git操作"""
        try:
            # 切换到仓库目录
            if not os.path.exists(self.local_path):
                os.makedirs(self.local_path, exist_ok=True)

            os.chdir(self.local_path)

            # 配置Git用户信息
            if self.config.get('username') and self.config.get('email'):
                self._run_cmd(
                    f'git config user.name "{self.config["username"]}"',
                    "配置用户名", silent=True
                )
                self._run_cmd(
                    f'git config user.email "{self.config["email"]}"',
                    "配置邮箱", silent=True
                )

            # 执行相应操作
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
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if result.returncode != 0 and not silent:
            error_msg = result.stderr.strip() or result.stdout.strip()
            if error_msg:
                raise Exception(f"{description} 失败: {error_msg}")

        return result.stdout.strip()

    def _init_repo(self):
        """初始化仓库"""
        self.progress.emit("🔧 正在初始化Git仓库...", "info")

        if not os.path.exists('.git'):
            self._run_cmd("git init", "初始化Git仓库")
            self._run_cmd(f'git remote add origin "{self.remote_url}"', "添加远程仓库")
            self._run_cmd("git branch -M main", "创建main分支")
            self.progress.emit("✓ 仓库初始化完成", "success")
        else:
            # 检查远程仓库
            try:
                current_remote = self._run_cmd("git remote get-url origin", "获取远程URL", silent=True)
                if current_remote != self.remote_url:
                    self._run_cmd(f'git remote set-url origin "{self.remote_url}"', "更新远程仓库URL")
                    self.progress.emit("✓ 远程仓库已更新", "success")
                else:
                    self.progress.emit("✓ 仓库已存在且配置正确", "success")
            except:
                self._run_cmd(f'git remote add origin "{self.remote_url}"', "添加远程仓库")

        self.finished.emit(True, "✓ 仓库初始化完成")

    def _create_backup(self):
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(self.local_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        self.backup_path = backup_dir / f"backup_{timestamp}"

        self.progress.emit(f"📦 正在创建备份到: {self.backup_path.name}", "info")

        # 复制整个目录
        shutil.copytree(self.local_path, self.backup_path, dirs_exist_ok=True)

        self.progress.emit(f"✓ 备份完成: {self.backup_path}", "success")
        return self.backup_path

    def _find_main_script(self):
        """查找主程序脚本"""
        # 查找可能的主程序文件
        possible_names = ['main.py', 'app.py', 'run.py', 'start.py', '__main__.py']

        for name in possible_names:
            script_path = Path(self.local_path) / name
            if script_path.exists():
                return str(script_path)

        # 如果没有找到,查找第一个.py文件
        for file in Path(self.local_path).glob("*.py"):
            if file.name != "__init__.py":
                return str(file)

        return None

    def _check_status(self):
        """检查仓库状态"""
        try:
            # 检查是否是Git仓库
            if not os.path.exists('.git'):
                self.finished.emit(False, "当前目录不是Git仓库")
                return

            # 获取分支
            branch = self._run_cmd("git branch --show-current", "获取当前分支", silent=True)
            self.progress.emit(f"当前分支: {branch or 'main'}", "info")

            # 检查状态
            status = self._run_cmd("git status --porcelain", "检查文件状态", silent=True)
            if status:
                changes = len(status.split('\n'))
                self.progress.emit(f"未提交更改: {changes} 个文件", "warning")
            else:
                self.progress.emit("工作区干净", "success")

            self.finished.emit(True, "状态检查完成")
        except Exception as e:
            self.finished.emit(False, f"状态检查失败: {str(e)}")

    def _smart_upload(self):
        """智能上传 - 检测更改并推送"""
        self.progress.emit("📊 正在分析本地文件变化...", "info")

        # 确保仓库已初始化
        if not os.path.exists('.git'):
            self._init_repo()

        # 检查是否有变化
        status = subprocess.run(
            "git status --porcelain",
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()

        if not status:
            self.finished.emit(True, "✓ 工作区干净,没有需要上传的更改")
            return

        # 显示变化统计
        changes = status.split('\n')
        self.progress.emit(f"检测到 {len(changes)} 个文件变化", "info")

        # 添加所有文件
        self._run_cmd("git add .", "添加文件到暂存区")

        # 提交更改
        commit_msg = f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._run_cmd(f'git commit -m "{commit_msg}"', "提交更改")

        # 推送到远程
        try:
            self._run_cmd("git push origin main", "推送到远程仓库")
        except:
            # 如果是第一次推送
            self._run_cmd("git push -u origin main", "首次推送到远程仓库")

        self.finished.emit(True, f"✓ 上传成功! {len(changes)} 个文件已同步到远程仓库")

    def _smart_download(self):
        """智能下载 - 拉取远程更新"""
        self.progress.emit("🔍 正在检查远程仓库更新...", "info")

        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化,请先初始化仓库")
            return

        # 获取远程更新
        self._run_cmd("git fetch origin", "获取远程更新信息")

        # 检查是否有远程更新
        try:
            behind = self._run_cmd(
                "git rev-list HEAD..origin/main --count",
                "检查远程更新",
                silent=True
            )

            if behind and behind != "0":
                self.progress.emit(f"发现 {behind} 个远程提交", "info")
                self._run_cmd("git pull origin main", "拉取远程更新")
                self.finished.emit(True, f"✓ 下载成功! 已更新 {behind} 个提交")
            else:
                self.finished.emit(True, "✓ 本地已是最新版本")
        except Exception as e:
            # 如果分支不存在,尝试直接拉取
            try:
                self._run_cmd("git pull origin main", "拉取远程更新")
                self.finished.emit(True, "✓ 下载成功! 本地仓库已更新")
            except:
                self.finished.emit(False, f"下载失败: {str(e)}")

    def _smart_sync(self):
        """智能同步 - 双向同步"""
        self.progress.emit("🔄 正在执行双向智能同步...", "info")

        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化,请先初始化仓库")
            return

        # 1. 保存本地更改
        status = subprocess.run(
            "git status --porcelain",
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()

        has_local_changes = bool(status)

        if has_local_changes:
            self.progress.emit("保存本地更改...", "info")
            self._run_cmd("git add .", "添加本地更改")
            commit_msg = f"Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self._run_cmd(f'git commit -m "{commit_msg}"', "提交本地更改")

        # 2. 拉取远程更新
        self.progress.emit("拉取远程更新...", "info")
        try:
            self._run_cmd("git fetch origin", "获取远程信息")
            self._run_cmd("git pull origin main --rebase", "合并远程更改")
        except:
            # 如果有冲突,尝试使用merge
            try:
                self._run_cmd("git pull origin main", "合并远程更改")
            except:
                pass

        # 3. 推送到远程
        self.progress.emit("推送到远程仓库...", "info")
        try:
            self._run_cmd("git push origin main", "推送更新")
        except:
            self._run_cmd("git push -u origin main", "推送更新")

        self.finished.emit(True, "✓ 同步完成! 本地与远程已保持一致")

    def _smart_overwrite(self):
        """强制覆盖远程"""
        self.progress.emit("⚠ 正在强制覆盖远程仓库...", "warning")

        if not os.path.exists('.git'):
            self._init_repo()

        # 添加并提交所有文件
        self._run_cmd("git add .", "添加所有文件")
        commit_msg = f"Force overwrite: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        try:
            self._run_cmd(f'git commit -m "{commit_msg}"', "提交更改")
        except:
            pass  # 可能没有更改

        # 强制推送
        self._run_cmd("git push -f origin main", "强制推送")

        self.finished.emit(True, "✓ 覆盖完成! 远程仓库已被本地版本替换")

    def _smart_delete(self):
        """删除远程所有文件"""
        self.progress.emit("🗑 正在清理远程仓库...", "warning")

        if not os.path.exists('.git'):
            self.finished.emit(False, "本地仓库未初始化")
            return

        # 删除所有文件并提交
        self._run_cmd("git rm -rf .", "删除所有文件")
        self._run_cmd('git commit -m "Clean repository"', "提交删除")
        self._run_cmd("git push origin main", "推送删除")

        self.finished.emit(True, "✓ 删除完成! 远程文件已清理")
