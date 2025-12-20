# ui/widgets/draggable_table.py

from PyQt5.QtWidgets import QTableWidget, QAbstractItemView
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor, QFont

class DraggableTableWidget(QTableWidget):
    """一个支持拖拽操作的QTableWidget，用于将脚本拖到分组。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(False) # 表格本身不接受拖放
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def startDrag(self, supportedActions):
        """当拖拽开始时被调用。"""
        row = self.currentRow()
        if row < 0:
            return

        item = self.item(row, 0)
        if not item:
            return

        script_id = item.data(Qt.UserRole)
        script_name = item.text()
        
        if script_id is None:
            return

        # 创建MIME数据
        mime_data = QMimeData()
        mime_data.setText(str(script_id)) # 纯文本ID，用于简单拖放
        mime_data.setData('application/x-script-id', str(script_id).encode())

        # 创建一个拖拽对象
        drag = QDrag(self)
        drag.setMimeData(mime_data)

        # 创建一个自定义的拖拽预览图
        pixmap = self._create_drag_pixmap(script_name)
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())

        # 执行拖拽操作
        drag.exec_(Qt.CopyAction)

    def _create_drag_pixmap(self, text):
        """创建一个用于拖拽预览的自定义QPixmap。"""
        # 限制文本长度以适应预览图
        display_text = text[:25] + '...' if len(text) > 25 else text
        
        pixmap = QPixmap(220, 35)
        pixmap.fill(QColor(14, 99, 156, 200)) # 半透明背景

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, display_text)
        painter.end()

        return pixmap
