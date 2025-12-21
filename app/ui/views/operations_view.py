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
            object_name = f"OperationButton_{btn_config['id']}"
            btn = self._create_operation_button(
                btn_config["text"],
                btn_config["tooltip"],
                object_name
            )
            self.buttons[btn_config["id"]] = btn
            layout.addWidget(btn, i // 3, i % 3)

        self.setLayout(layout)

    def _create_operation_button(self, text, tooltip, object_name):
        """创建单个操作按钮"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        # 使用对象名称代替内联样式
        btn.setObjectName(object_name)
        return btn
