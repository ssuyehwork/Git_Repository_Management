"""
UI 样式与资源
"""
from PyQt6.QtGui import QColor

def get_main_stylesheet():
    """获取全局样式表"""
    return """
        QMainWindow {
            background-color: #0f172a;
        }
        QGroupBox {
            color: #f1f5f9;
            border: 2px solid #3a5fcd;
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: #1c2a4a;
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: #1c2a4a;
        }
        QLabel {
            color: #cbd5e1;
            font-size: 13px;
        }
        QLineEdit {
            background-color: #202c48;
            color: #f1f5f9;
            border: 2px solid #3a5fcd;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: #6366f1;
        }
        QLineEdit:focus {
            border: 2px solid #6366f1;
            background-color: #1c2a4a;
        }
        QLineEdit::placeholder {
            color: #a0b3d4;
        }
        QPushButton {
            background-color: #3a5fcd;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4f75e3;
        }
        QPushButton:pressed {
            background-color: #202c48;
        }
        QPushButton:disabled {
            background-color: #202c48;
            color: #a0b3d4;
        }
        QStatusBar {
            background-color: #1c2a4a;
            color: #cbd5e1;
        }
    """

def darken_color(hex_color, amount=20):
    """使颜色变暗"""
    color = QColor(hex_color)
    h, s, l, a = color.getHsl()
    color.setHsl(h, s, max(0, l - amount), a)
    return color.name()
