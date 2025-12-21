# app/ui/views/log_view.py
"""
UI视图层：操作日志区域
"""
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtGui import QFont
from app.config import settings

class LogView(QGroupBox):
    """
    操作日志区域的UI组件。
    """
    def __init__(self, parent=None):
        super().__init__(settings.LOG_GROUP_TITLE, parent)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # 对外暴露的UI控件
        self.log_text = None
        self.clear_btn = None

        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 12, 8, 8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {settings.Colors.LOG_BACKGROUND};
                color: {settings.Colors.PRIMARY_TEXT};
                border: 2px solid {settings.Colors.SECONDARY_BACKGROUND};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        layout.addWidget(self.log_text)

        self.clear_btn = QPushButton(settings.LOG_CLEAR_BUTTON_TEXT)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)
