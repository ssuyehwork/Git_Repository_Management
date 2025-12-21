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
        # 为QSS设置对象名称
        self.setObjectName("TitleView")

        layout = QHBoxLayout(self)

        title = QLabel(settings.TITLE_VIEW_TEXT)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        # 使用对象名称代替内联样式
        title.setObjectName("TitleView_TitleLabel")
        layout.addWidget(title)

        layout.addStretch()

        version = QLabel(settings.APP_VERSION)
        version.setFont(QFont("Arial", 10))
        # 使用对象名称代替内联样式
        version.setObjectName("TitleView_VersionLabel")
        layout.addWidget(version)
