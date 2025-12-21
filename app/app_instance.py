# app/app_instance.py
"""
负责管理 QApplication 实例和主窗口的生命周期。
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from app.core.dependency_manager import DependencyManager
from app.ui.main_window import MainWindow
from app.ui.splash import create_splash_screen
from app.ui.styling import set_dark_theme, get_main_stylesheet

class AppInstance:
    """
    管理应用程序的生命周期。
    """
    def __init__(self):
        # 1. 依赖检查
        DependencyManager.check_and_install()
        if not DependencyManager.check_git():
            # (这里需要一个UI无关的方式来显示错误)
            print("错误: 未检测到Git!")
            sys.exit(1)

        # 2. 创建 QApplication 实例
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')

        # 3. 设置主题和样式
        set_dark_theme(self.app)
        self.app.setStyleSheet(get_main_stylesheet())

        # 4. 创建和显示启动画面
        self.splash = create_splash_screen()
        self.splash.show()
        self.app.processEvents()

        # 5. 延迟创建主窗口
        QTimer.singleShot(1500, self._show_main_window)

    def _show_main_window(self):
        """创建并显示主窗口，然后关闭启动画面"""
        self.window = MainWindow()
        self.window.show()
        self.splash.close()

    def run(self):
        """
        启动应用程序的事件循环。
        :return: 应用程序的退出代码。
        """
        return self.app.exec()
