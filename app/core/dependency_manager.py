# app/core/dependency_manager.py
"""
智能依赖管理器，负责检查和安装所需的Python包。
"""
import sys
import subprocess
import importlib

from app.config import settings

class DependencyManager:
    """智能依赖管理器"""

    @staticmethod
    def check_and_install():
        """检查并安装所有依赖"""
        print("=" * 60)
        print(f"🔍 {settings.APP_NAME} - 依赖检查系统")
        print("=" * 60)

        missing_packages = []
        installed_packages = set()

        # 检查依赖
        for module_name, package_name in settings.REQUIRED_PACKAGES.items():
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
