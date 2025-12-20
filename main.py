"""
应用程序主入口
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor

from app.utils.dependency_manager import DependencyManager
from app.utils.splash_screen import create_splash_screen
from app.ui.main_window import GitHubManager
from app.logic.app_logic import AppLogic

def set_dark_theme(app):
    """设置暗色主题"""
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

def main():
    """主函数"""
    # 1. 启动时检查依赖
    DependencyManager.check_and_install()

    # 2. 创建应用实例
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    set_dark_theme(app)

    # 3. 显示启动画面
    splash = create_splash_screen()
    splash.show()
    app.processEvents()

    # 4. 创建UI和逻辑实例
    window = GitHubManager()
    logic = AppLogic(window) # 将UI实例传递给逻辑层

    # 5. 关闭启动画面并显示主窗口
    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)

    # 6. 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
