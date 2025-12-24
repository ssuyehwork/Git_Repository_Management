# app/ui/styles.py

def get_stylesheet():
    return """
        /* 对话框和消息框的全局背景 */
        QDialog, QMessageBox {
            background-color: #1e293b; /* 使用面板颜色，比主窗口稍亮 */
        }

        /* 消息框内的文本颜色 */
        QMessageBox QLabel {
            color: #f1f5f9;
        }

        /* 消息框内的按钮样式 */
        QMessageBox QPushButton {
            background-color: #475569;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px; /* 调整内边距 */
            font-size: 13px;
            font-weight: bold;
            min-width: 80px; /* 设置最小宽度 */
        }
        QMessageBox QPushButton:hover {
            background-color: #64748b;
        }
        QMessageBox QPushButton:pressed {
            background-color: #334155;
        }

        /* 主窗口及其他所有控件的样式 */
        QMainWindow { background-color: #0f172a; }
        QGroupBox {
            color: #f1f5f9; border: 2px solid #334155; border-radius: 10px;
            margin-top: 8px; padding-top: 18px; background-color: #1e293b; font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin; left: 20px; padding: 0 8px; background-color: #1e293b;
        }
        QLabel { color: #cbd5e1; font-size: 13px; }
        QLineEdit {
            background-color: #334155; color: #f1f5f9; border: 2px solid #475569;
            border-radius: 6px; padding: 8px; font-size: 12px; selection-background-color: #6366f1;
        }
        QLineEdit:focus { border: 2px solid #6366f1; background-color: #3f4d63; }
        QLineEdit::placeholder { color: #64748b; }

        QComboBox {
            background-color: #334155;
            color: #f1f5f9;
            border: 2px solid #475569;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }
        QComboBox:focus {
            border: 2px solid #6366f1;
        }
        QComboBox QAbstractItemView {
            background-color: #334155;
            color: #f1f5f9;
            border: 1px solid #475569;
            selection-background-color: #6366f1;
        }
        /* 通用按钮样式，会被特定样式覆盖 */
        QPushButton {
            background-color: #475569; color: white; border: none;
            border-radius: 6px; padding: 10px; font-size: 12px; font-weight: bold;
        }
        QPushButton:hover { background-color: #64748b; }
        QPushButton:pressed { background-color: #334155; }
        QPushButton:disabled { background-color: #334155; color: #64748b; }
        QStatusBar { background-color: #1e293b; color: #cbd5e1; }
    """
