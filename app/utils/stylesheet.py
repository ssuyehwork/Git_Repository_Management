"""
UI 样式与资源
"""
from PyQt6.QtGui import QColor

def get_main_stylesheet():
    """获取全局样式表"""
    # --- 深蓝色调色板 ---
    BG_COLOR = "#0B1120"          # 主背景色
    PANEL_COLOR = "#1A243A"       # 面板/容器背景色
    BORDER_COLOR = "#2A3F6C"      # 边框色
    TEXT_COLOR = "#E0E8FF"        # 主要文字颜色
    SUBTLE_TEXT_COLOR = "#A0B3D4" # 次要文字颜色
    INPUT_BG = "#202C48"          # 输入框背景
    BUTTON_BG = "#3A5FCD"         # 按钮背景
    BUTTON_HOVER = "#4F75E3"       # 按钮悬停
    PRIMARY_ACCENT = "#5D8BFF"     # 主高亮/焦点色

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
