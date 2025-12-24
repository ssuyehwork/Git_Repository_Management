import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.utils.dependency_manager import DependencyManager
from app.ui.main_window import MainWindow

def main():
    """主应用程序入口"""
    # 1. 初始化Qt应用实例，以便能够显示消息框
    app = QApplication(sys.argv)

    # 2. 检查核心依赖：Git
    if not DependencyManager.check_git():
        QMessageBox.critical(
            None,
            "Git未安装",
            "未检测到Git！请先安装Git并确保其在系统路径中。\n"
            "可以从 https://git-scm.com/downloads 下载。"
        )
        sys.exit(1) # 关键：如果Git未安装，则终止程序

    # 3. 检查并安装Python包依赖
    DependencyManager.check_and_install()

    # 4. 实例化主窗口并显示
    window = MainWindow()
    window.show()

    # 5. 启动事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
