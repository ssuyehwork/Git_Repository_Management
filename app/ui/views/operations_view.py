# app/ui/views/operations_view.py
"""
UI视图层：智能操作按钮区域
"""
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QPushButton
from PyQt6.QtGui import QFont, QColor
from app.config import settings

class OperationsView(QGroupBox):
    """
    智能操作按钮区域的UI组件。
    """
    def __init__(self, parent=None):
        super().__init__(settings.OPERATIONS_GROUP_TITLE, parent)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.buttons = {}
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 12, 8, 8)

        for i, btn_config in enumerate(settings.OPERATIONS_BUTTONS):
            btn = self._create_operation_button(
                btn_config["text"],
                btn_config["tooltip"],
                btn_config["color"]
            )
            self.buttons[btn_config["id"]] = btn
            layout.addWidget(btn, i // 3, i % 3)

        self.setLayout(layout)

    def _create_operation_button(self, text, tooltip, hex_color):
        """创建单个操作按钮"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        # 动态生成样式表
        color = QColor(hex_color)
        darker_color_name = color.darker(120).name()
        pressed_color_name = color.darker(140).name()

        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hex_color}, stop:1 {darker_color_name});
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {darker_color_name};
            }}
            QPushButton:pressed {{
                background: {pressed_color_name};
            }}
            QPushButton:disabled {{
                background: {settings.Colors.BUTTON_DISABLED_BG};
                color: {settings.Colors.BUTTON_DISABLED_TEXT};
            }}
        """)
        return btn
