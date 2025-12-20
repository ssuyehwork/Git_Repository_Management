"""
UI 样式与资源
"""
import app.utils.color_palette as cp

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
            color: {cp.TEXT_COLOR};
            font-size: 13px;
            background-color: transparent;
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
            background-color: {cp.PANEL_COLOR};
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
        QPushButton[role="upload"] {{ background-color: {cp.UPLOAD_BG}; }}
        QPushButton[role="upload"]:hover {{ background-color: {cp.UPLOAD_HOVER}; }}
        QPushButton[role="download"] {{ background-color: {cp.DOWNLOAD_BG}; }}
        QPushButton[role="download"]:hover {{ background-color: {cp.DOWNLOAD_HOVER}; }}
        QPushButton[role="sync"] {{ background-color: {cp.SYNC_BG}; }}
        QPushButton[role="sync"]:hover {{ background-color: {cp.SYNC_HOVER}; }}
        QPushButton[role="overwrite"] {{ background-color: {cp.OVERWRITE_BG}; }}
        QPushButton[role="overwrite"]:hover {{ background-color: {cp.OVERWRITE_HOVER}; }}
        QPushButton[role="delete"] {{ background-color: {cp.DELETE_BG}; }}
        QPushButton[role="delete"]:hover {{ background-color: {cp.DELETE_HOVER}; }}
        QPushButton[role="init"] {{ background-color: {cp.INIT_BG}; }}
        QPushButton[role="init"]:hover {{ background-color: {cp.INIT_HOVER}; }}
        QPushButton[role="primary"] {{ background-color: {cp.PRIMARY_BUTTON_BG}; }}
        QPushButton[role="primary"]:hover {{ background-color: {cp.PRIMARY_BUTTON_HOVER}; }}
        QPushButton[role="danger"] {{ background-color: {cp.DANGER_BUTTON_BG}; }}
        QPushButton[role="danger"]:hover {{ background-color: {cp.DANGER_BUTTON_HOVER}; }}
        QStatusBar {{
            background-color: {cp.PANEL_COLOR};
            color: {cp.TEXT_COLOR};
        }}
        QTabWidget::pane {{
            border-top: 2px solid {cp.BORDER_COLOR};
            background-color: {cp.PANEL_COLOR};
        }}
        QTabBar::tab {{
            background-color: {cp.INPUT_BG};
            color: {cp.SUBTLE_TEXT_COLOR};
            border: 1px solid {cp.BORDER_COLOR};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {cp.PANEL_COLOR};
            color: {cp.TEXT_COLOR};
            border: 2px solid {cp.BORDER_COLOR};
            border-bottom: 2px solid {cp.PANEL_COLOR};
        }}
        QTabBar::tab:!selected:hover {{
            background-color: {cp.BUTTON_HOVER};
            color: white;
        }}
        QComboBox {{
            background-color: {cp.INPUT_BG};
            color: {cp.TEXT_COLOR};
            border: 1px solid {cp.BORDER_COLOR};
            border-radius: 4px;
            padding: 5px;
        }}
        QComboBox:hover {{
            border: 1px solid {cp.PRIMARY_ACCENT};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {cp.BORDER_COLOR};
        }}
        QComboBox QAbstractItemView {{
            background-color: {cp.PANEL_COLOR};
            color: {cp.TEXT_COLOR};
            border: 1px solid {cp.BORDER_COLOR};
            selection-background-color: {cp.PRIMARY_ACCENT};
        }}
        QTextEdit {{
            background-color: {cp.INPUT_BG};
            color: {cp.TEXT_COLOR};
            border: 2px solid {cp.BORDER_COLOR};
            border-radius: 6px;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {cp.INPUT_BG};
            width: 12px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {cp.BUTTON_BG};
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {cp.BUTTON_HOVER};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {cp.INPUT_BG};
            height: 12px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {cp.BUTTON_BG};
            min-width: 20px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {cp.BUTTON_HOVER};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """
