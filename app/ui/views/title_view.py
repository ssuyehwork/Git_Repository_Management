# app/ui/views/title_view.py
"""
UI视图层：标题区域
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont
from app.config import settings

class TitleView(QWidget):
    """
    应用程序的标题栏视图。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {brand_start}, stop:1 {brand_end});
                border-radius: 10px;
                padding: 12px;
            }
        """.format(
            brand_start=settings.Colors.BRAND_PRIMARY_START,
            brand_end=settings.Colors.BRAND_PRIMARY_END
        ))

        layout = QHBoxLayout(self)

        title = QLabel(settings.TITLE_VIEW_TEXT)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        layout.addStretch()

        version = QLabel(settings.APP_VERSION)
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: rgba(255,255,255,0.8);")
        layout.addWidget(version)
