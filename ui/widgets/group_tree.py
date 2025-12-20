# ui/widgets/group_tree.py
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal

class GroupTreeWidget(QTreeWidget):
    """
    一个支持拖放操作的QTreeWidget，用于接受被拖拽的脚本并将其绑定到分组。
    """
    # 当一个脚本被拖放到一个分组上时发出此信号
    script_dropped_on_group = pyqtSignal(int, int) # script_id, group_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        """当拖拽进入此组件时调用。"""
        # 检查MIME数据是否包含我们期望的格式
        if event.mimeData().hasFormat('application/x-script-id'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """当拖拽在组件内移动时调用。"""
        # 获取鼠标指针下的项
        item = self.itemAt(event.pos())
        if item and item.data(0, Qt.UserRole) != "FIXED_RECENT":
            # 如果是有效的分组项，则接受移动
            event.acceptProposedAction()
            self.setCurrentItem(item) # 高亮显示目标分组
        else:
            # 如果是“最近使用”或空白区域，则忽略
            event.ignore()

    def dropEvent(self, event):
        """当拖拽释放时调用。"""
        item = self.itemAt(event.pos())

        # 确保释放到了一个有效的分组上
        if not item or item.data(0, Qt.UserRole) == "FIXED_RECENT":
            event.ignore()
            return

        # 提取脚本ID
        script_id_bytes = event.mimeData().data('application/x-script-id')
        if not script_id_bytes:
            event.ignore()
            return

        try:
            script_id = int(script_id_bytes.data().decode())
        except (ValueError, AttributeError):
            event.ignore()
            return
            
        # 提取分组ID
        group_id = item.data(0, Qt.UserRole)
        
        if script_id and group_id:
            # 发出信号，通知逻辑层处理绑定
            self.script_dropped_on_group.emit(script_id, group_id)
            event.acceptProposedAction()
        else:
            event.ignore()
