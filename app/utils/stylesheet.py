"""
UI 样式与资源
"""
from PyQt6.QtGui import QColor
from .color_palette import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR, TEXT_COLOR, SUBTLE_TEXT_COLOR,
    INPUT_BG, BUTTON_BG, BUTTON_HOVER, PRIMARY_ACCENT, DANGER_ACCENT,
    DANGER_HOVER_ACCENT
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
        QPushButton[role="primary"] {{
            background-color: {PRIMARY_ACCENT};
        }}
        QPushButton[role="primary"]:hover {{
            background-color: {BUTTON_HOVER};
        }}
        QPushButton[role="danger"] {{
            background-color: {DANGER_ACCENT};
            color: white;
        }}
        QPushButton[role="danger"]:hover {{
            background-color: {DANGER_HOVER_ACCENT};
        }}
        QStatusBar {{
            background-color: {PANEL_COLOR};
            color: {SUBTLE_TEXT_COLOR};
        }}
        QTextEdit {{
            background-color: {INPUT_BG};
            color: {TEXT_COLOR};
            border: 2px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
            font-family: Consolas, monospace;
        }}
        QTabWidget::pane {{
            border: none;
            border-top: 3px solid {BORDER_COLOR};
        }}
        QTabBar::tab {{
            background-color: {BG_COLOR};
            color: {SUBTLE_TEXT_COLOR};
            padding: 10px 25px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            min-width: 120px;
            border-bottom: 3px solid transparent; /* Reserve space for the border */
            margin-bottom: -3px; /* Pull tab down to overlap the pane border */
        }}
        QTabBar::tab:hover {{
            background-color: {INPUT_BG};
            color: {TEXT_COLOR};
        }}
        QTabBar::tab:selected {{
            background-color: {PANEL_COLOR}; /* Make it look connected to the content */
            color: {PRIMARY_ACCENT};
            border-bottom: 3px solid {PANEL_COLOR}; /* Cover the pane's border */
        }}
        QComboBox {{
            background-color: {INPUT_BG};
            color: {TEXT_COLOR};
            border: 2px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: {PRIMARY_ACCENT};
        }}
        QComboBox:hover {{
            border: 2px solid {PRIMARY_ACCENT};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: {BORDER_COLOR};
            border-left-style: solid;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {INPUT_BG};
            color: {TEXT_COLOR};
            border: 2px solid {BORDER_COLOR};
            selection-background-color: {PRIMARY_ACCENT};
        }}
        QScrollBar:vertical {{
            border: none;
            background: {BG_COLOR};
            width: 12px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER_COLOR};
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {PRIMARY_ACCENT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

def darken_color(hex_color, amount=20):
    """使颜色变暗"""
    color = QColor(hex_color)
    h, s, l, a = color.getHsl()
    color.setHsl(h, s, max(0, l - amount), a)
    return color.name()
