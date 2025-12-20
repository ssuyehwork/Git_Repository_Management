"""
UI 样式与资源
"""
from . import color_palette as cp

def get_main_stylesheet():
    """获取全局样式表"""
    return f"""
        QMainWindow {{
            background-color: {cp.BG_COLOR};
        }}
        QGroupBox {{
            color: {cp.TEXT_COLOR};
            border: 2px solid {cp.BORDER_COLOR};
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: {cp.PANEL_COLOR};
            font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: {cp.PANEL_COLOR};
        }}
        QLabel {{
            color: {cp.SUBTLE_TEXT_COLOR};
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: {cp.INPUT_BG};
            color: {cp.TEXT_COLOR};
            border: 2px solid {cp.BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: {cp.PRIMARY_ACCENT};
        }}
        QLineEdit:focus {{
            border: 2px solid {cp.PRIMARY_ACCENT};
            background-color: {cp.INPUT_BG};
        }}
        QLineEdit::placeholder {{
            color: {cp.SUBTLE_TEXT_COLOR};
        }}
        QPushButton {{
            background-color: {cp.BUTTON_BG};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {cp.BUTTON_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {cp.INPUT_BG};
        }}
        QPushButton:disabled {{
            background-color: {cp.INPUT_BG};
            color: {cp.SUBTLE_TEXT_COLOR};
        }}
        QStatusBar {{
            background-color: {cp.PANEL_COLOR};
            color: {cp.SUBTLE_TEXT_COLOR};
        }}
    """
