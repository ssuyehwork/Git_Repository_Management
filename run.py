import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt, QTimer
from app.utils.dependency_manager import DependencyManager
from app.ui.main_window import MainWindow

def create_splash_screen():
    """创建并返回一个启动画面实例"""
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(QColor(15, 23, 42))

    painter = QPainter(splash_pix)
    painter.setPen(QColor(99, 102, 241))
    painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
    painter.drawText(splash_pix.rect(), Qt.AlignmentFlag.AlignCenter,
                    "GitHub 仓库智能管理器\n\nv3.0 (模块化版)")
    painter.end()

    splash = QSplashScreen(splash_pix)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash

def main():
    """主应用程序入口"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # ... (调色板设置代码省略)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    # ...
    app.setPalette(palette)

    # 显示启动画面
    splash = create_splash_screen()
    splash.show()
    app.processEvents()

    if not DependencyManager.check_git():
        # ... (Git检查代码省略)
        sys.exit(1)

    DependencyManager.check_and_install()

    # 创建主窗口
    window = MainWindow()

    # 在显示主窗口前关闭启动画面
    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
