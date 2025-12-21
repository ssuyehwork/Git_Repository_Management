# app/ui/views/status_view.py
"""
UI视图层：仓库状态显示区域
"""
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from app.config import settings

class StatusView(QGroupBox):
    """
    仓库状态显示区域的UI组件。
    """
    def __init__(self, parent=None):
        super().__init__(settings.STATUS_GROUP_TITLE, parent)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.status_labels = {}
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(8, 12, 8, 8)

        # 创建状态标签
        for i, (key, item) in enumerate(settings.STATUS_ITEMS.items()):
            object_name = f"StatusWidget_{key}"
            label_widget = self._create_status_label(
                item["title"],
                settings.STATUS_DEFAULT_VALUE,
                item["color"],
                object_name
            )
            self.status_labels[key] = label_widget
            layout.addWidget(label_widget, 0, i)

        self.setLayout(layout)

    def _create_status_label(self, title, value, color_ignored, object_name):
        """创建单个状态标签的小部件"""
        widget = QWidget()
        # 使用对象名称代替内联样式
        widget.setObjectName(object_name)

        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        # 颜色将由全局样式表通过父控件的对象名称来设置

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        # 将 value_label 附加到 widget 以便后续访问
        widget.value_label = value_label
        return widget

    def update_status(self, status_data):
        """
        根据传入的字典更新状态标签。
        :param status_data: 字典，键为 'branch', 'uncommitted', 'unpushed', 'sync'
        """
        for key, widget in self.status_labels.items():
            new_value = status_data.get(key, settings.STATUS_DEFAULT_VALUE)
            widget.value_label.setText(str(new_value))
