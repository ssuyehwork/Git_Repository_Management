# app/ui/styling.py
"""
UI展现层：全局样式表和样式工具
"""
from PyQt6.QtGui import QPalette, QColor
from app.config import settings

def get_main_stylesheet():
    """获取全局QSS样式表"""
    return f"""
        QMainWindow {{
            background-color: {settings.Colors.PRIMARY_BACKGROUND};
        }}
        QGroupBox {{
            color: {settings.Colors.PRIMARY_TEXT};
            border: 2px solid {settings.Colors.BORDER_PRIMARY};
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
            font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
        }}
        QLabel {{
            color: {settings.Colors.SECONDARY_TEXT};
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: {settings.Colors.INPUT_BACKGROUND};
            color: {settings.Colors.PRIMARY_TEXT};
            border: 2px solid {settings.Colors.BORDER_SECONDARY};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: {settings.Colors.HIGHLIGHT};
        }}
        QLineEdit:focus {{
            border: 2px solid {settings.Colors.BORDER_FOCUS};
            background-color: {settings.Colors.INPUT_FOCUS_BACKGROUND};
        }}
        QLineEdit::placeholder {{
            color: {settings.Colors.PLACEHOLDER_TEXT};
        }}
        QPushButton {{
            background-color: {settings.Colors.BUTTON_NORMAL};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {settings.Colors.BUTTON_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {settings.Colors.BUTTON_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {settings.Colors.BUTTON_DISABLED_BG};
            color: {settings.Colors.BUTTON_DISABLED_TEXT};
        }}
        QStatusBar {{
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
            color: {settings.Colors.SECONDARY_TEXT};
        }}
    """

def set_dark_theme(app):
    """为应用程序设置一个暗色主题调色板"""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(settings.Colors.PRIMARY_BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(settings.Colors.PRIMARY_TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(settings.Colors.SECONDARY_BACKGROUND))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(settings.Colors.TERTIARY_BACKGROUND))
    palette.setColor(QPalette.ColorRole.Text, QColor(settings.Colors.PRIMARY_TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(settings.Colors.BUTTON_NORMAL))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(settings.Colors.PRIMARY_TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(settings.Colors.HIGHLIGHT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(settings.Colors.PRIMARY_TEXT))
    app.setPalette(palette)
