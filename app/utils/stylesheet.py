"""
UI 样式与资源
"""
from PyQt6.QtGui import QColor

def get_main_stylesheet():
    """获取全局样式表"""
    return """
        QMainWindow {
            background-color: #1e293b; /* 深蓝灰背景 */
        }
        QGroupBox {
            color: #f1f5f9;
            border: 2px solid #334155;
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: #2b3a55; /* 稍亮的蓝灰背景 */
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: #2b3a55;
        }
        QLabel {
            color: #cbd5e1;
            font-size: 13px;
        }
        QLineEdit {
            background-color: #334155;
            color: #f1f5f9;
            border: 2px solid #4a5568;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: #6366f1;
        }
        QLineEdit:focus {
            border: 2px solid #6366f1;
            background-color: #3f4d63;
        }
        QLineEdit::placeholder {
            color: #64748b;
        }
        QPushButton {
            background-color: #4a5568;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #64748b;
        }
        QPushButton:pressed {
            background-color: #334155;
        }
        QPushButton:disabled {
            background-color: #334155;
            color: #64748b;
        }
        QStatusBar {
            background-color: #2b3a55;
            color: #cbd5e1;
        }
        QTabWidget::pane {
            border: none;
        }
        QTabBar::tab {
            background: #2b3a55;
            color: #cbd5e1;
            padding: 10px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 150px;
        }
        QTabBar::tab:selected {
            background: #1e293b;
            color: white;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background: #334155;
        }
    """

def darken_color(hex_color, amount=20):
    """使颜色变暗"""
    color = QColor(hex_color)
    h, s, l, a = color.getHsl()
    color.setHsl(h, s, max(0, l - amount), a)
    return color.name()
