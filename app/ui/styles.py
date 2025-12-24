from PyQt6.QtGui import QColor

def darken_color(hex_color, amount=20):
    """使十六进制颜色变暗指定量"""
    color = QColor(hex_color)
    h, s, l, a = color.getHsl()
    # 减少亮度, 最小为0
    color.setHsl(h, s, max(0, l - amount), a)
    return color.name()

def get_stylesheet():
    """返回应用程序的全局QSS样式表"""
    return f"""
        QMainWindow {{
            background-color: #0f172a; /* 深蓝灰色背景 */
        }}

        QGroupBox {{
            color: #f1f5f9; /* 亮灰色文字 */
            border: 2px solid #334155; /* 边框颜色 */
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 18px;
            background-color: #1e293b; /* 组背景色 */
            font-size: 14px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 8px;
            background-color: #1e293b; /* 标题背景与组背景一致 */
        }}

        QLabel {{
            color: #cbd5e1; /* 默认标签文字颜色 */
            font-size: 13px;
            background-color: transparent; /* 标签背景透明 */
        }}

        /* 特定标题样式 */
        QWidget #titleWidget QLabel {{
            color: white;
        }}

        QLineEdit {{
            background-color: #334155;
            color: #f1f5f9;
            border: 2px solid #475569;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            selection-background-color: #6366f1; /* 选中文本背景色 */
        }}
        QLineEdit:focus {{
            border: 2px solid #6366f1; /* 焦点状态边框高亮 */
            background-color: #3f4d63;
        }}
        QLineEdit::placeholder {{
            color: #64748b; /* 占位符文字颜色 */
        }}

        QPushButton {{
            background-color: #475569;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #64748b;
        }}
        QPushButton:pressed {{
            background-color: #334155;
        }}
        QPushButton:disabled {{
            background-color: #334155;
            color: #64748b;
        }}

        /* 特定按钮样式 */
        QPushButton#saveButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #10b981, stop:1 #059669);
        }}
        QPushButton#saveButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #059669, stop:1 #047857);
        }}
        QPushButton#refreshButton {{
             background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #4f46e5);
        }}
        QPushButton#refreshButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #4338ca);
        }}

        QStatusBar {{
            background-color: #1e293b;
            color: #10b981;
            font-weight: bold;
        }}

        QTextEdit {{
            background-color: #0f172a;
            color: #e2e8f0;
            border: 2px solid #1e293b;
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
        }}

        QProgressBar {{
            border: 2px solid #6366f1;
            border-radius: 8px;
            text-align: center;
            height: 30px;
            background-color: #1f2937;
            color: white;
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366f1, stop:1 #8b5cf6);
            border-radius: 6px;
        }}

        /* 状态标签特定样式 */
        QWidget#statusLabelWidget {{
            background-color: #1f2937;
            border-radius: 5px;
            padding: 6px;
        }}
        QWidget#statusLabelWidget QLabel {{
            color: #9ca3af; /* 标题颜色 */
            background-color: transparent;
        }}
        QWidget#statusLabelWidget QLabel#value {{
            background-color: transparent; /* 值标签背景也透明 */
        }}

    """
