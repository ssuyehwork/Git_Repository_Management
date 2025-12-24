"""
GitHub 仓库智能管理器 - 专业版
自动依赖检测与安装 | 智能Git操作 | 企业级架构
Author: Professional Developer
Version: 2.0
"""

import sys
import os
import json
import subprocess
import importlib
import shutil
from pathlib import Path
from datetime import datetime


# ================================
# 依赖管理系统
# ================================
class DependencyManager:
    """智能依赖管理器"""
    
    REQUIRED_PACKAGES = {
        'PyQt6': 'PyQt6',
        'PyQt6.QtWidgets': 'PyQt6',
        'PyQt6.QtCore': 'PyQt6',
        'PyQt6.QtGui': 'PyQt6'
    }
    
    @staticmethod
    def check_and_install():
        """检查并安装所有依赖"""
        print("=" * 60)
        print("🔍 GitHub 仓库管理器 - 依赖检查系统")
        print("=" * 60)
        
        missing_packages = []
        installed_packages = set()
        
        # 检查依赖
        for module_name, package_name in DependencyManager.REQUIRED_PACKAGES.items():
            if package_name in installed_packages:
                continue
                
            try:
                importlib.import_module(module_name)
                print(f"✓ {package_name:20} - 已安装")
                installed_packages.add(package_name)
            except ImportError:
                if package_name not in missing_packages:
                    print(f"✗ {package_name:20} - 未安装")
                    missing_packages.append(package_name)
        
        # 安装缺失的包
        if missing_packages:
            print("\n" + "=" * 60)
            print(f"📦 发现 {len(missing_packages)} 个缺失的依赖包")
            print("=" * 60)
            
            for package in missing_packages:
                DependencyManager._install_package(package)
            
            print("\n" + "=" * 60)
            print("✓ 所有依赖已成功安装!")
            print("=" * 60)
            print("🚀 正在启动应用程序...\n")
        else:
            print("\n✓ 所有依赖已就绪!")
            print("🚀 正在启动应用程序...\n")
        
        return True
    
    @staticmethod
    def _install_package(package_name):
        """安装单个包"""
        print(f"\n📥 正在安装 {package_name}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name, "-q"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✓ {package_name} 安装成功!")
        except subprocess.CalledProcessError as e:
            print(f"✗ {package_name} 安装失败!")
            print(f"错误信息: {e}")
            print(f"请手动执行: pip install {package_name}")
            sys.exit(1)
    
    @staticmethod
    def check_git():
        """检查Git是否安装"""
        try:
            subprocess.run(["git", "--version"], 
                         capture_output=True, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


# 启动时检查依赖
if __name__ == '__main__':
    DependencyManager.check_and_install()


# ================================
# 导入Qt库
# ================================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QMessageBox, QFileDialog, QProgressBar, QSplashScreen,
    QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter


# ================================
# Git操作工作线程
# ================================
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
        from datetime import datetime
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
            from datetime import datetime
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
        from datetime import datetime
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


# ================================
# 主窗口类
# ================================
class GitHubManager(QMainWindow):
    """GitHub仓库智能管理器 - 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / ".github_manager_config.json"
        self.profiles = {}  # 用于存储多个配置方案
        self.current_profile_name = None # 用于跟踪当前选中的方案
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
        self.load_config()
        QTimer.singleShot(500, self.auto_check_status)
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub 仓库智能管理器 v2.0 Professional")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet(self._get_stylesheet())
        
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
        
        # 状态栏
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
        
        # 配置方案
        layout.addWidget(QLabel("📂 配置方案:"), 0, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self._load_profile_to_ui)
        layout.addWidget(self.profile_combo, 0, 1, 1, 2)

        # 本地路径
        layout.addWidget(QLabel("📁 本地路径:"), 1, 0)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("例如: G:\\PYthon\\GitHub 仓库管理")
        layout.addWidget(self.local_path_input, 1, 1)
        
        browse_btn = QPushButton("📂 浏览")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(browse_btn, 1, 2)
        
        # 远程URL
        layout.addWidget(QLabel("🌐 远程仓库:"), 2, 0)
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText("https://github.com/username/repo.git")
        layout.addWidget(self.remote_url_input, 2, 1, 1, 2)
        
        # Git用户名
        layout.addWidget(QLabel("👤 用户名:"), 3, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Git用户名 (可选)")
        layout.addWidget(self.username_input, 3, 1, 1, 2)
        
        # Git邮箱
        layout.addWidget(QLabel("📧 邮箱:"), 4, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Git邮箱 (可选)")
        layout.addWidget(self.email_input, 4, 1, 1, 2)
        
        # 按钮行
        button_layout = QHBoxLayout()

        btn_style = """
            QPushButton {{
                color: white; font-weight: bold; padding: 8px 15px;
                border-radius: 6px; font-size: 13px;
            }}
            QPushButton:hover {{ background: {hover_color}; }}
        """

        new_btn = QPushButton("➕ 新建方案")
        new_btn.setStyleSheet(btn_style.format(hover_color="#059669") + \
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669); }")
        new_btn.clicked.connect(self.create_new_profile)
        button_layout.addWidget(new_btn)
        
        update_btn = QPushButton("💾 更新方案")
        update_btn.setStyleSheet(btn_style.format(hover_color="#4f46e5") + \
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #4f46e5); }")
        update_btn.clicked.connect(self.update_current_profile)
        button_layout.addWidget(update_btn)

        delete_btn = QPushButton("❌ 删除方案")
        delete_btn.setStyleSheet(btn_style.format(hover_color="#d97706") + \
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706); }")
        delete_btn.clicked.connect(self.delete_current_profile)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch(1)

        refresh_btn = QPushButton("🔄 刷新状态")
        refresh_btn.setStyleSheet(btn_style.format(hover_color="#4338ca") + \
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #4338ca); }")
        refresh_btn.clicked.connect(self.auto_check_status)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout, 5, 0, 1, 3)
        
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
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color, 40)};
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
        
        # 清空日志按钮
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
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择本地仓库路径",
            self.local_path_input.text() or str(Path.home())
        )
        if folder:
            self.local_path_input.setText(folder)
    
    def load_config(self):
        """加载配置"""
        try:
            if not self.config_file.exists():
                # 如果没有配置文件，创建一个默认配置
                self.profiles = {
                    "默认配置": {
                        'local_path': r"G:\PYthon\GitHub 仓库管理\GitHub 仓库管理",
                        'remote_url': "https://github.com/ssuyehwork/Syn_Github_Upload.git",
                        'username': '',
                        'email': ''
                    }
                }
                self.current_profile_name = "默认配置"
                self._save_config_data()
                self.log("ℹ️ 未找到配置文件，已创建默认配置", "info")
            else:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 兼容旧格式：检查顶层是否存在 local_path
                if 'local_path' in config:
                    self.profiles = {"默认配置": config}
                    self.current_profile_name = "默认配置"
                    self._save_config_data() # 迁移到新格式
                    self.log("🔄 旧配置文件已成功迁移到新格式", "success")
                else: # 新格式
                    self.profiles = config.get('profiles', {})
                    self.current_profile_name = config.get('last_profile')
                    self.log("✓ 配置已从本地加载", "success")

            self._update_profile_combo()

        except Exception as e:
            self.log(f"⚠ 加载配置失败: {str(e)}", "error")
            QMessageBox.critical(self, "错误", f"加载配置时发生严重错误: {e}")

    def _update_profile_combo(self):
        """更新配置方案下拉菜单"""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()

        if not self.profiles:
            self.profile_combo.addItem("无可用配置")
            self._clear_input_fields()
        else:
            self.profile_combo.addItems(self.profiles.keys())
            if self.current_profile_name in self.profiles:
                self.profile_combo.setCurrentText(self.current_profile_name)
                self._load_profile_to_ui(self.current_profile_name)
            elif self.profiles:
                first_profile_name = list(self.profiles.keys())[0]
                self.profile_combo.setCurrentText(first_profile_name)
                self._load_profile_to_ui(first_profile_name)
                self.current_profile_name = first_profile_name

        self.profile_combo.blockSignals(False)
        self.auto_check_status()

    def _load_profile_to_ui(self, profile_name):
        """将指定配置方案加载到UI输入框"""
        profile_data = self.profiles.get(profile_name, {})
        self.local_path_input.setText(profile_data.get('local_path', ''))
        self.remote_url_input.setText(profile_data.get('remote_url', ''))
        self.username_input.setText(profile_data.get('username', ''))
        self.email_input.setText(profile_data.get('email', ''))
        self.current_profile_name = profile_name

    def _clear_input_fields(self):
        """清空所有输入框"""
        self.local_path_input.clear()
        self.remote_url_input.clear()
        self.username_input.clear()
        self.email_input.clear()

    def _save_config_data(self):
        """将内存中的配置数据写入文件"""
        try:
            config_data = {
                'profiles': self.profiles,
                'last_profile': self.current_profile_name
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.log(f"✗ 保存配置文件失败: {str(e)}", "error")
            QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")
            return False

    def create_new_profile(self):
        """创建新的配置方案"""
        profile_name, ok = QInputDialog.getText(self, "新建配置方案", "请输入方案名称:")
        if ok and profile_name:
            if profile_name in self.profiles:
                QMessageBox.warning(self, "名称已存在", f"名为 '{profile_name}' 的配置方案已存在。")
                return

            # 验证输入
            if not self.local_path_input.text() or not self.remote_url_input.text():
                QMessageBox.warning(self, "信息不完整", "请先填写本地路径和远程仓库URL。")
                return

            new_profile = {
                'local_path': self.local_path_input.text(),
                'remote_url': self.remote_url_input.text(),
                'username': self.username_input.text(),
                'email': self.email_input.text()
            }
            
            self.profiles[profile_name] = new_profile
            self.current_profile_name = profile_name
            
            if self._save_config_data():
                self.log(f"✓ 新建并保存了配置方案: {profile_name}", "success")
                self._update_profile_combo()
                QMessageBox.information(self, "成功", f"已创建新的配置方案: {profile_name}")

    def update_current_profile(self):
        """更新当前选中的配置方案"""
        if not self.current_profile_name:
            QMessageBox.warning(self, "无活动方案", "没有选中的配置方案可供更新。")
            return

        # 验证输入
        if not self.local_path_input.text() or not self.remote_url_input.text():
            QMessageBox.warning(self, "信息不完整", "请填写本地路径和远程仓库URL。")
            return

        updated_profile = {
            'local_path': self.local_path_input.text(),
            'remote_url': self.remote_url_input.text(),
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

        self.profiles[self.current_profile_name] = updated_profile

        if self._save_config_data():
            self.log(f"✓ 更新了配置方案: {self.current_profile_name}", "success")
            QMessageBox.information(self, "成功", f"配置方案 '{self.current_profile_name}' 已更新。")

    def delete_current_profile(self):
        """删除当前选中的配置方案"""
        if not self.current_profile_name:
            QMessageBox.warning(self, "无活动方案", "没有选中的配置方案可供删除。")
            return
            
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "无法删除", "这是最后一个配置方案，无法删除。")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除配置方案 '{self.current_profile_name}' 吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.profiles[self.current_profile_name]
            self.current_profile_name = list(self.profiles.keys())[0] # 切换到第一个
            
            if self._save_config_data():
                self.log(f"✓ 删除了配置方案: {self.current_profile_name}", "success")
                self._update_profile_combo()
                QMessageBox.information(self, "成功", "配置方案已删除。")
    
    def log(self, message, msg_type="info"):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 颜色映射
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
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def auto_check_status(self):
        """自动检查仓库状态"""
        local_path = self.local_path_input.text()
        if not local_path or not os.path.exists(local_path):
            self.update_status_display("--", "--", "--", "未配置")
            return
        
        try:
            os.chdir(local_path)
            
            # 检查是否是Git仓库
            if not os.path.exists('.git'):
                self.update_status_display("--", "--", "--", "未初始化")
                return
            
            # 获取分支
            branch = subprocess.run(
                "git branch --show-current",
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            ).stdout.strip() or "main"
            
            # 未提交更改
            status = subprocess.run(
                "git status --porcelain",
                shell=True,
                capture_output=True,
                text=True
            ).stdout
            uncommitted = len(status.strip().split('\n')) if status.strip() else 0
            
            # 未推送提交
            try:
                unpushed = subprocess.run(
                    "git rev-list @{u}..HEAD --count",
                    shell=True,
                    capture_output=True,
                    text=True
                ).stdout.strip()
            except:
                unpushed = "--"
            
            # 更新显示
            self.update_status_display(
                branch,
                str(uncommitted),
                str(unpushed),
                "✓ 已连接" if unpushed != "--" else "本地仓库"
            )
            
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
        # 验证配置
        local_path = self.local_path_input.text()
        remote_url = self.remote_url_input.text()
        
        if not local_path:
            QMessageBox.warning(self, "警告", "请先配置本地路径!")
            return
        
        if not remote_url and operation != "status":
            QMessageBox.warning(self, "警告", "请先配置远程仓库!")
            return
        
        # 确认对话框
        if confirm_msg:
            reply = QMessageBox.question(
                self, "确认操作", confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 禁用UI
        self.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage(f"正在执行: {operation}")
        
        # 创建工作线程
        config = {
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }
        
        self.worker = GitWorker(operation, local_path, remote_url, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.execute_script.connect(self.execute_downloaded_script)
        self.worker.start()
    
    def on_progress(self, message, msg_type):
        """进度回调"""
        self.log(message, msg_type)
    
    def on_operation_finished(self, success, message):
        """操作完成回调"""
        self.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("就绪")
        
        self.log(message, "success" if success else "error")
        
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)
        
        # 刷新状态
        QTimer.singleShot(500, self.auto_check_status)
    
    def execute_downloaded_script(self, script_path):
        """执行下载后的脚本"""
        try:
            self.log(f"🚀 正在启动: {Path(script_path).name}", "info")
            
            # 使用subprocess在新进程中运行脚本
            if sys.platform == "win32":
                # Windows系统
                subprocess.Popen(
                    [sys.executable, script_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=str(Path(script_path).parent)
                )
            else:
                # Linux/Mac系统
                subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=str(Path(script_path).parent)
                )
            
            self.log(f"✓ 程序已在新窗口启动", "success")
            
        except Exception as e:
            self.log(f"✗ 启动程序失败: {str(e)}", "error")
            QMessageBox.warning(
                self,
                "启动失败",
                f"自动启动程序失败:\n{str(e)}\n\n请手动运行: {script_path}"
            )
    
    def smart_upload(self):
        """智能上传"""
        self.execute_operation("upload")
    
    def smart_download(self):
        """智能下载"""
        self.execute_operation("download")
    
    def smart_sync(self):
        """智能同步"""
        self.execute_operation(
            "sync",
            "将执行双向同步操作:\n\n"
            "1. 保存本地更改\n"
            "2. 拉取远程更新\n"
            "3. 推送到远程\n\n"
            "确定继续吗?"
        )
    
    def smart_overwrite(self):
        """强制覆盖"""
        self.execute_operation(
            "overwrite",
            "⚠ 警告: 强制覆盖操作\n\n"
            "这将用本地版本强制覆盖远程仓库!\n"
            "远程的更改将永久丢失!\n\n"
            "确定要继续吗?"
        )
    
    def smart_delete(self):
        """删除远程"""
        reply = QMessageBox.critical(
            self, 
            "⚠ 危险操作",
            "这将删除远程仓库的所有文件!\n"
            "此操作不可恢复!\n\n"
            "请输入 'DELETE' 确认:",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Ok:
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(
                self, 
                "确认删除", 
                "请输入 'DELETE' 确认删除:"
            )
            if ok and text == "DELETE":
                self.execute_operation("delete")
    
    def init_repo(self):
        """初始化仓库"""
        self.execute_operation("init")


# ================================
# 启动画面
# ================================
def create_splash_screen():
    """创建启动画面"""
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(QColor(15, 23, 42))
    
    painter = QPainter(splash_pix)
    painter.setPen(QColor(99, 102, 241))
    painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
    painter.drawText(splash_pix.rect(), Qt.AlignmentFlag.AlignCenter, 
                    "GitHub 仓库智能管理器\n\nv2.0 Professional")
    painter.end()
    
    splash = QSplashScreen(splash_pix)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash


# ================================
# 主函数
# ================================
def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置暗色主题
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(241, 245, 249))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 41, 59))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(51, 65, 85))
    palette.setColor(QPalette.ColorRole.Text, QColor(241, 245, 249))
    palette.setColor(QPalette.ColorRole.Button, QColor(71, 85, 105))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # 显示启动画面
    splash = create_splash_screen()
    splash.show()
    app.processEvents()
    
    # 创建主窗口
    window = GitHubManager()
    
    # 关闭启动画面并显示主窗口
    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
