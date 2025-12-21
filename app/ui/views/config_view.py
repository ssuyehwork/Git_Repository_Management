# app/ui/views/config_view.py
"""
UI视图层：仓库配置区域
"""
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont
from app.config import settings

class ConfigView(QGroupBox):
    """
    仓库配置区域的UI组件。
    """
    def __init__(self, parent=None):
        super().__init__(settings.CONFIG_GROUP_TITLE, parent)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # 对外暴露的UI控件
        self.local_path_input = None
        self.remote_url_input = None
        self.username_input = None
        self.email_input = None
        self.browse_btn = None
        self.save_btn = None
        self.refresh_btn = None

        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 10, 8, 8)

        # 本地路径
        layout.addWidget(QLabel(settings.CONFIG_LABELS["local_path"]), 0, 0)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText(settings.CONFIG_PLACEHOLDERS["local_path"])
        layout.addWidget(self.local_path_input, 0, 1)

        self.browse_btn = QPushButton(settings.CONFIG_BUTTONS["browse"])
        self.browse_btn.setFixedWidth(100)
        layout.addWidget(self.browse_btn, 0, 2)

        # 远程URL
        layout.addWidget(QLabel(settings.CONFIG_LABELS["remote_url"]), 1, 0)
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText(settings.CONFIG_PLACEHOLDERS["remote_url"])
        layout.addWidget(self.remote_url_input, 1, 1, 1, 2)

        # Git用户名
        layout.addWidget(QLabel(settings.CONFIG_LABELS["username"]), 2, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(settings.CONFIG_PLACEHOLDERS["username"])
        layout.addWidget(self.username_input, 2, 1, 1, 2)

        # Git邮箱
        layout.addWidget(QLabel(settings.CONFIG_LABELS["email"]), 3, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(settings.CONFIG_PLACEHOLDERS["email"])
        layout.addWidget(self.email_input, 3, 1, 1, 2)

        # 按钮行
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton(settings.CONFIG_BUTTONS["save"])
        self.save_btn.setStyleSheet("""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_start}, stop:1 {color_end});
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_end}, stop:1 {color_start_dark});
            }}
        """.format(
            color_start=settings.Colors.SUCCESS,
            color_end=settings.Colors.SUCCESS_DARK,
            color_start_dark=settings.Colors.SUCCESS_DARK
        ))
        button_layout.addWidget(self.save_btn)

        self.refresh_btn = QPushButton(settings.CONFIG_BUTTONS["refresh"])
        self.refresh_btn.setStyleSheet("""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_start}, stop:1 {color_end});
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_end}, stop:1 {color_start});
            }}
        """.format(
            color_start=settings.Colors.BRAND_PRIMARY_START,
            color_end=settings.Colors.BRAND_PRIMARY_END
        ))
        button_layout.addWidget(self.refresh_btn)

        layout.addLayout(button_layout, 4, 0, 1, 3)

        self.setLayout(layout)

    def get_config_data(self):
        """获取当前所有输入框的数据"""
        return {
            'local_path': self.local_path_input.text(),
            'remote_url': self.remote_url_input.text(),
            'username': self.username_input.text(),
            'email': self.email_input.text()
        }

    def set_config_data(self, config_data):
        """使用给定的数据填充输入框"""
        self.local_path_input.setText(config_data.get('local_path', ''))
        self.remote_url_input.setText(config_data.get('remote_url', ''))
        self.username_input.setText(config_data.get('username', ''))
        self.email_input.setText(config_data.get('email', ''))
