"""
启动画面
"""
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont

def create_splash_screen():
    """创建启动画面"""
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(QColor(15, 23, 42))

    painter = QPainter(splash_pix)
    painter.setPen(QColor(99, 102, 241))
    painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
    painter.drawText(splash_pix.rect(), Qt.AlignmentFlag.AlignCenter,
                    "智能开发工具套件\n\nv3.0 Integrated")
    painter.end()

    splash = QSplashScreen(splash_pix)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash
