"""
应用程序主入口
"""
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor

from app.utils.dependency_manager import DependencyManager
from app.utils.splash_screen import create_splash_screen
from app.utils.instance_lock import SingleInstanceManager
from app.ui.main_window import GitHubManager
from app.logic.app_logic import AppLogic

def set_dark_theme(app):
    """设置暗色主题"""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    # ... (其他颜色设置保持不变)
    app.setPalette(palette)

def main():
    """主函数"""
    # 1. 启动时检查依赖
    DependencyManager.check_and_install()

    # 2. 创建应用实例
    app = QApplication(sys.argv)

    # 3. 单实例控制
    instance_manager = SingleInstanceManager(on_exit_callback=app.quit)
    is_first = instance_manager.try_start_server()

    if not is_first:
        SingleInstanceManager.notify_existing_instance_to_exit()
        time.sleep(0.5)
        # 再次尝试抢占（后例接管模式）
        if not instance_manager.try_start_server():
            sys.exit(0) # 如果仍然失败，则退出

    app.setStyle('Fusion')
    set_dark_theme(app)

    # 4. 显示启动画面
    splash = create_splash_screen()
    splash.show()
    app.processEvents()

    # 5. 创建UI和逻辑实例
    window = GitHubManager()
    logic = AppLogic(window)

    # 6. 确保线程在关闭时退出
    app.aboutToQuit.connect(logic.close_threads)

    # 7. 关闭启动画面并显示主窗口
    QTimer.singleShot(1500, lambda: (splash.close(), window.show()))

    # 8. 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
