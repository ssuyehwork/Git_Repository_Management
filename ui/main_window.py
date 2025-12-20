# ui/main_window.py

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTextEdit, QSplitter, 
                             QMenu, QInputDialog, QHeaderView, QShortcut, QApplication,
                             QTableWidgetItem, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QKeySequence

from ui.widgets.draggable_table import DraggableTableWidget
from ui.widgets.group_tree import GroupTreeWidget
from config import WINDOW_TITLE, DEFAULT_WINDOW_GEOMETRY

class PyLauncherApp(QMainWindow):
    """
    应用程序的主窗口(UI)。
    负责UI组件的初始化、布局和事件连接。
    通过app_logic与业务逻辑层交互。
    """
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.app_logic = app_logic
        self.expanded_group_ids = set()

        self._setup_ui()
        self._connect_signals()
        
        # 让业务逻辑层加载初始数据
        self.app_logic.load_initial_data()

    def _setup_ui(self):
        """初始化UI组件和布局。"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*DEFAULT_WINDOW_GEOMETRY)
        self.setFont(QFont("Microsoft YaHei", 10))
        self._apply_stylesheet()

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Input Area ---
        top_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("输入以搜索 | 回车执行首个匹配项 | F5 运行输入框路径...")
        self.clear_btn = QPushButton("×")
        self.clear_btn.setMaximumWidth(40)
        self.run_btn = QPushButton("运行 (F5)")
        top_layout.addWidget(self.path_input)
        top_layout.addWidget(self.clear_btn)
        top_layout.addWidget(self.run_btn)
        main_layout.addLayout(top_layout)

        # --- Main Splitter ---
        h_splitter = QSplitter(Qt.Horizontal)
        
        # --- Left: Group Tree ---
        self.group_tree = GroupTreeWidget(self)
        self.group_tree.setHeaderLabel("分组管理")
        
        # --- Middle: Script Table ---
        self.script_table = DraggableTableWidget(self)
        self.script_table.setColumnCount(3)
        self.script_table.setHorizontalHeaderLabels(['文件名', '标记', '路径'])
        self.script_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.script_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.script_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.script_table.verticalHeader().setVisible(True)

        # --- Right: Log Area ---
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0,0,0,0)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.clear_log_btn = QPushButton("清空日志")
        self.copy_log_btn = QPushButton("复制日志")
        log_btn_layout = QHBoxLayout()
        log_btn_layout.addWidget(self.clear_log_btn)
        log_btn_layout.addWidget(self.copy_log_btn)
        log_layout.addLayout(log_btn_layout)
        log_layout.addWidget(self.log_text)

        h_splitter.addWidget(self.group_tree)
        h_splitter.addWidget(self.script_table)
        h_splitter.addWidget(log_widget)
        h_splitter.setSizes([200, 700, 500])
        main_layout.addWidget(h_splitter)
        
        self.log_text.append("[系统] Python脚本启动器已就绪\n")

    def _connect_signals(self):
        """连接所有UI组件的信号到槽函数。"""
        # --- App Logic -> UI ---
        self.app_logic.scripts_updated.connect(self.update_script_table)
        self.app_logic.groups_updated.connect(self.update_group_tree)
        self.app_logic.log_message.connect(self.log_text.append)
        
        # --- UI -> App Logic ---
        self.path_input.textChanged.connect(self.app_logic.search_scripts)
        self.path_input.returnPressed.connect(self._handle_enter_press)
        self.run_btn.clicked.connect(self._run_script_from_input)
        self.group_tree.itemClicked.connect(self._on_group_selected)
        self.group_tree.script_dropped_on_group.connect(self.app_logic.bind_script_to_group)
        
        # --- UI Internal ---
        self.clear_btn.clicked.connect(self.path_input.clear)
        self.clear_log_btn.clicked.connect(self.log_text.clear)
        self.copy_log_btn.clicked.connect(self._copy_log)
        self.script_table.cellDoubleClicked.connect(self._run_script_from_table)

        # --- Context Menus ---
        self.group_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.group_tree.customContextMenuRequested.connect(self._show_group_menu)
        self.script_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.script_table.customContextMenuRequested.connect(self._show_table_menu)
        
        # --- Shortcuts ---
        for i in range(6):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, lambda r=i: self._set_selected_script_rating(r))
            QShortcut(QKeySequence(f"Meta+{i}"), self, lambda r=i: self._set_selected_script_rating(r))
        QShortcut(QKeySequence("F5"), self, self._run_script_from_input)
        
    def _run_script_from_input(self):
        path = self.path_input.text().strip()
        self.app_logic.run_script(path, sys.argv[0])
        
    def _run_script_from_table(self, row, col):
        path_item = self.script_table.item(row, 2)
        if path_item:
            self.path_input.setText(path_item.text())
            self.app_logic.run_script(path_item.text(), sys.argv[0])
            
    def _handle_enter_press(self):
        if self.script_table.rowCount() > 0:
            path_item = self.script_table.item(0, 2)
            if path_item:
                self.path_input.setText(path_item.text())
                self.app_logic.run_script(path_item.text(), sys.argv[0])
        else:
            self._run_script_from_input()
            
    def _on_group_selected(self, item, column):
        group_id = item.data(0, Qt.UserRole)
        if group_id is not None:
            self.app_logic.filter_scripts_by_group(group_id)

    def _set_selected_script_rating(self, rating):
        row = self.script_table.currentRow()
        if row < 0:
            self.log_text.append("[标记日志] 错误：未选中任何脚本\n")
            return
        script_id = self.script_table.item(row, 0).data(Qt.UserRole)
        if script_id:
            self.app_logic.set_script_rating(script_id, rating)
            
    def update_script_table(self, scripts):
        """使用业务逻辑层提供的数据更新脚本表格。"""
        self.script_table.setRowCount(0)
        search_text = self.path_input.text().strip().lower()
        
        for idx, (s_id, name, path, rating) in enumerate(scripts):
            self.script_table.insertRow(idx)
            
            # Name Item
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, s_id)
            self.script_table.setItem(idx, 0, name_item)
            
            # Rating Item
            stars = "★" * (rating if rating else 0)
            star_item = QTableWidgetItem(stars)
            star_item.setForeground(QColor("#ffd700"))
            self.script_table.setItem(idx, 1, star_item)

            # Path Item
            path_item = QTableWidgetItem(path)
            self.script_table.setItem(idx, 2, path_item)

            # Highlight if matches search text
            if search_text and (search_text in name.lower() or search_text in path.lower()):
                font = name_item.font()
                font.setBold(True)
                name_item.setFont(font)
                for col in range(3):
                    self.script_table.item(idx, col).setBackground(QColor(30, 60, 100, 80))

    def update_group_tree(self, group_data, expanded_ids):
        """使用业务逻辑层提供的数据更新分组树。"""
        self._save_tree_expansion_state()
        self.group_tree.clear()
        
        # Add "Recent" item
        recent_count = group_data.get("recent_count", 0)
        recent_item = QTreeWidgetItem([f"最近使用 ({min(recent_count, 20)})"])
        recent_item.setData(0, Qt.UserRole, "FIXED_RECENT")
        recent_item.setForeground(0, QColor("#ffd700"))
        self.group_tree.addTopLevelItem(recent_item)

        # Add other groups recursively
        group_tree = group_data.get("tree", {})
        counts = group_data.get("counts", {})
        for g_id, node in group_tree.items():
            self._add_group_tree_item(self.group_tree, node, counts)

        self._restore_tree_expansion_state()

    def _add_group_tree_item(self, parent_widget, node, counts):
        """递归地向树中添加分组项。"""
        count = counts.get(node['id'], 0)
        item = QTreeWidgetItem([f"{node['name']} ({count})"])
        item.setData(0, Qt.UserRole, node['id'])
        item.setForeground(0, QColor(node['color']))
        
        # Distinguish between adding to root (QTreeWidget) and to an item (QTreeWidgetItem)
        if isinstance(parent_widget, QTreeWidget):
            parent_widget.addTopLevelItem(item)
        else:
            parent_widget.addChild(item)
        
        for child_node in node['children']:
            self._add_group_tree_item(item, child_node, counts)
            
    def _save_tree_expansion_state(self):
        """保存当前分组树的展开状态。"""
        self.expanded_group_ids.clear()
        for i in range(self.group_tree.topLevelItemCount()):
            item = self.group_tree.topLevelItem(i)
            self._traverse_tree_for_expansion(item, save=True)

    def _restore_tree_expansion_state(self):
        """恢复分组树的展开状态。"""
        for i in range(self.group_tree.topLevelItemCount()):
            item = self.group_tree.topLevelItem(i)
            self._traverse_tree_for_expansion(item, save=False)

    def _traverse_tree_for_expansion(self, item, save):
        """递归遍历树以保存或恢复展开状态。"""
        group_id = item.data(0, Qt.UserRole)
        if group_id is not None and group_id != "FIXED_RECENT":
            if save:
                if item.isExpanded():
                    self.expanded_group_ids.add(group_id)
            else:
                if group_id in self.expanded_group_ids:
                    item.setExpanded(True)

        for i in range(item.childCount()):
            self._traverse_tree_for_expansion(item.child(i), save)

    # --- Context Menu Implementations ---
    def _show_group_menu(self, position):
        item = self.group_tree.itemAt(position)
        if item and item.data(0, Qt.UserRole) == "FIXED_RECENT": return
        
        menu = QMenu()
        add_group_action = menu.addAction("添加分组")
        add_subgroup_action = menu.addAction("添加子分组")
        delete_action = menu.addAction("删除分组")
        
        action = menu.exec_(self.group_tree.viewport().mapToGlobal(position))

        if action == add_group_action:
            name, ok = QInputDialog.getText(self, "添加分组", "分组名称:")
            if ok and name: self.app_logic.add_group(name)
        elif action == add_subgroup_action:
            if not item: return
            parent_id = item.data(0, Qt.UserRole)
            name, ok = QInputDialog.getText(self, "添加子分组", "分组名称:")
            if ok and name: self.app_logic.add_group(name, parent_id)
        elif action == delete_action:
            if not item: return
            group_id = item.data(0, Qt.UserRole)
            group_name = item.text(0).split(' (')[0]
            self.app_logic.delete_group(group_id, group_name)
            
    def _show_table_menu(self, pos):
        row = self.script_table.rowAt(pos.y())
        if row < 0: return

        script_id = self.script_table.item(row, 0).data(Qt.UserRole)
        path = self.script_table.item(row, 2).text()
        
        menu = QMenu()
        run_action = menu.addAction("运行")
        copy_action = menu.addAction("复制路径")
        open_folder_action = menu.addAction("打开所在文件夹")
        unbind_action = menu.addAction("从当前分组解绑")
        delete_action = menu.addAction("从数据库删除")
        edit_name_action = menu.addAction("编辑名称")

        action = menu.exec_(self.script_table.viewport().mapToGlobal(pos))
        
        if action == run_action:
            self.path_input.setText(path)
            self.app_logic.run_script(path, sys.argv[0])
        elif action == copy_action:
            QApplication.clipboard().setText(path)
            self.log_text.append("[交互] 路径已复制到剪贴板\n")
        elif action == open_folder_action:
            self.app_logic.open_containing_folder(path)
        elif action == unbind_action:
            current_group = self.group_tree.currentItem()
            if current_group:
                group_id = current_group.data(0, Qt.UserRole)
                if group_id and group_id != "FIXED_RECENT":
                    self.app_logic.unbind_script_from_group(script_id, group_id)
        elif action == delete_action:
            self.app_logic.delete_script(script_id)
        elif action == edit_name_action:
            current_name = self.script_table.item(row, 0).text()
            new_name, ok = QInputDialog.getText(self, "编辑名称", "新名称:", text=current_name)
            if ok and new_name:
                self.app_logic.update_script_name(script_id, new_name)

    def _copy_log(self):
        QApplication.clipboard().setText(self.log_text.toPlainText())
        self.log_text.append("[系统] 日志已复制到剪贴板\n")
        
    def closeEvent(self, event):
        """在关闭窗口前执行清理工作。"""
        self._save_tree_expansion_state()
        if self.app_logic.is_runner_active():
            self.log_text.append("[关闭] 检测到有脚本正在运行，程序将退出...\n")
        event.accept()

    def _apply_stylesheet(self):
        """应用全局样式表。"""
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #2c3e50; 
                color: #ecf0f1; 
                font-family: 'Microsoft YaHei';
            }
            QLineEdit { 
                background-color: #34495e; 
                border: 1px solid #3498db; 
                padding: 5px; 
                border-radius: 3px; 
                color: #ecf0f1;
            }
            QLineEdit:focus {
                border: 1px solid #5dade2;
            }
            QPushButton { 
                background-color: #3498db; 
                color: white;
                border: none; 
                padding: 5px 12px; 
                border-radius: 3px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
            QTableWidget { 
                background-color: #34495e; 
                alternate-background-color: #2c3e50; 
                border: 1px solid #2c3e50; 
                gridline-color: #2c3e50; 
                selection-background-color: #2980b9; 
                color: #ecf0f1;
            }
            QHeaderView::section { 
                background-color: #34495e; 
                padding: 5px; 
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
            QTextEdit { 
                background-color: #283747; 
                border: 1px solid #2c3e50; 
                color: #ecf0f1;
            }
            QTreeWidget { 
                background-color: #34495e; 
                border: 1px solid #2c3e50; 
            }
            QTreeWidget::item:selected { 
                background-color: #2980b9; 
            }
            QSplitter::handle {
                background-color: #2c3e50;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
            QSplitter::handle:vertical {
                height: 1px;
            }
        """)
