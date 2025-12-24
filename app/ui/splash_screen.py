from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

# ================================
# 启动画面
# ================================
def create_splash_screen():
    """创建一个美观的启动画面"""
    # 创建一个基础的Pixmap
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(QColor("#0f172a")) # 使用与主窗口一致的背景色

    # 使用QPainter绘制更复杂的文本和效果
    painter = QPainter(splash_pix)

    # 设置抗锯齿，使文本更平滑
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制主标题
    painter.setPen(QColor("#6366f1")) # 使用主题中的高亮颜色
    painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))

    # 使用drawText支持换行
    main_title_rect = splash_pix.rect().adjusted(0, -40, 0, -40) # 向上移动一点
    painter.drawText(main_title_rect, Qt.AlignmentFlag.AlignCenter,
                     "GitHub 仓库智能管理器")

    # 绘制副标题 (版本号)
    painter.setPen(QColor("#e2e8f0")) # 使用柔和的文字颜色
    painter.setFont(QFont("Arial", 16, QFont.Weight.Normal))

    sub_title_rect = splash_pix.rect().adjusted(0, 60, 0, 60) # 向下移动
    painter.drawText(sub_title_rect, Qt.AlignmentFlag.AlignCenter,
                     "v2.0 Professional")

    # 绘制一个简单的底部装饰条
    painter.setPen(Qt.PenStyle.NoPen)
    gradient = QColor(88, 80, 236, 150) # 半透明渐变
    painter.setBrush(gradient)
    painter.drawRect(0, splash_pix.height() - 10, splash_pix.width(), 10)

    painter.end()

    # 创建QSplashScreen实例
    splash = QSplashScreen(splash_pix)

    # 确保启动画面总在最前
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    return splash
