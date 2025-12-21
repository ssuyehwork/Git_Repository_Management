# app/ui/splash.py
"""
UI展现层：应用程序启动画面
"""
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import Qt

from app.config import settings

def create_splash_screen():
    """
    创建一个自定义的启动画面。
    :return: QSplashScreen 实例
    """
    splash_pix = QPixmap(settings.SPLASH_WIDTH, settings.SPLASH_HEIGHT)
    splash_pix.fill(QColor(settings.Colors.PRIMARY_BACKGROUND))

    painter = QPainter(splash_pix)
    painter.setPen(QColor(settings.Colors.BRAND_PRIMARY_START))
    painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))

    # 构建要绘制的文本
    splash_text = f"{settings.APP_NAME}\\n\\n{settings.APP_VERSION}"

    painter.drawText(
        splash_pix.rect(),
        Qt.AlignmentFlag.AlignCenter,
        splash_text
    )
    painter.end()

    splash = QSplashScreen(splash_pix)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash
