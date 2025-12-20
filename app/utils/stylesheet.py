"""
UI 样式与资源
"""
from PyQt6.QtGui import QColor
from .color_palette import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR, TEXT_COLOR, SUBTLE_TEXT_COLOR,
    INPUT_BG, BUTTON_BG, BUTTON_HOVER, PRIMARY_ACCENT
)

def get_main_stylesheet():
    """获取全局样式表"""
    return f"""
        QMainWindow {{
            background-color: {BG_COLOR};
        }}
        QGroupBox {{
            color: {TEXT_COLOR};
            border: 2px solid {BORDER_COLOR};
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: {PANEL_COLOR};
            font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: {PANEL_COLOR};
        }}
        QLabel {{
            color: {SUBTLE_TEXT_COLOR};
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: {INPUT_BG};
            color: {TEXT_COLOR};
            border: 2px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: {PRIMARY_ACCENT};
        }}
        QLineEdit:focus {{
            border: 2px solid {PRIMARY_ACCENT};
            background-color: #283659; /* 输入框聚焦时稍亮的背景 */
        }}
        QLineEdit::placeholder {{
            color: {SUBTLE_TEXT_COLOR};
        }}
        QPushButton {{
            background-color: {BUTTON_BG};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {BUTTON_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {BORDER_COLOR};
        }}
        QPushButton:disabled {{
            background-color: {BORDER_COLOR};
            color: {SUBTLE_TEXT_COLOR};
        }}
        QStatusBar {{
            background-color: {PANEL_COLOR};
            color: {SUBTLE_TEXT_COLOR};
        }}
    """

def darken_color(hex_color, amount=20):
    """使颜色变暗"""
    color = QColor(hex_color)
    h, s, l, a = color.getHsl()
    color.setHsl(h, s, max(0, l - amount), a)
    return color.name()
