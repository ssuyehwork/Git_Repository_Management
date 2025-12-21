# app/ui/styling.py
"""
UI展现层：全局样式表和样式工具
"""
from PyQt6.QtGui import QPalette, QColor
from app.config import settings

def _darken_color(hex_color, amount=120):
    """辅助函数，使颜色变暗"""
    color = QColor(hex_color)
    return color.darker(amount).name()

def get_main_stylesheet():
    """获取全局QSS样式表"""

    # 从 settings.py 中为特殊按钮动态生成样式
    op_button_styles = []
    for btn_config in settings.OPERATIONS_BUTTONS:
        op_id = btn_config['id']
        color = btn_config['color']
        darker_color = _darken_color(color)
        pressed_color = _darken_color(color, 140)

        op_button_styles.append(f"""
            QPushButton#OperationButton_{op_id} {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {darker_color});
            }}
            QPushButton#OperationButton_{op_id}:hover {{
                background: {darker_color};
            }}
            QPushButton#OperationButton_{op_id}:pressed {{
                background: {pressed_color};
            }}
        """)

    status_widget_styles = []
    for key, item in settings.STATUS_ITEMS.items():
        status_widget_styles.append(f"""
            QWidget#StatusWidget_{key} {{
                border-left: 3px solid {item['color']};
            }}
            QWidget#StatusWidget_{key} QLabel {{
                color: {item['color']};
            }}
        """)

    return f"""
        /* --- 全局样式 --- */
        QMainWindow {{ background-color: {settings.Colors.PRIMARY_BACKGROUND}; }}
        QGroupBox {{
            color: {settings.Colors.PRIMARY_TEXT}; border: 2px solid {settings.Colors.BORDER_PRIMARY};
            border-radius: 10px; margin-top: 8px; padding-top: 18px;
            background-color: {settings.Colors.SECONDARY_BACKGROUND}; font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin; left: 20px; padding: 0 8px;
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
        }}
        QLabel {{ color: {settings.Colors.SECONDARY_TEXT}; font-size: 13px; }}
        QLineEdit {{
            background-color: {settings.Colors.INPUT_BACKGROUND}; color: {settings.Colors.PRIMARY_TEXT};
            border: 2px solid {settings.Colors.BORDER_SECONDARY}; border-radius: 6px;
            padding: 8px; font-size: 12px;
            selection-background-color: {settings.Colors.HIGHLIGHT};
        }}
        QLineEdit:focus {{
            border: 2px solid {settings.Colors.BORDER_FOCUS};
            background-color: {settings.Colors.INPUT_FOCUS_BACKGROUND};
        }}
        QLineEdit::placeholder {{ color: {settings.Colors.PLACEHOLDER_TEXT}; }}
        QPushButton {{
            background-color: {settings.Colors.BUTTON_NORMAL}; color: white;
            border: none; border-radius: 6px; padding: 10px;
            font-size: 12px; font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {settings.Colors.BUTTON_HOVER}; }}
        QPushButton:pressed {{ background-color: {settings.Colors.BUTTON_PRESSED}; }}
        QPushButton:disabled {{
            background-color: {settings.Colors.BUTTON_DISABLED_BG};
            color: {settings.Colors.BUTTON_DISABLED_TEXT};
        }}
        QStatusBar {{
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
            color: {settings.Colors.SECONDARY_TEXT};
        }}

        /* --- 特定组件样式 --- */

        /* Title View */
        QWidget#TitleView {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {settings.Colors.BRAND_PRIMARY_START}, stop:1 {settings.Colors.BRAND_PRIMARY_END});
            border-radius: 10px;
            padding: 12px;
        }}
        QLabel#TitleView_TitleLabel {{ color: white; }}
        QLabel#TitleView_VersionLabel {{ color: rgba(255,255,255,0.8); }}

        /* Config View Buttons */
        QPushButton#SaveConfigButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {settings.Colors.SUCCESS}, stop:1 {settings.Colors.SUCCESS_DARK});
            padding: 8px 15px; font-size: 13px;
        }}
        QPushButton#SaveConfigButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {settings.Colors.SUCCESS_DARK}, stop:1 {_darken_color(settings.Colors.SUCCESS_DARK)});
        }}
        QPushButton#RefreshStatusButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {settings.Colors.BRAND_PRIMARY_START}, stop:1 {settings.Colors.BRAND_PRIMARY_END});
            padding: 8px 15px; font-size: 13px;
        }}
        QPushButton#RefreshStatusButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {settings.Colors.BRAND_PRIMARY_END}, stop:1 {settings.Colors.BRAND_PRIMARY_START});
        }}

        /* Status View Widgets */
        QWidget[objectName^="StatusWidget"] {{
            background-color: {settings.Colors.SECONDARY_BACKGROUND};
            border-radius: 5px;
            padding: 6px;
        }}
        QWidget[objectName^="StatusWidget"] QLabel:first-child {{
             color: {settings.Colors.SECONDARY_TEXT}; /* Title Label */
             font-weight: normal;
        }}
        {''.join(status_widget_styles)}

        /* Operations View Buttons */
        {''.join(op_button_styles)}

        /* Log View */
        QTextEdit#LogView_TextEdit {{
            background-color: {settings.Colors.LOG_BACKGROUND};
            color: {settings.Colors.PRIMARY_TEXT};
            border: 2px solid {settings.Colors.SECONDARY_BACKGROUND};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
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
