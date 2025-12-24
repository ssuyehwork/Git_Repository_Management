import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt, QTimer
from app.utils.dependency_manager import DependencyManager
from app.ui.main_window import MainWindow
from app.ui.styles import get_stylesheet

def create_splash_screen():
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
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 应用全局样式表
    app.setStyleSheet(get_stylesheet())

    splash = create_splash_screen()
    splash.show()
    app.processEvents()

    if not DependencyManager.check_git():
        QMessageBox.critical(None, "Git未安装", "未检测到Git！请先安装。")
        sys.exit(1)

    DependencyManager.check_and_install()

    window = MainWindow()

    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
